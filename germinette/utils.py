import sys
import os
import io
import contextlib
import urllib.request
import re
from rich.console import Console

console = Console()

class IOTester:
    @staticmethod
    def run_function(func, inputs=None, args=None):
        """
        Runs a function, mocking input() and capturing print().
        
        Args:
            func: The function object to call
            inputs: A list of strings to string to mock input(). 
                   They are fed in order.
            args: A list/tuple of arguments to pass to the function (if any).
        
        Returns:
            captured_stdout: The string printed to stdout.
        """
        # Prepare mock input
        input_iterator = iter(inputs) if inputs else iter([])
        
        def mock_input(prompt=""):
            # We can optionally capture prompts if needed, but for now just return next input
            try:
                return str(next(input_iterator))
            except StopIteration:
                raise EOFError("Function requested more input than provided.")

        # Capture stdout
        capture = io.StringIO()
        
        # Override builtin input and sys.stdout
        # We generally use unittest.mock.patch for 'builtins.input'
        from unittest.mock import patch
        
        with contextlib.redirect_stdout(capture):
            with patch('builtins.input', side_effect=mock_input):
                if args:
                    func(*args)
                else:
                    func()
        
        return capture.getvalue()

    @staticmethod
    def assert_output(actual, expected, fuzzy=False):
        """
        Asserts that actual output matches expected.
        
        Args:
            actual: Actual string output.
            expected: Expected string output or list of strings that lines must match.
            fuzzy: If True, ignores whitespace/capitalization differences (not used yet).
        """
        # Basic normalization: strip trailing whitespace from lines and total
        actual_clean = actual.strip()
        expected_clean = expected.strip()
        
        if actual_clean == expected_clean:
            return True, None
        else:
            return False, f"Expected:\n{expected_clean}\n\nGot:\n{actual_clean}"

def check_update(current_version):
    """
    Checks if a newer version is available on GitHub main.

    For local UI testing without depending on what is published, set:
        GERMINETTE_DEBUG_REMOTE_VERSION=1.6.8
    (compared against the real or GERMINETTE_FORCE_VERSION current version).

    Returns:
        tuple: (needs_update: bool, remote_version: str | None, check_ok: bool)
        - needs_update: True if remote on GitHub is strictly newer than current_version.
        - remote_version: Parsed __version__ from GitHub when check_ok else None.
        - check_ok: True if the version string was fetched and parsed successfully.
    """
    def parse_v(v):
        return tuple(map(int, v.split(".")))

    debug_remote = os.environ.get("GERMINETTE_DEBUG_REMOTE_VERSION", "").strip()
    if debug_remote:
        try:
            if debug_remote != current_version and parse_v(debug_remote) > parse_v(current_version):
                return True, debug_remote, True
            return False, debug_remote, True
        except ValueError:
            return False, None, False

    url = "https://raw.githubusercontent.com/ExceptedPrism3/germinette/main/germinette/__init__.py"

    try:
        # Set timeout to 2 seconds to not block startup
        with urllib.request.urlopen(url, timeout=2) as response:
            content = response.read().decode("utf-8")

        # Regex to find __version__ = "1.0.0"
        match = re.search(r'__version__\s*=\s*"(.*?)"', content)
        if not match:
            return False, None, False

        remote_version = match.group(1)
        if remote_version != current_version:
            if parse_v(remote_version) > parse_v(current_version):
                return True, remote_version, True
        return False, remote_version, True
    except Exception:
        pass  # Network / parse failure

    return False, None, False
