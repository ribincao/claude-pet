#!/usr/bin/env python3
"""OpenAI gpt-image-1 image-edit variant.

Same purpose as edit_frame.py but uses OpenAI when Gemini is geo-blocked.
gpt-image-1 supports input_fidelity="high" which is exactly what we need for
pose-preserving micro-edits (blink, breathe).

Usage:
    python edit_frame_openai.py idle_01 idle_02 "both eyes softly closed"
    python edit_frame_openai.py sleep_01 sleep_02 "chest slightly contracted, exhaling"
"""
from __future__ import annotations

import base64
import io
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image

ROOT = Path(__file__).parent
OUT = ROOT / "out"


def main() -> None:
    if len(sys.argv) != 4:
        sys.exit("usage: edit_frame_openai.py <source> <dest> '<edit instruction>'")
    src_name, dst_name, instruction = sys.argv[1], sys.argv[2], sys.argv[3]
    src_path = OUT / f"{src_name}.png"
    if not src_path.exists():
        sys.exit(f"missing source: {src_path}")

    load_dotenv(ROOT / ".env")
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    prompt = (
        f"Modify this image: {instruction}.\n\n"
        "Constraints (must hold):\n"
        "- Body pose, position, fur color and pattern, tail, head angle, all "
        "expression apart from the specified change — must remain IDENTICAL "
        "to the source. Do NOT shift, rotate, or re-pose the body.\n"
        "- Background fully transparent (alpha), no white fill.\n"
        "- Same composition, same camera angle, square 1:1."
    )

    model = os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-2")
    with src_path.open("rb") as f:
        resp = client.images.edit(
            model=model,
            image=f,
            prompt=prompt,
            n=1,
            size="1024x1024",
        )

    b64 = resp.data[0].b64_json
    img = Image.open(io.BytesIO(base64.b64decode(b64))).convert("RGBA").resize((512, 512), Image.LANCZOS)
    dst_path = OUT / f"{dst_name}.png"
    img.save(dst_path)
    print(f"saved {dst_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
