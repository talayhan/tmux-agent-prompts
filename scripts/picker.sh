#!/usr/bin/env bash
# Runs inside the popup opened by main.sh: pick a source, pick a prompt, pick
# an action, then deliver the raw prompt body via tmux buffers. Any cancelled
# picker exits cleanly with no paste/copy/subprocess side effect (FZF-003).
set -uo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_DIR

# shellcheck source=scripts/common.sh disable=SC1091
source "$SCRIPT_DIR/common.sh"
# shellcheck source=scripts/fzf.sh disable=SC1091
source "$SCRIPT_DIR/fzf.sh"
# shellcheck source=scripts/tmux.sh disable=SC1091
source "$SCRIPT_DIR/tmux.sh"

main() {
	local target_pane="${1:?picker.sh requires a target pane argument}"

	local source_id
	source_id="$(fzf_pick_source)" || exit 0

	local prompt_id
	prompt_id="$(fzf_pick_prompt "$source_id")" || exit 0

	local action
	action="$(fzf_pick_action)" || exit 0

	local auto_submit="0"
	[ "$(tmux_option_or_default "@tmux-agent-prompts-auto-submit" "off")" = "on" ] && auto_submit="1"
	[ "${TMUX_AGENT_PROMPTS_AUTO_SUBMIT:-0}" = "1" ] && auto_submit="1"

	run_cli body --source "$source_id" --id "$prompt_id" |
		tmux_deliver "$action" "$target_pane" "$auto_submit"
}

main "$@"
