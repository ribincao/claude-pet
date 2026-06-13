use std::path::PathBuf;
use std::sync::mpsc::channel;
use std::thread;
use std::time::Duration;

use notify::{Config, Event, RecommendedWatcher, RecursiveMode, Watcher};
use serde::{Deserialize, Serialize};
use tauri::{Emitter, Manager, PhysicalPosition};

#[derive(Debug, Clone, Serialize, Deserialize)]
struct PetState {
    state: String,
    #[serde(default)]
    message: Option<String>,
    #[serde(default)]
    ts: Option<u64>,
}

fn state_file_path() -> PathBuf {
    let home = dirs::home_dir().expect("could not resolve home dir");
    home.join(".claude").join("pet-state")
}

fn read_state(path: &PathBuf) -> Option<PetState> {
    let text = std::fs::read_to_string(path).ok()?;
    serde_json::from_str(&text).ok()
}

fn ensure_state_file(path: &PathBuf) {
    if !path.exists() {
        if let Some(parent) = path.parent() {
            let _ = std::fs::create_dir_all(parent);
        }
        let _ = std::fs::write(path, br#"{"state":"idle"}"#);
    }
}

pub fn run() {
    tauri::Builder::default()
        .setup(|app| {
            let app_handle = app.handle().clone();
            let path = state_file_path();
            ensure_state_file(&path);

            if let Some(s) = read_state(&path) {
                let _ = app_handle.emit("pet-state", s);
            }

            // Park the pet at the bottom-center of the primary screen on launch
            // (not dead-center), like a real desktop pet sitting on the floor.
            // The window starts hidden (visible:false in tauri.conf.json) so we
            // position it first, then show — no flash at the center.
            if let Some(window) = app.get_webview_window("pet") {
                if let (Ok(Some(monitor)), Ok(win_size)) =
                    (window.primary_monitor(), window.outer_size())
                {
                    // work_area excludes the Dock and menu bar, so its bottom edge
                    // sits just above the Dock. Park the pet there, centered — it
                    // ends up standing on top of the Dock, not behind it.
                    let wa = monitor.work_area();
                    let x = wa.position.x + (wa.size.width as i32 - win_size.width as i32) / 2;
                    let y = wa.position.y + (wa.size.height as i32 - win_size.height as i32);
                    let _ = window.set_position(PhysicalPosition::new(x, y.max(0)));
                }
                let _ = window.show();
            }

            let watch_path = path.clone();
            thread::spawn(move || {
                let (tx, rx) = channel::<notify::Result<Event>>();
                let mut watcher: RecommendedWatcher =
                    Watcher::new(tx, Config::default().with_poll_interval(Duration::from_millis(500)))
                        .expect("failed to create watcher");
                let parent = watch_path.parent().expect("state file has no parent");
                eprintln!("[pet] watching dir: {}", parent.display());
                watcher
                    .watch(parent, RecursiveMode::NonRecursive)
                    .expect("failed to watch state dir");

                let watch_name = watch_path.file_name().map(|s| s.to_os_string());
                for res in rx {
                    let Ok(event) = res else {
                        eprintln!("[pet] watcher err");
                        continue;
                    };
                    eprintln!("[pet] event {:?} paths={:?}", event.kind, event.paths);
                    let matches = event.paths.iter().any(|p| p.file_name().map(|s| s.to_os_string()) == watch_name);
                    if !matches {
                        continue;
                    }
                    match read_state(&watch_path) {
                        Some(s) => {
                            eprintln!("[pet] -> emit state={}", s.state);
                            let _ = app_handle.emit("pet-state", s);
                        }
                        None => eprintln!("[pet] could not parse {}", watch_path.display()),
                    }
                }
            });

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
