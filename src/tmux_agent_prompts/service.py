"""Resolve configured sources into normalized prompts."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from urllib.request import Request, urlopen

from tmux_agent_prompts.adapters.csv_source import parse_prompts_chat
from tmux_agent_prompts.adapters.json_source import load_json_prompts
from tmux_agent_prompts.cache import cached_content
from tmux_agent_prompts.models import Prompt
from tmux_agent_prompts.registry import Source


class SourceNotFoundError(ValueError):
    """Raised when the requested source ID is not registered."""


def prompts_for_source(
    source: Source,
    *,
    cache_directory: Path,
    project_directory: Path,
    package_root: Path,
    refresh: bool = False,
    for_devs_only: bool = False,
    fetch: Callable[[str], str] | None = None,
) -> list[Prompt]:
    downloader = _download if fetch is None else fetch
    if source.kind == "remote-csv":
        assert source.url is not None
        content = cached_content(
            cache_directory / f"{source.id}.csv",
            source.url,
            ttl_hours=source.ttl_hours,
            refresh=refresh,
            fetch=downloader,
        )
        return parse_prompts_chat(content, for_devs_only=for_devs_only)
    assert source.path is not None
    if source.kind == "project-json":
        path = project_directory / source.path
    elif source.kind == "bundled-json":
        path = package_root / source.path
    else:
        path = Path(source.path).expanduser()
    return load_json_prompts(path)


def source_by_id(sources: list[Source], source_id: str) -> Source:
    for source in sources:
        if source.id == source_id:
            return source
    raise SourceNotFoundError(f"unknown prompt source: {source_id}")


def _download(url: str) -> str:
    request = Request(url, headers={"User-Agent": "tmux-agent-prompts"})
    with urlopen(request, timeout=10) as response:  # noqa: S310 - URLs are registry-validated HTTPS.
        payload: bytes = response.read(6 * 1024 * 1024 + 1)
    if len(payload) > 6 * 1024 * 1024:
        raise OSError("remote source exceeds 6 MiB limit")
    return payload.decode("utf-8")
