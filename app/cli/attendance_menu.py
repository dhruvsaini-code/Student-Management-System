import datetime
from rich.prompt import Prompt
from rich.table import Table
from rich.console import Console
from rich import print as rprint

from app.services.attendance_service import AttendanceService
from app.services.student_service import StudentService
from app.cli.landing import print_header
from app.utils.validators import validate_date

console = Console()

def handle_record_attendance() -> None:
    """Takes status logs and records or updates a student's daily attendance entry."""
    print_header("Record Daily Attendance")
    
    date_str = Prompt.ask("[bold yellow]Enter Date[/bold yellow] (YYYY-MM-DD)", default=str(datetime.date.today())).strip()
    if not validate_date(date_str):
        rprint("[bold red]❌ Invalid date format. Please use YYYY-MM-DD.[/bold red]")
        Prompt.ask("\nPress Enter to return...")
        return

    student_id = Prompt.ask("[bold yellow]Enter Student ID[/bold yellow]").strip().upper()
    if not StudentService.get_student(student_id):
        rprint(f"[bold red]❌ Student with ID '{student_id}' not found.[/bold red]")
        Prompt.ask("\nPress Enter to return...")
        return

    status = Prompt.ask("[bold yellow]Attendance Status[/bold yellow]", choices=["Present", "Absent", "Late"], default="Present")

    with console.status("[bold green]Saving attendance entry...", spinner="dots"):
        success = AttendanceService.record_attendance(student_id, date_str, status)

    if success:
        rprint(f"\n[bold green]✔ Attendance status recorded: Student '{student_id}' marked '{status}' on {date_str}.[/bold green]")
    else:
        rprint("\n[bold red]❌ Failed to save attendance log in database.[/bold red]")
    Prompt.ask("\nPress Enter to continue...")

def handle_view_student_attendance() -> None:
    """Displays attendance history table for a specific student."""
    print_header("Student Attendance History")
    
    student_id = Prompt.ask("[bold yellow]Enter Student ID[/bold yellow]").strip().upper()
    student = StudentService.get_student(student_id)
    if not student:
        rprint(f"[bold red]❌ Student with ID '{student_id}' not found.[/bold red]")
        Prompt.ask("\nPress Enter to return...")
        return

    logs = AttendanceService.get_student_attendance(student_id)
    if not logs:
        rprint(f"[bold yellow]No attendance logs exist in database for {student.name}.[/bold yellow]")
        Prompt.ask("\nPress Enter to continue...")
        return

    table = Table(title=f"Attendance Logs: {student.name}", border_style="blue")
    table.add_column("Date Checked", style="bold blue")
    table.add_column("Status Logged", style="bold green")

    for a in logs:
        status_style = "green" if a['status'] == "Present" else "yellow" if a['status'] == "Late" else "red"
        table.add_row(a['date'], f"[{status_style}]{a['status']}[/{status_style}]")

    console.print(table)
    console.print()
    Prompt.ask("Press Enter to continue...")

def handle_view_date_attendance() -> None:
    """Lists student logs matching a specific calendar date."""
    print_header("View Attendance Log by Date")
    
    date_str = Prompt.ask("[bold yellow]Enter Date[/bold yellow] (YYYY-MM-DD)", default=str(datetime.date.today())).strip()
    if not validate_date(date_str):
        rprint("[bold red]❌ Invalid date format. Please use YYYY-MM-DD.[/bold red]")
        Prompt.ask("\nPress Enter to return...")
        return

    logs = AttendanceService.get_attendance_by_date(date_str)
    if not logs:
        rprint(f"[bold yellow]No student attendance logs found registered on {date_str}.[/bold yellow]")
        Prompt.ask("\nPress Enter to continue...")
        return

    table = Table(title=f"Attendance Logs: {date_str}", border_style="blue")
    table.add_column("Student ID", style="bold yellow")
    table.add_column("Student Name", style="bold white")
    table.add_column("Status Logged", style="bold green")

    for l in logs:
        status_style = "green" if l['status'] == "Present" else "yellow" if l['status'] == "Late" else "red"
        table.add_row(l['student_id'], l['name'], f"[{status_style}]{l['status']}[/{status_style}]")

    console.print(table)
    console.print()
    Prompt.ask("Press Enter to continue...")

def attendance_submenu() -> None:
    """Controller routing menu choices for the attendance tracking module."""
    while True:
        print_header("Attendance Tracking")
        rprint("[bold blue]1.[/bold blue] Record Daily Attendance Status")
        rprint("[bold blue]2.[/bold blue] View Student Attendance History Logs")
        rprint("[bold blue]3.[/bold blue] View Attendance Status Logs by Date")
        rprint("[bold blue]4.[/bold blue] Back to Main Menu")
        rprint()
        
        choice = Prompt.ask("[bold cyan]Select an option[/bold cyan]", choices=["1", "2", "3", "4"], default="4")
        
        if choice == "1":
            handle_record_attendance()
        elif choice == "2":
            handle_view_student_attendance()
        elif choice == "3":
            handle_view_date_attendance()
        elif choice == "4":
            break
