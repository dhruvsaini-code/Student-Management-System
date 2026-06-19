import os
from typing import Optional
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

from app.utils.config import Config
from app.services.student_service import StudentService
from app.services.course_service import CourseService
from app.utils.logger import activity_logger, error_logger

class ReportService:
    """Generates PDF documents for student report cards, attendance summaries, and course stats."""

    @staticmethod
    def generate_student_report_card(student_id: str) -> Optional[str]:
        """Generates a professional PDF report card for a single student.

        Args:
            student_id: Target student identifier.

        Returns:
            The absolute file path of the generated PDF, or None if errors.
        """
        report_data = StudentService.get_student_report_card(student_id)
        if not report_data:
            return None

        student = report_data["student"]
        pdf_path = Config.REPORTS_DIR / f"report_card_{student.student_id}.pdf"

        try:
            doc = SimpleDocTemplate(
                str(pdf_path),
                pagesize=letter,
                rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54
            )
            story = []
            styles = getSampleStyleSheet()

            # Custom typography styles
            title_style = ParagraphStyle(
                'DocTitle',
                parent=styles['Heading1'],
                fontSize=24,
                leading=28,
                textColor=colors.HexColor("#2B2E4A"),
                spaceAfter=15,
                alignment=1 # Centered
            )
            subtitle_style = ParagraphStyle(
                'DocSubTitle',
                parent=styles['Normal'],
                fontSize=10,
                leading=12,
                textColor=colors.HexColor("#E84545"),
                spaceAfter=25,
                alignment=1
            )
            section_style = ParagraphStyle(
                'DocSection',
                parent=styles['Heading2'],
                fontSize=14,
                leading=18,
                textColor=colors.HexColor("#2B2E4A"),
                spaceBefore=15,
                spaceAfter=8
            )
            body_style = ParagraphStyle(
                'DocBody',
                parent=styles['Normal'],
                fontSize=10,
                leading=14,
                textColor=colors.HexColor("#333333")
            )

            # Header
            story.append(Paragraph("STUDENT REPORT CARD", title_style))
            story.append(Paragraph(f"Generated on: {os.environ.get('APP_DATE', '2026-06-19')}", subtitle_style))
            story.append(Spacer(1, 10))

            # Student Info Section
            info_data = [
                [Paragraph("<b>Student ID:</b>", body_style), Paragraph(student.student_id, body_style),
                 Paragraph("<b>Date of Birth:</b>", body_style), Paragraph(student.dob or "N/A", body_style)],
                [Paragraph("<b>Full Name:</b>", body_style), Paragraph(student.name, body_style),
                 Paragraph("<b>Phone Number:</b>", body_style), Paragraph(student.phone or "N/A", body_style)],
                [Paragraph("<b>Email Address:</b>", body_style), Paragraph(student.email, body_style),
                 Paragraph("<b>Current GPA:</b>", body_style), Paragraph(f"{report_data['average_grade']}%", body_style)]
            ]
            info_table = Table(info_data, colWidths=[1.2*inch, 2.3*inch, 1.2*inch, 2.3*inch])
            info_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F9F9F9")),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#EAEAEA")),
                ('TOPPADDING', (0,0), (-1,-1), 8),
                ('LEFTPADDING', (0,0), (-1,-1), 10),
                ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ]))
            story.append(info_table)
            story.append(Spacer(1, 20))

            # Courses & Grades Section
            story.append(Paragraph("Enrolled Courses & Academic Grades", section_style))
            course_header_style = ParagraphStyle('CH', parent=body_style, fontName='Helvetica-Bold', textColor=colors.white)
            
            course_data = [[
                Paragraph("Course Code", course_header_style),
                Paragraph("Course Name", course_header_style),
                Paragraph("Grade Achieved", course_header_style)
            ]]
            
            for enc in report_data["enrollments"]:
                g_val = f"{enc['grade']}%" if enc['grade'] is not None else "Not Graded"
                course_data.append([
                    Paragraph(enc["course_code"], body_style),
                    Paragraph(enc["course_name"], body_style),
                    Paragraph(g_val, body_style)
                ])

            if len(course_data) == 1:
                course_data.append([Paragraph("No course enrollments found.", body_style), "", ""])

            course_table = Table(course_data, colWidths=[1.5*inch, 3.5*inch, 2.0*inch])
            course_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2B2E4A")),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F9F9F9")]),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E1E1E1")),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ('TOPPADDING', (0,0), (-1,-1), 8),
                ('LEFTPADDING', (0,0), (-1,-1), 10),
            ]))
            story.append(course_table)
            story.append(Spacer(1, 20))

            # Attendance Record Section
            story.append(Paragraph("Attendance Rate Summary", section_style))
            story.append(Paragraph(f"Overall Attendance: <b>{report_data['attendance_rate']}%</b> (Present or Late)", body_style))
            story.append(Spacer(1, 10))

            attendance_data = [[
                Paragraph("Date Checked", course_header_style),
                Paragraph("Status logged", course_header_style)
            ]]

            # Limit to recent 10 records to keep PDF neat
            for att in report_data["attendance"][:10]:
                status_color = "#2E8B57" if att['status'] == "Present" else "#FF8C00" if att['status'] == "Late" else "#CD5C5C"
                status_style = ParagraphStyle('AttStatus', parent=body_style, textColor=colors.HexColor(status_color), fontName='Helvetica-Bold')
                attendance_data.append([
                    Paragraph(att["date"], body_style),
                    Paragraph(att["status"], status_style)
                ])

            if len(attendance_data) == 1:
                attendance_data.append([Paragraph("No attendance records logged.", body_style), ""])

            attendance_table = Table(attendance_data, colWidths=[3.5*inch, 3.5*inch])
            attendance_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E84545")),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F9F9F9")]),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E1E1E1")),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ('TOPPADDING', (0,0), (-1,-1), 8),
                ('LEFTPADDING', (0,0), (-1,-1), 10),
            ]))
            story.append(attendance_table)

            doc.build(story)
            activity_logger.info(f"Report card PDF generated at '{pdf_path}'")
            return str(pdf_path)

        except Exception as e:
            error_logger.error(f"Error compiling student report PDF for '{student_id}': {str(e)}")
            return None

    @staticmethod
    def generate_attendance_report() -> Optional[str]:
        """Generates a PDF document compiling attendance rates and warnings across the school.

        Returns:
            The absolute file path of the generated PDF, or None if errors.
        """
        stats = StudentService.get_system_stats()
        analytics = StudentService.get_attendance_analytics()
        pdf_path = Config.REPORTS_DIR / "attendance_report.pdf"

        try:
            doc = SimpleDocTemplate(
                str(pdf_path),
                pagesize=letter,
                rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54
            )
            story = []
            styles = getSampleStyleSheet()

            # Custom typography styles
            title_style = ParagraphStyle(
                'DocTitle', parent=styles['Heading1'], fontSize=24, leading=28,
                textColor=colors.HexColor("#1F4E5B"), spaceAfter=15, alignment=1
            )
            subtitle_style = ParagraphStyle(
                'DocSubTitle', parent=styles['Normal'], fontSize=10, leading=12,
                textColor=colors.HexColor("#F2A154"), spaceAfter=25, alignment=1
            )
            section_style = ParagraphStyle(
                'DocSection', parent=styles['Heading2'], fontSize=14, leading=18,
                textColor=colors.HexColor("#1F4E5B"), spaceBefore=15, spaceAfter=8
            )
            body_style = ParagraphStyle(
                'DocBody', parent=styles['Normal'], fontSize=10, leading=14,
                textColor=colors.HexColor("#333333")
            )
            header_cell_style = ParagraphStyle(
                'HC', parent=body_style, fontName='Helvetica-Bold', textColor=colors.white
            )

            # Header
            story.append(Paragraph("SYSTEM ATTENDANCE REPORT", title_style))
            story.append(Paragraph(f"Generated on: {os.environ.get('APP_DATE', '2026-06-19')}", subtitle_style))
            story.append(Spacer(1, 10))

            # General attendance details
            story.append(Paragraph("System Statistics Summary", section_style))
            summary_data = [
                [Paragraph("<b>Total Active Students:</b>", body_style), Paragraph(str(stats["total_students"]), body_style)],
                [Paragraph("<b>Average System Attendance Rate:</b>", body_style), Paragraph(f"{stats['overall_attendance']}%", body_style)],
                [Paragraph("<b>Present Logs Registered:</b>", body_style), Paragraph(str(analytics["counts"].get("Present", 0)), body_style)],
                [Paragraph("<b>Late Logs Registered:</b>", body_style), Paragraph(str(analytics["counts"].get("Late", 0)), body_style)],
                [Paragraph("<b>Absent Logs Registered:</b>", body_style), Paragraph(str(analytics["counts"].get("Absent", 0)), body_style)]
            ]
            summary_table = Table(summary_data, colWidths=[2.5*inch, 4.5*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F4F7F6")),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#D8E3E7")),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('LEFTPADDING', (0,0), (-1,-1), 12),
            ]))
            story.append(summary_table)
            story.append(Spacer(1, 20))

            # Low Attendance Alert Table
            story.append(Paragraph("Critical Warning: Low Attendance Alert (Rate < 75%)", section_style))
            
            warning_data = [[
                Paragraph("Student ID", header_cell_style),
                Paragraph("Student Name", header_cell_style),
                Paragraph("Attendance Rate", header_cell_style)
            ]]

            for bad in analytics["low_attendance"]:
                warning_data.append([
                    Paragraph(bad["student_id"], body_style),
                    Paragraph(bad["name"], body_style),
                    Paragraph(f"[red]{round(bad['rate'], 1)}%[/red]".replace('[red]', '').replace('[/red]', ''), body_style) # ReportLab doesn't support BBCode, using clean floats
                ])

            if len(warning_data) == 1:
                warning_data.append([Paragraph("No students with critical attendance rates (all >= 75%).", body_style), "", ""])

            warning_table = Table(warning_data, colWidths=[1.5*inch, 3.5*inch, 2.0*inch])
            warning_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#CD5C5C")),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#FDF3F3")]),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E5D4D4")),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ('TOPPADDING', (0,0), (-1,-1), 8),
                ('LEFTPADDING', (0,0), (-1,-1), 10),
            ]))
            story.append(warning_table)

            doc.build(story)
            activity_logger.info(f"System attendance PDF report generated at '{pdf_path}'")
            return str(pdf_path)

        except Exception as e:
            error_logger.error(f"Error compiling overall attendance PDF report: {str(e)}")
            return None

    @staticmethod
    def generate_class_performance_report() -> Optional[str]:
        """Generates a PDF document compiling statistics and course performance metrics.

        Returns:
            The absolute file path of the generated PDF, or None if errors.
        """
        course_analytics = CourseService.get_course_analytics()
        pdf_path = Config.REPORTS_DIR / "class_performance_report.pdf"

        try:
            doc = SimpleDocTemplate(
                str(pdf_path),
                pagesize=letter,
                rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54
            )
            story = []
            styles = getSampleStyleSheet()

            # Custom typography styles
            title_style = ParagraphStyle(
                'DocTitle', parent=styles['Heading1'], fontSize=24, leading=28,
                textColor=colors.HexColor("#2C061F"), spaceAfter=15, alignment=1
            )
            subtitle_style = ParagraphStyle(
                'DocSubTitle', parent=styles['Normal'], fontSize=10, leading=12,
                textColor=colors.HexColor("#F1CA89"), spaceAfter=25, alignment=1
            )
            section_style = ParagraphStyle(
                'DocSection', parent=styles['Heading2'], fontSize=14, leading=18,
                textColor=colors.HexColor("#2C061F"), spaceBefore=15, spaceAfter=8
            )
            body_style = ParagraphStyle(
                'DocBody', parent=styles['Normal'], fontSize=10, leading=14,
                textColor=colors.HexColor("#333333")
            )
            header_cell_style = ParagraphStyle(
                'HC', parent=body_style, fontName='Helvetica-Bold', textColor=colors.white
            )

            # Header
            story.append(Paragraph("ACADEMIC PERFORMANCE REPORT", title_style))
            story.append(Paragraph(f"Generated on: {os.environ.get('APP_DATE', '2026-06-19')}", subtitle_style))
            story.append(Spacer(1, 10))

            # Performance Table
            story.append(Paragraph("Course Performance Breakdown", section_style))
            
            perf_data = [[
                Paragraph("Course Code", header_cell_style),
                Paragraph("Course Name", header_cell_style),
                Paragraph("Enrolled", header_cell_style),
                Paragraph("Avg Grade", header_cell_style),
                Paragraph("Pass Rate", header_cell_style)
            ]]

            for row in course_analytics:
                perf_data.append([
                    Paragraph(row["course_code"], body_style),
                    Paragraph(row["course_name"], body_style),
                    Paragraph(str(row["enrolled_count"]), body_style),
                    Paragraph(f"{row['avg_grade']}%", body_style),
                    Paragraph(f"{row['passing_rate']}%", body_style)
                ])

            if len(perf_data) == 1:
                perf_data.append([Paragraph("No courses available in catalog.", body_style), "", "", "", ""])

            perf_table = Table(perf_data, colWidths=[1.2*inch, 2.6*inch, 1.0*inch, 1.1*inch, 1.1*inch])
            perf_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#371B58")),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F4EEFF")]),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#DCD6F7")),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ('TOPPADDING', (0,0), (-1,-1), 8),
                ('LEFTPADDING', (0,0), (-1,-1), 10),
            ]))
            story.append(perf_table)

            doc.build(story)
            activity_logger.info(f"Class performance PDF report generated at '{pdf_path}'")
            return str(pdf_path)

        except Exception as e:
            error_logger.error(f"Error compiling class performance PDF report: {str(e)}")
            return None
