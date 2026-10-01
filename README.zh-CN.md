# hira-cg-extractor

<p align="center">
  <a href="README.zh-CN.md"><img src="https://img.shields.io/badge/lang-简体中文-EE4D2B?style=flat-square" alt="简体中文"></a>
  <a href="README.md"><img src="https://img.shields.io/badge/lang-English-4285F4?style=flat-square" alt="English"></a>
</p>

> **状态**：个人自用工具，按需更新。不承诺支持与维护时效，Issue 可能长期不回复。欢迎自行 Fork 改进。

从 Unity 引擎打包的游戏目录里，把美术资源和视频提取出来，生成一个能离线浏览的画廊页面。

最初是为了备份《Hira Hira Hihiru》的 CG 而写的，后来把游戏相关的硬编码去掉了，对大多数 Unity 游戏都能用。

**完全没用过命令行？** 直接看 [新手教程](#新手教程)，每一步都有截图级别的说明，不需要任何基础。

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

---

## 新手教程

本节以 Windows 为例，**假设你从没打开过命令行**。
已经熟悉的可以直接跳到 [完整参数说明](#完整参数说明)。

### 需要准备什么

| | |
|---|---|
| 游戏 | 已安装，**运行本工具时要完全退出** |
| Python | 3.8 或更新版本 |
| 约 2 分钟 | 提取本身大概就这个时间 |
| 约 1 GB 磁盘空间 | 存放导出的结果 |

---

### 第 0 步 · 确认 Python 有没有装

打开命令行，输入：

```bash
python --version
```

看到类似 `Python 3.13.14` 就没问题，继续往下。

**如果提示「不是内部或外部命令」：**

1. 打开 <https://www.python.org/downloads/>
2. 点那个黄色的 **Download Python 3** 大按钮
3. 运行安装程序
4. ⚠️ **在安装向导的第一个页面，勾上 "Add python.exe to PATH" 这个选项**
   再点 *Install now*。这个勾很容易漏，漏了后面全都跑不起来。
5. **重新开一个**命令行窗口（老窗口读不到新的 PATH），再试一次

> 有些 Windows 只装了叫 `py` 的启动器。如果 `python` 不行，就试 `py --version`，
> 并把下面所有命令里的 `python` 换成 `py`。

---

### 第 1 步 · 下载代码

在本项目的 GitHub 页面上：

1. 点右上角绿色的 **`< > Code`** 按钮（在文件列表上方）
2. 点 **Download ZIP**

解压。你会得到一个叫 `hira-cg-extractor-main` 的文件夹。

> 想要的话可以把它改名成 `hira-cg-extractor`，命令能短一点。不是必须的。

---

### 第 2 步 · 在这个文件夹里打开命令行

**这一步是新手最容易卡住的地方。** 你需要让命令行「站在」这个项目文件夹里。

**最简单的办法：** 用文件资源管理器打开 `hira-cg-extractor-main`，
在空白处**点右键**。如果菜单里有 **"在终端中打开"**（或 "Open in Terminal"），
直接点它。

**如果右键菜单里没有：** 从开始菜单打开终端 / PowerShell / 命令提示符，然后输入：

```bash
cd C:\Users\你的用户名\Downloads\hira-cg-extractor-main
```

（路径换成你自己的。`cd` 就是「切换目录」的意思。）

如果成功了，命令行提示符末尾会显示这个文件夹名。

---

### 第 3 步 · 安装依赖

```bash
python -m venv venv
venv\Scripts\pip install -r requirements.txt
```

这一步会下载 UnityPy 和 Pillow，大约 1 分钟。

**venv 是什么？** 「虚拟环境」其实就是给这个项目单独建一个文件夹，
把它的依赖装在里面。这样就不会和你电脑上别的 Python 项目互相干扰，
而且以后想卸载，直接把这个文件夹删掉就行，不留垃圾。

> **macOS / Linux** 的第二行要用斜杠、`bin` 而不是 `Scripts`：
> `venv/bin/pip install -r requirements.txt`

---

### 第 4 步 · 先「干跑」一次

```bash
venv\Scripts\python hira_cg.py --game-dir "D:\Steam\steamapps\common\Hira Hira Hihiru" --dry-run
```

把路径换成你自己的游戏目录。干跑会告诉你「将会导出多少张图」，
**但一个文件都不会写**，所以完全安全。

如果路径填错了，会明确报「未能定位 Unity `_Data` 目录」——
这就是这步存在的意义。

---

### 第 5 步 · 正式提取

```bash
venv\Scripts\python hira_cg.py --game-dir "D:\Steam\steamapps\common\Hira Hira Hihiru" --profile hihiru --out-dir "./cg_out"
```

⚠️ **先把游戏关掉。** 正在运行的游戏会锁住数据文件，工具读不出来。

一个 4 GB 左右的游戏，这一步大约 2 分钟。

---

### 第 6 步 · 看结果

打开 `cg_out` 文件夹，**双击 `index.html`**，浏览器会打开画廊：
可以搜索、分组筛选、点击看大图。

大功告成。图片就放在它旁边的 `resources\`、`sharedassets0\` 等目录里。

---

### ⚠️ 新手最容易踩的两个坑

**1. 千万不要双击 `hira_cg.py`。**
双击会让它在一个命令行窗口里运行，而这个窗口在执行结束的瞬间就关闭了——
所以一旦出错，你什么都看不到，只会觉得「点了没反应」。
**永远要在命令行里敲命令**，这样才能看到输出。

**2. 命令一定要在项目文件夹里敲。**
这就是第 2 步 `cd` 的作用。如果你不在那个目录，
`pip install -r requirements.txt` 会报「找不到文件」。

---

## 常见报错对照表

| 你看到的 | 意思 | 怎么办 |
|---|---|---|
| `'python' 不是内部或外部命令` | 没装 Python，或没进 PATH | 重做第 0 步 |
| `No module named 'PIL'` | 依赖没装 | 重做第 3 步 |
| `No module named 'UnityPy'` | 依赖没装 | 重做第 3 步 |
| `can't open file 'requirements.txt'` | 不在项目文件夹里 | 重做第 2 步 |
| `the following arguments are required: --game-dir` | 忘了给游戏路径 | 补上 `--game-dir "游戏路径"` |
| `未能定位 Unity *_Data 目录` | 游戏路径填错 | 试试 `--data-dir "...\_Data"` |
| `Permission denied` / 文件被占用 | 游戏还在运行 | 关掉，或在任务管理器里结束 `GameName.exe` |
| 窗口一闪就没了 | 你双击了 .py | 改用命令行 |

---

## 完整参数说明

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

更多用法：

```bash
# 只要纹理，不导视频
venv\Scripts\python hira_cg.py --game-dir "D:\...\Game" --no-video

# 直接指定 _Data 目录，跳过自动探测
venv\Scripts\python hira_cg.py --data-dir "D:\...\Game_Data" --out-dir ./cg_out

# 只要 PNG，不要画廊页面
venv\Scripts\python hira_cg.py --game-dir "D:\...\Game" --no-gallery
```

### 命名分组 profile

不同游戏的资源命名习惯不一样，`--profile` 决定怎么把文件名归类到画廊的分组里：

- `generic`（默认）：`ev*`/`cg*` → 事件 CG，`bg*` → 场景背景，`chapter*` → 章节标题，其余归到 UI/特效
- `hihiru`：针对《Hira Hira Hihiru》调过

要适配新游戏，在 `unitypack/naming.py` 里加一个 `Profile` 就行。

---

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

---

## 关于「有几张图没导出来」

如果你看到 log 里少数条目失败，先看它们的宽高：

- **宽高 `0x0`** —— 多半是 TextMeshPro 的动态字体图集。它们在游戏构建时就是空的，运行时才现场往里渲染文字，磁盘上根本没有像素可导。**这不是提取失败。**
- **其它原因** —— 才是真的失败，`export.log` 的「失败明细」里会写具体报错。

---

## 法律与使用范围

本项目**只分发工具代码**，不包含任何游戏素材。

- 请仅用于**备份你自己购买、且你拥有合法使用权**的游戏内容，供个人留存。
- 提取出的图片、音视频、剧本等，**版权归各自权利人所有**（例如《Hira Hira Hihiru》属 Aniplex）。
- **不要**把提取出的素材上传到任何公共仓库、网盘或再分发。
- 各游戏的 EULA 可能有额外条款，请自行确认后再使用。

同类开源工具可参考 [AssetStudio](https://github.com/AssetRipper/AssetStudio) 和 [AssetRipper](https://github.com/AssetRipper/AssetRipper)。

---

## 原理

Unity 把游戏资源打包成若干 `.assets` 文件，结构为「metadata + 外部数据」两部分：

- `.assets` —— 对象目录，记录每个对象的路径 ID、类型、偏移和大小
- `.assets.resS` / `.resource` —— 大块二进制数据（纹理像素、音频、视频），由 `.assets` 按 offset/size 引用

`UnityPy` 负责解析这套结构。本项目在其之上做了三件事：

1. 枚举全部 `Texture2D` 并解码成通用位图
2. 识别同名多分辨率，分辨原图与缩略图
3. 定位 `VideoClip` 的字节区间（优先用解析器给出的 offset/size，回退到手解原始数据，再回退到扫描 MP4 的 `ftyp` box 签名）

---

## License

MIT，见 [LICENSE](LICENSE)。
