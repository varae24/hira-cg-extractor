# hira-cg-extractor

<p align="center">
  <a href="README.md"><img src="https://img.shields.io/badge/lang-English-4285F4?style=flat-square" alt="English"></a>
  <a href="README.zh-CN.md"><img src="https://img.shields.io/badge/lang-简体中文-EE4D2B?style=flat-square" alt="简体中文"></a>
</p>

> **Status**: Personal utility, updated as needed. No commitment to support
> turnaround times — issues may go unanswered. Contributions via fork are welcome.

Extract art assets and videos out of Unity-engine games, and turn them into an
offline-browsable gallery.

It started as a way to back up the CGs of *Hira Hira Hihiru*; the game-specific
hardcoding was later removed, so it now works with most Unity titles.

**New to this?** Jump straight to [Getting Started](#getting-started) — it walks
you through every step, assuming you have never run a Python script before.

---

## What it does

- Scans `<game>/<Game>_Data/` and picks up every `.assets` and `level*` file
- Decodes each `Texture2D` into a lossless **PNG**
- Generates a **JPEG thumbnail** per image for the gallery
- Locates each `VideoClip` byte range inside `resources.resource` and carves out
  the original **MP4** (no re-encoding)
- Writes an `index.html` gallery: grouping, search, click-to-view, video playback
- Writes an `inventory.csv` manifest and an `export.log` summary

## What it does not do

- It never modifies, decrypts or repacks the game — **read-only throughout**
- Audio extraction is not implemented
- It does not composite layered character sprites back into a single image

---

## Getting Started

This section assumes Windows and that you have never used a terminal before.
If you already know your way around, skip to [Options reference](#options-reference).

### What you need

| | |
|---|---|
| The game | Installed and **closed** when you run the tool |
| Python | 3.8 or newer |
| About 2 minutes | The extraction itself takes roughly that long |
| ~1 GB free disk | For the output |

---

### Step 0 — Check that Python is installed

Open a terminal and run:

```bash
python --version
```

If you see something like `Python 3.13.14`, you're good — move on.

**If it says `'python' is not recognized`:**

1. Go to <https://www.python.org/downloads/>
2. Click the big yellow **Download Python 3** button
3. Run the installer
4. ⚠️ **On the very first screen, tick the box that says "Add python.exe to PATH"**
   before clicking *Install now*. This is easy to miss and everything breaks
   without it.
5. Open a **new** terminal window (the old one won't see the new PATH) and check
   again

> Some Windows setups only provide a launcher called `py` instead of `python`.
> If `python` fails, try `py --version` and use `py` in all the commands below.

---

### Step 1 — Get the code

On the GitHub page of this repository:

1. Click the green **`< > Code`** button (top right, above the file list)
2. Click **Download ZIP**

Unzip it. You now have a folder named `hira-cg-extractor-main`.

> Rename it to just `hira-cg-extractor` if you like — it makes the commands below
> shorter. Not required.

---

### Step 2 — Open a terminal inside that folder

This is the step beginners get stuck on. You need the terminal to be *pointing
at* the project folder.

**Easiest way:** open File Explorer, navigate into `hira-cg-extractor-main`,
then **right-click on an empty area**. If you see **"Open in Terminal"** (or
"Open in PowerShell"), click it.

**Alternative:** open Terminal / PowerShell / Command Prompt from the Start menu,
then type:

```bash
cd C:\Users\YourName\Downloads\hira-cg-extractor-main
```

(Adjust the path. `cd` just means "change directory".)

You'll know it worked if the prompt now ends with the folder name.

---

### Step 3 — Install the dependencies

```bash
python -m venv venv
venv\Scripts\pip install -r requirements.txt
```

This downloads UnityPy and Pillow. Takes about a minute.

**What is a `venv`?** A "virtual environment" is just a private folder holding
this project's own copy of its dependencies. It keeps them from tangled up with
other Python projects on your machine, and deleting the folder uninstalls
everything cleanly — no leftovers.

> **On macOS / Linux**, the second line uses a forward slash and `bin` instead of
> `Scripts`: `venv/bin/pip install -r requirements.txt`

---

### Step 4 — Do a dry run first

```bash
venv\Scripts\python hira_cg.py --game-dir "D:\Steam\steamapps\common\Hira Hira Hihiru" --dry-run
```

Replace the path with your actual game folder. A dry run reports what *would* be
exported and **writes nothing at all**, so it's completely safe.

If the path is wrong you'll get a clear "could not locate the Unity `_Data`
directory" error — that's the point of doing this step first.

---

### Step 5 — Extract for real

```bash
venv\Scripts\python hira_cg.py --game-dir "D:\Steam\steamapps\common\Hira Hira Hihiru" --profile hihiru --out-dir "./cg_out"
```

⚠️ **Close the game first.** A running game locks its data files and the tool
won't be able to read them.

On a 4 GB game this takes roughly two minutes.

---

### Step 6 — View the results

Open the `cg_out` folder and **double-click `index.html`**. It opens in your
browser: a browsable gallery with search, grouping, and click-to-view.

That's it. The images sit alongside it in `resources/`, `sharedassets0/`, etc.

---

### ⚠️ Two rules that trip people up

**1. Never double-click `hira_cg.py`.** Double-clicking runs it in a console
window that closes the instant it finishes — so if it errors, you see nothing
and it looks like "nothing happened". Always type the commands in a terminal
where you can read the output.

**2. Always type commands inside the project folder.** That's what the `cd` in
Step 2 was for. Commands like `pip install -r requirements.txt` fail with
"can't open file" if you're in the wrong directory.

---

## Common errors

| What you see | What it means | How to fix |
|---|---|---|
| `'python' is not recognized` | Python isn't installed, or isn't on PATH | Redo Step 0 |
| `No module named 'PIL'` | Dependencies not installed | Redo Step 3 |
| `No module named 'UnityPy'` | Dependencies not installed | Redo Step 3 |
| `can't open file 'requirements.txt'` | You're in the wrong folder | Redo Step 2 |
| `the following arguments are required: --game-dir` | You forgot the game path | Add `--game-dir "path\to\game"` |
| `Could not locate the Unity *_Data directory` | Game path is wrong | Try `--data-dir "...\_Data"` |
| `Permission denied` / file in use | The game is still running | Quit it, or end `GameName.exe` in Task Manager |
| A window flashes and disappears | You double-clicked the .py | Use a terminal instead |

---

## Options reference

| Flag | Description |
|---|---|
| `--game-dir` | Game folder (the level containing the `.exe` or `_Data`). Required unless `--data-dir` is given |
| `--data-dir` | Point straight at the `*_Data` directory |
| `--out-dir` | Output directory. Default `./cg_out` |
| `--profile` | Naming profile: `generic` (default) / `hihiru` |
| `--no-video` | Skip video extraction |
| `--no-gallery` | Do not generate `index.html` |
| `--dry-run` | Report only, write nothing |
| `--quiet` | Reduce console output |

More examples:

```bash
# Textures only, no video
venv\Scripts\python hira_cg.py --game-dir "D:\...\Game" --no-video

# Skip auto-detection and give the _Data directory directly
venv\Scripts\python hira_cg.py --data-dir "D:\...\Game_Data" --out-dir ./cg_out

# PNGs without the gallery page
venv\Scripts\python hira_cg.py --game-dir "D:\...\Game" --no-gallery
```

### Naming profiles

Naming conventions differ between games, so `--profile` decides how filenames
are bucketed into gallery groups:

- `generic` (default): `ev*` / `cg*` → Event CG, `bg*` → Background,
  `chapter*` → Chapter title, everything else → UI / Effects
- `hihiru`: tuned for *Hira Hira Hihiru*

To support another game, add a `Profile` in `unitypack/naming.py`.

---

## Output layout

```
cg_out/
├─ resources/         PNGs extracted from resources.assets
├─ sharedassets0/     ...one directory per source file, to avoid name clashes
├─ _thumbs/           gallery thumbnails (JPEG)
├─ _videos/           carved MP4s
├─ index.html         open this in a browser
├─ manifest.json      structured manifest
├─ inventory.csv      per-item detail, handy for auditing
└─ export.log         run summary and failure list
```

When the game stores the same image at several sizes (common for CG gallery
thumbnails), the smaller copies automatically get a `_thumb` suffix.

---

## "A few images didn't export"

If the log lists a handful of failures, check their dimensions first:

- **0×0** — almost certainly a TextMeshPro dynamic font atlas. These are empty
  at build time and only get filled in at runtime as text is drawn, so there are
  no pixels on disk to recover. **This is not an extraction failure.**
- Anything else is a genuine failure, with the concrete exception message
  written to the "失败明细" section of `export.log`.

---

## Legal scope

This project distributes **tool code only** and contains no game assets.

- Use it solely to back up content from games you have purchased and are
  legally entitled to, for personal retention.
- Extracted images, audio, video and scripts remain the property of their
  respective rights holders (e.g. *Hira Hira Hihiru* belongs to Aniplex).
- **Do not** upload or redistribute extracted assets to any public repository,
  file host or mirror.
- Individual games' EULAs may impose additional terms — check before use.

Comparable open-source tools: [AssetStudio](https://github.com/AssetRipper/AssetStudio)
and [AssetRipper](https://github.com/AssetRipper/AssetRipper).

---

## How it works

Unity packages game resources into `.assets` files with a "metadata + external
data" split:

- `.assets` — the object directory: path ID, type, offset and size per object
- `.assets.resS` / `.resource` — large binary blobs (texture pixels, audio,
  video) that `.assets` references by offset and size

`UnityPy` parses that structure. On top of it this project does three things:

1. Enumerate every `Texture2D` and decode it into a general-purpose bitmap
2. Detect names that appear at multiple resolutions, separating the real image
   from its gallery thumbnail
3. Locate each `VideoClip`'s byte range, trying three strategies in order:
   the offset/size from the parser, then a hand-parse of the raw VideoClip
   bytes, then a scan for the MP4 `ftyp` box signature

---

## License

MIT — see [LICENSE](LICENSE).
