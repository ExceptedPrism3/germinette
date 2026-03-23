import os
import re
import sys
import importlib
from pathlib import Path
from urllib.parse import quote
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table

console = Console()


def _terminal_hyperlink_url_for_file(abs_path: str) -> str:
    """
    URL for Rich [link=...] / OSC-8 hyperlinks.

    In VS Code / Cursor's integrated terminal, ``vscode://file/...`` and plain
    ``file://`` often go to the OS handler (wrong app / new window). The
    ``vscode://vscode/open?url=file%3A%2F%2F...`` form is handled by the running
    editor and opens the file in the same window.

    Cursor registers the same ``vscode://`` handler. Other terminals fall back
    to ``file:///...``.
    """
    p = Path(abs_path).resolve()
    in_editor_terminal = (
        os.environ.get("TERM_PROGRAM") == "vscode"
        or os.environ.get("CURSOR_TRACE_ID")
        or os.environ.get("CURSOR_AGENT")
    )

    if in_editor_terminal:
        try:
            file_uri = p.as_uri()
            return "vscode://vscode/open?url=" + quote(file_uri, safe="")
        except ValueError:
            pass

    try:
        return p.as_uri()
    except ValueError:
        return ""


def _flake8_first_line_col(flake8_first_line: str) -> tuple[int, int] | None:
    """Parse line/column before ``E###`` / ``W###`` (works with ``C:\\...`` paths)."""
    m = re.search(r"(\d+):(\d+):\s*[A-Z]\d{3}\s", flake8_first_line)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None

class ModuleDetector:
    """Detects which module the current directory corresponds to."""
    
    MODULE_SIGNATURES = {
        "python_module_00": {
            "files": ["ft_hello_garden.py", "ex0/ft_hello_garden.py"],
            "dirs": ["ex0"]
        },
        "python_module_01": {
            "files": [
                "ft_garden_intro.py", "ex0/ft_garden_intro.py",
                "ft_garden_data.py", "ex1/ft_garden_data.py",
                "ft_plant_growth.py", "ex2/ft_plant_growth.py",
                "ft_plant_factory.py", "ex3/ft_plant_factory.py",
                "ft_garden_security.py", "ex4/ft_garden_security.py",
                "ft_plant_types.py", "ex5/ft_plant_types.py",
                "ft_garden_analytics.py", "ex6/ft_garden_analytics.py"
            ],
            "dirs": ["ex0", "ex1", "ex2", "ex3", "ex4", "ex5", "ex6"],
        },
        "python_module_02": {
            "files": [
                "ft_first_exception.py", "ex0/ft_first_exception.py",
                "ft_different_errors.py", "ex1/ft_different_errors.py",
                "ft_custom_errors.py", "ex2/ft_custom_errors.py",
                "ft_finally_block.py", "ex3/ft_finally_block.py",
                "ft_raise_errors.py", "ex4/ft_raise_errors.py",
                "ft_garden_management.py", "ex5/ft_garden_management.py"
            ],
            "dirs": ["ex0", "ex1", "ex2", "ex3", "ex4", "ex5"]
        },
        "a_maze_ing": {
            "files": ["a_maze_ing.py", "Makefile"],
            "dirs": []
        },
        "python_module_03": {
            "files": [
                "ft_command_quest.py", "ex0/ft_command_quest.py",
                "ft_score_analytics.py", "ex1/ft_score_analytics.py"
            ],
            "dirs": ["ex0", "ex1", "ex2", "ex3", "ex4", "ex5", "ex6"]
        },
        "python_module_04": {
            "files": [
                "ft_ancient_text.py", "ex0/ft_ancient_text.py",
                "ft_archive_creation.py", "ex1/ft_archive_creation.py"
            ],
            "dirs": ["ex0", "ex1", "ex2", "ex3", "ex4"]
        },
        "python_module_05": {
            "files": [
                "stream_processor.py", "ex0/stream_processor.py",
                "data_stream.py", "ex1/data_stream.py",
                "nexus_pipeline.py", "ex2/nexus_pipeline.py"
            ],
            "dirs": ["ex0", "ex1", "ex2"]
        },
        "python_module_06": {
            "files": ["ft_sacred_scroll.py", "ft_import_transmutation.py"],
            "dirs": ["alchemy"]
        },
        "python_module_07": {
            "files": ["ex0/Card.py", "ex1/Deck.py", "ex2/EliteCard.py", "ex3/GameEngine.py", "ex4/TournamentPlatform.py"],
            "dirs": ["ex0", "ex1", "ex2", "ex3", "ex4"]
        },
        "python_module_08": {
            "files": ["ex0/construct.py", "ex1/loading.py", "ex2/oracle.py"],
            "dirs": ["ex0", "ex1", "ex2"]
        },
        "python_module_09": {
            "files": ["ex0/space_station.py", "ex1/alien_contact.py", "ex2/space_crew.py"],
            "dirs": ["ex0", "ex1", "ex2"]
        },
        "python_module_10": {
            "files": [
                "ex0/lambda_spells.py",
                "ex1/higher_magic.py",
                "ex2/scope_mysteries.py",
                "ex3/functools_artifacts.py",
                "ex4/decorator_mastery.py",
            ],
            "dirs": ["ex0", "ex1", "ex2", "ex3", "ex4"],
        },
    }

    @classmethod
    def detect(cls):
        """Scans current directory and returns the detected module name or None."""
        cwd = os.getcwd()
        
        for mod_name, signature in cls.MODULE_SIGNATURES.items():
            # Check for specific files
            for rel_path in signature.get("files", []):
                if os.path.exists(os.path.join(cwd, rel_path)):
                    console.print(f"[bold green]Detected {mod_name} based on {rel_path}[/bold green]")
                    return mod_name
            
            # Check for directories (less specific, but helpful)
            # Only if strictly unique directories exist?
            # "ex0" is common, so maybe relies on files mostly.
            
        return None

