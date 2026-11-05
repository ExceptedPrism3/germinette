"""Regression checks for the bis subjects and their portable report."""

import json
import shutil
from pathlib import Path

import pytest

from germinette.subjects.python_module_05_bis import Tester as CodexTester
from germinette.subjects.python_module_06_bis import Tester as NexusTester


def test_missing_files_fail_for_both_subjects(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    for tester in (CodexTester(), NexusTester()):
        tester.run()
        report = tester.report()
        assert report["version"] == 1
        assert report["total"] == 5
        assert report["failed"] == 5
        assert report["passed"] == 0
        assert len(report["checks"]) == 5


def test_nexus_processor_checks_structure_and_execution(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path("data_processor.py").write_text(
        "class DataProcessor:\n    pass\n", encoding="utf-8"
    )
    tester = NexusTester()
    tester.run("data_processor")
    assert tester.report()["failed"] == 5
    assert tester.report()["passed"] == 4


def test_cli_report_contains_failed_results(tmp_path, monkeypatch):
    from germinette import __main__

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        __main__, "check_update", lambda _: (False, None, False)
    )
    monkeypatch.setattr(
        "sys.argv",
        ["germinette", "python_module_05_bis", "--report", "result.json"],
    )
    with pytest.raises(SystemExit) as exit_code:
        __main__.main()
    assert exit_code.value.code == 1
    report = json.loads(Path("result.json").read_text())
    assert report["total"] == report["failed"] == 5


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_codex_environment_checks_inside_outside_and_missing_packages(
    codex_project,
):
    tester = CodexTester()
    tester.run("ex0")
    assert not tester.grouped_errors
    assert tester.report()["skipped"] == tester.report()["errors"] == 0


def test_codex_alembic_accepts_expected_exception(codex_project):
    tester = CodexTester()
    tester.run("alembic")
    assert not tester.grouped_errors
    write(Path("ft_alembic_1.py"), 'raise ValueError("wrong exception")\n')
    tester = CodexTester()
    tester.run("alembic")
    assert any(
        check["name"] == "ft_alembic_1.py" and check["status"] == "failed"
        for check in tester.checks
    )
    write(Path("ft_alembic_1.py"), 'print("no demonstration")\n')
    tester = CodexTester()
    tester.run("alembic")
    hidden = next(c for c in tester.checks if c["name"] == "ft_alembic_1.py")
    assert hidden["status"] == "failed"


def test_report_skipped_counts_and_incomplete_run(codex_project, monkeypatch):
    from germinette.core import GerminetteRunner
    from germinette.subjects.bis_common import BisTester

    tester = BisTester()
    tester.record("missing dependency", "skipped", "not installed")
    report = tester.report()
    assert report["skipped"] == report["total"] == 1
    write(Path("ex1/oracle.py"), "import dotenv\ndotenv.load_dotenv()\n")
    write(Path("ex1/requirements.txt"), "python-dotenv\n")
    write(
        Path("ex1/.env.example"),
        "\n".join(
            f"{key}="
            for key in (
                "MATRIX_MODE",
                "DATABASE_URL",
                "API_KEY",
                "LOG_LEVEL",
                "ZION_ENDPOINT",
            )
        ),
    )
    write(Path("ex1/.gitignore"), ".env\n")
    from importlib.util import find_spec

    monkeypatch.setattr(
        "germinette.subjects.python_module_05_bis.importlib.util.find_spec",
        lambda name: None if name == "dotenv" else find_spec(name),
    )
    runner = GerminetteRunner()
    assert runner.run_module("python_module_05_bis", "ex1") is None
    assert runner.last_tester.report()["skipped"] == 1


def test_unknown_exercise_produces_reported_failure(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    tester = CodexTester()
    tester.run("not-an-exercise")
    assert tester.report()["failed"] == 1
    assert tester.report()["total"] == 1


def test_policy_distinguishes_reading_and_mutating_sys_path(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    path = Path("example.py")
    path.write_text("import sys\nprint(sys.path)\n", encoding="utf-8")
    tester = CodexTester()
    tester.policy("policy", [path], no_syspath=True)
    assert tester.report()["passed"] == 1
    path.write_text(
        'import sys\nsys.path.append("example")\n', encoding="utf-8"
    )
    tester = CodexTester()
    tester.policy("policy", [path], no_syspath=True)
    assert tester.report()["failed"] == 1


def test_nexus_processor_passing_and_invalid_ingestion(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    source = Path(__file__).parent / "fixtures/nexus_golden/data_processor.py"
    shutil.copy(source, Path("data_processor.py"))
    tester = NexusTester()
    tester.run("data_processor")
    assert not tester.grouped_errors
    assert tester.report()["passed"] >= 8


def test_factory_contract_requires_two_implementations(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write(
        Path("ex3/factories.py"),
        """from abc import ABC, abstractmethod


class Family(ABC):
    @abstractmethod
    def create_base(self):
        pass

    @abstractmethod
    def create_evolved(self):
        pass


class FireFamily(Family):
    pass


class WaterFamily(Family):
    pass
""",
    )
    tester = NexusTester()
    tester.package_contract(
        "ex3", [("Factory interface", {"create_base", "create_evolved"})]
    )
    assert tester.report()["passed"] == 2
    file = Path("ex3/factories.py")
    file.write_text(
        file.read_text().replace(
            "class WaterFamily(Family):", "class WaterFamily:"
        ),
        encoding="utf-8",
    )
    tester = NexusTester()
    tester.package_contract(
        "ex3", [("Factory interface", {"create_base", "create_evolved"})]
    )
    assert tester.report()["failed"] == 1


def copy_combat_reference(tmp_path):
    source = Path(__file__).parent / "fixtures/nexus_bis_golden"
    shutil.copytree(source, tmp_path, dirs_exist_ok=True)


def test_factory_runtime_checks_transform_and_package_exports(tmp_path, monkeypatch):
    copy_combat_reference(tmp_path)
    monkeypatch.chdir(tmp_path)
    tester = NexusTester()
    tester.run("ex3")
    assert not tester.grouped_errors, tester.grouped_errors
    path = Path("ex3/transforms.py")
    original = path.read_text()
    path.write_text(original.replace("self.transformed = True", "self.transformed = False"))
    tester = NexusTester()
    tester.run("ex3")
    check = next(c for c in tester.checks if c["name"] == "Factory and capability behavior")
    assert check["status"] == "failed", check
    path.write_text(original)
    factory = Path("ex3/factories.py")
    factory.write_text(factory.read_text().replace(
        "class FlameFactory(CreatureFactory):\n",
        "class FlameFactory(CreatureFactory):\n    def __init__(self, name: str) -> None:\n"
        "        self.name = name\n\n",
    ))
    battle = Path("battle.py")
    battle.write_text(battle.read_text().replace("FlameFactory()", 'FlameFactory("named")'))
    from germinette.core import GerminetteRunner

    runner = GerminetteRunner()
    runner.run_module("python_module_06_bis", "ex3")
    check = next(c for c in runner.last_tester.checks if c["name"] == "Factory and capability behavior")
    assert check["status"] == "skipped", check


def test_strategy_runtime_checks_order_and_invalid_entity(tmp_path, monkeypatch):
    copy_combat_reference(tmp_path)
    monkeypatch.chdir(tmp_path)
    tester = NexusTester()
    tester.run("ex4")
    assert not tester.grouped_errors, tester.grouped_errors
    path = Path("ex4/strategies.py")
    path.write_text(path.read_text().replace("        print(creature.revert())\n", ""))
    tester = NexusTester()
    tester.run("ex4")
    result = next(c for c in tester.checks if c["name"] == "Strategy behavior")
    assert result["status"] == "failed", result
