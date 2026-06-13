#!/usr/bin/env python3
"""Generate a consistent walk cycle as a single 2x2 sprite sheet, then slice.

Key idea: generating all frames in ONE image forces the model to keep them
mutually consistent (same character, same scale, coherent leg progression) —
which independently-generated frames never are.

Usage:
    python walk_sheet.py            # generate sheet + slice to out/walk_s1..s4.png
"""
from __future__ import annotations

import base64
import io
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image

ROOT = Path(__file__).parent
OUT = ROOT / "out"
ANCHOR = OUT / "walk_01.png"  # character reference
TARGET = 512


PROMPT = (
    "Using the attached cat as the exact character, create a 2x2 grid sprite "
    "sheet of a SIDE-VIEW walk cycle, the cat facing RIGHT. Four frames showing "
    "one full walk gait in sequence:\n"
    "- Top-left: front-right leg reaching forward and planting, back-left leg pushing off behind.\n"
    "- Top-right: passing position, legs gathered under the body, mid-step.\n"
    "- Bottom-left: front-left leg reaching forward and planting, back-right leg pushing off behind.\n"
    "- Bottom-right: passing position again, opposite legs gathered under the body.\n\n"
    "CRITICAL: identical character, fur, size, and camera framing in all 4 cells; "
    "evenly spaced 2x2 grid, each cell the same size; pure white background; "
    "the only difference between cells is leg position. Smooth, natural cat gait."
)


def main() -> None:
    if not ANCHOR.exists():
        raise SystemExit(f"missing anchor {ANCHOR}")
    load_dotenv(ROOT / ".env")
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    model = os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-2")

    with ANCHOR.open("rb") as f:
        resp = client.images.edit(model=model, image=f, prompt=PROMPT, n=1, size="1024x1024")

    sheet = Image.open(io.BytesIO(base64.b64decode(resp.data[0].b64_json))).convert("RGBA")
    sheet.save(OUT / "_walk_sheet.png")
    print(f"sheet saved {sheet.size}")

    # slice 2x2
    w, h = sheet.size
    cw, ch = w // 2, h // 2
    cells = [(0, 0), (cw, 0), (0, ch), (cw, ch)]
    for i, (x, y) in enumerate(cells, start=1):
        cell = sheet.crop((x, y, x + cw, y + ch)).resize((TARGET, TARGET), Image.LANCZOS)
        cell.save(OUT / f"walk_s{i}.png")
        print(f"  walk_s{i}.png")


if __name__ == "__main__":
    main()
