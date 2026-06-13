# Ragdoll Cat Desktop Pet — Style & Character Guide

You are generating a desktop pet sprite of THIS specific Ragdoll cat (shown in the reference images). Every output must depict the SAME cat — same fur color, same pattern, same proportions, same face. Treat the references as ground truth for identity.

## Character

Use the reference photos to nail:
- Fur color, markings, pattern (this individual's exact coat)
- Body proportions and fluff level
- Face shape, eye color, ear shape and tufts
- Overall "vibe" — playful but sometimes lazy

## CRITICAL identity markers (must be respected in EVERY sprite)

This cat is a **BLUE POINT Ragdoll**, NOT seal point. The most common Ragdoll image in training data is seal point (brown mask/ears). DO NOT default to that. Specifically:

- **Coat color**: body is very light cream / off-white / pale ivory. Almost no warm tones — it's a cool palette.
- **Point coloring** (mask, ears, legs, tail): **blue-grey**, cool tone. NOT brown, NOT seal, NOT chocolate. Think dove-grey / slate.
- **Nose**: **solid BLACK** (or very dark charcoal). NEVER pink, NEVER brick, NEVER pale. This is unusual for a Ragdoll and is a key identity marker.
- **Muzzle around the nose**: a small white area surrounds the black nose, making the nose stand out sharply against the white muzzle.
- **Mouth**: a small dark line (lip / mouth slit) just below the black nose. Subtle but visible.
- **Eyes**: vivid blue, large, slightly almond-shaped.
- **Fur**: long and very fluffy, especially around the ruff (neck) and tail.

If a generated sprite has a pink nose, brown mask, or warm-toned coat, it is WRONG — that's a generic Ragdoll, not THIS cat.

## Visual style

- Semi-realistic, painterly rendering — like a high-quality 3D-rendered or hand-painted desktop pet (think CatDeskPet, but YOUR cat)
- Soft, warm shading with subtle highlights
- Detailed-looking fur (or rendered to look like it)
- Cute but NOT chibi — keep realistic proportions, no oversized head

## Canvas & technical requirements

- **Square 1:1 aspect ratio** (will be resized to 512×512)
- **Transparent background** — no scenery, no ground shadow, no environment; cat isolated on transparent (or pure white if transparency unavailable)
- Cat is **fully in frame** with a small ~5% margin
- Cat's feet (or lowest body point in lying/sleeping poses) must rest at the **BOTTOM CENTER of the canvas** — this is the anchor for placement on screen
- **Default facing: camera-RIGHT** (the cat looks to the viewer's right). Left-facing sprites are produced by mirroring later, so DO NOT generate left-facing versions.
- No text, no UI, no speech bubbles in the image itself
- One sprite per generation — no sprite sheets, grids, or multiple poses in one image
