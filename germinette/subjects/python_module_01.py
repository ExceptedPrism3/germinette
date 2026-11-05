from germinette.core import BaseTester
from germinette.utils import IOTester
from rich.console import Console
from rich.panel import Panel
import importlib.util
import ast
import builtins
import sys
import os
import inspect
import contextlib
import io

console = Console()

class Tester(BaseTester):
    def __init__(self):
        super().__init__()
        self.title = "[bold blue]Testing Module 01: Code Cultivation (v3.2)[/bold blue]"
        self.exercises = [
            ("ft_garden_intro", self.test_garden_intro),
            ("ft_garden_data", self.test_garden_data),
            ("ft_plant_growth", self.test_plant_growth),
            ("ft_plant_factory", self.test_plant_factory),
            ("ft_garden_security", self.test_garden_security),
            ("ft_plant_types", self.test_plant_types),
            ("ft_garden_analytics", self.test_garden_analytics),
        ]

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

            type_hint_errors = self.check_type_hints(found_path)
            if type_hint_errors:
                 console.print("[red]KO[/red]")
                 self.record_error(exercise_label, "Style Error (Missing Type Hints)", type_hint_errors)
                 return None, None

            static_sanity = self._static_sanity_checks(found_path)
            if static_sanity:
                 console.print("[red]KO[/red]")
                 self.record_error(exercise_label, "Static Sanity Error", static_sanity)
                 return None, None

            return mod, found_path
        except Exception as e:
            console.print("[red]KO (Import Error)[/red]")
            self.record_error(exercise_label, "Import Error", str(e))
            return None, None

    def _static_sanity_checks(self, path):
        """
        Reject builtins accidentally passed as plant values to super().__init__.
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=path)
        except Exception as e:
            return f"AST parse failed: {e}"

        builtin_names = set(dir(builtins))
        violations = []

        # 1) Builtin misuse in super().__init__(...)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if not isinstance(func, ast.Attribute) or func.attr != "__init__":
                continue
            owner = func.value
            if not isinstance(owner, ast.Call):
                continue
            if not isinstance(owner.func, ast.Name) or owner.func.id != "super":
                continue

            for arg in node.args:
                if isinstance(arg, ast.Name) and arg.id in builtin_names:
                    violations.append(
                        f"Line {node.lineno}: suspicious builtin '{arg.id}' passed to super().__init__(...)"
                    )

        if violations:
            return "\n".join(violations)
        return None

    # Credit to @eloiberlinger1 (GitHub PR #2) for improving Module 01 error handling and class/method validation!
    def test_garden_intro(self):
        console.print("\n[bold]Testing Exercise 0: ft_garden_intro[/bold]")
        label = "Exercise 0"
        mod, path = self._load_module("ft_garden_intro", label)
        if not path: return

        try:
            output = self._run_script(path)
            if self.check_for_crash(output, label): return

            # v3.2: Must use if __name__ == "__main__": pattern
            # Output should include plant info (name, height, age)
            with open(path, "r") as f:
                source = f.read()

            tree = ast.parse(source)
            has_main = any(
                isinstance(node, ast.If)
                and isinstance(node.test, ast.Compare)
                and isinstance(node.test.left, ast.Name)
                and node.test.left.id == "__name__"
                and len(node.test.ops) == 1
                and isinstance(node.test.ops[0], ast.Eq)
                and len(node.test.comparators) == 1
                and isinstance(node.test.comparators[0], ast.Constant)
                and node.test.comparators[0].value == "__main__"
                for node in tree.body
            )
            if not has_main:
                console.print("[red]KO[/red]")
                self.record_error(label, "Missing Pattern",
                                  "Your script must use the 'if __name__ == \"__main__\":' pattern.\n"
                                  "This is required by the subject.")
                return

            if not output.strip():
                self.record_error(label, "Output Mismatch", "Display the plant name, height and age.")
                return

            console.print("[green]OK[/green]")
        except Exception as e:
            console.print("[red]KO[/red]")
            self.record_error(label, "Execution Error", str(e))

    # Credit to @zoeleu (GitHub Issue #20) for reporting unparameterized Plant class construction support in Ex1/Ex2!
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

            # v3.2: Plant class must have show() method.
            # Support both parameterized and unparameterized Plant instantiation
            try:
                p = Plant("Test", 10, 5)
            except TypeError:
                try:
                    p = Plant()
                except TypeError:
                    p = Plant.__new__(Plant)

            if not hasattr(p, 'show') and not hasattr(Plant, 'show'):
                self.record_error(label, "Missing Method",
                                  "Plant class must have a 'show()' method.\n"
                                  "The subject requires show() to display plant information.")
                console.print("[red]KO[/red]")
                return

            # Run script to catch runtime errors and verify output
            output = self._run_script(path)
            if self.check_for_crash(output, label): return

            # v3.2 expects at least 3 plants displayed.
            # Format: "Name: Xcm, Y days old"
            line_count = 0
            for line in output.strip().split("\n"):
                if "cm" in line and "days old" in line:
                    line_count += 1

            if line_count < 3:
                self.record_error(label, "Insufficient Plants",
                                  f"Expected at least 3 plants displayed. Found {line_count} plant lines.\n"
                                  f"Output:\n{output}")
                console.print("[red]KO[/red]")
                return

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

            try:
                p = Plant("Bamboo", 100, 10)
            except TypeError:
                try:
                    p = Plant()
                    p.name = "Bamboo"
                    p.height = 100
                    p.plant_age = 10
                except TypeError:
                    p = Plant.__new__(Plant)
                    p.name = "Bamboo"
                    p.height = 100
                    p.plant_age = 10
            
            # v3.2: requires grow() and age() methods; show() instead of get_info()
            missing = []
            if not callable(getattr(Plant, 'grow', None)): missing.append('grow')
            if not callable(getattr(Plant, 'age', None)): missing.append('age')
            if not hasattr(p, 'show') and not hasattr(Plant, 'show'):
                # Accept get_info as fallback for backwards compat
                if not hasattr(p, 'get_info') and not hasattr(Plant, 'get_info'):
                    missing.append('show (or get_info)')

            if missing:
                self.record_error(label, "Missing Methods", f"Missing required methods: {', '.join(missing)}")
                console.print("[red]KO[/red]")
                return

            # Check output for Day 1-7 simulation
            output = self._run_script(path)
            if self.check_for_crash(output, label): return

            if "Day 1" not in output or "Day 7" not in output:
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
            if self.check_for_crash(output, label): return

            Plant = getattr(mod, "Plant", None)
            if not inspect.isclass(Plant):
                self.record_error(label, "Missing Class", "Plant must be a class.")
                return
            plant = Plant("Test", 10, 5)
            if not callable(getattr(plant, "show", None)):
                self.record_error(label, "Missing Method", "Plant must have show().")
                return
            if sum("cm" in line and "days" in line for line in output.splitlines()) < 5:
                self.record_error(label, "Insufficient Plants", "Display at least five initialized plants.")
                return

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
            # v3.2 says improve Plant class, not create SecurePlant
            # Accept both for backwards compatibility
            PlantClass = getattr(mod, 'Plant', None)
            class_name = 'Plant'
            if not PlantClass:
                PlantClass = getattr(mod, 'SecurePlant', None)
                class_name = 'SecurePlant'
            if not PlantClass:
                self.record_error(label, "Missing Class",
                                  "Neither 'Plant' nor 'SecurePlant' class found.\n"
                                  "The v3.2 subject requires improving the Plant class with encapsulation.")
                console.print("[red]KO[/red]")
                return

            # Check required accessor methods
            p = PlantClass("Test", 10, 1)
            req_methods = ['set_height', 'set_age', 'get_height', 'get_age']
            missing = [m for m in req_methods if not hasattr(p, m)]
            
            if missing:
                self.record_error(label, "Missing Methods",
                                  f"Missing required accessor methods on {class_name}: {missing}")
                console.print("[red]KO[/red]")
                return

            for setter, getter in ((p.set_height, p.get_height), (p.set_age, p.get_age)):
                setter(0)
                if getter() != 0:
                    self.record_error(label, "Security Error", "Zero is a valid height or age.")
                    return
                setter(20)
                if getter() != 20:
                    self.record_error(label, "Security Error", "Valid updates must be stored.")
                    return
                captured = io.StringIO()
                with contextlib.redirect_stdout(captured):
                    setter(-1)
                if getter() != 20 or not captured.getvalue().strip():
                    self.record_error(label, "Security Error", "Reject negative values with an error message and preserve existing data.")
                    return
            instance_vars = vars(p)
            if not any(key.startswith("_") for key in instance_vars) or any(
                key.startswith(f"_{class_name}__") for key in instance_vars
            ):
                self.record_error(label, "Encapsulation Error", "Use protected attributes (_name), not name mangling (__name).")
                return

            # Run script to check validation messages
            output = self._run_script(path)
            if self.check_for_crash(output, label): return

            # v3.2 error format: "Rose: Error, height can't be negative"
            # Accept both old and new error messages
            has_rejection = False
            rejection_patterns = [
                "error" in output.lower() and "negative" in output.lower(),
                "rejected" in output.lower(),
                "can't be negative" in output.lower(),
            ]
            has_rejection = any(rejection_patterns)

            if not has_rejection:
                 self.record_error(label, "Security Error",
                                   "Expected error/rejection message when setting negative values.\n"
                                   "v3.2 format: 'Rose: Error, height can't be negative'")
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
            # Check classes exist
            for cls_name in ['Flower', 'Tree', 'Vegetable']:
                if not hasattr(mod, cls_name):
                    self.record_error(label, "Missing Class", f"Missing class '{cls_name}'")
                    console.print("[red]KO[/red]")
                    return

            Flower = mod.Flower
            Tree = mod.Tree
            Vegetable = mod.Vegetable

            # Check inheritance — all should inherit from Plant
            Plant = getattr(mod, 'Plant', None)
            if not inspect.isclass(Plant):
                self.record_error(label, 'Missing Class', 'Plant class is required.')
                return
            if Plant:
                for cls, name in [(Flower, "Flower"), (Tree, "Tree"), (Vegetable, "Vegetable")]:
                    if not issubclass(cls, Plant):
                        self.record_error(label, "Inheritance Error",
                                          f"'{name}' must inherit from 'Plant'")
                        console.print("[red]KO[/red]")
                        return

            # Check required methods
            f = Flower("Test", 1, 1, "Red")
            if not hasattr(f, 'bloom'):
                 self.record_error(label, "Missing Method", "Flower missing 'bloom()'")
                 console.print("[red]KO[/red]")
                 return

            t = Tree("Test", 100, 10, 50)
            if not hasattr(t, 'produce_shade'):
                 self.record_error(label, "Missing Method", "Tree missing 'produce_shade()'")
                 console.print("[red]KO[/red]")
                 return

            v = Vegetable("Tomato", 5, 10, "April")
            def nutrition():
                return getattr(v, "nutritional_value", getattr(v, "_nutritional_value", None))
            if nutrition() != 0:
                self.record_error(label, "Nutrition Error", "Vegetable nutritional value must start at zero.")
                return
            for method in (v.age, v.grow):
                before = nutrition()
                parameters = inspect.signature(method).parameters
                method(*([1] if parameters else []))
                if nutrition() is None or nutrition() <= before:
                    self.record_error(label, "Nutrition Error", "Vegetable age() and grow() must increase nutritional value.")
                    return

            # Verify script execution
            output = self._run_script(path)
            if self.check_for_crash(output, label): return

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
            Plant = getattr(mod, "Plant", None)
            Flower = getattr(mod, "Flower", None)
            Seed = getattr(mod, "Seed", None)
            if not all(inspect.isclass(cls) for cls in (Plant, Flower, Seed)):
                self.record_error(label, "Missing Class", "Plant, Flower and Seed classes are required.")
                return
            if not issubclass(Seed, Flower):
                self.record_error(label, "Inheritance Error", "Seed must inherit from Flower.")
                return
            static = [getattr(Plant, name) for name in dir(Plant)
                      if isinstance(inspect.getattr_static(Plant, name), staticmethod)]
            if not any(method(30) is False and method(365) is False and method(400) is True
                       for method in static if len(inspect.signature(method).parameters) == 1):
                self.record_error(label, "Static Method Error", "Plant needs a static method checking whether an age is older than a year.")
                return
            class_methods = [getattr(Plant, name) for name in dir(Plant)
                             if isinstance(inspect.getattr_static(Plant, name), classmethod)]
            if not class_methods:
                self.record_error(label, "Class Method Error", "Plant needs an anonymous plant class method.")
                return
            nested = [value for value in vars(Plant).values() if inspect.isclass(value)]
            if not nested:
                self.record_error(label, "Statistics Error", "Plant needs a nested statistics class.")
                return
            functions = [value for value in vars(mod).values()
                         if inspect.isfunction(value) and value.__module__ == mod.__name__]
            if not functions:
                self.record_error(label, "Statistics Error", "A standalone statistics display function is required.")
                return

            # Run script and check for expected output sections
            output = self._run_script(path)
            if self.check_for_crash(output, label): return

            # v3.2 expects: year-old check, flower stats, tree stats with shade, seed, anonymous
            # Accept both old and new output formats
            checks = 0
            if "Stats:" in output or "Garden scores" in output:
                checks += 1
            if "True" in output or "False" in output:
                checks += 1
            if "Anonymous" in output or "Unknown plant" in output or "Total gardens" in output:
                checks += 1

            if checks < 2:
                self.record_error(label, "Output Error",
                                  "Missing expected analytics sections in output.\n"
                                  "v3.2 expects: year check, stats display, anonymous plant.\n"
                                  f"Got:\n{output}")
                console.print("[red]KO[/red]")
                return

            console.print("[green]OK[/green]")
        except Exception as e:
            console.print("[red]KO[/red]")
            self.record_error(label, "Execution Error", str(e))
