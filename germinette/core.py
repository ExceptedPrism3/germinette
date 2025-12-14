import os
import sys
import importlib
from rich.console import Console
from rich.table import Table

console = Console()

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
            "dirs": ["ex0", "ex1", "ex2"]
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
        }
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
             self.run_module(detected)
             return

        modules = self.list_modules()
        if not modules:
            console.print("[red]No modules found in subjects directory![/red]")
            return

        console.print("[bold]Available Modules:[/bold]")
        for i, mod in enumerate(modules):
            console.print(f"{i + 1}. {mod}")
        
        console.print("\n[yellow]Could not auto-detect module in this directory.[/yellow]")
        console.print("Run with: [bold]germinette <module_name>[/bold]")

    def run_module(self, module_name, exercise=None):
        try:
            # Dynamically import the module checker
            mod = importlib.import_module(f"germinette.subjects.{module_name}")
            tester = getattr(mod, "Tester")()
            tester.run(exercise)
        except ModuleNotFoundError:
            console.print(f"[red]Module {module_name} not found![/red]")
        except AttributeError:
            console.print(f"[red]Module {module_name} is invalid (missing Tester class).[/red]")
        except Exception as e:
            console.print(f"[bold red]Error loading module:[/bold red] {e}")

class BaseTester:
    def run(self, exercise_name=None):
        raise NotImplementedError
