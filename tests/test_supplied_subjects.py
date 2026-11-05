"""Regressions and valid alternatives derived from the nine supplied PDFs."""

import importlib
from pathlib import Path
import shutil
import textwrap
from types import SimpleNamespace

import pytest


def write(path, source):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(source).strip() + "\n", encoding="utf-8")


@pytest.mark.parametrize(
    "module,version",
    [
        ("00", "3.0"),
        ("01", "3.2"),
        ("02", "3.0"),
        ("03", "3.1"),
        ("04", "3.0"),
        ("05", "3.1"),
        ("05_bis", "1.0"),
        ("06_bis", "1.0"),
        ("07", "3.0"),
    ],
)
def test_supplied_versions(module, version):
    from germinette.core import MODULE_VERSION_LABELS

    assert MODULE_VERSION_LABELS["python_module_" + module] == "v." + version


def test_module00_allows_any_recursive_helper_name(tmp_path, monkeypatch):
    from germinette.subjects.python_module_00 import Tester

    source = tmp_path / "ex6/ft_count_harvest_recursive.py"
    write(
        source,
        """
        def countdown(day=1, total=3):
            if day <= total:
                print(f'Day {day}')
                countdown(day + 1, total)
            else:
                print('Harvest time!')


        def ft_count_harvest_recursive():
            countdown(1, int(input()))
    """,
    )
    monkeypatch.chdir(tmp_path)
    tester = Tester()
    func = tester._load_func("ft_count_harvest_recursive", "Exercise 6")
    assert callable(func), tester.grouped_errors


@pytest.mark.parametrize(
    "source",
    [
        "if True:\n    print('side effect')\n\n"
        "def ft_hello_garden():\n    pass",
        "def ft_hello_garden():\n    import os\n    print(os.name)",
    ],
)
def test_module00_rejects_executable_statements_and_nested_imports(
    tmp_path, monkeypatch, source
):
    from germinette.subjects.python_module_00 import Tester

    write(tmp_path / "ex0/ft_hello_garden.py", source)
    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.test_hello_garden()
    assert tester.grouped_errors


@pytest.mark.parametrize("annotation", ["", " -> int"])
def test_module00_requires_none_return_annotation(
    tmp_path, monkeypatch, annotation
):
    from germinette.subjects.python_module_00 import Tester

    write(
        tmp_path / "ex7/ft_seed_inventory.py",
        f"""
        def ft_seed_inventory(seed_type: str, quantity: int,
                              unit: str){annotation}:
            print('wrong')
    """,
    )
    monkeypatch.chdir(tmp_path)
    tester = Tester()
    # Isolate signature validation from mypy's independent return-value checks.
    monkeypatch.setattr(tester, "check_flake8", lambda path: None)
    tester.test_seed_inventory()
    errors = "\n".join(tester.grouped_errors["Exercise 7"])
    assert "return annotation" in errors


def test_module01_comment_is_not_a_main_guard(tmp_path, monkeypatch):
    from germinette.subjects.python_module_01 import Tester

    write(
        tmp_path / "ex0/ft_garden_intro.py",
        """
        # if __name__ == "__main__":
        print('Plant: Rose, Height: 25cm, Age: 30 days')
    """,
    )
    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.test_garden_intro()
    assert "Missing Pattern" in "\n".join(tester.grouped_errors["Exercise 0"])


def test_module01_accepts_custom_intro_output(tmp_path, monkeypatch):
    from germinette.subjects.python_module_01 import Tester

    write(
        tmp_path / "ex0/ft_garden_intro.py",
        """
        if __name__ == '__main__':
            name, height, age = 'Basil', 20, 15
            print(f'{name}: {height} centimeters, {age} days')
    """,
    )
    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.test_garden_intro()
    assert not tester.grouped_errors


@pytest.mark.parametrize("accept_negative", [False, True])
def test_module01_security_checks_actual_state(
    tmp_path, monkeypatch, accept_negative
):
    from germinette.subjects.python_module_01 import Tester

    source = """
        class Plant:
            def __init__(self, name: str, height: int, age: int) -> None:
                self._height = height
                self._age = age

            def set_height(self, value: int) -> None:
                if value < 0:
                    print('Error: negative height rejected')
                    return
                self._height = value

            def set_age(self, value: int) -> None:
                if value < 0:
                    print('Error: negative age rejected')
                    return
                self._age = value

            def get_height(self) -> int:
                return self._height

            def get_age(self) -> int:
                return self._age


        if __name__ == '__main__':
            plant = Plant('Rose', 10, 20)
            plant.set_height(-1)
            plant.set_age(-1)
    """
    if accept_negative:
        source = source.replace("if value < 0:", "if value == -999:")
    write(tmp_path / "ex4/ft_garden_security.py", source)
    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.test_garden_security()
    assert bool(tester.grouped_errors) is accept_negative


