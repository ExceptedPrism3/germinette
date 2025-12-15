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
        for i, mod in enumerate(modules, 1):
             display_name = mod
             if mod == "python_module_03":
                 display_name += " [yellow](Coming Soon 🚧)[/yellow]"
             console.print(f"{i}. {display_name}")
        
        console.print("\n[yellow]Could not auto-detect module in this directory.[/yellow]")
        console.print("Run with: [bold]germinette <module_name>[/bold]")

    def run_module(self, module_name, exercise=None):
        try:
            # Dynamically import the module checker
            mod = importlib.import_module(f"germinette.subjects.{module_name}")
            tester = getattr(mod, "Tester")()
            tester.run(exercise)
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

        except AttributeError:
            console.print(f"[red]Module {module_name} is invalid (missing Tester class).[/red]")
        except Exception as e:
            console.print(f"[bold red]Error loading module:[/bold red] {e}")

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
