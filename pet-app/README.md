# pet-app

Tauri 2 透明浮窗，渲染 Phase 1 生成的 sprite，按 `~/.claude/pet-state` 文件内容切换动画。

## 运行（开发模式）

```bash
cd projects/claude-pet/pet-app
cargo tauri dev
```

首次编译会装 ~300 个 crate，3-5 分钟。之后增量秒级。

## 手动驱动状态（不依赖 Claude Code hook）

```bash
echo '{"state":"walk"}' > ~/.claude/pet-state
echo '{"state":"sleep"}' > ~/.claude/pet-state
echo '{"state":"happy","message":"✓ 完成"}' > ~/.claude/pet-state
echo '{"state":"sad","message":"出错了"}' > ~/.claude/pet-state
```

支持的状态：`idle` · `walk` · `sleep` · `sit` · `alert` · `happy` · `sad`
可选字段：`message`（气泡文字，3.5s 后淡出）

## 结构

```
pet-app/
├── src/                vanilla HTML/JS frontend
│   ├── index.html
│   ├── pet.js          状态机 + sprite 切换
│   ├── styles.css
│   └── sprites/        Phase 1 复制过来的 12 张 PNG
└── src-tauri/          Rust 后端
    ├── Cargo.toml
    ├── tauri.conf.json 透明 / frameless / alwaysOnTop
    └── src/
        ├── main.rs     entrypoint
        └── lib.rs      文件监听 + emit("pet-state")
```

## 已知 TODO（Phase 4）

- 走路动画：让猫在屏幕边沿来回走（现在只是定点)
- 点击穿透：开关 `set_ignore_cursor_events(true)`
- 多显示器：现在固定主屏 (1200, 700)
- 拖动调整位置
