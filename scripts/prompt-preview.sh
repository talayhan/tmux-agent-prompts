#!/usr/bin/env bash
# fzf --preview command: renders one prompt by opaque ID. Never receives body text on argv.
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/common.sh disable=SC1091
source "$SCRIPT_DIR/common.sh"

if [ "$#" -ne 2 ]; then
	echo "usage: prompt-preview.sh <source-id> <prompt-id>" >&2
	exit 2
fi

run_cli preview --source "$1" --id "$2"
