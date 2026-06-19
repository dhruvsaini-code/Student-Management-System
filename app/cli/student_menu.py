from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.console import Console
from rich import print as rprint
from typing import List

from app.services.student_service import StudentService
from app.services.search_service import SearchService
from app.cli.landing import print_header
from app.utils.validators import validate_email, validate_date, validate_phone

console = Console()

def show_student_profile(student_id: str) -> None:
    """Retrieves and displays a student profile panel including attendance rate and grades.

    Args:
        student_id: Student ID.
    """
    card = StudentService.get_student_report_card(student_id)
    if not card:
        rprint(f"[bold red]❌ Student with ID '{student_id}' not found.[/bold red]")
        Prompt.ask("\nPress Enter to continue...")
        return

    student = card["student"]
    
    profile_text = (
        f"[bold cyan]Student ID:[/bold cyan] {student.student_id}\n"
        f"[bold cyan]Full Name:[/bold cyan] {student.name}\n"
        f"[bold cyan]Email:[/bold cyan] {student.email}\n"
        f"[bold cyan]Date of Birth:[/bold cyan] {student.dob or 'N/A'}\n"
        f"[bold cyan]Phone Number:[/bold cyan] {student.phone or 'N/A'}\n\n"
        f"[bold yellow]Average Grade:[/bold yellow] {card['average_grade']}%\n"
        f"[bold magenta]Attendance Rate:[/bold magenta] {card['attendance_rate']}%"
    )
    
    print_header(f"Profile: {student.name}")
    console.print(Panel(profile_text, title="Demographics & Performance Summary", border_style="cyan"))
    console.print()

    # Show enrollments table
    enrollments_table = Table(title="Course Enrollments & Grades", border_style="green")
    enrollments_table.add_column("Course Code", style="bold yellow")
    enrollments_table.add_column("Course Name", style="bold white")
    enrollments_table.add_column("Grade", style="bold magenta")

    for e in card['enrollments']:
        grade_str = f"{e['grade']}%" if e['grade'] is not None else "[italic dim]Not Graded[/italic dim]"
        enrollments_table.add_row(e['course_code'], e['course_name'], grade_str)

    # Show recent attendance table
    attendance_table = Table(title="Recent Attendance Logs (Last 10)", border_style="magenta")
    attendance_table.add_column("Date", style="bold blue")
    attendance_table.add_column("Status", style="bold green")

    for a in card['attendance'][:10]:
        status_style = "green" if a['status'] == "Present" else "yellow" if a['status'] == "Late" else "red"
        attendance_table.add_row(a['date'], f"[{status_style}]{a['status']}[/{status_style}]")

    console.print(Columns([enrollments_table, attendance_table], equal=True))
    console.print()
    Prompt.ask("Press Enter to continue...")

def handle_add_student() -> None:
    """Interactive form to collect data and register a student."""
    print_header("Add New Student")
    
    student_id = Prompt.ask("[bold yellow]Enter Student ID[/bold yellow] (e.g. STU006)").strip().upper()
    if not student_id:
        rprint("[bold red]❌ Student ID cannot be empty.[/bold red]")
        Prompt.ask("\nPress Enter to return...")
        return
        
    if StudentService.get_student(student_id):
        rprint(f"[bold red]❌ Student ID '{student_id}' already exists.[/bold red]")
        Prompt.ask("\nPress Enter to return...")
        return

    name = Prompt.ask("[bold yellow]Enter Full Name[/bold yellow]").strip()
    if not name:
        rprint("[bold red]❌ Name cannot be empty.[/bold red]")
        Prompt.ask("\nPress Enter to return...")
        return

    email = Prompt.ask("[bold yellow]Enter Email Address[/bold yellow]").strip()
    if not validate_email(email):
        rprint("[bold red]❌ Invalid email format.[/bold red]")
        Prompt.ask("\nPress Enter to return...")
        return

    dob = Prompt.ask("[bold yellow]Enter Date of Birth[/bold yellow] (YYYY-MM-DD, optional)", default="").strip()
    if dob and not validate_date(dob):
        rprint("[bold red]❌ Invalid date format. Use YYYY-MM-DD.[/bold red]")
        Prompt.ask("\nPress Enter to return...")
        return

    phone = Prompt.ask("[bold yellow]Enter Phone Number[/bold yellow] (optional)", default="").strip()
    if phone and not validate_phone(phone):
        rprint("[bold red]❌ Invalid phone format. Use digits, space, or hyphens.[/bold red]")
        Prompt.ask("\nPress Enter to return...")
        return

    with console.status("[bold green]Saving student records...", spinner="dots"):
        success = StudentService.add_student(student_id, name, email, dob, phone)

    if success:
        rprint(f"\n[bold green]✔ Student '{name}' ({student_id}) added successfully![/bold green]")
    else:
        rprint("\n[bold red]❌ Failed to save student records. Ensure email is unique.[/bold red]")
    Prompt.ask("\nPress Enter to continue...")

