#!/usr/bin/env bash
# tmux entry point: reads plugin options and binds the launch key.
set -euo pipefail

CURRENT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly CURRENT_DIR

# shellcheck source=scripts/common.sh disable=SC1091
source "$CURRENT_DIR/scripts/common.sh"

readonly DEFAULT_LAUNCH_KEY="A"

main() {
	local launch_key
	launch_key="$(tmux_option_or_default "@tmux-agent-prompts-launch-key" "$DEFAULT_LAUNCH_KEY")"
	tmux bind-key "$launch_key" run-shell "$CURRENT_DIR/main.sh '#{pane_id}'"
}

main
