# sprite-gen

Optional Python scripts for generating still sprite frames of **your own cat** from reference photos, using image models (Gemini 2.5 Flash Image, or OpenAI's image edit models).

> **Note:** this was the original, frame-by-frame pipeline. The pet bundled in `pet-app/src/sprites/cpp/` uses three WebP sprite sheets (~60 frames each at 12 fps) and wasn't produced by these scripts. Output here is individual PNGs in `out/`. To use them in the app, pack each animation into a grid sheet and register it in `CLIPS` in [`pet.js`](../pet-app/src/pet.js) (see "Bring your own pet" in the [main README](../README.md)).

## Setup (once)

```bash
cd sprite-gen
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# then fill in GEMINI_API_KEY and/or OPENAI_API_KEY in .env
```

Put 10 or more photos of your cat in `refs/` (jpg / png / webp / heic). The more angles, poses and lighting, the better. `refs/`, `out/` and `.env` are gitignored.

## Scripts

| Script | Model | What it does |
|---|---|---|
| `generate.py` | Gemini | Generates base poses from `refs/`. `python generate.py` for all, `python generate.py walk_01` for one, `--list` for the names |
| `walk_sheet.py` | Gemini | Generates a 2×2 walk cycle in **one** image so the frames stay consistent, then slices it into `out/walk_s1..s4.png` |
| `edit_frame.py` | Gemini | Makes a near-identical copy of one frame with a small change: `python edit_frame.py idle_01 idle_02 "eyes closed (blink)"` |
| `edit_frame_openai.py` | OpenAI | Same as `edit_frame.py`, for when Gemini isn't available in your region |
| `regen_smooth.py` | OpenAI | Batch version: edits base frames into blink, breathing and in-between walk frames (the job list is at the top of the file) |
| `clean_alpha.py` | rembg (local) | Removes the soft white halo around generated cut-outs, `out/` → `out_clean/` |

Pose descriptions live in [prompts/states.yaml](prompts/states.yaml); the shared style prompt is [prompts/base.md](prompts/base.md). Model overrides: `GEMINI_MODEL` (default `gemini-2.5-flash-image`) and `OPENAI_IMAGE_MODEL` (default `gpt-image-2`).

## Iterating

If a frame doesn't look like your cat or the pose is wrong:
1. Edit that pose's description in `states.yaml`.
2. Re-run `python generate.py <name>` to overwrite it.

For small changes that must keep the body still (blinks, breathing), edit an existing frame with `edit_frame.py` instead of generating from scratch.
