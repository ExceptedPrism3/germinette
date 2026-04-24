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
            ("ft_data_alchemist", self.test_data_alchemist),
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

        ex_map = {
            "ft_command_quest": 0,
            "ft_score_analytics": 1,
            "ft_coordinate_system": 2,
            "ft_achievement_tracker": 3,
            "ft_inventory_system": 4,
            "ft_data_stream": 5,
            "ft_data_alchemist": 6
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
        
        type_hint_errors = self.check_type_hints(found_path)
        if type_hint_errors:
            console.print("[red]KO[/red]")
            self.record_error(exercise_label, "Style Error (Missing Type Hints)", type_hint_errors)
            return None, None
            
        return "FOUND", found_path 

    def run(self, exercise_name=None):
        console.print("[bold purple]Testing Module 03: Data Quest (v3.0)[/bold purple]")
        
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

    def verify_strict(self, path, exercise_label, allowed_funcs, allowed_imports=["sys"], enforce_try_except=False):
        err = self.check_no_file_io(path)
        if err:
            console.print(f"[red]KO (Forbidden Operation)[/red]")
            self.record_error(exercise_label, "Forbidden Operation", err)
            return False

        err = self.check_imports(path, allowed_imports)
        if err:
            console.print(f"[red]KO (Forbidden Import)[/red]")
            self.record_error(exercise_label, "Forbidden Import", err)
            return False

        if enforce_try_except:
            err = self.check_try_except(path, exercise_label)
            if err:
                console.print(f"[red]KO (Strictness)[/red]")
                self.record_error(exercise_label, "Structure Error", err)
                return False

        err = self.check_authorized_functions(path, allowed_funcs)
        if err:
            console.print(f"[red]KO (Forbidden Function)[/red]")
            self.record_error(exercise_label, "Authorized Functions", err)
            return False
        
        return True

    # --- Exercise Tests ---

    def test_command_quest(self):
        console.print("\n[bold]Testing Exercise 0: ft_command_quest[/bold]")
        exercise_label = "Exercise 0"
        status, path = self._load_module("ft_command_quest", exercise_label)
        if not status: return

        if not self.verify_strict(path, exercise_label, ["len", "print"], allowed_imports=["sys"]): return

        out1 = self._run_script_args(path, [])
        if self.check_for_crash(out1, exercise_label): return
        if "=== Command Quest ===" in out1 and "No arguments provided!" in out1:
            console.print("[green]OK (No Args)[/green]")
        else:
            console.print("[red]KO (No Args)[/red]")
            self.record_error(exercise_label, "Output Error", f"Expected 'No arguments provided!'. Got:\n{out1}")

        out2 = self._run_script_args(path, ["hello", "world", "42"])
        if self.check_for_crash(out2, exercise_label): return
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

        if not self.verify_strict(path, exercise_label, 
                                  ["len", "sum", "max", "min", "int", "print"], 
                                  allowed_imports=["sys"], 
                                  enforce_try_except=True): return

        out1 = self._run_script_args(path, ["1500", "2300", "1800", "2100", "1950"])
        if self.check_for_crash(out1, exercise_label): return
        if "Average score: 1930.0" in out1 and "High score: 2300" in out1:
            console.print("[green]OK (Valid Scores)[/green]")
        else:
            console.print("[red]KO (Valid Scores)[/red]")
            self.record_error(exercise_label, "Math Error", f"Expected Average: 1930.0. Got:\n{out1}")
        
        out2 = self._run_script_args(path, [])
        if self.check_for_crash(out2, exercise_label): return
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

        # v3.0 authorized: import math, math.sqrt(), input(), round(), print()
        if not self.verify_strict(path, exercise_label, 
                                  ["tuple", "float", "round", "print", "input"], 
                                  allowed_imports=["math"],
                                  enforce_try_except=True): return

        import subprocess
        # Test Case 1: Valid
        try:
             cmd = [sys.executable, path]
             proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
             stdout, stderr = proc.communicate(input="3,4,0\n4,5,6\n")
             out = stdout + stderr

             if self.check_for_crash(out, exercise_label): return

             if "=== Game Coordinate System ===" not in out:
                  console.print("[red]KO (Missing Header)[/red]")
                  self.record_error(exercise_label, "Output Error", "Missing '=== Game Coordinate System ==='")
                  return
             
             # distance of (3,4,0) to origin is 5.0
             if "5.0" in out or "5.00" in out or "Distance to center:" in out:
                  console.print("[green]OK (Calculation)[/green]")
             else:
                  console.print("[red]KO (Calculation)[/red]")
                  self.record_error(exercise_label, "Math Error", f"Distance calculation incorrect. Got:\n{out}")

        except Exception as e:
             console.print(f"[red]KO (Execution: {e})[/red]")

        # Test Case 2: Invalid (requires try/except handling)
        try:
             proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
             stdout, stderr = proc.communicate(input="3,abc,0\n3,4,0\n4,5,6\n")
             out = stdout + stderr

             # Should not crash unhandled, should show error message
             if self.check_for_crash(out, exercise_label): return
             
             if "ValueError" in out or "error" in out.lower() or "invalid" in out.lower():
                  console.print("[green]OK (Error Handling)[/green]")
             else:
                  console.print("[red]KO (Error Handling)[/red]")
                  self.record_error(exercise_label, "Handling Error", f"Expected error handling output. Got:\n{out}")
        except Exception as e:
             console.print(f"[red]KO (Execution: {e})[/red]")

    def test_achievement_tracker(self):
        console.print("\n[bold]Testing Exercise 3: ft_achievement_tracker[/bold]")
        exercise_label = "Exercise 3"
        status, path = self._load_module("ft_achievement_tracker", exercise_label)
        if not status: return

        # v3.0 alignment (Issue #14, reported by koldoest26):
        # Data Quest v3.0 — Achievement Hunter: four players, fixed output labels; subject PDF
        # authorizes: len(), print(), import random, random.*, set(), set.union() /
        # set.intersection() / set.difference() (no sys.argv exercise).
        if not self.verify_strict(
            path, exercise_label, ["set", "len", "print"], allowed_imports=["random"]
        ):
            return

        out = self._run_script_args(path, [])
        if self.check_for_crash(out, exercise_label):
            return

        if "=== Achievement Tracker System ===" not in out:
            console.print("[red]KO (Missing Header)[/red]")
            self.record_error(
                exercise_label, "Output Error", "Missing '=== Achievement Tracker System ==='."
            )
            return

        required_lines: list[str] = [
            "Player Alice:",
            "Player Bob:",
            "Player Charlie:",
            "Player Dylan:",
            "All distinct achievements:",
            "Common achievements:",
            "Only Alice has:",
            "Only Bob has:",
            "Only Charlie has:",
            "Only Dylan has:",
            "Alice is missing:",
            "Bob is missing:",
            "Charlie is missing:",
            "Dylan is missing:",
        ]
        missing = [s for s in required_lines if s not in out]
        if not missing:
            console.print("[green]OK (Set Operations v3.0)[/green]")
        else:
            console.print("[red]KO (Set Operations v3.0)[/red]")
            self.record_error(
                exercise_label,
                "Logic Error",
                f"Missing v3.0 output markers: {missing!r}.\nGot:\n{out}",
            )

    def test_inventory_system(self):
        console.print("\n[bold]Testing Exercise 4: ft_inventory_system[/bold]")
        exercise_label = "Exercise 4"
        status, path = self._load_module("ft_inventory_system", exercise_label)
        if not status: return

        # v3.0 alignment update (Issue #13, reported by koldoest26):
        # Header/logic expectations were updated from older Data Quest versions.
        # v3.0 authorized: import sys, sys.argv, len(), print(), sum(), list(),
        # round(), dict.keys(), dict.values(), dict.update()
        if not self.verify_strict(path, exercise_label, 
                                  ["dict", "len", "print", "keys", "values", "update", "int", "sum", "round", "list"], 
                                  allowed_imports=["sys"]): return

        # Sample from v3.0 subject includes duplicate + invalid entries.
        args = ["sword:1", "potion:5", "shield:2", "armor:3", "helmet:1", "sword:2", "hello", "key:value"]
        out = self._run_script_args(path, args)
        if self.check_for_crash(out, exercise_label): return
        
        # 1. Header Checks
        if "=== Inventory System Analysis ===" not in out:
             console.print("[red]KO (Missing Header)[/red]")
             self.record_error(exercise_label, "Structure Error", "Missing '=== Inventory System Analysis ==='")
             return

        # 2. v3.0 behavior checks: duplicate/invalid handling + expected aggregate.
        if "Redundant item" in out and "invalid parameter" in out.lower():
             console.print("[green]OK (Validation Handling)[/green]")
        else:
             console.print("[red]KO (Validation Handling)[/red]")
             self.record_error(exercise_label, "Handling Error", f"Expected duplicate/invalid parameter handling. Got:\n{out}")

        # 3. Stats checks (subject-style phrasing).
        if "Total quantity" in out and "represents" in out:
             console.print("[green]OK (Percentages)[/green]")
        else:
             console.print("[red]KO (Percentages)[/red]")
             self.record_error(exercise_label, "Output Error", "Missing quantity/percentage outputs.")

        # 4. Most / Least + update line.
        if "most abundant" in out.lower() and "least abundant" in out.lower() and "Updated inventory" in out:
             console.print("[green]OK (Statistics)[/green]")
        else:
             console.print("[red]KO (Statistics)[/red]")
             self.record_error(exercise_label, "Logic Error", "Missing most/least abundant item report or final update.")

    def test_data_stream(self):
        console.print("\n[bold]Testing Exercise 5: ft_data_stream[/bold]")
        exercise_label = "Exercise 5"
        status, path = self._load_module("ft_data_stream", exercise_label)
        if not status: return

        if not self.verify_strict(path, exercise_label,
                                  ["next", "iter", "range", "len", "print", "tuple"],
                                  allowed_imports=["sys", "typing", "random"]):
             return

        out = self._run_script_args(path, [])
        if self.check_for_crash(out, exercise_label): return
        
        if "=== Game Data Stream Processor ===" not in out:
             console.print("[red]KO (Missing Header)[/red]")
             return

        # v3.0 alignment update (Issue #13, reported by koldoest26):
        # gen_event yields (player_name, action), then consume_event drains list.
        if "Event 0:" in out and "Event 999:" in out:
             console.print("[green]OK (1000 Events)[/green]")
        else:
             console.print("[red]KO (1000 Events)[/red]")
             self.record_error(exercise_label, "Output Error", "Expected event stream from Event 0 to Event 999.")

        if "Built list of 10 events:" in out and "Got event from list:" in out and "Remains in list:" in out:
             console.print("[green]OK (consume_event flow)[/green]")
        else:
             console.print("[red]KO (consume_event flow)[/red]")
             self.record_error(exercise_label, "Logic Error", "Expected consume_event output over the 10-event list.")

    def test_data_alchemist(self):
        console.print("\n[bold]Testing Exercise 6: ft_data_alchemist[/bold]")
        exercise_label = "Exercise 6"
        status, path = self._load_module("ft_data_alchemist", exercise_label)
        if not status: return
        
        # v3.0 alignment update (Issue #13, reported by koldoest26):
        # random import and comprehension expectations were updated for the new subject.
        # v3.0 authorized: import random, random.*, print(), len(), sum(), round()
        if not self.verify_strict(path, exercise_label, ["len", "print", "sum", "round", "int", "float"], allowed_imports=["random"]): return

        out = self._run_script_args(path, [])
        if self.check_for_crash(out, exercise_label): return
        
        if "=== Game Data Alchemist ===" not in out:
             console.print("[red]KO (Missing Header)[/red]")
             self.record_error(exercise_label, "Output Error", "Missing '=== Game Data Alchemist ==='")
             return
        
        # Check for comprehension examples usage in output (rough proxy for now)
        required_hints = [
            "List comp", "Dict comp", "Set comp", "Filtered"
        ]
        
        # Not requiring exact section headers, just signs of list/dict/set operations.
        # Let's inspect the AST for comprehensions instead to be sure.
        import ast
        try:
             with open(path, "r", encoding="utf-8") as f:
                  tree = ast.parse(f.read())
             
             has_list_comp = any(isinstance(n, ast.ListComp) for n in ast.walk(tree))
             has_dict_comp = any(isinstance(n, ast.DictComp) for n in ast.walk(tree))
             has_set_comp = any(isinstance(n, ast.SetComp) for n in ast.walk(tree))
             
             # Subject requires list + dict comprehensions; set comprehensions are optional.
             if has_list_comp and has_dict_comp:
                  console.print("[green]OK (Comprehensions verified in AST)[/green]")
             else:
                  console.print("[red]KO (Missing Comprehensions)[/red]")
                  self.record_error(exercise_label, "Structure Error", f"Script must use list and dict comprehensions.\nListComp: {has_list_comp}, DictComp: {has_dict_comp}, SetComp(optional): {has_set_comp}")
        except Exception as e:
             console.print(f"[red]KO (AST Error: {e})[/red]")

    def _run_script_args(self, path, args):
        import subprocess
        try:
            cmd = [sys.executable, path] + args
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            return result.stdout + result.stderr
        except Exception as e:
            return str(e)
