import sys
import os
import ast
import subprocess
import tempfile
from pathlib import Path
from rich.console import Console
from germinette.core import BaseTester

console = Console()

class Tester(BaseTester):
    def __init__(self):
        super().__init__()
        self.title = "[bold cyan]Testing Module 04: Data Archivist (v3.0)[/bold cyan]"
        self.exercises = [
            ("ft_ancient_text", self.test_ancient_text),
            ("ft_archive_creation", self.test_archive_creation),
            ("ft_stream_management", self.test_stream_management),
            ("ft_vault_security", self.test_vault_security),
        ]
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

    def _execute(self, path, label, directory, args=(), answer=""):
        try:
            result = subprocess.run(
                [sys.executable, path, *map(str, args)], cwd=directory,
                input=answer, capture_output=True, text=True, timeout=15,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            self.record_error(label, "Execution Error", str(exc))
            return None
        if result.returncode:
            self.record_error(label, "Runtime Error", result.stdout + result.stderr)
            return None
        return result

    def _prepare(self, name, label, functions):
        status, path = self._load_module(name, label)
        if not status:
            return None
        if not self.verify_strict(
            path, label, functions + ['str', 'int', 'float', 'list', 'dict', 'set', 'tuple'],
            allowed_imports=['sys', 'typing'] if name != 'ft_vault_security' else [],
        ):
            return None
        if name != 'ft_vault_security' and not self._enforce_no_with_before_ex3(path, label):
            return None
        return path

    def test_ancient_text(self):
        label = "Exercise 0"
        path = self._prepare('ft_ancient_text', label, ['open', 'read', 'close', 'print', 'len'])
        if not path:
            return
        with tempfile.TemporaryDirectory(prefix='germinette-archive-') as directory:
            source = Path(directory) / 'fragment.txt'
            content = 'Unique archive fragment 731\nSecond line\n'
            source.write_text(content, encoding='utf-8')
            result = self._execute(path, label, directory, [source])
            if result and content not in result.stdout:
                self.record_error(label, 'Read Error', 'Display the complete file contents.\n' + result.stdout)
            for args in ([], [Path(directory) / 'missing.txt'], [Path(directory)]):
                result = self._execute(path, label, directory, args)
                if result and not (result.stdout + result.stderr).strip():
                    self.record_error(label, 'Handling Error', 'Explain missing arguments and unreadable files.')

    def test_archive_creation(self):
        label = 'Exercise 1'
        path = self._prepare('ft_archive_creation', label,
                             ['open', 'read', 'write', 'close', 'print', 'input', 'len'])
        if not path:
            return
        with tempfile.TemporaryDirectory(prefix='germinette-archive-') as directory:
            source = Path(directory) / 'fragment.txt'
            target = Path(directory) / 'saved.txt'
            content = 'First record\n\nFinal record'
            source.write_text(content, encoding='utf-8')
            target.write_text('old content that must be replaced', encoding='utf-8')
            result = self._execute(path, label, directory, [source], str(target) + '\n')
            expected = [line + '#' for line in content.splitlines()]
            if result and (not target.is_file() or target.read_text().splitlines() != expected):
                self.record_error(label, 'Transformation Error', 'Preserve every input line, append # to each, and replace the destination.')
            target.unlink(missing_ok=True)
            result = self._execute(path, label, directory, [source], '\n')
            if result and any(item != source for item in Path(directory).iterdir()):
                self.record_error(label, 'Save Error', 'An empty destination must not create a file.')

    def test_stream_management(self):
        label = 'Exercise 2'
        path = self._prepare('ft_stream_management', label,
                             ['open', 'read', 'readline', 'write', 'flush', 'close', 'print', 'len'])
        if not path:
            return
        with tempfile.TemporaryDirectory(prefix='germinette-stream-') as directory:
            source = Path(directory) / 'fragment.txt'
            source.write_text('Stream payload\n', encoding='utf-8')
            # A directory is an unwritable file target regardless of user privileges.
            result = self._execute(path, label, directory, [source], directory + '\n')
            if result and ('[STDERR]' not in result.stderr or not result.stderr.strip()):
                self.record_error(label, 'Stream Error', 'Send prefixed save errors to stderr.')
            result = self._execute(path, label, directory, [Path(directory) / 'missing'], '\n')
            if result and ('[STDERR]' not in result.stderr or '[STDERR]' in result.stdout):
                self.record_error(label, 'Stream Error', 'Send prefixed read errors to stderr, not stdout.')
            target = Path(directory) / 'saved.txt'
            result = self._execute(path, label, directory, [source], str(target) + '\n')
            if result and (not target.is_file() or target.read_text().splitlines() != ['Stream payload#']):
                self.record_error(label, 'Stream Error', 'Read a destination from stdin and save transformed data.')

    def test_vault_security(self):
        label = 'Exercise 3'
        path = self._prepare('ft_vault_security', label, ['open', 'read', 'write', 'print'])
        if not path:
            return
        tree = ast.parse(Path(path).read_text(encoding='utf-8'))
        fn = next((node for node in tree.body if isinstance(node, ast.FunctionDef)
                   and node.name == 'secure_archive'), None)
        if fn is None or not any(isinstance(node, ast.With) for node in ast.walk(fn)):
            self.record_error(label, 'Structure Error', 'secure_archive() must use with for file operations.')
            return
        with tempfile.TemporaryDirectory(prefix='germinette-vault-') as directory:
            self.check_behavior(label, """
import ast
import inspect
import runpy
from pathlib import Path
fn = runpy.run_path(PATH)['secure_archive']
parameters = list(inspect.signature(fn).parameters.values())
assert len(parameters) == 3, 'Expected file, optional action and optional content'
assert all(p.default is not inspect.Parameter.empty for p in parameters[1:])
source = Path('fragment.txt')
source.write_text('Vault payload\\nSecond line', encoding='utf-8')
assert fn(str(source)) == (True, source.read_text()), 'Read success must contain the full file'
missing = fn('missing.txt')
assert isinstance(missing, tuple) and len(missing) == 2
assert missing[0] is False and isinstance(missing[1], str) and missing[1]
action = parameters[1]
assert type(action.default) in (int, str), 'The action may be an int or str'
candidates = ['write', 'w', 0, 1, 2]
for node in ast.walk(ast.parse(inspect.getsource(fn))):
    if isinstance(node, ast.Compare) and any(isinstance(part, ast.Name)
            and part.id == action.name for part in (node.left, *node.comparators)):
        candidates.extend(part.value for part in (node.left, *node.comparators)
                          if isinstance(part, ast.Constant))
for mode in candidates:
    if type(mode) is not type(action.default):
        continue
    target = Path('written.txt')
    target.unlink(missing_ok=True)
    result = fn(str(target), mode, 'written payload')
    if (isinstance(result, tuple) and len(result) == 2 and result[0] is True
            and isinstance(result[1], str) and target.is_file()
            and target.read_text() == 'written payload'):
        failed = fn('.', mode, 'cannot write a directory')
        assert isinstance(failed, tuple) and len(failed) == 2
        assert failed[0] is False and isinstance(failed[1], str) and failed[1]
        break
else:
    raise AssertionError('Writing must save the supplied content and return (True, str)')
""".replace('PATH', repr(path)), cwd=directory)
