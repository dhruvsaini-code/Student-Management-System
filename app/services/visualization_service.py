import matplotlib
# Use non-interactive backend to prevent GUI popups in TUI
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from typing import Tuple, Dict, Any

from app.utils.config import Config
from app.database.connection import get_db_connection
from app.utils.logger import activity_logger, error_logger

class VisualizationService:
    """Generates charts for academic grades, enrollment metrics, and attendance distributions."""

    @staticmethod
    def generate_grade_distribution() -> Tuple[bool, str]:
        """Creates a histogram representing the overall distribution of grades.

        Saves the resulting PNG image in the charts directory.

        Returns:
            A tuple of (success_status, output_file_path_or_error_msg).
        """
        Config.initialize_directories()
        dest_path = Config.CHARTS_DIR / "grade_distribution.png"

        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT grade FROM enrollments WHERE grade IS NOT NULL")
            grades = [row[0] for row in cursor.fetchall()]
            conn.close()

            if not grades:
                return False, "No graded course enrollments exist to plot."

            # Create plot
            plt.figure(figsize=(7, 4.5))
            plt.style.use('ggplot')
            
            # Draw histogram
            n, bins, patches = plt.hist(
                grades, bins=10, range=(0, 100), color='#2B2E4A', edgecolor='#FFFFFF', rwidth=0.85
            )
            
            # Style customizations
            plt.title("Academic Grades Distribution", fontsize=14, fontweight='bold', pad=15, color='#2B2E4A')
            plt.xlabel("Grade Range (0 - 100%)", fontsize=11, labelpad=10)
            plt.ylabel("Number of Students", fontsize=11, labelpad=10)
            plt.grid(True, linestyle='--', alpha=0.5)
            plt.xlim(0, 100)
            
            # Save and clean up
            plt.tight_layout()
            plt.savefig(str(dest_path), dpi=150)
            plt.close()

            activity_logger.info(f"Grade distribution chart generated at '{dest_path}'")
            return True, str(dest_path)

        except Exception as e:
            error_logger.error(f"Error plotting grade distribution: {str(e)}")
            plt.close()
            return False, str(e)

    @staticmethod
    def generate_attendance_graph() -> Tuple[bool, str]:
        """Creates a bar chart representing attendance rates across Present, Absent, and Late statuses.

        Returns:
            A tuple of (success_status, output_file_path_or_error_msg).
        """
        Config.initialize_directories()
        dest_path = Config.CHARTS_DIR / "attendance_graph.png"

        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT status, COUNT(*) as cnt FROM attendance GROUP BY status")
            rows = cursor.fetchall()
            conn.close()

            status_counts = {"Present": 0, "Absent": 0, "Late": 0}
            for row in rows:
                if row["status"] in status_counts:
                    status_counts[row["status"]] = row["cnt"]

            # Create plot
            plt.figure(figsize=(7, 4.5))
            plt.style.use('ggplot')

            categories = list(status_counts.keys())
            values = list(status_counts.values())
            bar_colors = ['#2E8B57', '#CD5C5C', '#FF8C00']  # Green, Red, Orange

            bars = plt.bar(categories, values, color=bar_colors, width=0.6, edgecolor='#FFFFFF')

            # Add counts above bars
            for bar in bars:
                height = bar.get_height()
                plt.text(
                    bar.get_x() + bar.get_width()/2.0, height + 0.1,
                    f'{int(height)}', ha='center', va='bottom', fontsize=10, fontweight='bold'
                )

            plt.title("Attendance Status Distribution Summary", fontsize=14, fontweight='bold', pad=15, color='#2B2E4A')
            plt.xlabel("Attendance Type Logged", fontsize=11, labelpad=10)
            plt.ylabel("Days Checked / Records", fontsize=11, labelpad=10)
            plt.grid(True, axis='y', linestyle='--', alpha=0.5)
            
            plt.tight_layout()
            plt.savefig(str(dest_path), dpi=150)
            plt.close()

            activity_logger.info(f"Attendance status chart generated at '{dest_path}'")
            return True, str(dest_path)

        except Exception as e:
            error_logger.error(f"Error plotting attendance summary: {str(e)}")
            plt.close()
            return False, str(e)

    @staticmethod
    def generate_enrollment_graph() -> Tuple[bool, str]:
        """Creates a horizontal bar chart representing student enrollments per course.

        Returns:
            A tuple of (success_status, output_file_path_or_error_msg).
        """
        Config.initialize_directories()
        dest_path = Config.CHARTS_DIR / "course_enrollment.png"

        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.course_code, COUNT(e.student_id) as enrolled_count
                FROM courses c
                LEFT JOIN enrollments e ON c.course_code = e.course_code
                GROUP BY c.course_code
                ORDER BY enrolled_count ASC
            """)
            rows = cursor.fetchall()
            conn.close()

            if not rows:
                return False, "No courses exist to plot enrollments."

            course_codes = [row[0] for row in rows]
            counts = [row[1] for row in rows]

            # Create plot
            plt.figure(figsize=(7, 4.5))
            plt.style.use('ggplot')

            bars = plt.barh(course_codes, counts, color='#E84545', height=0.6, edgecolor='#FFFFFF')

            # Add counts inside/outside bars
            for bar in bars:
                width = bar.get_width()
                plt.text(
                    width + 0.1, bar.get_y() + bar.get_height()/2.0,
                    f'{int(width)}', ha='left', va='center', fontsize=10, fontweight='bold'
                )

            plt.title("Student Enrollment counts per Course", fontsize=14, fontweight='bold', pad=15, color='#2B2E4A')
            plt.xlabel("Number of Students Enrolled", fontsize=11, labelpad=10)
            plt.ylabel("Course Code", fontsize=11, labelpad=10)
            plt.grid(True, axis='x', linestyle='--', alpha=0.5)

            plt.tight_layout()
            plt.savefig(str(dest_path), dpi=150)
            plt.close()

            activity_logger.info(f"Course enrollments chart generated at '{dest_path}'")
            return True, str(dest_path)

        except Exception as e:
            error_logger.error(f"Error plotting course enrollments graph: {str(e)}")
            plt.close()
            return False, str(e)
