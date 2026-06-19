from rich.prompt import Prompt
from rich.console import Console
from rich import print as rprint
from app.services.auth_service import AuthService
from app.cli.landing import print_header

console = Console()

def handle_login() -> bool:
    """Renders the admin login interface.

    Allows the user to input administrator credentials. Password input is hidden/masked.
    Loops until successful login or the user chooses to exit.

    Returns:
        True if the user authenticates successfully, False if they choose to exit.
    """
    while True:
        print_header("Secure Admin Authentication")
        
        rprint("[bold yellow]Please enter your administrator credentials below.[/bold yellow]")
        rprint("[italic dim]Default credentials: admin / admin123 (Type 'exit' to quit)[/italic dim]\n")
        
        username = Prompt.ask("[bold cyan]Username[/bold cyan]").strip()
        if not username:
            rprint("[bold red]❌ Username cannot be empty.[/bold red]")
            Prompt.ask("\nPress Enter to retry...")
            continue
            
        if username.lower() == 'exit':
            return False
            
        password = Prompt.ask("[bold cyan]Password[/bold cyan]", password=True)
        if not password:
            rprint("[bold red]❌ Password cannot be empty.[/bold red]")
            Prompt.ask("\nPress Enter to retry...")
            continue

        with console.status("[bold magenta]Verifying administrator credentials...", spinner="dots"):
            success = AuthService.login(username, password)

        if success:
            rprint(f"\n[bold green]✔ Access Granted! Welcome, {AuthService.get_current_user()}.[/bold green]")
            Prompt.ask("\nPress Enter to load Dashboard...")
            return True
        else:
            rprint("\n[bold red]❌ Access Denied: Incorrect username or password.[/bold red]")
            retry = Prompt.ask("Would you like to try again? (y/n)", choices=["y", "n"], default="y")
            if retry.strip().lower() == "n":
                return False

def handle_logout() -> None:
    """Handles logout procedure and wipes session data."""
    AuthService.logout()
    rprint("[bold green]✔ Logged out successfully. Administrative session closed.[/bold green]")
    Prompt.ask("\nPress Enter to continue...")
