"""Machine-readable CLI used by the tmux/fzf shell boundary."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from tmux_agent_prompts.models import Prompt
from tmux_agent_prompts.registry import load_registry, paths_from_environment
from tmux_agent_prompts.service import prompts_for_source, source_by_id


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tmux-agent-prompts")
    commands = parser.add_subparsers(dest="command", required=True)
    sources = commands.add_parser("sources")
    sources.add_argument("--format", choices=("jsonl", "fzf"), default="jsonl")
    prompts = commands.add_parser("prompts")
    prompts.add_argument("--source", required=True)
    prompts.add_argument("--cwd", type=Path, default=Path.cwd())
    prompts.add_argument("--refresh", action="store_true")
    prompts.add_argument("--for-devs-only", action="store_true")
    prompts.add_argument("--format", choices=("jsonl", "fzf"), default="jsonl")
    preview = commands.add_parser("preview")
    preview.add_argument("--source", required=True)
    preview.add_argument("--id", required=True)
    preview.add_argument("--cwd", type=Path, default=Path.cwd())
    body = commands.add_parser("body")
    body.add_argument("--source", required=True)
    body.add_argument("--id", required=True)
    body.add_argument("--cwd", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)

    try:
        configured = load_registry(paths_from_environment().registry)
        if args.command == "sources":
            for source in configured:
                _emit_source(source.id, source.label, args.format)
            return 0
        source = source_by_id(configured, args.source)
        prompt_list = prompts_for_source(
            source,
            cache_directory=paths_from_environment().cache,
            project_directory=args.cwd,
            package_root=Path(__file__).parents[2],
            refresh=getattr(args, "refresh", False),
            for_devs_only=getattr(args, "for_devs_only", False),
        )
        if args.command == "prompts":
            for prompt in prompt_list:
                _emit_prompt(prompt, args.format)
            return 0
        prompt = _find_prompt(prompt_list, source.id, args.id)
        if args.command == "body":
            sys.stdout.write(prompt.body)
        else:
            print(_preview(prompt))
        return 0
    except (OSError, ValueError) as error:
        print(f"tmux-agent-prompts: {error}", file=sys.stderr)
        return 2


def _find_prompt(prompt_list: list[Prompt], source_id: str, prompt_id: str) -> Prompt:
    for prompt in prompt_list:
        if prompt.id == prompt_id:
            return prompt
    raise ValueError(f"unknown prompt ID in {source_id}: {prompt_id}")


def _emit_source(source_id: str, label: str, output_format: str) -> None:
    if output_format == "fzf":
        print(f"{source_id}\t{label}")
    else:
        print(json.dumps({"id": source_id, "label": label}, ensure_ascii=False))


def _emit_prompt(prompt: Prompt, output_format: str) -> None:
    if output_format == "fzf":
        metadata = " · ".join((*prompt.tags, prompt.contributor or ""))
        print(f"{prompt.id}\t{prompt.title}\t{metadata}")
    else:
        print(json.dumps(prompt.to_mapping(), ensure_ascii=False))


def _preview(prompt: Prompt) -> str:
    metadata = [f"Tags: {', '.join(prompt.tags) or 'none'}"]
    if prompt.contributor:
        metadata.append(f"Contributor: {prompt.contributor}")
    if prompt.source_url:
        metadata.append(f"Source: {prompt.source_url}")
    return f"{prompt.title}\n{'─' * len(prompt.title)}\n{prompt.body}\n\n{'\n'.join(metadata)}"


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
