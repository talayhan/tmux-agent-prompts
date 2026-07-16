"""Native JSON prompt-source adapter."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tmux_agent_prompts.models import Prompt, PromptValidationError


class JsonSourceError(ValueError):
    """Raised when a native JSON source cannot be read."""


def load_json_prompts(path: Path) -> list[Prompt]:
    if not path.is_file():
        raise JsonSourceError(f"prompt source does not exist: {path}")
    try:
        data: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise JsonSourceError(f"could not read prompt source {path}: {error}") from error
    if not isinstance(data, dict) or not isinstance(data.get("prompts"), list):
        raise JsonSourceError(f"prompt source {path} must contain a 'prompts' list")
    if not all(isinstance(record, dict) for record in data["prompts"]):
        raise JsonSourceError(f"prompt source {path} must contain prompt objects")
    try:
        return [Prompt.from_mapping(record) for record in data["prompts"]]
    except PromptValidationError as error:
        raise JsonSourceError(f"invalid prompt in {path}: {error}") from error
