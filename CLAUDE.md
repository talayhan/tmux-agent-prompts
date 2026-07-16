# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

`tmux-agent-prompts` is a tmux plugin (source-aware prompt picker for terminal AI agents) that is early in implementation. **Only the Python core (`src/tmux_agent_prompts/`) exists today.** The shell boundary described in `DESIGN.md` and referenced by the `Makefile` (`main.tmux`, `main.sh`, `scripts/*.sh`, `tests/shell/*.bats`, `tests/integration/`, `tests/docs/`) has not been created yet — `make lint`/`make format-check`/`make test-shell`/`make test-integration`/`make test-docs` will no-op or fail on missing paths until those land. Check what actually exists before assuming a shell file is present.

The project follows strict TDD: every behavior starts as a failing test, then the minimal implementation, then refactor under the suite. See `DESIGN.md` for the full architecture and delivery plan, and `TEST_PLAN.md` for the test strategy.

## Commands

```bash
# Setup
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt

# Development loop
make format-check   # ruff format --check (Python); shfmt if shell files exist
make lint            # ruff check + mypy --strict (Python); shellcheck if shell files exist
make test-unit        # pytest (src/tmux_agent_prompts, 95% branch coverage required)
make check            # everything above plus shell/integration/docs targets

# Single test
python3 -m pytest tests/unit/test_service.py::test_name
python3 -m pytest tests/unit/test_service.py -k pattern
```

`pytest` is configured (in `pyproject.toml`) to run with `--cov-branch --cov-fail-under=95` by default, `testpaths = ["tests/unit"]`, and `pythonpath = ["src"]` — so `tmux_agent_prompts` imports directly without installation.

## Architecture

The core is a small, dependency-free Python package that normalizes prompts from multiple sources into one record type, plus a CLI that the (not-yet-built) shell/fzf layer will call as a subprocess and parse line-oriented output from.

Data flow: `registry.py` (which sources exist, from XDG config + built-ins) → `service.py` (resolve a source to a list of `Prompt` — dispatches by `source.kind`) → adapters (`adapters/json_source.py`, `adapters/csv_source.py`) parse raw source formats into `Prompt` records (`models.py`) → `cli.py` emits them as JSON Lines or tab-separated `fzf` input.

- **`models.py`** — `Prompt` is the single normalized record all sources map into (`id`, `title`, `body`, `tags`, `contributor`, `source_url`). `Prompt.from_mapping` is the strict validation entry point (rejects unknown fields, empty required text, non-list tags); everything downstream trusts a constructed `Prompt`.
- **`registry.py`** — Defines the four built-in sources (`personal`, `project`, `prompts-chat`, `claude-code`) and merges them with user-defined sources from `sources.json` (XDG config dir). A user source with a built-in's ID **replaces** it; this is deliberate, not a bug. `remote-csv` sources are required to use HTTPS; validation happens here, not at fetch time.
- **`service.py`** — `prompts_for_source` dispatches on `source.kind`: `remote-csv` goes through `cache.py` + the CSV adapter; `project-json` resolves relative to the caller's cwd; `bundled-json` resolves relative to the package root (`prompts/claude-code.json`); `local-json` expands `~`. The `fetch` parameter exists so tests can inject a fake downloader instead of hitting the network.
- **`cache.py`** — TTL-based cache-first fetch for remote sources. Writes go through a temp-file-then-`os.replace` swap so a failed refresh never corrupts or replaces a working cache; if a fetch raises `OSError` and a cache file exists, the stale cache is served rather than failing.
- **`cli.py`** — The only supported entry point for the shell layer. Subcommands: `sources`, `prompts --source <id>`, `preview --source <id> --id <prompt-id>`. Each supports `--format jsonl|fzf`. All expected errors (`OSError`, `ValueError`, and their subclasses `RegistryError`, `SourceNotFoundError`, `PromptValidationError`, `CacheError`) are caught in `main()` and reported on stderr with exit code 2 — do not let new failure modes escape as uncaught tracebacks here.

### Key invariants to preserve

- Prompt bodies are **data, never executed** — no `eval`/shell interpolation of prompt content anywhere in the core; this is a stated safety goal in `DESIGN.md`.
- Remote sources: HTTPS-only, size-limited (6 MiB, enforced in `service.py:_download`), cached under `${XDG_CACHE_HOME}/tmux-agent-prompts/`, and never fetched during unit tests (inject `fetch` instead of hitting the network).
- `Prompt.from_mapping` and `_source_from_mapping` (registry.py) reject unknown fields outright — extending the schema means updating both the `allowed` set and its tests, not silently accepting extra keys.
