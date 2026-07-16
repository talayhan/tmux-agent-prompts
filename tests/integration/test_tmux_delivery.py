"""TMUX-001..006: buffer-based paste/copy delivery against a real headless tmux server."""

from __future__ import annotations

import os
import subprocess

from conftest import PROJECT_ROOT, HeadlessTmux

TMUX_SH = os.path.join(PROJECT_ROOT, "scripts", "tmux.sh")

LITERAL_PAYLOAD = 'line one\nline "two" with $VAR and `backticks`\nunicode: café ✨\n'


def deliver(
    server: HeadlessTmux,
    action: str,
    target_pane: str,
    text: str,
    *,
    auto_submit: bool = False,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["TMUX"] = server.tmux_env
    script = f'source "{TMUX_SH}" && tmux_deliver "$1" "$2" "$3"'
    return subprocess.run(
        ["bash", "-c", script, "tmux_deliver", action, target_pane, "1" if auto_submit else "0"],
        input=text,
        text=True,
        capture_output=True,
        env=env,
        timeout=10,
        check=True,
    )


def test_tmux_001_paste_delivers_body_to_the_target_pane(headless_tmux: HeadlessTmux) -> None:
    pane = headless_tmux.pane_id()
    deliver(headless_tmux, "paste", pane, "hello from tmux-agent-prompts")
    assert "hello from tmux-agent-prompts" in headless_tmux.capture(pane)


def test_tmux_002_paste_preserves_literal_text_unchanged(headless_tmux: HeadlessTmux) -> None:
    pane = headless_tmux.pane_id()
    deliver(headless_tmux, "paste", pane, LITERAL_PAYLOAD)
    captured = headless_tmux.capture(pane)
    assert 'line "two" with $VAR and `backticks`' in captured
    assert "café ✨" in captured


def test_tmux_003_no_enter_is_sent_by_default(headless_tmux: HeadlessTmux) -> None:
    pane = headless_tmux.pane_id()
    deliver(headless_tmux, "paste", pane, "not yet submitted")
    captured = headless_tmux.capture(pane)
    lines = [line for line in captured.splitlines() if line.strip()]
    assert lines[-1].strip().endswith("not yet submitted")


def test_tmux_004_auto_submit_sends_one_enter_after_paste(headless_tmux: HeadlessTmux) -> None:
    pane = headless_tmux.pane_id()
    deliver(headless_tmux, "paste", pane, "echo submitted-marker", auto_submit=True)
    captured = headless_tmux.capture(pane)
    assert "submitted-marker" in captured


def test_tmux_005_copy_loads_the_buffer_without_touching_the_pane(
    headless_tmux: HeadlessTmux,
) -> None:
    pane = headless_tmux.pane_id()
    before = headless_tmux.capture(pane)
    deliver(headless_tmux, "copy", pane, "copied text never appears in the pane")
    after = headless_tmux.capture(pane)
    assert before == after
    buffer_content = headless_tmux.run("show-buffer").stdout
    assert buffer_content == "copied text never appears in the pane"


def test_tmux_006_delivery_targets_the_captured_pane_even_after_focus_moves(
    headless_tmux: HeadlessTmux,
) -> None:
    original_pane = headless_tmux.pane_id()
    other_pane = headless_tmux.new_window("moved-away")
    headless_tmux.run("select-window", "-t", "moved-away")
    assert headless_tmux.pane_id() != original_pane

    deliver(headless_tmux, "paste", original_pane, "still targets the original pane")

    assert "still targets the original pane" in headless_tmux.capture(original_pane)
    assert "still targets the original pane" not in headless_tmux.capture(other_pane)
