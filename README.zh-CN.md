# hira-cg-extractor

<p align="center">
  <a href="README.zh-CN.md"><img src="https://img.shields.io/badge/lang-简体中文-EE4D2B?style=flat-square" alt="简体中文"></a>
  <a href="README.md"><img src="https://img.shields.io/badge/lang-English-4285F4?style=flat-square" alt="English"></a>
</p>

> **状态**：个人自用工具，按需更新。不承诺支持与维护时效，Issue 可能长期不回复。欢迎自行 Fork 改进。

从 Unity 引擎打包的游戏目录里，把美术资源和视频提取出来，生成一个能离线浏览的画廊页面。

最初是为了备份《Hira Hira Hihiru》的 CG 而写的，后来把游戏相关的硬编码去掉了，对大多数 Unity 游戏都能用。

---

## 它做什么

- 扫描 `<游戏目录>/<游戏>_Data/`，自动找出所有 `.assets` 和 `level*` 资源文件
- 解析每个 `Texture2D`，导出为 **PNG**（无损）
- 为每张图生成一张 **缩略图 JPEG**，供画廊使用
- 定位 `VideoClip` 在 `resources.resource` 里的原始字节，按 offset/size 原样切出 **MP4**（不重新编码）
- 输出一份 `index.html` 画廊：分组筛选、搜索、点击看原图、视频播放
- 输出一份 `inventory.csv` 清单，列出每条资源的来源、路径 ID、分辨率、像素格式

## 它不做什么

- 不解密、不修改、不重打包游戏的任何文件，全程**只读**
- 不处理音频（脚本没做这个需求）
- 不合并同一场景的分层立绘

## 环境要求

- Python 3.8+
- 依赖：`UnityPy`、`Pillow`

```bash
pip install -r requirements.txt
```

## 用法

最常见的情况——给游戏目录，让它自己找 `_Data`：

```bash
python hira_cg.py --game-dir "D:\Steam\steamapps\common\Hira Hira Hihiru" --out-dir ./cg_out
```

先干跑看看会导出什么，**不写任何文件**（推荐第一次都先来一发）：

```bash
python hira_cg.py --game-dir "D:\...\Hira Hira Hihiru" --dry-run
```

其它用法：

```bash
# 直接指定 _Data 目录，跳过自动探测
python hira_cg.py --data-dir "D:\...\Hira Hira Hihiru_Data" --out-dir ./cg_out

# 只想看纹理，不碰视频
python hira_cg.py --game-dir <游戏目录> --no-video

# 用针对特定游戏的命名分组（见下）
python hira_cg.py --game-dir <游戏目录> --profile hihiru

# 不要画廊，只出 PNG
python hira_cg.py --game-dir <游戏目录> --no-gallery
```

完整参数：

| 参数 | 说明 |
|---|---|
| `--game-dir` | 游戏目录（含 `.exe` 或 `*_Data` 的那一层）。必填，除非给了 `--data-dir` |
| `--data-dir` | 直接指定 `*_Data` 目录 |
| `--out-dir` | 输出目录，默认 `./cg_out` |
| `--profile` | 命名分组：`generic`（默认）/ `hihiru` |
| `--no-video` | 跳过视频 |
| `--no-gallery` | 不生成 `index.html` |
| `--dry-run` | 只统计，不写文件 |
| `--quiet` | 精简输出 |

### 命名分组 profile

不同游戏的资源命名习惯不一样，`--profile` 决定怎么把文件名归类到画廊的分组里：

- `generic`（默认）：`ev*`/`cg*` → 事件 CG，`bg*` → 场景背景，`chapter*` → 章节标题，其余归到 UI/特效
- `hihiru`：针对《Hira Hira Hihiru》调过

要适配新游戏，在 `unitypack/naming.py` 里加一个 `Profile` 就行。

## 输出长什么样

```
cg_out/
├─ resources/         <源文件名>.assets 里导出的 PNG
├─ sharedassets0/     ...按源文件分目录，避免同名冲突
├─ _thumbs/           画廊缩略图 JPEG
├─ _videos/           切出来的 MP4
├─ index.html         双击打开
├─ manifest.json      结构化清单
├─ inventory.csv      逐条明细，便于核对
└─ export.log         运行摘要 + 失败明细
```

同一张图如果在游戏里存了多个尺寸（常见于 CG 画廊缩略图），小的那张会自动加 `_thumb` 后缀。

## 关于「有几张图没导出来」

如果你看到 log 里少数条目失败，先看它们的宽高：

- **宽高 `0x0`** —— 多半是 TextMeshPro 的动态字体图集。它们在游戏构建时就是空的，运行时才现场往里渲染文字，磁盘上根本没有像素可导。**这不是提取失败。**
- **其它原因** —— 才是真的失败，`export.log` 的「失败明细」里会写具体报错。

## 法律与使用范围

本项目**只分发工具代码**，不包含任何游戏素材。

- 请仅用于**备份你自己购买、且你拥有合法使用权**的游戏内容，供个人留存。
- 提取出的图片、音视频、剧本等，**版权归各自权利人所有**（例如《Hira Hira Hihiru》属 Aniplex）。
- **不要**把提取出的素材上传到任何公共仓库、网盘或再分发。
- 各游戏的 EULA 可能有额外条款，请自行确认后再使用。

同类开源工具可参考 [AssetStudio](https://github.com/AssetRipper/AssetStudio) 和 [AssetRipper](https://github.com/AssetRipper/AssetRipper)。

## 原理

Unity 把游戏资源打包成若干 `.assets` 文件，结构为「metadata + 外部数据」两部分：

- `.assets` —— 对象目录，记录每个对象的路径 ID、类型、偏移和大小
- `.assets.resS` / `.resource` —— 大块二进制数据（纹理像素、音频、视频），由 `.assets` 按 offset/size 引用

`UnityPy` 负责解析这套结构。本项目在其之上做了三件事：

1. 枚举全部 `Texture2D` 并解码成通用位图
2. 识别同名多分辨率，分辨原图与缩略图
3. 定位 `VideoClip` 的字节区间（优先用解析器给出的 offset/size，回退到手解原始数据，再回退到扫描 MP4 的 `ftyp` box 签名）

## License

MIT，见 [LICENSE](LICENSE)。
