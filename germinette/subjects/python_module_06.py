from germinette.core import BaseTester
import subprocess
import sys
import ast
import os
from typing import List
from rich.console import Console
from rich.panel import Panel

console = Console()

class Tester(BaseTester):
    def __init__(self):
        self.exercises = [
            ("ft_alembic_0", self.test_alembic_0),
            ("ft_alembic_1", self.test_alembic_1),
            ("ft_alembic_2", self.test_alembic_2),
            ("ft_alembic_3", self.test_alembic_3),
            ("ft_alembic_4", self.test_alembic_4),
            ("ft_alembic_5", self.test_alembic_5),
            ("ft_distillation_0", self.test_distillation_0),
            ("ft_distillation_1", self.test_distillation_1),
            ("ft_transmutation_0", self.test_transmutation_0),
            ("ft_transmutation_1", self.test_transmutation_1),
            ("ft_transmutation_2", self.test_transmutation_2),
            ("ft_kaboom_0", self.test_kaboom_0),
            ("ft_kaboom_1", self.test_kaboom_1),
        ]
        self.grouped_errors = {}

    def record_error(self, exercise_label, error_type, message):
        if exercise_label not in self.grouped_errors:
            self.grouped_errors[exercise_label] = []
        self.grouped_errors[exercise_label].append(f"[bold]{error_type}[/bold]\n{message}")

    def _load_module(self, module_name, exercise_label):
        cwd = os.getcwd()
        base_dir = cwd
        target_file = f"{module_name}.py"
        found_path = os.path.join(base_dir, target_file)
        
        if not os.path.exists(found_path):
             console.print("[red]KO (Missing File)[/red]")
             msg = (f"[bold red]File not found[/bold red]\n\n"
                    f"Expected: [cyan]{target_file}[/cyan]\n"
                    f"Directory: [cyan]{base_dir}[/cyan]\n")
             self.record_error(exercise_label, "Missing File", msg)
             return None, None

        style_errors = self.check_flake8(found_path)
        if style_errors:
             console.print("[red]KO[/red]")
             self.record_error(exercise_label, "Style Error (Flake8)", style_errors)
             return None, None
        
        type_errors = self.check_type_hints(found_path)
        if type_errors:
             console.print("[red]KO[/red]")
             self.record_error(exercise_label, "Style Error (Type Hints)", type_errors)
             return None, None
            
        return "FOUND", found_path 

    def run(self, exercise_name=None):
        console.print("[bold cyan]Testing Module 06: The Codex (v2.0)[/bold cyan]")
        
        if os.getcwd() not in sys.path:
            sys.path.insert(0, os.getcwd())

        exercises_to_run = self.exercises
        if exercise_name:
            exercises_to_run = [ex for ex in self.exercises if ex[0] == exercise_name]
            if not exercises_to_run:
                console.print(f"[red]Unknown exercise: {exercise_name}[/red]")
                self.record_error(
                    "Exercise filter",
                    "Unknown exercise",
                    f"No exercise matches '{exercise_name}'.",
                )

        for _, test_func in exercises_to_run:
            test_func()
            
        if self.grouped_errors:
            console.print()
            console.rule("[bold red]Detailed Error Report[/bold red]")
            console.print()
            for label, messages in self.grouped_errors.items():
                content = "\n\n[dim]────────────────────────────────[/dim]\n\n".join(messages)
                console.print(Panel(content, title=f"[bold red]{label}[/bold red]", border_style="red", expand=False))
                console.print()
        else:
            console.print(Panel("[bold green]All tests passed! Module 06 complete.[/bold green]", border_style="green"))

    def check_strict_forbidden(self, path, exercise_label):
        try:
            with open(path, "r") as f:
                tree = ast.parse(f.read())
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Attribute):
                    if isinstance(node.value, ast.Name) and node.value.id == 'sys' and node.attr == 'path':
                         console.print("[red]KO (Forbidden Path Mod)[/red]")
                         self.record_error(exercise_label, "Forbidden Magic", "Modifying 'sys.path' is forbidden.")
                         return False

                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id in ['exec', 'eval']:
                        console.print("[red]KO (Forbidden Function)[/red]")
                        self.record_error(exercise_label, "Forbidden Magic", f"Using '{node.func.id}' is forbidden.")
                        return False
            
            return True
        except Exception as e:
            console.print(f"[red]KO (AST Error: {e})[/red]")
            return False

    def check_import_type(self, path, exercise_label, require_from=False, forbidden_module=None):
        try:
            with open(path, "r") as f:
                tree = ast.parse(f.read())
            
            has_import = False
            has_import_from = False

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    has_import = True
                    # Check if they imported something forbidden
                    if forbidden_module:
                        for alias in node.names:
                            if forbidden_module in alias.name:
                                console.print(f"[red]KO (Forbidden Module Import: {alias.name})[/red]")
                                return False

                elif isinstance(node, ast.ImportFrom):
                    has_import_from = True
                    if forbidden_module and node.module and forbidden_module in node.module:
                        console.print(f"[red]KO (Forbidden Module ImportFrom: {node.module})[/red]")
                        return False

            if require_from and not has_import_from:
                console.print("[red]KO (Must use 'from ... import ...')[/red]")
                self.record_error(exercise_label, "Import Style", "Must use 'from ... import ...' structure.")
                return False
            elif not require_from and has_import_from:
                # If we specifically said "use 'import ...' structure", don't allow 'from'
                pass # But maybe we will just verify the correct positive structure
                
            return True
        except Exception as e:
            console.print(f"[red]KO (AST Error: {e})[/red]")
            return False

    # --- Part I: The Alembic ---

    def test_alembic_0(self):
        console.print("\n[bold]Testing Alembic 0[/bold]")
        exercise_label = "Alembic 0"
        status, path = self._load_module("ft_alembic_0", exercise_label)
        if not status: return
        if not self.check_strict_forbidden(path, exercise_label): return

        # Must use "import ..." structure to access elements.py directly
        # Should not use `from`
        try:
             with open(path, "r") as f: tree = ast.parse(f.read())
             has_import_from = any(isinstance(n, ast.ImportFrom) for n in ast.walk(tree))
             if has_import_from:
                 console.print("[red]KO (import type)[/red]")
                 self.record_error(exercise_label, "Import Style", "Must use 'import ...' structure. Found 'from' import.")
                 return
        except: pass

        out = self._run_script(path)
        if self.check_for_crash(out, exercise_label): return

        if "=== Alembic 0 ===" in out and "Fire element created" in out:
            console.print("[green]OK[/green]")
        else:
             console.print("[red]KO (Output)[/red]")
             self.record_error(exercise_label, "Output", f"Output mismatch:\n{out}")

    def test_alembic_1(self):
        console.print("\n[bold]Testing Alembic 1[/bold]")
        exercise_label = "Alembic 1"
        status, path = self._load_module("ft_alembic_1", exercise_label)
        if not status: return
        if not self.check_strict_forbidden(path, exercise_label): return

        # Must use "from ... import ..."
        if not self.check_import_type(path, exercise_label, require_from=True): return

        out = self._run_script(path)
        if self.check_for_crash(out, exercise_label): return

        if "=== Alembic 1 ===" in out and "Water element created" in out:
            console.print("[green]OK[/green]")
        else:
             console.print("[red]KO (Output)[/red]")

    def test_alembic_2(self):
        console.print("\n[bold]Testing Alembic 2[/bold]")
        exercise_label = "Alembic 2"
        status, path = self._load_module("ft_alembic_2", exercise_label)
        if not status: return
        if not self.check_strict_forbidden(path, exercise_label): return

        try:
             with open(path, "r") as f: tree = ast.parse(f.read())
             has_import_from = any(isinstance(n, ast.ImportFrom) for n in ast.walk(tree))
             if has_import_from:
                 console.print("[red]KO (import type)[/red]")
                 return
        except: pass

        out = self._run_script(path)
        if self.check_for_crash(out, exercise_label): return

        if "=== Alembic 2 ===" in out and "Earth element created" in out:
            console.print("[green]OK[/green]")
        else:
             console.print("[red]KO (Output)[/red]")

    def test_alembic_3(self):
        console.print("\n[bold]Testing Alembic 3[/bold]")
        exercise_label = "Alembic 3"
        status, path = self._load_module("ft_alembic_3", exercise_label)
        if not status: return
        if not self.check_strict_forbidden(path, exercise_label): return
        if not self.check_import_type(path, exercise_label, require_from=True): return

        out = self._run_script(path)
        if self.check_for_crash(out, exercise_label): return

        if "=== Alembic 3 ===" in out and "Air element created" in out:
            console.print("[green]OK[/green]")
        else:
             console.print("[red]KO (Output)[/red]")

    def test_alembic_4(self):
        console.print("\n[bold]Testing Alembic 4[/bold]")
        exercise_label = "Alembic 4"
        status, path = self._load_module("ft_alembic_4", exercise_label)
        if not status: return
        if not self.check_strict_forbidden(path, exercise_label): return

        try:
             with open(path, "r") as f: tree = ast.parse(f.read())
             has_import_from = any(isinstance(n, ast.ImportFrom) for n in ast.walk(tree))
             if has_import_from:
                 console.print("[red]KO (import type)[/red]")
                 return
        except: pass

        out = self._run_script(path)
        # Should crash intentionally, but check what it outputs first
        if "=== Alembic 4 ===" in out and "Air element created" in out and "AttributeError" in out and "create_earth" in out:
            console.print("[green]OK[/green]")
        else:
             console.print("[red]KO (Output)[/red]")

    def test_alembic_5(self):
        console.print("\n[bold]Testing Alembic 5[/bold]")
        exercise_label = "Alembic 5"
        status, path = self._load_module("ft_alembic_5", exercise_label)
        if not status: return
        if not self.check_strict_forbidden(path, exercise_label): return
        if not self.check_import_type(path, exercise_label, require_from=True): return

        out = self._run_script(path)
        if self.check_for_crash(out, exercise_label): return

        if "=== Alembic 5 ===" in out and "Air element created" in out:
            console.print("[green]OK[/green]")
        else:
             console.print("[red]KO (Output)[/red]")

    # --- Part II: Distillation ---

    def test_distillation_0(self):
        console.print("\n[bold]Testing Distillation 0[/bold]")
        exercise_label = "Distillation 0"
        status, path = self._load_module("ft_distillation_0", exercise_label)
        if not status: return
        if not self.check_import_type(path, exercise_label, require_from=True): return

        out = self._run_script(path)
        if self.check_for_crash(out, exercise_label): return

        if "Strength potion brewed" in out and "Healing potion brewed" in out:
             console.print("[green]OK[/green]")
        else:
             console.print("[red]KO[/red]")

    def test_distillation_1(self):
        console.print("\n[bold]Testing Distillation 1[/bold]")
        exercise_label = "Distillation 1"
        status, path = self._load_module("ft_distillation_1", exercise_label)
        if not status: return
        
        try:
             with open(path, "r") as f: tree = ast.parse(f.read())
             has_import_from = any(isinstance(n, ast.ImportFrom) for n in ast.walk(tree))
             if has_import_from:
                 console.print("[red]KO (import type)[/red]")
                 return
        except: pass

        out = self._run_script(path)
        if self.check_for_crash(out, exercise_label): return

        if "Strength potion brewed" in out and "alias" in out.lower() and "Healing potion" in out:
             console.print("[green]OK[/green]")
        else:
             console.print("[red]KO[/red]")

    # --- Part III: Transmutation ---

    def test_transmutation_0(self):
        console.print("\n[bold]Testing Transmutation 0[/bold]")
        exercise_label = "Transmutation 0"
        status, path = self._load_module("ft_transmutation_0", exercise_label)
        if not status: return
        
        out = self._run_script(path)
        if self.check_for_crash(out, exercise_label): return
        
        if "Recipe transmuting Lead to Gold" in out: console.print("[green]OK[/green]")
        else: console.print("[red]KO[/red]")

    def test_transmutation_1(self):
        console.print("\n[bold]Testing Transmutation 1[/bold]")
        exercise_label = "Transmutation 1"
        status, path = self._load_module("ft_transmutation_1", exercise_label)
        if not status: return
        
        out = self._run_script(path)
        if self.check_for_crash(out, exercise_label): return
        if "Recipe transmuting Lead to Gold" in out: console.print("[green]OK[/green]")
        else: console.print("[red]KO[/red]")

    def test_transmutation_2(self):
        console.print("\n[bold]Testing Transmutation 2[/bold]")
        exercise_label = "Transmutation 2"
        status, path = self._load_module("ft_transmutation_2", exercise_label)
        if not status: return
        
        out = self._run_script(path)
        if self.check_for_crash(out, exercise_label): return
        if "Recipe transmuting Lead to Gold" in out: console.print("[green]OK[/green]")
        else: console.print("[red]KO[/red]")

    # --- Part IV: Kaboom ---

    def test_kaboom_0(self):
        console.print("\n[bold]Testing Kaboom 0[/bold]")
        exercise_label = "Kaboom 0"
        status, path = self._load_module("ft_kaboom_0", exercise_label)
        if not status: return
        
        out = self._run_script(path)
        if self.check_for_crash(out, exercise_label): return
        if "Spell recorded:" in out and "VALID" in out: console.print("[green]OK[/green]")
        else: console.print("[red]KO[/red]")

    def test_kaboom_1(self):
        console.print("\n[bold]Testing Kaboom 1[/bold]")
        exercise_label = "Kaboom 1"
        status, path = self._load_module("ft_kaboom_1", exercise_label)
        if not status: return
        
        out = self._run_script(path)
        if "ImportError" in out and "circular import" in out:
             console.print("[green]OK (Circular import caught)[/green]")
        else:
             console.print("[red]KO (No circular import crash)[/red]")
