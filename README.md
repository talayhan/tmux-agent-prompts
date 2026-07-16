# tmux-agent-prompts

> Your prompt library, one tmux keybinding away.

[![CI](https://github.com/talayhan/tmux-agent-prompts/actions/workflows/ci.yml/badge.svg)](https://github.com/talayhan/tmux-agent-prompts/actions/workflows/ci.yml)
[![tmux](https://img.shields.io/badge/tmux-3.2%2B-1BB91F?logo=tmux&logoColor=white)](https://github.com/tmux/tmux)
[![fzf](https://img.shields.io/badge/fzf-required-ff5f5f?logo=gnu-bash&logoColor=white)](https://github.com/junegunn/fzf)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-8A2BE2)](LICENSE)

`tmux-agent-prompts` is a fast, source-aware prompt picker for terminal-based AI agents. Press `prefix + A`, choose a source, search a prompt with fzf, preview it, then paste it safely into the active pane.

It works with Claude Code, Codex, Aider, OpenCode, or any terminal workflow—without needing to know which program is running in the pane.

> **Project status:** design and test plan are ready; implementation is the next milestone. See [DESIGN.md](DESIGN.md) for the architecture and TDD plan.

<!-- Replace this placeholder with a real recorded GIF before the first public release. -->

```text
prefix + A
  │
  ├── Personal prompts
  ├── Project prompts
  ├── prompts.chat
  └── Claude Code library
        │
        └── Search + preview → Paste / Copy / Cancel
```

## Why this exists

Agent workflows are most effective when good prompts are easy to reuse. Browser bookmarks and scattered snippets break flow; hardcoded shell aliases cannot handle a growing prompt library.

This plugin makes prompt discovery native to tmux:

- **Fast:** source picker → fuzzy search → paste.
- **Source-aware:** mix personal, project, curated, and remote libraries.
- **Safe:** prompts are opaque text, never shell code.
- **Agent-neutral:** use the same library in Claude Code, Codex, Aider, OpenCode, or a shell.
- **Offline-friendly:** remote sources remain available from cache.
- **Built for teams:** commit project prompts alongside the project that needs them.

## Features

| Feature | What it does |
|---|---|
| Source picker | Select a prompt library before searching. |
| fzf search + preview | Search titles, tags, types, and contributors while reading the full prompt. |
| Personal prompts | Keep private, reusable prompts in your XDG config directory. |
| Project prompts | Share repository-specific prompts in `.agent-prompts/prompts.json`. |
| `prompts.chat` | Browse a cached public CSV source; optionally focus on developer prompts. |
| Claude Code library | Browse a curated, versioned bundle of Claude Code prompt patterns. |
| Safe multiline paste | Uses tmux buffers instead of shell-escaped `send-keys`. |
| Copy or paste | Copy to the tmux buffer/clipboard or paste into the active pane. |
| Configurable | Customize binding, sources, cache behavior, and submit behavior. |

## Requirements

- tmux **3.2+** (for the best popup experience)
- [fzf](https://github.com/junegunn/fzf)
- Bash
- Python **3.10+**
- `curl` for refreshing remote sources
- [TPM](https://github.com/tmux-plugins/tpm) (recommended for installation)

The plugin can run with older tmux versions using an fzf-tmux fallback; the final support matrix will be verified in CI before v1.0.

## Install

### TPM

Add this before TPM's initialization line in `~/.tmux.conf`.

```tmux
set -g @plugin 'talayhan/tmux-agent-prompts'
```

Reload tmux, then press `prefix + I` to install through TPM.

### Manual installation

```bash
git clone https://github.com/talayhan/tmux-agent-prompts ~/.tmux/plugins/tmux-agent-prompts
```

Then add this to `~/.tmux.conf`:

```tmux
run-shell ~/.tmux/plugins/tmux-agent-prompts/main.tmux
```

Reload your tmux configuration:

```bash
tmux source-file ~/.tmux.conf
```

## Quick start

1. Press `prefix + A`.
2. Choose a source—for example, **Personal prompts**.
3. Type to filter prompts and use the preview to inspect the complete text.
4. Choose **Paste** to insert it into the current pane, or **Copy** to keep it in a tmux buffer.
5. Review/edit the pasted text and press Enter when ready.

The plugin never submits a prompt by default. Enable automatic submit only if that is how you prefer to work.

## Prompt sources

### Personal prompts

Create `${XDG_CONFIG_HOME:-~/.config}/tmux-agent-prompts/prompts.json`:

```json
{
  "prompts": [
    {
      "id": "review-current-changes",
      "title": "Review current changes",
      "body": "Review the current changes for correctness, tests, regressions, and maintainability. Report findings first, ordered by severity, with file references.",
      "tags": ["review", "testing"],
      "contributor": "me"
    },
    {
      "id": "explain-code",
      "title": "Explain this code",
      "body": "Explain the selected code in plain language. Cover its inputs, outputs, side effects, and important edge cases.",
      "tags": ["learning", "explanation"],
      "contributor": "me"
    }
  ]
}
```

### Project prompts

Add `.agent-prompts/prompts.json` to a repository:

```json
{
  "prompts": [
    {
      "id": "run-release-check",
      "title": "Release readiness check",
      "body": "Review this repository for release readiness. Run the documented checks, inspect the current changes, and list any blockers before proposing a release.",
      "tags": ["release", "repository"],
      "contributor": "team"
    }
  ]
}
```

When the active pane belongs to that repository, **Project prompts** appears in the source picker. This makes the prompt library reviewable and versioned with your code.

### prompts.chat

The built-in `prompts.chat` source maps its public CSV fields into the plugin's common prompt format:

| CSV field | Plugin field |
|---|---|
| `act` | title |
| `prompt` | body |
| `type` | tag |
| `contributor` | contributor |

The source is cached locally for 24 hours by default. The picker offers a refresh action and can filter to entries marked as developer-oriented. The data is parsed with Python's CSV parser, so multiline prompts and quoted commas remain correct.

### Claude Code prompt library

The plugin bundles a curated, versioned prompt pack inspired by the [Claude Code prompt library](https://code.claude.com/docs/en/prompt-library). It updates with plugin releases instead of scraping the documentation site at runtime. Each entry preserves source attribution in its preview.

## Configuration

### tmux options

```tmux
# Default: A
set -g @tmux-agent-prompts-launch-key 'A'

# Default: paste. Other value: copy
set -g @tmux-agent-prompts-default-action 'paste'

# Default: off. Submit pasted text with Enter automatically.
set -g @tmux-agent-prompts-auto-submit 'off'

# Extra options forwarded to fzf.
set -g @tmux-agent-prompts-fzf-options '--height=80% --layout=reverse --border'
```

### Source registry

Configure sources in `${XDG_CONFIG_HOME:-~/.config}/tmux-agent-prompts/sources.json`. User-defined sources extend the built-ins; using a built-in ID overrides it deliberately.

```json
{
  "sources": [
    {
      "id": "personal",
      "label": "Personal prompts",
      "kind": "local-json",
      "path": "~/.config/tmux-agent-prompts/prompts.json"
    },
    {
      "id": "project",
      "label": "Project prompts",
      "kind": "project-json",
      "path": ".agent-prompts/prompts.json"
    },
    {
      "id": "prompts-chat",
      "label": "prompts.chat",
      "kind": "remote-csv",
      "url": "https://raw.githubusercontent.com/f/prompts.chat/refs/heads/main/prompts.csv",
      "ttl_hours": 24
    }
  ]
}
```

Remote caches are stored at `${XDG_CACHE_HOME:-~/.cache}/tmux-agent-prompts/`. A failed refresh never replaces a working cached source.

## Keybindings

| Key | Action |
|---|---|
| `prefix + A` | Open source picker (default). |
| `Enter` | Select the highlighted source, prompt, or action. |
| `Esc` | Cancel the current picker. |
| `Alt-R` | Refresh a remote source from its source menu. |
| `?` | Show fzf key help. |

The final fzf bindings will be documented from automated tests, not copied from assumptions.

## Safety and privacy

Prompt text is data, not executable code.

- The plugin does not `eval`, source, or execute prompt content.
- Multiline prompts are transferred through `tmux load-buffer` and `tmux paste-buffer`, not interpolated shell strings.
- Remote URLs must use HTTPS by default; downloads have size limits and timeouts.
- Remote sources are fetched only when the cache is missing, expired, or explicitly refreshed.
- Prompt bodies are not logged by default.

Using a remote source naturally sends a request to that source's host. Use local or project sources for confidential prompts.

## Development

The project follows test-driven development: every behavior begins with a failing test, then the smallest implementation that makes it pass, then refactoring under the test suite.

```bash
git clone https://github.com/talayhan/tmux-agent-prompts
cd tmux-agent-prompts
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
make test
```

Expected developer commands:

```bash
make format-check  # ruff format, shfmt
make lint          # ruff, mypy, shellcheck
make test          # pytest + bats
make integration   # headless tmux integration tests
make check         # everything above
```

The implementation will enforce:

- `pytest` unit tests with at least **95% branch coverage** for the Python core
- `bats-core` tests for shell orchestration
- headless tmux tests for real paste behavior
- `ruff`, strict `mypy`, `shellcheck`, and `shfmt`
- no live network access in unit tests

See [DESIGN.md](DESIGN.md) for the architecture, fixtures, adapter contract, and GitHub Actions plan.

## Release process

GitHub Actions validates pull requests and `main` across supported Python versions, then runs shell and headless tmux checks. Maintainers publish an annotated `vX.Y.Z` tag only after required checks pass. The release workflow reruns validation, creates a source tarball and SHA-256 checksum, and attaches both to a GitHub Release.

TPM installs straight from the GitHub repository—there is no additional package registry to trust.

## Contributing

Contributions are welcome. Good first contributions include new test fixtures, documentation improvements, source adapters, curated prompt packs with clear provenance, and accessibility improvements to the fzf interface.

Before opening a pull request:

1. Start with a focused issue or discussion for changes that affect behavior or source formats.
2. Add or update tests first.
3. Run `make check` locally.
4. Keep prompts attributable and do not submit confidential, unsafe, or license-incompatible material.

The public repository will add `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, issue templates, and a pull-request template before the first release.

## Roadmap

- [ ] v0.1 — local JSON prompts, source picker, safe paste/copy, test harness
- [ ] v0.2 — `prompts.chat` adapter, cache controls, developer-only filtering
- [ ] v0.3 — curated Claude Code prompt pack and GitHub Release workflow
- [ ] v1.0 — stable configuration format, documentation site, compatibility matrix

## License

This project will be released under the [MIT License](LICENSE).

---

Built for people who would rather keep working than hunt for the right prompt.
