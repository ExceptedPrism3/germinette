"""Shared checks and structured results for the version 1.0 bis subjects."""

import ast
import importlib.util
import subprocess
import sys
from pathlib import Path

from rich.markup import escape
from rich.panel import Panel
from germinette.core import BaseTester, console


def qualified_name(node, aliases):
    if isinstance(node, ast.Name):
        return aliases.get(node.id, node.id)
    if isinstance(node, ast.Attribute):
        return qualified_name(node.value, aliases) + "." + node.attr
    return ""


def import_aliases(tree):
    # shortcut: static aliases only, use isolation for untrusted student code.
    aliases = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for item in node.names:
                aliases[item.asname or item.name.split(".")[0]] = (
                    item.name if item.asname else item.name.split(".")[0]
                )
        elif isinstance(node, ast.ImportFrom):
            for item in node.names:
                aliases[item.asname or item.name] = (
                    node.module + "." if node.module else ""
                ) + item.name
    # Resolve ordinary assignments such as run = builtins.eval or p = sys.path.
    for _ in range(2):
        for node in ast.walk(tree):
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                value = qualified_name(node.value, aliases)
                targets = (
                    node.targets
                    if isinstance(node, ast.Assign)
                    else [node.target]
                )
                if value:
                    for target in targets:
                        if isinstance(target, ast.Name):
                            aliases[target.id] = value
    return aliases


