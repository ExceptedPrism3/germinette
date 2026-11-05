"""Codex v1.0 requirements and the audit's false passes and false KOs."""

import json
import subprocess
from pathlib import Path

import pytest

from germinette.core import GerminetteRunner, ModuleDetector
from germinette.subjects.python_module_05_bis import (
    Tester as CodexTester,
    poetry_constraint,
)


def outcome(tester, name):
    return next(check for check in tester.checks if check["name"] == name)


def test_codex_complete_reference_and_cli_report(codex_project, monkeypatch):
    from germinette import __main__

    assert ModuleDetector.detect() == "python_module_05_bis"
    monkeypatch.setattr(
        __main__, "check_update", lambda _: (False, None, False)
    )
    monkeypatch.setattr(
        "sys.argv",
        ["germinette", "python_module_05_bis", "--report", "report.json"],
    )
    with pytest.raises(SystemExit) as result:
        __main__.main()
    assert result.value.code == 0
    report = json.loads(Path("report.json").read_text())
    assert report["version"] == 1
    assert report["total"] == report["passed"] == len(report["checks"])
    assert report["failed"] == report["errors"] == report["skipped"] == 0
    assert {
        "Dotenv configuration",
        "Environment precedence",
        "Potion and recipe behavior",
        "Light grimoire",
        "Dark circular import",
    } <= {check["name"] for check in report["checks"]}


def test_combined_broken_submission_fails_all_exercise_groups(codex_project):
    changes = {
        "ex0/loading.py": 'print("pip poetry")\n',
        "ex1/oracle.py": 'print("defaults")\n',
        "ft_alembic_0.py": "",
        "alchemy/transmutation/recipes.py": "",
        "alchemy/grimoire/dark_spellbook.py": (
            'raise ImportError("circular import")\n'
        ),
    }
    for name, source in changes.items():
        Path(name).write_text(source)
    tester = CodexTester()
    tester.run()
    for name in (
        "Missing dependency guidance",
        "Dotenv configuration",
        "ft_alembic_0.py",
        "Potion and recipe behavior",
        "Dark circular import",
    ):
        assert outcome(tester, name)["status"] == "failed", tester.report()


