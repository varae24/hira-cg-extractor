"""勘察报告：把资源清单导出成 CSV，便于人工核对 / 二次处理。"""

import csv
import json
import os
import time
from collections import Counter

from .formats import texture_format_name


def write_inventory(out_dir, images, videos, title="Unity 资源勘察清单"):
    """生成 inventory.csv（纹理+视频逐条明细）。"""
    path = os.path.join(out_dir, "inventory.csv")
    fields = ["source", "path_id", "type", "name", "width", "height",
              "tex_format", "tex_format_name", "group", "bytes", "rel"]
    rows = []
    for d in images:
        rows.append({
            "source": d.get("src", ""), "path_id": d.get("path_id", ""),
            "type": "Texture2D", "name": d.get("name", ""),
            "width": d.get("w", 0), "height": d.get("h", 0),
            "tex_format": d.get("fmt_int", ""), "tex_format_name": d.get("fmt", ""),
            "group": d.get("group", ""), "bytes": d.get("bytes", 0),
            "rel": d.get("rel", ""),
        })
    for d in videos:
        rows.append({
            "source": "resources.resource", "path_id": d.get("path_id", ""),
            "type": "VideoClip", "name": d.get("name", ""),
            "width": d.get("w", 0), "height": d.get("h", 0),
            "tex_format": "", "tex_format_name": "", "group": "视频",
            "bytes": d.get("bytes", 0), "rel": d.get("rel", ""),
        })
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    return path, len(rows)


def write_log(out_dir, meta, images, videos, errors, title="Unity 资源提取"):
    """生成人类可读的 export.log。"""
    path = os.path.join(out_dir, "export.log")
    total = sum(d.get("bytes", 0) for d in images) + sum(d.get("bytes", 0) for d in videos)
    with open(path, "w", encoding="utf-8") as f:
        f.write("%s\n%s\n" % (title, "=" * 60))
        f.write("时间      : %s\n" % time.strftime("%Y-%m-%d %H:%M:%S"))
        f.write("数据目录  : %s\n" % meta.get("data_dir", ""))
        f.write("纹理      : %d 成功 / %d 失败\n" % (meta.get("img_ok", 0), meta.get("img_fail", 0)))
        f.write("视频      : %d\n" % len(videos))
        f.write("总计      : %.1f MB\n" % (total / 1e6))
        f.write("用时      : %.1f s\n\n" % meta.get("elapsed", 0))

        f.write("分组统计:\n")
        for k, v in Counter(d.get("group", "?") for d in images).most_common():
            f.write("  %-18s %d\n" % (k, v))
        if videos:
            f.write("  %-18s %d\n" % ("视频", len(videos)))

        f.write("\n纹理格式分布:\n")
        for k, v in Counter(d.get("fmt", "?") for d in images).most_common():
            f.write("  %-20s %d\n" % (k, v))

        if errors:
            f.write("\n失败明细 (%d):\n" % len(errors))
            for e in errors:
                f.write("  %s\n" % e)
            f.write("\n注: 宽高为 0x0 的条目通常是 TextMeshPro 动态字体图集，\n"
                    "    构建时就是空的，运行时才填充，没有像素可导——非提取失败。\n")
    return path