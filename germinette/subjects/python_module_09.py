from germinette.core import BaseTester
from germinette.utils import IOTester
from rich.console import Console
from rich.panel import Panel
import sys
import os
import importlib.util
import traceback
import ast
from datetime import datetime, date

console = Console()

class Tester(BaseTester):
    def __init__(self):
        self.exercises = [
            ("ex00", self.test_space_station),
            ("ex0", self.test_space_station),
            ("ex01", self.test_alien_contact),
            ("ex1", self.test_alien_contact),
            ("ex02", self.test_space_crew),
            ("ex2", self.test_space_crew),
        ]
        self.grouped_errors = {}
        self.required_ex_files = {
            "ex0": "space_station.py",
            "ex1": "alien_contact.py",
            "ex2": "space_crew.py",
        }

    def record_error(self, exercise_label, error_type, message):
        if exercise_label not in self.grouped_errors:
            self.grouped_errors[exercise_label] = []
        self.grouped_errors[exercise_label].append(f"[bold]{error_type}[/bold]\n{message}")

    def _load_module(self, ex_num, main_file):
        """Standardized loading logic for python_module_09 structure"""
        cwd = os.getcwd()
        if os.path.basename(cwd) == "python_module_09":
            # Running inside python_module_09
            ex_possible = [f"ex0{ex_num}", f"ex{ex_num}"]
            for ex in ex_possible:
                if os.path.exists(ex):
                    path = os.path.join(cwd, ex, main_file)
                    if os.path.exists(path):
                        return self._load_from_path(path)
        
        # Check devtools/test structure or root structure
        base_search = [
            os.path.join(cwd, "python_module_09"),
            os.path.join(cwd, "devtools", "test", "python_module_09"),
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
            spec = importlib.util.spec_from_file_location("mod_09_test", path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod, path
        except Exception as e:
            console.print(f"[red]Failed to load {path}: {e}[/red]")
            import traceback
            traceback.print_exc()
            return None, path

    def common_strict_check(self, path, label, extra_imports=None):
        allowed_funcs = [
            "print", "len", "sum", "max", "min", "range", "zip", "enumerate", 
            "int", "float", "str", "bool", "list", "dict", "set", "tuple",
            "isinstance", "issubclass", "super", "next", "iter", "all", "any", "id",
            "open", "exit", "repr", "type", "globals", "locals", "vars", "hasattr", "getattr", "setattr"
        ]
        
        # Pydantic requires a lot of things, we might need to be lenient on strict parsing
        # because Pydantic does AST magic or metaclass stuff that might look like violations.
        # But we check user code, not library code.
        
        allowed_imports_base = ["typing", "datetime", "pydantic", "enum", "json", "csv"]
        if extra_imports:
             allowed_imports_base.extend(extra_imports)

        style_errors = self.check_flake8(path)
        if style_errors:
             console.print("[red]KO[/red]")
             self.record_error(label, "Style Error (Flake8)", style_errors)
             return False

        type_errors = self.check_type_hints(path)
        if type_errors:
             console.print("[red]KO (Type Hints)[/red]")
             self.record_error(label, "Style Error (Missing Type Hints)", type_errors)
             return False

        return self.verify_strict(path, label, allowed_funcs, allowed_imports_base, enforce_try_except=False)

    def _check_project_structure(self):
        cwd = os.getcwd()
        base_candidates = [
            os.path.join(cwd, "python_module_09"),
            os.path.join(cwd, "devtools", "test", "python_module_09"),
            cwd,
        ]
        base = None
        for b in base_candidates:
            if os.path.exists(b):
                base = b
                break
        if base is None:
            return
        missing = []
        for ex, fname in self.required_ex_files.items():
            path = os.path.join(base, ex, fname)
            if not os.path.exists(path):
                missing.append(f"{ex}/{fname}")
        if missing:
            self.record_error(
                "Project Structure",
                "Missing Exercise Files",
                "Module 09 expected files are missing:\n- " + "\n- ".join(missing),
            )

    def _assert_pydantic_v2_validators(self, path, exercise_label, require_model_validator):
        try:
            with open(path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
        except Exception as e:
            self.record_error(exercise_label, "AST Error", f"Could not parse file: {e}")
            return False

        has_model_validator = False
        has_deprecated_validator = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for deco in node.decorator_list:
                    deco_name = None
                    if isinstance(deco, ast.Name):
                        deco_name = deco.id
                    elif isinstance(deco, ast.Attribute):
                        deco_name = deco.attr
                    elif isinstance(deco, ast.Call):
                        if isinstance(deco.func, ast.Name):
                            deco_name = deco.func.id
                        elif isinstance(deco.func, ast.Attribute):
                            deco_name = deco.func.attr
                    if deco_name == "model_validator":
                        has_model_validator = True
                    if deco_name == "validator":
                        has_deprecated_validator = True

        if has_deprecated_validator:
            self.record_error(
                exercise_label,
                "Structure Error",
                "Deprecated @validator detected. Use @model_validator (Pydantic v2).",
            )
            return False
        if require_model_validator and not has_model_validator:
            self.record_error(
                exercise_label,
                "Structure Error",
                "Missing required @model_validator(mode='after') business validation.",
            )
            return False
        return True

    def test_space_station(self):
        console.print("\n[bold]Testing Exercise 0: Space Station Data[/bold]")
        exercise_label = "Exercise 0"
        mod, path = self._load_module(0, "space_station.py")

        if not path:
            console.print("[red]KO (Missing File)[/red]")
            self.record_error(
                exercise_label, "Missing File", "Could not find space_station.py"
            )
            return

        if not mod:
            console.print("[red]KO (Import Failed)[/red]")
            self.record_error(
                exercise_label, "Import Error", "Failed to import module."
            )
            return

        if not self.common_strict_check(path, exercise_label):
            return

        try:
            SpaceStation = getattr(mod, "SpaceStation", None)
            if not SpaceStation:
                self.record_error(
                    exercise_label,
                    "Structure Error",
                    "One or more classes missing: SpaceStation",
                )
                console.print("[red]KO[/red]")
                return

            # Invalid Case Check
            errors = []
            try:
                # Valid case
                start = datetime(2024, 1, 1)
                SpaceStation(
                    station_id="ISS001",
                    name="Test Station",
                    crew_size=10,
                    power_level=80.5,
                    oxygen_level=95.0,
                    last_maintenance=start,
                    is_operational=True,
                )
            except Exception as e:
                self.record_error(
                    exercise_label,
                    "Validation Error",
                    f"Failed to instantiate valid model: {e}",
                )
                console.print("[red]KO[/red]")
                return

            try:
                SpaceStation(
                    station_id="ISS001",
                    name="Test",
                    crew_size=25,  # Invalid (>20)
                    power_level=101.0,  # Invalid
                    oxygen_level=95.0,
                    last_maintenance=start
                )
                errors.append("Model failed to raise error for crew_size > 20")
            except Exception:
                pass  # Good

            # Extra constraints from subject
            try:
                SpaceStation(
                    station_id="AA",  # too short
                    name="X",
                    crew_size=2,
                    power_level=80.0,
                    oxygen_level=80.0,
                    last_maintenance=start,
                )
                errors.append("Model failed to enforce station_id min length (3)")
            except Exception:
                pass
            try:
                SpaceStation(
                    station_id="ISS_VALID",
                    name="X" * 51,  # too long
                    crew_size=2,
                    power_level=80.0,
                    oxygen_level=80.0,
                    last_maintenance=start,
                )
                errors.append("Model failed to enforce name max length (50)")
            except Exception:
                pass
            try:
                SpaceStation(
                    station_id="ISS_VALID",
                    name="Station",
                    crew_size=2,
                    power_level=80.0,
                    oxygen_level=80.0,
                    last_maintenance=start,
                    notes="n" * 201,  # too long
                )
                errors.append("Model failed to enforce notes max length (200)")
            except Exception:
                pass

            if errors:
                self.record_error(exercise_label, "Logic Error", "\n".join(errors))
                console.print("[red]KO[/red]")
                return

            console.print("[green]OK[/green]")

        except Exception as e:
            console.print(f"[red]KO (Execution Error: {e})[/red]")
            self.record_error(exercise_label, "Runtime Error", traceback.format_exc())

    def test_alien_contact(self):
        console.print("\n[bold]Testing Exercise 1: Alien Contact Logs[/bold]")
        exercise_label = "Exercise 1"
        mod, path = self._load_module(1, "alien_contact.py")
        
        if not path:
             console.print("[red]KO (Missing File)[/red]")
             return
        if not mod:
             console.print("[red]KO (Import Failed)[/red]")
             return
            
        if not self.common_strict_check(path, exercise_label): return
        if not self._assert_pydantic_v2_validators(
            path, exercise_label, require_model_validator=True
        ):
            return

        try:
             AlienContact = getattr(mod, "AlienContact", None)
             ContactType = getattr(mod, "ContactType", None)
             
             if not AlienContact or not ContactType:
                 self.record_error(exercise_label, "Structure Error", "Missing AlienContact or ContactType")
                 console.print("[red]KO[/red]")
                 return

             # Valid
             try:
                 AlienContact(
                     contact_id="AC_2024_001",
                     timestamp=datetime.now(),
                     location="Area 51",
                     contact_type=ContactType.radio,
                     signal_strength=5.0,
                     duration_minutes=10,
                     witness_count=1,
                     is_verified=False
                 )
             except Exception as e:
                 self.record_error(exercise_label, "Validation Error", f"Valid input failed: {e}")
                 console.print("[red]KO[/red]")
                 return

             # Validation Rules Check
             # 1. AC Prefix
             try:
                 AlienContact(
                      contact_id="XX_2024",
                      timestamp=datetime.now(),
                      location="Loc",
                      contact_type=ContactType.radio,
                      signal_strength=5.0,
                      duration_minutes=10,
                      witness_count=1
                 )
                 self.record_error(exercise_label, "Logic Error", "Allowed ID without 'AC' prefix")
                 console.print("[red]KO[/red]")
                 return
             except: pass

             # 2. Telepathic Witness Count
             try:
                 AlienContact(
                      contact_id="AC_2024",
                      timestamp=datetime.now(),
                      location="Loc",
                      contact_type=ContactType.telepathic,
                      signal_strength=5.0,
                      duration_minutes=10,
                      witness_count=1 # Must be >= 3
                 )
                 self.record_error(exercise_label, "Logic Error", "Allowed telepathic contact with < 3 witnesses")
                 console.print("[red]KO[/red]")
                 return
             except: pass

             # 3. Physical contact must be verified
             try:
                 AlienContact(
                      contact_id="AC_PHYS",
                      timestamp=datetime.now(),
                      location="Loc",
                      contact_type=ContactType.physical,
                      signal_strength=5.0,
                      duration_minutes=10,
                      witness_count=5,
                      is_verified=False
                 )
                 self.record_error(exercise_label, "Logic Error", "Allowed physical contact without verification")
                 console.print("[red]KO[/red]")
                 return
             except: pass

             # 4. Strong signal (> 7.0) must include received message
             try:
                 AlienContact(
                      contact_id="AC_SIG",
                      timestamp=datetime.now(),
                      location="Loc",
                      contact_type=ContactType.radio,
                      signal_strength=8.5,
                      duration_minutes=10,
                      witness_count=1
                 )
                 self.record_error(exercise_label, "Logic Error", "Allowed strong signal (> 7.0) without received message")
                 console.print("[red]KO[/red]")
                 return
             except: pass

             console.print("[green]OK[/green]")

        except Exception as e:
             console.print(f"[red]KO (Execution Error: {e})[/red]")
             self.record_error(exercise_label, "Runtime Error", traceback.format_exc())

    def test_space_crew(self):
        console.print("\n[bold]Testing Exercise 2: Space Crew Management[/bold]")
        exercise_label = "Exercise 2"
        mod, path = self._load_module(2, "space_crew.py")
        
        if not path:
             console.print("[red]KO (Missing File)[/red]")
             return
        if not mod:
             console.print("[red]KO (Import Failed)[/red]")
             return
            
        if not self.common_strict_check(path, exercise_label): return
        if not self._assert_pydantic_v2_validators(
            path, exercise_label, require_model_validator=True
        ):
            return

        try:
             CrewMember = getattr(mod, "CrewMember", None)
             SpaceMission = getattr(mod, "SpaceMission", None)
             Rank = getattr(mod, "Rank", None)
             
             if not CrewMember or not SpaceMission or not Rank:
                 self.record_error(exercise_label, "Structure Error", "Missing classes")
                 console.print("[red]KO[/red]")
                 return
             
             # Create Valid Crew
             cmdr = CrewMember(
                 member_id="CM001", name="Cmdr Shep", rank=Rank.commander,
                 age=40, specialization="Command", years_experience=15
             )
             pilot = CrewMember(
                 member_id="CM002", name="Joker", rank=Rank.lieutenant,
                 age=30, specialization="Pilot", years_experience=8
             )
             
             # Valid Mission
             try:
                 SpaceMission(
                     mission_id="M2025_TEST",
                     mission_name="Test Mission",
                     destination="Mars",
                     launch_date=datetime.now(),
                     duration_days=100,
                     crew=[cmdr, pilot],
                     budget_millions=500.0
                 )
             except Exception as e:
                 self.record_error(exercise_label, "Validation Error", f"Valid input failed: {e}")
                 console.print("[red]KO[/red]")
                 return

             # Invalid Mission: No Commander
             try:
                 SpaceMission(
                     mission_id="M2025_BAD",
                     mission_name="Bad Mission",
                     destination="Mars",
                     launch_date=datetime.now(),
                     duration_days=100,
                     crew=[pilot], # No commander
                     budget_millions=500.0
                 )
                 self.record_error(exercise_label, "Logic Error", "Allowed mission without Commander/Captain")
                 console.print("[red]KO[/red]")
                 return
             except: pass

             # Invalid Mission: Long mission without 50% experienced crew
             cadet1 = CrewMember(
                 member_id="CM003", name="Newbie1", rank=Rank.cadet,
                 age=20, specialization="Science", years_experience=1
             )
             cadet2 = CrewMember(
                 member_id="CM004", name="Newbie2", rank=Rank.cadet,
                 age=21, specialization="Engineering", years_experience=2
             )
             try:
                 SpaceMission(
                     mission_id="M2025_LONG",
                     mission_name="Long Mission",
                     destination="Jupiter",
                     launch_date=datetime.now(),
                     duration_days=400,
                     crew=[cmdr, cadet1, cadet2],
                     budget_millions=500.0
                 )
                 self.record_error(exercise_label, "Logic Error", "Allowed long mission (> 365 days) without 50% experienced crew")
                 console.print("[red]KO[/red]")
                 return
             except: pass

             # Invalid Mission: Inactive crew member
             inactive = CrewMember(
                 member_id="CM005", name="Retired", rank=Rank.captain,
                 age=55, specialization="Command", years_experience=25,
                 is_active=False
             )
             try:
                 SpaceMission(
                     mission_id="M2025_ACT",
                     mission_name="Active Check",
                     destination="Moon",
                     launch_date=datetime.now(),
                     duration_days=30,
                     crew=[inactive],
                     budget_millions=100.0
                 )
                 self.record_error(exercise_label, "Logic Error", "Allowed mission with inactive crew member")
                 console.print("[red]KO[/red]")
                 return
             except: pass

             console.print("[green]OK[/green]")

        except Exception as e:
             console.print(f"[red]KO (Execution Error: {e})[/red]")
             self.record_error(exercise_label, "Runtime Error", traceback.format_exc())

    def run(self, exercise_name=None):
        console.print("[bold purple]Testing Module 09: Cosmic Data[/bold purple]")
        
        # Ensure imports work for local files
        if os.getcwd() not in sys.path:
            sys.path.insert(0, os.getcwd())
        self._check_project_structure()

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
