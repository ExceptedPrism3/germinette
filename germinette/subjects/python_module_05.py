import sys
import os
import ast
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

    def check_polymorphism_requirements(self, path, exercise_label):
        """Checks for mandatory usage of super()."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
            
            has_super = False
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'super':
                    has_super = True
                    break
            if not has_super:
                console.print("[red]KO (Missing super())[/red]")
                self.record_error(exercise_label, "Structure Error", "Must use 'super()' to initialize parent classes or call parent methods.")
                return False
            return True
        except Exception as e:
            console.print(f"[red]KO (AST Error: {e})[/red]")
            return False

    def test_data_processor(self):
        console.print("\n[bold]Testing Exercise 0: data_processor[/bold]")
        exercise_label = "Exercise 0"
        status, path = self._load_module("data_processor", exercise_label)
        if not status: return

        # v3.0 check architecture (ABC module required)
        allowed_builtins = ["print", "len", "float", "int", "str", "isinstance", "issubclass", "all", "any", "zip", "sum", "list", "dict", "tuple"]
        
        if not self.verify_strict(path, exercise_label, 
                                  allowed_builtins, 
                                  allowed_imports=["sys", "abc", "typing"], 
                                  enforce_try_except=True): return

        if not self.check_polymorphism_requirements(path, exercise_label): return

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
            
            # v3.0 check output
            required = [
                "Testing Numeric Processor",
                "Processed: 3 items",
                "Testing Text Processor",
                "Testing Log Processor",
                "Testing Error Handling"
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

        # v3.0
        allowed_builtins = ["next", "iter", "range", "len", "print", "float", "int", "str", "isinstance", "issubclass", "tuple", "list", "dict"]
        
        if not self.verify_strict(path, exercise_label, 
                                  allowed_builtins, 
                                  allowed_imports=["sys", "abc", "typing"], 
                                  enforce_try_except=True): return

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

            required = [
                "=== Streaming Data Demo ===",
                "Registering processors",
                "Processing stream",
                "Stream Results",
                "Total numeric items",
                "Total textual items",
                "Total log items"
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

        # v3.0: export plugin protocols
        allowed_builtins = ["print", "len", "range", "float", "int", "str", "isinstance", "issubclass", "list", "dict", "tuple"]
        
        if not self.verify_strict(path, exercise_label, 
                                  allowed_builtins, 
                                  allowed_imports=["sys", "json", "csv", "io", "abc", "typing", "collections"], 
                                  enforce_try_except=False): return

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            if "Protocol" not in content:
                 console.print("[red]KO (Missing Protocol)[/red]")
                 self.record_error(exercise_label, "Structure Error", "You must use typing.Protocol for ExportPlugin.")
                 return
        except: pass

        import subprocess
        try:
            cmd = [sys.executable, path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            out = result.stdout + result.stderr
            if self.check_for_crash(out, exercise_label): return

            if "=== Protocol & Pipeline Demo ===" not in out:
                console.print("[red]KO (Missing Header)[/red]")
                self.record_error(exercise_label, "Output Error", "Missing header '=== Protocol & Pipeline Demo ==='")
                return

            required = [
                "Exporting to CSV",
                "Exporting to JSON",
                "csv_output",
                "json_output"
            ]

            missing = [r for r in required if r not in out]
            if not missing:
                console.print("[green]OK[/green]")
            else:
                 console.print("[red]KO (Output Mismatch)[/red]")
                 self.record_error(exercise_label, "Output Error", f"Missing output strings: {missing}")

        except Exception as e:
             console.print(f"[red]KO (Execution Error: {e})[/red]")
