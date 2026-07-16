#!/usr/bin/env bats

load helpers/mock_bin

setup() {
	PROJECT_ROOT="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
	TEST_TMP="$(mktemp -d)"
	MOCK_BIN="$(make_mock_bin_dir "$TEST_TMP/bin")"
	FZF_LOG="$TEST_TMP/fzf.log"
	export FZF_LOG
	PATH="$MOCK_BIN:$PATH"
	export PATH

	# Real tmux is not running under bats; no plugin options are configured.
	write_mock "$MOCK_BIN" tmux 'exit 1'

	source "$PROJECT_ROOT/scripts/fzf.sh"
}

teardown() {
	rm -rf "$TEST_TMP"
}

mock_python_sources() {
	write_mock "$MOCK_BIN" python3 '
if [ "$3" = "sources" ]; then
  printf "personal\tPersonal prompts\n"
  printf "project\tProject prompts\n"
fi
'
}

mock_python_prompts() {
	write_mock "$MOCK_BIN" python3 '
if [ "$3" = "prompts" ]; then
  printf "claude/investigate-build-failure\tInvestigate a build failure\tdebugging \xc2\xb7 Anthropic\n"
fi
'
}

mock_fzf_logs_and_selects() {
	local line_to_select="$1"
	write_mock "$MOCK_BIN" fzf "
cat >\"\$FZF_LOG.stdin\"
printf '%s\n' \"\$@\" >\"\$FZF_LOG.args\"
printf '%b\n' '$line_to_select'
"
}

mock_fzf_cancelled() {
	write_mock "$MOCK_BIN" fzf '
cat >/dev/null
exit 130
'
}

@test "FZF-001: source picker feeds fzf labels, not raw JSON" {
	mock_python_sources
	mock_fzf_logs_and_selects "project\tProject prompts"

	result="$(fzf_pick_source)"

	[ "$result" = "project" ]
	run cat "$FZF_LOG.stdin"
	[[ "$output" == *"Project prompts"* ]]
	[[ "$output" != *'{"id"'* ]]
}

@test "FZF-001: source picker hides the ID column from the visible list" {
	mock_python_sources
	mock_fzf_logs_and_selects "personal\tPersonal prompts"

	fzf_pick_source >/dev/null

	run cat "$FZF_LOG.args"
	[[ "$output" == *"--with-nth=2"* ]]
}

@test "FZF-002: prompt picker preview command references an opaque ID placeholder, never a body" {
	mock_python_prompts
	mock_fzf_logs_and_selects "claude/investigate-build-failure\tInvestigate a build failure\tdebugging"

	fzf_pick_prompt "claude-code" >/dev/null

	run cat "$FZF_LOG.args"
	[[ "$output" == *"prompt-preview.sh"* ]]
	[[ "$output" == *"{1}"* ]]
	[[ "$output" != *"@build.log"* ]]
	[[ "$output" != *"Why is the build failing"* ]]
}

@test "FZF-003: cancelling the source picker returns failure with no output" {
	mock_python_sources
	mock_fzf_cancelled

	run fzf_pick_source
	[ "$status" -ne 0 ]
	[ -z "$output" ]
}

@test "FZF-003: cancelling the prompt picker returns failure with no output" {
	mock_python_prompts
	mock_fzf_cancelled

	run fzf_pick_prompt "claude-code"
	[ "$status" -ne 0 ]
	[ -z "$output" ]
}

@test "FZF-003: cancelling the action picker returns failure with no output" {
	mock_fzf_cancelled

	run fzf_pick_action
	[ "$status" -ne 0 ]
	[ -z "$output" ]
}
