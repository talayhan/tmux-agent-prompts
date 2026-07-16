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
	# run-shell's shell-command is format-expanded by tmux (documented), so
	# #{pane_id} resolves here. display-popup's shell-command is NOT format-
	# expanded (undocumented for that purpose) - main.sh takes the already-
	# resolved pane id and opens the popup itself with a literal argument.
	tmux bind-key "$launch_key" run-shell "$CURRENT_DIR/main.sh '#{pane_id}'"
}

main
