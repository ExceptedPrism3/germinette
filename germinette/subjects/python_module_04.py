import sys
import os
import ast
import json
from rich.console import Console
from rich.panel import Panel
from germinette.core import BaseTester
from germinette.utils import IOTester

console = Console()

class Tester(BaseTester):
    def __init__(self):
        self.exercises = [
            ("ft_ancient_text", self.test_archive_extraction),
            ("ft_archive_creation", self.test_archive_preservation),
            ("ft_stream_management", self.test_stream_management),
            ("ft_vault_security", self.test_vault_security),
            ("ft_crisis_response", self.test_crisis_response),
        ]
        self.grouped_errors = {}
        self.generated_files = []
        self._setup_test_data()

    def _setup_test_data(self):
        """Generates necessary test files for Module 04."""
        files = {
            "ancient_fragment.txt": "SECURE ARCHIVE FRAGMENT - 0x892B\nType: Text Data\nOrigin: Sector 7\nContent: The binary flow remains constant...",
            "classified_data.txt": "TOP SECRET - EYES ONLY\nSecurity Level: 5\nAccess Code: ALPHA-DELTA-9\nProtocol: Vault Access Confirmed",
            "security_protocols.txt": "PROTOCOL ALPHA: Verify all secure connections\nPROTOCOL BETA: Encrypt all outgoing data\nPROTOCOL GAMMA: Archive all transaction logs",
            "standard_archive.txt": "Archive ID: STD-2024-X\nStatus: Preserved\nRetention: Indefinite\nContent: Standard daily logs and system metrics.",
            "corrupted_archive.txt": "DATA_CORRUPTION_ERROR_0x7F4A"
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
            "ft_archive_extraction": 0,
            "ft_ancient_text": 0,
            "ft_archive_preservation": 1,
            "ft_archive_creation": 1,
            "ft_stream_management": 2,
            "ft_vault_security": 3,
            "ft_crisis_response": 4
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

        # Style Checks
        style_errors = self.check_flake8(found_path)
        if style_errors:
             console.print("[red]KO[/red]")
             self.record_error(exercise_label, "Style Error (Flake8)", style_errors)
             return None, None
        
        doc_errors = self.check_docstrings(found_path)
        if doc_errors:
             console.print("[red]KO[/red]")
             self.record_error(exercise_label, "Style Error (Missing Docstrings)", doc_errors)
             return None, None
            
        return "FOUND", found_path 

    def run(self, exercise_name=None):
        console.print("[bold cyan]Testing Module 04: Data Archivist[/bold cyan]")
        
        if os.getcwd() not in sys.path:
            sys.path.insert(0, os.getcwd())

        # Ensure test data is ready
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
        else:
            for _, func in self.exercises:
                func()
        
        # Cleanup
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

    def test_archive_extraction(self):
        console.print("\n[bold]Testing Exercise 0: ft_ancient_text[/bold]")
        exercise_label = "Exercise 0"
        status, path = self._load_module("ft_ancient_text", exercise_label)
        if not status: return

        import subprocess
        try:
            cmd = [sys.executable, path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            out = result.stdout + result.stderr

            if "=== CYBER ARCHIVES - EXTRACTION SYSTEM ===" not in out:
                console.print("[red]KO (Missing Header)[/red]")
                self.record_error(exercise_label, "Output Error", "Missing '=== CYBER ARCHIVES - EXTRACTION SYSTEM ==='")
                return
            
            if "SECURE ARCHIVE FRAGMENT" in out and "The binary flow remains constant" in out:
                console.print("[green]OK (Content matches)[/green]")
            else:
                 console.print("[red]KO (Content Mismatch)[/red]")
                 self.record_error(exercise_label, "Output Error", f"Output does not match 'ancient_fragment.txt' content.\nGot:\n{out}")
        except Exception as e:
             console.print(f"[red]KO (Execution Error: {e})[/red]")

    def test_archive_preservation(self):
        console.print("\n[bold]Testing Exercise 1: ft_archive_creation[/bold]")
        exercise_label = "Exercise 1"
        status, path = self._load_module("ft_archive_creation", exercise_label)
        if not status: return

        # Ensure target file doesn't exist
        if os.path.exists("new_discovery.txt"):
            os.remove("new_discovery.txt")

        import subprocess
        try:
            cmd = [sys.executable, path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            out = result.stdout

            if "=== CYBER ARCHIVES - PRESERVATION SYSTEM ===" not in out:
                 console.print("[red]KO (Missing Header)[/red]")
                 return

            if "Archive 'new_discovery.txt' ready" in out or "ready for long-term preservation" in out:
                 if os.path.exists("new_discovery.txt"):
                     with open("new_discovery.txt", "r") as f:
                         content = f.read()
                     if "[ENTRY" in content:
                          console.print("[green]OK (File Created & Content)[/green]")
                     else:
                          console.print("[red]KO (File Empty/Wrong Content)[/red]")
                          self.record_error(exercise_label, "Logic Error", f"File created but content weird:\n{content}")
                 else:
                     console.print("[red]KO (File Not Created)[/red]")
                     self.record_error(exercise_label, "Logic Error", "Script claimed success but 'new_discovery.txt' not found.")
            else:
                 console.print("[red]KO (Output Mismatch)[/red]")
                 self.record_error(exercise_label, "Output Error", f"Expected success message. Got:\n{out}")

        except Exception as e:
             console.print(f"[red]KO (Execution Error: {e})[/red]")

    def test_stream_management(self):
        console.print("\n[bold]Testing Exercise 2: ft_stream_management[/bold]")
        exercise_label = "Exercise 2"
        status, path = self._load_module("ft_stream_management", exercise_label)
        if not status: return

        import subprocess
        
        # Test Case: Normal input
        input_str = "ARCH_TEST\nSystems OK\n"
        try:
            cmd = [sys.executable, path]
            # Capture stdout and stderr separately
            proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = proc.communicate(input=input_str)
            
            if "=== CYBER ARCHIVES - COMMUNICATION SYSTEM ===" not in stdout:
                 console.print("[red]KO (Missing Header)[/red]")
                 return

            if "[STANDARD]" in stdout and "ARCH_TEST" in stdout:
                 console.print("[green]OK (Stdout)[/green]")
            else:
                 console.print("[red]KO (Stdout)[/red]")
                 self.record_error(exercise_label, "Output Error", f"Expected [STANDARD] log in stdout. Got:\n{stdout}")

            if "[ALERT]" in stderr:
                 console.print("[green]OK (Stderr)[/green]")
            else:
                 console.print("[red]KO (Stderr)[/red]")
                 self.record_error(exercise_label, "Output Error", f"Expected [ALERT] log in stderr. Got:\n{stderr}")

        except Exception as e:
             console.print(f"[red]KO ({e})[/red]")

    def test_vault_security(self):
        console.print("\n[bold]Testing Exercise 3: ft_vault_security[/bold]")
        exercise_label = "Exercise 3"
        status, path = self._load_module("ft_vault_security", exercise_label)
        if not status: return

        # Static Check: enforce 'with' statement
        try:
            with open(path, "r") as f:
                tree = ast.parse(f.read())
            has_with = any(isinstance(node, ast.With) for node in ast.walk(tree))
            if has_with:
                console.print("[green]OK (Uses 'with')[/green]")
            else:
                console.print("[red]KO (Missing 'with')[/red]")
                self.record_error(exercise_label, "Structure Error", "Must use 'with' statement for file operations.")
                return
        except:
            pass

        # Runtime Check
        import subprocess
        try:
            cmd = [sys.executable, path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            out = result.stdout

            if "=== CYBER ARCHIVES - VAULT SECURITY SYSTEM ===" not in out:
                 console.print("[red]KO (Header)[/red]")
                 return

            if "Vault automatically sealed" in out or "Access Code: ALPHA-DELTA-9" in out:
                 console.print("[green]OK (Logic)[/green]")
            else:
                 console.print("[red]KO (Logic)[/red]")
                 self.record_error(exercise_label, "Output Error", f"Expected vault operation logs. Got:\n{out}")
        except Exception as e:
             console.print(f"[red]KO ({e})[/red]")

    def test_crisis_response(self):
        console.print("\n[bold]Testing Exercise 4: ft_crisis_response[/bold]")
        exercise_label = "Exercise 4"
        status, path = self._load_module("ft_crisis_response", exercise_label)
        if not status: return

        # Check for try/except
        try:
            with open(path, "r") as f:
                tree = ast.parse(f.read())
            has_try = any(isinstance(node, ast.Try) for node in ast.walk(tree))
            if has_try:
                console.print("[green]OK (Uses try/except)[/green]")
            else:
                console.print("[red]KO (Missing try/except)[/red]")
                self.record_error(exercise_label, "Structure Error", "Must use try/except block.")
                return
        except: pass

        # Runtime Check
        import subprocess
        try:
            cmd = [sys.executable, path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            out = result.stdout

            if "=== CYBER ARCHIVES - CRISIS RESPONSE SYSTEM ===" not in out:
                 console.print("[red]KO (Header)[/red]")
                 return

            conditions = [
                "CRISIS ALERT",
                "RESPONSE: Archive not found",
                "STATUS: Crisis handled",
                "SUCCESS: Archive recovered"
            ]
            
            if all(c in out for c in conditions):
                console.print("[green]OK (Logic)[/green]")
            else:
                console.print("[red]KO (Logic)[/red]")
                self.record_error(exercise_label, "Output Error", f"Missing some crisis logs. Got:\n{out}")

        except Exception as e:
             console.print(f"[red]KO ({e})[/red]")
