from __future__ import annotations

import pytest

from tmux_agent_prompts.adapters.csv_source import CsvSourceError, parse_prompts_chat

CSV = (
    "act,prompt,for_devs,type,contributor\n"
    'Developer,"line one, with comma\nline two",TRUE,TEXT,Ada\n'
    "Writer,words,FALSE,TEXT,Bea\n"
)


def test_csv_maps_and_preserves_multiline_cells() -> None:
    prompts = parse_prompts_chat(CSV)

    assert prompts[0].id == "prompts-chat/developer"
    assert prompts[0].body == "line one, with comma\nline two"
    assert prompts[0].tags == ("TEXT", "developer")
    assert prompts[0].contributor == "Ada"


def test_developer_filter_excludes_false_rows() -> None:
    prompts = parse_prompts_chat(CSV, for_devs_only=True)

    assert [prompt.title for prompt in prompts] == ["Developer"]


def test_csv_requires_expected_headers() -> None:
    try:
        parse_prompts_chat("act,prompt\nA,B\n")
    except CsvSourceError as error:
        assert "for_devs" in str(error)
    else:
        pytest.fail("expected CsvSourceError")


def test_csv_rejects_blank_required_values() -> None:
    with pytest.raises(CsvSourceError, match="row 2"):
        parse_prompts_chat("act,prompt,for_devs,type,contributor\n,,TRUE,TEXT,Ada\n")
