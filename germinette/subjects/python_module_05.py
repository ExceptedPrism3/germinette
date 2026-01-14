from rich.console import Console
from germinette.core import BaseTester

console = Console()

class Tester(BaseTester):
    def run(self, exercise_name=None):
        console.print("[yellow]🚧 Module 05 is Coming Soon! 🚧[/yellow]")
