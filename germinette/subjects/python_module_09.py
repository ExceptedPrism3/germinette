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
from enum import Enum
from typing import Type

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

    @staticmethod
    def _resolve_enum_member(enum_cls: Type[Enum], semantic: str):
        """Map subject semantic tokens (radio, commander, …) to Enum members regardless of Python member naming."""
        want = semantic.strip().lower()
        if not isinstance(enum_cls, type) or not issubclass(enum_cls, Enum):
            raise TypeError(f"Expected Enum type, got {enum_cls}")
        picks: dict[int, Enum] = {}
        for member in enum_cls:
            nm = getattr(member, "name", "").lower()
            val = getattr(member, "value", None)
            if nm == want:
                picks.setdefault(id(member), member)
            elif isinstance(val, str) and val.lower() == want:
                picks.setdefault(id(member), member)
            elif val is not None and str(val).strip().lower() == want:
                picks.setdefault(id(member), member)
        unique = list(picks.values())
        if len(unique) == 1:
            return unique[0]
        if not unique:
            raise LookupError(
                f"No {enum_cls.__name__} member matches semantic {semantic!r} "
                f"(accepted: member.name or .value case-insensitive)."
            )
        raise LookupError(
            f"Ambiguous Enum match for {semantic!r} in {enum_cls.__name__}: {unique}"
        )

    def _crew_list_bounds_from_json_schema(self, model_cls):
        """Return (min_items, max_items) for SpaceMission.crew if JSON schema exposes them."""
        try:
            js = model_cls.model_json_schema()
        except Exception:
            return None, None
        defs = js.get("$defs") or {}

        def deref(node):
            if not isinstance(node, dict):
                return node
            ref = node.get("$ref")
            if isinstance(ref, str) and "/" in ref:
                key = ref.rsplit("/", 1)[-1]
                inner = defs.get(key)
                if inner is not None:
                    return deref(inner)
            if "anyOf" in node:
                for cand in node["anyOf"]:
                    got = deref(cand)
                    if isinstance(got, dict) and got.get("type") == "array":
                        return got
            return node

        prop = js.get("properties") or {}
        crew_node = prop.get("crew")
        if crew_node is None:
            return None, None
        resolved = deref(crew_node)
        if not isinstance(resolved, dict) or resolved.get("type") != "array":
            return None, None
        mi = resolved.get("minItems")
        ma = resolved.get("maxItems")
        try:
            return (int(mi) if mi is not None else None, int(ma) if ma is not None else None)
        except (TypeError, ValueError):
            return None, None

    @staticmethod
    def _accepts_invalid_payload(fn):
        """True if fn() runs without raising (invalid payload wrongly accepted)."""
        try:
            fn()
            return True
        except Exception:
            return False

    def _check_ex2_space_mission_scalar_field_bounds(
        self, exercise_label, SpaceMission, cmdr_inst, pilot_inst
    ):
        """PDF Exercise 2: SpaceMission ids/names/ranges enforced via Field (runtime probes)."""
        launch = datetime.now()
        failures: list[str] = []

        def base_mission(extra):
            kw = dict(
                mission_id="M2029_BASE01",
                mission_name="Baseline mission name long enough here",
                destination="Moon",
                launch_date=launch,
                duration_days=200,
                crew=[cmdr_inst, pilot_inst],
                budget_millions=100.0,
            )
            kw.update(extra)
            return kw

        checks = [
            (
                'SpaceMission must reject mission_id shorter than 5 characters '
                '(subject: mission_id length 5–15).',
                lambda: SpaceMission(**base_mission({"mission_id": "M202"})),
            ),
            (
                'SpaceMission must reject mission_id longer than 15 characters '
                '(subject: mission_id length 5–15).',
                lambda: SpaceMission(
                    **base_mission({"mission_id": "P" + "0" * 15})
                ),
            ),
            (
                'SpaceMission must reject mission_name shorter than 3 characters '
                '(subject: mission_name length 3–100).',
                lambda: SpaceMission(
                    **base_mission({"mission_name": "Mo"})
                ),
            ),
            (
                'SpaceMission must reject mission_name longer than 100 characters '
                '(subject: mission_name length 3–100).',
                lambda: SpaceMission(
                    **base_mission(
                        {"mission_name": ("X" * 101)},
                    ),
                ),
            ),
            (
                'SpaceMission must reject destination shorter than 3 characters '
                '(subject: destination length 3–50).',
                lambda: SpaceMission(
                    **base_mission({"destination": "MZ"}),
                ),
            ),
            (
                'SpaceMission must reject destination longer than 50 characters '
                '(subject: destination length 3–50).',
                lambda: SpaceMission(
                    **base_mission(
                        {"destination": "D" * 51},
                    ),
                ),
            ),
            (
                'SpaceMission must reject duration_days < 1 '
                '(subject: duration_days 1–3650).',
                lambda: SpaceMission(**base_mission({"duration_days": 0})),
            ),
            (
                'SpaceMission must reject duration_days > 3650 '
                '(subject: duration_days 1–3650).',
                lambda: SpaceMission(**base_mission({"duration_days": 4000})),
            ),
            (
                'SpaceMission must reject budget_millions < 1.0 '
                '(subject: budget_millions 1.0–10000.0).',
                lambda: SpaceMission(
                    **base_mission({"budget_millions": 0.5}),
                ),
            ),
            (
                'SpaceMission must reject budget_millions > 10000.0 '
                '(subject: budget_millions 1.0–10000.0).',
                lambda: SpaceMission(
                    **base_mission({"budget_millions": 11000.0}),
                ),
            ),
        ]

        for msg, thunk in checks:
            if self._accepts_invalid_payload(thunk):
                failures.append(msg)
        if failures:
            self.record_error(
                exercise_label,
                "Logic Error",
                "PDF SpaceMission Field constraints violated (must reject):\n"
                + "\n".join(f"- {f}" for f in failures),
            )
            return False
        return True

    def _check_ex2_crew_member_scalar_field_bounds(
        self,
        exercise_label,
        CrewMember,
        rk_commander,
    ):
        """PDF Exercise 2: CrewMember string ranges and numeric bounds (runtime probes)."""
        failures: list[str] = []

        base = dict(
            member_id="MBX001",
            name="Valid Enough Name",
            rank=rk_commander,
            age=30,
            specialization="Enough spec text",
            years_experience=10,
            is_active=True,
        )

        def member(extra):
            m = dict(base)
            m.update(extra)
            return CrewMember(**m)

        checks = [
            (
                'CrewMember must reject member_id shorter than 3 chars '
                '(subject: member_id length 3–10).',
                lambda: member({"member_id": "AB"}),
            ),
            (
                'CrewMember must reject member_id longer than 10 chars '
                '(subject: member_id length 3–10).',
                lambda: member({"member_id": "ABCDEFGHIJX"}),
            ),
            (
                'CrewMember must reject name shorter than 2 chars '
                '(subject: name length 2–50).',
                lambda: member({"name": "A"}),
            ),
            (
                'CrewMember must reject name longer than 50 chars '
                '(subject: name length 2–50).',
                lambda: member({"name": "N" * 51}),
            ),
            (
                'CrewMember must reject specialization shorter than 3 chars '
                '(subject: specialization length 3–30).',
                lambda: member({"specialization": "AB"}),
            ),
            (
                'CrewMember must reject specialization longer than 30 chars '
                '(subject: specialization length 3–30).',
                lambda: member({"specialization": "Z" * 31}),
            ),
            (
                'CrewMember must reject age below 18 (subject: age 18–80).',
                lambda: member({"age": 17}),
            ),
            (
                'CrewMember must reject age above 80 (subject: age 18–80).',
                lambda: member({"age": 81}),
            ),
            (
                'CrewMember must reject years_experience > 50 '
                '(subject: years_experience 0–50).',
                lambda: member({"years_experience": 55}),
            ),
            (
                'CrewMember must reject years_experience < 0 '
                '(subject: years_experience 0–50).',
                lambda: member({"years_experience": -1}),
            ),
        ]

        for msg, thunk in checks:
            if self._accepts_invalid_payload(thunk):
                failures.append(msg)
        if failures:
            self.record_error(
                exercise_label,
                "Logic Error",
                "PDF CrewMember Field constraints violated (must reject):\n"
                + "\n".join(f"- {f}" for f in failures),
            )
            return False
        return True

    def _check_ex1_pdf_field_constraints(self, exercise_label, AlienContact, ct_radio):
        """PDF Exercise 1: AlienContact Field bounds (strings + numeric intervals), runtime probes."""
        ts = datetime.now()
        failures: list[str] = []

        base = dict(
            contact_id="AC_BASE_MAIN",
            timestamp=ts,
            location="Nevada Test Range Bunker Nine",
            contact_type=ct_radio,
            signal_strength=4.5,
            duration_minutes=30,
            witness_count=2,
            is_verified=False,
        )

        def contact(**upd):
            d = dict(base)
            d.update(upd)
            return AlienContact(**d)

        checks = [
            (
                "contact_id shorter than 5 characters (subject: 5–15).",
                lambda: contact(contact_id="AC_Z"),
            ),
            (
                "contact_id longer than 15 characters (subject: 5–15).",
                lambda: contact(contact_id="AC" + ("Z" * 14)),
            ),
            (
                "location shorter than 3 characters (subject: 3–100).",
                lambda: contact(location="Nv"),
            ),
            (
                "location longer than 100 characters (subject: 3–100).",
                lambda: contact(location="L" * 101),
            ),
            (
                "signal_strength below 0.0 (subject: 0.0–10.0).",
                lambda: contact(signal_strength=-0.01),
            ),
            (
                "signal_strength above 10.0 (subject: 0.0–10.0).",
                lambda: contact(signal_strength=10.5),
            ),
            (
                "duration_minutes below 1 (subject: 1–1440).",
                lambda: contact(duration_minutes=0),
            ),
            (
                "duration_minutes above 1440 (subject: 1–1440).",
                lambda: contact(duration_minutes=2000),
            ),
            (
                "witness_count below 1 (subject: 1–100).",
                lambda: contact(witness_count=0),
            ),
            (
                "witness_count above 100 (subject: 1–100).",
                lambda: contact(witness_count=101),
            ),
            (
                "message_received beyond 500 characters "
                "(subject: optional max 500).",
                lambda: contact(message_received=("M" * 501)),
            ),
        ]
        desc = []
        for label, thunk in checks:
            if self._accepts_invalid_payload(thunk):
                desc.append(label)
        if desc:
            self.record_error(
                exercise_label,
                "Logic Error",
                "PDF AlienContact Field constraints violated (must reject):\n"
                + "\n".join(f"- {f}" for f in desc),
            )
            return False
        return True

    def _check_ex2_pdf_field_constraints(
        self,
        exercise_label,
        SpaceMission,
        CrewMember,
        commander_rank,
        pilot_rank,
        crew_commander_person,
        crew_pilot_person,
    ):
        """PDF Exercise 2: crew cardinality plus SpaceMission/CrewMember Field bounds by runtime probes."""

        mission_kwargs = lambda crew: dict(
            mission_id="M_BOUNDS_CHK",
            mission_name="Bounds Check",
            destination="Moon",
            launch_date=datetime.now(),
            duration_days=10,
            crew=crew,
            budget_millions=100.0,
        )

        crew_empty_accepted = False
        crew_oversized_accepted = False
        try:
            SpaceMission(**mission_kwargs([]))
            crew_empty_accepted = True
        except Exception:
            pass

        thirteen = []
        for i in range(13):
            thirteen.append(
                CrewMember(
                    member_id=f"MB{i:02d}",
                    name=f"Member {i}",
                    rank=pilot_rank,
                    age=25,
                    specialization="Ops",
                    years_experience=i % 10,
                    is_active=True,
                )
            )
        thirteen[0] = CrewMember(
            member_id="MB_CMD",
            name="Command Holder",
            rank=commander_rank,
            age=45,
            specialization="Cmd",
            years_experience=10,
            is_active=True,
        )
        try:
            SpaceMission(**mission_kwargs(thirteen))
            crew_oversized_accepted = True
        except Exception:
            pass

        if crew_empty_accepted:
            self.record_error(
                exercise_label,
                "Logic Error",
                "SpaceMission.crew must reject an empty crew (subject requires 1–12 members).",
            )
            return False
        if crew_oversized_accepted:
            self.record_error(
                exercise_label,
                "Logic Error",
                "SpaceMission.crew must reject lists longer than 12 members "
                "(subject requires 1–12 members).",
            )
            return False

        mi, ma = self._crew_list_bounds_from_json_schema(SpaceMission)
        if mi is not None and ma is not None and (mi != 1 or ma != 12):
            self.record_error(
                exercise_label,
                "Structure Error",
                f"crew list constraints in model JSON schema should be min_items=1, max_items=12; "
                f"got minItems={mi}, maxItems={ma}.",
            )
            return False
        if not self._check_ex2_space_mission_scalar_field_bounds(
            exercise_label,
            SpaceMission,
            crew_commander_person,
            crew_pilot_person,
        ):
            return False
        if not self._check_ex2_crew_member_scalar_field_bounds(
            exercise_label,
            CrewMember,
            commander_rank,
        ):
            return False
        return True

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

             try:
                 ct_radio = self._resolve_enum_member(ContactType, "radio")
                 ct_telepathic = self._resolve_enum_member(ContactType, "telepathic")
                 ct_physical = self._resolve_enum_member(ContactType, "physical")
             except LookupError as e:
                 self.record_error(exercise_label, "Structure Error", str(e))
                 console.print("[red]KO[/red]")
                 return

             if not self._check_ex1_pdf_field_constraints(
                 exercise_label, AlienContact, ct_radio
             ):
                 console.print("[red]KO[/red]")
                 return

             # Valid
             try:
                 AlienContact(
                     contact_id="AC_2024_001",
                     timestamp=datetime.now(),
                     location="Area 51",
                     contact_type=ct_radio,
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
                      contact_type=ct_radio,
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
                      contact_type=ct_telepathic,
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
                      contact_type=ct_physical,
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
                      contact_type=ct_radio,
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

             try:
                 rk_commander = self._resolve_enum_member(Rank, "commander")
                 rk_lieutenant = self._resolve_enum_member(Rank, "lieutenant")
                 rk_cadet = self._resolve_enum_member(Rank, "cadet")
                 rk_captain = self._resolve_enum_member(Rank, "captain")
             except LookupError as e:
                 self.record_error(exercise_label, "Structure Error", str(e))
                 console.print("[red]KO[/red]")
                 return
             
             # Create Valid Crew
             cmdr = CrewMember(
                 member_id="CM001",
                 name="Cmdr Shep",
                 rank=rk_commander,
                 age=40,
                 specialization="Command",
                 years_experience=15,
             )
             pilot = CrewMember(
                 member_id="CM002",
                 name="Joker",
                 rank=rk_lieutenant,
                 age=30,
                 specialization="Pilot",
                 years_experience=8,
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

             if not self._check_ex2_pdf_field_constraints(
                 exercise_label,
                 SpaceMission,
                 CrewMember,
                 rk_commander,
                 rk_lieutenant,
                 cmdr,
                 pilot,
             ):
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
                 member_id="CM003",
                 name="Newbie1",
                 rank=rk_cadet,
                 age=20,
                 specialization="Science",
                 years_experience=1,
             )
             cadet2 = CrewMember(
                 member_id="CM004",
                 name="Newbie2",
                 rank=rk_cadet,
                 age=21,
                 specialization="Engineering",
                 years_experience=2,
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
                 member_id="CM005",
                 name="Retired",
                 rank=rk_captain,
                 age=55,
                 specialization="Command",
                 years_experience=25,
                 is_active=False,
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
