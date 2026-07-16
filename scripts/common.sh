#!/usr/bin/env bash
# Shared helpers for the shell boundary. Sourced by other scripts, not executed.
# Guarded against double-sourcing: main.sh and fzf.sh both source this file.
if [ -n "${TMUX_AGENT_PROMPTS_COMMON_SH_LOADED:-}" ]; then
	# shellcheck disable=SC2317 # exit is reached when sourced by a non-function top-level script
	return 0 2>/dev/null || exit 0
fi
readonly TMUX_AGENT_PROMPTS_COMMON_SH_LOADED=1

PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
readonly PROJECT_ROOT

tmux_option_or_default() {
	local option_name="$1" default_value="$2" option_value
	option_value="$(tmux show-option -gqv "$option_name" 2>/dev/null || true)"
	if [ -z "$option_value" ]; then
		printf '%s' "$default_value"
	else
		printf '%s' "$option_value"
	fi
}

run_cli() {
	PYTHONPATH="$PROJECT_ROOT/src${PYTHONPATH:+:$PYTHONPATH}" python3 -m tmux_agent_prompts.cli "$@"
}

require_dependencies() {
	local missing=() cmd
	for cmd in tmux fzf python3; do
		command -v "$cmd" >/dev/null 2>&1 || missing+=("$cmd")
	done
	if [ "${#missing[@]}" -gt 0 ]; then
		echo "tmux-agent-prompts: missing required dependencies: ${missing[*]}" >&2
		echo "tmux-agent-prompts: install them and retry (see README.md#requirements)" >&2
		return 1
	fi
}
