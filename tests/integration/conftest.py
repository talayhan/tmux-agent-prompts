"""Headless tmux server fixture for integration tests.

Starts an isolated tmux server on its own control socket so tests never touch
a real user session, per DESIGN.md's `tmux -L agent-prompts-test -f /dev/null` policy.
"""

from __future__ import annotations

import os
import subprocess
import uuid
from collections.abc import Iterator
from dataclasses import dataclass

import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TMUX_BIN = "/usr/bin/tmux"


@dataclass
class HeadlessTmux:
    socket_name: str
    socket_path: str

    def run(self, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [TMUX_BIN, "-L", self.socket_name, *args],
            check=check,
            capture_output=True,
            text=True,
            timeout=10,
        )

    @property
    def tmux_env(self) -> str:
        return f"{self.socket_path},0,0"

    def pane_id(self, target: str = "main") -> str:
        return self.run("display-message", "-p", "-t", target, "#{pane_id}").stdout.strip()

    def capture(self, pane_id: str) -> str:
        return self.run("capture-pane", "-p", "-J", "-t", pane_id).stdout

    def new_window(self, name: str) -> str:
        self.run("new-window", "-d", "-t", "main", "-n", name)
        return self.run("display-message", "-p", "-t", name, "#{pane_id}").stdout.strip()


@pytest.fixture
def headless_tmux() -> Iterator[HeadlessTmux]:
    socket_name = f"agent-prompts-test-{uuid.uuid4().hex[:10]}"
    tmux_tmpdir = os.environ.get("TMUX_TMPDIR", "/tmp")
    socket_path = f"{tmux_tmpdir}/tmux-{os.getuid()}/{socket_name}"
    server = HeadlessTmux(socket_name, socket_path)
    server.run("-f", "/dev/null", "new-session", "-d", "-s", "main", "-x", "80", "-y", "24")
    try:
        yield server
    finally:
        server.run("kill-server", check=False)
