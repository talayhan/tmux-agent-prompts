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

	run "$PROJECT_ROOT/main.sh" "%0"

	[ "$status" -eq 0 ]
	! grep -q -- "load-buffer" "$TMUX_LOG"
	! grep -q -- "paste-buffer" "$TMUX_LOG"
}

@test "SHELL-002: a missing dependency is reported and exits nonzero without a cascading trace" {
	local minimal_bin="$TEST_TMP/minimal-bin" bash_bin
	mkdir -p "$minimal_bin"
	ln -s "$(command -v dirname)" "$minimal_bin/dirname"
	bash_bin="$(command -v bash)"

	PATH="$minimal_bin" run "$bash_bin" "$PROJECT_ROOT/main.sh" "%0"

	[ "$status" -ne 0 ]
	[[ "$output" == *"missing required dependencies"* ]]
	[[ "$output" == *"tmux"* ]]
	[[ "$output" == *"fzf"* ]]
	[[ "$output" == *"python3"* ]]
}
