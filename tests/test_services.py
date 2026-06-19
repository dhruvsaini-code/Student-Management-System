import unittest
import os
import shutil
from pathlib import Path

os.environ["APP_ENV"] = "test"
os.environ["DB_NAME"] = "test_student_management_services.db"

from app.utils.config import Config
Config.DB_NAME = "test_student_management_services.db"
Config.DB_PATH = Config.BASE_DIR / Config.DB_NAME

from app.database.schema import init_db
from app.services.student_service import StudentService
from app.services.course_service import CourseService
from app.services.attendance_service import AttendanceService
from app.services.search_service import SearchService
from app.services.backup_service import BackupService
from app.services.report_service import ReportService
from app.services.visualization_service import VisualizationService

class TestServices(unittest.TestCase):
    """Integrative suite validating CRUD services, fuzzy search, backup restorations, report generators, and plots."""

    def setUp(self) -> None:
        """Prepares database and system environments."""
        if Config.DB_PATH.exists():
            try:
                Config.DB_PATH.unlink()
            except PermissionError:
                pass
        init_db()

    def tearDown(self) -> None:
        """Cleans up the database file and charts/reports created during testing."""
        if Config.DB_PATH.exists():
            try:
                Config.DB_PATH.unlink()
            except PermissionError:
                pass
        
        # Clean up test backups, reports, and charts if generated
        for folder in [Config.BACKUPS_DIR, Config.REPORTS_DIR, Config.CHARTS_DIR]:
            if folder.exists():
                for f in folder.glob("*"):
                    if "test" in f.name or "report_card_STU" in f.name or f.suffix in [".png", ".pdf", ".csv"]:
                        try:
                            f.unlink()
                        except PermissionError:
                            pass

    def test_student_crud(self) -> None:
        """Tests student insertion, lookup, editing, listing, and deletion."""
        # Create
        success = StudentService.add_student("STU999", "Alice Wonder", "alice.w@example.com", "2000-05-20", "555-9876")
        self.assertTrue(success)

        # Retrieve
        student = StudentService.get_student("STU999")
        self.assertIsNotNone(student)
        self.assertEqual(student.name, "Alice Wonder")
        self.assertEqual(student.email, "alice.w@example.com")

        # Update
        update_success = StudentService.update_student("STU999", "Alice Marvel", "alice.w@example.com", "2000-05-20", "555-1111")
        self.assertTrue(update_success)
        student_updated = StudentService.get_student("STU999")
        self.assertEqual(student_updated.name, "Alice Marvel")
        self.assertEqual(student_updated.phone, "555-1111")

        # List
        all_students = StudentService.get_all_students()
        self.assertTrue(any(s.student_id == "STU999" for s in all_students))

        # Delete
        delete_success = StudentService.delete_student("STU999")
        self.assertTrue(delete_success)
        self.assertIsNone(StudentService.get_student("STU999"))

    def test_course_and_grading_flow(self) -> None:
        """Tests course additions, enrollments, and academic grades update loops."""
        # Add course
        success = CourseService.add_course("CS303", "Systems Programming")
        self.assertTrue(success)
        
        course = CourseService.get_course("CS303")
        self.assertIsNotNone(course)
        self.assertEqual(course.course_name, "Systems Programming")

        # Enroll student
        enroll_success = CourseService.enroll_student("STU001", "CS303")
        self.assertTrue(enroll_success)

        # Grade student
        grade_success = CourseService.update_grade("STU001", "CS303", 94.5)
        self.assertTrue(grade_success)

        # Retrieve grade checks
        enrollments = CourseService.get_student_enrollments("STU001")
        target = next((e for e in enrollments if e["course_code"] == "CS303"), None)
        self.assertIsNotNone(target)
        self.assertEqual(target["grade"], 94.5)

    def test_attendance_service(self) -> None:
        """Tests logging and historical checks for student attendance."""
        success = AttendanceService.record_attendance("STU001", "2026-06-20", "Late")
        self.assertTrue(success)

        logs = AttendanceService.get_student_attendance("STU001")
        self.assertTrue(any(l["date"] == "2026-06-20" and l["status"] == "Late" for l in logs))

        date_logs = AttendanceService.get_attendance_by_date("2026-06-20")
        self.assertTrue(any(d["student_id"] == "STU001" and d["status"] == "Late" for d in date_logs))

    def test_search_engine_and_fuzzy_matching(self) -> None:
        """Tests search service capability including fuzzy matching search."""
        # Exact field queries
        matches_id = SearchService.search_by_id("STU001")
        self.assertTrue(any(s.name == "John Doe" for s in matches_id))

        matches_name = SearchService.search_by_name("Jane")
        self.assertTrue(any(s.student_id == "STU002" for s in matches_name))

        matches_email = SearchService.search_by_email("alex.c")
        self.assertTrue(any(s.name == "Alex Carter" for s in matches_email))

        # Fuzzy Search verification
        fuzzy_matches = SearchService.search_fuzzy("jon doe")
        self.assertTrue(len(fuzzy_matches) > 0)
        self.assertEqual(fuzzy_matches[0][0].student_id, "STU001") # Best match should be John Doe

    def test_backup_and_restore(self) -> None:
        """Tests copying DB file to backups folder and database restoration from copy."""
        # 1. Create Backup
        success, backup_file = BackupService.create_backup()
        self.assertTrue(success)
        
        backup_path = Config.BACKUPS_DIR / backup_file
        self.assertTrue(backup_path.exists())

        # 2. Add temporary student records to differentiate DB state
        StudentService.add_student("STUTEMP", "Temp Student", "temp@example.com", "", "")
        self.assertIsNotNone(StudentService.get_student("STUTEMP"))

        # 3. Restore backup file
        restore_success, restore_msg = BackupService.restore_backup(backup_file)
        self.assertTrue(restore_success)

        # 4. Check database state reverted (STUTEMP should no longer exist)
        self.assertIsNone(StudentService.get_student("STUTEMP"))

        # Clean up backup file
        backup_path.unlink()

    def test_pdf_report_generators(self) -> None:
        """Tests report service generating PDF report cards, performance reports, and attendance reviews."""
        # Student Report Card PDF
        rc_path = ReportService.generate_student_report_card("STU001")
        self.assertIsNotNone(rc_path)
        self.assertTrue(Path(rc_path).exists())

        # Attendance PDF report
        att_path = ReportService.generate_attendance_report()
        self.assertIsNotNone(att_path)
        self.assertTrue(Path(att_path).exists())

        # Performance PDF report
        perf_path = ReportService.generate_class_performance_report()
        self.assertIsNotNone(perf_path)
        self.assertTrue(Path(perf_path).exists())

    def test_matplotlib_visualization_charts(self) -> None:
        """Tests visualization service drawing grade distributions, course enrollments, and attendance counts."""
        # Grade Distribution chart
        s1, p1 = VisualizationService.generate_grade_distribution()
        self.assertTrue(s1)
        self.assertTrue(Path(p1).exists())

        # Attendance Graph chart
        s2, p2 = VisualizationService.generate_attendance_graph()
        self.assertTrue(s2)
        self.assertTrue(Path(p2).exists())

        # Course Enrollments chart
        s3, p3 = VisualizationService.generate_enrollment_graph()
        self.assertTrue(s3)
        self.assertTrue(Path(p3).exists())

if __name__ == "__main__":
    unittest.main()
