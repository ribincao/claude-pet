#!/usr/bin/env python3
"""Batch regen multi-frame "subtle change" animations via gpt-image-2 edit mode.

Strategy: take an existing good base sprite and edit it into N near-identical
variants. gpt-image-2's edit endpoint preserves body/pose extremely well, which
is exactly what we need for blinks (idle) and breathing (sleep).
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
MODEL = os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-2")
TARGET = 512


# (source_name, dest_name, change_description) tuples.
# Always edit FROM the same base — that's the consistency anchor.
JOBS = [
    # ---- idle blink cycle (6 frames around idle_01) ----
    ("idle_01", "idle_02", "eyes 60% open, a soft squint as the blink starts. Otherwise identical to source."),
    ("idle_01", "idle_03", "eyes 25% open, almost fully closed mid-blink. Otherwise identical to source."),
    ("idle_01", "idle_04", "both eyes softly closed (full blink), eyelashes faintly visible. Otherwise identical."),
    ("idle_01", "idle_05", "eyes 25% open, reopening from a blink. Otherwise identical to source."),
    ("idle_01", "idle_06", "eyes 60% open, almost fully open after a blink. Otherwise identical to source."),

    # ---- sleep breathing cycle (4 frames around sleep_01) ----
    ("sleep_01", "sleep_02", "chest very slightly expanded (mid inhale). Body curl, head, paws all unchanged."),
    ("sleep_01", "sleep_03", "chest at peak inhale, slightly larger silhouette. Body curl identical otherwise."),
    ("sleep_01", "sleep_04", "chest very slightly contracted (exhale). Body curl, head, paws all unchanged."),

    # ---- walk: intermediate transition frames between walk_01 and walk_03 ----
    # walk_01 = front-RIGHT stride extended; walk_03 = front-LEFT stride extended.
    # walk_02 sits between them (legs mid-swap). walk_04 sits between walk_03 and the loop back to walk_01.
    ("walk_01", "walk_02", "the cat is mid-walk transition: front-right paw lowering toward ground, back-left paw mid-swing forward, front-left paw beginning to lift, back-right paw still planted. All four legs in clearly different positions from a standing pose. Same side view, same character, same fur and tail."),
    ("walk_03", "walk_04", "the cat is mid-walk transition: front-left paw lowering toward ground, back-right paw mid-swing forward, front-right paw beginning to lift, back-left paw still planted. All four legs clearly mid-motion (not standing). Same side view, same character."),

    # ---- walk: insert 4 more in-between frames for an 8-frame cycle ----
    # Cycle order will be: 01 → 05 → 02 → 06 → 03 → 07 → 04 → 08 → loop.
    ("walk_01", "walk_05", "the cat just after maximum-right stride: front-right paw still extended but slightly lower toward ground, back-left paw still extended back, body just barely starting to shift forward. Legs CLEARLY in motion (not standing). Same character, same side view."),
    ("walk_03", "walk_06", "the cat approaching maximum-left stride: front-left paw extending forward but not yet fully extended, back-right paw lifting and starting to swing back, body shifting weight onto right-front. Legs CLEARLY in motion. Same character."),
    ("walk_03", "walk_07", "the cat just after maximum-left stride: front-left paw still extended but slightly lower toward ground, back-right paw still extended back, body just barely starting to shift forward. Legs CLEARLY in motion. Same character."),
    ("walk_01", "walk_08", "the cat approaching maximum-right stride: front-right paw extending forward but not yet fully extended, back-left paw lifting and starting to swing back, body shifting weight onto left-front. Legs CLEARLY in motion. Same character."),
]


def edit_one(client: OpenAI, src_name: str, dst_name: str, instruction: str) -> bool:
    src_path = OUT / f"{src_name}.png"
    if not src_path.exists():
        print(f"  ! missing source {src_path}")
        return False

    prompt = (
        f"Modify the attached image: {instruction}\n\n"
        "CRITICAL: Everything else (body pose, position, fur color and pattern, "
        "tail, head angle) must remain EXACTLY IDENTICAL to the source. Do NOT "
        "shift, rotate, or re-pose the body. Output a clean image at the same "
        "composition and camera angle, square 1:1."
    )

    with src_path.open("rb") as f:
        resp = client.images.edit(
            model=MODEL,
            image=f,
            prompt=prompt,
            n=1,
            size="1024x1024",
        )

    b64 = resp.data[0].b64_json
    img = Image.open(io.BytesIO(base64.b64decode(b64))).convert("RGBA").resize((TARGET, TARGET), Image.LANCZOS)
    dst_path = OUT / f"{dst_name}.png"
    img.save(dst_path)
    print(f"  ✓ {dst_name}")
    return True


def main() -> None:
    load_dotenv(ROOT / ".env")
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"], timeout=300.0)

    only = set(sys.argv[1:]) if len(sys.argv) > 1 else None
    print(f"model={MODEL}, jobs={len(JOBS) if not only else len(only)}")

    for src, dst, change in JOBS:
        if only and dst not in only:
            continue
        print(f"→ {src} → {dst}")
        try:
            edit_one(client, src, dst, change)
        except Exception as e:
            print(f"  ! error: {e}")


if __name__ == "__main__":
    main()