def test_module01_missing_analytics_is_a_failure(monkeypatch):
    from germinette.subjects.python_module_01 import Tester

    class Plant:
        pass

    class Flower(Plant):
        pass

    class Seed(Flower):
        pass

    tester = Tester()
    module = SimpleNamespace(Plant=Plant, Flower=Flower, Seed=Seed)
    monkeypatch.setattr(
        tester, "_load_module", lambda *args: (module, "unused.py")
    )
    monkeypatch.setattr(
        tester, "_run_script", lambda path: "Stats: False Unknown plant"
    )
    tester.test_garden_analytics()
    assert tester.grouped_errors


def test_module02_rejects_suppressed_invalid_temperature(monkeypatch):
    from germinette.subjects.python_module_02 import Tester

    module = SimpleNamespace(
        input_temperature=lambda value: (
            int(value) if value.isnumeric() else None
        ),
        test_temperature=lambda: None,
    )
    tester = Tester()
    monkeypatch.setattr(
        tester, "_load_module", lambda *args: (module, "unused.py")
    )
    monkeypatch.setattr(tester, "verify_strict", lambda *args, **kwargs: True)
    monkeypatch.setattr(
        tester,
        "_run_script",
        lambda path: "=== Garden Temperature Checker ===",
    )
    tester.test_raise_exception()
    assert "Missing Raise" in "\n".join(tester.grouped_errors["Exercise 1"])


@pytest.mark.parametrize("mode", ['"write"', "1", "7"])
def test_module04_accepts_string_and_integer_actions(
    tmp_path, monkeypatch, mode
):
    from germinette.subjects.python_module_04 import Tester

    annotation = "str" if '"' in mode else "int"
    default = '"read"' if annotation == "str" else "0"
    write(
        tmp_path / "ex3/ft_vault_security.py",
        f"""
        def secure_archive(filename: str, mode: {annotation} = {default},
                           content: str = '') -> tuple[bool, str]:
            try:
                if mode == {mode}:
                    with open(filename, 'w') as file:
                        file.write(content)
                    return True, 'written'
                with open(filename) as file:
                    return True, file.read()
            except OSError as error:
                return False, str(error)
    """,
    )
    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.test_vault_security()
    assert not tester.grouped_errors, tester.grouped_errors
    assert not list(tmp_path.glob("*.txt"))


@pytest.mark.parametrize("bad", [False, True])
def test_module04_checks_actual_read_content(tmp_path, monkeypatch, bad):
    from germinette.subjects.python_module_04 import Tester

    read_result = "'fake content'" if bad else "file.read()"
    write(
        tmp_path / "ex3/ft_vault_security.py",
        f"""
        def secure_archive(filename: str, mode: str = 'read',
                           content: str = '') -> tuple[bool, str]:
            try:
                if mode == 'write':
                    with open(filename, 'w') as file:
                        file.write(content)
                    return True, 'written'
                with open(filename) as file:
                    return True, {read_result}
            except OSError as error:
                return False, str(error)
    """,
    )
    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.test_vault_security()
    assert bool(tester.grouped_errors) is bad


@pytest.mark.parametrize(
    "module", ["python_module_07", "python_module_06_bis"]
)
def test_combat_reference(tmp_path, monkeypatch, module):
    source = (
        "python_module_07_golden"
        if module.endswith("07")
        else "nexus_bis_golden"
    )
    shutil.copytree(
        Path(__file__).parent / "fixtures" / source,
        tmp_path,
        dirs_exist_ok=True,
    )
    if module.endswith("bis"):
        for file in (Path(__file__).parent / "fixtures/nexus_golden").glob(
            "*.py"
        ):
            shutil.copy(file, tmp_path / file.name)
    monkeypatch.chdir(tmp_path)
    tester = importlib.import_module("germinette.subjects." + module).Tester()
    tester.run()
    assert not tester.grouped_errors, tester.grouped_errors


@pytest.mark.parametrize(
    "file,before,after,exercise",
    [
        (
            "ex1/creatures.py",
            "self.transformed = True",
            "self.transformed = False",
            "ex1",
        ),
        ("ex2/strategies.py", "print(creature.revert())", "pass", "ex2"),
        (
            "ex2/strategies.py",
            "raise InvalidStrategyError('Invalid defensive strategy')",
            "return",
            "ex2",
        ),
    ],
)
def test_datadeck_rejects_broken_capabilities_and_strategies(
    tmp_path, monkeypatch, file, before, after, exercise
):
    from germinette.subjects.python_module_07 import Tester

    shutil.copytree(
        Path(__file__).parent / "fixtures/python_module_07_golden",
        tmp_path,
        dirs_exist_ok=True,
    )
    path = tmp_path / file
    path.write_text(path.read_text().replace(before, after))
    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.run(exercise)
    assert tester.grouped_errors


