#!/usr/bin/env bash
# Buffer-based delivery into a target pane. Reads the payload from stdin so
# prompt text never touches argv or a shell-interpolated command string.

tmux_deliver() {
	local action="$1" target_pane="$2" auto_submit="${3:-0}"

	tmux load-buffer -

	case "$action" in
	paste)
		tmux paste-buffer -t "$target_pane"
		if [ "$auto_submit" = "1" ]; then
			tmux send-keys -t "$target_pane" Enter
		fi
		;;
	copy) : ;;
	*)
		echo "tmux.sh: unknown action: $action" >&2
		return 2
		;;
	esac
}
