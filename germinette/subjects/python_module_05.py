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
            ("stream_processor", self.test_stream_processor),
            ("data_stream", self.test_polymorphic_streams),
            ("nexus_pipeline", self.test_nexus_integration),
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
            "stream_processor": 0,
            "data_stream": 1,
            "nexus_pipeline": 2,
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
        console.print("[bold cyan]Testing Module 05: Code Nexus (Polymorphism)[/bold cyan]")
        
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

    def test_stream_processor(self):
        console.print("\n[bold]Testing Exercise 0: stream_processor[/bold]")
        exercise_label = "Exercise 0"
        status, path = self._load_module("stream_processor", exercise_label)
        if not status: return

        # Static Check: ABC inheritance
        try:
            with open(path, "r") as f:
                tree = ast.parse(f.read())
            
            # Check for ABC import
            has_abc = False
            for node in tree.body:
                if isinstance(node, ast.ImportFrom) and node.module == 'abc':
                    if 'ABC' in [n.name for n in node.names]:
                        has_abc = True
            
            if not has_abc:
                console.print("[red]KO (No ABC)[/red]")
                self.record_error(exercise_label, "Structure Error", "Must import ABC from abc.")
                return
        except: pass

        import subprocess
        try:
            cmd = [sys.executable, path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            out = result.stdout + result.stderr

            if "=== CODE NEXUS - DATA PROCESSOR FOUNDATION ===" not in out:
                console.print("[red]KO (Missing Header)[/red]")
                self.record_error(exercise_label, "Output Error", "Missing header '=== CODE NEXUS - DATA PROCESSOR FOUNDATION ==='")
                return
            
            required = [
                "Initializing Numeric Processor...",
                "Processed 5 numeric values",
                "Initializing Text Processor...",
                "Processed text: 17 characters",
                "Initializing Log Processor...",
                "ALERT] ERROR level detected",
                "=== Polymorphic Processing Demo ==="
            ]
            
            missing = [r for r in required if r not in out]
            if not missing:
                console.print("[green]OK[/green]")
            else:
                 console.print("[red]KO (Output Mismatch)[/red]")
                 self.record_error(exercise_label, "Output Error", f"Missing output strings: {missing}\nGot:\n{out}")

        except Exception as e:
             console.print(f"[red]KO (Execution Error: {e})[/red]")

    def test_polymorphic_streams(self):
        console.print("\n[bold]Testing Exercise 1: data_stream[/bold]")
        exercise_label = "Exercise 1"
        status, path = self._load_module("data_stream", exercise_label)
        if not status: return

        import subprocess
        try:
            cmd = [sys.executable, path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            out = result.stdout + result.stderr

            if "=== CODE NEXUS - POLYMORPHIC STREAM SYSTEM ===" not in out:
                console.print("[red]KO (Missing Header)[/red]")
                self.record_error(exercise_label, "Output Error", "Missing header '=== CODE NEXUS - POLYMORPHIC STREAM SYSTEM ==='")
                return

            required = [
                "Initializing Sensor Stream",
                "Sensor analysis: 3 readings processed",
                "Initializing Transaction Stream",
                "Transaction analysis: 3 operations",
                "Initializing Event Stream",
                "Event analysis: 3 events",
                "=== Polymorphic Stream Processing ===",
                "Batch 1 Results:",
                "Stream filtering active",
                "Filtered results: 2 critical sensor alerts"
            ]

            missing = [r for r in required if r not in out]
            if not missing:
                console.print("[green]OK[/green]")
            else:
                 console.print("[red]KO (Output Mismatch)[/red]")
                 self.record_error(exercise_label, "Output Error", f"Missing output strings: {missing}\nGot:\n{out}")

        except Exception as e:
             console.print(f"[red]KO (Execution Error: {e})[/red]")

    def test_nexus_integration(self):
        console.print("\n[bold]Testing Exercise 2: nexus_pipeline[/bold]")
        exercise_label = "Exercise 2"
        status, path = self._load_module("nexus_pipeline", exercise_label)
        if not status: return

        import subprocess
        try:
            cmd = [sys.executable, path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            out = result.stdout + result.stderr

            if "=== CODE NEXUS - ENTERPRISE PIPELINE SYSTEM ===" not in out:
                console.print("[red]KO (Missing Header)[/red]")
                self.record_error(exercise_label, "Output Error", "Missing header '=== CODE NEXUS - ENTERPRISE PIPELINE SYSTEM ==='")
                return

            required = [
                "Creating Data Processing Pipeline",
                "Stage 1: Input validation",
                "Stage 3: Output formatting",
                "=== Multi-Format Data Processing ===",
                "Processing JSON data",
                "Output: Processed temperature reading",
                "Processing CSV data",
                "Processing Stream data",
                "=== Pipeline Chaining Demo ===",
                "Pipeline A -> Pipeline B -> Pipeline C",
                "=== Error Recovery Test ===",
                "Recovery successful: Pipeline restored"
            ]

            missing = [r for r in required if r not in out]
            if not missing:
                console.print("[green]OK[/green]")
            else:
                 console.print("[red]KO (Output Mismatch)[/red]")
                 self.record_error(exercise_label, "Output Error", f"Missing output strings: {missing}\nGot:\n{out}")

        except Exception as e:
             console.print(f"[red]KO (Execution Error: {e})[/red]")
