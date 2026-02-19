from germinette.core import BaseTester
from germinette.utils import IOTester
from rich.console import Console
from rich.panel import Panel
import importlib.util
import sys
import os
import inspect

console = Console()

class Tester(BaseTester):
    def __init__(self):
        self.exercises = [
            ("ft_garden_intro", self.test_garden_intro),
            ("ft_garden_data", self.test_garden_data),
            ("ft_plant_growth", self.test_plant_growth),
            ("ft_plant_factory", self.test_plant_factory),
            ("ft_garden_security", self.test_garden_security),
            ("ft_plant_types", self.test_plant_types),
            ("ft_garden_analytics", self.test_garden_analytics),
        ]
        self.grouped_errors = {}

    def record_error(self, exercise_label, error_type, message):
        if exercise_label not in self.grouped_errors:
            self.grouped_errors[exercise_label] = []
        self.grouped_errors[exercise_label].append(f"[bold]{error_type}[/bold]\n{message}")

    def run(self, exercise_name=None):
        console.print("[bold blue]Testing Module 01: Garden Object Oriented Programming (v18)[/bold blue]")
        
        if os.getcwd() not in sys.path:
            sys.path.insert(0, os.getcwd())

        if exercise_name:
            found = False
            for name, func in self.exercises:
                if name == exercise_name or exercise_name.replace(".py", "") == name:
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

    def _load_module(self, module_name, exercise_label):
        cwd = os.getcwd()
        base_dir = os.path.join(cwd, "python_module_01") if os.path.exists(os.path.join(cwd, "python_module_01")) else cwd

        try:
            ex_num = int(exercise_label.split()[-1])
            expected_dir = os.path.join(base_dir, f"ex{ex_num}")
            
            if not os.path.exists(expected_dir):
                 console.print("[red]KO (Directory Missing)[/red]")
                 self.record_error(exercise_label, "Missing Directory", f"Expected directory: ex{ex_num}")
                 return None, None
        except ValueError:
            expected_dir = base_dir

        target_file = f"{module_name}.py"
        found_path = os.path.join(expected_dir, target_file)
        
        if not os.path.exists(found_path):
             console.print("[red]KO (Missing File)[/red]")
             self.record_error(exercise_label, "Missing File", f"Expected file: {found_path}")
             return None, None

        try:
            spec = importlib.util.spec_from_file_location(module_name, found_path)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = mod
            spec.loader.exec_module(mod)
            
            # Style Checks
            style_errors = self.check_flake8(found_path)
            if style_errors:
                 console.print("[red]KO[/red]")
                 self.record_error(exercise_label, "Style Error (Flake8)", style_errors)
                 return None, None


            
            return mod, found_path
        except Exception as e:
            console.print("[red]KO (Import Error)[/red]")
            self.record_error(exercise_label, "Import Error", str(e))
            return None, None

    def test_garden_intro(self):
        console.print("\n[bold]Testing Exercise 0: ft_garden_intro[/bold]")
        label = "Exercise 0"
        mod, path = self._load_module("ft_garden_intro", label)
        if not path: return

        try:
            output = self._run_script(path)
            # PDF v18: "Rose: 25cm, 30 days old" (approximate match required)
            if "Rose" not in output or "25cm" not in output:
                console.print("[red]KO[/red]")
                self.record_error(label, "Output Mismatch", f"Expected 'Rose' and '25cm' in output.\nGot:\n{output}")
                return
            
            console.print("[green]OK[/green]")
        except Exception as e:
            console.print("[red]KO[/red]")
            self.record_error(label, "Execution Error", str(e))

    def test_garden_data(self):
        console.print("\n[bold]Testing Exercise 1: ft_garden_data[/bold]")
        label = "Exercise 1"
        mod, path = self._load_module("ft_garden_data", label)
        if not path: return

        try:
            if not hasattr(mod, 'Plant'):
                self.record_error(label, "Missing Class", "Class 'Plant' not found.")
                console.print("[red]KO[/red]")
                return

            Plant = mod.Plant
            p = Plant("Test", 10, 5)
            
            console.print("[green]OK[/green]")
        except Exception as e:
            console.print("[red]KO[/red]")
            self.record_error(label, "Execution Error", str(e))

    def test_plant_growth(self):
        console.print("\n[bold]Testing Exercise 2: ft_plant_growth[/bold]")
        label = "Exercise 2"
        mod, path = self._load_module("ft_plant_growth", label)
        if not path: return

        try:
            Plant = getattr(mod, 'Plant', None)
            if not Plant:
                self.record_error(label, "Missing Class", "Class 'Plant' not found")
                console.print("[red]KO[/red]")
                return

            p = Plant("Bamboo", 100, 10)
            
            # PDF v18 Strict Requirements: grow(), age()
            # PDF v18: Methods not strictly named, just functionality via simulation.
            # missing = []
            # if not hasattr(p, 'grow'): missing.append('grow')
            # if not hasattr(p, 'age'): missing.append('age')
            # if not hasattr(p, 'get_info'): missing.append('get_info')
            
            # if missing:
            #     self.record_error(label, "Missing Methods", f"Missing required methods: {', '.join(missing)}")
            #     console.print("[red]KO[/red]")
            #     return

            # Check output for "=== Day 7 ===" simulation
            output = self._run_script(path)
            if "=== Day 1 ===" not in output or "=== Day 7 ===" not in output:
                 self.record_error(label, "Output Mismatch", "Expected simulation output (Day 1 to Day 7).")
                 console.print("[red]KO[/red]")
                 return

            console.print("[green]OK[/green]")
        except Exception as e:
            console.print("[red]KO[/red]")
            self.record_error(label, "Execution Error", str(e))

    def test_plant_factory(self):
        console.print("\n[bold]Testing Exercise 3: ft_plant_factory[/bold]")
        label = "Exercise 3"
        mod, path = self._load_module("ft_plant_factory", label)
        if not path: return

        try:
            output = self._run_script(path)
            required = ["=== Plant Factory Output ===", "Total plants created:"]
            
            for req in required:
                if req not in output:
                     self.record_error(label, "Output Mismatch", f"Missing required header/footer: '{req}'")
                     console.print("[red]KO[/red]")
                     return
            
            # PDF does not strictly enforce 5 instances.
            # if output.count("Created:") < 5:
            #      self.record_error(label, "Logic Error", "Expected at least 5 plants to be created.")
            #      console.print("[red]KO[/red]")
            #      return

            console.print("[green]OK[/green]")
        except Exception as e:
            console.print("[red]KO[/red]")
            self.record_error(label, "Execution Error", str(e))

    def test_garden_security(self):
        console.print("\n[bold]Testing Exercise 4: ft_garden_security[/bold]")
        label = "Exercise 4"
        mod, path = self._load_module("ft_garden_security", label)
        if not path: return

        try:
            SecurePlant = getattr(mod, 'SecurePlant', None)
            if not SecurePlant:
                self.record_error(label, "Missing Class", "Class 'SecurePlant' not found")
                console.print("[red]KO[/red]")
                return

            # Check Strict Methods (Getters not required)
            p = SecurePlant("Test", 10, 1)
            req_methods = ['set_height', 'set_age'] # , 'get_height', 'get_age'
            missing = [m for m in req_methods if not hasattr(p, m)]
            
            if missing:
                self.record_error(label, "Missing Methods", f"Missing required accessor methods: {missing}")
                console.print("[red]KO[/red]")
                return

            # Run script to check validation messages
            output = self._run_script(path)
            if "Security: Negative height rejected" not in output:
                 self.record_error(label, "Security Error", "Expected security rejection message in output.")
                 console.print("[red]KO[/red]")
                 return

            console.print("[green]OK[/green]")
        except Exception as e:
            console.print("[red]KO[/red]")
            self.record_error(label, "Execution Error", str(e))

    def test_plant_types(self):
        console.print("\n[bold]Testing Exercise 5: ft_plant_types[/bold]")
        label = "Exercise 5"
        mod, path = self._load_module("ft_plant_types", label)
        if not path: return

        try:
            # Check classes
            for cls_name in ['Flower', 'Tree', 'Vegetable']:
                if not hasattr(mod, cls_name):
                    self.record_error(label, "Missing Class", f"Missing class '{cls_name}'")
                    console.print("[red]KO[/red]")
                    return

            # Check Inheritance and Methods
            Flower = mod.Flower
            Tree = mod.Tree
            
            f = Flower("Test", 1, 1, "Red")
            t = Tree("Test", 100, 10, 50)
            
            # if not hasattr(f, 'bloom'):
            #      self.record_error(label, "Missing Method", "Flower missing 'bloom()'")
            #      console.print("[red]KO[/red]")
            #      return
            if not hasattr(t, 'produce_shade'):
                 self.record_error(label, "Missing Method", "Tree missing 'produce_shade()'")
                 console.print("[red]KO[/red]")
                 return

            console.print("[green]OK[/green]")
        except Exception as e:
            console.print("[red]KO[/red]")
            self.record_error(label, "Execution Error", str(e))

    def test_garden_analytics(self):
        console.print("\n[bold]Testing Exercise 6: ft_garden_analytics[/bold]")
        label = "Exercise 6"
        mod, path = self._load_module("ft_garden_analytics", label)
        if not path: return

        try:
            GardenManager = getattr(mod, 'GardenManager', None)
            if not GardenManager:
                self.record_error(label, "Missing Class", "GardenManager not found")
                console.print("[red]KO[/red]")
                return

            # Strict Nested Class Check
            if not hasattr(GardenManager, 'GardenStats') or not inspect.isclass(getattr(GardenManager, 'GardenStats')):
                 self.record_error(label, "Structure Error", "GardenStats must be a Nested Class inside GardenManager.")
                 console.print("[red]KO[/red]")
                 return

            output = self._run_script(path)
            if "Garden scores" not in output or "Total gardens managed" not in output:
                 self.record_error(label, "Output Error", "Missing analytics sections (scores/totals) in output.")
                 console.print("[red]KO[/red]")
                 return

            console.print("[green]OK[/green]")
        except Exception as e:
            console.print("[red]KO[/red]")
            self.record_error(label, "Execution Error", str(e))
