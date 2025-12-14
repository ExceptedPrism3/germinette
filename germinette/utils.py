import sys
import io
import contextlib
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
        original_stdin = sys.stdin
        # We can't easily replace builtins.input locally without patching builtins
        # But we can patch sys.stdin if the function reads from it (it doesn't, it uses input())
        # The standard way to mock input() is modifying __builtins__ output
        # BUT this is dangerous/messy.
        # Better: use unittest.mock or a custom way if possible.
        # Since we are essentially a test runner, let's use a simpler approach:
        # We will wrap the execution in a way that checks if they use input().
        
        # Actually, let's just patch builtins.input module-wide or use unittest.mock
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

