"""纹理导出为 PNG + 画廊缩略图。"""

import os
import gc
import time
import sys

from PIL import Image

from .formats import texture_format_name

THUMB_MAX_W = 420
JPEG_Q = 82


def export_texture(data, out_png):
    """把 Unity Texture2D 解码并存为 PNG，返回 (宽, 高, 文件字节数)。"""
    img = data.image
    clean = img.copy()          # 丢掉 UnityPy 附带的元数据，得到干净图像
    img = None
    clean.save(out_png, "PNG", compress_level=6)
    size = os.path.getsize(out_png)
    return clean, size


def save_thumb(img, out_jpg):
    """由原图生成缩略图 JPEG（自动合成 alpha 背景）。返回是否成功。"""
    if img.width < 160:
        return False
    tw = min(THUMB_MAX_W, img.width)
    th = max(1, round(img.height * tw / img.width))
    if img.mode in ("RGBA", "LA", "P"):
        bg = Image.new("RGB", img.size, (255, 255, 255))
        rgba = img.convert("RGBA")
        bg.paste(rgba, (0, 0), rgba)
        src = bg
    else:
        src = img.convert("RGB")
    t = src.resize((tw, th), Image.LANCZOS)
    t.save(out_jpg, "JPEG", quality=JPEG_Q, optimize=True)
    t.close()
    src.close()
    return True


def export_all(bundles, out_dir, dry_run=False, progress_every=100, log=print):
    """遍历所有 bundle 的 Texture2D，导出 PNG + 缩略图。

    返回 (records, ok, fail, errors)。每条 record 是一个 dict。
    """
    os.makedirs(out_dir, exist_ok=True)
    thumb_dir = os.path.join(out_dir, "_thumbs")
    os.makedirs(thumb_dir, exist_ok=True)

    records = []
    ok = fail = 0
    errors = []
    t0 = time.time()

    for bundle in bundles:
        src_stem = bundle.filename.rsplit(".", 1)[0]
        dst = os.path.join(out_dir, src_stem)
        os.makedirs(dst, exist_ok=True)
        texs = bundle.textures()
        log("[image] %s -> %s  (%d 张)" % (bundle.filename, src_stem, len(texs)))
        sys.stdout.flush()

        # 先建立 name -> [(w,h,pid)] 以识别同名多分辨率（缩略图）
        by_name = {}
        for pid, o in texs:
            try:
                d = o.read()
            except Exception:
                continue
            by_name.setdefault(d.m_Name, []).append((d.m_Width, d.m_Height, pid))
            del d, o
        gc.collect()

        used = set()
        for i, (pid, o) in enumerate(texs, 1):
            try:
                d = o.read()
                name = d.m_Name or ""
                w, h = d.m_Width, d.m_Height

                base = _safe(name)
                sib = by_name.get(name, [])
                if len(sib) > 1:
                    biggest = max(x * y for x, y, _ in sib)
                    if w * h < biggest:
                        base += "_thumb"       # 同名里较小的那张 = 缩略图
                if base in used:
                    base = "%s__%d" % (base, pid)
                used.add(base)

                rec = {
                    "name": name, "file": base, "src": bundle.filename,
                    "src_stem": src_stem, "path_id": pid, "w": w, "h": h,
                    "fmt": texture_format_name(getattr(d, "m_TextureFormat", None)),
                }
                rel_png = "%s/%s.png" % (src_stem, base)
                out_png = os.path.join(out_dir, rel_png)
                rec["rel"] = rel_png
                rec["thumb"] = rel_png         # 默认缩略图即原图

                if dry_run:
                    rec["bytes"] = w * h  # 粗略占位
                    records.append(rec)
                    ok += 1
                else:
                    img, fsize = export_texture(d, out_png)
                    rec["bytes"] = fsize
                    tname = base + ".jpg"
                    if save_thumb(img, os.path.join(thumb_dir, tname)):
                        rec["thumb"] = "_thumbs/" + tname
                    img.close()
                    records.append(rec)
                    ok += 1
            except Exception as exc:
                fail += 1
                errors.append("%s pid=%s %s: %s" % (bundle.filename, pid, type(exc).__name__, exc))
            if progress_every and i % progress_every == 0:
                log("    %d/%d  ok=%d fail=%d  %.0fs"
                    % (i, len(texs), ok, fail, time.time() - t0))
                sys.stdout.flush()
            if i % 150 == 0:
                gc.collect()

    return records, ok, fail, errors, time.time() - t0


_BAD = None


def _safe(name):
    import re
    global _BAD
    if _BAD is None:
        _BAD = re.compile(r'[\\/:*?"<>|\x00-\x1f]')
    s = _BAD.sub("_", (name or "").strip()).rstrip(". ")
    return s or "unnamed"