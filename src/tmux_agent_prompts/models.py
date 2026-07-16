"""Validated, source-independent prompt records."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


class PromptValidationError(ValueError):
    """Raised when a prompt record cannot be normalized safely."""


@dataclass(frozen=True, slots=True)
class Prompt:
    id: str
    title: str
    body: str
    tags: tuple[str, ...] = ()
    contributor: str | None = None
    source_url: str | None = None

    @classmethod
    def from_mapping(cls, record: Mapping[str, Any]) -> Prompt:
        allowed = {"id", "title", "body", "tags", "contributor", "source_url"}
        unknown = set(record) - allowed
        if unknown:
            raise PromptValidationError(f"unknown prompt field: {sorted(unknown)[0]}")

        prompt_id = _required_text(record, "id")
        title = _required_text(record, "title")
        body = _required_text(record, "body")
        tags = _tags(record.get("tags", []))
        contributor = _optional_text(record, "contributor")
        source_url = _optional_text(record, "source_url")
        return cls(prompt_id, title, body, tags, contributor, source_url)

    def to_mapping(self) -> dict[str, object]:
        record: dict[str, object] = {
            "id": self.id,
            "title": self.title,
            "body": self.body,
            "tags": list(self.tags),
        }
        if self.contributor is not None:
            record["contributor"] = self.contributor
        if self.source_url is not None:
            record["source_url"] = self.source_url
        return record


def _required_text(record: Mapping[str, Any], field: str) -> str:
    value = record.get(field)
    if not isinstance(value, str) or not (normalized := value.strip()):
        raise PromptValidationError(f"prompt field '{field}' must be non-empty text")
    return normalized if field != "body" else value


def _optional_text(record: Mapping[str, Any], field: str) -> str | None:
    value = record.get(field)
    if value is None:
        return None
    if not isinstance(value, str) or not (normalized := value.strip()):
        raise PromptValidationError(f"prompt field '{field}' must be non-empty text when set")
    return normalized


def _tags(value: object) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(
        isinstance(tag, str) and tag.strip() for tag in value
    ):
        raise PromptValidationError("prompt field 'tags' must be a list of non-empty text")
    return tuple(tag.strip() for tag in value)
