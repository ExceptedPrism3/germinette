import sys
import os
import argparse
import subprocess
from rich.console import Console
from rich.panel import Panel
from germinette.core import GerminetteRunner
from germinette import __version__
from germinette.utils import check_update

console = Console()

def update_repo():
    """Updates the local git repository found in configuration."""
    repo_path = None
    config_file = os.path.expanduser("~/.germinette_repo_path")
    
    # Try locating repo from config first
    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                path = f.read().strip()
                if os.path.exists(os.path.join(path, ".git")):
                    repo_path = path
        except Exception:
            return None
    
    # Fallback: Check current directory
    if not repo_path and os.path.exists(".git"):
         repo_path = os.getcwd()

    if not repo_path:
        # Silent return if no repo found
        return

    console.print(f"\n[bold blue]📂 Detected source repository at: {repo_path}[/bold blue]")
    try:
        # Check remote for safety
        remote = subprocess.check_output(["git", "remote", "get-url", "origin"], cwd=repo_path, text=True).strip()
        if "germinette" not in remote:
             return 
             
        subprocess.check_call(["git", "pull"], cwd=repo_path)
        console.print("[bold green]✅ Local source Updated source files![/bold green]")
    except subprocess.CalledProcessError:
        console.print("\n[bold red]⚠️  Merge conflict or local changes detected![/bold red]")
        from rich.prompt import Confirm
        if Confirm.ask("Do you want to FORCE update? (This will reset local changes)", default=False):
             console.print("[yellow]Force updating...[/yellow]")
             subprocess.check_call(["git", "fetch", "--all"], cwd=repo_path)
             subprocess.check_call(["git", "reset", "--hard", "origin/main"], cwd=repo_path)
             console.print("[bold green]✅ Local repository force updated![/bold green]")
        else:
             console.print("[yellow]Skipping local repo update.[/yellow]")

def update_germinette():
    """Updates Germinette from the remote repository."""
    console.print("[bold cyan]🔄 Updating Germinette Package...[/bold cyan]")
    try:
        import subprocess
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", 
            "git+https://github.com/ExceptedPrism3/germinette.git"
        ])
        console.print("[bold green]✅ Germinette package updated successfully![/bold green]")
        
        # Update local repo if we are in one
        update_repo()
        
        console.print("\nPlease restart your terminal or run the command again.")
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
    
    try:
        if args.module:
            target_path = args.module
            module_name = target_path
            module_name_extracted = module_name
            
            # Check if the argument is a path to a directory
            if os.path.exists(target_path):
                 # It's a directory path (e.g., "../python_module_00")
                 abs_path = os.path.abspath(target_path)
                 
                 # Logic to deduce module name if it's a path
                 if os.path.isdir(abs_path):
                     module_name_extracted = os.path.basename(abs_path) 
                 
                 # Change CWD to that directory so the tester finds the files
                 if os.path.isdir(abs_path):
                     os.chdir(abs_path)
                     console.print(f"[bold blue]Switched working directory to:[/bold blue] {abs_path}")
            
            runner.run_module(module_name_extracted, args.exercise)
        else:
            # interactive mode or auto-detect
            runner.interactive_menu()
    finally:
        # Cleanup __pycache__
        GerminetteRunner.cleanup_pycache()

if __name__ == "__main__":
    main()
