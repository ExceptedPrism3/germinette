"""Code Nexus behavior shared by Module 05 v3.1 and Module 06 bis v1.0."""

import importlib
from pathlib import Path
import shutil

import pytest

FIXTURES = Path(__file__).parent / "fixtures"
EXERCISES = ["data_processor", "data_stream", "data_pipeline"]


def prepare(tmp_path, monkeypatch, module):
    for source in (FIXTURES / "nexus_golden").glob("*.py"):
        if module == "python_module_05":
            directory = tmp_path / f"ex{EXERCISES.index(source.stem)}"
        else:
            directory = tmp_path
        directory.mkdir(exist_ok=True)
        shutil.copy(source, directory / source.name)
    monkeypatch.chdir(tmp_path)
    return importlib.import_module("germinette.subjects." + module).Tester()


@pytest.mark.parametrize(
    "module", ["python_module_05", "python_module_06_bis"]
)
@pytest.mark.parametrize(
    "exercise", ["data_processor", "data_stream", "data_pipeline"]
)
def test_nexus_reference(tmp_path, monkeypatch, module, exercise):
    tester = prepare(tmp_path, monkeypatch, module)
    tester.run(exercise)
    assert not tester.grouped_errors, tester.grouped_errors


@pytest.mark.parametrize(
    "module", ["python_module_05", "python_module_06_bis"]
)
@pytest.mark.parametrize(
    "exercise,before,after",
    [
        (
            "data_processor",
            "return isinstance(data, (int, float))",
            "return True",
        ),
        ("data_processor", "self.items.pop(0)", "self.items.pop()"),
        ("data_processor", "self.rank += 1", "self.rank += 0"),
        (
            "data_processor",
            "raise ValueError('Improper numeric data')",
            "return",
        ),
        ("data_stream", "processor.ingest(item)", "pass"),
        ("data_pipeline", "plugin.process_output(result)", "pass"),
    ],
)
def test_nexus_rejects_broken_behavior(
    tmp_path, monkeypatch, module, exercise, before, after
):
    tester = prepare(tmp_path, monkeypatch, module)
    directory = (
        tmp_path
        if module.endswith("bis")
        else tmp_path / f"ex{EXERCISES.index(exercise)}"
    )
    source = directory / (exercise + ".py")
    text = source.read_text()
    assert before in text
    source.write_text(text.replace(before, after))
    tester.run(exercise)
    assert tester.grouped_errors


def test_nexus_intentional_error_does_not_hide_unrelated_type_error(
    tmp_path, monkeypatch
):
    tester = prepare(tmp_path, monkeypatch, "python_module_05")
    source = tmp_path / "ex0/data_processor.py"
    source.write_text(
        source.read_text().replace("self.rank = 0", 'self.rank: int = "wrong"')
    )
    tester.run("data_processor")
    assert any(
        "assignment" in error
        for errors in tester.grouped_errors.values()
        for error in errors
    )


def test_nexus_reports_malformed_source(tmp_path, monkeypatch):
    tester = prepare(tmp_path, monkeypatch, "python_module_05")
    source = tmp_path / "ex0/data_processor.py"
    source.write_text("def broken(\n", encoding="utf-8")
    tester.run("data_processor")
    assert "Source Error" in "\n".join(tester.grouped_errors["Exercise 0"])
