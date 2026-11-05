# pet-app

The Tauri 2 app: a transparent, frameless, always-on-top window that plays the pet's sprite sheets and switches animation whenever `~/.claude/pet-state` changes.

## Run (dev mode)

From this folder:

```bash
make start      # cargo tauri dev in the background, logs in /tmp/claude-pet.log
make stop
```

The first build compiles roughly 300 crates and takes a few minutes; later builds are incremental and fast. See the [main README](../README.md) for the other `make` targets and for building a standalone `Claude Pet.app`.

## Drive it by hand (no Claude Code needed)

```bash
echo '{"state":"walk"}' > ~/.claude/pet-state
echo '{"state":"sleep"}' > ~/.claude/pet-state
echo '{"state":"happy","message":"done"}' > ~/.claude/pet-state
echo '{"state":"sad","message":"something broke"}' > ~/.claude/pet-state
```

| State | Clip | Notes |
|---|---|---|
| `idle` | looking | Default; also what `happy` and `sad` fall back to |
| `sit` | looking | Used for "need input" |
| `alert` | looking | Slightly faster |
| `happy` | looking | Fastest; back to `idle` after 3s |
| `walk` | walking | The window moves along the screen and turns at each edge |
| `sleep` | lying | Slow |
| `sad` | lying | Back to `idle` after 4s |

Optional field: `message`, shown in a speech bubble that fades after 3.5s. If the file doesn't exist on launch, the app creates it with `{"state":"idle"}`.

## Layout

```
pet-app/
├── Makefile             start / stop / restart / status / logs
├── src/                 static HTML/CSS/JS frontend (no npm build step)
│   ├── index.html
│   ├── pet.js           sprite engine, state machine, edge-walking, drag
│   ├── styles.css
│   └── sprites/cpp/     looking / walking / lying WebP sheets + pet.json
└── src-tauri/           Rust backend
    ├── tauri.conf.json  window: 160×160, transparent, frameless, always on top
    └── src/
        ├── main.rs      entry point
        └── lib.rs       places the window above the Dock, watches the state file, emits "pet-state"
```

## Known limitations

- **Primary screen only.** The pet starts on the primary monitor's work area and walks within its width.
- **No click-through.** The 160×160 window always catches clicks, even on its transparent parts.
- **Apple Silicon only** for the prebuilt release; build locally for anything else.
