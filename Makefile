.DEFAULT_GOAL := check

.PHONY: format-check lint test-unit test-shell test-integration test-docs check

format-check:
	python3 -m ruff format --check src tests
	@if command -v shfmt >/dev/null 2>&1; then shfmt -d main.tmux main.sh scripts/*.sh tests/shell/*.bats; else echo "shfmt not installed; skipping shell format check"; fi

lint:
	python3 -m ruff check src tests
	python3 -m mypy src
	@if command -v shellcheck >/dev/null 2>&1; then shellcheck main.tmux main.sh scripts/*.sh; else echo "shellcheck not installed; skipping shell lint"; fi

test-unit:
	python3 -m pytest

test-shell:
	@if command -v bats >/dev/null 2>&1; then bats tests/shell; else echo "bats not installed; skipping shell tests"; fi

test-integration:
	python3 -m pytest -o addopts="" tests/integration

test-docs:
	python3 -m pytest -o addopts="" tests/docs

check: format-check lint test-unit test-shell test-integration test-docs
