import sys
import os
import ast
import builtins
from rich.console import Console
from rich.panel import Panel
from germinette.core import BaseTester

console = Console()

class Tester(BaseTester):
    def __init__(self):
        self.exercises = [
            ("data_processor", self.test_data_processor),
            ("data_stream", self.test_data_stream),
            ("data_pipeline", self.test_data_pipeline),
        ]
        self.grouped_errors = {}

    def record_error(self, exercise_label, error_type, message):
        if exercise_label not in self.grouped_errors:
            self.grouped_errors[exercise_label] = []
        self.grouped_errors[exercise_label].append(f"[bold]{error_type}[/bold]\n{message}")

    def _load_module(self, module_name, exercise_label):
        cwd = os.getcwd()
        if os.path.exists(os.path.join(cwd, "python_module_05")):
            base_dir = os.path.join(cwd, "python_module_05")
        else:
            base_dir = cwd

        ex_map = {
            "data_processor": 0,
            "data_stream": 1,
            "data_pipeline": 2,
        }
        
        expected_dir = None
        if module_name in ex_map:
            ex_num = ex_map[module_name]
            potential_dir = os.path.join(base_dir, f"ex{ex_num}")
            if os.path.exists(potential_dir):
                expected_dir = potential_dir
            else:
                 console.print("[red]KO (Directory Missing)[/red]")
                 msg = (f"[bold red]Directory not found[/bold red]\n\n"
                        f"Expected directory: [cyan]ex{ex_num}[/cyan]\n"
                        f"Location: {base_dir}\n")
                 self.record_error(exercise_label, "Missing Directory", msg)
                 return None, None

        target_file = f"{module_name}.py"
        found_path = os.path.join(expected_dir, target_file)
        
        if not os.path.exists(found_path):
             console.print("[red]KO (Missing File)[/red]")
             msg = (f"[bold red]File not found[/bold red]\n\n"
                    f"Expected: [cyan]{target_file}[/cyan]\n"
                    f"Directory: [cyan]{expected_dir}[/cyan]\n")
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
        console.print("[bold cyan]Testing Module 05: Code Nexus (v3.0)[/bold cyan]")
        
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
            for _, func in self.exercises:
                func()
            
        if self.grouped_errors:
            console.print()
            console.rule("[bold red]Detailed Error Report[/bold red]")
            console.print()
            for label, messages in self.grouped_errors.items():
                content = "\n\n[dim]────────────────────────────────[/dim]\n\n".join(messages)
                console.print(Panel(content, title=f"[bold red]{label}[/bold red]", border_style="red", expand=False))
                console.print()

    # --- Exercise Tests ---

    def _all_builtin_functions(self):
        return [n for n in dir(builtins) if not n.startswith("_")]

    def test_data_processor(self):
        console.print("\n[bold]Testing Exercise 0: data_processor[/bold]")
        exercise_label = "Exercise 0"
        status, path = self._load_module("data_processor", exercise_label)
        if not status: return

        # v3.0 general rules: imports restricted to abc + typing, all builtins authorized.
        if not self.verify_strict(
            path,
            exercise_label,
            self._all_builtin_functions(),
            allowed_imports=["abc", "typing"],
            enforce_try_except=False,
        ):
            return

        import subprocess
        try:
            cmd = [sys.executable, path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            out = result.stdout + result.stderr
            if self.check_for_crash(out, exercise_label): return

            # AST Verification for ABC
            with open(path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
            
            classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            if "DataProcessor" not in classes or "NumericProcessor" not in classes or "TextProcessor" not in classes or "LogProcessor" not in classes:
                 console.print("[red]KO (Missing Classes)[/red]")
                 self.record_error(exercise_label, "Structure Error", f"Missing required classes. Found: {classes}")
                 return
            methods = {
                node.name: {f.name for f in node.body if isinstance(f, ast.FunctionDef)}
                for node in ast.walk(tree)
                if isinstance(node, ast.ClassDef)
            }
            expected_dp = {"validate", "ingest", "output"}
            if not expected_dp.issubset(methods.get("DataProcessor", set())):
                self.record_error(
                    exercise_label,
                    "Structure Error",
                    "DataProcessor must define validate(), ingest(), and output().",
                )
                return
            
            # v3.0 output is customizable; enforce presence of core demo parts.
            required = [
                "Code Nexus",
                "Numeric Processor",
                "Text Processor",
                "Log Processor",
            ]
            
            missing = [r for r in required if r not in out]
            if not missing:
                console.print("[green]OK[/green]")
            else:
                 console.print("[red]KO (Output Mismatch)[/red]")
                 self.record_error(exercise_label, "Output Error", f"Missing expected output segments. Missing: {missing}")

        except Exception as e:
             console.print(f"[red]KO (Execution Error: {e})[/red]")

    def test_data_stream(self):
        console.print("\n[bold]Testing Exercise 1: data_stream[/bold]")
        exercise_label = "Exercise 1"
        status, path = self._load_module("data_stream", exercise_label)
        if not status: return

        if not self.verify_strict(
            path,
            exercise_label,
            self._all_builtin_functions(),
            allowed_imports=["abc", "typing"],
            enforce_try_except=False,
        ):
            return

        import subprocess
        try:
            cmd = [sys.executable, path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            out = result.stdout + result.stderr
            if self.check_for_crash(out, exercise_label): return

            with open(path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
            classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            if "DataStream" not in classes:
                 console.print("[red]KO (Missing DataStream Class)[/red]")
                 self.record_error(exercise_label, "Structure Error", "DataStream class is missing.")
                 return
            methods = {
                node.name: {f.name for f in node.body if isinstance(f, ast.FunctionDef)}
                for node in ast.walk(tree)
                if isinstance(node, ast.ClassDef)
            }
            required_methods = {
                "register_processor",
                "process_stream",
                "print_processors_stats",
            }
            if not required_methods.issubset(methods.get("DataStream", set())):
                self.record_error(
                    exercise_label,
                    "Structure Error",
                    "DataStream must implement register_processor, process_stream, "
                    "and print_processors_stats.",
                )
                return

            required = [
                "Code Nexus - Data Stream",
                "DataStream statistics",
            ]

            missing = [r for r in required if r not in out]
            if not missing:
                console.print("[green]OK[/green]")
            else:
                 console.print("[red]KO (Output Mismatch)[/red]")
                 self.record_error(exercise_label, "Output Error", f"Missing expected output: {missing}")

        except Exception as e:
              console.print(f"[red]KO (Execution Error: {e})[/red]")

    def test_data_pipeline(self):
        console.print("\n[bold]Testing Exercise 2: data_pipeline[/bold]")
        exercise_label = "Exercise 2"
        status, path = self._load_module("data_pipeline", exercise_label)
        if not status: return

        if not self.verify_strict(
            path,
            exercise_label,
            self._all_builtin_functions(),
            allowed_imports=["abc", "typing"],
            enforce_try_except=False,
        ):
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                tree = ast.parse(content)
            if "Protocol" not in content:
                console.print("[red]KO (Missing Protocol)[/red]")
                self.record_error(exercise_label, "Structure Error", "You must use typing.Protocol for ExportPlugin.")
                return
            classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            if "DataStream" not in classes:
                self.record_error(exercise_label, "Structure Error", "Missing DataStream class.")
                return
            has_csv = any("CSV" in name.upper() for name in classes)
            has_json = any("JSON" in name.upper() for name in classes)
            if not has_csv or not has_json:
                self.record_error(
                    exercise_label,
                    "Structure Error",
                    "Expected at least one CSV plugin class and one JSON plugin class.",
                )
                return
            methods = {
                node.name: {f.name for f in node.body if isinstance(f, ast.FunctionDef)}
                for node in ast.walk(tree)
                if isinstance(node, ast.ClassDef)
            }
            if "output_pipeline" not in methods.get("DataStream", set()):
                self.record_error(
                    exercise_label,
                    "Structure Error",
                    "DataStream must implement output_pipeline(nb, plugin).",
                )
                return
        except Exception:
            pass

        import subprocess
        try:
            cmd = [sys.executable, path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            out = result.stdout + result.stderr
            if self.check_for_crash(out, exercise_label): return

            if "Code Nexus - Data Pipeline" not in out:
                console.print("[red]KO (Missing Header)[/red]")
                self.record_error(exercise_label, "Output Error", "Missing header '=== Code Nexus - Data Pipeline ==='")
                return

            required = [
                "CSV",
                "JSON",
                "DataStream statistics",
            ]

            missing = [r for r in required if r not in out]
            if not missing:
                console.print("[green]OK[/green]")
            else:
                 console.print("[red]KO (Output Mismatch)[/red]")
                 self.record_error(exercise_label, "Output Error", f"Missing output strings: {missing}")

        except Exception as e:
             console.print(f"[red]KO (Execution Error: {e})[/red]")
