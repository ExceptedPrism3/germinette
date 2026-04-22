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
        console.print("[bold blue]Testing Module 01: Code Cultivation (v3.0)[/bold blue]")
        
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
        Catch common silent false positives:
        1) passing builtins (hex/list/str/...) as values into super().__init__(...)
        2) using self.<attr> names that were never assigned anywhere in the class
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

        # 2) Undefined self.<attr> usage in classes
        for cls in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
            # Only validate classes that define their own __init__.
            # Subclasses often read inherited attributes set by parent __init__.
            method_names = {
                n.name for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            }
            nested_class_names = {
                n.name for n in cls.body if isinstance(n, ast.ClassDef)
            }
            if "__init__" not in method_names:
                continue
            # If __init__ delegates to super().__init__(...), parent class owns
            # core attribute assignment (common in this module), so skip this
            # undefined-attribute heuristic for that class.
            has_super_init_call = False
            for node in cls.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "__init__":
                    for sub in ast.walk(node):
                        if not isinstance(sub, ast.Call):
                            continue
                        func = sub.func
                        if not isinstance(func, ast.Attribute) or func.attr != "__init__":
                            continue
                        if (
                            isinstance(func.value, ast.Call)
                            and isinstance(func.value.func, ast.Name)
                            and func.value.func.id == "super"
                        ):
                            has_super_init_call = True
                            break
                if has_super_init_call:
                    break
            if has_super_init_call:
                continue

            assigned = set()
            used = []

            for n in ast.walk(cls):
                if not isinstance(n, ast.Attribute):
                    continue
                if not isinstance(n.value, ast.Name) or n.value.id != "self":
                    continue
                if isinstance(n.ctx, ast.Store):
                    assigned.add(n.attr)
                elif isinstance(n.ctx, ast.Load):
                    used.append((n.attr, n.lineno))

            for attr, lineno in used:
                if attr in method_names or attr in nested_class_names:
                    continue
                if attr not in assigned:
                    violations.append(
                        f"Line {lineno}: self.{attr} is used but never assigned in class {cls.name}"
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

            # v3.0: Must use if __name__ == "__main__": pattern
            # Output should include plant info (name, height, age)
            with open(path, "r") as f:
                source = f.read()

            if '__name__' not in source or '__main__' not in source:
                console.print("[red]KO[/red]")
                self.record_error(label, "Missing Pattern",
                                  "Your script must use the 'if __name__ == \"__main__\":' pattern.\n"
                                  "This is required by the subject.")
                return

            # v3.0 PDF shows Rose, 25cm, 30 days as example — approximate match
            checks_found = 0
            for keyword in ["Plant:", "Height:", "Age:"]:
                if keyword in output:
                    checks_found += 1

            if checks_found < 2:
                # Fallback: check for the old-style format too
                if "Rose" not in output and "cm" not in output:
                    console.print("[red]KO[/red]")
                    self.record_error(label, "Output Mismatch",
                                      "Expected plant information in output (name, height, age).\n"
                                      f"Got:\n{output}")
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

            # v3.0: Plant class must have show() method.
            p = Plant("Test", 10, 5)
            if not hasattr(p, 'show'):
                self.record_error(label, "Missing Method",
                                  "Plant class must have a 'show()' method.\n"
                                  "The subject requires show() to display plant information.")
                console.print("[red]KO[/red]")
                return

            # Run script to catch runtime errors and verify output
            output = self._run_script(path)
            if self.check_for_crash(output, label): return

            # v3.0 expects at least 3 plants displayed.
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

            p = Plant("Bamboo", 100, 10)
            
            # v3.0: requires grow() and age() methods; show() instead of get_info()
            missing = []
            if not hasattr(p, 'grow'): missing.append('grow')
            if not hasattr(p, 'age'): missing.append('age')
            if not hasattr(p, 'show'):
                # Accept get_info as fallback for backwards compat
                if not hasattr(p, 'get_info'):
                    missing.append('show (or get_info)')

            if missing:
                self.record_error(label, "Missing Methods", f"Missing required methods: {', '.join(missing)}")
                console.print("[red]KO[/red]")
                return

            # Check output for Day 1-7 simulation
            output = self._run_script(path)
            if self.check_for_crash(output, label): return

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
            if self.check_for_crash(output, label): return

            # v3.0: expects "=== Plant Factory Output ===" header and at least 5 "Created:" lines
            if "=== Plant Factory Output ===" not in output:
                self.record_error(label, "Output Mismatch", "Missing required header: '=== Plant Factory Output ==='")
                console.print("[red]KO[/red]")
                return
            
            if output.count("Created:") < 5:
                 self.record_error(label, "Logic Error", "Expected at least 5 plants to be created (5 'Created:' lines).")
                 console.print("[red]KO[/red]")
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
            # v3.0 says improve Plant class, not create SecurePlant
            # Accept both for backwards compatibility
            PlantClass = getattr(mod, 'Plant', None)
            class_name = 'Plant'
            if not PlantClass:
                PlantClass = getattr(mod, 'SecurePlant', None)
                class_name = 'SecurePlant'
            if not PlantClass:
                self.record_error(label, "Missing Class",
                                  "Neither 'Plant' nor 'SecurePlant' class found.\n"
                                  "The v3.0 subject requires improving the Plant class with encapsulation.")
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

            # v3.0: check encapsulation uses _protected convention (not __mangling)
            instance_vars = vars(p)
            has_protected = any(k.startswith('_') and not k.startswith('__') for k in instance_vars)
            has_mangling = any(k.startswith(f'_{class_name}__') or k.startswith('__') and not k.startswith('__') and k.endswith('__') for k in instance_vars)
            
            if not has_protected and not has_mangling:
                console.print("[yellow]Warning: No protected attributes found (expected _ prefix convention)[/yellow]")

            # Run script to check validation messages
            output = self._run_script(path)
            if self.check_for_crash(output, label): return

            # v3.0 error format: "Rose: Error, height can't be negative"
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
                                   "v3.0 format: 'Rose: Error, height can't be negative'")
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

            # v3.0: Vegetable needs harvest_season and nutritional_value
            try:
                v = Vegetable("Tomato", 5, 10, "April")
                if not hasattr(v, 'harvest_season') and not hasattr(v, '_harvest_season'):
                    console.print("[yellow]Warning: Vegetable missing 'harvest_season' attribute[/yellow]")
            except TypeError:
                # Constructor might need different args, that's okay
                pass

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
            # v3.0: Plant class with static method, class method, nested stats
            # Also accept old GardenManager for backwards compat
            Plant = getattr(mod, 'Plant', None)
            GardenManager = getattr(mod, 'GardenManager', None)

            # Check for Seed class (v3.0: inherits from Flower)
            Seed = getattr(mod, 'Seed', None)

            if not Plant and not GardenManager:
                self.record_error(label, "Missing Class",
                                  "Neither 'Plant' nor 'GardenManager' found.\n"
                                  "v3.0 requires Plant class with static/class methods and nested stats.")
                console.print("[red]KO[/red]")
                return

            # v3.0 checks: static method on Plant for age check
            if Plant:
                # Check for static method (is_older_than_year or similar)
                has_static = False
                for name, method in inspect.getmembers(Plant):
                    if isinstance(inspect.getattr_static(Plant, name, None), staticmethod):
                        has_static = True
                        break
                
                if not has_static:
                    console.print("[yellow]Warning: No static method found on Plant class[/yellow]")

                # Check for class method (anonymous plant creation)
                has_classmethod = False
                for name, method in inspect.getmembers(Plant):
                    if isinstance(inspect.getattr_static(Plant, name, None), classmethod):
                        has_classmethod = True
                        break
                
                if not has_classmethod:
                    console.print("[yellow]Warning: No class method found on Plant class[/yellow]")

            # Check for nested stats class
            has_nested_stats = False
            if Plant:
                for attr_name in dir(Plant):
                    attr = getattr(Plant, attr_name, None)
                    if inspect.isclass(attr) and attr_name not in ('__class__',):
                        has_nested_stats = True
                        break
            if GardenManager:
                if hasattr(GardenManager, 'GardenStats') and inspect.isclass(getattr(GardenManager, 'GardenStats')):
                    has_nested_stats = True

            if not has_nested_stats:
                console.print("[yellow]Warning: No nested stats class found[/yellow]")

            # Check Seed class inherits from Flower
            if Seed:
                Flower = getattr(mod, 'Flower', None)
                if Flower and not issubclass(Seed, Flower):
                    self.record_error(label, "Inheritance Error",
                                      "Seed class must inherit from Flower")
                    console.print("[red]KO[/red]")
                    return

            # Run script and check for expected output sections
            output = self._run_script(path)
            if self.check_for_crash(output, label): return

            # v3.0 expects: year-old check, flower stats, tree stats with shade, seed, anonymous
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
                                  "v3.0 expects: year check, stats display, anonymous plant.\n"
                                  f"Got:\n{output}")
                console.print("[red]KO[/red]")
                return

            console.print("[green]OK[/green]")
        except Exception as e:
            console.print("[red]KO[/red]")
            self.record_error(label, "Execution Error", str(e))