@pytest.mark.parametrize(
    "exercise,path,source,check",
    [
        ("ex0", "ex0/pyproject.toml", "not TOML", "Dependency declarations"),
        (
            "ex0",
            "ex0/requirements.txt",
            "# nothing\n",
            "Dependency declarations",
        ),
        (
            "ex0",
            "ex0/requirements.txt",
            "numpy==1.0\npandas\n",
            "Dependency declarations",
        ),
        (
            "ex0",
            "ex0/loading.py",
            'print("pip poetry")\n',
            "Missing dependency guidance",
        ),
        (
            "ex0",
            "ex0/construct.py",
            'import sys\n\nprint("venv activate", sys.prefix)\n',
            "Environment detection",
        ),
        (
            "ex1",
            "ex1/oracle.py",
            (
                "import os\nimport dotenv\n\nprint(dotenv.__name__,"
                ' os.getenv("MATRIX_MODE", "development"))\n'
            ),
            "Dotenv configuration",
        ),
        ("ex1", "ex1/requirements.txt", "", "Oracle dependency declaration"),
        ("ex1", "ex1/.gitignore", ".env\n!.env\n", "Ignore .env"),
        ("alembic", "ft_alembic_0.py", "", "ft_alembic_0.py"),
        (
            "alembic",
            "ft_alembic_1.py",
            "import alchemy\n\nif False:\n    alchemy.create_earth()\n",
            "ft_alembic_1.py",
        ),
        ("transmutation", "ft_distillation_0.py", "", "ft_distillation_0.py"),
        (
            "transmutation",
            "alchemy/transmutation/recipes.py",
            "",
            "Potion and recipe behavior",
        ),
        (
            "transmutation",
            "alchemy/transmutation/recipes.py",
            (
                "if False:\n    import alchemy\n    from . import recipes\n   "
                " print(alchemy, recipes)\n"
            ),
            "Recipe import styles",
        ),
        (
            "transmutation",
            "alchemy/potions.py",
            (
                'def healing_potion() -> str:\n    return "Earth element'
                ' created Air element created"\n\n\ndef strength_potion() ->'
                ' str:\n    return "Fire element created Water element'
                ' created"\n'
            ),
            "Potion and recipe behavior",
        ),
        (
            "grimoire",
            "alchemy/grimoire/light_validator.py",
            (
                "def validate_ingredients(ingredients: str) -> str:\n   "
                ' return "INVALID"\n'
            ),
            "Light grimoire",
        ),
        (
            "grimoire",
            "alchemy/grimoire/light_validator.py",
            (
                "def validate_ingredients(ingredients: str) -> str:\n   "
                ' status = "VALID" if ingredients.lower() == "earth" else'
                ' "INVALID"\n    return f"{ingredients} - {status}"\n'
            ),
            "Light grimoire",
        ),
        (
            "grimoire",
            "alchemy/grimoire/dark_spellbook.py",
            'raise ImportError("circular import")\n',
            "Dark grimoire structure",
        ),
        ("grimoire", "ft_kaboom_0.py", "", "ft_kaboom_0.py"),
        (
            "grimoire",
            "ft_kaboom_1.py",
            (
                "if False:\n    import alchemy.grimoire.dark_spellbook\n   "
                " print(alchemy.grimoire.dark_spellbook)\n"
            ),
            "Dark circular import",
        ),
        (
            "alembic",
            "helper.py",
            'import json\n\nprint(json.dumps("unauthorized"))\n',
            "Exercise 2 forbidden operations",
        ),
        (
            "alembic",
            "helper.py",
            "def missing(value):\n    return value\n",
            "Exercise 2 types",
        ),
    ],
)
def test_codex_rejects_audit_broken_submissions(
    codex_project,
    exercise,
    path,
    source,
    check,
):
    Path(path).write_text(source)
    tester = CodexTester()
    tester.run(exercise)
    assert outcome(tester, check)["status"] == "failed", tester.report()


@pytest.mark.parametrize(
    "source",
    [
        "from builtins import eval as run\nprint(run('1 + 1'))\n",
        "import builtins as b\nrun = b.exec\nrun('pass')\n",
        "import sys as s\ns.path.append('bad')\n",
        "from sys import path as p\np.insert(0, 'bad')\n",
        "import sys\np = sys.path\np[0] = 'bad'\n",
        "import sys\ndel sys.path[0]\n",
    ],
)
def test_policy_rejects_aliases_and_deletion(codex_project, source):
    Path("helper.py").write_text(source)
    tester = CodexTester()
    tester.policy("policy", [Path("helper.py")], no_syspath=True)
    assert outcome(tester, "policy")["status"] == "failed"


def test_policy_allows_sys_path_reads_and_alias_creation(codex_project):
    Path("helper.py").write_text("from sys import path\np = path\nprint(p)\n")
    tester = CodexTester()
    tester.policy("policy", [Path("helper.py")], no_syspath=True)
    assert outcome(tester, "policy")["status"] == "passed"


def test_oracle_rejects_dotenv_overriding_environment(codex_project):
    path = Path("ex1/oracle.py")
    path.write_text(
        path.read_text().replace('".env"))', '".env"), override=True)')
    )
    tester = CodexTester()
    tester.run("ex1")
    assert outcome(tester, "Environment precedence")["status"] == "failed"


def test_oracle_rejects_ignored_configuration_keys(codex_project):
    path = Path("ex1/oracle.py")
    path.write_text(path.read_text().split("for key in", 1)[0])
    tester = CodexTester()
    tester.run("ex1")
    assert outcome(tester, "Dotenv configuration")["status"] == "failed"


