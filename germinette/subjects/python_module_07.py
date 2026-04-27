"""
Module 07 (DataDeck) tester - v3.0

Tests Abstract Factories, Capabilities (Mixins), and Abstract Strategies.
"""
import sys
import os
import ast
import traceback
import subprocess
import builtins
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from germinette.core import BaseTester

console = Console()

class Tester(BaseTester):
    def __init__(self):
        self.exercises = [
            ("ex00", self.test_creature_factory),
            ("ex0", self.test_creature_factory),
            ("ex01", self.test_capabilities),
            ("ex1", self.test_capabilities),
            ("ex02", self.test_abstract_strategy),
            ("ex2", self.test_abstract_strategy),
        ]
        self.grouped_errors = {}

    def record_error(self, exercise_label, error_type, message):
        if exercise_label not in self.grouped_errors:
            self.grouped_errors[exercise_label] = []
        self.grouped_errors[exercise_label].append(f"[bold]{error_type}[/bold]\n{message}")

    def _find_root_dir(self):
        cwd = os.getcwd()
        if os.path.basename(cwd) == "python_module_07":
            return cwd
        base_search = [
            os.path.join(cwd, "python_module_07"),
            os.path.join(cwd, "devtools", "test", "python_module_07"),
            cwd
        ]
        for base in base_search:
            if os.path.exists(os.path.join(base, "ex0")):
                return base
        return cwd

    def common_strict_check(self, path, label, extra_imports=None):
        # Subject v3.0: all builtins authorized except eval/exec.
        allowed_funcs = [
            n for n in dir(builtins)
            if not n.startswith("_") and n not in {"eval", "exec"}
        ]

        allowed_imports = ["typing", "abc"]
        if extra_imports:
             allowed_imports.extend(extra_imports)

        style_errors = self.check_flake8(path)
        if style_errors:
             console.print("[red]KO[/red]")
             self.record_error(label, "Style Error (Flake8)", style_errors)
             return False

        type_errors = self.check_type_hints(path)
        if type_errors:
             console.print("[red]KO (Type Hints)[/red]")
             self.record_error(label, "Style Error (Missing Type Hints)", type_errors)
             return False

        if not self.verify_strict(
            path, label, allowed_funcs, allowed_imports, enforce_try_except=False
        ):
            return False
        return self._check_no_external_imports(path, label)

    def _allowed_import_roots(self, root_dir):
        roots = {"abc", "typing", "__future__"}
        cwd = Path(root_dir)
        for py in cwd.rglob("*.py"):
            rel = py.relative_to(cwd)
            if rel.name == "__init__.py":
                parts = rel.parts[:-1]
            else:
                parts = rel.parts
            if not parts:
                continue
            if len(parts) == 1:
                roots.add(parts[0].replace(".py", ""))
            else:
                roots.add(parts[0])
        return roots

    def _check_no_external_imports(self, path, label):
        try:
            root_dir = self._find_root_dir()
            allowed_roots = self._allowed_import_roots(root_dir)
            with open(path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
            bad = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        root = alias.name.split(".")[0]
                        if root not in allowed_roots:
                            bad.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.level > 0:
                        continue
                    if node.module:
                        root = node.module.split(".")[0]
                        if root not in allowed_roots:
                            bad.append(node.module)
            if bad:
                self.record_error(
                    label,
                    "Forbidden Import",
                    "External libraries are forbidden in Module 07.\n"
                    f"Forbidden imports: {sorted(set(bad))}",
                )
                return False
            return True
        except Exception as e:
            self.record_error(label, "AST Error", f"Import scan failed: {e}")
            return False

    def _check_mandatory_package_inits(self, root_dir):
        missing = []
        for ex_name in ("ex0", "ex1", "ex2"):
            init_path = os.path.join(root_dir, ex_name, "__init__.py")
            if not os.path.exists(init_path):
                missing.append(f"{ex_name}/__init__.py")
        if missing:
            self.record_error(
                "Project Structure",
                "Missing Package Files",
                "__init__.py is mandatory for each exercise folder.\nMissing:\n- "
                + "\n- ".join(missing),
            )
            return False
        return True

    def _check_ex_directory(self, root_dir, ex_name, label):
        ex_dir = os.path.join(root_dir, ex_name)
        if not os.path.exists(ex_dir):
            self.record_error(label, "Missing Directory", f"Missing required directory: {ex_name}/")
            return False
        for fname in os.listdir(ex_dir):
            if fname.endswith(".py"):
                path = os.path.join(ex_dir, fname)
                if not self.common_strict_check(path, label, extra_imports=["ex0", "ex1", "ex2"]):
                    return False
        return True

    def test_creature_factory(self):
        console.print("\n[bold]Testing Exercise 0: Creature Factory[/bold]")
        exercise_label = "Exercise 0"
        root_dir = self._find_root_dir()
        script_path = os.path.join(root_dir, "battle.py")
        
        if not os.path.exists(script_path):
             console.print("[red]KO (Missing File)[/red]")
             self.record_error(exercise_label, "Missing File", "Could not find battle.py at root.")
             return
            
        if not self.common_strict_check(script_path, exercise_label, extra_imports=["ex0", "ex1", "ex2"]): return
        if not self._check_ex_directory(root_dir, "ex0", exercise_label): return

        try:
            cmd = [sys.executable, "battle.py"]
            result = subprocess.run(cmd, cwd=root_dir, capture_output=True, text=True)
            out = result.stdout + result.stderr
            if self.check_for_crash(out, exercise_label): return

            required = [
                "Flameling", "Pyrodon", "Aquabub", "Torragon",
                "Fire type", "Water type",
                "factory", "battle"
            ]

            missing = [r for r in required if r.lower() not in out.lower()]
            if not missing:
                console.print("[green]OK[/green]")
            else:
                 console.print("[red]KO (Output Mismatch)[/red]")
                 self.record_error(exercise_label, "Output Error", f"Missing keywords showing Abstract Factory usage: {missing}\nGot:\n{out}")

        except Exception as e:
             console.print(f"[red]KO (Execution Error: {e})[/red]")
             self.record_error(exercise_label, "Runtime Error", traceback.format_exc())

    def test_capabilities(self):
        console.print("\n[bold]Testing Exercise 1: Capabilities[/bold]")
        exercise_label = "Exercise 1"
        root_dir = self._find_root_dir()
        script_path = os.path.join(root_dir, "capacitor.py")
        
        if not os.path.exists(script_path):
             console.print("[red]KO (Missing File)[/red]")
             return
            
        if not self.common_strict_check(script_path, exercise_label, extra_imports=["ex0", "ex1", "ex2"]): return
        if not self._check_ex_directory(root_dir, "ex1", exercise_label): return

        try:
            cmd = [sys.executable, "capacitor.py"]
            result = subprocess.run(cmd, cwd=root_dir, capture_output=True, text=True)
            out = result.stdout + result.stderr
            if self.check_for_crash(out, exercise_label): return

            required = [
                "Sproutling", "Grass type",
                "Bloomelle", "heal",
                "Shiftling", "Normal type",
                "Morphagon", "transform",
                "revert"
            ]

            missing = [r for r in required if r.lower() not in out.lower()]
            if not missing:
                console.print("[green]OK[/green]")
            else:
                 console.print("[red]KO (Output Mismatch)[/red]")
                 self.record_error(exercise_label, "Output Error", f"Missing capabilities output: {missing}\nGot:\n{out}")

        except Exception as e:
             console.print(f"[red]KO (Execution Error: {e})[/red]")
             self.record_error(exercise_label, "Runtime Error", traceback.format_exc())

    def test_abstract_strategy(self):
        console.print("\n[bold]Testing Exercise 2: Abstract Strategy[/bold]")
        exercise_label = "Exercise 2"
        root_dir = self._find_root_dir()
        script_path = os.path.join(root_dir, "tournament.py")
        
        if not os.path.exists(script_path):
             console.print("[red]KO (Missing File)[/red]")
             return
            
        if not self.common_strict_check(script_path, exercise_label, extra_imports=["ex0", "ex1", "ex2"]): return
        if not self._check_ex_directory(root_dir, "ex2", exercise_label): return

        try:
            cmd = [sys.executable, "tournament.py"]
            result = subprocess.run(cmd, cwd=root_dir, capture_output=True, text=True)
            out = result.stdout + result.stderr
            if self.check_for_crash(out, exercise_label): return

            required = [
                "tournament", "battle", "vs"
            ]

            missing = [r for r in required if r.lower() not in out.lower()]
            
            # Check for error handling of invalid strategy
            # The PDF mentions "If the act method is called with an invalid combination, a dedicated exception is raised"
            # And example output shows "Battle error, aborting tournament: Invalid Creature ... for this aggressive strategy"
            error_caught = "invalid" in out.lower() or "error" in out.lower() or "abort" in out.lower()
            
            if not missing and error_caught:
                console.print("[green]OK[/green]")
            else:
                 console.print("[red]KO (Output Mismatch)[/red]")
                 msg = f"Missing tournament terminology: {missing}" if missing else "Did not detect handling of invalid Creature-strategy tuples."
                 self.record_error(exercise_label, "Output Error", f"{msg}\nGot:\n{out}")

        except Exception as e:
             console.print(f"[red]KO (Execution Error: {e})[/red]")
             self.record_error(exercise_label, "Runtime Error", traceback.format_exc())

    def run(self, exercise_name=None):
        console.print("[bold cyan]Testing Module 07: DataDeck (Abstract Patterns)[/bold cyan]")
        
        if os.getcwd() not in sys.path:
            sys.path.insert(0, os.getcwd())

        root_dir = self._find_root_dir()
        # The PDF instructions for Mod07 v3.0 say testing code is at root.
        root_init = os.path.join(root_dir, "__init__.py")
        if not os.path.exists(root_init):
             console.print("[yellow]Warning: Missing __init__.py at repository root. This may cause import issues.[/yellow]")
        self._check_mandatory_package_inits(root_dir)

        if exercise_name:
            found = False
            for name, func in self.exercises:
                if name == exercise_name:
                    func()
                    found = True
                    break
            if not found:
                console.print(f"[red]Unknown exercise: {exercise_name}[/red]")
                self.record_error(
                    "Exercise filter",
                    "Unknown exercise",
                    f"No exercise matches '{exercise_name}'.",
                )
        else:
            visited = set()
            for name, func in self.exercises:
                if func not in visited:
                    func()
                    visited.add(func)
            
        if self.grouped_errors:
            console.print()
            console.rule("[bold red]Detailed Error Report[/bold red]")
            console.print()
            for label, messages in self.grouped_errors.items():
                content = "\n\n[dim]────────────────────────────────[/dim]\n\n".join(messages)
                console.print(Panel(content, title=f"[bold red]{label}[/bold red]", border_style="red", expand=False))
                console.print()
