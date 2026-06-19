from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.console import Console
from rich.prompt import Prompt
from rich import print as rprint

from app.services.student_service import StudentService
from app.services.course_service import CourseService
from app.cli.landing import print_header

console = Console()

def render_top_and_bottom_students() -> None:
    """Retrieves and prints the top and lowest performing students by average grade."""
    print_header("Performance Leaders & Alerts")
    
    top = StudentService.get_top_performing_students(5)
    bottom = StudentService.get_lowest_performing_students(5)
    
    # Render Top Students Table
    top_table = Table(title="Top Performing Students (GPA)", border_style="green", header_style="bold green")
    top_table.add_column("Rank", style="bold green", justify="center")
    top_table.add_column("Student ID", style="bold yellow")
    top_table.add_column("Name", style="bold white")
    top_table.add_column("Avg Grade", style="bold green")

    for idx, s in enumerate(top, 1):
        top_table.add_row(str(idx), s["student_id"], s["name"], f"{round(s['avg_grade'], 1)}%")

    # Render Bottom Students Table
    bottom_table = Table(title="Academic Concern List (Lowest GPA)", border_style="red", header_style="bold red")
    bottom_table.add_column("Alert", style="bold red", justify="center")
    bottom_table.add_column("Student ID", style="bold yellow")
    bottom_table.add_column("Name", style="bold white")
    bottom_table.add_column("Avg Grade", style="bold red")

    for idx, s in enumerate(bottom, 1):
        bottom_table.add_row(f"⚠️ {idx}", s["student_id"], s["name"], f"{round(s['avg_grade'], 1)}%")

    console.print(Columns([top_table, bottom_table], equal=True))
    console.print()
    Prompt.ask("Press Enter to continue...")

def render_attendance_analytics() -> None:
    """Displays overall attendance logs count distribution and lists low attendance warning flags."""
    print_header("Attendance Analytics Dashboard")
    
    analytics = StudentService.get_attendance_analytics()
    counts = analytics["counts"]
    
    # Calculate totals
    total = sum(counts.values())
    present_pct = (counts.get("Present", 0) / total * 100) if total > 0 else 0
    absent_pct = (counts.get("Absent", 0) / total * 100) if total > 0 else 0
    late_pct = (counts.get("Late", 0) / total * 100) if total > 0 else 0

    stats_text = (
        f"[bold blue]Total Logs Registered:[/bold blue] {total}\n\n"
        f"[bold green]Present Logs:[/bold green] {counts.get('Present', 0)} ({round(present_pct, 1)}%)\n"
        f"[bold yellow]Late Logs:   [/bold yellow] {counts.get('Late', 0)} ({round(late_pct, 1)}%)\n"
        f"[bold red]Absent Logs: [/bold red] {counts.get('Absent', 0)} ({round(absent_pct, 1)}%)"
    )
    
    console.print(Panel(stats_text, title="Log Distribution Summary", border_style="blue"))
    console.print()

    # List warnings
    warning_table = Table(title="Low Attendance Warnings (Rate < 75%)", border_style="red")
    warning_table.add_column("Student ID", style="bold yellow")
    warning_table.add_column("Name", style="bold white")
    warning_table.add_column("Attendance Rate", style="bold red")

    for bad in analytics["low_attendance"]:
        warning_table.add_row(bad["student_id"], bad["name"], f"{round(bad['rate'], 1)}%")

    if not analytics["low_attendance"]:
        warning_table.add_row("No students flagged.", "All attendance rates >= 75%", "-")

    console.print(warning_table)
    console.print()
    Prompt.ask("Press Enter to continue...")

def render_course_analytics() -> None:
    """Lists enrollment sizes and average performance metrics grouped by course catalog item."""
    print_header("Course-wise Metrics & Size")
    
    course_stats = CourseService.get_course_analytics()
    
    if not course_stats:
        rprint("[bold yellow]No course data is currently available.[/bold yellow]")
        Prompt.ask("\nPress Enter to continue...")
        return

    table = Table(title="Course Analytics Overview", border_style="green", header_style="bold magenta")
    table.add_column("Course Code", style="bold yellow")
    table.add_column("Course Name", style="bold white")
    table.add_column("Enrolled Count", style="bold blue")
    table.add_column("Average Grade", style="bold green")
    table.add_column("Passing Rate (>=60%)", style="bold yellow")

    for c in course_stats:
        table.add_row(
            c["course_code"],
            c["course_name"],
            str(c["enrolled_count"]),
            f"{c['avg_grade']}%",
            f"{c['passing_rate']}%"
        )

    console.print(table)
    console.print()
    Prompt.ask("Press Enter to continue...")

def render_gpa_rankings() -> None:
    """Lists all students ranked by average GPA."""
    print_header("GPA Rankings & Catalog Status")
    
    rankings = StudentService.get_gpa_ranking_table()
    
    if not rankings:
        rprint("[bold yellow]No student ranking data is currently available.[/bold yellow]")
        Prompt.ask("\nPress Enter to continue...")
        return

    table = Table(title="Class Rankings (GPAs)", border_style="magenta", header_style="bold magenta")
    table.add_column("Rank", style="bold white", justify="center")
    table.add_column("Student ID", style="bold yellow")
    table.add_column("Name", style="bold white")
    table.add_column("Avg Grade", style="bold green")
    table.add_column("Enrolled Count", style="bold blue")

    for idx, r in enumerate(rankings, 1):
        table.add_row(
            str(r["rank"]),
            r["student_id"],
            r["name"],
            f"{r['avg_grade']}%" if r["avg_grade"] > 0 else "N/A",
            str(r["courses_count"])
        )

    console.print(table)
    console.print()
    Prompt.ask("Press Enter to continue...")

def analytics_submenu() -> None:
    """Controller routing menu choices for the Analytics Dashboard."""
    while True:
        print_header("Analytics Dashboard & Metrics")
        rprint("[bold magenta]1.[/bold magenta] Academic Performers (Top/Bottom GPAs)")
        rprint("[bold magenta]2.[/bold magenta] Attendance Distribution & Warning Flags")
        rprint("[bold magenta]3.[/bold magenta] Course-wise Metrics & Size Statistics")
        rprint("[bold magenta]4.[/bold magenta] Complete Class GPA Rankings Table")
        rprint("[bold magenta]5.[/bold magenta] Back to Main Menu")
        rprint()
        
        choice = Prompt.ask("[bold cyan]Select an option[/bold cyan]", choices=["1", "2", "3", "4", "5"], default="5")
        
        if choice == "1":
            render_top_and_bottom_students()
        elif choice == "2":
            render_attendance_analytics()
        elif choice == "3":
            render_course_analytics()
        elif choice == "4":
            render_gpa_rankings()
        elif choice == "5":
            break
