#!/usr/bin/env bash
# fzf pickers for sources, prompts, and the paste/copy action.
# Sourced by main.sh; relies on functions from common.sh.

FZF_SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly FZF_SCRIPT_DIR

# shellcheck source=scripts/common.sh disable=SC1091
source "$FZF_SCRIPT_DIR/common.sh"

readonly FZF_DEFAULT_OPTS_TEXT="--height=80% --layout=reverse --border"

fzf_configured_options() {
	local -n out_array="$1"
	local raw
	raw="$(tmux_option_or_default "@tmux-agent-prompts-fzf-options" "$FZF_DEFAULT_OPTS_TEXT")"
	# shellcheck disable=SC2206,SC2034 # word-split flag string into the caller's nameref array
	out_array=($raw)
}

fzf_pick_source() {
	local extra_opts selection
	fzf_configured_options extra_opts
	selection="$(
		run_cli sources --format fzf |
			fzf --delimiter=$'\t' --with-nth=2 --prompt="Source> " "${extra_opts[@]}"
	)" || return 1
	[ -n "$selection" ] || return 1
	printf '%s' "${selection%%$'\t'*}"
}

fzf_pick_prompt() {
	local source_id="$1" for_devs_only="${2:-}" cwd="${3:-$PWD}"
	local cli_args=(prompts --source "$source_id" --format fzf --cwd "$cwd")
	if [ "$for_devs_only" = "1" ]; then
		cli_args+=(--for-devs-only)
	fi

	local preview_cmd="$FZF_SCRIPT_DIR/prompt-preview.sh $source_id {1}"
	local extra_opts selection
	fzf_configured_options extra_opts
	selection="$(
		run_cli "${cli_args[@]}" |
			fzf --delimiter=$'\t' --with-nth=2,3 --prompt="Prompt> " \
				--preview "$preview_cmd" "${extra_opts[@]}"
	)" || return 1
	[ -n "$selection" ] || return 1
	printf '%s' "${selection%%$'\t'*}"
}

fzf_pick_action() {
	local default_action selection
	default_action="$(tmux_option_or_default "@tmux-agent-prompts-default-action" "paste")"
	selection="$(
		printf 'paste\ncopy\n' | fzf --prompt="Action> " --header="Default: $default_action"
	)" || return 1
	[ -n "$selection" ] || return 1
	printf '%s' "$selection"
}
