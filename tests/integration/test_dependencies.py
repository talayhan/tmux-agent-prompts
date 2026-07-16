"""TMUX-007: a missing tmux/fzf/python3 dependency produces a concise, actionable message."""

from __future__ import annotations

import os
import subprocess

from conftest import PROJECT_ROOT

COMMON_SH = os.path.join(PROJECT_ROOT, "scripts", "common.sh")


def run_dependency_check(path_bin_dir: str) -> subprocess.CompletedProcess[str]:
    script = f'source "{COMMON_SH}" && require_dependencies'
    env = os.environ.copy()
    env["PATH"] = path_bin_dir
    return subprocess.run(
        ["/usr/bin/bash", "-c", script],
        capture_output=True,
        text=True,
        env=env,
        timeout=10,
    )


def test_tmux_007_reports_each_missing_dependency_by_name(tmp_path) -> None:
    empty_bin = tmp_path / "empty-bin"
    empty_bin.mkdir()
    result = run_dependency_check(str(empty_bin))
    assert result.returncode != 0
    assert "tmux" in result.stderr
    assert "fzf" in result.stderr
    assert "python3" in result.stderr


def test_tmux_007_passes_when_all_dependencies_are_present() -> None:
    result = run_dependency_check(os.environ["PATH"])
    assert result.returncode == 0
    assert result.stderr == ""