def handle_view_students() -> None:
    """Queries and displays all students in a formatted Table."""
    print_header("All Students")
    students = StudentService.get_all_students()
    
    if not students:
        rprint("[bold yellow]No student records found in the database.[/bold yellow]")
        Prompt.ask("\nPress Enter to continue...")
        return

    table = Table(title="Student Catalog", border_style="cyan", header_style="bold magenta")
    table.add_column("Student ID", style="bold yellow")
    table.add_column("Name", style="bold white")
    table.add_column("Email Address", style="green")
    table.add_column("Date of Birth", style="blue")
    table.add_column("Phone Number", style="magenta")

    for s in students:
        table.add_row(s.student_id, s.name, s.email, s.dob or '-', s.phone or '-')

    console.print(table)
    console.print()
    Prompt.ask("Press Enter to continue...")

def handle_update_student() -> None:
    """Interface to update student properties, with current-value defaults."""
    print_header("Update Student Information")
    student_id = Prompt.ask("[bold yellow]Enter Student ID to update[/bold yellow]").strip().upper()
    student = StudentService.get_student(student_id)
    
    if not student:
        rprint(f"[bold red]❌ Student '{student_id}' not found.[/bold red]")
        Prompt.ask("\nPress Enter to return...")
        return

    rprint(f"[cyan]Updating records for {student.name}. Press Enter to preserve current values.[/cyan]\n")
    
    name = Prompt.ask("Full Name", default=student.name).strip()
    
    email = Prompt.ask("Email Address", default=student.email).strip()
    while email and not validate_email(email):
        rprint("[bold red]❌ Invalid email format. Try again.[/bold red]")
        email = Prompt.ask("Email Address", default=student.email).strip()
        
    dob = Prompt.ask("Date of Birth (YYYY-MM-DD)", default=student.dob or "").strip()
    while dob and not validate_date(dob):
        rprint("[bold red]❌ Invalid date format. Use YYYY-MM-DD.[/bold red]")
        dob = Prompt.ask("Date of Birth (YYYY-MM-DD)", default=student.dob or "").strip()
        
    phone = Prompt.ask("Phone Number", default=student.phone or "").strip()
    while phone and not validate_phone(phone):
        rprint("[bold red]❌ Invalid phone format. Try again.[/bold red]")
        phone = Prompt.ask("Phone Number", default=student.phone or "").strip()

    with console.status("[bold yellow]Applying database updates...", spinner="dots"):
        success = StudentService.update_student(student_id, name, email, dob, phone)

    if success:
        rprint("\n[bold green]✔ Student record updated successfully![/bold green]")
    else:
        rprint("\n[bold red]❌ Failed to update record. Check if email conflicts with another student.[/bold red]")
    Prompt.ask("\nPress Enter to continue...")

def handle_delete_student() -> None:
    """Deletes a student after confirming with the administrator."""
    print_header("Delete Student Record")
    student_id = Prompt.ask("[bold yellow]Enter Student ID to delete[/bold yellow]").strip().upper()
    student = StudentService.get_student(student_id)
    
    if not student:
        rprint(f"[bold red]❌ Student '{student_id}' not found.[/bold red]")
        Prompt.ask("\nPress Enter to return...")
        return

    confirm = Confirm.ask(
        f"[bold red]Are you absolutely sure you want to delete {student.name} ({student_id})?[/bold red]\n"
        "This deletes all attendance logs and course grades. This cannot be undone.",
        default=False
    )
    
    if confirm:
        with console.status("[bold red]Removing student from database...", spinner="dots"):
            success = StudentService.delete_student(student_id)
        if success:
            rprint("\n[bold green]✔ Student record and all dependencies deleted successfully.[/bold green]")
        else:
            rprint("\n[bold red]❌ Failed to delete student due to database error.[/bold red]")
    else:
        rprint("\n[yellow]Deletion cancelled.[/yellow]")
    Prompt.ask("\nPress Enter to continue...")

