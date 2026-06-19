from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.console import Console
from rich import print as rprint

from app.services.course_service import CourseService
from app.services.student_service import StudentService
from app.cli.landing import print_header

console = Console()

def handle_add_course() -> None:
    """Collects inputs and adds a course to the catalog."""
    print_header("Add New Course")
    
    code = Prompt.ask("[bold yellow]Enter Course Code[/bold yellow] (e.g. CS101)").strip().upper()
    if not code:
        rprint("[bold red]❌ Course Code cannot be empty.[/bold red]")
        Prompt.ask("\nPress Enter to return...")
        return
        
    if CourseService.get_course(code):
        rprint(f"[bold red]❌ Course code '{code}' already exists.[/bold red]")
        Prompt.ask("\nPress Enter to return...")
        return

    name = Prompt.ask("[bold yellow]Enter Course Name[/bold yellow]").strip()
    if not name:
        rprint("[bold red]❌ Course Name cannot be empty.[/bold red]")
        Prompt.ask("\nPress Enter to return...")
        return

    with console.status("[bold green]Saving course catalog details...", spinner="dots"):
        success = CourseService.add_course(code, name)

    if success:
        rprint(f"\n[bold green]✔ Course {code} - '{name}' added successfully![/bold green]")
    else:
        rprint("\n[bold red]❌ Failed to save course catalog details.[/bold red]")
    Prompt.ask("\nPress Enter to continue...")

def handle_view_courses() -> None:
    """Queries and lists all course catalog items."""
    print_header("Course Catalog")
    courses = CourseService.get_all_courses()
    
    if not courses:
        rprint("[bold yellow]No courses found in the catalog.[/bold yellow]")
        Prompt.ask("\nPress Enter to continue...")
        return

    table = Table(title="Course Catalog", border_style="green", header_style="bold magenta")
    table.add_column("Course Code", style="bold yellow")
    table.add_column("Course Name", style="bold white")

    for c in courses:
        table.add_row(c.course_code, c.course_name)

    console.print(table)
    console.print()
    Prompt.ask("Press Enter to continue...")

def handle_enroll_student() -> None:
    """Enrolls an active student into a course."""
    print_header("Enroll Student in Course")
    
    student_id = Prompt.ask("[bold yellow]Enter Student ID[/bold yellow]").strip().upper()
    if not StudentService.get_student(student_id):
        rprint(f"[bold red]❌ Student with ID '{student_id}' not found.[/bold red]")
        Prompt.ask("\nPress Enter to return...")
        return

    course_code = Prompt.ask("[bold yellow]Enter Course Code[/bold yellow]").strip().upper()
    if not CourseService.get_course(course_code):
        rprint(f"[bold red]❌ Course Code '{course_code}' not found.[/bold red]")
        Prompt.ask("\nPress Enter to return...")
        return

    with console.status("[bold green]Enrolling student in database...", spinner="dots"):
        success = CourseService.enroll_student(student_id, course_code)

    if success:
        rprint(f"\n[bold green]✔ Student '{student_id}' successfully enrolled in course '{course_code}'![/bold green]")
    else:
        rprint("\n[bold red]❌ Enrollment failed. Student might already be enrolled in this course.[/bold red]")
    Prompt.ask("\nPress Enter to continue...")

def handle_grade_student() -> None:
    """Records or updates student numeric grade in an enrolled course."""
    print_header("Enter Student Grade")
    
    student_id = Prompt.ask("[bold yellow]Enter Student ID[/bold yellow]").strip().upper()
    course_code = Prompt.ask("[bold yellow]Enter Course Code[/bold yellow]").strip().upper()

    enrollments = CourseService.get_student_enrollments(student_id)
    enrolled = any(e["course_code"] == course_code for e in enrollments)

    if not enrolled:
        rprint(f"[bold red]❌ Student '{student_id}' is not enrolled in course '{course_code}'.[/bold red]")
        Prompt.ask("\nPress Enter to return...")
        return

    grade_str = Prompt.ask("[bold yellow]Enter Numeric Grade[/bold yellow] (0.0 - 100.0)").strip()
    try:
        grade = float(grade_str)
        if not (0.0 <= grade <= 100.0):
            raise ValueError
    except ValueError:
        rprint("[bold red]❌ Grade must be a valid number between 0.0 and 100.0.[/bold red]")
        Prompt.ask("\nPress Enter to return...")
        return

    with console.status("[bold yellow]Recording academic grade...", spinner="dots"):
        success = CourseService.update_grade(student_id, course_code, grade)

    if success:
        rprint(f"\n[bold green]✔ Grade of {grade}% recorded successfully for student '{student_id}' in course '{course_code}'![/bold green]")
    else:
        rprint("\n[bold red]❌ Failed to record grade in database.[/bold red]")
    Prompt.ask("\nPress Enter to continue...")

