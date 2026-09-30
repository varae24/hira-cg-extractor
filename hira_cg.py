#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
hira-cg-extractor —— Unity 游戏美术资源提取器

从 Unity 引擎打包的游戏目录中提取纹理（CG / 背景 / 立绘 / UI）与视频，
输出 PNG/JPEG/MP4 和一个可离线浏览的 index.html 画廊。

仅供个人备份自己已购游戏使用；素材版权归原厂所有，请勿传播或再分发。

用法见 --help，或阅读 README.md。
"""

import argparse
import os
import sys
import time

from unitypack import images as images_mod
from unitypack import videos as videos_mod
from unitypack import gallery as gallery_mod
from unitypack import report as report_mod
from unitypack import reader
from unitypack import naming


def build_parser():
    p = argparse.ArgumentParser(
        prog="hira-cg-extractor",
        description="提取 Unity 游戏的美术资源与视频，生成离线画廊。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""示例:
  # 自动定位游戏目录
  python hira_cg.py --game-dir "D:\\Steam\\steamapps\\common\\Hira Hira Hihiru" --out-dir ./out

  # 先干跑看看会导出什么，不写文件
  python hira_cg.py --game-dir <游戏目录> --dry-run

  # 用针对该游戏的命名分组
  python hira_cg.py --game-dir <游戏目录> --profile hihiru --out-dir ./cg
""")
    p.add_argument("--game-dir", required=True,
                   help="游戏目录（含 .exe 或 *_Data 的那一层）")
    p.add_argument("--data-dir", default=None,
                   help="直接指定 *_Data 目录（给了就忽略 --game-dir 的自动探测）")
    p.add_argument("--out-dir", default="./cg_out",
                   help="输出目录，默认 ./cg_out")
    p.add_argument("--profile", default="generic",
                   help="命名分组 profile: generic | hihiru（默认 generic）")
    p.add_argument("--no-video", action="store_true",
                   help="跳过视频提取")
    p.add_argument("--no-gallery", action="store_true",
                   help="不生成 index.html")
    p.add_argument("--dry-run", action="store_true",
                   help="只统计和打印将要导出的内容，不写任何文件")
    p.add_argument("--quiet", action="store_true", help="精简输出")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    log = (lambda *a, **k: None) if args.quiet else print
    t0 = time.time()

    # —— 定位数据目录 ——
    data_dir = args.data_dir or reader.find_data_dir(args.game_dir)
    if not data_dir or not reader.is_data_dir(data_dir):
        print("错误：未能定位 Unity *_Data 目录。\n"
              "请用 --data-dir 直接指定，或检查 --game-dir 是否正确。", file=sys.stderr)
        return 2
    log("[data] %s" % data_dir)

    profile = naming.get_profile(args.profile)
    out_dir = os.path.abspath(args.out_dir)
    os.makedirs(out_dir, exist_ok=True)

    # —— 打开所有资源文件 ——
    files = reader.list_source_files(data_dir)
    log("[scan] %d 个资源文件" % len(files))
    bundles, failed_files = reader.load_all(data_dir, files, verbose=not args.quiet)

    try:
        # —— 导出纹理 ——
        if args.dry_run:
            log("[dry-run] 统计纹理 ...")
            n_tex = sum(len(b.textures()) for b in bundles)
            log("[dry-run] 共 %d 个 Texture2D，将导出到 %s" % (n_tex, out_dir))
            n_vid = sum(len(b.videos()) for b in bundles)
            log("[dry-run] 共 %d 个 VideoClip" % n_vid)
            return 0

        img_records, img_ok, img_fail, img_errors, img_dt = \
            images_mod.export_all(bundles, out_dir, log=log)
        log("[image] 完成 ok=%d fail=%d  用时 %.1fs" % (img_ok, img_fail, img_dt))

        # —— 导出视频 ——
        vid_records = []
        if not args.no_video:
            res = os.path.join(data_dir, "resources.resource")
            vid_records, _ = videos_mod.export_videos(bundles, res, out_dir, log=log)

        # —— 分组 ——
        for r in img_records:
            r["group"], _ = profile.classify(r["name"])

        # —— 报告 + 画廊 ——
        report_mod.write_inventory(out_dir, img_records, vid_records)
        report_mod.write_log(out_dir, {
            "data_dir": data_dir,
            "img_ok": img_ok, "img_fail": img_fail,
            "elapsed": time.time() - t0,
        }, img_records, vid_records, img_errors)

        if not args.no_gallery:
            idx, n, total = gallery_mod.build_gallery(
                out_dir, img_records, vid_records,
                title=os.path.basename(data_dir))
            log("[gallery] %s  (%d 项, %.1f MB)" % (idx, n, total / 1e6))

        log("\n完成：纹理 %d / 失败 %d，视频 %d，用时 %.1fs"
            % (img_ok, img_fail, len(vid_records), time.time() - t0))
        log("输出目录：%s" % out_dir)
        if failed_files:
            log("（%d 个资源文件未能解析，已跳过）" % len(failed_files))
        return 0
    finally:
        for b in bundles:
            b.close()


if __name__ == "__main__":
    sys.exit(main())