"""Regression tests for Module 08 v3.0 checker alignment."""

from __future__ import annotations

from pathlib import Path
import textwrap

import pytest


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).strip() + "\n", encoding="utf-8")


def _assert_ok(tester, label: str) -> None:
    errors = tester.grouped_errors.get(label, [])
    assert not errors, f"{label} should pass but failed with:\n{errors}"


def test_module08_ex0_construct_subject_shape(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from germinette.subjects.python_module_08 import Tester

    _write(
        tmp_path / "ex0" / "construct.py",
        """
        import os
        import site
        import sys


        def main() -> None:
            in_venv = sys.prefix != sys.base_prefix
            if in_venv:
                print("MATRIX STATUS: Welcome to the construct")
            else:
                print("MATRIX STATUS: You're still plugged in")
            print(f"Current Python: {sys.executable}")
            if in_venv:
                print(f"Virtual Environment: {os.path.basename(sys.prefix)}")
                print(f"Environment Path: {sys.prefix}")
                print("Package installation path:")
                if len(site.getsitepackages()):
                    print(site.getsitepackages()[0])
                else:
                    print("site-packages")
            else:
                print("Virtual Environment: None detected")
                print("To enter the construct, run:")
                print("python -m venv matrix_env")
                print("source matrix_env/bin/activate")


        if __name__ == "__main__":
            main()
        """,
    )

    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.test_the_matrix()
    _assert_ok(tester, "Exercise 0")


def test_module08_ex1_loading_accepts_subject_shape(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from germinette.subjects.python_module_08 import Tester

    _write(
        tmp_path / "ex1" / "loading.py",
        """
        import importlib
        import sys

        def main() -> None:
            print("LOADING STATUS: Loading programs...")
            print("Checking dependencies:")
            mods = ["pandas", "numpy", "matplotlib", "requests"]
            for mod in mods:
                spec = importlib.util.find_spec(mod)
                if spec is None:
                    print(f"[MISSING] {mod} - install with pip or Poetry")
                else:
                    print(f"[OK] {mod} (installed)")
            print("Dataset source: np.random")
            print("Dependency managers compared: pip vs Poetry")
            print("pip install -r requirements.txt")
            print("poetry install")
            print("Analyzing Matrix data...")
            print("Processing 1000 data points...")
            print("Generating visualization...")
            print("Analysis complete!")

        if __name__ == "__main__":
            main()
        """,
    )
    _write(
        tmp_path / "ex1" / "requirements.txt",
        """
        pandas
        numpy
        matplotlib
        requests
        """,
    )
    _write(
        tmp_path / "ex1" / "pyproject.toml",
        """
        [tool.poetry]
        name = "matrix-loading"
        version = "0.1.0"
        description = ""
        authors = ["test"]

        [tool.poetry.dependencies]
        python = "^3.10"
        pandas = "*"
        numpy = "*"
        matplotlib = "*"
        requests = "*"
        """,
    )

    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.test_loading_programs()
    _assert_ok(tester, "Exercise 1")


def test_module08_ex2_requires_env_example_keys(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from germinette.subjects.python_module_08 import Tester

    _write(
        tmp_path / "ex2" / "oracle.py",
        """
        import os
        import sys
        from dotenv import load_dotenv

        def main() -> None:
            load_dotenv()
            print("ORACLE STATUS: Reading the Matrix...")
            mode = os.getenv("MATRIX_MODE", "development")
            print(f"Mode: {mode}")

        if __name__ == "__main__":
            main()
        """,
    )
    _write(tmp_path / "ex2" / ".gitignore", ".env\n")
    _write(tmp_path / "ex2" / ".env.example", "MATRIX_MODE=development\n")

    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.test_accessing_mainframe()
    errors = "\n".join(tester.grouped_errors.get("Exercise 2", []))
    assert "DATABASE_URL" in errors
    assert "API_KEY" in errors
    assert "LOG_LEVEL" in errors
    assert "ZION_ENDPOINT" in errors
