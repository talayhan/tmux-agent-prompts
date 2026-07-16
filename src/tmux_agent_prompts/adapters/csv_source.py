"""Adapter for the public prompts.chat CSV format."""

from __future__ import annotations

import csv
import io
import re

from tmux_agent_prompts.models import Prompt


class CsvSourceError(ValueError):
    """Raised when a CSV source does not match the supported schema."""


REQUIRED_HEADERS = frozenset({"act", "prompt", "for_devs", "type", "contributor"})

# Above Python's 128 KiB default; real-world prompts.chat rows exceed it
# (e.g. a documented ~144 KiB prompt body). Bounded well under service.py's
# 6 MiB download cap, so this can never mask a runaway/corrupt field.
_CSV_FIELD_SIZE_LIMIT = 8 * 1024 * 1024


def parse_prompts_chat(content: str, *, for_devs_only: bool = False) -> list[Prompt]:
    csv.field_size_limit(_CSV_FIELD_SIZE_LIMIT)
    reader = csv.DictReader(io.StringIO(content))
    headers = frozenset(reader.fieldnames or ())
    missing = REQUIRED_HEADERS - headers
    if missing:
        raise CsvSourceError(f"CSV source is missing headers: {', '.join(sorted(missing))}")

    prompts: list[Prompt] = []
    try:
        for row_number, row in enumerate(reader, start=2):
            if for_devs_only and row["for_devs"].strip().upper() != "TRUE":
                continue
            title = row["act"].strip()
            body = row["prompt"]
            if not title or not body.strip():
                raise CsvSourceError(f"CSV row {row_number} needs non-empty act and prompt")
            source_id = _slug(title)
            prompts.append(
                Prompt(
                    id=f"prompts-chat/{source_id}",
                    title=title,
                    body=body,
                    tags=tuple(
                        filter(
                            None,
                            (
                                row["type"].strip(),
                                "developer" if row["for_devs"].strip().upper() == "TRUE" else "",
                            ),
                        )
                    ),
                    contributor=row["contributor"].strip() or None,
                    source_url="https://github.com/f/prompts.chat",
                )
            )
    except csv.Error as error:
        raise CsvSourceError(f"could not parse CSV source: {error}") from error
    return prompts


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "untitled"
