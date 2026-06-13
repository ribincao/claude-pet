// === Sprite-sheet animation engine (v2-sprite sheet pack) ====================
// Each clip is ONE WebP sheet packed as a grid of `cols` columns. Frame index N
// maps to cell (col = N % cols, row = floor(N / cols)). We render by sizing the
// #sprite <div> to one scaled cell and stepping background-position each tick.
// Each action is ~60 frames @12fps sliced into a sheet, so cell sizes differ
// (each was cropped to the subject's bounding box). Swap in your own per the README.
const ASSET_DIR = "sprites/cpp";
const CLIPS = {
  lying:   { sheet: "lying-sheet.webp",   cols: 6, cw: 581, ch: 383, frames: 60 },
  looking: { sheet: "looking-sheet.webp", cols: 6, cw: 405, ch: 527, frames: 60 },
  walking: { sheet: "walking-sheet.webp", cols: 6, cw: 615, ch: 301, frames: 59 },
};

// claude-pet state -> clip + playback feel.
//   looking = attentive sit (idle / sit / alert / happy)
//   walking = moving across the screen edge
//   lying   = resting (sleep / sad)
// pingpong plays forward then backward so a non-seamless video loop never pops
// at the wraparound. walk loops straight — a reversed walk cycle looks wrong,
// and the window motion masks the seam anyway. Faster fps reads as more excited.
const STATE_MAP = {
  idle:  { clip: "looking", fps: 12, pingpong: true  },
  sit:   { clip: "looking", fps: 12, pingpong: true  },
  alert: { clip: "looking", fps: 15, pingpong: true  },
  happy: { clip: "looking", fps: 18, pingpong: true  },
  walk:  { clip: "walking", fps: 12, pingpong: false },
  sleep: { clip: "lying",   fps: 8,  pingpong: true  },
  sad:   { clip: "lying",   fps: 9,  pingpong: true  },
};

// Longest side of the pet in CSS px. Window is 160; leaves headroom for the
// bubble above a tall sitting pose. Bottom-center anchoring keeps paws grounded.
// Tweak this single number to resize the pet.
const BOX = 108;

const sprite = document.getElementById("sprite");
const bubble = document.getElementById("bubble");

let frameTimer = null;
let bubbleTimer = null;
let autoReturnTimer = null;

// States that should auto-fall-back to idle after a few seconds — they're
// emotional reactions, not steady states. happy after Stop, sad after error.
const TRANSIENT_STATES = { happy: 3000, sad: 4000 };

function playAnimation(name) {
  const map = STATE_MAP[name] || STATE_MAP.idle;
  const clip = CLIPS[map.clip];
  if (frameTimer) {
    clearTimeout(frameTimer);
    frameTimer = null;
  }

  // Fit one cell into BOX (preserve aspect). A sitting cat ends up taller than a
  // walking one — which is the natural relative proportion, so we don't correct it.
  const scale = BOX / Math.max(clip.cw, clip.ch);
  const dispW = clip.cw * scale, dispH = clip.ch * scale;
  const rows = Math.ceil(clip.frames / clip.cols);
  sprite.style.width = `${dispW}px`;
  sprite.style.height = `${dispH}px`;
  sprite.style.backgroundImage = `url("${ASSET_DIR}/${clip.sheet}")`;
  sprite.style.backgroundSize = `${clip.cols * dispW}px ${rows * dispH}px`;

  const interval = 1000 / (map.fps || 12);
  let i = 0, dir = 1;
  const draw = (n) => {
    const col = n % clip.cols, row = Math.floor(n / clip.cols);
    sprite.style.backgroundPosition = `${-col * dispW}px ${-row * dispH}px`;
  };
  const tick = () => {
    draw(i);
    if (map.pingpong) {
      if (i + dir >= clip.frames || i + dir < 0) dir = -dir;
      i += dir;
    } else {
      i = (i + 1) % clip.frames;
    }
    frameTimer = setTimeout(tick, interval);
  };
  tick();
}

function showBubble(text, autoHideMs = 3500) {
  if (bubbleTimer) {
    clearTimeout(bubbleTimer);
    bubbleTimer = null;
  }
  if (!text) {
    bubble.classList.add("hidden");
    return;
  }
  bubble.textContent = text;
  bubble.classList.remove("hidden");
  if (autoHideMs > 0) {
    bubbleTimer = setTimeout(() => bubble.classList.add("hidden"), autoHideMs);
  }
}

function applyState(payload) {
  const { state, message } = payload || {};
  if (!state) return;
  playAnimation(state);
  showBubble(message);

  if (autoReturnTimer) {
    clearTimeout(autoReturnTimer);
    autoReturnTimer = null;
  }
  const fallbackMs = TRANSIENT_STATES[state];
  if (fallbackMs) {
    autoReturnTimer = setTimeout(() => {
      playAnimation("idle");
      autoReturnTimer = null;
    }, fallbackMs);
  }
}

