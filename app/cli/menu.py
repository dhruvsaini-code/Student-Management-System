import sys
from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns
from rich.align import Align
from rich.box import ROUNDED
from rich.prompt import Prompt
from rich import print as rprint

from app.database.schema import init_db
from app.services.auth_service import AuthService
from app.services.student_service import StudentService
from app.cli.landing import show_landing_page, print_header, clear_screen
from app.cli.auth_menu import handle_login, handle_logout
from app.cli.student_menu import student_submenu
from app.cli.course_menu import course_submenu
from app.cli.attendance_menu import attendance_submenu
from app.cli.analytics_menu import analytics_submenu
from app.cli.report_menu import report_submenu
from app.cli.backup_menu import backup_submenu

console = Console()

def render_dashboard() -> None:
    """Queries aggregate system statistics and displays them inside styled dashboard panels."""
    try:
        stats = StudentService.get_system_stats()
    except Exception as e:
        stats = {
            "total_students": 0,
            "total_courses": 0,
            "average_grade": 0.0,
            "overall_attendance": 100.0
        }
        rprint(f"[bold red]⚠️ Warning: Failed to query dashboard metrics ({str(e)}).[/bold red]")

    p_students = Panel(
        Align.center(f"[bold cyan]{stats['total_students']}[/bold cyan]"),
        title="Total Students",
        border_style="cyan",
        box=ROUNDED
    )
    p_courses = Panel(
        Align.center(f"[bold green]{stats['total_courses']}[/bold green]"),
        title="Total Courses",
        border_style="green",
        box=ROUNDED
    )
    p_grades = Panel(
        Align.center(f"[bold yellow]{stats['average_grade']}%[/bold yellow]"),
        title="Avg Grade",
        border_style="yellow",
        box=ROUNDED
    )
    p_attendance = Panel(
        Align.center(f"[bold magenta]{stats['overall_attendance']}%[/bold magenta]"),
        title="Avg Attendance",
        border_style="magenta",
        box=ROUNDED
    )
    
    console.print(Columns([p_students, p_courses, p_grades, p_attendance], equal=True))
    console.print()

def start_app() -> None:
    """Launches database setups, boot-screens, handles auth gates, and runs the main loop."""
    # 1. Initialize DB tables, indexes, and seed default records
    try:
        init_db()
    except Exception as e:
        rprint(f"[bold red]❌ Critical Database Error: Failed to initialize schema ({str(e)}).[/bold red]")
        rprint("[bold yellow]Attempting to start application, but database functions may fail.[/bold yellow]")
        Prompt.ask("Press Enter to continue...")

    # 2. Boot landing sequence
    try:
        show_landing_page()
    except Exception as e:
        rprint(f"[bold red]⚠️ Warning: Failed to load startup landing page ({str(e)}).[/bold red]")
        Prompt.ask("Press Enter to continue...")

    # 3. Auth login gate
    while not AuthService.is_authenticated():
        try:
            success = handle_login()
            if not success:
                clear_screen()
                rprint("[bold red]Administrative authentication is required. System closing. Goodbye![/bold red]")
                sys.exit(0)
        except Exception as e:
            rprint(f"[bold red]❌ Authentication System Error: {str(e)}[/bold red]")
            Prompt.ask("Press Enter to retry authentication...")

    # 4. Main Menu Loop
    while True:
        try:
            print_header("Academic Management System Dashboard")
            render_dashboard()
            
            rprint(f"[italic dim]Logged in as: admin[/italic dim]\n")
            rprint("[bold cyan]1.[/bold cyan] Student Profiles Management (CRUD & Search)")
            rprint("[bold cyan]2.[/bold cyan] Course Catalog & Grades Management")
            rprint("[bold cyan]3.[/bold cyan] Attendance Tracking")
            rprint("[bold cyan]4.[/bold cyan] Analytics & Performance Reports")
            rprint("[bold cyan]5.[/bold cyan] PDF Report Generation & Graph Visualizations")
            rprint("[bold cyan]6.[/bold cyan] System Backups & Recovery Operations")
            rprint("[bold cyan]7.[/bold cyan] Log Out Admin Session")
            rprint("[bold cyan]8.[/bold cyan] Exit System")
            rprint()
            
            choice = Prompt.ask("[bold magenta]Select Module[/bold magenta]", choices=["1", "2", "3", "4", "5", "6", "7", "8"], default="8")
            
            if choice == "1":
                student_submenu()
            elif choice == "2":
                course_submenu()
            elif choice == "3":
                attendance_submenu()
            elif choice == "4":
                analytics_submenu()
            elif choice == "5":
                report_submenu()
            elif choice == "6":
                backup_submenu()
            elif choice == "7":
                handle_logout()
                # If logged out, require authentication loop again
                while not AuthService.is_authenticated():
                    try:
                        success = handle_login()
                        if not success:
                            clear_screen()
                            rprint("[bold red]Session terminated. Goodbye![/bold red]")
                            sys.exit(0)
                    except Exception as e:
                        rprint(f"[bold red]❌ Authentication System Error: {str(e)}[/bold red]")
                        Prompt.ask("Press Enter to retry...")
            elif choice == "8":
                clear_screen()
                rprint("[bold green]Thank you for using Student Management System. Goodbye![/bold green]")
                sys.exit(0)
        except Exception as menu_err:
            rprint(f"[bold red]⚠️ An error occurred in the menu interface: {str(menu_err)}[/bold red]")
            Prompt.ask("Press Enter to return to main dashboard...")
