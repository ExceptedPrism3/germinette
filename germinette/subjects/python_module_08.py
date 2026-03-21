import sys
import os
import subprocess
from rich.console import Console
from rich.panel import Panel
from germinette.core import BaseTester

console = Console()

class Tester(BaseTester):
    def __init__(self):
        self.exercises = [
            ("ex00", self.test_the_matrix),
            ("ex0", self.test_the_matrix), # Alias
            ("ex01", self.test_loading_programs),
            ("ex1", self.test_loading_programs), # Alias
            ("ex02", self.test_accessing_mainframe),
            ("ex2", self.test_accessing_mainframe), # Alias
        ]
        self.grouped_errors = {}

    def record_error(self, exercise_label, error_type, message):
        if exercise_label not in self.grouped_errors:
            self.grouped_errors[exercise_label] = []
        self.grouped_errors[exercise_label].append(f"[bold]{error_type}[/bold]\n{message}")

    def _load_module_path(self, ex_dir_name, main_file):
        cwd = os.getcwd()
        # Direct check
        if os.path.exists(ex_dir_name):
            possible = os.path.join(cwd, ex_dir_name, main_file)
            if os.path.exists(possible):
                return possible
        
        # Inside python_module_08
        if os.path.exists("python_module_08"):
             sub_path = os.path.join("python_module_08", ex_dir_name, main_file)
             if os.path.exists(sub_path):
                 return os.path.abspath(sub_path)

        # Fallback if cwd is python_module_08
        if os.path.basename(cwd) == "python_module_08":
             if os.path.exists(ex_dir_name):
                 return os.path.join(cwd, ex_dir_name, main_file)
        
        return None

    def common_strict_check(self, path, label, extra_funcs=None, extra_imports=None):
        allowed_funcs = [
            "print", "len", "sum", "max", "min", "range", "zip", "enumerate", 
            "int", "float", "str", "bool", "list", "dict", "set", "tuple",
            "isinstance", "issubclass", "super", "next", "iter", "all", "any", "id",
            "open", "exit" # Often needed for scripts
        ]
        if extra_funcs:
            allowed_funcs.extend(extra_funcs)

        allowed_imports = ["sys", "os", "typing", "abc", "random", "datetime", "site"]
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

        return self.verify_strict(path, label, allowed_funcs, allowed_imports, enforce_try_except=False)

    def test_the_matrix(self):
        console.print("\n[bold]Testing Exercise 0: The Matrix[/bold]")
        exercise_label = "Exercise 0"
        path = self._load_module_path("ex00", "construct.py")
        if not path:
            path = self._load_module_path("ex0", "construct.py")
        
        if not path or not os.path.exists(path):
            console.print("[red]KO (Missing File)[/red]")
            self.record_error(exercise_label, "Missing File", "Could not find ex00/construct.py")
            return

        if not self.common_strict_check(path, exercise_label): return

        # Test 1: Run standard (Outside Matrix)
        try:
            cmd = [sys.executable, path]
            cwd = os.path.dirname(path)
            result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
            out = result.stdout + result.stderr
            if self.check_for_crash(out, exercise_label): return

            if "Virtual Environment: None detected" in out or "Outside the Matrix" in out:
                console.print("[green]OK (Outside Detection)[/green]")
            else:
                 console.print("[red]KO (Detection Fail)[/red]")
                 self.record_error(exercise_label, "Run Error", f"Failed to detect 'No Virtual Env'. Got:\n{out}")
        except Exception as e:
             console.print(f"[red]KO (Execution Error: {e})[/red]")

    def test_loading_programs(self):
        console.print("\n[bold]Testing Exercise 1: Loading Programs[/bold]")
        exercise_label = "Exercise 1"
        
        # Check files
        path = self._load_module_path("ex01", "loading.py")
        if not path: path = self._load_module_path("ex1", "loading.py")
        
        if not path or not os.path.exists(path):
            console.print("[red]KO (Missing File)[/red]")
            self.record_error(exercise_label, "Missing File", "Could not find loading.py")
            return

        requirements = os.path.join(os.path.dirname(path), "requirements.txt")
        pyproject = os.path.join(os.path.dirname(path), "pyproject.toml")
        
        if not os.path.exists(requirements):
            self.record_error(exercise_label, "Missing File", "Missing requirements.txt")
        if not os.path.exists(pyproject):
            self.record_error(exercise_label, "Missing File", "Missing pyproject.toml")
        if not os.path.exists(requirements) or not os.path.exists(pyproject):
            return

        # Strict Check
        allowed_imports = ["pandas", "requests", "matplotlib", "numpy", "importlib", "time"]
        allowed_funcs = ["getattr"]
        if not self.common_strict_check(path, exercise_label, extra_funcs=allowed_funcs, extra_imports=allowed_imports): return

        # Run
        try:
            cmd = [sys.executable, path]
            cwd = os.path.dirname(path)
            result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
            out = result.stdout + result.stderr
            if self.check_for_crash(out, exercise_label): return
            
            # We look for some indication of status check, even if failing due to missing deps
            if "LOADING STATUS" not in out and "Checking dependencies" not in out:
                console.print("[red]KO (Output Mismatch)[/red]")
                self.record_error(
                    exercise_label,
                    "Output Error",
                    f"Output doesn't match expected structure. Got:\n{out}",
                )
                return

            # Subject: matplotlib visualization written to matrix_analysis.png
            if "Results saved to: matrix_analysis.png" in out:
                png_path = os.path.join(cwd, "matrix_analysis.png")
                if not os.path.isfile(png_path):
                    console.print("[red]KO (Missing PNG)[/red]")
                    self.record_error(
                        exercise_label,
                        "Output Error",
                        "Output claims results were saved to matrix_analysis.png, "
                        "but that file was not created next to loading.py.",
                    )
                    return
                if os.path.getsize(png_path) < 64:
                    console.print("[red]KO (Invalid PNG)[/red]")
                    self.record_error(
                        exercise_label,
                        "Output Error",
                        "matrix_analysis.png exists but is too small to be a real plot.",
                    )
                    return

            console.print("[green]OK[/green]")

        except Exception as e:
             console.print(f"[red]KO (Execution Error: {e})[/red]")

    def test_accessing_mainframe(self):
        console.print("\n[bold]Testing Exercise 2: Accessing the Mainframe[/bold]")
        exercise_label = "Exercise 2"
        path = self._load_module_path("ex02", "oracle.py")
        if not path: path = self._load_module_path("ex2", "oracle.py")
        
        if not path or not os.path.exists(path):
            console.print("[red]KO (Missing File)[/red]")
            self.record_error(exercise_label, "Missing File", "Could not find oracle.py")
            return

        # Check gitignore
        gitignore = os.path.join(os.path.dirname(path), ".gitignore")
        if not os.path.exists(gitignore):
            self.record_error(exercise_label, "Missing File", "Missing .gitignore")
        else:
            with open(gitignore, "r") as f:
                content = f.read()
                if ".env" not in content:
                    self.record_error(exercise_label, "Security Risk", ".env not found in .gitignore")

        env_example = os.path.join(os.path.dirname(path), ".env.example")
        if not os.path.exists(env_example):
            self.record_error(
                exercise_label,
                "Missing File",
                "Missing .env.example file (required by subject)",
            )
        else:
            with open(env_example, "r", encoding="utf-8") as f:
                ex_lines = f.read().splitlines()
            non_comment = [
                ln.strip()
                for ln in ex_lines
                if ln.strip() and not ln.strip().startswith("#")
            ]
            if not any("=" in ln for ln in non_comment):
                self.record_error(
                    exercise_label,
                    "Config Error",
                    ".env.example should document at least one KEY=value placeholder.",
                )

        # Strict Check
        allowed_imports = ["dotenv"] # python-dotenv usually imported as dotenv
        if not self.common_strict_check(path, exercise_label, extra_imports=allowed_imports): return

        # Test Run 1: No Env
        try:
            cmd = [sys.executable, path]
            cwd = os.path.dirname(path)
            # Run with cleaned env to ensure no interference? 
            # But we need basic env vars.
            # Just run it.
            result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
            out = result.stdout + result.stderr
            if self.check_for_crash(out, exercise_label): return

            if "ORACLE STATUS" in out:
                console.print("[green]OK (Run)[/green]")
            else:
                console.print("[red]KO (Output Mismatch)[/red]")
                self.record_error(exercise_label, "Run Error", f"Unexpected output:\n{out}")

        except Exception as e:
             console.print(f"[red]KO (Execution Error: {e})[/red]")

    def run(self, exercise_name=None):
        console.print("[bold cyan]Testing Module 08: The Matrix[/bold cyan]")
        
        if os.getcwd() not in sys.path:
            sys.path.insert(0, os.getcwd())

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
            # Run all unique
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
