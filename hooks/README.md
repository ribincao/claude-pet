# hooks

Claude Code hook config that lets a real Claude Code session drive the pet. Every hook is a one-line shell command that writes a small JSON state to `~/.claude/pet-state`.

## State mapping

| Claude Code event | Pet state | Meaning |
|---|---|---|
| `SessionStart` | `idle` | Session started; the cat sits and watches you |
| `UserPromptSubmit` | `walk` | You sent a prompt; the cat starts pacing |
| `PreToolUse` (`*`) | `walk` | A tool is running |
| `Notification` | `sit` + bubble "need input" | Claude is waiting on you (a permission prompt, etc.) |
| `Stop` | `happy` + bubble "done" → `idle` | The turn finished; livelier for 3s, then back to idle |
| `SubagentStop` | `happy` → `idle` | A subagent finished |
| `SessionEnd` | `sleep` | Session closed; the cat curls up |

Not mapped yet, but easy to add: `PreCompact`, `PostCompact`, or `sad` on a failing tool.

## Install

Merge the `hooks` block from [claude-settings.json](claude-settings.json) into `~/.claude/settings.json`. If you already have hooks, merge per event name into the existing arrays rather than replacing the whole block.

Then **restart Claude Code**; hooks are loaded at startup.

## Check it works

1. Start the pet (`make start` in [`pet-app/`](../pet-app/), or open `Claude Pet.app`).
2. Open a new Claude Code session.
3. Send a simple prompt such as "list the files here" and watch:
   - when you submit → the cat starts walking
   - while tools run → it keeps walking
   - when the answer is done → "done" bubble, livelier for 3s, then idle
4. Close the session → the cat lies down to sleep.

## Debugging

If the pet doesn't react, first find out whether the hook didn't run or the pet didn't pick it up:

```bash
# what did the hook write?
cat ~/.claude/pet-state

# test the pet on its own
echo '{"state":"walk"}' > ~/.claude/pet-state
echo '{"state":"happy","message":"test"}' > ~/.claude/pet-state
```

If `cat` shows the state you expect but the pet doesn't move, the problem is on the app side (check `make logs`). If the file's content is wrong or stale, the hooks aren't configured or Claude Code didn't reload them.
