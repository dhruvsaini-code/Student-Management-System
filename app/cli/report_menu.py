from rich.prompt import Prompt
from rich.console import Console
from rich import print as rprint

from app.services.report_service import ReportService
from app.services.visualization_service import VisualizationService
from app.cli.landing import print_header

console = Console()

def handle_student_pdf_card() -> None:
    """Takes input student ID and generates a PDF report card document."""
    print_header("Generate PDF Report Card")
    student_id = Prompt.ask("[bold yellow]Enter Student ID[/bold yellow]").strip().upper()
    
    with console.status("[bold green]Compiling PDF layout & database records...", spinner="dots"):
        pdf_path = ReportService.generate_student_report_card(student_id)

    if pdf_path:
        rprint(f"\n[bold green]✔ PDF Report Card generated successfully![/bold green]")
        rprint(f"[bold cyan]Location:[/bold cyan] {pdf_path}")
    else:
        rprint(f"\n[bold red]❌ Failed to generate Report Card. Verify Student ID '{student_id}' exists.[/bold red]")
    Prompt.ask("\nPress Enter to continue...")

def handle_attendance_pdf_report() -> None:
    """Generates the school-wide PDF attendance analytics summary."""
    print_header("Generate Attendance Report PDF")
    
    with console.status("[bold green]Generating overall attendance PDF report...", spinner="dots"):
        pdf_path = ReportService.generate_attendance_report()

    if pdf_path:
        rprint(f"\n[bold green]✔ Attendance Report PDF generated successfully![/bold green]")
        rprint(f"[bold cyan]Location:[/bold cyan] {pdf_path}")
    else:
        rprint("\n[bold red]❌ Failed to compile attendance report.[/bold red]")
    Prompt.ask("\nPress Enter to continue...")

def handle_class_performance_pdf() -> None:
    """Generates the class performance and course list stats PDF report."""
    print_header("Generate Academic Performance PDF")
    
    with console.status("[bold green]Compiling class performance statistics...", spinner="dots"):
        pdf_path = ReportService.generate_class_performance_report()

    if pdf_path:
        rprint(f"\n[bold green]✔ Academic Performance PDF report generated successfully![/bold green]")
        rprint(f"[bold cyan]Location:[/bold cyan] {pdf_path}")
    else:
        rprint("\n[bold red]❌ Failed to compile academic performance report.[/bold red]")
    Prompt.ask("\nPress Enter to continue...")

def handle_generate_charts() -> None:
    """Invokes matplotlib to render distribution histograms and bar charts, saving as PNGs."""
    print_header("Data Visualization Dashboard")
    rprint("[bold yellow]Generating visual analytics (Matplotlib PNGs)...[/bold yellow]\n")

    # Chart 1: Grade Distributions
    with console.status("[bold magenta]Plotting academic grades distribution...", spinner="dots"):
        success1, path1 = VisualizationService.generate_grade_distribution()
    if success1:
        rprint(f"[bold green]✔ Grades distribution histogram saved:[/bold green] {path1}")
    else:
        rprint(f"[bold red]❌ Failed to plot grades distribution:[/bold red] {path1}")

    # Chart 2: Attendance Distribution
    with console.status("[bold magenta]Plotting attendance status counts...", spinner="dots"):
        success2, path2 = VisualizationService.generate_attendance_graph()
    if success2:
        rprint(f"[bold green]✔ Attendance status summary graph saved:[/bold green] {path2}")
    else:
        rprint(f"[bold red]❌ Failed to plot attendance status graph:[/bold red] {path2}")

    # Chart 3: Course Enrollments
    with console.status("[bold magenta]Plotting course sizes...", spinner="dots"):
        success3, path3 = VisualizationService.generate_enrollment_graph()
    if success3:
        rprint(f"[bold green]✔ Course size & enrollment bar chart saved:[/bold green] {path3}")
    else:
        rprint(f"[bold red]❌ Failed to plot course enrollment chart:[/bold red] {path3}")

    Prompt.ask("\nPress Enter to continue...")

def report_submenu() -> None:
    """Controller routing menu choices for report cards, PDFs, and charts."""
    while True:
        print_header("Reports & Visual Analytics")
        rprint("[bold magenta]1.[/bold magenta] Generate Student PDF Report Card")
        rprint("[bold magenta]2.[/bold magenta] Generate School-wide Attendance Report PDF")
        rprint("[bold magenta]3.[/bold magenta] Generate Academic Performance Report PDF")
        rprint("[bold magenta]4.[/bold magenta] Render Matplotlib Analytics Graphs (PNG charts)")
        rprint("[bold magenta]5.[/bold magenta] Back to Main Menu")
        rprint()
        
        choice = Prompt.ask("[bold cyan]Select an option[/bold cyan]", choices=["1", "2", "3", "4", "5"], default="5")
        
        if choice == "1":
            handle_student_pdf_card()
        elif choice == "2":
            handle_attendance_pdf_report()
        elif choice == "3":
            handle_class_performance_pdf()
        elif choice == "4":
            handle_generate_charts()
        elif choice == "5":
            break
