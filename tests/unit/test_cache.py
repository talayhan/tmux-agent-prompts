from __future__ import annotations

from pathlib import Path

import pytest

from tmux_agent_prompts.cache import CacheError, cached_content


def test_fresh_cache_skips_fetch(tmp_path: Path) -> None:
    cache = tmp_path / "source.csv"
    cache.write_text("cached", encoding="utf-8")

    assert (
        cached_content(
            cache, "https://example.test/prompts.csv", ttl_hours=24, fetch=lambda _: "new"
        )
        == "cached"
    )


def test_missing_cache_fetches_and_writes_atomically(tmp_path: Path) -> None:
    cache = tmp_path / "nested" / "source.csv"

    result = cached_content(
        cache, "https://example.test/prompts.csv", ttl_hours=24, fetch=lambda _: "new"
    )

    assert result == "new"
    assert cache.read_text(encoding="utf-8") == "new"


def test_failed_refresh_retains_existing_cache(tmp_path: Path) -> None:
    cache = tmp_path / "source.csv"
    cache.write_text("cached", encoding="utf-8")

    assert (
        cached_content(
            cache, "https://example.test/prompts.csv", ttl_hours=24, refresh=True, fetch=_fail
        )
        == "cached"
    )


def test_failed_initial_fetch_is_an_error(tmp_path: Path) -> None:
    with pytest.raises(CacheError, match="could not refresh"):
        cached_content(
            tmp_path / "source.csv", "https://example.test/prompts.csv", ttl_hours=24, fetch=_fail
        )


def _fail(_: str) -> str:
    raise OSError("offline")
