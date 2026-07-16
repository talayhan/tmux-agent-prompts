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
}

teardown() {
	rm -rf "$TEST_TMP"
}

mock_tmux_default_options() {
	write_mock "$MOCK_BIN" tmux '
echo "$@" >>"$TMUX_LOG"
[ "$1" = "show-option" ] && exit 0
exit 0
'
}

mock_tmux_with_option() {
	local option="$1" value="$2"
	write_mock "$MOCK_BIN" tmux "
echo \"\$@\" >>\"\$TMUX_LOG\"
if [ \"\$1\" = \"show-option\" ]; then
  for arg in \"\$@\"; do
    if [ \"\$arg\" = \"$option\" ]; then
      echo \"$value\"
      exit 0
    fi
  done
  exit 0
fi
exit 0
"
}

@test "SHELL-001: binds the default launch key when no option is set" {
	mock_tmux_default_options
	run "$PROJECT_ROOT/main.tmux"
	[ "$status" -eq 0 ]
	grep -q -- "bind-key A run-shell" "$TMUX_LOG"
	grep -q -- "main.sh" "$TMUX_LOG"
}

@test "SHELL-001: binds a configured launch key" {
	mock_tmux_with_option "@tmux-agent-prompts-launch-key" "Z"
	run "$PROJECT_ROOT/main.tmux"
	[ "$status" -eq 0 ]
	grep -q -- "bind-key Z run-shell" "$TMUX_LOG"
}

@test "SHELL-001: passes the plugin directory to main.sh so it can be relocated" {
	mock_tmux_default_options
	run "$PROJECT_ROOT/main.tmux"
	[ "$status" -eq 0 ]
	grep -q -- "$PROJECT_ROOT/main.sh" "$TMUX_LOG"
}

@test "SHELL-001/TMUX-006: binding captures the triggering pane via #{pane_id}" {
	mock_tmux_default_options
	run "$PROJECT_ROOT/main.tmux"
	[ "$status" -eq 0 ]
	grep -q -- "#{pane_id}" "$TMUX_LOG"
}
