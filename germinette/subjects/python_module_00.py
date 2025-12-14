from germinette.core import BaseTester
from germinette.utils import IOTester
from rich.console import Console
from rich.panel import Panel
import importlib
import sys
import os

console = Console()

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
            spec = importlib.util.spec_from_file_location(module_name, found_path)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = mod
            spec.loader.exec_module(mod)
            
            func = getattr(mod, func_name)
            return func
        except ImportError as e:
            console.print("[red]KO[/red]")
            self.record_error(exercise_label, "Import Error", str(e))
            return None
        except AttributeError:
             console.print("[red]KO[/red]")
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
            self.record_error(exercise_label, "Execution Error", str(e))

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
                self.record_error(exercise_label, f"Execution Error (Input: {inputs})", str(e))

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
                self.record_error(exercise_label, f"Execution Error (Input: {inputs})", str(e))

    def test_plant_age(self):
        console.print("\n[bold]Testing Exercise 3: ft_plant_age[/bold]")
        exercise_label = "Exercise 3"
        func = self._load_func("ft_plant_age", exercise_label)
        if not func: return

        cases = [
            ("75", "Plant is ready to harvest!"),
            ("100", "Plant is ready to harvest!"),
            ("45", "Plant needs more time to grow"),
            ("12", "Plant needs more time to grow"),
            ("0", "Plant needs more time to grow")
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
                self.record_error(exercise_label, f"Execution Error (Input: {inp})", str(e))

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
                self.record_error(exercise_label, f"Execution Error (Input: {inp})", str(e))

    def test_count_harvest(self):
        console.print("\n[bold]Testing Exercise 5: ft_count_harvest[/bold]")
        exercise_label = "Exercise 5"
        
        func1 = self._load_func("ft_count_harvest_iterative", exercise_label)
        if func1:
            cases = [
                ("3", ["Day 1", "Day 3", "Harvest time!"]),
                ("1", ["Day 1", "Harvest time!"]),
                ("0", ["Harvest time!"])
            ]
            for inp, must_have in cases:
                try:
                    out = IOTester.run_function(func1, inputs=[inp])
                    if all(x in out for x in must_have):
                        console.print(f"[green]Iterative OK ({inp} days)[/green]")
                    else:
                        console.print(f"[red]Iterative KO ({inp} days)[/red]")
                        self.record_error(exercise_label, f"Iterative Failed (Input: {inp})", f"Expected: {must_have}\nGot:\n{out}")
                except Exception as e:
                     console.print(f"[red]Iterative KO[/red]")
                     self.record_error(exercise_label, f"Iterative Error (Input: {inp})", str(e))

        func2 = self._load_func("ft_count_harvest_recursive", exercise_label)
        if func2:
            cases = [
                ("3", ["Day 1", "Day 3", "Harvest time!"]),
                ("1", ["Day 1", "Harvest time!"]),
                ("0", ["Harvest time!"])
            ]
            for inp, must_have in cases:
                try:
                    out = IOTester.run_function(func2, inputs=[inp])
                    if all(x in out for x in must_have):
                        console.print(f"[green]Recursive OK ({inp} days)[/green]")
                    else:
                        console.print(f"[red]Recursive KO ({inp} days)[/red]")
                        self.record_error(exercise_label, f"Recursive Failed (Input: {inp})", f"Expected: {must_have}\nGot:\n{out}")
                except Exception as e:
                     console.print(f"[red]Recursive KO[/red]")
                     self.record_error(exercise_label, f"Recursive Error (Input: {inp})", str(e))

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
                self.record_error(exercise_label, "Execution Error", str(e))

    def test_seed_inventory(self):
        console.print("\n[bold]Testing Exercise 7: ft_seed_inventory[/bold]")
        exercise_label = "Exercise 7"
        func = self._load_func("ft_seed_inventory", exercise_label)
        if not func: return
        
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
                if expected in out:
                     console.print(f"[green]OK ({args[0]})[/green]")
                else:
                     console.print(f"[red]KO ({args[0]})[/red]")
                     self.record_error(exercise_label, f"Failed Case ({args[2]})", f"Input: {args}\nExpected: '{expected}'\nGot:\n{out}")
            except Exception as e:
                console.print(f"[red]KO[/red]")
                self.record_error(exercise_label, "Execution Error", str(e))
