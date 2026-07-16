"""Safe, cache-first retrieval for remote prompt sources."""

from __future__ import annotations

import os
import time
from collections.abc import Callable
from pathlib import Path


class CacheError(RuntimeError):
    """Raised when a remote source cannot be retrieved and has no cache."""


Fetch = Callable[[str], str]


def cached_content(
    cache_path: Path,
    url: str,
    *,
    ttl_hours: int,
    refresh: bool = False,
    fetch: Fetch,
    now: float | None = None,
) -> str:
    """Return cached text, refreshing it when required without losing good data."""
    timestamp = time.time() if now is None else now
    if cache_path.is_file() and not refresh and _is_fresh(cache_path, ttl_hours, timestamp):
        return cache_path.read_text(encoding="utf-8")
    try:
        content = fetch(url)
        _replace(cache_path, content)
        return content
    except OSError as error:
        if cache_path.is_file():
            return cache_path.read_text(encoding="utf-8")
        raise CacheError(f"could not refresh {url}: {error}") from error


def _is_fresh(path: Path, ttl_hours: int, now: float) -> bool:
    return now - path.stat().st_mtime < ttl_hours * 60 * 60


def _replace(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(f"{path.suffix}.tmp")
    temporary.write_text(content, encoding="utf-8")
    os.replace(temporary, path)
