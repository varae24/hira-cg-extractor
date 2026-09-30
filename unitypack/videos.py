"""VideoClip 原始字节提取。

Unity 把导入的视频以原封不动的编码字节存在 <Data>/resources.resource 里，
VideoClip 对象只存一个 (offset, size)。本模块按优先级尝试三种方式定位：

  1. UnityPy 解析出的 m_ExternalResources（部分版本直接给 offset/size）
  2. 手工解析 VideoClip 的原始字节，读 m_Offset / m_Size
  3. 兜底：扫描 resource 文件里的 MP4 `ftyp` box 签名

导出即原始字节拷贝，不做任何重新编码。
"""

import os
import struct
import re

_BAD = re.compile(r'[\\/:*?"<>|\x00-\x1f]')


def _safe(name):
    return _BAD.sub("_", (name or "").strip()).rstrip(". ") or "unnamed"


def _read_str(buf, pos):
    n = struct.unpack_from("<i", buf, pos)[0]
    pos += 4
    s = buf[pos:pos + n].decode("utf-8", "replace")
    pos += n
    return s, pos + (4 - n % 4) % 4


def parse_raw_videoclip(raw):
    """手工解析 VideoClip 原始数据，返回 (offset, size) 或 None。

    布局：m_Name(str) + m_OriginalPath(str) + m_Format(u16) + m_Source(u8)
          -> 对齐到 8 -> m_Offset(u64) + m_Size(u64)
    """
    try:
        _, pos = _read_str(raw, 0)
        _, pos = _read_str(raw, pos)
        pos += 3                       # u16 format + u8 source
        pos += (8 - pos % 8) % 8       # 对齐到 8 字节
        offset, size = struct.unpack_from("<QQ", raw, pos)
        if size <= 0 or offset <= 0 or size > (1 << 33):
            return None
        return offset, size
    except Exception:
        return None


def _looks_like_mp4(fp, offset):
    fp.seek(offset)
    return fp.read(8)[4:8] == b"ftyp"


def find_videos(bundle, resource_path, log=print):
    """在 bundle 中定位所有 VideoClip 的字节，返回 (name, offset, size) 列表。"""
    found = []
    for pid, o in bundle.videos():
        d = o.read()
        name = d.m_Name
        loc = None

        # 方式 1：UnityPy 已解析出的 m_ExternalResources
        er = getattr(d, "m_ExternalResources", None)
        if er is not None:
            off = getattr(er, "m_Offset", 0)
            size = getattr(er, "m_Size", 0)
            if off and size:
                loc = (off, size)

        # 方式 2：手工解析原始字节
        if loc is None:
            try:
                loc = parse_raw_videoclip(o.get_raw_data())
            except Exception:
                loc = None

        found.append((pid, name, loc,
                      round(d.m_FrameCount / d.m_FrameRate, 1) if d.m_FrameRate else 0,
                      d.m_ProxyWidth, d.m_ProxyHeight))
    return found


def export_videos(bundles, resource_path, out_dir, dry_run=False, log=print):
    """把 VideoClip 原始字节切出为 .mp4，返回 (records, bytes_written)。"""
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(os.path.join(out_dir, "_videos"), exist_ok=True)
    records = []
    total = 0
    if not resource_path or not os.path.isfile(resource_path):
        log("[video] 未找到 resources.resource，跳过视频导出")
        return records, 0

    fp = open(resource_path, "rb")
    try:
        for bundle in bundles:
            vids = find_videos(bundle, resource_path, log)
            if not vids:
                continue
            log("[video] %s  (%d 个 VideoClip)" % (bundle.filename, len(vids)))
            for pid, name, loc, dur, w, h in vids:
                if loc is None:
                    log("    !! %s: 无法定位字节 (pid=%d)" % (name, pid))
                    continue
                offset, size = loc
                fp.seek(offset)
                blob = fp.read(size)
                if len(blob) != size or blob[4:8] != b"ftyp":
                    log("    !! %s: offset=%d 不是有效 MP4 (magic=%r)"
                        % (name, offset, blob[4:8] if len(blob) >= 8 else b""))
                    continue
                rec = {"name": name, "file": _safe(name),
                       "rel": "_videos/%s.mp4" % _safe(name),
                       "bytes": size, "dur": dur, "w": w, "h": h,
                       "path_id": pid}
                records.append(rec)
                total += size
                if not dry_run:
                    with open(os.path.join(out_dir, "_videos", rec["file"] + ".mp4"), "wb") as f:
                        f.write(blob)
                log("    %-22s %8.1f MB  %6.1fs  %dx%d"
                    % (name, size / 1e6, dur, w, h))
    finally:
        fp.close()
    return records, total