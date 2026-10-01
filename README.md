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

## Requirements

- Python 3.8+
- Dependencies: `UnityPy`, `Pillow`

```bash
pip install -r requirements.txt
```

## Usage

The common case — point it at the game folder and let it find `_Data` itself:

```bash
python hira_cg.py --game-dir "D:\Steam\steamapps\common\Hira Hira Hihiru" --out-dir ./cg_out
```

Dry run first to see what it would export without writing anything:

```bash
python hira_cg.py --game-dir "D:\...\Hira Hira Hihiru" --dry-run
```

More examples:

```bash
# Skip auto-detection and give the _Data directory directly
python hira_cg.py --data-dir "D:\...\Hira Hira Hihiru_Data" --out-dir ./cg_out

# Textures only, no video
python hira_cg.py --game-dir <game dir> --no-video

# Use a game-specific naming profile
python hira_cg.py --game-dir <game dir> --profile hihiru

# PNGs without the gallery page
python hira_cg.py --game-dir <game dir> --no-gallery
```

Full options:

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

### Naming profiles

Naming conventions differ between games, so `--profile` decides how filenames
are bucketed into gallery groups:

- `generic` (default): `ev*` / `cg*` → Event CG, `bg*` → Background,
  `chapter*` → Chapter title, everything else → UI / Effects
- `hihiru`: tuned for *Hira Hira Hihiru*

To support another game, add a `Profile` in `unitypack/naming.py`.

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

## "A few images didn't export"

If the log lists a handful of failures, check their dimensions first:

- **0×0** — almost certainly a TextMeshPro dynamic font atlas. These are empty
  at build time and only get filled in at runtime as text is drawn, so there are
  no pixels on disk to recover. **This is not an extraction failure.**
- Anything else is a genuine failure, with the concrete exception message
  written to the "失败明细" section of `export.log`.

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

## License

MIT — see [LICENSE](LICENSE).
