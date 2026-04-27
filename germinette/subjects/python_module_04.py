import sys
import os
import ast
import importlib.util
from rich.console import Console
from rich.panel import Panel
from germinette.core import BaseTester
from germinette.utils import IOTester

console = Console()

class Tester(BaseTester):
    def __init__(self):
        self.exercises = [
            ("ft_ancient_text", self.test_ancient_text),
            ("ft_archive_creation", self.test_archive_creation),
            ("ft_stream_management", self.test_stream_management),
            ("ft_vault_security", self.test_vault_security),
        ]
        self.grouped_errors = {}
        self.generated_files = []
        self._setup_test_data()

    def _setup_test_data(self):
        """Generates necessary test files for Module 04."""
        files = {
            "ancient_fragment.txt": "SECURE ARCHIVE FRAGMENT - 0x892B\nType: Text Data\nOrigin: Sector 7\nContent: Digital preservation protocols established 2087\nKnowledge must survive the entropy wars\nEvery byte saved is a victory against oblivion",
            "standard_archive.txt": "Archive ID: STD-2024-X\nStatus: Preserved\nRetention: Indefinite\nContent: Knowledge preserved for humanity",
        }
        
        try:
            for name, content in files.items():
                if not os.path.exists(name):
                    with open(name, "w") as f:
                        f.write(content)
                    self.generated_files.append(name)
        except Exception as e:
            console.print(f"[red]Warning: Failed to create test data: {e}[/red]")

    def record_error(self, exercise_label, error_type, message):
        if exercise_label not in self.grouped_errors:
            self.grouped_errors[exercise_label] = []
        self.grouped_errors[exercise_label].append(f"[bold]{error_type}[/bold]\n{message}")

    def _load_module(self, module_name, exercise_label):
        cwd = os.getcwd()
        if os.path.exists(os.path.join(cwd, "python_module_04")):
            base_dir = os.path.join(cwd, "python_module_04")
        else:
            base_dir = cwd

        ex_map = {
            "ft_ancient_text": 0,
            "ft_archive_creation": 1,
            "ft_stream_management": 2,
            "ft_vault_security": 3,
        }
        
        expected_dir = None
        if module_name in ex_map:
            ex_num = ex_map[module_name]
            potential_dir = os.path.join(base_dir, f"ex{ex_num}")
            if os.path.exists(potential_dir):
                expected_dir = potential_dir
            else:
                 console.print("[red]KO (Directory Missing)[/red]")
                 msg = (f"[bold red]Directory not found[/bold red]\n\n"
                        f"Expected directory: [cyan]ex{ex_num}[/cyan]\n"
                        f"Location: {base_dir}\n")
                 self.record_error(exercise_label, "Missing Directory", msg)
                 return None, None

        target_file = f"{module_name}.py"
        found_path = os.path.join(expected_dir, target_file)
        
        if not os.path.exists(found_path):
             console.print("[red]KO (Missing File)[/red]")
             msg = (f"[bold red]File not found[/bold red]\n\n"
                    f"Expected: [cyan]{target_file}[/cyan]\n"
                    f"Directory: [cyan]{expected_dir}[/cyan]\n")
             self.record_error(exercise_label, "Missing File", msg)
             return None, None

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

        return "FOUND", found_path

    def run(self, exercise_name=None):
        console.print("[bold cyan]Testing Module 04: Data Archivist (v3.0)[/bold cyan]")
        
        if os.getcwd() not in sys.path:
            sys.path.insert(0, os.getcwd())

        self._setup_test_data()

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
            for _, func in self.exercises:
                func()
        
        for f in self.generated_files:
            try:
                if os.path.exists(f): os.remove(f)
            except: pass
            
        if self.grouped_errors:
            console.print()
            console.rule("[bold red]Detailed Error Report[/bold red]")
            console.print()
            for label, messages in self.grouped_errors.items():
                content = "\n\n[dim]────────────────────────────────[/dim]\n\n".join(messages)
                console.print(Panel(content, title=f"[bold red]{label}[/bold red]", border_style="red", expand=False))
                console.print()

    # --- Exercise Tests ---

    def _enforce_no_with_before_ex3(self, path, exercise_label):
        try:
            with open(path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
            has_with = any(isinstance(node, ast.With) for node in ast.walk(tree))
            if has_with:
                self.record_error(
                    exercise_label,
                    "Structure Error",
                    "The 'with' statement is introduced in Exercise 3 only and "
                    "must not be used before then.",
                )
                return False
        except Exception:
            pass
        return True

    def _load_module_object(self, path):
        module_name = f"_germinette_mod04_{os.path.basename(path).replace('.py', '')}"
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_ancient_text(self):
        console.print("\n[bold]Testing Exercise 0: ft_ancient_text[/bold]")
        exercise_label = "Exercise 0"
        status, path = self._load_module("ft_ancient_text", exercise_label)
        if not status: return

        # v3.0: uses sys.argv and may use typing.IO annotations.
        if not self.verify_strict(
            path,
            exercise_label,
            allowed_funcs=['open', 'read', 'close', 'print', 'len'],
            allowed_imports=['sys', 'typing'],
        ):
            return
        if not self._enforce_no_with_before_ex3(path, exercise_label):
            return

        import subprocess
        # Test 1: File exists
        try:
            cmd = [sys.executable, path, "ancient_fragment.txt"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            out = result.stdout + result.stderr
            if self.check_for_crash(out, exercise_label): return

            # v3.0 Header
            if "=== Cyber Archives Recovery ===" not in out:
                console.print("[red]KO (Missing Header)[/red]")
                self.record_error(exercise_label, "Output Error", "Missing '=== Cyber Archives Recovery ==='")
                return
            
            if "Digital preservation protocols established 2087" in out:
                console.print("[green]OK (Content matches)[/green]")
            else:
                 console.print("[red]KO (Content Mismatch)[/red]")
                 self.record_error(exercise_label, "Output Error", f"Output does not match 'ancient_fragment.txt' content.\nGot:\n{out}")
        except Exception as e:
             console.print(f"[red]KO (Execution Error: {e})[/red]")

        # Test 2: No Arguments
        try:
             cmd = [sys.executable, path]
             result = subprocess.run(cmd, capture_output=True, text=True)
             out = result.stdout + result.stderr
             if "Usage:" in out or "Error:" in out or "provide" in out.lower():
                  console.print("[green]OK (No Args handled)[/green]")
             else:
                  console.print("[red]KO (No Args handled)[/red]")
                  self.record_error(exercise_label, "Handling Error", "Script must handle missing argument (no filename provided).")
        except Exception as e:
             pass

        # Test 3: File Doesn't Exist
        try:
             cmd = [sys.executable, path, "non_existent_file.txt"]
             result = subprocess.run(cmd, capture_output=True, text=True)
             out = result.stdout + result.stderr
             if "FileNotFoundError" in out or "Error:" in out or "not found" in out.lower():
                  console.print("[green]OK (Missing file handled)[/green]")
             else:
                  console.print("[red]KO (Missing file handled)[/red]")
                  self.record_error(exercise_label, "Handling Error", "Script must catch FileNotFoundError / display error.")
        except Exception as e:
             pass

    def test_archive_creation(self):
        console.print("\n[bold]Testing Exercise 1: ft_archive_creation[/bold]")
        exercise_label = "Exercise 1"
        status, path = self._load_module("ft_archive_creation", exercise_label)
        if not status: return

        # v3.0: append '#' at EOL and save by user-provided filename.
        if not self.verify_strict(
            path,
            exercise_label,
            allowed_funcs=['open', 'read', 'write', 'close', 'print', 'input', 'len'],
            allowed_imports=['sys', 'typing'],
        ):
            return
        if not self._enforce_no_with_before_ex3(path, exercise_label):
            return

        target_file = "test_output_archive.txt"
        if os.path.exists(target_file):
            os.remove(target_file)

        import subprocess
        try:
            cmd = [sys.executable, path, "ancient_fragment.txt"]
            proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = proc.communicate(input=f"{target_file}\n")
            out = stdout + stderr

            if self.check_for_crash(out, exercise_label): return

            if "=== Cyber Archives Recovery & Preservation ===" not in out:
                 console.print("[red]KO (Missing Header)[/red]")
                 self.record_error(
                    exercise_label,
                    "Output Error",
                    "Missing '=== Cyber Archives Recovery & Preservation ==='",
                )
                 return

            if os.path.exists(target_file):
                with open(target_file, "r") as f:
                    content = f.read()
                
                # Subject requires trailing '#' at end of each line.
                lines = [ln for ln in content.splitlines() if ln]
                if lines and all(ln.endswith("#") for ln in lines):
                    console.print("[green]OK (File Created & Transformed)[/green]")
                else:
                    console.print("[red]KO (File Content Missing trailing '#')[/red]")
                    self.record_error(
                        exercise_label,
                        "Logic Error",
                        "File created but transformed lines do not all end with '#'.\n"
                        f"Got:\n{content}",
                    )
                
                os.remove(target_file)
            else:
                console.print("[red]KO (File Not Created)[/red]")
                self.record_error(exercise_label, "Logic Error", f"Script claimed success but '{target_file}' not found.")

        except Exception as e:
             console.print(f"[red]KO (Execution Error: {e})[/red]")

    def test_stream_management(self):
        console.print("\n[bold]Testing Exercise 2: ft_stream_management[/bold]")
        exercise_label = "Exercise 2"
        status, path = self._load_module("ft_stream_management", exercise_label)
        if not status: return

        # v3.0: reuse Ex1 logic, sys.stdin for prompt answer, and sys.stderr for errors.
        if not self.verify_strict(
            path,
            exercise_label,
            allowed_funcs=['open', 'read', 'readline', 'write', 'flush', 'close', 'print', 'len'],
            allowed_imports=['sys', 'typing'],
        ):
            return
        if not self._enforce_no_with_before_ex3(path, exercise_label):
            return

        # Explicitly check for NO input() function
        import ast
        try:
            with open(path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
            has_input = any(isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'input' for node in ast.walk(tree))
            if has_input:
                console.print("[red]KO (Forbidden Function input())[/red]")
                self.record_error(exercise_label, "Forbidden Magic", "You must use sys.stdin directly, not the input() function.")
                return
        except Exception:
            pass

        import subprocess
        input_str = "/etc/passwd\n"
        try:
            cmd = [sys.executable, path, "ancient_fragment.txt"]
            proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = proc.communicate(input=input_str)
            
            if self.check_for_crash(stdout + stderr, exercise_label): return

            if "=== Cyber Archives Recovery & Preservation ===" not in stdout:
                 console.print("[red]KO (Missing Header)[/red]")
                 self.record_error(
                    exercise_label,
                    "Output Error",
                    "Missing '=== Cyber Archives Recovery & Preservation ==='",
                )
                 return

            if "Digital preservation protocols established 2087" in stdout:
                 console.print("[green]OK (Read/Transform flow)[/green]")
            else:
                 console.print("[red]KO (Read/Transform flow)[/red]")
                 self.record_error(
                    exercise_label,
                    "Output Error",
                    f"Expected recovered content in stdout. Got:\n{stdout}",
                )

            # Stderr must contain prefixed exception message for save failure.
            if "[STDERR]" in stderr and "Error opening file" in stderr:
                 console.print("[green]OK (Stderr Prefix + Routing)[/green]")
            else:
                 console.print("[red]KO (Stderr Prefix + Routing)[/red]")
                 self.record_error(
                    exercise_label,
                    "Output Error",
                    "Expected error lines in sys.stderr with '[STDERR]' prefix.\n"
                    f"stdout:\n{stdout}\n\nstderr:\n{stderr}",
                )

        except Exception as e:
             console.print(f"[red]KO ({e})[/red]")

    def test_vault_security(self):
        console.print("\n[bold]Testing Exercise 3: ft_vault_security[/bold]")
        exercise_label = "Exercise 3"
        status, path = self._load_module("ft_vault_security", exercise_label)
        if not status: return

        if not self.verify_strict(path, exercise_label, allowed_funcs=['open', 'read', 'write', 'print', 'len', 'tuple']):
            return

        # Check for `with`
        try:
            with open(path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
            has_with = any(isinstance(node, ast.With) for node in ast.walk(tree))
            if has_with:
                console.print("[green]OK (Uses 'with')[/green]")
            else:
                console.print("[red]KO (Missing 'with')[/red]")
                self.record_error(exercise_label, "Structure Error", "Must use 'with' statement for file operations.")
                return
        except Exception:
            pass

        import subprocess
        try:
            cmd = [sys.executable, path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            out = result.stdout + result.stderr
            if self.check_for_crash(out, exercise_label): return

            if "=== Cyber Archives Security ===" not in out:
                 console.print("[red]KO (Header)[/red]")
                 self.record_error(
                    exercise_label,
                    "Output Error",
                    "Missing '=== Cyber Archives Security ==='",
                )
                 return

            module = self._load_module_object(path)
            fn = getattr(module, "secure_archive", None) if module else None
            if fn is None:
                self.record_error(
                    exercise_label,
                    "Structure Error",
                    "Missing required function: secure_archive(...)",
                )
                return

            read_ok = fn("ancient_fragment.txt")
            if not isinstance(read_ok, tuple) or len(read_ok) != 2:
                self.record_error(
                    exercise_label,
                    "Logic Error",
                    "secure_archive() must return a tuple(bool, str).",
                )
                return
            if not isinstance(read_ok[0], bool) or not isinstance(read_ok[1], str):
                self.record_error(
                    exercise_label,
                    "Logic Error",
                    "secure_archive() tuple must be (bool, str).",
                )
                return

            miss = fn("/not/existing/file")
            if not isinstance(miss, tuple) or len(miss) != 2 or miss[0] is not False:
                self.record_error(
                    exercise_label,
                    "Logic Error",
                    "Reading a nonexistent file should return (False, <error message>).",
                )
                return

            write_path = "vault_security_test_output.txt"
            try:
                write_ok = fn(write_path, "write", "vault payload")
                if not isinstance(write_ok, tuple) or len(write_ok) != 2 or write_ok[0] is not True:
                    self.record_error(
                        exercise_label,
                        "Logic Error",
                        "Writing via secure_archive should return (True, <message>).",
                    )
                    return
                if not os.path.exists(write_path):
                    self.record_error(
                        exercise_label,
                        "Logic Error",
                        "Write operation returned success but output file was not created.",
                    )
                    return
            finally:
                if os.path.exists(write_path):
                    os.remove(write_path)

            console.print("[green]OK (secure_archive contract)[/green]")

        except Exception as e:
             console.print(f"[red]KO ({e})[/red]")
