from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.console import Console
from rich import print as rprint

from app.services.backup_service import BackupService
from app.cli.landing import print_header

console = Console()

def handle_create_backup() -> None:
    """Invokes DB backup utility and logs details."""
    print_header("Create Database Backup")
    
    with console.status("[bold green]Writing database clone... (Copying SQLite file)", spinner="dots"):
        success, res = BackupService.create_backup()

    if success:
        rprint(f"\n[bold green]✔ Database backup created successfully![/bold green]")
        rprint(f"[bold cyan]Backup File name:[/bold cyan] {res}")
    else:
        rprint(f"\n[bold red]❌ Failed to create database backup: {res}[/bold red]")
    Prompt.ask("\nPress Enter to continue...")

def handle_restore_backup() -> None:
    """Lists available backups and restores the selected database version."""
    print_header("Restore Database from Backup")
    
    backups = BackupService.list_backups()
    
    if not backups:
        rprint("[bold yellow]No database backup files found in the backups directory.[/bold yellow]")
        Prompt.ask("\nPress Enter to return...")
        return

    # Render backups table
    table = Table(title="Available Backups", border_style="yellow")
    table.add_column("Index", style="bold white", justify="center")
    table.add_column("Backup File Name", style="bold yellow")
    table.add_column("Creation / Modification Date", style="bold blue")
    table.add_column("Size (bytes)", style="bold green")

    for idx, (name, mtime, size) in enumerate(backups, 1):
        table.add_row(str(idx), name, mtime, f"{size:,}")

    console.print(table)
    console.print()

    choices = [str(i) for i in range(1, len(backups) + 1)]
    choices.append("c")
    
    choice = Prompt.ask("[bold cyan]Enter backup index to restore (or 'c' to cancel)[/bold cyan]", choices=choices, default="c")
    if choice == "c":
        rprint("[yellow]Restore operation cancelled.[/yellow]")
        Prompt.ask("\nPress Enter to continue...")
        return

    selected_backup = backups[int(choice) - 1][0]

    confirm = Confirm.ask(
        f"[bold red]WARNING: Are you sure you want to restore '{selected_backup}'?[/bold red]\n"
        "This completely replaces the current database catalog. A safety checkpoint will be saved before overwriting.",
        default=False
    )

    if confirm:
        with console.status("[bold red]Restoring database files...", spinner="dots"):
            success, msg = BackupService.restore_backup(selected_backup)
        if success:
            rprint(f"\n[bold green]✔ Database restored successfully![/bold green]")
            rprint(f"[cyan]Detail:[/cyan] {msg}")
        else:
            rprint(f"\n[bold red]❌ Database restore failed: {msg}[/bold red]")
    else:
        rprint("\n[yellow]Restore cancelled.[/yellow]")
        
    Prompt.ask("\nPress Enter to continue...")

def backup_submenu() -> None:
    """Controller routing menu choices for the backup/restore utility."""
    while True:
        print_header("Database Backup System")
        rprint("[bold yellow]1.[/bold yellow] Create Timestamped Database Backup")
        rprint("[bold yellow]2.[/bold yellow] List and Restore Database from Backup File")
        rprint("[bold yellow]3.[/bold yellow] Back to Main Menu")
        rprint()
        
        choice = Prompt.ask("[bold cyan]Select an option[/bold cyan]", choices=["1", "2", "3"], default="3")
        
        if choice == "1":
            handle_create_backup()
        elif choice == "2":
            handle_restore_backup()
        elif choice == "3":
            break