// Tauri global API (enabled via withGlobalTauri in tauri.conf.json)
if (window.__TAURI__ && window.__TAURI__.event) {
  window.__TAURI__.event.listen("pet-state", (event) => {
    applyState(event.payload);
  });
}

const stage = document.getElementById("stage");
const tauriWindow = window.__TAURI__?.window;

// ---- Edge-walking: when state=walk, move the window horizontally across the
// screen until it hits an edge, then turn around (mirror sprite).
// Monitor/window geometry is queried ONCE at start and cached; each tick does a
// single setPosition call (querying geometry every tick was ~120 IPC calls/sec
// and silently failed).
const WALK_SPEED_PX = 1.8; // logical px per tick
const WALK_TICK_MS = 33;   // ~30fps
const walkMotion = {
  active: false,
  paused: false,
  dir: 1, // +1 right, -1 left
  x: 0, y: 0, winW: 0, screenW: 0,
  timer: null,
};

async function tickWalk() {
  if (!walkMotion.active) return;
  if (!walkMotion.paused && tauriWindow) {
    walkMotion.x += walkMotion.dir * WALK_SPEED_PX;
    if (walkMotion.x <= 0) {
      walkMotion.x = 0; walkMotion.dir = 1;
      sprite.classList.remove("facing-left");
    } else if (walkMotion.x + walkMotion.winW >= walkMotion.screenW) {
      walkMotion.x = walkMotion.screenW - walkMotion.winW; walkMotion.dir = -1;
      sprite.classList.add("facing-left");
    }
    try {
      await tauriWindow.getCurrentWindow()
        .setPosition(new tauriWindow.LogicalPosition(walkMotion.x, walkMotion.y));
    } catch (e) { /* ignore one-tick failure */ }
  }
  walkMotion.timer = setTimeout(tickWalk, WALK_TICK_MS);
}

async function startWalkMotion() {
  if (walkMotion.active || !tauriWindow) return;
  try {
    const w = tauriWindow.getCurrentWindow();
    const scale = await w.scaleFactor();
    const pos = await w.outerPosition();
    const size = await w.outerSize();
    walkMotion.x = pos.x / scale;
    walkMotion.y = pos.y / scale;
    walkMotion.winW = size.width / scale;
    // screen.width is logical CSS px in the webview — no Tauri permission needed.
    walkMotion.screenW = window.screen.width;
    walkMotion.active = true;
    sprite.classList.toggle("facing-left", walkMotion.dir === -1);
    tickWalk();
  } catch (e) {
    console.error("walk motion init failed:", e);
  }
}

function stopWalkMotion() {
  walkMotion.active = false;
  if (walkMotion.timer) { clearTimeout(walkMotion.timer); walkMotion.timer = null; }
  sprite.classList.remove("facing-left");
}

// Hook into state machine — extend applyState to start/stop motion.
const origApplyState = applyState;
applyState = function (payload) {
  origApplyState(payload);
  const state = payload && payload.state;
  if (state === "walk") startWalkMotion();
  else stopWalkMotion();
};

// Click-and-drag to reposition. While walking, the walk loop calls setPosition
// every tick and would yank the window out from under the cursor — so we PAUSE
// walk motion on mousedown and only resume on mouseup, re-syncing our cached
// position to wherever the pet was dropped. (startDragging() resolves when the
// OS drag *begins*, not when it ends, so we can't just await it — we listen for
// the release.)
async function startDrag(e) {
  if (e.button !== 0) return;
  e.preventDefault();
  walkMotion.paused = true; // synchronous: tickWalk stops moving the window now

  const finishDrag = async () => {
    window.removeEventListener("mouseup", finishDrag);
    if (tauriWindow) {
      try {
        const w = tauriWindow.getCurrentWindow();
        const scale = await w.scaleFactor();
        const pos = await w.outerPosition();
        walkMotion.x = pos.x / scale; // resume the walk from the dropped spot
        walkMotion.y = pos.y / scale;
      } catch (_) { /* keep last cached position */ }
    }
    walkMotion.paused = false;
  };
  window.addEventListener("mouseup", finishDrag);

  try {
    if (tauriWindow) await tauriWindow.getCurrentWindow().startDragging();
  } catch (err) {
    console.error("startDragging failed:", err);
    finishDrag();
  }
}
stage.addEventListener("mousedown", startDrag);
sprite.addEventListener("mousedown", startDrag);

// Boot: default to idle until first event arrives.
playAnimation("idle");
