import sys
import os
import importlib.util
from rich.console import Console
from rich.panel import Panel
from germinette.core import BaseTester
from germinette.utils import IOTester

console = Console()

class Tester(BaseTester):
    def __init__(self):
        self.exercises = [
            ("ft_command_quest", self.test_command_quest),
            ("ft_score_analytics", self.test_score_analytics),
            ("ft_coordinate_system", self.test_coordinate_system),
            ("ft_achievement_tracker", self.test_achievement_tracker),
            ("ft_inventory_system", self.test_inventory_system),
            ("ft_data_stream", self.test_data_stream),
            ("ft_analytics_dashboard", self.test_analytics_dashboard),
        ]
        self.grouped_errors = {}

    def record_error(self, exercise_label, error_type, message):
        if exercise_label not in self.grouped_errors:
            self.grouped_errors[exercise_label] = []
        self.grouped_errors[exercise_label].append(f"[bold]{error_type}[/bold]\n{message}")

    def _load_module(self, module_name, exercise_label):
        cwd = os.getcwd()
        if os.path.exists(os.path.join(cwd, "python_module_03")):
            base_dir = os.path.join(cwd, "python_module_03")
        else:
            base_dir = cwd

        # Map exercise to directory
        ex_map = {
            "ft_command_quest": 0,
            "ft_score_analytics": 1,
            "ft_coordinate_system": 2,
            "ft_achievement_tracker": 3,
            "ft_inventory_system": 4,
            "ft_data_stream": 5,
            "ft_analytics_dashboard": 6
        }
        
        expected_dir = None
        if module_name in ex_map:
            ex_num = ex_map[module_name]
            # Try to find exactly exN
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
        # Flake8
        style_errors = self.check_flake8(found_path)
        if style_errors:
             console.print("[red]KO[/red]")
             self.record_error(exercise_label, "Style Error (Flake8)", style_errors)
             return None, None
        
        # Docstrings
        doc_errors = self.check_docstrings(found_path)
        if doc_errors:
             console.print("[red]KO[/red]")
             self.record_error(exercise_label, "Style Error (Missing Docstrings)", doc_errors)
             return None, None
        
        type_hint_errors = self.check_type_hints(found_path)
        if type_hint_errors:
             console.print("[red]KO[/red]")
             self.record_error(exercise_label, "Style Error (Missing Type Hints)", type_hint_errors)
             return None, None
            
        return "FOUND", found_path 

    def run(self, exercise_name=None):
        console.print("[bold purple]Testing Module 03: Data Quest[/bold purple]")
        
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

    def test_command_quest(self):
        console.print("\n[bold]Testing Exercise 0: ft_command_quest[/bold]")
        exercise_label = "Exercise 0"
        status, path = self._load_module("ft_command_quest", exercise_label)
        if not status: return

        # Test Case 1: No args
        out1 = self._run_script_args(path, [])
        if "=== Command Quest ===" in out1 and "No arguments provided!" in out1:
            console.print("[green]OK (No Args)[/green]")
        else:
            console.print("[red]KO (No Args)[/red]")
            self.record_error(exercise_label, "Output Error", f"Expected 'No arguments provided!'. Got:\n{out1}")

        # Test Case 2: Args
        out2 = self._run_script_args(path, ["hello", "world", "42"])
        if "Arguments received: 3" in out2 and "Argument 1: hello" in out2:
            console.print("[green]OK (With Args)[/green]")
        else:
            console.print("[red]KO (With Args)[/red]")
            self.record_error(exercise_label, "Output Error", f"Expected argument details. Got:\n{out2}")

    def test_score_analytics(self):
        console.print("\n[bold]Testing Exercise 1: ft_score_analytics[/bold]")
        exercise_label = "Exercise 1"
        status, path = self._load_module("ft_score_analytics", exercise_label)
        if not status: return

        # Test Case 1: Valid Scores
        out1 = self._run_script_args(path, ["1500", "2300", "1800", "2100", "1950"])
        if "Average score: 1930.0" in out1 and "High score: 2300" in out1:
            console.print("[green]OK (Valid Scores)[/green]")
        else:
            console.print("[red]KO (Valid Scores)[/red]")
            self.record_error(exercise_label, "Math Error", f"Expected Average: 1930.0. Got:\n{out1}")
        
        # Test Case 2: No Scores
        out2 = self._run_script_args(path, [])
        if "No scores provided" in out2:
             console.print("[green]OK (No Scores)[/green]")
        else:
             console.print("[red]KO (No Scores)[/red]")
             self.record_error(exercise_label, "Handling Error", "Should handle empty input gracefully.")

    def test_coordinate_system(self):
        console.print("\n[bold]Testing Exercise 2: ft_coordinate_system[/bold]")
        exercise_label = "Exercise 2"
        status, path = self._load_module("ft_coordinate_system", exercise_label)
        if not status: return

        # This exercise seems to take no args but uses internal logic or input? 
        # PDF says "Parsing coordinates: '3,4,0'". 
        # If it's pure script output, we just run it.
        # "Parsing invalid coordinates..." suggests it demonstrates parsing internally.
        
        out = self._run_script_args(path, [])
        
        # Check specific headers and results
        if "=== Game Coordinate System ===" not in out:
             console.print("[red]KO (Missing Header)[/red]")
             self.record_error(exercise_label, "Output Error", "Missing '=== Game Coordinate System ==='")
             return

        if "Distance between (0, 0, 0) and (10, 20, 5): 22.91" in out:
             console.print("[green]OK (Calculation)[/green]")
        else:
             console.print("[red]KO (Calculation)[/red]")
             self.record_error(exercise_label, "Math Error", "Distance calculation incorrect or format mismatch.")

        if "Error details - Type: ValueError" in out:
             console.print("[green]OK (Error Handling)[/green]")
        else:
             console.print("[red]KO (Error Handling)[/red]")

    def test_achievement_tracker(self):
        console.print("\n[bold]Testing Exercise 3: ft_achievement_tracker[/bold]")
        exercise_label = "Exercise 3"
        status, path = self._load_module("ft_achievement_tracker", exercise_label)
        if not status: return

        out = self._run_script_args(path, [])
        
        if "=== Achievement Tracker System ===" not in out:
             console.print("[red]KO (Missing Header)[/red]")
             self.record_error(exercise_label, "Output Error", "Missing header.")
             return
            
        # Check set operations evidence
        if "Common to all players: {'level_10'}" in out or "Common to all players: {'level_10'}" in out.replace('"', "'"):
             console.print("[green]OK (Intersection)[/green]")
        else:
             console.print("[red]KO (Intersection)[/red]")
             self.record_error(exercise_label, "Logic Error", "Failed to find common achievements.")

        if "Total unique achievements: 7" in out:
             console.print("[green]OK (Union/Len)[/green]")
        else:
             console.print("[red]KO (Union/Len)[/red]")

    def test_inventory_system(self):
        console.print("\n[bold]Testing Exercise 4: ft_inventory_system[/bold]")
        exercise_label = "Exercise 4"
        status, path = self._load_module("ft_inventory_system", exercise_label)
        if not status: return

        out = self._run_script_args(path, [])
        
        if "=== Player Inventory System ===" not in out:
             console.print("[red]KO (Missing Header)[/red]")
             self.record_error(exercise_label, "Output Error", "Missing header.")
             return

        if "Inventory value: 950 gold" in out:
             console.print("[green]OK (Value Calculation)[/green]")
        else:
             console.print("[red]KO (Value Calculation)[/red]")
             
        if "=== Transaction: Alice gives Bob 2 potions ===" in out:
             console.print("[green]OK (Transaction Logic)[/green]")
        else:
             console.print("[red]KO (Transaction Logic)[/red]")

    def test_data_stream(self):
        console.print("\n[bold]Testing Exercise 5: ft_data_stream[/bold]")
        exercise_label = "Exercise 5"
        status, path = self._load_module("ft_data_stream", exercise_label)
        if not status: return

        out = self._run_script_args(path, [])
        
        if "=== Game Data Stream Processor ===" not in out:
             console.print("[red]KO (Missing Header)[/red]")
             return

        # Check Generator evidence
        if "Processing 1000 game events..." in out:
             console.print("[green]OK (Stream Start)[/green]")
        else:
             console.print("[red]KO (Stream Start)[/red]")

        if "Fibonacci sequence" in out:
             console.print("[green]OK (Generator Demo)[/green]")
        else:
             console.print("[red]KO (Generator Demo)[/red]")

    def test_analytics_dashboard(self):
        console.print("\n[bold]Testing Exercise 6: ft_analytics_dashboard[/bold]")
        exercise_label = "Exercise 6"
        status, path = self._load_module("ft_analytics_dashboard", exercise_label)
        if not status: return

        out = self._run_script_args(path, [])
        
        if "=== Game Analytics Dashboard ===" not in out:
             console.print("[red]KO (Missing Header)[/red]")
             return
        
        required_headers = [
            "=== List Comprehension Examples ===",
            "=== Dict Comprehension Examples ===",
            "=== Set Comprehension Examples ===",
            "=== Combined Analysis ==="
        ]
        
        missing = [h for h in required_headers if h not in out]
        if missing:
             console.print(f"[red]KO (Missing Sections: {len(missing)})[/red]")
             self.record_error(exercise_label, "Structure Error", f"Missing sections: {missing}")
        else:
             console.print("[green]OK (All Sections Present)[/green]")

    def _run_script_args(self, path, args):
        import subprocess
        try:
            cmd = [sys.executable, path] + args
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            # Return combined output to verify stderr too if needed
            return result.stdout + result.stderr
        except Exception as e:
            return str(e)
