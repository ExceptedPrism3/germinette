import sys
import os
import argparse
from rich.console import Console
from rich.panel import Panel
from germinette.core import GerminetteRunner

console = Console()

def main():
    parser = argparse.ArgumentParser(description="Germinette - 42 Python Testing Tool")
    parser.add_argument("module", nargs="?", help="Module to test (e.g., module_00)")
    parser.add_argument("--exercise", "-e", help="Specific exercise to test")
    
    args = parser.parse_args()

    console.print(Panel.fit("[bold green]🌱 Germinette[/bold green] - [italic]Python Checker for 42[/italic]"))

    runner = GerminetteRunner()
    
    if args.module:
        target_path = args.module
        module_name = target_path

        # Check if the argument is a path to a directory
        if os.path.exists(target_path) and os.path.isdir(target_path):
             # It's a directory path (e.g., "../python_module_00")
             abs_path = os.path.abspath(target_path)
             module_name = os.path.basename(abs_path) # Extract "python_module_00"
             
             # Change CWD to that directory so the tester finds the files
             os.chdir(abs_path)
             console.print(f"[bold blue]Switched working directory to:[/bold blue] {abs_path}")
        
        runner.run_module(module_name, args.exercise)
    else:
        # interactive mode or auto-detect
        runner.interactive_menu()

if __name__ == "__main__":
    main()
