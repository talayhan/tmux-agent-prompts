"""DOCS-001/DOCS-002: README examples parse and reference real, distributed behavior."""

from __future__ import annotations

import json
import os
import re
import subprocess

import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
README = os.path.join(PROJECT_ROOT, "README.md")

JSON_FENCE = re.compile(r"```json\n(?P<body>.*?)\n```", re.DOTALL)

TMUX_OPTIONS_TABLE = re.compile(r"@tmux-agent-prompts-[a-z-]+")


def _json_blocks() -> list[dict]:
    with open(README, encoding="utf-8") as handle:
        text = handle.read()
    return [json.loads(match.group("body")) for match in JSON_FENCE.finditer(text)]


def test_docs_001_every_readme_json_block_parses() -> None:
    blocks = _json_blocks()
    assert len(blocks) >= 3, "expected README to keep documenting prompt/source JSON examples"


def test_docs_001_prompt_examples_match_the_native_prompt_schema(tmp_path) -> None:
    import sys

    sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))
    from tmux_agent_prompts.adapters.json_source import load_json_prompts

    prompt_blocks = [block for block in _json_blocks() if "prompts" in block]
    assert prompt_blocks, "expected at least one documented native prompt source example"

    for index, block in enumerate(prompt_blocks):
        fixture = tmp_path / f"prompts-{index}.json"
        fixture.write_text(json.dumps(block), encoding="utf-8")
        prompts = load_json_prompts(fixture)
        assert prompts, f"README prompt example {index} produced no prompts"


def test_docs_001_source_registry_examples_match_the_registry_schema(tmp_path) -> None:
    import sys

    sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))
    from tmux_agent_prompts.registry import load_registry

    source_blocks = [block for block in _json_blocks() if "sources" in block]
    assert source_blocks, "expected at least one documented sources.json example"

    for index, block in enumerate(source_blocks):
        fixture = tmp_path / f"sources-{index}.json"
        fixture.write_text(json.dumps(block), encoding="utf-8")
        sources = load_registry(fixture)
        assert sources


def test_docs_002_manual_install_references_a_real_entry_point() -> None:
    with open(README, encoding="utf-8") as handle:
        text = handle.read()
    assert "main.tmux" in text
    assert os.path.isfile(os.path.join(PROJECT_ROOT, "main.tmux"))


@pytest.mark.parametrize(
    "expected_option",
    [
        "@tmux-agent-prompts-launch-key",
        "@tmux-agent-prompts-default-action",
        "@tmux-agent-prompts-auto-submit",
        "@tmux-agent-prompts-fzf-options",
    ],
)
def test_docs_002_documented_tmux_options_are_actually_read_by_the_plugin(
    expected_option: str,
) -> None:
    with open(README, encoding="utf-8") as handle:
        readme_text = handle.read()
    assert expected_option in readme_text, f"{expected_option} is documented in README.md"

    grep = subprocess.run(
        ["grep", "-rl", expected_option, "main.tmux", "main.sh", "scripts"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    assert grep.returncode == 0, f"{expected_option} is documented but not read by any script"
