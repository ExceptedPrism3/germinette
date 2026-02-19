from germinette.core import BaseTester
from germinette.utils import IOTester
from rich.console import Console
from rich.panel import Panel
import importlib
import importlib.util
import sys
import os

console = Console()
import inspect
import traceback

class Tester(BaseTester):
    def __init__(self):
        self.exercises = [
            ("ft_hello_garden", self.test_hello_garden),
            ("ft_plot_area", self.test_plot_area),
            ("ft_harvest_total", self.test_harvest_total),
            ("ft_plant_age", self.test_plant_age),
            ("ft_water_reminder", self.test_water_reminder),
            ("ft_count_harvest", self.test_count_harvest),
            ("ft_garden_summary", self.test_garden_summary),
            ("ft_seed_inventory", self.test_seed_inventory),
        ]
        self.grouped_errors = {}

    def record_error(self, exercise_label, error_type, message):
        """Records an error grouped by exercise label."""
        if exercise_label not in self.grouped_errors:
            self.grouped_errors[exercise_label] = []
        self.grouped_errors[exercise_label].append(f"[bold]{error_type}[/bold]\n{message}")

    def run(self, exercise_name=None):
        console.print("[bold blue]Testing Module 00: Growing Code[/bold blue]")
        
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
        
        # Display grouped errors
        if self.grouped_errors:
            console.print()
            console.rule("[bold red]Detailed Error Report[/bold red]")
            console.print()
            for label, messages in self.grouped_errors.items():
                # Join multiple errors for the same exercise with a separator
                content = "\n\n[dim]────────────────────────────────[/dim]\n\n".join(messages)
                console.print(Panel(content, title=f"[bold red]{label}[/bold red]", border_style="red", expand=False))
                console.print()

    def _load_func(self, module_name, exercise_label="Unknown Exercise", func_name=None):
        if not func_name:
            func_name = module_name
        
        # Determine base directory: prefer "python_module_00" if it exists in CWD
        cwd = os.getcwd()
        if os.path.exists(os.path.join(cwd, "python_module_00")):
            base_dir = os.path.join(cwd, "python_module_00")
        else:
            base_dir = cwd

        # Validate directory existence if exercise number can be parsed
        expected_dir = None
        try:
            # Extract number from "Exercise 7"
            ex_num = int(exercise_label.split()[-1])
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
                        f"[bold]Please ensure the exercise folder exists and follows strictly 'exXX' naming (e.g., ex7, not ex07).[/bold]")
                 self.record_error(exercise_label, "Missing Directory", msg)
                 return None

        except ValueError:
            pass # Could not parse exercise number

        # Search for file
        search_paths = [base_dir]
        if expected_dir:
            search_paths.append(expected_dir)
        else:
             # Fallback to scanning all if parsing failed
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
             console.print("[red]KO[/red]")
             msg = (f"[bold red]File not found[/bold red]\n\n"
                    f"Expected: [cyan]{target_file}[/cyan]\n"
                    f"Directory: [cyan]{expected_dir if expected_dir else 'scanned directories'}[/cyan]\n\n"
                    f"[bold]Please ensure the file exists and is named correctly.[/bold]")
             self.record_error(exercise_label, "Missing File", msg)
             return None

        try:
            console.print(f"[dim]Debug: Loading {found_path} as {module_name}[/dim]")
            spec = importlib.util.spec_from_file_location(module_name, found_path)
            if spec is None:
                console.print("[red]Spec is None![/red]")
                raise ImportError(f"Could not create spec for {found_path}")
            
            mod = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = mod
            spec.loader.exec_module(mod)
            
            func = getattr(mod, func_name)
            
            
            # Check Style
            style_errors = self.check_flake8(found_path)
            if style_errors:
                 console.print("[red]KO[/red]")
                 self.record_error(exercise_label, "Style Error", style_errors)
                 return None

            return func
        except ImportError as e:
            console.print("[red]KO[/red]")
            self.record_error(exercise_label, "Import Error", str(e))
            return None
        except AttributeError:
             console.print("[red]KO[/red]")
             debug_attrs = dir(mod) if 'mod' in locals() else "Module not loaded"
             console.print(f"[dim]Attributes in module: {debug_attrs}[/dim]")
             self.record_error(exercise_label, "Function Missing", f"Could not find function '{func_name}' in {found_path}")
             return None
        except Exception as e:
             console.print("[red]KO[/red]")
             self.record_error(exercise_label, "Error Loading Module", str(e))
             return None

    def test_hello_garden(self):
        console.print("\n[bold]Testing Exercise 0: ft_hello_garden[/bold]")
        exercise_label = "Exercise 0"
        func = self._load_func("ft_hello_garden", exercise_label)
        if not func: return

        try:
            output = IOTester.run_function(func)
            expected = "Hello, Garden Community!"
            success, msg = IOTester.assert_output(output, expected)
            if success:
                console.print("[green]OK[/green]")
            else:
                console.print(f"[red]KO[/red]")
                self.record_error(exercise_label, "Output Mismatch", msg)
        except Exception as e:
            console.print(f"[red]KO[/red]")
            self.record_error(exercise_label, "Runtime Error", traceback.format_exc())

    def test_plot_area(self):
        console.print("\n[bold]Testing Exercise 1: ft_plot_area[/bold]")
        exercise_label = "Exercise 1"
        func = self._load_func("ft_plot_area", exercise_label)
        if not func: return

        test_cases = [
            (["5", "3"], "15"),
            (["10", "10"], "100"),
            (["0", "5"], "0"),
            (["7", "2"], "14")
        ]

        for inputs, expected_part in test_cases:
            try:
                output = IOTester.run_function(func, inputs=inputs)
                if expected_part in output:
                    console.print(f"[green]OK ({inputs[0]}x{inputs[1]}={expected_part})[/green]")
                else:
                    console.print(f"[red]KO ({inputs[0]}x{inputs[1]}={expected_part})[/red]")
                    self.record_error(exercise_label, f"Failed Test Case (Input: {inputs})", f"Expected result: {expected_part}\nGot:\n{output}")
            except Exception as e:
                console.print(f"[red]KO[/red]")
                self.record_error(exercise_label, f"Runtime Error (Input: {inputs})", traceback.format_exc())

    def test_harvest_total(self):
        console.print("\n[bold]Testing Exercise 2: ft_harvest_total[/bold]")
        exercise_label = "Exercise 2"
        func = self._load_func("ft_harvest_total", exercise_label)
        if not func: return

        test_cases = [
            (["5", "8", "3"], "16"),
            (["0", "0", "0"], "0"),
            (["10", "20", "30"], "60"),
            (["1", "2", "3"], "6")
        ]

        for inputs, expected_sum in test_cases:
            try:
                output = IOTester.run_function(func, inputs=inputs)
                if f"Total harvest: {expected_sum}" in output or expected_sum in output:
                     console.print(f"[green]OK ({'+'.join(inputs)}={expected_sum})[/green]")
                else:
                     console.print(f"[red]KO ({'+'.join(inputs)}={expected_sum})[/red]")
                     self.record_error(exercise_label, f"Failed Test Case (Input: {inputs})", f"Expected 'Total harvest: {expected_sum}'\nGot:\n{output}")
            except Exception as e:
                console.print(f"[red]KO[/red]")
                self.record_error(exercise_label, f"Runtime Error (Input: {inputs})", traceback.format_exc())

    def test_plant_age(self):
        console.print("\n[bold]Testing Exercise 3: ft_plant_age[/bold]")
        exercise_label = "Exercise 3"
        func = self._load_func("ft_plant_age", exercise_label)
        if not func: return

        cases = [
            ("75", "Plant is ready to harvest!"),
            ("100", "Plant is ready to harvest!"),
            ("45", "Plant needs more time to grow."),
            ("12", "Plant needs more time to grow."),
            ("0", "Plant needs more time to grow.")
        ]

        for inp, expected in cases:
            try:
                output = IOTester.run_function(func, inputs=[inp])
                if expected.lower() in output.lower():
                     console.print(f"[green]OK ({inp})[/green]")
                else:
                     console.print(f"[red]KO ({inp})[/red]")
                     self.record_error(exercise_label, f"Failed Case (Input: {inp})", f"Input: {inp}\nExpected '{expected}'\nGot: {output}")
            except Exception as e:
                console.print(f"[red]KO[/red]")
                self.record_error(exercise_label, f"Runtime Error (Input: {inp})", traceback.format_exc())

    def test_water_reminder(self):
        console.print("\n[bold]Testing Exercise 4: ft_water_reminder[/bold]")
        exercise_label = "Exercise 4"
        func = self._load_func("ft_water_reminder", exercise_label)
        if not func: return
        
        cases = [
            ("4", "Water the plants!"),
            ("10", "Water the plants!"),
            ("2", "Plants are fine"),
            ("0", "Plants are fine")
        ]

        for inp, expected in cases:
            try:
                output = IOTester.run_function(func, inputs=[inp])
                if expected.lower() in output.lower():
                     console.print(f"[green]OK ({inp})[/green]")
                else:
                     console.print(f"[red]KO ({inp})[/red]")
                     self.record_error(exercise_label, f"Failed Case (Input: {inp})", f"Input: {inp}\nExpected '{expected}'\nGot: {output}")
            except Exception as e:
                console.print(f"[red]KO[/red]")
                self.record_error(exercise_label, f"Runtime Error (Input: {inp})", traceback.format_exc())

    def test_count_harvest(self):
        console.print("\n[bold]Testing Exercise 5: ft_count_harvest[/bold]")
        exercise_label = "Exercise 5"
        
        func1 = self._load_func("ft_count_harvest_iterative", exercise_label)
        if func1:
            cases = ["3", "1", "0", "5"]
            for inp in cases:
                try:
                    out = IOTester.run_function(func1, inputs=[inp])
                    # Build expected strict output
                    n = int(inp)
                    expected_lines = [f"Day {d}" for d in range(1, n + 1)]
                    expected_lines.append("Harvest time!")
                    
                    # Verify each line is present
                    missing = []
                    for line in expected_lines:
                        if line not in out:
                            missing.append(line)
                    
                    if not missing:
                        console.print(f"[green]Iterative OK ({inp} days)[/green]")
                    else:
                        console.print(f"[red]Iterative KO ({inp} days)[/red]")
                        self.record_error(exercise_label, f"Iterative Failed (Input: {inp})", f"Missing lines: {missing}\nGot:\n{out}")
                except Exception as e:
                     console.print(f"[red]Iterative KO[/red]")
                     self.record_error(exercise_label, f"Iterative Error (Input: {inp})", traceback.format_exc())

        func2 = self._load_func("ft_count_harvest_recursive", exercise_label)
        if func2:
            cases = ["3", "1", "0", "4"]
            for inp in cases:
                try:
                    out = IOTester.run_function(func2, inputs=[inp])
                    n = int(inp)
                    expected_lines = [f"Day {d}" for d in range(1, n + 1)]
                    expected_lines.append("Harvest time!")
                    
                    missing = []
                    for line in expected_lines:
                        if line not in out:
                            missing.append(line)
                            
                    if not missing:
                        console.print(f"[green]Recursive OK ({inp} days)[/green]")
                    else:
                        console.print(f"[red]Recursive KO ({inp} days)[/red]")
                        self.record_error(exercise_label, f"Recursive Failed (Input: {inp})", f"Missing lines: {missing}\nGot:\n{out}")
                except Exception as e:
                     console.print(f"[red]Recursive KO[/red]")
                     self.record_error(exercise_label, f"Recursive Error (Input: {inp})", traceback.format_exc())

    def test_garden_summary(self):
        console.print("\n[bold]Testing Exercise 6: ft_garden_summary[/bold]")
        exercise_label = "Exercise 6"
        func = self._load_func("ft_garden_summary", exercise_label)
        if not func: return

        test_cases = [
            (["MyGarden", "25"], ["Garden: MyGarden", "Plants: 25", "Status: Growing well!"]),
            (["SpaceFarm", "100"], ["Garden: SpaceFarm", "Plants: 100", "Status: Growing well!"]),
            (["SmallPlot", "0"], ["Garden: SmallPlot", "Plants: 0", "Status: Growing well!"])
        ]

        for inputs, checks in test_cases:
            try:
                out = IOTester.run_function(func, inputs=inputs)
                failed = False
                for c in checks:
                    if c not in out:
                        failed = True
                
                if failed:
                   console.print(f"[red]KO ({inputs})[/red]")
                   self.record_error(exercise_label, "Failed Test Case", f"Input: {inputs}\nExpected strings: {checks}\nGot:\n{out}")
                else:
                   console.print(f"[green]OK ({inputs[0]})[/green]")
            except Exception as e:
                console.print(f"[red]KO[/red]")
                self.record_error(exercise_label, "Runtime Error", traceback.format_exc())

    def test_seed_inventory(self):
        console.print("\n[bold]Testing Exercise 7: ft_seed_inventory[/bold]")
        exercise_label = "Exercise 7"
        func = self._load_func("ft_seed_inventory", exercise_label)
        if not func: return

        # Check Signature (Strict Type Hints)
        try:
            sig = inspect.signature(func)
            params = list(sig.parameters.items())
            
            # Expected: (seed_type: str, quantity: int, unit: str) -> None
            if len(params) != 3:
                console.print(f"[red]KO (Signature Mismatch)[/red]")
                self.record_error(exercise_label, "Signature Error", f"Expected 3 parameters, got {len(params)}.")
                return

            p1_name, p1 = params[0]
            p2_name, p2 = params[1]
            p3_name, p3 = params[2]

            if p1.annotation != str:
                console.print(f"[red]KO (Type Hint Error)[/red]")
                self.record_error(exercise_label, "Type Hint Error", f"Parameter '{p1_name}': Expected str, got {p1.annotation}")
                return
            if p2.annotation != int:
                console.print(f"[red]KO (Type Hint Error)[/red]")
                self.record_error(exercise_label, "Type Hint Error", f"Parameter '{p2_name}': Expected int, got {p2.annotation}")
                return
            if p3.annotation != str:
                console.print(f"[red]KO (Type Hint Error)[/red]")
                self.record_error(exercise_label, "Type Hint Error", f"Parameter '{p3_name}': Expected str, got {p3.annotation}")
                return
            
            if sig.return_annotation is not None and sig.return_annotation != None: # 'None' type
                # in python 3.10 match NoneType or strict None.
                # Just check string repr or strict.
                pass 

        except Exception as e:
             console.print(f"[red]KO (Signature Check Failed)[/red]")
             self.record_error(exercise_label, "Signature Check Error", str(e))
             return

        cases = [
            (("tomato", 15, "packets"), "Tomato seeds: 15 packets available"),
            (("pepper", 100, "packets"), "Pepper seeds: 100 packets available"),
            (("carrot", 8, "grams"), "Carrot seeds: 8 grams total"),
            (("pumpkin", 1000, "grams"), "Pumpkin seeds: 1000 grams total"),
            (("lettuce", 12, "area"), "Lettuce seeds: covers 12 square meters"),
            (("grass", 50, "area"), "Grass seeds: covers 50 square meters"),
            (("basil", 5, "unknown"), "Unknown unit type"),
            (("mint", 1, "bushels"), "Unknown unit type")
        ]

        for args, expected in cases:
            try:
                out = IOTester.run_function(func, args=args)
                out_clean = out.strip()
                expected_clean = expected.strip()
                is_valid_unit = args[2] in ["packets", "grams", "area"]
                
                if out_clean == expected_clean:
                    console.print(f"[green]OK ({args[0]})[/green]")
                else:
                    # Check if expected is present but output has extra content
                    has_expected = expected_clean in out_clean
                    has_unwanted = "Unknown unit type" in out_clean if is_valid_unit else False
                    
                    console.print(f"[red]KO ({args[0]})[/red]")
                    error_msg = f"Input: {args}\nExpected (exact): '{expected_clean}'\nGot:\n{out_clean}"
                    
                    if has_unwanted and is_valid_unit:
                        error_msg += "\n\n[bold red]Error: 'Unknown unit type' was incorrectly printed for a valid unit![/bold red]"
                    elif has_expected:
                        error_msg += "\n\n[bold red]Error: Output contains unexpected additional content.[/bold red]"
                    else:
                        error_msg += "\n\n[bold red]Error: Expected string not found in output.[/bold red]"
                    
                    self.record_error(exercise_label, f"Failed Case ({args[2]})", error_msg)
            except Exception as e:
                console.print(f"[red]KO[/red]")
                self.record_error(exercise_label, "Runtime Error", traceback.format_exc())
