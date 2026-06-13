# hooks/

Claude Code hook 配置：让一个真实的 Claude 会话驱动桌面宠物。

## 状态映射

| Claude 事件 | 宠物状态 | 含义 |
|---|---|---|
| `SessionStart` | idle | 会话开始，进入站姿待机 |
| `UserPromptSubmit` | walk | 你刚发了 prompt，猫开始干活（走来走去） |
| `PreToolUse` (`*`) | walk | 工具运行中 |
| `Notification` | sit + 气泡 "need input" | 需要你回应（权限请求等） |
| `Stop` | happy + 气泡 "done" → idle | 任务完成，开心 3s 后回 idle |
| `SubagentStop` | happy → idle | 子代理完成 |
| `SessionEnd` | sleep | 会话关闭，猫睡了 |

未映射但可后续加：`PreCompact`、`PostCompact`、error 退出码等。

## 安装

把 [claude-settings.json](claude-settings.json) 里的 `hooks` 块**合并**到 `~/.claude/settings.json`。如果你已经有 hooks，按事件名合并到对应数组里，别整个覆盖。

合并完之后**重启 Claude Code**（hooks 在启动时加载）。

## 验证

1. 桌面宠物已启动（`projects/claude-pet/pet-app/src-tauri/target/debug/claude-pet`）
2. 新开一个 Claude Code 会话
3. 发个简单 prompt（"ls 当前目录"），观察：
   - prompt 提交瞬间 → 猫开始 walk
   - 工具调用期间 → walk 继续
   - 回答完成 → 跳一下（happy）+ 气泡 "done"，3s 后回 idle
4. 关闭会话 → sleep

## 调试

宠物没反应？先确认是 hook 没跑还是宠物没收到——

```bash
# 看 hook 写出了啥
cat ~/.claude/pet-state

# 手动测宠物渲染
echo '{"state":"walk"}' > ~/.claude/pet-state
echo '{"state":"happy","message":"测试"}' > ~/.claude/pet-state
```

如果 `cat` 显示的内容跟最近触发的事件对得上但宠物没反应——是 Tauri 这边的事；如果 `cat` 内容根本不对——是 hook 配置或 Claude Code 没加载到。
