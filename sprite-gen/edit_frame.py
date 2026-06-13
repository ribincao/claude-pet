#!/usr/bin/env python3
"""Edit an existing sprite to create a variant — pose-preserving micro-changes.

Use when you want frame_N+1 to be IDENTICAL to frame_N except for a small change
(eye blink, chest breath). 'Generate from refs' mode shifts the body pose; this
img-to-img edit mode locks it.

Usage:
    python edit_frame.py idle_01 idle_02 "both eyes gently closed (blink)"
    python edit_frame.py sleep_01 sleep_02 "chest slightly contracted (exhale)"
"""
from __future__ import annotations

import io
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from PIL import Image
import pillow_heif

from google import genai

pillow_heif.register_heif_opener()

ROOT = Path(__file__).parent
OUT = ROOT / "out"


def main() -> None:
    if len(sys.argv) != 4:
        sys.exit("usage: edit_frame.py <source_name> <dest_name> '<edit instruction>'")
    src_name, dst_name, instruction = sys.argv[1], sys.argv[2], sys.argv[3]
    src_path = OUT / f"{src_name}.png"
    if not src_path.exists():
        sys.exit(f"missing source: {src_path}")

    load_dotenv(ROOT / ".env")
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash-image")

    src = Image.open(src_path).convert("RGBA")
    prompt = (
        f"Modify the attached image as follows: {instruction}.\n\n"
        "CRITICAL CONSTRAINTS — these must be respected:\n"
        "- Everything else (body pose, position, fur color and pattern, tail, head "
        "angle, expression apart from the specified change) must remain EXACTLY "
        "IDENTICAL to the source image. Do NOT shift, rotate, or re-pose the body.\n"
        "- Background must be fully transparent (alpha channel), no white fill.\n"
        "- Same canvas size, same composition, same camera angle."
    )

    resp = client.models.generate_content(model=model, contents=[prompt, src])
    for part in resp.candidates[0].content.parts:
        inline = getattr(part, "inline_data", None)
        if inline and inline.data:
            img = Image.open(io.BytesIO(inline.data)).convert("RGBA").resize((512, 512), Image.LANCZOS)
            dst_path = OUT / f"{dst_name}.png"
            img.save(dst_path)
            print(f"saved {dst_path.relative_to(ROOT)}")
            return
    print("no image in response")


if __name__ == "__main__":
    main()
