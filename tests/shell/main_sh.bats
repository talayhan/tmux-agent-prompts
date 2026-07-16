#!/usr/bin/env bats

load helpers/mock_bin

setup() {
	PROJECT_ROOT="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
	TEST_TMP="$(mktemp -d)"
	MOCK_BIN="$(make_mock_bin_dir "$TEST_TMP/bin")"
	TMUX_LOG="$TEST_TMP/tmux.log"
	export TMUX_LOG
	PATH="$MOCK_BIN:$PATH"
	export PATH

	write_mock "$MOCK_BIN" tmux '
echo "$@" >>"$TMUX_LOG"
[ "$1" = "show-option" ] && exit 0
[ "$1" = "display-message" ] && { echo "%9"; exit 0; }
exit 0
'
}

teardown() {
	rm -rf "$TEST_TMP"
}

@test "main.sh opens a popup that runs picker.sh with the resolved pane id as a literal argument" {
	run "$PROJECT_ROOT/main.sh" "%3"

	[ "$status" -eq 0 ]
	run grep -- "display-popup" "$TMUX_LOG"
	[ "$status" -eq 0 ]
	run grep -- "picker.sh '%3'" "$TMUX_LOG"
	[ "$status" -eq 0 ]
	# tmux never format-expands display-popup's shell-command, so the literal
	# placeholder must never appear there - only a real, already-resolved pane id.
	run grep -- '#{pane_id}' "$TMUX_LOG"
	[ "$status" -ne 0 ]
}

@test "main.sh opens the popup with -E so it closes when picker.sh exits" {
	run "$PROJECT_ROOT/main.sh" "%3"

	[ "$status" -eq 0 ]
	run grep -- "display-popup -E" "$TMUX_LOG"
	[ "$status" -eq 0 ]
}

@test "main.sh falls back to querying the current pane when no argument is given" {
	run "$PROJECT_ROOT/main.sh"

	[ "$status" -eq 0 ]
	run grep -- "display-message" "$TMUX_LOG"
	[ "$status" -eq 0 ]
	run grep -- "picker.sh '%9'" "$TMUX_LOG"
	[ "$status" -eq 0 ]
}

@test "main.sh reports missing dependencies and exits nonzero without opening a popup" {
	local minimal_bin="$TEST_TMP/minimal-bin" bash_bin
	mkdir -p "$minimal_bin"
	ln -s "$(command -v dirname)" "$minimal_bin/dirname"
	bash_bin="$(command -v bash)"

	PATH="$minimal_bin" run "$bash_bin" "$PROJECT_ROOT/main.sh" "%3"

	[ "$status" -ne 0 ]
	[[ "$output" == *"missing required dependencies"* ]]
}
