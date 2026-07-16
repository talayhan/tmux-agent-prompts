#!/usr/bin/env bash
# Shared bats setup for building a mock command directory on PATH.
# Sourced by *.bats files; do not execute directly.

make_mock_bin_dir() {
  local dir="$1"
  mkdir -p "$dir"
  printf '%s\n' "$dir"
}

write_mock() {
  local mock_bin="$1" name="$2" body="$3"
  {
    printf '#!/usr/bin/env bash\n'
    printf '%s\n' "$body"
  } >"$mock_bin/$name"
  chmod +x "$mock_bin/$name"
}
