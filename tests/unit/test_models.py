from __future__ import annotations

import pytest

from tmux_agent_prompts.models import Prompt, PromptValidationError


def test_complete_prompt_is_normalized() -> None:
    prompt = Prompt.from_mapping(
        {
            "id": " review ",
            "title": " Review ",
            "body": "inspect changes",
            "tags": [" testing ", "review"],
            "contributor": " me ",
            "source_url": "https://example.test/prompts",
        }
    )

    assert prompt.id == "review"
    assert prompt.title == "Review"
    assert prompt.tags == ("testing", "review")
    assert prompt.contributor == "me"
    assert prompt.to_mapping()["body"] == "inspect changes"


@pytest.mark.parametrize(
    ("record", "field"),
    [
        ({"id": "", "title": "A", "body": "B"}, "id"),
        ({"id": "a", "title": "A", "body": ""}, "body"),
        ({"id": "a", "title": "A", "body": "B", "tags": "bad"}, "tags"),
        ({"id": "a", "title": "A", "body": "B", "source_url": ""}, "source_url"),
        ({"id": "a", "title": "A", "body": "B", "extra": 1}, "extra"),
    ],
)
def test_invalid_prompt_reports_field(record: dict[str, object], field: str) -> None:
    with pytest.raises(PromptValidationError, match=field):
        Prompt.from_mapping(record)


def test_unicode_and_multiline_body_round_trip() -> None:
    body = "Plan\n- café\n- 東京\n$HOME and `literal`"
    prompt = Prompt.from_mapping({"id": "unicode", "title": "Übersicht", "body": body})

    assert Prompt.from_mapping(prompt.to_mapping()) == prompt
