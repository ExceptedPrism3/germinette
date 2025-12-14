# 🤝 Contributing to Germinette

Thank you for helping to grow **Germinette**! 🌱

We want to make this the standard testing tool for 42 Python modules. Here is how you can add support for new projects.

---

## 🚀 Adding a New Project

Adding a new project is simple. You just need to create one file!

### 1. Create the Subject Tester
Create a new file in `germinette/subjects/` named exactly like the module:
`germinette/subjects/python_module_03.py`

### 2. Implement the `Tester` Class
Copy this template into your new file. The class **must** be named `Tester` and have a `run` method.

```python
import sys
import os
from rich.console import Console
from germinette.utils import IOTester

console = Console()

class Tester:
    def __init__(self):
        # Tuple: (ExerciseName, TestMethod)
        self.exercises = [
            ("ft_example_func", self.test_ex0),
            # Add more here...
        ]

    def _load_module(self, module_name, exercise_label):
        # ... logic to load module (copy from module_00.py or module_01.py) ...
        # Ensure you enforce "ex0", "ex1" strict naming!
        pass

    def run(self, exercise_name=None):
        """Main entry point called by Germinette."""
        console.print("[bold blue]Testing Module 03[/bold blue]")
        
        # ... logic to run specific or all exercises ...

    def test_ex0(self):
        console.print("\n[bold]Testing Exercise 0[/bold]")
        # verify your test here
```

> 💡 **Tip**: Look at `python_module_01.py` for a full example of how we load modules and capture output.

### 3. (Optional) Enable Auto-Detection
For Germinette to automatically detect "Hey, I'm in module 03 folder!", update `germinette/core.py`.

Add your module to `MODULE_SIGNATURES`:

```python
        "python_module_03": {
            "files": ["ft_example.py", "ex0/ft_example.py"],
            "dirs": ["ex0", "ex1"]
        }
```

---

## 🛠 utils.IOTester
We provide a helper to test output easily:

```python
from germinette.utils import IOTester

# 1. Capture output
output = IOTester.run_function(my_func, args=["arg1"])

# 2. Assert output matches expected string
success, msg = IOTester.assert_output(output, "Expected Output")
```

## 📏 Guidelines

1.  **Strict Naming**: Enforce `ex0`, `ex1` (unless the subject specifically says `ex00`).
2.  **No Cows**: Do not rely on hardcoded paths that only work on your machine.
3.  **Cross-Platform**: Ensure imports work on Mac and Linux.

Happy Testing! 🐍