class BisTester(BaseTester):
    def __init__(self):
        super().__init__()
        self.checks = []

    def run(self, exercise_name=None):
        if exercise_name and exercise_name.replace(".py", "") not in {
            name for name, _ in self.exercises
        }:
            self.record(
                "Exercise filter",
                "failed",
                f"Unknown exercise: {exercise_name}",
            )
            self.display_error_report()
            return
        super().run(exercise_name)

    def display_error_report(self):
        if self.grouped_errors:
            console.rule("[bold red]Detailed Error Report[/bold red]")
            for label, messages in self.grouped_errors.items():
                console.print(
                    Panel("\n\n".join(messages), title=escape(label))
                )
        report = self.report()
        console.rule("[bold cyan]Summary[/bold cyan]")
        console.print(
            f"Passed: {report['passed']}  Failed: {report['failed']}  "
            f"Errors: {report['errors']}  Skipped: {report['skipped']}"
        )
        if report["skipped"]:
            console.print("[yellow]Some checks did not run.[/yellow]")

    def record(self, name, status, message=""):
        self.checks.append(
            {"name": name, "status": status, "message": message}
        )
        if status == "passed":
            self.mark_ok()
            console.print(f"[green]OK[/green] {escape(name)}")
        elif status == "skipped":
            console.print(
                f"[yellow]SKIP[/yellow] {escape(name)}: {escape(message)}"
            )
        else:
            self.record_error(
                name,
                "Error" if status == "errors" else "Check failed",
                escape(message),
            )
            console.print(f"[red]KO[/red] {escape(name)}")
        return status == "passed"

    def check(self, name, condition, message):
        return self.record(
            name,
            "passed" if condition else "failed",
            "" if condition else message,
        )

    def files(self, name, paths):
        missing = [str(path) for path in paths if not Path(path).is_file()]
        return self.check(
            name, not missing, "Missing files: " + ", ".join(missing)
        )

    def process(self, name, args, *, cwd=None, env=None):
        try:
            return subprocess.run(
                args,
                cwd=cwd,
                env=env,
                capture_output=True,
                text=True,
                timeout=15,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            self.record(name, "errors", str(exc))
            return None

    def script(self, path, *, env=None):
        result = self.process(str(path), [sys.executable, str(path)], env=env)
        if result is not None:
            self.check(
                str(path),
                result.returncode == 0,
                "Unexpected exit status.\n" + result.stdout + result.stderr,
            )
        return result

    def probe(self, name, source, *, can_skip=False):
        result = self.process(name, [sys.executable, "-E", "-B", "-c", source])
        if result is not None:
            if can_skip and result.returncode == 77:
                return self.record(name, "skipped", result.stdout.strip())
            return self.check(
                name,
                result.returncode == 0,
                result.stdout + result.stderr
                or "Behavior did not match the subject.",
            )
        return False

    def tree(self, path):
        try:
            return ast.parse(Path(path).read_text(encoding="utf-8"))
        except (OSError, UnicodeError, SyntaxError) as exc:
            self.check(f"{path}: syntax", False, str(exc))
            return None

    def lint(self, name, paths):
        if importlib.util.find_spec("flake8") is None:
            self.record(
                name, "skipped", "Install flake8 in the tester environment."
            )
            return
        result = self.process(
            name,
            [sys.executable, "-m", "flake8", "--isolated", *map(str, paths)],
        )
        if result is None:
            return
        if result.returncode > 1:
            self.record(name, "errors", result.stderr or result.stdout)
        else:
            self.check(
                name, result.returncode == 0, result.stdout or result.stderr
            )

    def policy(self, name, paths, *, no_syspath=False, allowed_imports=None):
        violations = []
        for path in paths:
            tree = self.tree(path)
            if tree is None:
                continue
            aliases = import_aliases(tree)

            def local(module, level=0):
                base = Path(path).parent
                if level:
                    for _ in range(level - 1):
                        base = base.parent
                else:
                    base = Path(".")
                target = base.joinpath(*module.split(".")) if module else base
                return (
                    target.with_suffix(".py").is_file()
                    or (target / "__init__.py").is_file()
                )

            for node in ast.walk(tree):
                if allowed_imports is not None:
                    imports = []
                    if isinstance(node, ast.Import):
                        imports = [(a.name, 0) for a in node.names]
                    elif isinstance(node, ast.ImportFrom):
                        imports = [(node.module or "", node.level)]
                    if isinstance(node, ast.Call) and qualified_name(
                        node.func, aliases
                    ) in (
                        "__import__",
                        "builtins.__import__",
                        "importlib.import_module",
                    ):
                        if node.args and isinstance(
                            node.args[0], ast.Constant
                        ):
                            module = node.args[0].value
                            if isinstance(module, str):
                                imports.append((module, 0))
                    for module, level in imports:
                        if not local(module, level) and (
                            level
                            or module.split(".")[0] not in allowed_imports
                        ):
                            violations.append(
                                f"{path}:{node.lineno}: unauthorized import "
                                + "." * level
                                + module
                            )
                if isinstance(node, ast.Call) and qualified_name(
                    node.func, aliases
                ) in {"eval", "exec", "builtins.eval", "builtins.exec"}:
                    violations.append(
                        f"{path}:{node.lineno}: forbidden "
                        f"{qualified_name(node.func, aliases)}()"
                    )
                if no_syspath:
                    target = None
                    if isinstance(
                        node,
                        (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.Delete),
                    ):
                        targets = (
                            node.targets
                            if isinstance(node, ast.Assign)
                            else (
                                node.targets
                                if isinstance(node, ast.Delete)
                                else [node.target]
                            )
                        )
                        target = any(
                            qualified_name(part, aliases) == "sys.path"
                            for item in targets
                            if not isinstance(item, ast.Name)
                            for part in ast.walk(item)
                        )
                    if isinstance(node, ast.Call) and isinstance(
                        node.func, ast.Attribute
                    ):
                        obj = node.func.value
                        target = target or (
                            node.func.attr in {
                                "append",
                                "insert",
                                "extend",
                                "remove",
                                "pop",
                                "clear",
                                "reverse",
                                "sort",
                            }
                            and qualified_name(obj, aliases) == "sys.path"
                        )
                    if target:
                        violations.append(
                            f"{path}:{node.lineno}: modifies sys.path"
                        )
        self.check(name, not violations, "\n".join(violations))

    def report(self):
        counts = {
            status: sum(item["status"] == status for item in self.checks)
            for status in ("passed", "failed", "errors", "skipped")
        }
        return {
            "version": 1,
            "total": len(self.checks),
            **counts,
            "checks": self.checks,
        }
