"""The Codex: Packages, Environments and the Alchemist's Toolchain v1.0."""

import ast
import importlib.util
import importlib.metadata
import json
import os
import re
import shutil
import sys
import tempfile
import venv
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from packaging.version import Version

from germinette.subjects.bis_common import (
    BisTester,
    import_aliases,
    qualified_name,
)

FILES = {
    "ex0": [
        "ex0/construct.py",
        "ex0/loading.py",
        "ex0/requirements.txt",
        "ex0/pyproject.toml",
    ],
    "ex1": [
        "ex1/oracle.py",
        "ex1/requirements.txt",
        "ex1/.env.example",
        "ex1/.gitignore",
    ],
    "alembic": [
        "elements.py",
        "alchemy/__init__.py",
        "alchemy/elements.py",
        "ft_alembic_0.py",
        "ft_alembic_1.py",
    ],
    "transmutation": [
        "alchemy/potions.py",
        "alchemy/transmutation/__init__.py",
        "alchemy/transmutation/recipes.py",
        "ft_distillation_0.py",
        "ft_transmutation_0.py",
    ],
    "grimoire": [
        "alchemy/grimoire/__init__.py",
        "alchemy/grimoire/light_spellbook.py",
        "alchemy/grimoire/light_validator.py",
        "alchemy/grimoire/dark_spellbook.py",
        "alchemy/grimoire/dark_validator.py",
        "ft_kaboom_0.py",
        "ft_kaboom_1.py",
    ],
}
CONFIG_KEYS = (
    "MATRIX_MODE",
    "DATABASE_URL",
    "API_KEY",
    "LOG_LEVEL",
    "ZION_ENDPOINT",
)
RUNTIME = Path(__file__).with_name("codex_runtime.py")


def python_files(directory):
    paths = []
    for root, directories, files in os.walk(directory):
        directories[:] = [
            name
            for name in directories
            if not name.startswith(".")
            and name != "__pycache__"
            and not (Path(root) / name / "pyvenv.cfg").exists()
        ]
        paths.extend(
            Path(root) / name for name in files if name.endswith(".py")
        )
    return paths


def requirements(path):
    result = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.split(" #", 1)[0].strip()
        if not line or line.startswith("#"):
            continue
        requirement = Requirement(line)
        if requirement.url:
            raise NotImplementedError(
                "Direct URL dependency needs manual source review."
            )
        if requirement.marker and not requirement.marker.evaluate():
            continue
        name = requirement.name.lower().replace("_", "-")
        if name in result:
            raise ValueError("Duplicate dependency: " + name)
        result[name] = requirement.specifier
    return result


def poetry_constraint(value):
    if isinstance(value, dict):
        value = value.get("version", "*")
    if not isinstance(value, str):
        raise ValueError("Dependency constraints must be strings.")
    value = value.strip()
    if not value:
        raise ValueError("Empty dependency constraint.")
    if value == "*":
        return SpecifierSet()
    if (
        value.startswith("^")
        or value.startswith("~")
        and not value.startswith("~=")
    ):
        release = list(Version(value[1:]).release)
        if value[0] == "^":
            index = next(
                (i for i, n in enumerate(release) if n), len(release) - 1
            )
        else:
            index = min(1, len(release) - 1)
        upper = release[: index + 1]
        upper[-1] += 1
        return SpecifierSet(
            ">=" + value[1:] + ",<" + ".".join(map(str, upper))
        )
    if value[0].isdigit():
        value = "==" + value
    return SpecifierSet(value)


