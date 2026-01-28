import sys
import os
import ast
from rich.console import Console
from rich.panel import Panel
from germinette.core import BaseTester

console = Console()

class Tester(BaseTester):
    def __init__(self):
        self.exercises = [
            ("ex0", self.test_card_foundation),
            ("ex1", self.test_deck_builder),
            ("ex2", self.test_ability_system),
            ("ex3", self.test_game_engine),
            ("ex4", self.test_tournament_platform),
        ]
        self.grouped_errors = {}

    def record_error(self, exercise_label, error_type, message):
        if exercise_label not in self.grouped_errors:
            self.grouped_errors[exercise_label] = []
        self.grouped_errors[exercise_label].append(f"[bold]{error_type}[/bold]\n{message}")

    def _load_module_path(self, ex_dir_name, main_file="main.py"):
        cwd = os.getcwd()
        # Logic to find the exercise directory (handling repository root vs test dir)
        # We assume the user runs from root, and structure is ex0/, ex1/, etc.
        # But for 'germinette devtools/test/python_module_07', it might be different.
        
        # Try finding 'ex0', 'ex1' in current directory
        if os.path.exists(ex_dir_name) and os.path.isdir(ex_dir_name):
            return os.path.join(cwd, ex_dir_name, main_file)
        
        # Try finding it inside a 'python_module_07' folder
        if os.path.exists("python_module_07"):
             sub_path = os.path.join("python_module_07", ex_dir_name, main_file)
             if os.path.exists(sub_path):
                 return os.path.abspath(sub_path)

        # Fallback for devtools structure where we might be IN the module dir provided by arg
        # If cwd ends with python_module_07, look for exN
        if os.path.basename(cwd) == "python_module_07":
             if os.path.exists(ex_dir_name):
                 return os.path.join(cwd, ex_dir_name, main_file)

        return None

    def run(self, exercise_name=None):
        console.print("[bold cyan]Testing Module 07: DataDeck (Abstract Base Classes)[/bold cyan]")
        
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

    # --- Strictness Helpers ---
    def common_strict_check(self, path, label, extra_funcs=None, extra_imports=None, enforce_try_except=False):
        allowed_funcs = [
            "print", "len", "sum", "max", "min", "range", "zip", "enumerate", 
            "int", "float", "str", "bool", "list", "dict", "set", "tuple",
            "isinstance", "issubclass", "super", "next", "iter", "all", "any", "id"
        ]
        if extra_funcs:
            allowed_funcs.extend(extra_funcs)

        allowed_imports = ["sys", "abc", "typing", "enum", "random", "datetime"]
        if extra_imports:
            allowed_imports.extend(extra_imports)

        return self.verify_strict(path, label, allowed_funcs, allowed_imports, enforce_try_except=enforce_try_except)

    def check_abc_inheritance(self, file_path, class_name, abc_name="ABC"):
        """Checks if a class inherits from ABC."""
        try:
            with open(file_path, "r") as f:
                tree = ast.parse(f.read())
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == class_name:
                    for base in node.bases:
                        if isinstance(base, ast.Name) and base.id == abc_name:
                            return True
            return False
        except:
            return False

    # --- Exercise Tests ---

    def test_card_foundation(self):
        console.print("\n[bold]Testing Exercise 0: Card Foundation[/bold]")
        exercise_label = "Exercise 0"
        path = self._load_module_path("ex0")
        
        if not path or not os.path.exists(path):
            console.print("[red]KO (Missing File)[/red]")
            self.record_error(exercise_label, "Missing File", "Could not find ex0/main.py")
            return

        # Check strictness on Card.py if exists
        card_py = os.path.join(os.path.dirname(path), "Card.py")
        if os.path.exists(card_py):
            if not self.common_strict_check(card_py, exercise_label): return
            if not self.check_abc_inheritance(card_py, "Card", "ABC"):
                console.print("[red]KO (Structure Error)[/red]")
                self.record_error(exercise_label, "Structure Error", "Card class must inherit from ABC")
                return

        # Check CreatureCard strictness
        creature_py = os.path.join(os.path.dirname(path), "CreatureCard.py")
        if os.path.exists(creature_py):
            if not self.common_strict_check(creature_py, exercise_label): return

        import subprocess
        try:
            cmd = [sys.executable, "-m", "ex0.main"]
            # We need to run from the parent of ex0 to support 'from ex0.Card import ...'
            cwd = os.path.dirname(os.path.dirname(path)) 
            result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
            out = result.stdout + result.stderr

            required = [
                "=== DataDeck Card Foundation ===",
                "Testing Abstract Base Class Design:",
                "CreatureCard Info:",
                "Fire Dragon",
                "legendary", # Rarity check (case insensitive usually, but check pdf output) -> 'Legendary'
                "Play result:",
                "'card_played': 'Fire Dragon'",
                "'mana_used': 5",
                "Attack result:", 
                "'attacker': 'Fire Dragon'",
                "'target': 'Goblin Warrior'",
                "'damage_dealt': 7",
                "Playable: False"
            ]

            missing = [r for r in required if r.lower() not in out.lower()]
            if not missing:
                console.print("[green]OK[/green]")
            else:
                 console.print("[red]KO (Output Mismatch)[/red]")
                 self.record_error(exercise_label, "Output Error", f"Missing output strings: {missing}\nGot:\n{out}")

        except Exception as e:
             console.print(f"[red]KO (Execution Error: {e})[/red]")

    def test_deck_builder(self):
        console.print("\n[bold]Testing Exercise 1: Deck Builder[/bold]")
        exercise_label = "Exercise 1"
        path = self._load_module_path("ex1")
        
        if not path or not os.path.exists(path):
            console.print("[red]KO (Missing File)[/red]")
            self.record_error(exercise_label, "Missing File", "Could not find ex1/main.py")
            return

        # Check Deck.py strictness
        deck_py = os.path.join(os.path.dirname(path), "Deck.py")
        if os.path.exists(deck_py):
            # random is allowed
            if not self.common_strict_check(deck_py, exercise_label, extra_imports=["ex0"]): return

        import subprocess
        try:
            cmd = [sys.executable, "-m", "ex1.main"]
            cwd = os.path.dirname(os.path.dirname(path))
            result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
            out = result.stdout + result.stderr

            required = [
                "=== DataDeck Deck Builder ===",
                "Building deck with different card types...",
                "Deck stats:",
                "'total_cards': 3",
                "'creatures': 1",
                "'spells': 1",
                "'artifacts': 1",
                "Drew:",
                "Play result:",
                "Same interface, different card behaviors"
            ]

            missing = [r for r in required if r.lower() not in out.lower()]
            if not missing:
                console.print("[green]OK[/green]")
            else:
                 console.print("[red]KO (Output Mismatch)[/red]")
                 self.record_error(exercise_label, "Output Error", f"Missing output strings: {missing}\nGot:\n{out}")
        except Exception as e:
             console.print(f"[red]KO (Execution Error: {e})[/red]")

    def test_ability_system(self):
        console.print("\n[bold]Testing Exercise 2: Ability System[/bold]")
        exercise_label = "Exercise 2"
        path = self._load_module_path("ex2")
        
        if not path or not os.path.exists(path):
            console.print("[red]KO (Missing File)[/red]")
            self.record_error(exercise_label, "Missing File", "Could not find ex2/main.py")
            return

        # Check EliteCard.py strictness
        elite_py = os.path.join(os.path.dirname(path), "EliteCard.py")
        if os.path.exists(elite_py):
            if not self.common_strict_check(elite_py, exercise_label, extra_imports=["ex0"]): return

        import subprocess
        try:
            cmd = [sys.executable, "-m", "ex2.main"]
            cwd = os.path.dirname(os.path.dirname(path))
            result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
            out = result.stdout + result.stderr

            required = [
                "=== DataDeck Ability System ===",
                "EliteCard capabilities:",
                "- Card:", 
                "- Combatable:",
                "- Magical:",
                "Playing Arcane Warrior",
                "Combat phase:",
                "Attack result:", "'damage': 5",
                "Defense result:", "'still_alive': True",
                "Magic phase:",
                "Spell cast:", "'spell': 'Fireball'",
                "Mana channel:"
            ]

            missing = [r for r in required if r.lower() not in out.lower()]
            if not missing:
                console.print("[green]OK[/green]")
            else:
                 console.print("[red]KO (Output Mismatch)[/red]")
                 self.record_error(exercise_label, "Output Error", f"Missing output strings: {missing}\nGot:\n{out}")
        except Exception as e:
             console.print(f"[red]KO (Execution Error: {e})[/red]")

    def test_game_engine(self):
        console.print("\n[bold]Testing Exercise 3: Game Engine[/bold]")
        exercise_label = "Exercise 3"
        path = self._load_module_path("ex3")
        
        if not path or not os.path.exists(path):
            console.print("[red]KO (Missing File)[/red]")
            self.record_error(exercise_label, "Missing File", "Could not find ex3/main.py")
            return

        import subprocess
        try:
            cmd = [sys.executable, "-m", "ex3.main"]
            cwd = os.path.dirname(os.path.dirname(path))
            result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
            out = result.stdout + result.stderr

            required = [
                "=== DataDeck Game Engine ===",
                "Configuring Fantasy Card Game...",
                "Factory: FantasyCardFactory",
                "Strategy: AggressiveStrategy",
                "Available types:",
                "Simulating aggressive turn...",
                "Hand:",
                "Turn execution:",
                "Actions:",
                "'damage_dealt': 8",
                "Game Report:",
                "Abstract Factory + Strategy Pattern: Maximum flexibility achieved!"
            ]

            missing = [r for r in required if r.lower() not in out.lower()]
            if not missing:
                console.print("[green]OK[/green]")
            else:
                 console.print("[red]KO (Output Mismatch)[/red]")
                 self.record_error(exercise_label, "Output Error", f"Missing output strings: {missing}\nGot:\n{out}")
        except Exception as e:
             console.print(f"[red]KO (Execution Error: {e})[/red]")

    def test_tournament_platform(self):
        console.print("\n[bold]Testing Exercise 4: Tournament Platform[/bold]")
        exercise_label = "Exercise 4"
        path = self._load_module_path("ex4")
        
        if not path or not os.path.exists(path):
            console.print("[red]KO (Missing File)[/red]")
            self.record_error(exercise_label, "Missing File", "Could not find ex4/main.py")
            return

        import subprocess
        try:
            cmd = [sys.executable, "-m", "ex4.main"]
            cwd = os.path.dirname(os.path.dirname(path))
            result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
            out = result.stdout + result.stderr

            required = [
                "=== DataDeck Tournament Platform ===",
                "Registering Tournament Cards...",
                "Fire Dragon (ID: dragon_001):",
                "- Interfaces: [Card, Combatable, Rankable]",
                "- Rating:",
                "Creating tournament match...",
                "Match result:",
                "winner_rating",
                "Tournament Leaderboard:",
                "1. Fire Dragon",
                "Platform Report:",
                "'platform_status': 'active'"
            ]

            missing = [r for r in required if r.lower() not in out.lower()]
            if not missing:
                console.print("[green]OK[/green]")
            else:
                 console.print("[red]KO (Output Mismatch)[/red]")
                 self.record_error(exercise_label, "Output Error", f"Missing output strings: {missing}\nGot:\n{out}")
        except Exception as e:
             console.print(f"[red]KO (Execution Error: {e})[/red]")
