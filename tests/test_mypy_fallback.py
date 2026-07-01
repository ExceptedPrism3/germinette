import sys
from pathlib import Path
import pytest
from germinette.core import BaseTester

class MockTester(BaseTester):
    pass

def test_check_flake8_graceful_on_mypy_internal_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Create a test python file
    test_file = tmp_path / "test_file.py"
    test_file.write_text("def foo() -> None:\n    pass\n", encoding="utf-8")

    # Mock subprocess.run to make flake8 succeed (returncode=0)
    # and mypy fail with INTERNAL ERROR (returncode=1, stderr with INTERNAL ERROR)
    import subprocess
    original_run = subprocess.run

    def mock_run(args, **kwargs):
        if "flake8" in args:
            # Create a mock CompletedProcess for success
            class MockProcess:
                returncode = 0
                stdout = ""
                stderr = ""
            return MockProcess()
        elif "mypy" in args:
            # Create a mock CompletedProcess for crash
            class MockProcess:
                returncode = 1
                stdout = ""
                stderr = "error: INTERNAL ERROR -- Please try using mypy master on GitHub"
            return MockProcess()
        return original_run(args, **kwargs)

    monkeypatch.setattr(subprocess, "run", mock_run)

    tester = MockTester()
    result = tester.check_flake8(str(test_file))
    
    # It should return None (indicating style check passed / ignored mypy error)
    assert result is None