class Tester(BisTester):
    def __init__(self):
        super().__init__()
        self.title = (
            "[bold cyan]Testing Module 05 bis: The Codex (v1.0)[/bold cyan]"
        )
        self.exercises = [(name, getattr(self, name)) for name in FILES]

    def run(self, exercise_name=None):
        if (
            not exercise_name or exercise_name.replace(".py", "") in FILES
        ) and (
            any(
                Path(path).is_file()
                for paths in FILES.values()
                for path in paths
            )
        ):
            self.submission()
        super().run(exercise_name)

    def submission(self):
        result = self.process(
            "Submitted files", ["git", "rev-parse", "--show-toplevel"]
        )
        if result is None:
            return
        if result.returncode:
            self.record(
                "Submitted files",
                "skipped",
                "Not a Git repository; tracked secrets/venvs need review.",
            )
            return
        result = self.process(
            "Submitted files", ["git", "ls-files", "-z", "--", "."]
        )
        if result is not None:
            forbidden = [
                name
                for name in result.stdout.split("\0")
                if name
                and (
                    Path(name).name in {".env", "pyvenv.cfg"}
                    or "site-packages" in Path(name).parts
                )
            ]
            self.check(
                "Submitted files",
                result.returncode == 0 and not forbidden,
                "Do not submit .env files or virtual environments: "
                + ", ".join(forbidden),
            )

    def prepare(self, exercise):
        number = list(FILES).index(exercise)
        label = f"Exercise {number}"
        if not self.files(label + " files", FILES[exercise]):
            return False
        paths = {Path(p) for p in FILES[exercise] if p.endswith(".py")}
        if exercise in ("ex0", "ex1"):
            paths.update(python_files(exercise))
        else:
            known = {Path(p) for group in FILES.values() for p in group}
            paths.update(
                p
                for p in python_files(".")
                if p not in known and p.parts[0] not in ("ex0", "ex1")
            )
        paths = sorted(paths)
        self.lint(label + " flake8", paths)
        allowed = {
            "ex0": {"os", "sys", "site", "importlib", "pandas", "numpy"},
            "ex1": {"os", "sys", "dotenv"},
        }.get(exercise, {"builtins"})
        self.policy(
            label + " forbidden operations",
            paths,
            no_syspath=True,
            allowed_imports=allowed,
        )
        self.types(label + " types", paths)
        return True

    def types(self, name, paths):
        if importlib.util.find_spec("mypy") is None:
            self.record(
                name, "skipped", "Install mypy in the tester environment."
            )
            return
        result = self.process(
            name,
            [
                sys.executable,
                "-m",
                "mypy",
                "--config-file=",
                "--disallow-untyped-defs",
                "--follow-imports=silent",
                "--ignore-missing-imports",
                "--explicit-package-bases",
                "--show-error-codes",
                "--no-error-summary",
                *map(str, paths),
            ],
        )
        if result is None:
            return
        lines = (result.stdout + result.stderr).splitlines()
        remaining = [
            line
            for line in lines
            if not (
                re.match(
                    r"ft_alembic_1\.py:\d+: error: Module"
                    r" (?:\"alchemy\"|has no)",
                    line,
                )
                and 'has no attribute "create_earth"' in line
                and "[attr-defined]" in line
            )
            and ": note:" not in line
        ]
        if (
            result.returncode > 1
            or "INTERNAL ERROR" in result.stderr
            or result.returncode
            and not lines
        ):
            self.record(name, "errors", "\n".join(lines))
        else:
            self.check(name, not remaining, "\n".join(remaining))

    def observe(
        self,
        name,
        script,
        *,
        python=None,
        cwd=None,
        env=None,
        missing=False,
        blocked=None,
    ):
        command = [str(python or sys.executable), "-E", "-B"]
        if missing:
            command.append("-S")
        args = [*command, str(RUNTIME), script]
        if blocked:
            args.append(blocked)
        result = self.process(name, args, cwd=cwd, env=env)
        if result is None:
            return None
        try:
            stderr, payload = result.stderr.rsplit("GERMINETTE_TRACE=", 1)
            trace = json.loads(payload)
        except (ValueError, TypeError):
            self.record(
                name,
                "errors",
                "Script exited without an observation: "
                + result.stdout
                + result.stderr,
            )
            return None
        trace["stdout"] = result.stdout
        trace["stderr"] = stderr
        return trace

    def demonstration(self, path, calls, imports, *, exception=None):
        trace = self.observe(path, path)
        tree = self.tree(path)
        if trace is None or tree is None:
            return
        executed = set(trace["lines"].get(path, []))
        nodes = [
            node
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
            and node.lineno in executed
        ]
        correct_imports = all(
            any(
                isinstance(node, ast.Import)
                and kind in ("import", "package")
                and any(
                    item.name == module
                    or kind == "package"
                    and module.startswith(item.name + ".")
                    for item in node.names
                )
                or isinstance(node, ast.ImportFrom)
                and kind in ("from", "package")
                and (
                    node.module == module
                    or any(
                        (node.module or "") + "." + item.name == module
                        for item in node.names
                    )
                )
                for node in nodes
            )
            for kind, module in imports
        )
        correct_calls = all(
            [file, function] in trace["calls"] for file, function in calls
        )
        printed = all(
            any(
                file == source
                and function == name
                and value
                and value in trace["stdout"]
                for source, name, value in trace["returns"]
            )
            for file, function in calls
        )
        error = trace["exit"]
        correct_error = error is None
        if exception:
            expected_type, module, attribute = exception
            aliases = import_aliases(tree)
            attempted = {
                node.lineno
                for node in ast.walk(tree)
                if isinstance(node, ast.Call)
                and qualified_name(node.func, aliases)
                == module + "." + attribute
            }
            observed = any(
                file == path
                and line in attempted
                and kind == expected_type
                and module in message
                and attribute in message
                for file, line, kind, message in trace["errors"]
            )
            ordered = any(
                event[0] == "exception"
                and event[1] == path
                and event[2] in attempted
                and event[3] == expected_type
                and all(
                    ["call", file, function] in trace["events"][:index]
                    for file, function in calls
                )
                for index, event in enumerate(trace["events"])
            )
            correct_error = (
                observed
                and (error is None or error[0] == expected_type)
                and ordered
            )
        self.check(
            path,
            correct_imports and correct_calls and correct_error and printed,
            "Execute the required imports and function calls, and print "
            "the demonstration. Expected teaching errors may be caught.\n"
            + trace["stdout"]
            + trace["stderr"]
            + str(error or ""),
        )

    def ex0(self):
        if not self.prepare("ex0"):
            return
        try:
            pip = requirements("ex0/requirements.txt")
            project = tomllib.loads(Path("ex0/pyproject.toml").read_text())
            poetry = (
                project.get("tool", {})
                .get("poetry", {})
                .get("dependencies", {})
            )
            if poetry:
                declared = {
                    name.lower().replace("_", "-"): poetry_constraint(value)
                    for name, value in poetry.items()
                    if name != "python"
                }
            else:
                declared = {}
                for value in project.get("project", {}).get(
                    "dependencies", []
                ):
                    requirement = Requirement(value)
                    if (
                        requirement.marker
                        and not requirement.marker.evaluate()
                    ):
                        continue
                    declared[requirement.name.lower().replace("_", "-")] = (
                        requirement.specifier
                    )
            valid = (
                {"pandas", "numpy"} <= pip.keys()
                and pip.keys() == declared.keys()
                and all(
                    not constraint.is_unsatisfiable()
                    and constraint.to_range() == declared[name].to_range()
                    for name, constraint in pip.items()
                )
            )
            self.check(
                "Dependency declarations",
                valid,
                "Declare pandas and numpy with the same constraints in "
                "requirements.txt and the Poetry pyproject.toml.",
            )
        except NotImplementedError as error:
            self.record("Dependency declarations", "skipped", str(error))
            return
        except (
            OSError,
            UnicodeError,
            ValueError,
            TypeError,
            AttributeError,
        ) as error:
            self.check("Dependency declarations", False, str(error))
            return
        with tempfile.TemporaryDirectory(prefix="germinette-05-") as directory:
            root = Path(directory)
            shutil.copytree("ex0", root / "ex0")
            # Match CLI defaults; copying standalone interpreters can break.
            venv.create(
                root / "lab_env", with_pip=False, symlinks=os.name != "nt"
            )
            virtual = (
                root
                / "lab_env"
                / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            )
            base = str(
                Path(
                    getattr(sys, "_base_executable", None) or sys.executable
                ).resolve()
            )
            clean = {
                key: value
                for key, value in os.environ.items()
                if key not in {"VIRTUAL_ENV", "PYTHONHOME", "PYTHONPATH"}
            }
            outside = self.observe(
                "Outside virtual environment",
                "ex0/construct.py",
                python=base,
                cwd=root,
                env=clean,
            )
            inside = self.observe(
                "Inside virtual environment",
                "ex0/construct.py",
                python=virtual,
                cwd=root,
                env={**clean, "VIRTUAL_ENV": str(root / "lab_env")},
            )
            if outside is not None and inside is not None:
                output = outside["stdout"].lower()
                self.check(
                    "Environment detection",
                    not outside["exit"]
                    and not inside["exit"]
                    and outside["stdout"] != inside["stdout"]
                    and str(base) in outside["stdout"]
                    and str(virtual) in inside["stdout"]
                    and str(root / "lab_env") in inside["stdout"]
                    and "site-packages" in inside["stdout"],
                    "Show the Python executable, environment identity/path "
                    "and virtual package location; distinguish"
                    " outside/inside.",
                )
                self.check(
                    "Environment setup instructions",
                    bool(re.search(r"python\S*\s+-m\s+venv\s+\S+", output))
                    and "activat" in output,
                    "Outside a venv, show creation and activation commands.",
                )
            missing = self.observe(
                "Missing dependencies",
                "ex0/loading.py",
                python=virtual,
                cwd=root,
                env=clean,
                missing=True,
            )
            if missing is not None:
                output = (missing["stdout"] + missing["stderr"]).lower()
                self.check(
                    "Missing dependency guidance",
                    not missing["exit"]
                    and all(name in output for name in pip)
                    and "pip install" in output
                    and "poetry" in output
                    and ("poetry install" in output or "poetry add" in output),
                    "Attempt each reagent import, handle missing dependencies "
                    "and show pip and Poetry install commands.",
                )
            available = all(
                importlib.util.find_spec(name) is not None for name in pip
            )
            if available:
                try:
                    available = all(
                        importlib.metadata.version(name) in constraint
                        for name, constraint in pip.items()
                    )
                except importlib.metadata.PackageNotFoundError:
                    available = False
            if not available:
                self.record(
                    "Installed dependency versions",
                    "skipped",
                    "Install versions matching ex0/requirements.txt in the"
                    " tester environment.",
                )
            else:
                loaded = self.observe(
                    "Installed dependencies",
                    "ex0/loading.py",
                    cwd=root,
                    env=clean,
                )
                if loaded is not None:
                    versions = loaded["versions"]
                    self.check(
                        "Installed dependency versions",
                        not loaded["exit"]
                        and all(
                            name in versions
                            and name in loaded["stdout"].lower()
                            and versions[name] in loaded["stdout"]
                            for name in pip
                        ),
                        "Import every declared reagent and print its installed"
                        " version.",
                    )
                    output = loaded["stdout"].lower()
                    self.check(
                        "pip and Poetry comparison",
                        all(
                            word in output
                            for word in (
                                "pip",
                                "poetry",
                                "requirements.txt",
                                "pyproject.toml",
                                "lock",
                            )
                        ),
                        "Explain pip requirements versus Poetry's locked"
                        " dependencies.",
                    )
                for reagent in sorted(pip):
                    partial = self.observe(
                        "Missing reagent: " + reagent,
                        "ex0/loading.py",
                        cwd=root,
                        env=clean,
                        blocked=reagent,
                    )
                    if partial is not None:
                        output = (
                            partial["stdout"] + partial["stderr"]
                        ).lower()
                        self.check(
                            "Missing reagent: " + reagent,
                            not partial["exit"]
                            and reagent in output
                            and "pip install" in output
                            and (
                                "poetry install" in output
                                or "poetry add" in output
                            ),
                            "Handle a single missing reagent and give both"
                            " install commands.",
                        )

    def ex1(self):
        if not self.prepare("ex1"):
            return
        try:
            declared = requirements("ex1/requirements.txt")
            self.check(
                "Oracle dependency declaration",
                "python-dotenv" in declared,
                "Declare python-dotenv in ex1/requirements.txt.",
            )
        except NotImplementedError as error:
            self.record("Oracle dependency declaration", "skipped", str(error))
        except (OSError, UnicodeError, ValueError) as error:
            self.check("Oracle dependency declaration", False, str(error))
        with tempfile.TemporaryDirectory(
            prefix="germinette-ignore-"
        ) as directory:
            root = Path(directory)
            (root / "ex1").mkdir()
            shutil.copyfile("ex1/.gitignore", root / "ex1/.gitignore")
            initialized = self.process(
                "Ignore .env", ["git", "init", "-q"], cwd=root
            )
            if initialized is not None and initialized.returncode == 0:
                ignored = self.process(
                    "Ignore .env",
                    [
                        "git",
                        "-c",
                        "core.excludesFile=" + os.devnull,
                        "check-ignore",
                        "-q",
                        "ex1/.env",
                    ],
                    cwd=root,
                )
                if ignored is not None:
                    self.check(
                        "Ignore .env",
                        ignored.returncode == 0,
                        "ex1/.gitignore must effectively ignore .env,"
                        " including negations.",
                    )
            elif initialized is not None:
                self.record("Ignore .env", "errors", initialized.stderr)
        if importlib.util.find_spec("dotenv") is None:
            self.record(
                "Oracle runtime",
                "skipped",
                "Install python-dotenv in the tester environment.",
            )
            return
        from dotenv import dotenv_values

        example = dotenv_values("ex1/.env.example", interpolate=False)
        self.check(
            "Example configuration",
            set(CONFIG_KEYS) <= example.keys(),
            "Document all five configuration keys in .env.example.",
        )
        with tempfile.TemporaryDirectory(
            prefix="germinette-oracle-"
        ) as directory:
            root = Path(directory)
            shutil.copytree(
                "ex1", root / "ex1", ignore=shutil.ignore_patterns(".env")
            )
            # Stop dotenv's parent search at the isolated project boundary.
            (root / ".env").write_text("")
            clean = {
                key: value
                for key, value in os.environ.items()
                if key not in {
                    *CONFIG_KEYS,
                    "PYTHON_DOTENV_DISABLED",
                    "PYTHONPATH",
                }
            }
            empty = self.observe(
                "Oracle without configuration",
                "ex1/oracle.py",
                cwd=root,
                env=clean,
            )
            if empty is not None:
                output = (empty["stdout"] + empty["stderr"]).lower()
                self.check(
                    "Oracle without configuration",
                    not empty["exit"]
                    and bool(empty["stdout"].strip())
                    and any(
                        word in output
                        for word in (
                            "missing",
                            "warn",
                            "default",
                            "not set",
                            "not configured",
                        )
                    ),
                    "Show defaults and warn about missing configuration"
                    " without crashing.",
                )
            values = dict(
                zip(
                    CONFIG_KEYS,
                    (
                        "development",
                        "sqlite:///codex-dev",
                        "codex-example-dev",
                        "DEBUG",
                        "https://dev.invalid",
                    ),
                )
            )
            (root / "ex1/.env").write_text(
                "".join(f"{key}={value}\n" for key, value in values.items())
            )
            dev = self.observe(
                "Oracle development", "ex1/oracle.py", cwd=root, env=clean
            )
            overrides = dict(
                zip(
                    CONFIG_KEYS,
                    (
                        "production",
                        "postgresql://codex-prod",
                        "codex-example-prod",
                        "ERROR",
                        "https://prod.invalid",
                    ),
                )
            )
            prod = self.observe(
                "Oracle production",
                "ex1/oracle.py",
                cwd=root,
                env={**clean, **overrides},
            )
            for name, trace, expected in (
                ("Dotenv configuration", dev, values),
                ("Environment precedence", prod, overrides),
            ):
                if trace is not None:
                    reads = trace["reads"]
                    self.check(
                        name,
                        not trace["exit"]
                        and trace["dotenv"]
                        and (
                            all(
                                [key, value] in reads
                                for key, value in expected.items()
                            )
                            or expected in trace["configuration"]
                        ),
                        "Load dotenv and use all five configuration values; "
                        "environment variables must take priority.",
                    )
            if dev is not None and prod is not None:
                self.check(
                    "Development and production",
                    not dev["exit"]
                    and not prod["exit"]
                    and dev["stdout"] != prod["stdout"],
                    "Show a visible development/production difference.",
                )

    def alembic(self):
        if not self.prepare("alembic"):
            return
        self.probe(
            "Alembic package exports",
            r"""
import elements, alchemy
from alchemy import elements as local_elements

assert elements.create_fire() == "Fire element created"
assert elements.create_water() == "Water element created"
assert local_elements.create_earth() == "Earth element created"
assert local_elements.create_air() == "Air element created"
assert alchemy.create_air() == "Air element created"
assert not hasattr(alchemy, "create_earth")
""",
        )
        self.demonstration(
            "ft_alembic_0.py",
            [("elements.py", "create_fire")],
            [("import", "elements")],
        )
        self.demonstration(
            "ft_alembic_1.py",
            [("alchemy/elements.py", "create_air")],
            [("import", "alchemy")],
            exception=("AttributeError", "alchemy", "create_earth"),
        )

    def transmutation(self):
        if not self.prepare("transmutation"):
            return
        self.probe(
            "Potion and recipe behavior",
            r"""
import elements
import alchemy.elements as local

values = dict(
    fire="Fire element created",
    water="Water element created",
    earth="Earth element created",
    air="Air element created",
)
calls = []


def ingredient(name):
    def create():
        calls.append(name)
        return values[name]

    return create


elements.create_fire = ingredient("fire")
elements.create_water = ingredient("water")
local.create_earth = ingredient("earth")
local.create_air = ingredient("air")
from alchemy.potions import healing_potion, strength_potion
from alchemy.transmutation.recipes import lead_to_gold

for changed in (False, True):
    if changed:
        values.update({name: "observed-" + name for name in values})
    healing = (
        f"Healing potion brewed with '{values['earth']}' "
        f"and '{values['air']}'"
    )
    strength = (
        f"Strength potion brewed with '{values['fire']}' "
        f"and '{values['water']}'"
    )
    calls.clear()
    assert healing_potion() == healing
    assert {"earth", "air"} <= set(
        calls
    ), "Healing must use the element functions"
    calls.clear()
    assert strength_potion() == strength
    assert {"fire", "water"} <= set(
        calls
    ), "Strength must use the element functions"
    calls.clear()
    expected = (
        f"Recipe transmuting Lead to Gold: brew '{values['air']}' and "
        f"'{strength}' mixed with '{values['fire']}'"
    )
    assert lead_to_gold() == expected
    assert {"air", "fire", "water"} <= set(
        calls
    ), "Recipe must use elements/potion"
""",
        )
        self.demonstration(
            "ft_distillation_0.py",
            [
                ("alchemy/potions.py", "healing_potion"),
                ("alchemy/potions.py", "strength_potion"),
            ],
            [("from", "alchemy.potions")],
        )
        self.demonstration(
            "ft_transmutation_0.py",
            [("alchemy/transmutation/recipes.py", "lead_to_gold")],
            [("import", "alchemy.transmutation.recipes")],
        )
        trace = self.observe("Recipe import styles", "ft_transmutation_0.py")
        tree = self.tree("alchemy/transmutation/recipes.py")
        if trace is not None and tree is not None:
            lines = trace["lines"].get("alchemy/transmutation/recipes.py", [])
            imports = [
                n
                for n in ast.walk(tree)
                if isinstance(n, (ast.Import, ast.ImportFrom))
                and n.lineno in lines
            ]
            self.check(
                "Recipe import styles",
                any(isinstance(n, ast.ImportFrom) and n.level for n in imports)
                and any(
                    isinstance(n, ast.Import)
                    or isinstance(n, ast.ImportFrom)
                    and not n.level
                    for n in imports
                ),
                "Execute at least one absolute and one relative import in"
                " recipes.py.",
            )

    def grimoire(self):
        if not self.prepare("grimoire"):
            return
        self.probe(
            "Light grimoire",
            r"""
import re
import alchemy.grimoire.light_spellbook as book
import alchemy.grimoire.light_validator as validator

allowed = book.light_spell_allowed_ingredients()
assert isinstance(allowed, list) and set(allowed) == {
    "earth",
    "air",
    "fire",
    "water",
}
for ingredients in (
    "EARTH",
    "air",
    "FiRe",
    "water",
    "Earth, wind and fire",
    "unknown",
    "",
    "bats",
):
    valid = any(item in ingredients.lower() for item in allowed)
    result = validator.validate_ingredients(ingredients)
    assert (
        isinstance(result, str)
        and ingredients.lower() in result.lower()
    )
    assert set(
        re.findall(r"\b(?:VALID|INVALID)\b", result.upper())
    ) == {"VALID" if valid else "INVALID"}
    result = book.light_spell_record("CodexTest", ingredients)
    assert isinstance(result, str) and "CodexTest" in result
    pattern = (
        r"\b(record\w*|accept\w*|success\w*)\b"
        if valid
        else r"\b(reject\w*|denied|invalid|fail\w*)\b"
    )
    assert re.search(pattern, result, re.I), result
original = validator.validate_ingredients
allowed_function = book.light_spell_allowed_ingredients


def changed_allowed():
    return ["moonstone"]


for key, value in list(vars(validator).items()):
    if value is allowed_function:
        setattr(validator, key, changed_allowed)
book.light_spell_allowed_ingredients = changed_allowed
assert re.search(
    r"\bVALID\b", validator.validate_ingredients("moonstone")
), "Validator must consult allowed ingredients"
assert re.search(
    r"\bINVALID\b", validator.validate_ingredients("earth")
)
book.light_spell_allowed_ingredients = allowed_function
for key, value in list(vars(validator).items()):
    if value is changed_allowed:
        setattr(validator, key, allowed_function)


def reject(ingredients):
    return ingredients + " - INVALID"


references = [
    key for key, value in vars(book).items() if value is original
]
validator.validate_ingredients = reject
for key in references:
    setattr(book, key, reject)
assert re.search(
    r"reject|denied|invalid|fail",
    book.light_spell_record("CodexTest", "earth"),
    re.I,
), "Recorder must consult validator"
""",
        )
        self.demonstration(
            "ft_kaboom_0.py",
            [("alchemy/grimoire/light_spellbook.py", "light_spell_record")],
            [("package", "alchemy.grimoire")],
        )
        self.dark_grimoire()

    def dark_grimoire(self):
        book = "alchemy/grimoire/dark_spellbook.py"
        validator = "alchemy/grimoire/dark_validator.py"
        trees = [self.tree(path) for path in (book, validator)]
        if any(tree is None for tree in trees):
            return
        definitions = [
            {
                node.name
                for node in tree.body
                if isinstance(node, ast.FunctionDef)
            }
            for tree in trees
        ]
        functions = {
            "dark_spell_allowed_ingredients",
            "dark_spell_record",
        } <= definitions[0]
        functions = functions and bool(
            {"validate_ingredients", "dark_validate_ingredients"}
            & definitions[1]
        )
        mutual_imports = [
            [
                node
                for node in tree.body
                if isinstance(node, (ast.Import, ast.ImportFrom))
                and (
                    isinstance(node, ast.ImportFrom)
                    and (
                        node.module is not None
                        and node.module.endswith(target)
                        or any(alias.name == target for alias in node.names)
                    )
                    or isinstance(node, ast.Import)
                    and any(
                        alias.name.endswith("." + target)
                        for alias in node.names
                    )
                )
            ]
            for tree, target in zip(
                trees, ("dark_validator", "dark_spellbook")
            )
        ]
        self.check(
            "Dark grimoire structure",
            functions and all(mutual_imports),
            "Define the dark functions/ingredients and mutual top-level"
            " imports.",
        )
        trace = self.observe("Dark circular import", "ft_kaboom_1.py")
        tree = self.tree("ft_kaboom_1.py")
        if trace is None or tree is None:
            return
        lines = trace["lines"].get("ft_kaboom_1.py", [])
        direct = any(
            node.lineno in lines
            and (
                isinstance(node, ast.Import)
                and any(
                    alias.name == "alchemy.grimoire.dark_spellbook"
                    for alias in node.names
                )
                or isinstance(node, ast.ImportFrom)
                and (
                    node.module == "alchemy.grimoire.dark_spellbook"
                    or node.module == "alchemy.grimoire"
                    and any(
                        alias.name == "dark_spellbook" for alias in node.names
                    )
                )
            )
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
        )
        aliases = import_aliases(tree)
        record_attempt = any(
            isinstance(node, ast.Call)
            and qualified_name(node.func, aliases)
            == "alchemy.grimoire.dark_spellbook.dark_spell_record"
            for node in ast.walk(tree)
        )
        errors = trace["errors"]
        cycle = any(
            kind == "ImportError"
            and (
                "circular import" in message.lower()
                or "partially initialized" in message.lower()
            )
            for _, _, kind, message in errors
        )
        frames = {file for file, _, kind, _ in errors if kind == "ImportError"}
        self.check(
            "Dark circular import",
            direct
            and record_attempt
            and all(
                any(
                    node.lineno in trace["lines"].get(path, [])
                    for node in imports
                )
                for path, imports in zip((book, validator), mutual_imports)
            )
            and cycle
            and {book, validator} <= frames
            and (trace["exit"] is None or trace["exit"][0] == "ImportError"),
            "Demonstrate a genuine ImportError from the mutually importing"
            " dark pair; it may be caught or uncaught.\n"
            + str(trace["exit"] or ""),
        )
        # Inspect dark functions without repairing the submitted files.
        self.probe(
            "Dark ingredient behavior",
            r"""
import ast
import re
import sys
import types
from pathlib import Path
import alchemy.grimoire as package

pending = []
for name in ("dark_spellbook", "dark_validator"):
    filename = "alchemy/grimoire/" + name + ".py"
    module = types.ModuleType("alchemy.grimoire." + name)
    module.__package__ = "alchemy.grimoire"
    sys.modules[module.__name__] = module
    setattr(package, name, module)
    tree = ast.parse(Path(filename).read_text())
    target = (
        "dark_validator"
        if name == "dark_spellbook"
        else "dark_spellbook"
    )
    imports = [
        node
        for node in tree.body
        if (
            isinstance(node, ast.ImportFrom)
            and (
                (node.module or "").endswith(target)
                or any(alias.name == target for alias in node.names)
            )
            or isinstance(node, ast.Import)
            and any(
                alias.name.endswith("." + target)
                for alias in node.names
            )
        )
    ]
    tree.body = [node for node in tree.body if node not in imports]
    exec(compile(tree, filename, "exec"), vars(module))
    pending.append((module, imports, filename))
for module, imports, filename in pending:
    tree = ast.Module(body=imports, type_ignores=[])
    exec(compile(tree, filename, "exec"), vars(module))
book = package.dark_spellbook
validator = package.dark_validator
validate = getattr(validator, "dark_validate_ingredients", None)
if validate is None:
    validate = validator.validate_ingredients
allowed = book.dark_spell_allowed_ingredients()
assert isinstance(allowed, list) and set(allowed) == {
    "bats",
    "frogs",
    "arsenic",
    "eyeball",
}
for ingredients in (
    "BATS",
    "frogs",
    "ArSeNiC",
    "eyeball",
    "earth",
    "",
    "unknown",
):
    valid = any(item in ingredients.lower() for item in allowed)
    result = validate(ingredients)
    assert (
        isinstance(result, str)
        and ingredients.lower() in result.lower()
    )
    assert set(
        re.findall(r"\b(?:VALID|INVALID)\b", result.upper())
    ) == {"VALID" if valid else "INVALID"}
    result = book.dark_spell_record("CodexTest", ingredients)
    assert isinstance(result, str) and "CodexTest" in result
    pattern = (
        r"record\w*|accept\w*|success\w*"
        if valid
        else r"reject\w*|denied|invalid|fail\w*"
    )
    assert re.search(pattern, result, re.I), result
""",
        )
