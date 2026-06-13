#!/usr/bin/env python3
"""Strip semi-transparent white halo from every sprite in out/ and write to out_clean/.

Nano Banana's "transparent background" output is actually a soft-edged near-white
matte with low-alpha pixels. rembg cleanly cuts the cat silhouette.

Usage:
    python clean_alpha.py             # process all
    python clean_alpha.py walk_01     # one file
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image
from rembg import remove, new_session

ROOT = Path(__file__).parent
SRC = ROOT / "out"
DST = ROOT / "out_clean"

# u2netp is the lightest U2Net variant — plenty for a single subject on near-uniform bg.
SESSION = new_session("u2netp")


def clean_one(name: str) -> None:
    src_path = SRC / f"{name}.png"
    if not src_path.exists():
        print(f"missing {src_path}")
        return
    img = Image.open(src_path).convert("RGBA")
    cleaned = remove(img, session=SESSION)
    DST.mkdir(exist_ok=True)
    out_path = DST / f"{name}.png"
    cleaned.save(out_path)
    print(f"  {name}: {src_path.stat().st_size // 1024}KB -> {out_path.stat().st_size // 1024}KB")


def main() -> None:
    if len(sys.argv) > 1:
        targets = sys.argv[1:]
    else:
        targets = [p.stem for p in sorted(SRC.glob("*.png"))]
    print(f"cleaning {len(targets)} sprites with u2netp...")
    for name in targets:
        clean_one(name)


if __name__ == "__main__":
    main()
