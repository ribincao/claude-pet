.PHONY: start stop restart logs status

LOG := /tmp/claude-pet.log

start:
	@nohup cargo tauri dev > $(LOG) 2>&1 &
	@echo "claude-pet started in background (logs: $(LOG))"

stop:
	@pkill -f "target/debug/claude-pet" 2>/dev/null || true
	@pkill -f "tauri dev" 2>/dev/null || true
	@echo "claude-pet stopped"

restart: stop
	@sleep 1
	@$(MAKE) start

status:
	@pgrep -fl "target/debug/claude-pet" || echo "claude-pet not running"

logs:
	@tail -f $(LOG)
