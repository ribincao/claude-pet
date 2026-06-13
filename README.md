# claude-pet

A desktop pet for **Claude Code on macOS**. A cat lives on your desktop and reacts, in real time, to what Claude Code is doing — it walks around while Claude works, sits and looks at you when it needs your input, does a happy hop when a task finishes, and curls up to sleep when the session ends.

> Built with [Tauri](https://tauri.app) (Rust + web frontend). The pet is a transparent, always-on-top, frameless window that sits on top of the Dock.

## What it does

- **Reacts to Claude Code activity.** Claude Code [hooks](https://docs.anthropic.com/en/docs/claude-code/hooks) fire on session events and write a tiny state file; the pet animates accordingly.
- **Lives on your desktop.** Frameless, transparent, always-on-top window. Drag it anywhere; it walks back and forth along the bottom of the screen on its own.
- **Speaks.** Shows a small speech bubble for events like "need input" and "done".
- **Smooth, lifelike animation.** Sprite-sheet animations (idle/look, walk, rest) play at the bottom of the screen, just above the Dock.

### How Claude Code drives the pet

The three parts of this project talk through a **single file**: `~/.claude/pet-state` (JSON).

```
Claude Code event ──(hook writes JSON)──▶ ~/.claude/pet-state
                                                │ (file watcher)
                                                ▼
                                  pet-app (Tauri) emits → webview plays animation
```

| When | Claude Code event | Pet state | Animation |
|------|-------------------|-----------|-----------|
| Session starts / back to idle after a task | `SessionStart` / after `Stop` (3s) | `idle` | **look** (sits, watches you) |
| Claude needs your input (permission, etc.) | `Notification` | `sit` + 💬 "need input" | **look** |
| A task just finished | `Stop` / `SubagentStop` | `happy` + 💬 "done" | **look** (faster, livelier) → idle |
| You submit a prompt / a tool is running | `UserPromptSubmit` / `PreToolUse` | `walk` | **walk** (paces along the Dock) |
| Session ends (you quit / close it) | `SessionEnd` | `sleep` | **lie** (curls up) |

> Note: `Stop` fires at the end of **each turn** (→ back to idle/look), while `SessionEnd` only fires when the session is actually **closed** (→ lie down). So the pet only sleeps when you truly exit Claude Code.

## Project layout

```
claude-pet/
├── pet-app/        Tauri app: transparent pet window + animation engine + state watcher
│   ├── src/        Frontend (HTML/CSS/JS) — sprite engine lives in pet.js
│   └── src-tauri/  Rust — watches ~/.claude/pet-state and positions the window
├── hooks/          Claude Code hook config to drop into ~/.claude/settings.json
└── sprite-gen/     (optional) Python pipeline for generating new sprite frames
```

## Requirements

- **macOS** (uses macOS window APIs; the pet is positioned above the Dock).
- **[Rust](https://rustup.rs) + Cargo**.
- **Tauri CLI**: `cargo install tauri-cli` (or `npm i -g @tauri-apps/cli`). The build also needs Xcode Command Line Tools (`xcode-select --install`).
- **[Claude Code](https://docs.anthropic.com/en/docs/claude-code)** for the live integration.

## Run it

### 1. Start the pet

```bash
cd pet-app
make start      # runs `cargo tauri dev` in the background (logs: /tmp/claude-pet.log)
```

The first build compiles the Tauri/Rust dependencies and takes a few minutes; later starts are fast. The cat appears at the bottom-center of your screen.

Handy `make` targets (run inside `pet-app/`):

| Command | Does |
|---------|------|
| `make start` | Launch the pet (dev mode) |
| `make stop` | Quit it |
| `make restart` | Stop + start (use after editing the frontend) |
| `make status` | Is it running? |
| `make logs` | Tail the live log |

### 2. Connect Claude Code

Merge the `hooks` block from [`hooks/claude-settings.json`](hooks/claude-settings.json) into your `~/.claude/settings.json` (merge per-event arrays if you already have hooks — don't overwrite the whole block), then **restart Claude Code** so it reloads the hooks.

Now use Claude Code as usual and watch the cat react. To test the wiring without a session:

```bash
echo '{"state":"walk"}'  > ~/.claude/pet-state   # cat starts pacing
echo '{"state":"sleep"}' > ~/.claude/pet-state   # cat lies down
cat ~/.claude/pet-state                           # see the current state
```

### 3. (Optional) Get a standalone app

Dev mode runs a bare binary whose Dock icon is set at runtime. For a permanent, double-clickable app with a stable Dock icon, either **download a prebuilt build** from the [Actions tab](../../actions) (each push to `main` uploads a `claude-pet-macos-arm64` artifact containing a `.dmg`), or build it yourself:

```bash
cd pet-app && cargo tauri build
open src-tauri/target/release/bundle/macos/claude-pet.app
```

> **The app is not code-signed or notarized.** On first launch macOS Gatekeeper will block it ("can't be opened because it is from an unidentified developer"). This is expected for an open-source build. To open it:
> - **right-click the app → Open → Open**, or
> - clear the quarantine flag: `xattr -dr com.apple.quarantine "/Applications/claude-pet.app"`
>
> After that it launches normally. (Building locally with `cargo tauri build` ad-hoc signs it, so the prebuilt download is the one that needs this step.)

## Bring your own pet

Each pet is a folder of **sprite sheets + a manifest**, loaded by the animation engine in [`pet-app/src/pet.js`](pet-app/src/pet.js). The bundled pet uses a "v2-sprite" pack (one WebP sheet per action, frames laid out in a grid). To swap in your own:

1. Put your sprite sheets in `pet-app/src/sprites/<your-pet>/`.
2. Edit the `CLIPS` table (sheet file, grid columns, cell size, frame count) and the `STATE_MAP` (which clip + speed each state uses) at the top of `pet.js`.
3. `make restart`.

You can also use the `sprite-gen/` pipeline to generate frames from a photo. The pet's on-screen size is a single constant (`BOX`) in `pet.js`.

## License

[MIT](LICENSE) © 2026 Libin Cao. Free to use, modify, and share — bring your own cat. 🐱
