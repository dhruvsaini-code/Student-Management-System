import os
import time
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.box import ROUNDED, DOUBLE
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

console = Console()

def clear_screen() -> None:
    """Clears the terminal screen depending on operating system."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title: str = "Student Management System") -> None:
    """Prints a consistent, styled section header at the top of each view.

    Args:
        title: The header title string.
    """
    clear_screen()
    header_text = Text(title.upper(), style="bold white", justify="center")
    panel = Panel(
        header_text,
        style="bold cyan",
        border_style="magenta",
        box=DOUBLE,
        subtitle="[bold white]Version 2.0[/bold white]",
        subtitle_align="right"
    )
    console.print(panel)
    console.print()

def show_landing_page() -> None:
    """Displays a premium ASCII art banner, project status details, and a dynamic loading sequence."""
    clear_screen()
    
    # Beautiful ASCII Banner
    banner = """
 ██████  ████████ ██    ██ ██████  ███████ ███    ██ ████████ 
██          ██    ██    ██ ██   ██ ██      ████   ██    ██    
 █████      ██    ██    ██ ██   ██ █████   ██ ██  ██    ██    
      ██    ██    ██    ██ ██   ██ ██      ██  ██ ██    ██    
██████      ██     ██████  ██████  ███████ ██   ████    ██    
                                                              
 ███    ███  █████  ███    ██  █████   ██████  ███████ ██████  
 ████  ████ ██   ██ ████   ██ ██   ██ ██      ██      ██   ██ 
 ██ ████ ██ ███████ ██ ██  ██ ███████ ██   ███ █████   ██████  
 ██  ██  ██ ██   ██ ██  ██ ██ ██   ██ ██    ██ ██      ██   ██ 
 ██      ██ ██   ██ ██   ████ ██   ██  ██████  ███████ ██   ██ 
    """
    
    panel_banner = Panel(
        Align.center(Text(banner, style="bold cyan")),
        border_style="magenta",
        box=ROUNDED,
        subtitle="Advanced Terminal Management Suite",
        subtitle_align="center"
    )
    
    console.print(panel_banner)
    console.print()
    
    # Render metadata info
    meta_text = Text()
    meta_text.append("Project:   ", style="bold green")
    meta_text.append("Student Management System\n", style="white")
    meta_text.append("Developer: ", style="bold green")
    meta_text.append("Dhruv Saini\n", style="white")
    meta_text.append("Version:   ", style="bold green")
    meta_text.append("2.0\n", style="white")
    meta_text.append("Features:  ", style="bold green")
    meta_text.append("Bcrypt Auth | PDF Reports | SQLite Transactions | Matplotlib Graphs\n", style="white")
    meta_text.append("Status:    ", style="bold green")
    meta_text.append("Production-Ready / Secure Session Enabled\n", style="yellow")
    
    meta_panel = Panel(
        Align.center(meta_text),
        border_style="cyan",
        box=ROUNDED,
        title="SYSTEM INFORMATION"
    )
    
    console.print(meta_panel)
    console.print()

    # Dynamic loading progress bar
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=40, style="magenta", complete_style="cyan"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    ) as progress:
        task = progress.add_task("[bold magenta]Booting Secure Database...", total=100)
        
        while not progress.finished:
            time.sleep(0.015)
            progress.update(task, advance=1.5)
            if progress.tasks[0].completed >= 35 and progress.tasks[0].completed < 60:
                progress.tasks[0].description = "[bold cyan]Checking Admin Credentials..."
            elif progress.tasks[0].completed >= 60 and progress.tasks[0].completed < 85:
                progress.tasks[0].description = "[bold green]Configuring Logging Directory..."
            elif progress.tasks[0].completed >= 85:
                progress.tasks[0].description = "[bold yellow]Launching Interactive Interface..."
                
    time.sleep(0.3)
