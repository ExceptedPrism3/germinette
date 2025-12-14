import sys
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
    Checks if a newer version is available on GitHub.
    Returns (update_avaiable: bool, remote_version: str).
    """
    url = "https://raw.githubusercontent.com/ExceptedPrism3/germinette/main/germinette/__init__.py"
    try:
        # Set timeout to 2 seconds to not block startup
        with urllib.request.urlopen(url, timeout=2) as response:
            content = response.read().decode('utf-8')
            
        # Regex to find __version__ = "1.0.0"
        match = re.search(r'__version__\s*=\s*"(.*?)"', content)
        if match:
            remote_version = match.group(1)
            # Simple string verify (1.0.1 > 1.0.0 works for semantic versioning usually)
            # Ideally we'd use packaging.version, but we want to minimize deps or imports.
            if remote_version != current_version:
                 # Check if remote is actually 'newer'
                 # Split by . and compare integers tuple
                 def parse_v(v): return tuple(map(int, v.split('.')))
                 
                 if parse_v(remote_version) > parse_v(current_version):
                     return True, remote_version
    except Exception:
        pass # Fail silently if network/parsing fails
    
    return False, None
