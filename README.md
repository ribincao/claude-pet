# claude-pet

一只会根据 Claude Code 状态做反应的桌面宠物（布偶猫）。

灵感来自 CatDeskPet，UX 是桌面常驻：猫会在屏幕边沿走来走去，闲了卷起来睡，被通知时用气泡说话。状态由 Claude Code 的 hooks 推动。

## 结构

```
claude-pet/
├── sprite-gen/   Phase 1: 用 Gemini Nano Banana 生成 12 张 sprite
├── pet-app/      Phase 2: Tauri 透明浮窗（待建）
└── hooks/        Phase 3: Claude Code hooks 配置（待建）
```

3 个子系统通过**一个文件**通信：`~/.claude/pet-state`（JSON）。

## 路线图

- **Phase 1** — sprite 生成管线 ←  现在
- **Phase 2** — Tauri 浮窗 + 状态机
- **Phase 3** — Claude Code hooks 接通
- **Phase 4** — 边缘走路动画 + 气泡
# claude-pet
