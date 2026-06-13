#!/usr/bin/env python3
"""Generate Ragdoll cat sprite set via Gemini 2.5 Image (Nano Banana).

Usage:
    python generate.py                  # generate all 12 sprites
    python generate.py walk_01          # generate just one
    python generate.py walk_01 walk_02  # generate a subset
    python generate.py --list           # list known state names
"""
from __future__ import annotations

import argparse
import io
import os
import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv
from PIL import Image
import pillow_heif

from google import genai

pillow_heif.register_heif_opener()

ROOT = Path(__file__).parent
REFS_DIR = ROOT / "refs"
PROMPTS_DIR = ROOT / "prompts"
OUT_DIR = ROOT / "out"

DEFAULT_MODEL = "gemini-2.5-flash-image"
TARGET_SIZE = 512
REF_MAX_EDGE = 1024


def load_base_prompt() -> str:
    return (PROMPTS_DIR / "base.md").read_text(encoding="utf-8").strip()


def load_states() -> dict[str, str]:
    with (PROMPTS_DIR / "states.yaml").open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_refs() -> list[Image.Image]:
    exts = ("*.jpg", "*.jpeg", "*.png", "*.webp", "*.heic")
    paths: list[Path] = []
    for ext in exts:
        paths.extend(REFS_DIR.glob(ext))
        paths.extend(REFS_DIR.glob(ext.upper()))
    paths = sorted(set(paths))
    if not paths:
        sys.exit(f"no reference photos in {REFS_DIR} — drop 10+ photos of your cat there first")

    refs: list[Image.Image] = []
    for p in paths:
        img = Image.open(p).convert("RGB")
        img.thumbnail((REF_MAX_EDGE, REF_MAX_EDGE), Image.LANCZOS)
        refs.append(img)
    return refs


def gen_one(
    client: genai.Client,
    model: str,
    base_prompt: str,
    name: str,
    pose: str,
    refs: list[Image.Image],
) -> Image.Image | None:
    prompt = f"{base_prompt}\n\nPOSE FOR THIS SPRITE ({name}):\n{pose}"
    contents = [prompt, *refs]

    resp = client.models.generate_content(model=model, contents=contents)

    for part in resp.candidates[0].content.parts:
        inline = getattr(part, "inline_data", None)
        if inline and inline.data:
            img = Image.open(io.BytesIO(inline.data)).convert("RGBA")
            return img.resize((TARGET_SIZE, TARGET_SIZE), Image.LANCZOS)
    return None


def main() -> None:
    load_dotenv(ROOT / ".env")
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        sys.exit("GEMINI_API_KEY not set — copy .env.example to .env and paste your key")

    model = os.environ.get("GEMINI_MODEL", DEFAULT_MODEL)

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("states", nargs="*", help="state names to generate (default: all)")
    parser.add_argument("--list", action="store_true", help="list known state names and exit")
    args = parser.parse_args()

    states = load_states()

    if args.list:
        for name in states:
            print(name)
        return

    OUT_DIR.mkdir(exist_ok=True)
    base = load_base_prompt()
    refs = load_refs()
    print(f"loaded {len(refs)} reference images, model={model}")

    targets = args.states or list(states)
    unknown = [s for s in targets if s not in states]
    if unknown:
        sys.exit(f"unknown state(s): {', '.join(unknown)}. Run with --list to see valid names.")

    client = genai.Client(api_key=api_key)

    for name in targets:
        pose = states[name]
        print(f"→ {name}")
        try:
            img = gen_one(client, model, base, name, pose, refs)
        except Exception as e:
            print(f"  error: {e}")
            continue
        if img is None:
            print("  no image returned in response — skipping")
            continue
        out_path = OUT_DIR / f"{name}.png"
        img.save(out_path)
        print(f"  saved {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