def test_alembic_demonstrates_air_before_hidden_earth(codex_project):
    Path("ft_alembic_1.py").write_text(
        "import alchemy\n\ntry:\n    alchemy.create_earth()\n"
        "except AttributeError:\n    pass\nprint(alchemy.create_air())\n"
    )
    tester = CodexTester()
    tester.run("alembic")
    assert outcome(tester, "ft_alembic_1.py")["status"] == "failed"


def test_dark_demonstration_contains_record_attempt(codex_project):
    Path("ft_kaboom_1.py").write_text(
        "import alchemy.grimoire.dark_spellbook\n\n"
        "print(alchemy.grimoire.dark_spellbook)\n"
    )
    tester = CodexTester()
    tester.run("grimoire")
    assert outcome(tester, "Dark circular import")["status"] == "failed"


def test_venv_probe_cleans_inherited_activation(codex_project, monkeypatch):
    monkeypatch.setenv("VIRTUAL_ENV", "/incorrect/inherited/environment")
    tester = CodexTester()
    tester.run("ex0")
    assert not tester.grouped_errors, tester.report()


def test_oracle_accepts_valid_ignore_and_export_syntax(codex_project):
    Path("ex1/.gitignore").write_text(".[e]nv\n")
    path = Path("ex1/.env.example")
    path.write_text(
        "".join(
            "export " + line + "\n" for line in path.read_text().splitlines()
        )
    )
    tester = CodexTester()
    tester.run("ex1")
    assert not tester.grouped_errors, tester.report()


def test_oracle_accepts_dotenv_dictionary_configuration(codex_project):
    Path("ex1/oracle.py").write_text(
        "import os\nfrom dotenv import dotenv_values\n\nconfig ="
        ' {**dotenv_values(os.path.join(os.path.dirname(__file__), ".env")),\n'
        '          **os.environ}\nprint(config.get("MATRIX_MODE",'
        ' "development"))\nfor key in ("DATABASE_URL", "API_KEY", "LOG_LEVEL",'
        ' "ZION_ENDPOINT"):\n    print(key, "configured" if config.get(key)'
        ' else "missing")\n'
    )
    tester = CodexTester()
    tester.run("ex1")
    assert not tester.grouped_errors, tester.report()


def test_loader_accepts_find_spec_before_import(codex_project):
    Path("ex0/loading.py").write_text(
        "import importlib.util\n\n"
        'for name in ("pandas", "numpy"):\n'
        "    try:\n"
        "        if importlib.util.find_spec(name) is None:\n"
        "            raise ImportError(name)\n"
        "        reagent = importlib.import_module(name)\n"
        "        print(name, reagent.__version__)\n"
        "    except ImportError:\n"
        '        print(name, "missing: pip install -r requirements.txt")\n'
        '        print("poetry install")\n'
        'print("pip resolves requirements.txt; Poetry locks pyproject.toml")\n'
    )
    tester = CodexTester()
    tester.run("ex0")
    assert not tester.grouped_errors, tester.report()


def test_dependency_constraints_compare_equivalent_ranges(codex_project):
    Path("ex0/requirements.txt").write_text("pandas~=3.0\nnumpy~=2.0\n")
    path = Path("ex0/pyproject.toml")
    path.write_text(
        path.read_text()
        .replace('pandas = "*"', 'pandas = "^3.0"')
        .replace('numpy = "*"', 'numpy = "^2.0"')
    )
    tester = CodexTester()
    tester.run("ex0")
    assert outcome(tester, "Dependency declarations")["status"] == "passed"


def test_light_accepts_recorded_rejected_prose_and_package_from_import(
    codex_project,
):
    path = Path("alchemy/grimoire/light_spellbook.py")
    path.write_text(
        path.read_text().replace(
            'return f"Spell {status}: {spell_name} ({result})"',
            'return f"Spell {status}: {spell_name}"',
        )
    )
    path = Path("ft_kaboom_0.py")
    path.write_text(
        "from alchemy import"
        ' grimoire\n\nprint(grimoire.light_spell_record("Fantasy", "earth"))\n'
    )
    tester = CodexTester()
    tester.run("grimoire")
    assert not tester.grouped_errors, tester.report()