def handle_search_engine() -> None:
    """Interactive search system supporting field-specific query or fuzzy matching."""
    while True:
        print_header("Student Search Engine")
        rprint("[bold cyan]1.[/bold cyan] Search by Student ID")
        rprint("[bold cyan]2.[/bold cyan] Search by Name")
        rprint("[bold cyan]3.[/bold cyan] Search by Email")
        rprint("[bold cyan]4.[/bold cyan] Fuzzy Search Engine (Match Ratio Rank)")
        rprint("[bold cyan]5.[/bold cyan] Back to Student Management")
        rprint()
        
        choice = Prompt.ask("[bold magenta]Select query type[/bold magenta]", choices=["1", "2", "3", "4", "5"], default="5")
        if choice == "5":
            break
            
        query = Prompt.ask("[bold yellow]Enter search query[/bold yellow]").strip()
        if not query:
            rprint("[bold red]❌ Search query cannot be empty.[/bold red]")
            Prompt.ask("\nPress Enter to try again...")
            continue
            
        results: List[Student] = []
        fuzzy_results = []
        
        with console.status("[bold magenta]Scanning student indexes...", spinner="dots"):
            if choice == "1":
                results = SearchService.search_by_id(query)
            elif choice == "2":
                results = SearchService.search_by_name(query)
            elif choice == "3":
                results = SearchService.search_by_email(query)
            elif choice == "4":
                fuzzy_results = SearchService.search_fuzzy(query)

        # Print results
        print_header("Search Results")
        if (choice != "4" and not results) or (choice == "4" and not fuzzy_results):
            rprint("[bold yellow]No matching student records found.[/bold yellow]")
        else:
            table = Table(border_style="cyan", header_style="bold magenta")
            table.add_column("Student ID", style="bold yellow")
            table.add_column("Name", style="bold white")
            table.add_column("Email Address", style="green")
            if choice == "4":
                table.add_column("Match Score", style="bold yellow")
                
            if choice == "4":
                for stu, score in fuzzy_results:
                    table.add_row(stu.student_id, stu.name, stu.email, f"{score}%")
            else:
                for stu in results:
                    table.add_row(stu.student_id, stu.name, stu.email)
                    
            console.print(table)
            console.print()
            
            # Allow opening details directly
            view_opt = Confirm.ask("Would you like to view a student's full profile?", default=False)
            if view_opt:
                selected_id = Prompt.ask("[bold cyan]Enter Student ID[/bold cyan]").strip().upper()
                show_student_profile(selected_id)
                continue
                
        Prompt.ask("\nPress Enter to continue...")

def handle_csv_import_export() -> None:
    """Interactively exports or imports student lists using CSV files."""
    while True:
        print_header("CSV Import/Export Operations")
        rprint("[bold cyan]1.[/bold cyan] Export Student Catalog to CSV")
        rprint("[bold cyan]2.[/bold cyan] Import Student Records from CSV")
        rprint("[bold cyan]3.[/bold cyan] Back to Student Management")
        rprint()
        
        choice = Prompt.ask("[bold magenta]Select option[/bold magenta]", choices=["1", "2", "3"], default="3")
        if choice == "3":
            break
            
        if choice == "1":
            path = Prompt.ask("[bold yellow]Enter destination CSV path[/bold yellow]", default="exported_students.csv").strip()
            with console.status("[bold green]Writing CSV file...", spinner="dots"):
                success = StudentService.export_students_to_csv(path)
            if success:
                rprint(f"\n[bold green]✔ Catalog exported successfully to '{path}'[/bold green]")
            else:
                rprint(f"\n[bold red]❌ Failed to export catalog to '{path}'. Check write permissions.[/bold red]")
                
        elif choice == "2":
            path = Prompt.ask("[bold yellow]Enter source CSV path[/bold yellow]", default="students_import.csv").strip()
            with console.status("[bold green]Importing CSV records...", spinner="dots"):
                success, details = StudentService.import_students_from_csv(path)
            if success:
                rprint(f"\n[bold green]✔ Import summary: {details['imported']} records added.[/bold green]")
                if details["errors"]:
                    rprint("\n[bold yellow]Warnings/errors encountered during processing:[/bold yellow]")
                    for err in details["errors"][:10]:
                        rprint(f"[red]• {err}[/red]")
                    if len(details["errors"]) > 10:
                        rprint(f"[italic dim]... and {len(details['errors']) - 10} more warnings.[/italic dim]")
            else:
                rprint(f"\n[bold red]❌ Import failed: {', '.join(details.get('errors', []))}[/bold red]")
                
        Prompt.ask("\nPress Enter to continue...")

def student_submenu() -> None:
    """Controller routing menu options for the student module."""
    while True:
        print_header("Student Records Management")
        rprint("[bold magenta]1.[/bold magenta] Add New Student Profile")
        rprint("[bold magenta]2.[/bold magenta] View All Student Profiles")
        rprint("[bold magenta]3.[/bold magenta] Search Student Profiles (Search Engine)")
        rprint("[bold magenta]4.[/bold magenta] Update Student Info")
        rprint("[bold magenta]5.[/bold magenta] Delete Student Record")
        rprint("[bold magenta]6.[/bold magenta] CSV Import & Export Operations")
        rprint("[bold magenta]7.[/bold magenta] Back to Main Menu")
        rprint()
        
        choice = Prompt.ask("[bold cyan]Select an option[/bold cyan]", choices=["1", "2", "3", "4", "5", "6", "7"], default="7")
        
        if choice == "1":
            handle_add_student()
        elif choice == "2":
            handle_view_students()
        elif choice == "3":
            handle_search_engine()
        elif choice == "4":
            handle_update_student()
        elif choice == "5":
            handle_delete_student()
        elif choice == "6":
            handle_csv_import_export()
        elif choice == "7":
            break
