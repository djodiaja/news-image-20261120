"""Entry program: copy the rendered 20 November 2026 world-news page to /output/entry.png.

The page is drawn ahead of time by render.py (from the sourced stories in stories.py),
so this run needs no network and writes the same bytes every time.
"""
import shutil
from pathlib import Path

if __name__ == "__main__":
    out = Path("/output/entry.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(Path(__file__).resolve().parent / "assets" / "entry.png", out)
