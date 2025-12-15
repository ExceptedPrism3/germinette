import sys
import os
import argparse
from rich.console import Console
from rich.panel import Panel
from germinette.core import GerminetteRunner
from germinette import __version__
from germinette.utils import check_update

console = Console()

def update_germinette():
    """Updates Germinette from the remote repository."""
    console.print("[bold cyan]🔄 Updating Germinette...[/bold cyan]")
    try:
        import subprocess
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", 
            "git+https://github.com/ExceptedPrism3/germinette.git"
        ])
        console.print("[bold green]✅ Germinette updated successfully![/bold green]")
        console.print("Please restart your terminal or run the command again.")
    except Exception as e:
        console.print(f"[bold red]❌ Update failed:[/bold red] {e}")

def main():
    parser = argparse.ArgumentParser(description="Germinette - 42 Python Testing Tool")
    parser.add_argument("module", nargs="?", help="Module to test (e.g., module_00)")
    parser.add_argument("--exercise", "-e", help="Specific exercise to test")
    parser.add_argument("--update", "-u", action="store_true", help="Update Germinette to the latest version")
    
    args = parser.parse_args()

    if args.update:
        # Check updates first
        has_update, remote_ver = check_update(__version__)
        
        if has_update:
            console.print(f"[bold yellow]Found new version: v{remote_ver}[/bold yellow] (Current: v{__version__})")
            update_germinette()
        else:
            console.print(f"[bold green]✅ You are already on the latest version (v{__version__})![/bold green]")
        return

    # Check for updates silently
    has_update, remote_ver = check_update(__version__)
    
    banner_text = f"[bold green]🌱 Germinette[/bold green] [dim]v{__version__}[/dim] - [italic]Python Checker for 42[/italic]"
    console.print(Panel.fit(banner_text))

    if has_update:
        console.print(f"\n[bold yellow]🔔 Update Available: v{remote_ver}[/bold yellow]")
        console.print("[dim]Run 'germinette --update' to get the latest features![/dim]\n")

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
