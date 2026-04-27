import sys
import os
import subprocess
import builtins
from rich.console import Console
from rich.panel import Panel
from germinette.core import BaseTester

console = Console()

class Tester(BaseTester):
    def __init__(self):
        self.exercises = [
            ("ex00", self.test_the_matrix),
            ("ex0", self.test_the_matrix), # Alias
            ("ex01", self.test_loading_programs),
            ("ex1", self.test_loading_programs), # Alias
            ("ex02", self.test_accessing_mainframe),
            ("ex2", self.test_accessing_mainframe), # Alias
        ]
        self.grouped_errors = {}
        self.required_oracle_keys = [
            "MATRIX_MODE",
            "DATABASE_URL",
            "API_KEY",
            "LOG_LEVEL",
            "ZION_ENDPOINT",
        ]

    def record_error(self, exercise_label, error_type, message):
        if exercise_label not in self.grouped_errors:
            self.grouped_errors[exercise_label] = []
        self.grouped_errors[exercise_label].append(f"[bold]{error_type}[/bold]\n{message}")

    def _load_module_path(self, ex_dir_name, main_file):
        cwd = os.getcwd()
        # Direct check
        if os.path.exists(ex_dir_name):
            possible = os.path.join(cwd, ex_dir_name, main_file)
            if os.path.exists(possible):
                return possible
        
        # Inside python_module_08
        if os.path.exists("python_module_08"):
             sub_path = os.path.join("python_module_08", ex_dir_name, main_file)
             if os.path.exists(sub_path):
                 return os.path.abspath(sub_path)

        # Fallback if cwd is python_module_08
        if os.path.basename(cwd) == "python_module_08":
             if os.path.exists(ex_dir_name):
                 return os.path.join(cwd, ex_dir_name, main_file)
        
        return None

    def _check_required_markers(self, out, markers):
        missing = [m for m in markers if m not in out]
        return missing

    def common_strict_check(
        self,
        path,
        label,
        allowed_imports=None,
        allow_import_related_style_errors=False,
    ):
        # Module 08 general instructions authorize all builtins.
        # Keep strict function checks enabled by allowing full builtin namespace.
        allowed_funcs = [name for name in dir(builtins) if not name.startswith("_")]
        imports = list(allowed_imports or [])

        style_errors = self.check_flake8(path)
        if style_errors:
            if not allow_import_related_style_errors:
                console.print("[red]KO[/red]")
                self.record_error(label, "Style Error (Flake8)", style_errors)
                return False
            # Ex1 exception: tolerate only import-related issues.
            style_blob = style_errors.lower()
            if ("import" not in style_blob and "f401" not in style_blob
                    and "f811" not in style_blob):
                console.print("[red]KO[/red]")
                self.record_error(
                    label,
                    "Style Error (Flake8)",
                    "Exercise 1 allows import-related checker noise only.\n"
                    f"Got non-import style/type errors:\n{style_errors}",
                )
                return False

        type_errors = self.check_type_hints(path)
        if type_errors:
            if not allow_import_related_style_errors:
                console.print("[red]KO (Type Hints)[/red]")
                self.record_error(
                    label, "Style Error (Missing Type Hints)", type_errors
                )
                return False
            type_blob = type_errors.lower()
            if ("import" not in type_blob and "cannot find implementation"
                    not in type_blob and "missing library stubs" not in type_blob):
                console.print("[red]KO (Type Hints)[/red]")
                self.record_error(
                    label,
                    "Style Error (Missing Type Hints)",
                    "Exercise 1 allows import-related checker noise only.\n"
                    f"Got non-import mypy errors:\n{type_errors}",
                )
                return False

        return self.verify_strict(
            path, label, allowed_funcs, imports, enforce_try_except=False
        )

    def test_the_matrix(self):
        console.print("\n[bold]Testing Exercise 0: The Matrix[/bold]")
        exercise_label = "Exercise 0"
        path = self._load_module_path("ex00", "construct.py")
        if not path:
            path = self._load_module_path("ex0", "construct.py")
        
        if not path or not os.path.exists(path):
            console.print("[red]KO (Missing File)[/red]")
            self.record_error(exercise_label, "Missing File", "Could not find ex00/construct.py")
            return

        if not self.common_strict_check(
            path, exercise_label, allowed_imports=["sys", "os", "site"]
        ):
            return

        # Test 1: Run standard (Outside Matrix)
        try:
            cmd = [sys.executable, path]
            cwd = os.path.dirname(path)
            result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
            out = result.stdout + result.stderr
            if self.check_for_crash(out, exercise_label): return

            base_markers = [
                "MATRIX STATUS:",
                "Current Python:",
                "Virtual Environment:",
            ]
            missing = self._check_required_markers(out, base_markers)
            if missing:
                console.print("[red]KO (Output Mismatch)[/red]")
                self.record_error(
                    exercise_label,
                    "Output Error",
                    f"Missing mandatory output markers: {missing!r}\nGot:\n{out}",
                )
                return

            if "None detected" in out or "Outside the Matrix" in out:
                outside_markers = ["python -m venv", "activate"]
                missing = self._check_required_markers(out, outside_markers)
                if missing:
                    console.print("[red]KO (Outside Instructions)[/red]")
                    self.record_error(
                        exercise_label,
                        "Output Error",
                        f"Outside-venv instructions incomplete. Missing: {missing!r}\n"
                        f"Got:\n{out}",
                    )
                    return
                console.print("[green]OK (Outside Detection)[/green]")
            else:
                inside_markers = ["Environment Path:", "site-packages"]
                missing = self._check_required_markers(out, inside_markers)
                if missing:
                    console.print("[red]KO (Inside Details)[/red]")
                    self.record_error(
                        exercise_label,
                        "Output Error",
                        f"Inside-venv details incomplete. Missing: {missing!r}\nGot:\n{out}",
                    )
                    return
                console.print("[green]OK (Inside Detection)[/green]")
        except Exception as e:
             console.print(f"[red]KO (Execution Error: {e})[/red]")

    def test_loading_programs(self):
        console.print("\n[bold]Testing Exercise 1: Loading Programs[/bold]")
        exercise_label = "Exercise 1"
        
        # Check files
        path = self._load_module_path("ex01", "loading.py")
        if not path: path = self._load_module_path("ex1", "loading.py")
        
        if not path or not os.path.exists(path):
            console.print("[red]KO (Missing File)[/red]")
            self.record_error(exercise_label, "Missing File", "Could not find loading.py")
            return

        requirements = os.path.join(os.path.dirname(path), "requirements.txt")
        pyproject = os.path.join(os.path.dirname(path), "pyproject.toml")
        
        if not os.path.exists(requirements):
            self.record_error(exercise_label, "Missing File", "Missing requirements.txt")
        if not os.path.exists(pyproject):
            self.record_error(exercise_label, "Missing File", "Missing pyproject.toml")
        if not os.path.exists(requirements) or not os.path.exists(pyproject):
            return

        # Strict Check
        if not self.common_strict_check(
            path,
            exercise_label,
            allowed_imports=[
                "pandas", "requests", "matplotlib", "numpy", "sys", "importlib"
            ],
            allow_import_related_style_errors=True,
        ):
            return

        with open(path, "r", encoding="utf-8") as f:
            src = f.read()
        src_lower = src.lower()
        if ("numpy" not in src_lower or
                not any(tok in src for tok in ("np.random", "numpy.random", "np.arange", "numpy.arange"))):
            self.record_error(
                exercise_label,
                "Structure Error",
                "Dataset generation must come from numpy (e.g. numpy.random / numpy.arange), "
                "not only hardcoded lists or range().",
            )
        if "pip" not in src_lower or "poetry" not in src_lower:
            self.record_error(
                exercise_label,
                "Structure Error",
                "loading.py should explicitly demonstrate pip vs Poetry usage/comparison.",
            )
        req = open(requirements, "r", encoding="utf-8").read().lower()
        pyproj = open(pyproject, "r", encoding="utf-8").read().lower()
        for dep in ("pandas", "numpy", "matplotlib"):
            if dep not in req:
                self.record_error(
                    exercise_label,
                    "Dependency Error",
                    f"requirements.txt missing required dependency: {dep}",
                )
            if dep not in pyproj:
                self.record_error(
                    exercise_label,
                    "Dependency Error",
                    f"pyproject.toml missing required dependency: {dep}",
                )

        # Run
        try:
            cmd = [sys.executable, path]
            cwd = os.path.dirname(path)
            result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
            out = result.stdout + result.stderr
            if self.check_for_crash(out, exercise_label): return
            
            required_markers = ["LOADING STATUS", "Checking dependencies"]
            if self._check_required_markers(out, required_markers):
                console.print("[red]KO (Output Mismatch)[/red]")
                self.record_error(
                    exercise_label,
                    "Output Error",
                    f"Output doesn't match expected structure. Got:\n{out}",
                )
                return

            out_lower = out.lower()
            if "pip" not in out_lower or "poetry" not in out_lower:
                self.record_error(
                    exercise_label,
                    "Output Error",
                    "Output should mention both pip and Poetry management paths.",
                )

            # Subject: matplotlib visualization written to matrix_analysis.png
            if "Results saved to: matrix_analysis.png" in out:
                png_path = os.path.join(cwd, "matrix_analysis.png")
                if not os.path.isfile(png_path):
                    console.print("[red]KO (Missing PNG)[/red]")
                    self.record_error(
                        exercise_label,
                        "Output Error",
                        "Output claims results were saved to matrix_analysis.png, "
                        "but that file was not created next to loading.py.",
                    )
                    return
                if os.path.getsize(png_path) < 64:
                    console.print("[red]KO (Invalid PNG)[/red]")
                    self.record_error(
                        exercise_label,
                        "Output Error",
                        "matrix_analysis.png exists but is too small to be a real plot.",
                    )
                    return

            console.print("[green]OK[/green]")

        except Exception as e:
             console.print(f"[red]KO (Execution Error: {e})[/red]")

    def test_accessing_mainframe(self):
        console.print("\n[bold]Testing Exercise 2: Accessing the Mainframe[/bold]")
        exercise_label = "Exercise 2"
        path = self._load_module_path("ex02", "oracle.py")
        if not path: path = self._load_module_path("ex2", "oracle.py")
        
        if not path or not os.path.exists(path):
            console.print("[red]KO (Missing File)[/red]")
            self.record_error(exercise_label, "Missing File", "Could not find oracle.py")
            return

        # Check gitignore
        gitignore = os.path.join(os.path.dirname(path), ".gitignore")
        if not os.path.exists(gitignore):
            self.record_error(exercise_label, "Missing File", "Missing .gitignore")
        else:
            with open(gitignore, "r") as f:
                content = f.read()
                if ".env" not in content:
                    self.record_error(exercise_label, "Security Risk", ".env not found in .gitignore")

        env_example = os.path.join(os.path.dirname(path), ".env.example")
        if not os.path.exists(env_example):
            self.record_error(
                exercise_label,
                "Missing File",
                "Missing .env.example file (required by subject)",
            )
        else:
            with open(env_example, "r", encoding="utf-8") as f:
                ex_lines = f.read().splitlines()
            non_comment = [
                ln.strip()
                for ln in ex_lines
                if ln.strip() and not ln.strip().startswith("#")
            ]
            if not any("=" in ln for ln in non_comment):
                self.record_error(
                    exercise_label,
                    "Config Error",
                    ".env.example should document at least one KEY=value placeholder.",
                )
            joined = "\n".join(ex_lines)
            for key in self.required_oracle_keys:
                if key not in joined:
                    self.record_error(
                        exercise_label,
                        "Config Error",
                        f".env.example missing required key placeholder: {key}",
                    )

        # Strict Check
        if not self.common_strict_check(
            path, exercise_label, allowed_imports=["os", "sys", "dotenv"]
        ):
            return

        # Test Run 1: No Env
        try:
            cmd = [sys.executable, path]
            cwd = os.path.dirname(path)
            # Run with cleaned env to ensure no interference? 
            # But we need basic env vars.
            # Just run it.
            result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
            out = result.stdout + result.stderr
            if self.check_for_crash(out, exercise_label): return

            if "ORACLE STATUS" in out:
                console.print("[green]OK (Run)[/green]")
            else:
                console.print("[red]KO (Output Mismatch)[/red]")
                self.record_error(exercise_label, "Run Error", f"Unexpected output:\n{out}")

            # Run with explicit environment to validate dev/prod visibility.
            base_env = os.environ.copy()
            env_prod = dict(base_env)
            env_prod.update({
                "MATRIX_MODE": "production",
                "DATABASE_URL": "postgres://prod",
                "API_KEY": "secret_prod",
                "LOG_LEVEL": "INFO",
                "ZION_ENDPOINT": "https://zion.prod",
            })
            env_dev = dict(base_env)
            env_dev.update({
                "MATRIX_MODE": "development",
                "DATABASE_URL": "sqlite:///dev.db",
                "API_KEY": "secret_dev",
                "LOG_LEVEL": "DEBUG",
                "ZION_ENDPOINT": "http://localhost:9999",
            })
            prod_result = subprocess.run(
                cmd, cwd=cwd, capture_output=True, text=True, env=env_prod
            )
            dev_result = subprocess.run(
                cmd, cwd=cwd, capture_output=True, text=True, env=env_dev
            )
            out_prod = prod_result.stdout + prod_result.stderr
            out_dev = dev_result.stdout + dev_result.stderr
            if self.check_for_crash(out_prod, exercise_label): return
            if self.check_for_crash(out_dev, exercise_label): return
            if out_prod == out_dev:
                self.record_error(
                    exercise_label,
                    "Config Error",
                    "Development and production runs produce identical outputs; "
                    "subject requires visible configuration differences.",
                )
            if "production" not in out_prod.lower():
                self.record_error(
                    exercise_label,
                    "Config Error",
                    "Production run output should clearly display production mode.",
                )
            if "development" not in out_dev.lower():
                self.record_error(
                    exercise_label,
                    "Config Error",
                    "Development run output should clearly display development mode.",
                )

        except Exception as e:
             console.print(f"[red]KO (Execution Error: {e})[/red]")

    def run(self, exercise_name=None):
        console.print("[bold cyan]Testing Module 08: The Matrix[/bold cyan]")
        
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
                self.record_error(
                    "Exercise filter",
                    "Unknown exercise",
                    f"No exercise matches '{exercise_name}'.",
                )
        else:
            # Run all unique
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
