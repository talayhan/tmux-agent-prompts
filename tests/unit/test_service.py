from __future__ import annotations

from pathlib import Path

import pytest

from tmux_agent_prompts.registry import Source
from tmux_agent_prompts.service import SourceNotFoundError, prompts_for_source, source_by_id


def test_project_source_resolves_relative_to_project(tmp_path: Path) -> None:
    prompt_file = tmp_path / ".agent-prompts" / "prompts.json"
    prompt_file.parent.mkdir()
    prompt_file.write_text(
        '{"prompts": [{"id": "team", "title": "Team", "body": "Do it"}]}', encoding="utf-8"
    )

    prompts = prompts_for_source(
        Source("project", "Project", "project-json", path=".agent-prompts/prompts.json"),
        cache_directory=tmp_path / "cache",
        project_directory=tmp_path,
        package_root=tmp_path,
    )

    assert [prompt.id for prompt in prompts] == ["team"]


def test_remote_source_uses_injected_fetcher(tmp_path: Path) -> None:
    prompts = prompts_for_source(
        Source("remote", "Remote", "remote-csv", url="https://example.test/prompts.csv"),
        cache_directory=tmp_path / "cache",
        project_directory=tmp_path,
        package_root=tmp_path,
        fetch=lambda _: "act,prompt,for_devs,type,contributor\nA,B,TRUE,TEXT,C\n",
    )

    assert prompts[0].id == "prompts-chat/a"


def test_unknown_source_id_has_clear_error() -> None:
    with pytest.raises(SourceNotFoundError, match="unknown prompt source"):
        source_by_id([], "missing")
