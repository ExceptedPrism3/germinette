import sys
import os
import importlib.util
from rich.console import Console
from rich.panel import Panel
from germinette.utils import IOTester

console = Console()

class Tester:
    def __init__(self):
        self.exercises = [
            ("Structure Check", self.test_structure),
            ("Maze Generation (WIP)", self.test_generation_WIP),
        ]
        self.grouped_errors = {}

    def run(self, exercise_name=None):
        console.print("[bold purple]Testing Project: A-Maze-ing (Beta)[/bold purple]")
        console.print("[italic]⚠️  Work In Progress - Only basic checks implemented[/italic]\n")
        
        for name, func in self.exercises:
             func()

    def test_structure(self):
        console.print("\n[bold]Checking Project Structure[/bold]")
        
        required_files = ["a_maze_ing.py", "Makefile"]
        cwd = os.getcwd()
        
        all_ok = True
        for f in required_files:
            if os.path.exists(os.path.join(cwd, f)):
                 console.print(f"[green]OK ({f} found)[/green]")
            else:
                 console.print(f"[red]KO ({f} missing)[/red]")
                 all_ok = False
        
        if all_ok:
             console.print("[blue]>> Structure looks good for a start![/blue]")

    def test_generation_WIP(self):
        console.print("\n[bold]Testing Maze Generation (WIP)[/bold]")
        console.print("[dim]TODO: Implement Prim's algorithm verification[/dim]")
        console.print("[dim]TODO: Implement Hex output parsing[/dim]")
        console.print("[dim]TODO: Verify pathfinding[/dim]")
        console.print("[yellow]Skipping advanced tests...[/yellow]")
