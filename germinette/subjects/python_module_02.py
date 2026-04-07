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
            ("ft_first_exception", self.test_first_exception),
            ("ft_raise_exception", self.test_raise_exception),
            ("ft_different_errors", self.test_different_errors),
            ("ft_custom_errors", self.test_custom_errors),
            ("ft_finally_block", self.test_finally_block),
        ]
        self.grouped_errors = {}

    def record_error(self, exercise_label, error_type, message):
        if exercise_label not in self.grouped_errors:
            self.grouped_errors[exercise_label] = []
        self.grouped_errors[exercise_label].append(f"[bold]{error_type}[/bold]\n{message}")

    def _load_module(self, module_name, exercise_label):
        cwd = os.getcwd()
        if os.path.exists(os.path.join(cwd, "python_module_02")):
            base_dir = os.path.join(cwd, "python_module_02")
        else:
            base_dir = cwd

        ex_map = {
            "ft_first_exception": 0,
            "ft_raise_exception": 1,
            "ft_different_errors": 2,
            "ft_custom_errors": 3,
            "ft_finally_block": 4,
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
                       f"Location: {base_dir}\n\n"
                       f"[bold]Please ensure the exercise folder exists.[/bold]")
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

        try:
            spec = importlib.util.spec_from_file_location(module_name, found_path)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = mod
            spec.loader.exec_module(mod)

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

            return mod, found_path
        except Exception as e:
            console.print("[red]KO[/red]")
            self.record_error(exercise_label, "Import Error", str(e))
            return None, None

    def run(self, exercise_name=None):
        console.print("[bold blue]Testing Module 02: Garden Guardian (v3.0)[/bold blue]")

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
                self.record_error("Exercise filter", "Unknown exercise",
                                  f"No exercise matches '{exercise_name}'.")
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

    def test_first_exception(self):
        console.print("\n[bold]Testing Exercise 0: ft_first_exception[/bold]")
        exercise_label = "Exercise 0"
        mod, path = self._load_module("ft_first_exception", exercise_label)
        if not mod: return

        # Strict checks: authorized int(), print()
        if not self.verify_strict(path, exercise_label, ["int", "print"],
                                  allowed_imports=["sys"], enforce_try_except=True):
            return

        # v3.0: requires input_temperature(temp_str) and test_temperature()
        if not hasattr(mod, "input_temperature"):
            console.print("[red]KO (Function Missing)[/red]")
            self.record_error(exercise_label, "Missing Function",
                              "input_temperature(temp_str) not found.\n"
                              "v3.0 requires this function name (not check_temperature).")
            return

        if not hasattr(mod, "test_temperature"):
            console.print("[red]KO (Missing Test Function)[/red]")
            self.record_error(exercise_label, "Structure Error",
                              "Missing mandatory function 'test_temperature()'")
            return

        func = mod.input_temperature

        # Test valid input
        try:
            ret = func("25")
            if ret == 25:
                console.print("[green]OK (Valid: '25' → 25)[/green]")
            else:
                console.print(f"[red]KO (Valid: '25')[/red]")
                self.record_error(exercise_label, "Return Mismatch",
                                  f"Expected 25, got {ret}")
        except Exception as e:
            console.print(f"[red]KO (Crash on '25')[/red]")
            self.record_error(exercise_label, "Crash", f"Input: '25'\nException: {e}")

        # Test invalid input — should not crash
        try:
            func("abc")
            console.print("[green]OK ('abc' — Handled)[/green]")
        except Exception as e:
            console.print(f"[red]KO ('abc' — Crashed)[/red]")
            self.record_error(exercise_label, "Crash",
                              f"Input: 'abc'\nProgram must not crash on invalid input.\nException: {e}")

        # Script execution check
        output = self._run_script(path)
        if self.check_for_crash(output, exercise_label): return
        if "=== Garden Temperature ===" in output and "abc" in output:
            console.print("[green]OK (Script Execution)[/green]")
        else:
            console.print("[red]KO (Script Execution)[/red]")
            self.record_error(exercise_label, "Script Output",
                              f"Expected header '=== Garden Temperature ===' and 'abc' test.\nGot:\n{output}")

    def test_raise_exception(self):
        console.print("\n[bold]Testing Exercise 1: ft_raise_exception[/bold]")
        exercise_label = "Exercise 1"
        mod, path = self._load_module("ft_raise_exception", exercise_label)
        if not mod: return

        if not self.verify_strict(path, exercise_label, ["int", "print"],
                                  allowed_imports=["sys"], enforce_try_except=True):
            return

        if not hasattr(mod, "input_temperature"):
            console.print("[red]KO (Function Missing)[/red]")
            self.record_error(exercise_label, "Missing Function",
                              "input_temperature(temp_str) not found")
            return

        if not hasattr(mod, "test_temperature"):
            console.print("[red]KO (Missing Test Function)[/red]")
            self.record_error(exercise_label, "Structure Error",
                              "Missing mandatory function 'test_temperature()'")
            return

        func = mod.input_temperature

        # Valid input in range
        try:
            ret = func("25")
            if ret == 25:
                console.print("[green]OK (Valid: 25)[/green]")
            else:
                console.print(f"[red]KO (Valid: got {ret})[/red]")
                self.record_error(exercise_label, "Value Error",
                                  f"Expected 25, got {ret}")
        except Exception as e:
            console.print(f"[red]KO (Crash on '25')[/red]")
            self.record_error(exercise_label, "Crash", str(e))

        # Invalid: non-numeric
        try:
            func("abc")
            console.print("[green]OK ('abc' — Handled)[/green]")
        except ValueError:
            console.print("[green]OK ('abc' — Raised ValueError)[/green]")
        except Exception as e:
            console.print(f"[red]KO ('abc')[/red]")
            self.record_error(exercise_label, "Wrong Error", f"Expected ValueError, got {type(e).__name__}")

        # Out of range: too hot (>40)
        try:
            func("100")
            console.print("[red]KO ('100' — No exception raised)[/red]")
            self.record_error(exercise_label, "Missing Raise",
                              "100°C should raise an exception (max 40°C)")
        except (ValueError, Exception):
            console.print("[green]OK (100°C — Rejected)[/green]")

        # Out of range: too cold (<0)
        try:
            func("-50")
            console.print("[red]KO ('-50' — No exception raised)[/red]")
            self.record_error(exercise_label, "Missing Raise",
                              "-50°C should raise an exception (min 0°C)")
        except (ValueError, Exception):
            console.print("[green]OK (-50°C — Rejected)[/green]")

        # Boundary: 0 and 40 should be valid
        for boundary in ["0", "40"]:
            try:
                ret = func(boundary)
                if ret == int(boundary):
                    console.print(f"[green]OK (Boundary: {boundary}°C)[/green]")
                else:
                    console.print(f"[red]KO (Boundary: {boundary}°C)[/red]")
            except Exception:
                console.print(f"[red]KO (Boundary: {boundary}°C — should be valid)[/red]")
                self.record_error(exercise_label, "Boundary Error",
                                  f"{boundary}°C is within valid range (0-40) and should not raise")

        # Script execution
        output = self._run_script(path)
        if self.check_for_crash(output, exercise_label): return
        if "=== Garden Temperature Checker ===" in output:
            console.print("[green]OK (Script Execution)[/green]")
        else:
            console.print("[red]KO (Script Execution)[/red]")
            self.record_error(exercise_label, "Script Output",
                              f"Expected '=== Garden Temperature Checker ==='\nGot:\n{output}")

    def test_different_errors(self):
        console.print("\n[bold]Testing Exercise 2: ft_different_errors[/bold]")
        exercise_label = "Exercise 2"
        mod, path = self._load_module("ft_different_errors", exercise_label)
        if not mod: return

        # v3.0: authorized print(), open(), int()
        if not self.verify_strict(path, exercise_label, ["print", "open", "int"],
                                  allowed_imports=["sys"], enforce_try_except=True):
            return

        if not hasattr(mod, "garden_operations"):
            console.print("[red]KO[/red]")
            self.record_error(exercise_label, "Missing Function", "garden_operations() not found")
            return

        if not hasattr(mod, "test_error_types"):
            console.print("[red]KO (Missing Test Function)[/red]")
            self.record_error(exercise_label, "Structure Error",
                              "Missing mandatory function 'test_error_types()'")
            return

        # v3.0: garden_operations(operation_number) with int 0-3
        # 0→ValueError, 1→ZeroDivisionError, 2→FileNotFoundError, 3→TypeError
        expected_errors = {
            0: "ValueError",
            1: "ZeroDivisionError",
            2: "FileNotFoundError",
            3: "TypeError",
        }

        for op_num, expected_error in expected_errors.items():
            try:
                mod.garden_operations(op_num)
                # If it doesn't raise, it should be caught internally — check output
                console.print(f"[green]OK (op {op_num} — Handled)[/green]")
            except Exception as e:
                # The function may intentionally raise, which is fine
                if type(e).__name__ == expected_error:
                    console.print(f"[green]OK (op {op_num} — Raised {expected_error})[/green]")
                else:
                    console.print(f"[red]KO (op {op_num})[/red]")
                    self.record_error(exercise_label, "Wrong Error",
                                      f"Op {op_num}: Expected {expected_error}, got {type(e).__name__}")

        # Edge: operation 4 should complete successfully
        try:
            mod.garden_operations(4)
            console.print("[green]OK (op 4 — No error)[/green]")
        except Exception as e:
            console.print(f"[red]KO (op 4 — Should succeed)[/red]")
            self.record_error(exercise_label, "Unexpected Error",
                              f"Operation 4 should complete without error.\nGot: {e}")

        # Script execution
        output = self._run_script(path)
        if self.check_for_crash(output, exercise_label): return

        if "=== Garden Error Types Demo ===" not in output:
            console.print("[red]KO (Missing Header)[/red]")
            self.record_error(exercise_label, "Output Error",
                              "Missing header: '=== Garden Error Types Demo ==='")
        else:
            required = ["ValueError", "ZeroDivisionError", "FileNotFoundError", "TypeError"]
            missing = [r for r in required if r not in output]
            if not missing:
                console.print("[green]OK (Script Execution)[/green]")
            else:
                console.print("[red]KO (Script Execution)[/red]")
                self.record_error(exercise_label, "Script Output",
                                  f"Missing error types in output: {missing}")

    def test_custom_errors(self):
        console.print("\n[bold]Testing Exercise 3: ft_custom_errors[/bold]")
        exercise_label = "Exercise 3"
        mod, path = self._load_module("ft_custom_errors", exercise_label)
        if not mod: return

        if not self.verify_strict(path, exercise_label, ["print"],
                                  allowed_imports=["sys"], enforce_try_except=True):
            return

        # Check classes
        classes = ["GardenError", "PlantError", "WaterError"]
        for c in classes:
            if not hasattr(mod, c):
                console.print(f"[red]KO ({c} missing)[/red]")
                self.record_error(exercise_label, "Missing Class", f"{c} is missing")
                return

        try:
            GardenError = getattr(mod, "GardenError")
            PlantError = getattr(mod, "PlantError")
            WaterError = getattr(mod, "WaterError")

            if not issubclass(GardenError, Exception):
                console.print("[red]KO (Inheritance)[/red]")
                self.record_error(exercise_label, "Inheritance Error",
                                  "GardenError must inherit from Exception")
                return
            if not issubclass(PlantError, GardenError):
                console.print("[red]KO (Inheritance)[/red]")
                self.record_error(exercise_label, "Inheritance Error",
                                  "PlantError must inherit from GardenError")
                return
            if not issubclass(WaterError, GardenError):
                console.print("[red]KO (Inheritance)[/red]")
                self.record_error(exercise_label, "Inheritance Error",
                                  "WaterError must inherit from GardenError")
                return

            console.print("[green]OK (Classes Valid)[/green]")

            # v3.0: Check default messages
            try:
                pe = PlantError()
                if "plant" in str(pe).lower() or "unknown" in str(pe).lower():
                    console.print("[green]OK (Default Message: PlantError)[/green]")
                else:
                    console.print("[yellow]Warning: PlantError default message may not match v3.0[/yellow]")
            except TypeError:
                pass  # May require args

        except Exception as e:
            console.print("[red]KO[/red]")
            self.record_error(exercise_label, "Check Error", str(e))

        # v3.0: catching GardenError should catch PlantError and WaterError
        output = self._run_script(path)
        if self.check_for_crash(output, exercise_label): return
        if "=== Custom Garden Errors Demo ===" not in output:
            console.print("[red]KO (Missing Header)[/red]")
            self.record_error(exercise_label, "Output Error",
                              "Missing header: '=== Custom Garden Errors Demo ==='")
        elif "PlantError" in output and "WaterError" in output:
            # v3.0: must also show "catching all garden errors"
            if "catching all garden errors" in output.lower() or "GardenError" in output:
                console.print("[green]OK (Script Execution)[/green]")
            else:
                console.print("[green]OK (Script Execution — partial)[/green]")
        else:
            console.print("[red]KO (Script Execution)[/red]")
            self.record_error(exercise_label, "Script Output",
                              "Running script did not show PlantError/WaterError demos.")

    def test_finally_block(self):
        console.print("\n[bold]Testing Exercise 4: ft_finally_block[/bold]")
        exercise_label = "Exercise 4"
        mod, path = self._load_module("ft_finally_block", exercise_label)
        if not mod: return

        # v3.0: authorized print(), str.capitalize()
        if not self.verify_strict(path, exercise_label, ["print", "str"],
                                  allowed_imports=["sys"], enforce_try_except=True):
            return

        # v3.0: water_plant(plant_name) — singular, not water_plants(list)
        if not hasattr(mod, "water_plant"):
            # Fallback: accept old name water_plants
            if hasattr(mod, "water_plants"):
                console.print("[yellow]Warning: Found 'water_plants' — v3.0 expects 'water_plant(plant_name)'[/yellow]")
            else:
                self.record_error(exercise_label, "Missing Function",
                                  "water_plant(plant_name) not found.\n"
                                  "v3.0 requires this function (singular, takes a plant name string).")
                console.print("[red]KO (Missing water_plant)[/red]")
                return

        if not hasattr(mod, "test_watering_system"):
            self.record_error(exercise_label, "Missing Test Function",
                              "test_watering_system() not found")
            console.print("[red]KO (Missing Test Function)[/red]")
            return

        # Script execution — v3.0 specific output
        output = self._run_script(path)
        if self.check_for_crash(output, exercise_label): return

        if "=== Garden Watering System ===" not in output:
            console.print("[red]KO (Missing Header)[/red]")
            self.record_error(exercise_label, "Output Error",
                              "Missing header: '=== Garden Watering System ==='")
            return

        # v3.0: "Closing watering system" must always appear (finally block)
        if "Closing watering system" not in output:
            console.print("[red]KO (No Cleanup)[/red]")
            self.record_error(exercise_label, "Finally Block",
                              "'Closing watering system' not found — finally block not working")
            return

        # v3.0: valid plants are capitalized ("Tomato"), invalid are lowercase ("lettuce")
        # Check for OK markers and PlantError
        has_ok = "[OK]" in output or "Watering" in output
        has_error = "PlantError" in output or "Invalid plant" in output.lower() or "Error" in output

        if has_ok and has_error:
            console.print("[green]OK (Script Execution)[/green]")
        elif has_ok:
            console.print("[yellow]OK (Valid plants work, but no error case shown)[/yellow]")
        else:
            console.print("[red]KO (Script Execution)[/red]")
            self.record_error(exercise_label, "Script Output",
                              f"Expected watering + error handling output.\nGot:\n{output}")
