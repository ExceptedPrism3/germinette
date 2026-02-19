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
            ("ft_different_errors", self.test_different_errors),
            ("ft_custom_errors", self.test_custom_errors),
            ("ft_finally_block", self.test_finally_block),
            ("ft_raise_errors", self.test_raise_errors),
            ("ft_garden_management", self.test_garden_management),
        ]
        self.grouped_errors = {}

    def record_error(self, exercise_label, error_type, message):
        if exercise_label not in self.grouped_errors:
            self.grouped_errors[exercise_label] = []
        self.grouped_errors[exercise_label].append(f"[bold]{error_type}[/bold]\n{message}")

    def _load_module(self, module_name, exercise_label):
        # Determine base directory: prefer "python_module_02" if it exists in CWD
        cwd = os.getcwd()
        if os.path.exists(os.path.join(cwd, "python_module_02")):
            base_dir = os.path.join(cwd, "python_module_02")
        else:
            base_dir = cwd

        # Validate directory existence if exercise number can be parsed
        expected_dir = None
        try:
            # Extract number from "Exercise 7" (or just match generic exN)
            # Here we map exercise list to numbers manually or just check existence
            # Only checking strict ex0, ex1, etc.
            
            # Map module name to exercise number for simpler lookup
            ex_map = {
                "ft_first_exception": 0,
                "ft_different_errors": 1,
                "ft_custom_errors": 2,
                "ft_finally_block": 3,
                "ft_raise_errors": 4,
                "ft_garden_management": 5
            }
            if module_name in ex_map:
                ex_num = ex_map[module_name]
                expected_dirs = [f"ex{ex_num}"]
                
                dir_found = False
                for d in expected_dirs:
                    if os.path.exists(os.path.join(base_dir, d)):
                        dir_found = True
                        expected_dir = os.path.join(base_dir, d)
                        break
                
                if not dir_found:
                     console.print("[red]KO (Directory Missing)[/red]")
                     msg = (f"[bold red]Directory not found[/bold red]\n\n"
                            f"Expected directory: [cyan]{expected_dirs[0]}[/cyan]\n"
                            f"Location: {base_dir}\n\n"
                            f"[bold]Please ensure the exercise folder exists and follows strictly 'exXX' naming (e.g., ex0, not ex00).[/bold]")
                     self.record_error(exercise_label, "Missing Directory", msg)
                     return None, None

        except ValueError:
            pass 

        search_paths = [base_dir]
        if expected_dir:
            search_paths.append(expected_dir)
        else:
             # Fallback
             for i in range(10):
                ex_path = os.path.join(base_dir, f"ex{i}")
                if os.path.exists(ex_path):
                     search_paths.append(ex_path)

        target_file = f"{module_name}.py"
        found_path = None
        
        for path in search_paths:
            potential = os.path.join(path, target_file)
            if os.path.exists(potential):
                found_path = potential
                break
        
        if not found_path:
             console.print("[red]KO (Missing File)[/red]")
             msg = (f"[bold red]File not found[/bold red]\n\n"
                    f"Expected: [cyan]{target_file}[/cyan]\n"
                    f"Directory: [cyan]{expected_dir if expected_dir else 'scanned directories'}[/cyan]\n\n"
                    f"[bold]Please ensure the file exists and is named correctly.[/bold]")
             self.record_error(exercise_label, "Missing File", msg)
             return None, None

        try:
            spec = importlib.util.spec_from_file_location(module_name, found_path)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = mod
            spec.loader.exec_module(mod)
            # Check Style (Flake8)
            style_errors = self.check_flake8(found_path)
            if style_errors:
                 console.print("[red]KO[/red]")
                 self.record_error(exercise_label, "Style Error (Flake8)", style_errors)
                 return None, None
            

            
            # Check Type Hints (Mandatory in module 2)
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
        console.print("[bold blue]Testing Module 02: Garden Guardian[/bold blue]")
        
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

    def verify_strict(self, path, exercise_label, allowed_funcs):
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

    def test_first_exception(self):
        console.print("\n[bold]Testing Exercise 0: ft_first_exception[/bold]")
        exercise_label = "Exercise 0"
        mod, path = self._load_module("ft_first_exception", exercise_label)
        if not mod: return

        # Strict checks
        if not self.verify_strict(path, exercise_label, ["int", "print"]): return

        if not hasattr(mod, "check_temperature"):
            console.print("[red]KO (Function Missing)[/red]")
            self.record_error(exercise_label, "Missing Function", "check_temperature(temp_str) not found")
            return

        func = mod.check_temperature
        
        # Test cases
        # Good, Bad ("abc"), Extreme(100, -50)
        # Assuming function returns value on success, prints/returns error on failure?
        # Subject says "Returns the temperature if it's valid".
        # "Handles the case..." -> implies printing error or raising?
        # Example output shows "Error: ..." printed.
        
        cases = [
            ("25", 25, "OK"),
            ("abc", None, "must not return"), # Should print error
            ("100", None, "must not return"), # Too hot
            ("-50", None, "must not return"), # Too cold
            ("40", 40, "OK"),
            ("0", 0, "OK")
        ]
        
        all_ok = True
        for inp, expected_ret, desc in cases:
            try:
                # Capture output just in case they print
                ret = func(inp)
                
                if desc == "OK":
                    if ret == expected_ret:
                         console.print(f"[green]OK ({inp})[/green]")
                    else:
                         console.print(f"[red]KO ({inp})[/red]")
                         self.record_error(exercise_label, "Value Error", f"Input: {inp}\nExpected Return: {expected_ret}\nGot: {ret}")
                         all_ok = False
                else:
                    console.print(f"[green]OK ({inp} - Handled)[/green]")
                    
            except Exception as e:
                console.print(f"[red]KO (Crash: {inp})[/red]")
                self.record_error(exercise_label, "Crash", f"Input: {inp}\nException: {e}")
                all_ok = False

        # STRICTNESS CHECK: Run as script
        output = self._run_script(path)
        if self.check_for_crash(output, exercise_label): return
        if "Testing temperature" not in output or "Error:" not in output:
             console.print("[red]KO (Script Execution)[/red]")
             self.record_error(exercise_label, "Script Logic Error", "Running 'python3 ft_first_exception.py' did not produce expected output (Testing..., Error:...). Did you implement the test function?")
        else:
             console.print("[green]OK (Script Execution)[/green]")

    def test_different_errors(self):
        console.print("\n[bold]Testing Exercise 1: ft_different_errors[/bold]")
        exercise_label = "Exercise 1"
        mod, path = self._load_module("ft_different_errors", exercise_label)
        if not mod: return
        
        # Strict checks
        if not self.verify_strict(path, exercise_label, ["print", "open", "close"]): return
        
        if not hasattr(mod, "garden_operations"):
            console.print("[red]KO[/red]")
            self.record_error(exercise_label, "Missing Function", "garden_operations() not found")
            return
            
        if not hasattr(mod, "test_error_types"):
             console.print("[red]KO (Missing Test Function)[/red]")
             self.record_error(exercise_label, "Structure Error", "Missing mandatory function 'test_error_types()'")
             return

        # Test specific error cases
        cases = [
            ("value", "ValueError"),
            ("zero", "ZeroDivisionError"),
            ("file", "FileNotFoundError"),
            ("key", "KeyError")
        ]
        
        all_passed = True
        
        for arg, expected_error in cases:
            try:
                 output = IOTester.run_function(mod.garden_operations, args=(arg,))
                 if expected_error in output or f"Caught {expected_error}" in output:
                     console.print(f"[green]OK ({arg})[/green]")
                 else:
                     console.print(f"[red]KO ({arg})[/red]")
                     self.record_error(exercise_label, "Output Mismatch", f"Arg: '{arg}'\nExpected output containing: {expected_error}\nGot:\n{output}")
                     all_passed = False
            except TypeError as e:
                 console.print(f"[red]KO (Signature Error)[/red]")
                 self.record_error(exercise_label, "Signature Error", f"Function signature incorrect. Expected to accept arguments.\nError: {e}")
                 all_passed = False
                 break
            except Exception as e:
                 console.print(f"[red]KO (Crash: {arg})[/red]")
                 self.record_error(exercise_label, "Crash", f"Arg: '{arg}'\nException: {e}")
                 all_passed = False

        # Edge Case: Unknown argument
        try:
            output = IOTester.run_function(mod.garden_operations, args=("unknown",))
            # Should not crash. Output might be empty or generic.
            console.print("[green]OK (Edge Case: Unknown Arg)[/green]")
        except Exception as e:
            console.print("[red]KO (Edge Case: Unknown Arg)[/red]")
            self.record_error(exercise_label, "Crash", f"Arg: 'unknown'\nException: {e}")
            all_passed = False

        # STRICTNESS CHECK: Script execution
        # The script usually runs a demo of all cases.
        output = self._run_script(path)
        if self.check_for_crash(output, exercise_label): return
        required = ["ValueError", "ZeroDivisionError", "FileNotFoundError", "KeyError"]
        missing = [r for r in required if r not in output and r.lower() not in output.lower()]
        
        if "=== Garden Error Types Demo ===" not in output:
             console.print("[red]KO (Missing Header)[/red]")
             self.record_error(exercise_label, "Output Error", "Missing header: '=== Garden Error Types Demo ==='")
        elif not missing:
             console.print("[green]OK (Script Execution)[/green]")
        else:
             console.print("[red]KO (Script Execution)[/red]")
             self.record_error(exercise_label, "Script Output Mismatch", f"Running script failed to verify: {missing}")


    def test_custom_errors(self):
        console.print("\n[bold]Testing Exercise 2: ft_custom_errors[/bold]")
        exercise_label = "Exercise 2"
        mod, path = self._load_module("ft_custom_errors", exercise_label)
        if not mod: return

        if not self.verify_strict(path, exercise_label, ["print"]): return

        # Check classes
        classes = ["GardenError", "PlantError", "WaterError"]
        for c in classes:
            if not hasattr(mod, c):
                console.print(f"[red]KO ({c} missing)[/red]")
                self.record_error(exercise_label, "Missing Class", f"{c} is missing")
                return

        if not hasattr(mod, "test_custom_errors"):
             console.print("[red]KO (Missing Test Function)[/red]")
             self.record_error(exercise_label, "Structure Error", "Missing mandatory function 'test_custom_errors()'")
             return

        try:
            # Check inheritance
            GardenError = getattr(mod, "GardenError")
            PlantError = getattr(mod, "PlantError")
            WaterError = getattr(mod, "WaterError")
            
            if not issubclass(GardenError, Exception):
                console.print("[red]KO (Inheritance)[/red]")
                self.record_error(exercise_label, "Inheritance Error", "GardenError must inherit from Exception")
                return
            if not issubclass(PlantError, GardenError):
                console.print("[red]KO (Inheritance)[/red]")
                self.record_error(exercise_label, "Inheritance Error", "PlantError must inherit from GardenError")
                return
            if not issubclass(WaterError, GardenError):
                console.print("[red]KO (Inheritance)[/red]")
                self.record_error(exercise_label, "Inheritance Error", "WaterError must inherit from GardenError")
                return
                
            console.print("[green]OK (Classes Valid)[/green]")
        except Exception as e:
            console.print("[red]KO[/red]")
            self.record_error(exercise_label, "Check Error", str(e))

        # STRICTNESS CHECK
        output = self._run_script(path)
        if self.check_for_crash(output, exercise_label): return
        if "=== Custom Garden Errors Demo ===" not in output:
             console.print("[red]KO (Missing Header)[/red]")
             self.record_error(exercise_label, "Output Error", "Missing header: '=== Custom Garden Errors Demo ==='")
        elif "PlantError" in output and "WaterError" in output:
             console.print("[green]OK (Script Execution)[/green]")
        else:
             console.print("[red]KO (Script Execution)[/red]")
             self.record_error(exercise_label, "Script Output Mismatch", "Running script did not show custom error demonstrations.")

    def test_finally_block(self):
        console.print("\n[bold]Testing Exercise 3: ft_finally_block[/bold]")
        exercise_label = "Exercise 3"
        mod, path = self._load_module("ft_finally_block", exercise_label)
        if not mod: return

        if not self.verify_strict(path, exercise_label, ["print"]): return
        
        if not hasattr(mod, "water_plants"):
             self.record_error(exercise_label, "Missing Function", "water_plants not found")
             console.print("[red]KO (Missing water_plants)[/red]")
             return
        
        if not hasattr(mod, "test_watering_system"):
             self.record_error(exercise_label, "Missing Test Function", "test_watering_system() not found")
             console.print("[red]KO (Missing Test Function)[/red]")
             return
             
        # Check if 'finally' ensures cleanup
        # We can't strictly static check 'finally', but we can check output
        
        plants = ["tomato", "lettuce"]
        output = IOTester.run_function(mod.water_plants, args=(plants,))
        if "Closing watering system" in output:
             console.print("[green]OK (Cleanup confirmed)[/green]")
        else:
             console.print("[red]KO (Cleanup missing)[/red]")
             self.record_error(exercise_label, "Output Error", "Did not find 'Closing watering system' in output")

        # Error case
        output_err = IOTester.run_function(mod.water_plants, args=(["tomato", None],))
        if "Closing watering system" in output_err:
             console.print("[green]OK (Cleanup on error confirmed)[/green]")
        else:
             console.print("[red]KO (Cleanup on error missing)[/red]")
             self.record_error(exercise_label, "Output Error", "Did not find 'Closing watering system' after error")

        # Edge Case: Empty list
        output_empty = IOTester.run_function(mod.water_plants, args=([],))
        if "Closing watering system" in output_empty:
             console.print("[green]OK (Edge Case: Empty List)[/green]")
        else:
             console.print("[red]KO (Edge Case: Empty List)[/red]")
             self.record_error(exercise_label, "Output Error", "Did not find 'Closing watering system' for empty list")

        # STRICTNESS CHECK
        output = self._run_script(path)
        if self.check_for_crash(output, exercise_label): return
        if "=== Garden Watering System ===" not in output:
             console.print("[red]KO (Missing Header)[/red]")
             self.record_error(exercise_label, "Output Error", "Missing header: '=== Garden Watering System ==='")
        elif "Closing watering system" in output:
             console.print("[green]OK (Script Execution)[/green]")
        else:
             console.print("[red]KO (Script Execution)[/red]")
             self.record_error(exercise_label, "Script Output Mismatch", "Running script did not confirm 'Closing watering system' (finally block usage).")

    def test_raise_errors(self):
        console.print("\n[bold]Testing Exercise 4: ft_raise_errors[/bold]")
        exercise_label = "Exercise 4"
        mod, path = self._load_module("ft_raise_errors", exercise_label)
        if not mod: return

        if not self.verify_strict(path, exercise_label, ["print"]): return
        
        if not hasattr(mod, "check_plant_health"):
             console.print("[red]KO[/red]")
             return

        func = mod.check_plant_health
        
        # Test valid
        try:
            func("rose", 5, 5)
            console.print("[green]OK (Valid)[/green]")
        except Exception:
             console.print("[red]KO (Valid raised error)[/red]")
             
        # Test raises
        cases = [
            ("", 5, 5, "empty name"),
            ("rose", 15, 5, "water too high"),
            ("rose", 5, 0, "sun too low")
        ]
        
        for name, water, sun, desc in cases:
            try:
                func(name, water, sun)
                console.print(f"[red]KO ({desc} - No Raise)[/red]")
                self.record_error(exercise_label, "Missing Raise", f"Did not raise error for {desc}")
            except ValueError:
                console.print(f"[green]OK ({desc} - Raised ValueError)[/green]")
            except Exception as e:
                console.print(f"[red]KO ({desc} - Wrong Error Type)[/red]")
                self.record_error(exercise_label, "Wrong Error", f"Expected ValueError, got {type(e).__name__}")
        
        # STRICTNESS CHECK
        # Must verify test function exists
        if not hasattr(mod, "test_plant_checks"):
             console.print("[red]KO (Missing Test Function)[/red]")
             self.record_error(exercise_label, "Structure Error", "Missing mandatory function 'test_plant_checks()'")
             return

        output = self._run_script(path)
        if self.check_for_crash(output, exercise_label): return
        if "=== Garden Plant Health Checker ===" not in output:
             console.print("[red]KO (Missing Header)[/red]")
             self.record_error(exercise_label, "Output Error", "Missing header: '=== Garden Plant Health Checker ==='")
        elif "Error:" in output or "caught" in output.lower() or "Unexpected" in output:
             console.print("[green]OK (Script Execution)[/green]")
        else:
             console.print("[red]KO (Script Execution)[/red]")
             self.record_error(exercise_label, "Script Output Mismatch", "Running script did not show error handling output.")

    def test_garden_management(self):
        console.print("\n[bold]Testing Exercise 5: ft_garden_management[/bold]")
        exercise_label = "Exercise 5"
        mod, path = self._load_module("ft_garden_management", exercise_label)
        if not mod: return

        if not self.verify_strict(path, exercise_label, ["print"]): return
        
        if not hasattr(mod, "GardenManager"):
            console.print("[red]KO (Missing Class)[/red]")
            return
            
        try:
            gm = mod.GardenManager()
            if hasattr(gm, "add_plant") and hasattr(gm, "water_plants"):
                 console.print("[green]OK (Class Structure)[/green]")
            else:
                 console.print("[red]KO (Missing Methods)[/red]")
                 return

            # Functional Check: Add Plant (Valid)
            IOTester.run_function(gm.add_plant, args=("test_plant",))
            if "test_plant" in gm.plants:
                console.print("[green]OK (Functional: Add Plant)[/green]")
            else:
                console.print("[red]KO (Functional: Add Plant)[/red]")
                self.record_error(exercise_label, "Logic Error", "add_plant did not add to self.plants")

            # Functional Check: Use finally
            out_water = IOTester.run_function(gm.water_plants)
            if "Closing" in out_water:
                console.print("[green]OK (Functional: Water Plants)[/green]")
            else:
                console.print("[red]KO (Functional: Water Plants)[/red]")
                self.record_error(exercise_label, "Logic Error", "water_plants missing 'Closing' message")

        except Exception as e:
            console.print("[red]KO (Crash)[/red]")
            self.record_error(exercise_label, "Crash", str(e))

        # STRICTNESS CHECK
        if not hasattr(mod, "test_garden_management"):
             console.print("[red]KO (Missing Test Function)[/red]")
             self.record_error(exercise_label, "Structure Error", "Missing mandatory function 'test_garden_management()'")
             return

        output = self._run_script(path)
        if self.check_for_crash(output, exercise_label): return
        if "=== Garden Management System ===" not in output:
             console.print("[red]KO (Missing Header)[/red]")
             self.record_error(exercise_label, "Output Error", "Missing header: '=== Garden Management System ==='")
        elif "Watering" in output and "Error" in output:
             console.print("[green]OK (Script Execution)[/green]")
        else:
             console.print("[red]KO (Script Execution)[/red]")
             self.record_error(exercise_label, "Script Output Mismatch", "Running script did not show expected Garden Management flow (Watering, Errors).")
