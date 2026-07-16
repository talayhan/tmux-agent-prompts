from __future__ import annotations

import json
from pathlib import Path

from tmux_agent_prompts import cli
from tmux_agent_prompts.cache import CacheError
from tmux_agent_prompts.models import Prompt
from tmux_agent_prompts.registry import Paths, Source


def configure(monkeypatch, prompts: list[Prompt]) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(
        cli, "paths_from_environment", lambda: Paths(Path("registry"), Path("cache"))
    )
    monkeypatch.setattr(
        cli, "load_registry", lambda _: [Source("personal", "Personal", "local-json", path="x")]
    )
    monkeypatch.setattr(cli, "prompts_for_source", lambda *args, **kwargs: prompts)


def test_sources_jsonl_contract(monkeypatch, capsys) -> None:  # type: ignore[no-untyped-def]
    configure(monkeypatch, [])

    assert cli.main(["sources"]) == 0

    assert json.loads(capsys.readouterr().out) == {"id": "personal", "label": "Personal"}


def test_sources_fzf_contract(monkeypatch, capsys) -> None:  # type: ignore[no-untyped-def]
    configure(monkeypatch, [])

    assert cli.main(["sources", "--format", "fzf"]) == 0

    assert capsys.readouterr().out == "personal\tPersonal\n"


def test_prompts_fzf_contract(monkeypatch, capsys) -> None:  # type: ignore[no-untyped-def]
    configure(monkeypatch, [Prompt("p", "Title", "Body", ("tag",), "Me")])

    assert cli.main(["prompts", "--source", "personal", "--format", "fzf"]) == 0

    assert capsys.readouterr().out == "p\tTitle\ttag · Me\n"


def test_prompts_jsonl_contract(monkeypatch, capsys) -> None:  # type: ignore[no-untyped-def]
    configure(monkeypatch, [Prompt("p", "Title", "Body")])

    assert cli.main(["prompts", "--source", "personal"]) == 0

    assert json.loads(capsys.readouterr().out) == {
        "id": "p",
        "title": "Title",
        "body": "Body",
        "tags": [],
    }


def test_preview_renders_prompt_metadata(monkeypatch, capsys) -> None:  # type: ignore[no-untyped-def]
    configure(monkeypatch, [Prompt("p", "Title", "Body", ("tag",), "Me", "https://example.test")])

    assert cli.main(["preview", "--source", "personal", "--id", "p"]) == 0

    output = capsys.readouterr().out
    assert "Body" in output
    assert "Contributor: Me" in output
    assert "Source: https://example.test" in output


def test_preview_omits_optional_metadata_when_absent(monkeypatch, capsys) -> None:  # type: ignore[no-untyped-def]
    configure(monkeypatch, [Prompt("p", "Title", "Body")])

    assert cli.main(["preview", "--source", "personal", "--id", "p"]) == 0

    output = capsys.readouterr().out
    assert "Contributor:" not in output
    assert "Source:" not in output


def test_body_prints_raw_text_with_no_added_newline(monkeypatch, capsys) -> None:  # type: ignore[no-untyped-def]
    configure(monkeypatch, [Prompt("p", "Title", "line one\nline two", ("tag",), "Me")])

    assert cli.main(["body", "--source", "personal", "--id", "p"]) == 0

    assert capsys.readouterr().out == "line one\nline two"


def test_body_unknown_prompt_id_returns_error(monkeypatch, capsys) -> None:  # type: ignore[no-untyped-def]
    configure(monkeypatch, [Prompt("p", "Title", "Body")])

    assert cli.main(["body", "--source", "personal", "--id", "missing"]) == 2

    assert "unknown prompt ID in personal: missing" in capsys.readouterr().err


def test_unknown_source_returns_error(monkeypatch, capsys) -> None:  # type: ignore[no-untyped-def]
    configure(monkeypatch, [])

    assert cli.main(["prompts", "--source", "missing"]) == 2

    assert "unknown prompt source" in capsys.readouterr().err


def test_cache_refresh_failure_is_reported_not_raised(monkeypatch, capsys) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(
        cli, "paths_from_environment", lambda: Paths(Path("registry"), Path("cache"))
    )
    monkeypatch.setattr(
        cli,
        "load_registry",
        lambda _: [Source("prompts-chat", "prompts.chat", "remote-csv", url="https://x.test")],
    )

    def raise_cache_error(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise CacheError("could not refresh https://x.test: no network")

    monkeypatch.setattr(cli, "prompts_for_source", raise_cache_error)

    assert cli.main(["prompts", "--source", "prompts-chat"]) == 2

    assert "could not refresh" in capsys.readouterr().err