class GerminetteRunner:
    def __init__(self):
        self.subjects_dir = os.path.join(os.path.dirname(__file__), "subjects")
    
    def list_modules(self):
        modules = []
        if os.path.exists(self.subjects_dir):
            for f in os.listdir(self.subjects_dir):
                if f.startswith("python_module_") and f.endswith(".py"):
                    modules.append(f[:-3])
        return sorted(modules)

    def interactive_menu(self):
        # Auto-detect first
        detected = ModuleDetector.detect()
        if detected:
             console.print(f"Auto-running tests for [bold cyan]{detected}[/bold cyan]...")
             return self.run_module(detected)

        modules = self.list_modules()
        if not modules:
            console.print("[red]No modules found in subjects directory![/red]")
            return None
        
        # Hardcode A-Maze-ing for now as it doesn't follow naming convention
        modules.append("a_maze_ing")
        console.print("[bold]Available Modules:[/bold]")
        for i, mod in enumerate(modules, 1):
             display_name = mod
             coming_soon = ["a_maze_ing"]
             if mod in coming_soon:
                 display_name += " [yellow](Coming Soon 🚧)[/yellow]"
             


             console.print(f"{i}. {display_name}")
        
        console.print("\n[yellow]Could not auto-detect module in this directory.[/yellow]")
        console.print("Run with: [bold]germinette <module_name>[/bold]")
        return None

    @staticmethod
    def cleanup_pycache(root_dir=None):
        """Recursively removes __pycache__ directories."""
        if root_dir is None:
            root_dir = os.getcwd()
        
        for dirpath, dirnames, filenames in os.walk(root_dir):
            if "__pycache__" in dirnames:
                cache_path = os.path.join(dirpath, "__pycache__")
                try:
                    import shutil
                    shutil.rmtree(cache_path)
                    # console.print(f"[dim]Cleaned: {cache_path}[/dim]")
                except Exception as e:
                    pass
            # Don't walk into __pycache__ (though we just deleted it)
            if "__pycache__" in dirnames:
                dirnames.remove("__pycache__")

    def run_module(self, module_name, exercise=None):
        """
        Run tests for a subject module.

        Returns:
            True: tests ran and nothing was recorded in grouped_errors.
            False: tests ran but at least one error was recorded (or no grouped_errors attr).
            None: module could not be loaded or run (missing module, invalid Tester, etc.).
        """
        try:
            # Dynamically import the module checker
            mod = importlib.import_module(f"germinette.subjects.{module_name}")
            tester = getattr(mod, "Tester")()
            tester.run(exercise)
            ge = getattr(tester, "grouped_errors", None)
            if isinstance(ge, dict):
                return len(ge) == 0
            return False
        except ModuleNotFoundError:
            import difflib
            console.print(f"[bold red]❌ Module '{module_name}' not found![/bold red]")
            
            # Smart suggestions
            available = self.list_modules()
            matches = difflib.get_close_matches(module_name, available, n=1, cutoff=0.6)
            
            if matches:
                 console.print(f"\n[green]Did you mean [bold]{matches[0]}[/bold]?[/green]")
            
            console.print("\n[bold]Available Modules:[/bold]")
            for m in available:
                  console.print(f"- {m}")
            return None

        except AttributeError:
            console.print(f"[red]Module {module_name} is invalid (missing Tester class).[/red]")
            return None
        except Exception as e:
            import traceback
            console.print(f"[red]Error loading module: {e}[/red]")
            traceback.print_exc()
            return None