def test_dark_functions_are_checked_despite_intentional_cycle(codex_project):
    path = Path("alchemy/grimoire/dark_spellbook.py")
    path.write_text(path.read_text().replace('"bats"', '"earth"'))
    tester = CodexTester()
    tester.run("grimoire")
    assert outcome(tester, "Dark circular import")["status"] == "passed"
    assert outcome(tester, "Dark ingredient behavior")["status"] == "failed"


def test_dark_error_before_mutual_import_is_rejected(codex_project):
    path = Path("alchemy/grimoire/dark_validator.py")
    path.write_text(
        'raise ImportError("circular import")\n' + path.read_text()
    )
    tester = CodexTester()
    tester.run("grimoire")
    assert outcome(tester, "Dark grimoire structure")["status"] == "passed"
    assert outcome(tester, "Dark circular import")["status"] == "failed"


def test_dark_validator_accepts_the_pdf_example_name(codex_project):
    for name in ("dark_spellbook", "dark_validator"):
        path = Path("alchemy/grimoire") / (name + ".py")
        path.write_text(
            path.read_text().replace(
                "dark_validate_ingredients", "validate_ingredients"
            )
        )
    tester = CodexTester()
    tester.run("grimoire")
    assert not tester.grouped_errors, tester.report()


@pytest.mark.parametrize(
    "path,exception",
    [("ft_alembic_1.py", "AttributeError"), ("ft_kaboom_1.py", "ImportError")],
)
def test_codex_accepts_caught_teaching_exceptions(
    codex_project, path, exception
):
    file = Path(path)
    source = file.read_text()
    file.write_text(
        "try:\n"
        + "".join(
            ("    " + line if line else "") + "\n"
            for line in source.splitlines()
        )
        + f"except {exception} as error:\n    print(error)\n"
    )
    tester = CodexTester()
    tester.run("alembic" if exception == "AttributeError" else "grimoire")
    assert not tester.grouped_errors, tester.report()


@pytest.mark.parametrize("name", ["ex1/.env", "lab_env/pyvenv.cfg"])
def test_codex_rejects_tracked_secret_or_venv(codex_project, name):
    file = Path(name)
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text("example-only\n")
    subprocess.run(["git", "add", "-f", name], check=True)
    tester = CodexTester()
    tester.run("alembic")
    assert outcome(tester, "Submitted files")["status"] == "failed"


def test_codex_ignores_local_unsubmitted_secret_and_venv(codex_project):
    Path("ex1/.env").write_text("API_KEY=example-only\n")
    Path("lab_env").mkdir()
    Path("lab_env/pyvenv.cfg").write_text("home = /example\n")
    Path("lab_env/bad.py").write_text("syntax error!\n")
    tester = CodexTester()
    tester.run("alembic")
    assert not tester.grouped_errors, tester.report()


def test_missing_installed_reagent_is_a_skip(codex_project, monkeypatch):
    from importlib.util import find_spec

    monkeypatch.setattr(
        "germinette.subjects.python_module_05_bis.importlib.util.find_spec",
        lambda name: None if name == "pandas" else find_spec(name),
    )
    runner = GerminetteRunner()
    assert runner.run_module("python_module_05_bis", "ex0") is None
    assert (
        outcome(runner.last_tester, "Installed dependency versions")["status"]
        == "skipped"
    )


@pytest.mark.parametrize(
    "value,accepted,rejected",
    [
        ("^1.2", "1.9", "2.0"),
        ("^0.2.1", "0.2.9", "0.3"),
        ("~1.2", "1.2.9", "1.3"),
        ("1.2.*", "1.2.3", "1.3"),
    ],
)
def test_poetry_constraints(value, accepted, rejected):
    constraint = poetry_constraint(value)
    assert accepted in constraint
    assert rejected not in constraint