def handle_view_course_enrollments() -> None:
    """Queries and prints all students and grades in a course."""
    print_header("View Course Enrollments")
    
    course_code = Prompt.ask("[bold yellow]Enter Course Code[/bold yellow]").strip().upper()
    course = CourseService.get_course(course_code)
    
    if not course:
        rprint(f"[bold red]❌ Course '{course_code}' not found.[/bold red]")
        Prompt.ask("\nPress Enter to return...")
        return

    enrollments = CourseService.get_course_enrollments(course_code)
    if not enrollments:
        rprint(f"[bold yellow]No students are enrolled in '{course.course_name}' ({course_code}).[/bold yellow]")
        Prompt.ask("\nPress Enter to continue...")
        return

    table = Table(title=f"Course Class list: {course.course_name}", border_style="green")
    table.add_column("Student ID", style="bold yellow")
    table.add_column("Student Name", style="bold white")
    table.add_column("Grade", style="bold magenta")

    for e in enrollments:
        grade_str = f"{e['grade']}%" if e['grade'] is not None else "[italic dim]Not Graded[/italic dim]"
        table.add_row(e['student_id'], e['name'], grade_str)

    console.print(table)
    console.print()
    Prompt.ask("Press Enter to continue...")

def handle_delete_course() -> None:
    """Deletes course records after administrator verification."""
    print_header("Delete Course Catalog Entry")
    
    course_code = Prompt.ask("[bold yellow]Enter Course Code to delete[/bold yellow]").strip().upper()
    course = CourseService.get_course(course_code)
    
    if not course:
        rprint(f"[bold red]❌ Course '{course_code}' not found in catalog.[/bold red]")
        Prompt.ask("\nPress Enter to return...")
        return

    confirm = Confirm.ask(
        f"[bold red]Are you absolutely sure you want to delete course {course.course_name} ({course_code})?[/bold red]\n"
        "This deletes all enrollments and grades registered for this course. This cannot be undone.",
        default=False
    )
    
    if confirm:
        with console.status("[bold red]Removing course catalog entry...", spinner="dots"):
            success = CourseService.delete_course(course_code)
        if success:
            rprint("\n[bold green]✔ Course record and all associations deleted successfully.[/bold green]")
        else:
            rprint("\n[bold red]❌ Failed to delete course catalog entry due to database error.[/bold red]")
    else:
        rprint("\n[yellow]Deletion cancelled.[/yellow]")
    Prompt.ask("\nPress Enter to continue...")

def course_submenu() -> None:
    """Controller routing menu choices for the course management module."""
    while True:
        print_header("Course Catalog & Grades Management")
        rprint("[bold green]1.[/bold green] Add New Course Catalog Entry")
        rprint("[bold green]2.[/bold green] View Course Catalog")
        rprint("[bold green]3.[/bold green] Enroll Student in Course")
        rprint("[bold green]4.[/bold green] Enter/Update Student Grade")
        rprint("[bold green]5.[/bold green] View Course Enrollments & Grades")
        rprint("[bold green]6.[/bold green] Delete Course Catalog Entry")
        rprint("[bold green]7.[/bold green] Back to Main Menu")
        rprint()
        
        choice = Prompt.ask("[bold cyan]Select an option[/bold cyan]", choices=["1", "2", "3", "4", "5", "6", "7"], default="7")
        
        if choice == "1":
            handle_add_course()
        elif choice == "2":
            handle_view_courses()
        elif choice == "3":
            handle_enroll_student()
        elif choice == "4":
            handle_grade_student()
        elif choice == "5":
            handle_view_course_enrollments()
        elif choice == "6":
            handle_delete_course()
        elif choice == "7":
            break
