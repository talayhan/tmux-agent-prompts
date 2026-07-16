from __future__ import annotations

import json
from pathlib import Path

import pytest

from tmux_agent_prompts.adapters.json_source import JsonSourceError, load_json_prompts


def write_source(path: Path, prompts: list[dict[str, object]]) -> None:
    path.write_text(json.dumps({"prompts": prompts}), encoding="utf-8")


def test_loads_prompts_in_declared_order(tmp_path: Path) -> None:
    source = tmp_path / "prompts.json"
    write_source(
        source,
        [
            {"id": "first", "title": "First", "body": "one"},
            {"id": "second", "title": "Second", "body": "two"},
        ],
    )

    assert [prompt.id for prompt in load_json_prompts(source)] == ["first", "second"]


def test_missing_source_is_reported_without_crashing(tmp_path: Path) -> None:
    with pytest.raises(JsonSourceError, match="does not exist"):
        load_json_prompts(tmp_path / "missing.json")


def test_malformed_json_names_the_source(tmp_path: Path) -> None:
    source = tmp_path / "bad.json"
    source.write_text("{", encoding="utf-8")

    with pytest.raises(JsonSourceError, match="bad.json"):
        load_json_prompts(source)


@pytest.mark.parametrize("content", ["[]", '{"prompts": {}}', '{"prompts": ["bad"]}'])
def test_invalid_document_shape_is_rejected(tmp_path: Path, content: str) -> None:
    source = tmp_path / "invalid.json"
    source.write_text(content, encoding="utf-8")

    with pytest.raises(JsonSourceError, match="prompt"):
        load_json_prompts(source)


def test_invalid_prompt_field_is_wrapped_with_source_context(tmp_path: Path) -> None:
    source = tmp_path / "invalid-prompt.json"
    write_source(source, [{"id": "a", "title": "A", "body": "", "tags": []}])

    with pytest.raises(JsonSourceError, match="invalid prompt"):
        load_json_prompts(source)
