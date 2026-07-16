"""Source registry, defaults, and XDG path resolution."""

from __future__ import annotations

import json
import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


class RegistryError(ValueError):
    """Raised when a source registry is not valid."""


@dataclass(frozen=True, slots=True)
class Source:
    id: str
    label: str
    kind: str
    path: str | None = None
    url: str | None = None
    ttl_hours: int = 24


@dataclass(frozen=True, slots=True)
class Paths:
    registry: Path
    cache: Path


def paths_from_environment(environment: Mapping[str, str] | None = None) -> Paths:
    env = os.environ if environment is None else environment
    home = Path(env.get("HOME", str(Path.home())))
    config_root = Path(env.get("XDG_CONFIG_HOME", str(home / ".config")))
    cache_root = Path(env.get("XDG_CACHE_HOME", str(home / ".cache")))
    return Paths(
        config_root / "tmux-agent-prompts" / "sources.json", cache_root / "tmux-agent-prompts"
    )


def built_in_sources() -> list[Source]:
    return [
        Source(
            "personal",
            "Personal prompts",
            "local-json",
            path="~/.config/tmux-agent-prompts/prompts.json",
        ),
        Source("project", "Project prompts", "project-json", path=".agent-prompts/prompts.json"),
        Source(
            "prompts-chat",
            "prompts.chat",
            "remote-csv",
            url="https://raw.githubusercontent.com/f/prompts.chat/refs/heads/main/prompts.csv",
        ),
        Source(
            "claude-code", "Claude Code library", "bundled-json", path="prompts/claude-code.json"
        ),
    ]


def load_registry(path: Path) -> list[Source]:
    sources = built_in_sources()
    if not path.exists():
        return sources
    try:
        data: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RegistryError(f"could not read source registry {path}: {error}") from error
    if not isinstance(data, dict) or not isinstance(data.get("sources"), list):
        raise RegistryError("source registry must contain a 'sources' list")
    user_sources = [_source_from_mapping(item) for item in data["sources"]]
    replacements = {source.id: source for source in user_sources}
    merged = [replacements.pop(source.id, source) for source in sources]
    return [*merged, *replacements.values()]


def _source_from_mapping(record: object) -> Source:
    if not isinstance(record, dict):
        raise RegistryError("each source must be an object")
    allowed = {"id", "label", "kind", "path", "url", "ttl_hours"}
    unknown = set(record) - allowed
    if unknown:
        raise RegistryError(f"unknown source field: {sorted(unknown)[0]}")
    source_id = _text(record, "id")
    label = _text(record, "label")
    kind = _text(record, "kind")
    if kind not in {"local-json", "project-json", "remote-csv", "bundled-json"}:
        raise RegistryError(f"unsupported source kind: {kind}")
    path = record.get("path")
    url = record.get("url")
    if kind == "remote-csv":
        if not isinstance(url, str) or urlparse(url).scheme != "https":
            raise RegistryError("remote-csv source URL must use HTTPS")
    elif not isinstance(path, str) or not path.strip():
        raise RegistryError(f"{kind} source needs a path")
    ttl = record.get("ttl_hours", 24)
    if not isinstance(ttl, int) or ttl < 1:
        raise RegistryError("ttl_hours must be a positive integer")
    return Source(source_id, label, kind, path=path, url=url, ttl_hours=ttl)


def _text(record: Mapping[str, Any], field: str) -> str:
    value = record.get(field)
    if not isinstance(value, str) or not (normalized := value.strip()):
        raise RegistryError(f"source field '{field}' must be non-empty text")
    return normalized
