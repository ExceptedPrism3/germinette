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
            ("ft_command_quest", self.test_command_quest),
            ("ft_score_analytics", self.test_score_analytics),
            ("ft_coordinate_system", self.test_coordinate_system),
            ("ft_achievement_tracker", self.test_achievement_tracker),
            ("ft_inventory_system", self.test_inventory_system),
            ("ft_data_stream", self.test_data_stream),
            ("ft_analytics_dashboard", self.test_analytics_dashboard)
        ]
        self.grouped_errors = {}

    def _load_module_generic(self, filename, ex_name):
        # ... Basic loading logic ...
        # Simplified for checking existence only in this WIP version
        console.print(f"[dim]Checking {filename}...[/dim]", style="italic")
        # Real loading would go here
        return True

    def run(self, exercise_name=None):
        console.print("[bold cyan]Testing Module 03: Data Quest[/bold cyan]")
        console.print("[yellow]⚠️  WORK IN PROGRESS: Checks are not fully implemented![/yellow]\n")
        
        for name, func in self.exercises:
            func()

    def test_command_quest(self):
        console.print("\n[bold]Testing Exercise 0: Command Quest (sys.argv)[/bold]")
        console.print("[dim]TODO: Verify argument count and printing[/dim]")
        # Placeholder check
        if os.path.exists("ft_command_quest.py") or os.path.exists("ex0/ft_command_quest.py"):
             console.print("[green]File found (Logic check pending)[/green]")
        else:
             console.print("[red]File missing[/red]")

    def test_score_analytics(self):
        console.print("\n[bold]Testing Exercise 1: Score Cruncher (Lists)[/bold]")
        console.print("[dim]TODO: Test list statistics (min, max, avg)[/dim]")
        
    def test_coordinate_system(self):
        console.print("\n[bold]Testing Exercise 2: Position Tracker (Tuples)[/bold]")
        console.print("[dim]TODO: Test tuple distance calculations[/dim]")

    def test_achievement_tracker(self):
        console.print("\n[bold]Testing Exercise 3: Achievement Hunter (Sets)[/bold]")
        console.print("[dim]TODO: Test set operations (union, intersection)[/dim]")
        
    def test_inventory_system(self):
        console.print("\n[bold]Testing Exercise 4: Inventory Master (Dicts)[/bold]")
        console.print("[dim]TODO: Test dictionary management[/dim]")
        
    def test_data_stream(self):
        console.print("\n[bold]Testing Exercise 5: Stream Wizard (Generators)[/bold]")
        console.print("[dim]TODO: Test generator yield behavior[/dim]")

    def test_analytics_dashboard(self):
        console.print("\n[bold]Testing Exercise 6: Data Alchemist (Comprehensions)[/bold]")
        console.print("[dim]TODO: Verify comprehension usage[/dim]")