@pytest.mark.parametrize(
    "module,paths",
    [
        ("02", ["ex1/ft_raise_exception.py"]),
        ("05", ["ex0/data_processor.py", "ex2/data_pipeline.py"]),
        (
            "06_bis",
            [
                "data_processor.py",
                "data_stream.py",
                "data_pipeline.py",
                "ex3/__init__.py",
                "ex4/__init__.py",
                "battle.py",
                "capacitor.py",
                "tournament.py",
            ],
        ),
    ],
)
def test_supplied_layout_detection(tmp_path, monkeypatch, module, paths):
    from germinette.core import ModuleDetector

    for path in paths:
        write(tmp_path / path, "")
    monkeypatch.chdir(tmp_path)
    assert ModuleDetector.detect() == "python_module_" + module


@pytest.mark.parametrize("abort_on_invalid", [False, True])
def test_module03_discards_only_invalid_scores(
    tmp_path, monkeypatch, abort_on_invalid
):
    from germinette.subjects.python_module_03 import Tester

    source = """
        import sys


        def main() -> None:
            scores = []
            for parameter in sys.argv[1:]:
                try:
                    scores.append(int(parameter))
                except ValueError:
                    print(f'Invalid parameter: {parameter}')
                    # INVALID_ACTION
            if not scores:
                print('No scores provided')
                return
            print(f'Total players: {len(scores)}')
            print(f'Total score: {sum(scores)}')
            print(f'Average score: {sum(scores) / len(scores)}')
            print(f'High score: {max(scores)}')


        if __name__ == '__main__':
            main()
    """
    source = source.replace(
        "# INVALID_ACTION", "return" if abort_on_invalid else "pass"
    )
    write(tmp_path / "ex1/ft_score_analytics.py", source)
    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.test_score_analytics()
    assert bool(tester.grouped_errors) is abort_on_invalid


def test_module02_accepts_intentional_type_error(tmp_path, monkeypatch):
    from germinette.subjects.python_module_02 import Tester

    write(
        tmp_path / "ex2/ft_different_errors.py",
        """
        def garden_operations(operation_number: int) -> None:
            if operation_number == 0:
                int('abc')
            elif operation_number == 1:
                _ = 1 / 0
            elif operation_number == 2:
                open('/not/existing/file')
            elif operation_number == 3:
                _ = 'text' + 1


        def test_error_types() -> None:
            print('=== Garden Error Types Demo ===')
            for operation in (0, 1, 2, 3, 4):
                try:
                    garden_operations(operation)
                except (ValueError, ZeroDivisionError,
                        FileNotFoundError, TypeError) as error:
                    print(error.__class__.__name__)


        if __name__ == '__main__':
            test_error_types()
    """,
    )
    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.test_different_errors()
    assert not tester.grouped_errors, tester.grouped_errors


def test_datadeck_accepts_different_creature_names(tmp_path, monkeypatch):
    from germinette.subjects.python_module_07 import Tester

    source = Path(__file__).parent / "fixtures/python_module_07_golden"
    shutil.copytree(source, tmp_path, dirs_exist_ok=True)
    for path in tmp_path.rglob("*.py"):
        path.write_text(
            path.read_text()
            .replace("Flameling", "Emberling")
            .replace("Pyrodon", "Firebird")
        )
    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.test_creature_factory()
    assert not tester.grouped_errors, tester.grouped_errors


def test_datadeck_rejects_print_only_demo(tmp_path, monkeypatch):
    from germinette.subjects.python_module_07 import Tester

    source = Path(__file__).parent / "fixtures/python_module_07_golden"
    shutil.copytree(source, tmp_path, dirs_exist_ok=True)
    write(tmp_path / "battle.py", "print('Testing factory and battle')")
    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.test_creature_factory()
    assert tester.grouped_errors


def test_type_hints_include_all_parameter_kinds(tmp_path):
    from germinette.core import BaseTester

    path = tmp_path / "annotations.py"
    write(
        path,
        "def f(positional, /, *items, keyword, **options) -> None:\n    pass",
    )
    errors = BaseTester().check_type_hints(path)
    for name in ("positional", "items", "keyword", "options"):
        assert name in errors
