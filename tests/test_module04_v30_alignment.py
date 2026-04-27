"""Regression tests for Module 04 v3.0 checker alignment."""

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


def test_module04_ex1_accepts_recovery_and_preservation_header(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from germinette.subjects.python_module_04 import Tester

    _write(
        tmp_path / "ex1" / "ft_archive_creation.py",
        """
        import sys
        import typing


        def main() -> None:
            if len(sys.argv) != 2:
                print("Usage: ft_archive_creation.py <file>")
                return
            p = sys.argv[1]
            print("=== Cyber Archives Recovery & Preservation ===")
            print(f"Accessing file'{p}'")
            f: typing.IO[str] = open(p, "r", encoding="utf-8")
            data = f.read()
            f.close()
            print("---")
            print(data, end="" if data.endswith("\\n") else "\\n")
            print("---")
            print(f"File '{p}' closed.")
            print("Transform data:")
            transformed = "\\n".join([ln + "#" for ln in data.splitlines()]) + "\\n"
            print("---")
            print(transformed, end="")
            print("---")
            print("Enter new file name (or empty): ", end="")
            out_name = input()
            if not out_name:
                print("Not saving data.")
                return
            print(f"Saving data to'{out_name}'")
            out = open(out_name, "w", encoding="utf-8")
            out.write(transformed)
            out.close()
            print(f"Data saved in file '{out_name}'")


        if __name__ == "__main__":
            main()
        """,
    )
    _write(
        tmp_path / "ancient_fragment.txt",
        "[FRAGMENT 001] alpha\n[FRAGMENT 002] beta\n",
    )

    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.test_archive_creation()
    _assert_ok(tester, "Exercise 1")


def test_module04_ex2_rejects_input_builtin(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from germinette.subjects.python_module_04 import Tester

    _write(
        tmp_path / "ex2" / "ft_stream_management.py",
        """
        import sys


        def main() -> None:
            print("=== Cyber Archives Recovery & Preservation ===")
            sys.stdout.flush()
            input()
            print("bad")


        if __name__ == "__main__":
            main()
        """,
    )

    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.test_stream_management()
    errors = "\n".join(tester.grouped_errors.get("Exercise 2", []))
    assert "sys.stdin" in errors or "input" in errors


def test_module04_ex3_contract_checked(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from germinette.subjects.python_module_04 import Tester

    _write(
        tmp_path / "ex3" / "ft_vault_security.py",
        """
        def secure_archive(
            filename: str, mode: str = "read", payload: str = ""
        ) -> tuple[bool, str]:
            try:
                if mode == "write":
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(payload)
                    return (True, "Content successfully written to file")
                with open(filename, "r", encoding="utf-8") as f:
                    return (True, f.read())
            except Exception as e:
                return (False, f"{e}")


        def main() -> None:
            print("=== Cyber Archives Security ===")
            print(secure_archive("/not/existing/file"))


        if __name__ == "__main__":
            main()
        """,
    )
    _write(
        tmp_path / "ancient_fragment.txt",
        "[FRAGMENT 001] sample\n",
    )

    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.test_vault_security()
    _assert_ok(tester, "Exercise 3")
