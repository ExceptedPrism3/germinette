"""A complete Codex submission shared by the bis regression tests."""

import shutil
import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def codex_project(tmp_path, monkeypatch):
    source = Path(__file__).parent / "fixtures" / "codex_golden"
    shutil.copytree(source, tmp_path, dirs_exist_ok=True)
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    monkeypatch.chdir(tmp_path)
    return tmp_path