class BaseTester:
    def run(self, exercise_name=None):
        raise NotImplementedError

    def _run_script(self, path):
        """Runs a python script and returns stdout."""
        import subprocess
        try:
            result = subprocess.run(
                [sys.executable, path],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            # Return stderr as well for error checking
            return e.stdout + e.stderr
        except Exception as e:
            return str(e)

    def check_for_crash(self, output, label):
        """
        Checks if the script output contains runtime crash indicators.
        Returns True if a crash is detected (and prints KO), False otherwise.
        """
        if "Traceback (most recent call last):" in output or \
           "SyntaxError:" in output or \
           "IndentationError:" in output or \
           "AttributeError:" in output: # Added AttributeError explicitly for safety
            
            # If explicit "Runtime Error" is already recorded, maybe we don't need to duplicate?
            # But this helper is meant to BE the check.
            
            # Simple heuristic: if these strings are present, it's a crash.
            # Exceptions: If the exercise EXPECTS to print a traceback (Mod 02).
            # We will handle Mod 02 specifically later if needed.
            
            # Capture the error message (last few lines usually)
            self.record_error(label, "Runtime Error", f"Script crashed during execution:\n{output.strip()}")
            console.print("[red]KO[/red]")
            return True
        return False

    def check_docstrings(self, path):
        """Checks if the module itself and all classes/functions have docstrings."""
        import ast
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
            
            missing = []
            
            # Check Module-level Docstring (Top of file)
            if not ast.get_docstring(tree):
                 missing.append(f"Line 1: Missing module-level docstring (top of file)")

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                    # Strictly check everything
                    if not ast.get_docstring(node):
                        node_type = "Class" if isinstance(node, ast.ClassDef) else "Method"
                        missing.append(f"Line {node.lineno}: Missing docstring for {node_type} '{node.name}'")
            
            if missing:
                return "\n".join(missing)
            return None
            
        except Exception as e:
            return f"Error checking docstrings: {e}"

    def check_flake8(self, path):
        """Runs flake8 and returns None if compliant, or error string if violations found."""
        import subprocess
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "flake8", path],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return None
            else:
                # Parse and clean output
                # Output format: file:line:col: code message
                lines = result.stdout.strip().splitlines()
                cleaned_lines = []
                for line in lines:
                    # Remove file path (keep only line:col: code message)
                    parts = line.split(':', 1) # Split at first colon (after filename)
                    if len(parts) > 1:
                        cleaned_lines.append(f"Line {parts[1].strip()}")
                    else:
                        cleaned_lines.append(line)

                abs_path = os.path.normpath(os.path.abspath(path))
                fname = os.path.basename(abs_path)
                link_url = _terminal_hyperlink_url_for_file(abs_path)
                if link_url:
                    file_link = f"[link={link_url}]{escape(fname)}[/link]"
                else:
                    file_link = escape(fname)

                body = "\n".join(escape(line) for line in cleaned_lines)
                path_hint = f"\n[dim]{escape(abs_path)}[/dim]"

                # VS Code / Cursor: terminal often Ctrl+clicks ``path:line:col`` in plain text
                open_hint = ""
                if lines:
                    lc = _flake8_first_line_col(lines[0])
                    if lc:
                        ln, co = lc
                        plink = f"{abs_path}:{ln}:{co}"
                        open_hint = (
                            f"\n[dim]Or Ctrl+click:[/dim] [bold]{escape(plink)}[/bold]"
                        )

                return (
                    f"Flake8 — source file: {file_link}"
                    f"{path_hint}{open_hint}\n\n{body}"
                )

        except Exception as e:
            return f"Error running flake8: {e}"

    # Credit to @eloiberlinger1 (GitHub PR #3) for implementing mandatory type hint checks across module exercises!
    def check_type_hints(self, path):
        """Checks if all functions and methods have type hints (annotations)."""
        import ast
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
            
            missing = []
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if node.name.startswith("__") and node.name != "__init__":
                        continue
                    
                    # Check return type annotation
                    if node.returns is None:
                        missing.append(f"Line {node.lineno}: Missing return type hint for function '{node.name}'")
                    
                    # Check parameter type annotations (skip 'self' and 'cls')
                    for arg in node.args.args:
                        if arg.arg in ('self', 'cls'):
                            continue
                        if arg.annotation is None:
                            missing.append(f"Line {node.lineno}: Missing type hint for parameter '{arg.arg}' in function '{node.name}'")
            
            if missing:
                return "\n".join(missing)
            return None
            
        except Exception as e:
            return f"Error checking type hints: {e}"

    def check_try_except(self, path, exercise_label):
        """Checks if the file contains at least one try...except block."""
        import ast
        try:
            with open(path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
            
            has_try = False
            for node in ast.walk(tree):
                if isinstance(node, ast.Try):
                    has_try = True
                    break
            
            if not has_try:
                console.print(f"[red]KO (Strictness: Missing try/except)[/red]")
                # We return the error string instead of printing locally to allow caller to handle recording?
                # But BaseTester usually returns strings?
                # The existing methods return strings.
                # However, python_module_02 implementation printed directly.
                # To be consistent with check_docstrings, I should return error string or None.
                return "Strict check failed: You MUST use 'try/except' blocks."
            return None
        except Exception as e:
            return f"AST Error in check_try_except: {e}"

    def check_authorized_functions(self, path, allowed):
        """Checks if all called functions are in the allowed list (or built-in exceptions)."""
        import ast
        import builtins
        
        # Always allow exceptions (classes inheriting BaseException)
        builtin_exceptions = {item for item in dir(builtins) 
                              if isinstance(getattr(builtins, item), type) 
                              and issubclass(getattr(builtins, item), BaseException)}
        
        # Per-exercise ``allowed`` list is authoritative for builtins; exceptions + super are extra.
        allowed_set = set(allowed).union(builtin_exceptions).union({'super'})

        try:
            with open(path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
            
            violation = None
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                     func_name = None
                     if isinstance(node.func, ast.Name):
                         func_name = node.func.id
                     elif isinstance(node.func, ast.Attribute):
                         # Handle obj.method() ?
                         # If checking strict functions, usually we check builtins.
                         # Methods on objects (e.g. list.append) are hard to filter via AST without type interference.
                         # We usually only restrict global builtins.
                         pass
                     
                     if func_name and func_name in dir(builtins):
                         if func_name not in allowed_set:
                             violation = func_name
                             break
            
            if violation:
                return f"You used '{violation}()' which is NOT authorized.\nAuthorized: {', '.join(allowed)}"
            return None
                
        except Exception as e:
            return f"AST Error in check_authorized_functions: {e}"

    def check_no_file_io(self, path):
        """Checks if file I/O operations (open) are present."""
        import ast
        try:
            with open(path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id == 'open':
                         return "File I/O Forbidden: 'open()' function detected."
            return None
        except Exception as e:
            return f"AST Error in check_no_file_io: {e}"

    def check_imports(self, path, allowed_modules):
        """Checks if only allowed modules are imported."""
        import ast
        try:
            with open(path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
            
            # __future__ is always legal (e.g. `from __future__ import annotations`).
            # typing_extensions: backport for Self, ParamSpec, etc. on Python < 3.11 (e.g. 42 lab 3.10)
            allowed_set = set(allowed_modules).union(
                {'typing', 'typing_extensions', 'collections', '__future__'}
            )
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.split('.')[0] not in allowed_set:
                            return f"Forbidden Import: '{alias.name}' is not authorized."
                elif isinstance(node, ast.ImportFrom):
                    # Allow relative imports (level > 0)
                    if node.level > 0:
                        continue
                    if node.module and node.module.split('.')[0] not in allowed_set:
                        return f"Forbidden Import: '{node.module}' is not authorized."
            return None
        except Exception as e:
            return f"AST Error in check_imports: {e}"

    def verify_strict(self, path, exercise_label, allowed_funcs, allowed_imports=["sys"], enforce_try_except=False):
        """
        Runs a suite of strict checks:
        1. No File I/O
        2. Authorized Imports Only
        3. Try/Except (Optional)
        4. Authorized Functions Only
        """
        file_prefix = f"[bold cyan]File:[/bold cyan] [cyan]{os.path.basename(path)}[/cyan]\n\n"

        # 1. No File I/O
        err = None
        if 'open' not in allowed_funcs:
            err = self.check_no_file_io(path)
            
        if err:
            console.print(f"[red]KO (Forbidden Operation)[/red]")
            # Assuming 'record_error' is available on self (It is in Tester subclass, but BaseTester lacks it?)
            # BaseTester doesn't have record_error?
            # Tester subclasses implement record_error.
            # BaseTester is abstract base.
            # We should assume self.record_error exists or fallback.
            # But Python is dynamic. Verify Tester has it. Yes.
            if hasattr(self, 'record_error'):
                self.record_error(exercise_label, "Forbidden Operation", file_prefix + err)
            else:
                console.print(err)
            return False

        # 2. Imports
        err = self.check_imports(path, allowed_imports)
        if err:
            console.print(f"[red]KO (Forbidden Import)[/red]")
            if hasattr(self, 'record_error'):
                self.record_error(exercise_label, "Forbidden Import", file_prefix + err)
            else:
                console.print(err)
            return False

        # 3. Try/Except (if required)
        if enforce_try_except:
            err = self.check_try_except(path, exercise_label)
            if err:
                console.print(f"[red]KO (Strictness)[/red]")
                if hasattr(self, 'record_error'):
                    self.record_error(exercise_label, "Structure Error", file_prefix + err)
                else:
                    console.print(err)
                return False

        # 4. Authorized Functions
        err = self.check_authorized_functions(path, allowed_funcs)
        if err:
            console.print(f"[red]KO (Forbidden Function)[/red]")
            if hasattr(self, 'record_error'):
                self.record_error(exercise_label, "Authorized Functions", file_prefix + err)
            else:
                console.print(err)
            return False
        
        return True

