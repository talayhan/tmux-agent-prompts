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

	write_mock "$MOCK_BIN" python3 '
if [ "$3" = "sources" ]; then
  printf "personal\tPersonal prompts\n"
fi
'
}

teardown() {
	rm -rf "$TEST_TMP"
}

@test "SHELL-002/FZF-003: fzf cancel on the source picker exits cleanly with no tmux side effects" {
	write_mock "$MOCK_BIN" tmux 'echo "$@" >>"$TMUX_LOG"; [ "$1" = "show-option" ] && exit 0; exit 0'
	write_mock "$MOCK_BIN" fzf 'cat >/dev/null; exit 130'

	run "$PROJECT_ROOT/scripts/picker.sh" "%0"

	[ "$status" -eq 0 ]
	! grep -q -- "load-buffer" "$TMUX_LOG"
	! grep -q -- "paste-buffer" "$TMUX_LOG"
}

@test "picker.sh requires a target pane argument" {
	write_mock "$MOCK_BIN" tmux 'echo "$@" >>"$TMUX_LOG"; exit 0'

	run "$PROJECT_ROOT/scripts/picker.sh"

	[ "$status" -ne 0 ]
}
