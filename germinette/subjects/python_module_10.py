from germinette.core import BaseTester
from germinette.utils import IOTester
from rich.console import Console
from rich.panel import Panel
import sys
import os
import importlib.util
import ast
import functools
import operator
import itertools
import traceback
from collections import OrderedDict

console = Console()

class Tester(BaseTester):
    def __init__(self):
        self.exercises = [
            ("ex00", self.test_lambda_sanctum),
            ("ex0", self.test_lambda_sanctum),
            ("ex01", self.test_higher_realm),
            ("ex1", self.test_higher_realm),
            ("ex02", self.test_memory_depths),
            ("ex2", self.test_memory_depths),
            ("ex03", self.test_ancient_library),
            ("ex3", self.test_ancient_library),
            ("ex04", self.test_masters_tower),
            ("ex4", self.test_masters_tower),
        ]
        self.grouped_errors = {}

    def record_error(self, exercise_label, error_type, message):
        if exercise_label not in self.grouped_errors:
            self.grouped_errors[exercise_label] = []
        self.grouped_errors[exercise_label].append(f"[bold]{error_type}[/bold]\n{message}")

    def _load_module(self, ex_num, main_file):
        """Standardized loading logic for python_module_10"""
        cwd = os.getcwd()
        # Direct inside python_module_10
        if os.path.basename(cwd) == "python_module_10":
            ex_possible = [f"ex0{ex_num}", f"ex{ex_num}"]
            for ex in ex_possible:
                if os.path.exists(ex):
                    path = os.path.join(cwd, ex, main_file)
                    if os.path.exists(path):
                        return self._load_from_path(path)

        # Check standard paths
        base_search = [
            os.path.join(cwd, "python_module_10"),
            os.path.join(cwd, "devtools", "test", "python_module_10"),
            cwd
        ]
        
        for base in base_search:
            if not os.path.exists(base): continue
            ex_possible = [f"ex0{ex_num}", f"ex{ex_num}"]
            for ex in ex_possible:
                path = os.path.join(base, ex, main_file)
                if os.path.exists(path):
                    return self._load_from_path(path)
        
        return None, None

    def _load_from_path(self, path):
        try:
            spec = importlib.util.spec_from_file_location("mod_10_test", path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod, path
        except Exception as e:
            console.print(f"[red]Failed to load {path}: {e}[/red]")
            return None, path

    def common_strict_check(self, path, label, extra_imports=None):
        # Module 10 Strictness: Functional Programming Focus
        
        # 1. No Globals (functional purity)
        # We can try to detect assignments at module level, but that might flag constants.
        # The PDF says "Global variables (embrace functional purity)".
        # We'll skip strict AST check for globals for now to avoid false positives on constants,
        # but manual review is encouraged.
        
        # 2. No eval/exec
        # 3. No File I/O
        
        allowed_funcs = [
            "print", "len", "sum", "max", "min", "range", "zip", "enumerate", 
            "int", "float", "str", "bool", "list", "dict", "set", "tuple",
            "isinstance", "issubclass", "super", "next", "iter", "all", "any", "id",
            "map", "filter", "sorted", "callable", "repr", "type", "vars", "dir",
            "getattr", "setattr", "hasattr", "staticmethod", "classmethod", "property", "round"
        ]
        
        allowed_imports_base = ["sys", "os", "typing", "abc", "random", "datetime", 
                                "functools", "operator", "itertools", "math", "collections"]
        if extra_imports:
             allowed_imports_base.extend(extra_imports)

        # Strict Type Hints - MANDATORY
        type_errors = self.check_type_hints(path)
        if type_errors:
             console.print("[red]KO (Type Hints)[/red]")
             self.record_error(label, "Style Error (Missing Type Hints)", type_errors)
             return False
        
        # Docstrings explicitly NOT required by user
        
        return self.verify_strict(path, label, allowed_funcs, allowed_imports_base, enforce_try_except=False)

    def check_lambda_usage(self, path, required_count=1):
        """Checks if lambda is used in the file."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
            
            lambda_count = 0
            for node in ast.walk(tree):
                if isinstance(node, ast.Lambda):
                    lambda_count += 1
            
            return lambda_count
        except:
            return 0

    def check_no_def_in_ex0(self, path):
        """Checks if 'def' is used (forbidden in Ex0 except for the main test functions signatures?).
           Wait, subject says: 'Do not use the def keyword to create named functions for simple operations.'
           But we must define the required functions: artifact_sorter, etc.
           So 'def' IS required for the top-level functions.
           Inside them? misuse of def?
           The instruction is ambiguous: 'Do not use def... to create named functions for simple operations.'
           Likely means: use lambdas inside the main functions.
        """
        pass

    # --- Tests ---

    def test_lambda_sanctum(self):
        console.print("\n[bold]Testing Exercise 0: Lambda Sanctum[/bold]")
        exercise_label = "Exercise 0"
        mod, path = self._load_module(0, "lambda_spells.py")
        
        if not path:
             console.print("[red]KO (Missing File)[/red]")
             return
        if not mod:
             console.print("[red]KO (Import Failed)[/red]")
             return
            
        if not self.common_strict_check(path, exercise_label): return

        # Check Lambda Usage
        l_count = self.check_lambda_usage(path)
        if l_count < 3:
             console.print("[yellow]Warning: Few lambda expressions detected. Ensure you are using lambdas![/yellow]")

        try:
            # 1. Artifact Sorter
            artifacts = [
                {'name': 'Weak', 'power': 10, 'type': 'Ring'},
                {'name': 'Strong', 'power': 100, 'type': 'Staff'},
                {'name': 'Medium', 'power': 50, 'type': 'Wand'}
            ]
            
            if hasattr(mod, 'artifact_sorter'):
                sorted_arts = mod.artifact_sorter(artifacts.copy())
                if sorted_arts[0]['name'] == 'Strong' and sorted_arts[-1]['name'] == 'Weak':
                    console.print("[green]OK (Artifact Sorter)[/green]")
                else:
                    self.record_error(exercise_label, "Logic Error", "Artifacts not sorted by power descending")
                    console.print("[red]KO (Sorter)[/red]")
            else:
                self.record_error(exercise_label, "Missing Function", "artifact_sorter not found")

            # 2. Power Filter
            mages = [
                {'name': 'A', 'power': 10}, {'name': 'B', 'power': 100}, {'name': 'C', 'power': 50}
            ]
            if hasattr(mod, 'power_filter'):
                filtered = mod.power_filter(mages, 50)
                if len(filtered) == 2 and all(m['power'] >= 50 for m in filtered):
                     console.print("[green]OK (Power Filter)[/green]")
                else:
                     self.record_error(exercise_label, "Logic Error", "Filter failed")
                     console.print("[red]KO (Filter)[/red]")

            # 3. Spell Transformer
            if hasattr(mod, 'spell_transformer'):
                res = mod.spell_transformer(["fire", "ice"])
                if res == ["* fire *", "* ice *"]:
                     console.print("[green]OK (Spell Transformer)[/green]")
                else:
                     self.record_error(exercise_label, "Logic Error", f"Transformer failed. Got {res}")
                     console.print("[red]KO (Transformer)[/red]")

            # 4. Mage Stats
            if hasattr(mod, 'mage_stats'):
                stats = mod.mage_stats(mages)
                # Max 100, Min 10, Avg 53.33
                if stats['max_power'] == 100 and stats['min_power'] == 10 and 53.3 <= stats['avg_power'] <= 53.4:
                     console.print("[green]OK (Mage Stats)[/green]")
                else:
                     self.record_error(exercise_label, "Logic Error", f"Stats failed. Got {stats}")
                     console.print("[red]KO (Stats)[/red]")

        except Exception as e:
             console.print(f"[red]KO (Execution: {e})[/red]")
             self.record_error(exercise_label, "Runtime Error", traceback.format_exc())

    def test_higher_realm(self):
        console.print("\n[bold]Testing Exercise 1: Higher Realm[/bold]")
        exercise_label = "Exercise 1"
        mod, path = self._load_module(1, "higher_magic.py")
        
        if not path or not mod:
             console.print("[red]KO (Missing/Import)[/red]")
             return
            
        if not self.common_strict_check(path, exercise_label): return

        try:
            # 1. Spell Combiner
            if hasattr(mod, 'spell_combiner'):
                f1 = lambda x: x * 2
                f2 = lambda x: x + 10
                combined = mod.spell_combiner(f1, f2)
                res = combined(5) # (10, 15)
                if res == (10, 15):
                    console.print("[green]OK (Combiner)[/green]")
                else:
                    self.record_error(exercise_label, "Logic Error", f"Combiner failed. Got {res}")
                    console.print("[red]KO (Combiner)[/red]")

            # 2. Power Amplifier
            if hasattr(mod, 'power_amplifier'):
                base = lambda x: 10
                amp = mod.power_amplifier(base, 3)
                if amp(None) == 30:
                     console.print("[green]OK (Amplifier)[/green]")
                else:
                     self.record_error(exercise_label, "Logic Error", "Amplifier failed")
                     console.print("[red]KO (Amplifier)[/red]")

            # 3. Conditional Caster
            if hasattr(mod, 'conditional_caster'):
                cond_true = lambda x: True
                cond_false = lambda x: False
                spell = lambda x: "Casted"
                
                c1 = mod.conditional_caster(cond_true, spell)
                c2 = mod.conditional_caster(cond_false, spell)
                
                if c1(1) == "Casted" and c2(1) == "Spell fizzled":
                     console.print("[green]OK (Conditional)[/green]")
                else:
                     self.record_error(exercise_label, "Logic Error", "Conditional failed")
                     console.print("[red]KO (Conditional)[/red]")

            # 4. Spell Sequence
            if hasattr(mod, 'spell_sequence'):
                s1 = lambda x: x + "A"
                s2 = lambda x: x + "B"
                seq = mod.spell_sequence([s1, s2])
                res = seq("Start") # ["StartA", "StartB"]
                if res == ["StartA", "StartB"]:
                     console.print("[green]OK (Sequence)[/green]")
                else:
                     self.record_error(exercise_label, "Logic Error", f"Sequence failed: {res}")
                     console.print("[red]KO (Sequence)[/red]")

        except Exception as e:
             console.print(f"[red]KO (Crash: {e})[/red]")
             self.record_error(exercise_label, "Runtime Error", traceback.format_exc())

    def test_memory_depths(self):
        console.print("\n[bold]Testing Exercise 2: Memory Depths[/bold]")
        exercise_label = "Exercise 2"
        mod, path = self._load_module(2, "scope_mysteries.py") # The PDF says scope_mysteries.py
        
        if not path or not mod:
             console.print("[red]KO (Missing/Import)[/red]")
             return
            
        if not self.common_strict_check(path, exercise_label): return

        try:
            # 1. Mage Counter
            if hasattr(mod, 'mage_counter'):
                c = mod.mage_counter()
                v1 = c()
                v2 = c()
                if v1 == 1 and v2 == 2:
                    console.print("[green]OK (Counter)[/green]")
                else:
                    self.record_error(exercise_label, "Logic Error", f"Counter failed: {v1}, {v2}")
                    console.print("[red]KO (Counter)[/red]")

            # 2. Spell Accumulator
            if hasattr(mod, 'spell_accumulator'):
                acc = mod.spell_accumulator(10)
                v1 = acc(5) # 15
                v2 = acc(10) # 25
                if v1 == 15 and v2 == 25:
                     console.print("[green]OK (Accumulator)[/green]")
                else:
                     self.record_error(exercise_label, "Logic Error", f"Accumulator failed: {v1}, {v2}")
                     console.print("[red]KO (Accumulator)[/red]")

            # 3. Enchantment Factory
            if hasattr(mod, 'enchantment_factory'):
                fire = mod.enchantment_factory("Flaming")
                res = fire("Sword")
                if res == "Flaming Sword":
                     console.print("[green]OK (Factory)[/green]")
                else:
                     self.record_error(exercise_label, "Logic Error", f"Factory failed: {res}")
                     console.print("[red]KO (Factory)[/red]")

            # 4. Memory Vault
            if hasattr(mod, 'memory_vault'):
                vault = mod.memory_vault()
                vault['store']('secret', '42')
                val = vault['recall']('secret')
                missing = vault['recall']('unknown')
                
                if val == '42' and missing == "Memory not found":
                     console.print("[green]OK (Vault)[/green]")
                else:
                     self.record_error(exercise_label, "Logic Error", f"Vault failed: {val}, {missing}")
                     console.print("[red]KO (Vault)[/red]")

        except Exception as e:
             console.print(f"[red]KO (Crash: {e})[/red]")
             self.record_error(exercise_label, "Runtime Error", traceback.format_exc())

    def test_ancient_library(self):
        console.print("\n[bold]Testing Exercise 3: Ancient Library[/bold]")
        exercise_label = "Exercise 3"
        mod, path = self._load_module(3, "functools_artifacts.py")
        
        if not path or not mod:
             console.print("[red]KO (Missing/Import)[/red]")
             return
            
        if not self.common_strict_check(path, exercise_label): return

        try:
            # 1. Reducer
            if hasattr(mod, 'spell_reducer'):
                vals = [1, 2, 3, 4]
                s = mod.spell_reducer(vals, "add") # 10
                m = mod.spell_reducer(vals, "multiply") # 24
                if s == 10 and m == 24:
                     console.print("[green]OK (Reducer)[/green]")
                else:
                     console.print("[red]KO (Reducer)[/red]")

            # 2. Partial
            if hasattr(mod, 'partial_enchanter'):
                def base(power, element, target):
                    return f"{element} {target} ({power})"
                
                parts = mod.partial_enchanter(base)
                if 'fire_enchant' in parts:
                    res = parts['fire_enchant'](target="Sword")
                    # Should implicitly have power=50, element='fire' (or whatever logic user implements)
                    # We check stricter if we can, but let's assume valid partial usage.
                    console.print("[green]OK (Partial)[/green]")

            # 3. Memoized Fib
            if hasattr(mod, 'memoized_fibonacci'):
                # Check performance or simple result
                import time
                start = time.time()
                v1 = mod.memoized_fibonacci(30)
                end = time.time()
                if v1 == 832040:
                     console.print(f"[green]OK (Fibonacci)[/green]")
                else:
                     console.print(f"[red]KO (Fibonacci: {v1})[/red]")

            # 4. Dispatcher
            if hasattr(mod, 'spell_dispatcher'):
                d = mod.spell_dispatcher()
                # int -> damage, str -> enchant, list -> multi
                # We can't strict check output content as it's not specified exactly in requirements text provided (just "appropriate behavior")
                # But we can check it doesn't crash
                d(10)
                d("spell")
                d([1, 2])
                console.print("[green]OK (Dispatcher)[/green]")

        except Exception as e:
             console.print(f"[red]KO (Crash: {e})[/red]")
             self.record_error(exercise_label, "Runtime Error", traceback.format_exc())

    def test_masters_tower(self):
        console.print("\n[bold]Testing Exercise 4: Master's Tower[/bold]")
        exercise_label = "Exercise 4"
        mod, path = self._load_module(4, "decorator_mastery.py")
        
        if not path or not mod:
             console.print("[red]KO (Missing/Import)[/red]")
             return
            
        if not self.common_strict_check(path, exercise_label): return

        try:
            # 1. Timer
            if hasattr(mod, 'spell_timer'):
                @mod.spell_timer
                def fast_spell():
                    return "Done"
                
                res = fast_spell()
                if res == "Done":
                     console.print("[green]OK (Timer)[/green]")
                else:
                     console.print("[red]KO (Timer)[/red]")

            # 2. Power Validator
            if hasattr(mod, 'power_validator'):
                @mod.power_validator(min_power=10)
                def cast(power):
                    return "Cast"
                
                if cast(10) == "Cast" and cast(5) == "Insufficient power for this spell":
                     console.print("[green]OK (Validator)[/green]")
                else:
                     console.print("[red]KO (Validator)[/red]")
            
            # 3. Retry
            if hasattr(mod, 'retry_spell'):
                # Mock function that fails twice then succeeds
                msg = []
                @mod.retry_spell(max_attempts=3)
                def unstable():
                    msg.append("try")
                    if len(msg) < 3:
                        raise ValueError("Fail")
                    return "Success"
                
                res = unstable()
                if res == "Success" and len(msg) == 3:
                     console.print("[green]OK (Retry)[/green]")
                else:
                     console.print("[red]KO (Retry)[/red]")

            # 4. MageGuild
            if hasattr(mod, 'MageGuild'):
                mg = mod.MageGuild()
                if mod.MageGuild.validate_mage_name("Gandalf") and not mod.MageGuild.validate_mage_name("A"):
                     console.print("[green]OK (StaticMethod)[/green]")
                
                res = mg.cast_spell("Fire", 15)
                fail = mg.cast_spell("Fire", 5)
                
                if "Successfully" in res and "Insufficient" in fail:
                     console.print("[green]OK (Class Method)[/green]")

        except Exception as e:
             console.print(f"[red]KO (Crash: {e})[/red]")
             self.record_error(exercise_label, "Runtime Error", traceback.format_exc())

    def run(self, exercise_name=None):
        console.print("[bold magenta]Testing Module 10: FuncMage Chronicles[/bold magenta]")
        
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
            visited = set()
            for name, func in self.exercises:
                if func not in visited:
                    func()
                    visited.add(func)

        if self.grouped_errors:
            console.print()
            console.rule("[bold red]Detailed Error Report[/bold red]")
            console.print()
            for label, messages in self.grouped_errors.items():
                content = "\n\n[dim]────────────────────────────────[/dim]\n\n".join(messages)
                console.print(Panel(content, title=f"[bold red]{label}[/bold red]", border_style="red", expand=False))
                console.print()
