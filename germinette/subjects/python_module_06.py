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
            ("ft_sacred_scroll", self.test_sacred_scroll),
            ("ft_import_transmutation", self.test_import_transmutation),
            ("ft_pathway_debate", self.test_pathway_debate),
            ("ft_circular_curse", self.test_circular_curse),
        ]
        self.grouped_errors = {}

    def record_error(self, exercise_label, error_type, message):
        if exercise_label not in self.grouped_errors:
            self.grouped_errors[exercise_label] = []
        self.grouped_errors[exercise_label].append(f"[bold]{error_type}[/bold]\n{message}")

    def _load_module(self, module_name, exercise_label):
        cwd = os.getcwd()
        # For Mod 06, files are at root of repo (or test dir)
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

        # Style Checks
        style_errors = self.check_flake8(found_path)
        if style_errors:
             console.print("[red]KO[/red]")
             self.record_error(exercise_label, "Style Error (Flake8)", style_errors)
             return None, None
        
        doc_errors = self.check_docstrings(found_path)
        if doc_errors:
             console.print("[red]KO[/red]")
             self.record_error(exercise_label, "Style Error (Missing Docstrings)", doc_errors)
             return None, None

        # Type Hint Checks
        type_errors = self.check_type_hints(found_path)
        if type_errors:
             console.print("[red]KO[/red]")
             self.record_error(exercise_label, "Style Error (Type Hints)", type_errors)
             return None, None
            
        return "FOUND", found_path 

    def run(self, exercise_name=None):
        console.print("[bold cyan]Testing Module 06: The Codex (Import Mysteries)[/bold cyan]")
        
        if os.getcwd() not in sys.path:
            sys.path.insert(0, os.getcwd())

        exercises_to_run = self.exercises
        if exercise_name:
            exercises_to_run = [ex for ex in self.exercises if ex[0] == exercise_name]
            
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
        """Checks for forbidden libraries and modifications."""
        try:
            with open(path, "r") as f:
                tree = ast.parse(f.read())
            
            for node in ast.walk(tree):
                # Check sys.path modification (ONLY sys.path check kept, Imports handled by verify_strict)
                if isinstance(node, ast.Attribute):
                    if isinstance(node.value, ast.Name) and node.value.id == 'sys' and node.attr == 'path':
                         # If it's being assigned to or appended
                         console.print("[red]KO (Forbidden Path Mod)[/red]")
                         self.record_error(exercise_label, "Forbidden Magic", "Modifying 'sys.path' is forbidden.")
                         return False

                # Check exec/eval
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id in ['exec', 'eval']:
                        console.print("[red]KO (Forbidden Function)[/red]")
                        self.record_error(exercise_label, "Forbidden Magic", f"Using '{node.func.id}' is forbidden.")
                        return False
            
            return True
        except Exception as e:
            console.print(f"[red]KO (AST Error: {e})[/red]")
            return False

    def test_sacred_scroll(self):
        console.print("\n[bold]Testing Exercise 0: ft_sacred_scroll[/bold]")
        exercise_label = "Exercise 0"
        status, path = self._load_module("ft_sacred_scroll", exercise_label)
        if not status: return

        if not self.check_strict_forbidden(path, exercise_label):
            return

        # Use verify_strict for Imports and Functions
        # Allowed Imports: sys, alchemy (our package)
        # Allowed Funcs: print, len, dir, getattr, setattr (introspection tools)
        if not self.verify_strict(path, exercise_label, 
                                  ["print", "len", "dir", "getattr", "setattr", "zip", "all", "any"], 
                                  allowed_imports=["sys", "alchemy"], 
                                  enforce_try_except=False): return # Try/except enforced locally for specific logic or check below? 
                                  # Original test had separate try/except check but failed if missing.
                                  # Let's enforcing try/except via verify_strict too?
                                  # "use try/except blocks and return descriptive errors" -> Yes.


        # Explicit check for try/except required in PDF introduction: 
        # "use try/except blocks and return descriptive error messages instead of letting the program crash."
        # Not forcing it via AST for every file, but script should handle errors.
        
        try:
            cmd = [sys.executable, path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            out = result.stdout + result.stderr

            if "=== Sacred Scroll Mastery ===" not in out:
                console.print("[red]KO (Missing Header)[/red]")
                self.record_error(exercise_label, "Output Error", "Missing header '=== Sacred Scroll Mastery ==='")
                return

            required = [
                "alchemy.elements.create_fire(): Fire element created",
                "alchemy.create_fire(): Fire element created",
                "alchemy.create_earth():", # Handled message could be anything
                "Package metadata:",
                "Version: 1.0.0"
            ]
            
            # Check for hidden elements not exposed
            if "alchemy.create_earth(): Earth element created" in out:
                 console.print("[red]KO (Exposure Error)[/red]")
                 self.record_error(exercise_label, "Exposure Error", "create_earth should NOT be exposed by package.")
                 return

            missing = [r for r in required if r not in out]
            
            # Strict check for specific strings
            if "AttributeError" not in out and "not exposed" not in out:
                 console.print("[red]KO (Missing Error Handling)[/red]")
                 self.record_error(exercise_label, "Output Error", "Must handle hidden attributes gracefully (AttributeError).")
                 return

            if not missing:
                console.print("[green]OK[/green]")
            else:
                 console.print("[red]KO (Output Mismatch)[/red]")
                 self.record_error(exercise_label, "Output Error", f"Missing output strings: {missing}\nGot:\n{out}")

        except Exception as e:
             console.print(f"[red]KO (Execution Error: {e})[/red]")

    def test_import_transmutation(self):
        console.print("\n[bold]Testing Exercise 1: ft_import_transmutation[/bold]")
        exercise_label = "Exercise 1"
        status, path = self._load_module("ft_import_transmutation", exercise_label)
        if not status: return

        if not self.check_strict_forbidden(path, exercise_label):
            return

        # Ex1
        if not self.verify_strict(path, exercise_label, 
                                  ["print", "len", "dir", "getattr", "setattr"], 
                                  allowed_imports=["sys", "alchemy"], 
                                  enforce_try_except=False): return

        try:
            cmd = [sys.executable, path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            out = result.stdout + result.stderr

            if "=== Import Transmutation Mastery ===" not in out:
                console.print("[red]KO (Missing Header)[/red]")
                self.record_error(exercise_label, "Output Error", "Missing header '=== Import Transmutation Mastery ==='")
                return
            
            required = [
                "Method 1 - Full module import",
                "alchemy.elements.create_fire(): Fire element created",
                "Method 2 - Specific function import",
                "create_water(): Water element created",
                "Method 3 - Aliased import",
                "heal(): Healing potion brewed",
                "Method 4 - Multiple imports",
                "create_earth(): Earth element created",
                "All import transmutation methods mastered!"
            ]
            
            missing = [r for r in required if r not in out]
            if not missing:
                console.print("[green]OK[/green]")
            else:
                 console.print("[red]KO (Output Mismatch)[/red]")
                 self.record_error(exercise_label, "Output Error", f"Missing output strings: {missing}\nGot:\n{out}")

        except Exception as e:
             console.print(f"[red]KO (Execution Error: {e})[/red]")

    def test_pathway_debate(self):
        console.print("\n[bold]Testing Exercise 2: ft_pathway_debate[/bold]")
        exercise_label = "Exercise 2"
        status, path = self._load_module("ft_pathway_debate", exercise_label)
        if not status: return
        
        if not self.check_strict_forbidden(path, exercise_label):
            return
        
        # Ex2
        if not self.verify_strict(path, exercise_label, 
                                  ["print", "len", "dir", "getattr", "setattr"], 
                                  allowed_imports=["sys", "alchemy", "basic", "advanced"], # Relative imports might mean local modules.
                                  # Wait, Ex2 does separate modules? basic.py?
                                  # If user imports "basic", it must be allowed.
                                  enforce_try_except=False): return

        try:
            cmd = [sys.executable, path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            out = result.stdout + result.stderr
            
            if "=== Pathway Debate Mastery ===" not in out:
                console.print("[red]KO (Missing Header)[/red]")
                self.record_error(exercise_label, "Output Error", "Missing header '=== Pathway Debate Mastery ==='")
                return

            required = [
                "Testing Absolute Imports (from basic.py)",
                "lead_to_gold(): Lead transmuted to gold",
                "stone_to_gem(): Stone transmuted to gem",
                "Testing Relative Imports (from advanced.py)",
                "philosophers_stone(): Philosopher's stone created",
                "Testing Package Access",
                "Both pathways work!"
            ]
            
            missing = [r for r in required if r not in out]
            if not missing:
                console.print("[green]OK[/green]")
            else:
                 console.print("[red]KO (Output Mismatch)[/red]")
                 self.record_error(exercise_label, "Output Error", f"Missing output strings: {missing}\nGot:\n{out}")
        except Exception as e:
             console.print(f"[red]KO (Execution Error: {e})[/red]")

    def test_circular_curse(self):
        console.print("\n[bold]Testing Exercise 3: ft_circular_curse[/bold]")
        exercise_label = "Exercise 3"
        status, path = self._load_module("ft_circular_curse", exercise_label)
        if not status: return
        
        if not self.check_strict_forbidden(path, exercise_label):
            return
        
        # Ex3
        if not self.verify_strict(path, exercise_label, 
                                  ["print", "len", "dir", "getattr", "setattr"], 
                                  allowed_imports=["sys", "alchemy"], 
                                  enforce_try_except=False): return

        try:
            cmd = [sys.executable, path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            out = result.stdout + result.stderr
            
            if "=== Circular Curse Breaking ===" not in out:
                console.print("[red]KO (Missing Header)[/red]")
                self.record_error(exercise_label, "Output Error", "Missing header '=== Circular Curse Breaking ==='")
                return

            required = [
                "Testing ingredient validation:",
                "VALID",
                "INVALID",
                "Testing spell recording",
                "Spell recorded:",
                "Spell rejected:",
                "Circular dependency curse avoided"
            ]
            
            missing = [r for r in required if r not in out]
            if not missing:
                console.print("[green]OK[/green]")
            else:
                 console.print("[red]KO (Output Mismatch)[/red]")
                 self.record_error(exercise_label, "Output Error", f"Missing output strings: {missing}\nGot:\n{out}")
        except Exception as e:
             console.print(f"[red]KO (Execution Error: {e})[/red]")
