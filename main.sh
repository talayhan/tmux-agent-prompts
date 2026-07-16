#!/usr/bin/env bash
# Launcher bound via main.tmux's run-shell (no pty). Resolves the triggering
# pane, then opens a popup running scripts/picker.sh with that pane id as a
# literal argument - tmux does not format-expand display-popup's
# shell-command, so #{pane_id} would never reach picker.sh.
set -uo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_DIR

# shellcheck source=scripts/common.sh disable=SC1091
source "$SCRIPT_DIR/scripts/common.sh"

main() {
	require_dependencies || exit 1

	local target_pane="${1:-}"
	if [ -z "$target_pane" ]; then
		target_pane="$(tmux display-message -p '#{pane_id}')"
	fi

	exec tmux display-popup -E -w 80% -h 80% \
		"$SCRIPT_DIR/scripts/picker.sh '$target_pane'"
}

main "$@"
