from __future__ import annotations

import json
from pathlib import Path

import pytest

from tmux_agent_prompts.registry import (
    RegistryError,
    built_in_sources,
    load_registry,
    paths_from_environment,
)


def test_missing_user_registry_keeps_built_ins(tmp_path: Path) -> None:
    sources = load_registry(tmp_path / "missing.json")

    assert [source.id for source in sources] == [source.id for source in built_in_sources()]


def test_user_source_is_appended_and_can_override(tmp_path: Path) -> None:
    registry = tmp_path / "sources.json"
    registry.write_text(
        json.dumps(
            {
                "sources": [
                    {
                        "id": "personal",
                        "label": "Mine",
                        "kind": "local-json",
                        "path": "/tmp/mine.json",
                    },
                    {"id": "team", "label": "Team", "kind": "local-json", "path": "/tmp/team.json"},
                ]
            }
        ),
        encoding="utf-8",
    )

    sources = load_registry(registry)

    assert next(source for source in sources if source.id == "personal").label == "Mine"
    assert sources[-1].id == "team"


def test_invalid_source_is_rejected_before_access(tmp_path: Path) -> None:
    registry = tmp_path / "sources.json"
    registry.write_text(
        json.dumps(
            {
                "sources": [
                    {"id": "bad", "label": "Bad", "kind": "remote-csv", "url": "http://bad.test"}
                ]
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(RegistryError, match="HTTPS"):
        load_registry(registry)


@pytest.mark.parametrize(
    "source",
    [
        {"id": "bad", "label": "Bad", "kind": "unknown", "path": "/tmp/source"},
        {"id": "bad", "label": "Bad", "kind": "local-json"},
        {"id": "bad", "label": "Bad", "kind": "local-json", "path": "/tmp/source", "ttl_hours": 0},
        {"id": "bad", "label": "Bad", "kind": "local-json", "path": "/tmp/source", "extra": True},
    ],
)
def test_invalid_registry_fields_are_rejected(tmp_path: Path, source: dict[str, object]) -> None:
    registry = tmp_path / "sources.json"
    registry.write_text(json.dumps({"sources": [source]}), encoding="utf-8")

    with pytest.raises(RegistryError):
        load_registry(registry)


def test_xdg_paths_are_honored(tmp_path: Path) -> None:
    config = tmp_path / "config"
    cache = tmp_path / "cache"
    paths = paths_from_environment({"XDG_CONFIG_HOME": str(config), "XDG_CACHE_HOME": str(cache)})

    assert paths.registry == config / "tmux-agent-prompts" / "sources.json"
    assert paths.cache == cache / "tmux-agent-prompts"


@pytest.mark.parametrize("content", ["{", "[]", '{"sources": {}}', '{"sources": ["bad"]}'])
def test_invalid_registry_document_is_rejected(tmp_path: Path, content: str) -> None:
    registry = tmp_path / "sources.json"
    registry.write_text(content, encoding="utf-8")

    with pytest.raises(RegistryError):
        load_registry(registry)
