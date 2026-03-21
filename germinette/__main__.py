import sys
import os
import argparse
import subprocess
from rich.console import Console
from rich.panel import Panel
from germinette.core import GerminetteRunner
from . import __version__
from germinette.utils import check_update

console = Console()
REPO_ISSUES_URL = "https://github.com/ExceptedPrism3/germinette/issues"

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

def main() -> None:
    parser = argparse.ArgumentParser(description="Germinette - 42 Python Testing Tool")
    parser.add_argument("module", nargs="?", help="Module to test (e.g., module_00)")
    parser.add_argument("--exercise", "-e", help="Specific exercise to test")
    parser.add_argument("--update", "-u", action="store_true", help="Update Germinette to the latest version")
    
    args = parser.parse_args()

    if args.update:
        # Check updates first
        has_update, remote_ver, check_ok = check_update(__version__)

        if has_update:
            console.print(f"[bold yellow]Found new version: v{remote_ver}[/bold yellow] (Current: v{__version__})")
            update_germinette()
        elif check_ok:
            console.print(f"[bold green]✅ You are already on the latest version (v{__version__})![/bold green]")
        else:
            console.print(
                f"[bold yellow]⚠️  Could not reach GitHub to compare versions.[/bold yellow]\n"
                f"[dim]You are running v{__version__}. Try again when online, or reinstall from the repo.[/dim]"
            )
        return

    # Check for updates silently
    has_update, remote_ver, check_ok = check_update(__version__)
    
    banner_text = f"[bold green]🌱 Germinette[/bold green] [dim]v{__version__}[/dim] - [italic]Python Checker for 42[/italic]"
    console.print(Panel.fit(banner_text))

    if has_update:
        console.print(f"\n[bold yellow]🔔 Update Available: v{remote_ver}[/bold yellow]")
        console.print("[dim]Run 'germinette --update' to get the latest features![/dim]\n")

    runner = GerminetteRunner()
    run_outcome = None  # True = all exercises OK, False = failures, None = no test run

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
            
            run_outcome = runner.run_module(module_name_extracted, args.exercise)
        else:
            # interactive mode or auto-detect
            run_outcome = runner.interactive_menu()
    finally:
        # Cleanup __pycache__
        GerminetteRunner.cleanup_pycache()
        console.print()

        if run_outcome is True:
            console.print(
                Panel.fit(
                    "[bold green]🎉 All exercises passed![/bold green]\n\n"
                    "[green]Nice work — Germinette did not record any failures for this run.[/green]\n"
                    "[dim]Keep using the official subject and peer feedback as the final word.[/dim]",
                    border_style="bold green",
                    title="[bold green]✓[/bold green]",
                    title_align="left",
                    padding=(0, 1),
                )
            )
            console.print()

        # Disclaimer after every run (OK or KO): subjects move; tester cannot be perfect
        console.print(
            Panel.fit(
                "[bold red]Disclaimer[/bold red] [dim red]— please read[/dim red]\n\n"
                "[red]This tool is not 100% definitive:[/red] [dim red]42 subjects are updated often, and some "
                "requirements are not fully explicit — always re-check the official PDF and confirm "
                "with your peers.[/dim red]\n\n"
                "[red]• [italic]Suggestion:[/italic][/red] [dim red]use Germinette as one signal among many; "
                "discuss unclear cases with peers or staff before assuming you are right or wrong.[/dim red]\n"
                "[red]• [italic]Tester seems wrong?[/italic][/red] [dim red]open an issue on the [/dim red]"
                f"[link={REPO_ISSUES_URL}][bold red]Issues page[/bold red][/link]"
                "[dim red] so it can be fixed in the tool.[/dim red]",
                title="[bold red]![/bold red]",
                title_align="left",
                border_style="bold red",
                padding=(0, 1),
            )
        )

        # Version / update reminder (last thing on screen)
        console.print()
        if has_update:
            console.print(
                Panel.fit(
                    f"[bold yellow]Update available[/bold yellow]  "
                    f"[dim]You:[/dim] v{__version__}  [dim]→ Latest:[/dim] [bold]v{remote_ver}[/bold]\n\n"
                    f"Run [bold yellow]germinette -u[/bold yellow]",
                    border_style="bold yellow",
                    padding=(0, 2),
                )
            )
        elif check_ok:
            console.print(f"[dim]Germinette v{__version__} — [green]up to date[/green] with GitHub main[/dim]")
        else:
            console.print(
                f"[dim]Germinette v{__version__} — [yellow]could not check for updates[/yellow] "
                f"(offline?) · [bold]germinette -u[/bold] when online[/dim]"
            )

if __name__ == "__main__":
    main()
