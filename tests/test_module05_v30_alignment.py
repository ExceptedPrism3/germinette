"""Regression tests for Module 05 v3.0 checker alignment."""

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


def test_module05_ex0_does_not_require_super_call(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from germinette.subjects.python_module_05 import Tester

    _write(
        tmp_path / "ex0" / "data_processor.py",
        """
        from abc import ABC, abstractmethod
        from typing import Any


        class DataProcessor(ABC):
            @abstractmethod
            def validate(self, data: Any) -> bool:
                pass

            @abstractmethod
            def ingest(self, data: Any) -> None:
                pass

            def output(self) -> tuple[int, str]:
                return (0, "x")


        class NumericProcessor(DataProcessor):
            def validate(self, data: Any) -> bool:
                return True

            def ingest(self, data: int | float | list[int | float]) -> None:
                pass


        class TextProcessor(DataProcessor):
            def validate(self, data: Any) -> bool:
                return True

            def ingest(self, data: str | list[str]) -> None:
                pass


        class LogProcessor(DataProcessor):
            def validate(self, data: Any) -> bool:
                return True

            def ingest(self, data: dict[str, str] | list[dict[str, str]]) -> None:
                pass


        def main() -> None:
            print("=== Code Nexus - Data Processor ===")
            print("Testing Numeric Processor...")
            print("Testing Text Processor...")
            print("Testing Log Processor...")


        if __name__ == "__main__":
            main()
        """,
    )

    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.test_data_processor()
    _assert_ok(tester, "Exercise 0")


def test_module05_ex2_uses_protocol_without_json_csv_imports(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from germinette.subjects.python_module_05 import Tester

    _write(
        tmp_path / "ex2" / "data_pipeline.py",
        """
        from typing import Protocol


        class ExportPlugin(Protocol):
            def process_output(self, data: list[tuple[int, str]]) -> None:
                ...


        class CSVPlugin:
            def process_output(self, data: list[tuple[int, str]]) -> None:
                print("CSV Output:")
                print(",".join([v for _, v in data]))


        class JSONPlugin:
            def process_output(self, data: list[tuple[int, str]]) -> None:
                print("JSON Output:")
                print("{" + ", ".join([f'\"item_{k}\": \"{v}\"' for k, v in data]) + "}")


        class DataStream:
            def __init__(self) -> None:
                self.items: list[tuple[int, str]] = [(1, "alpha"), (2, "beta")]

            def output_pipeline(self, nb: int, plugin: ExportPlugin) -> None:
                plugin.process_output(self.items[:nb])

            def print_processors_stats(self) -> None:
                print("== DataStream statistics ==")
                print("No processor found, no data")


        def main() -> None:
            print("=== Code Nexus - Data Pipeline ===")
            ds = DataStream()
            ds.print_processors_stats()
            ds.output_pipeline(2, CSVPlugin())
            ds.output_pipeline(2, JSONPlugin())


        if __name__ == "__main__":
            main()
        """,
    )

    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.test_data_pipeline()
    _assert_ok(tester, "Exercise 2")
