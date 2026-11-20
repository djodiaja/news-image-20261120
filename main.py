"""Write the 20 November 2026 world-news page to /output/entry.png.

render.py draws the page ahead of time from the sourced stories in stories.py; this entry
only checks that page and writes its bytes, so it needs no network and never varies.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE = os.path.join(HERE, "assets", "entry.png")
TARGET = os.path.join(os.sep, "output", "entry.png")
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1 << 20  # the contest's 1 MiB cap


def main() -> int:
    with open(PAGE, "rb") as src:
        data = src.read()
    if not data.startswith(PNG_MAGIC) or len(data) > MAX_BYTES:
        sys.stderr.write("assets/entry.png is not a PNG within 1 MiB\n")
        return 1
    os.makedirs(os.path.dirname(TARGET), exist_ok=True)
    with open(TARGET, "wb") as dst:
        dst.write(data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
