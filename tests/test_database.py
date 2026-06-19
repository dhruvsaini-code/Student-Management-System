import unittest
import os
import sqlite3

os.environ["APP_ENV"] = "test"
os.environ["DB_NAME"] = "test_student_management_db.db"

from app.utils.config import Config
Config.DB_NAME = "test_student_management_db.db"
Config.DB_PATH = Config.BASE_DIR / Config.DB_NAME

from app.database.connection import get_db_connection, TransactionContext
from app.database.schema import init_db

class TestDatabase(unittest.TestCase):
    """Unit tests confirming connection capabilities, constraints enforcement, and rollback integrity."""

    def setUp(self) -> None:
        """Prepares a clean test database."""
        if Config.DB_PATH.exists():
            try:
                Config.DB_PATH.unlink()
            except PermissionError:
                pass
        init_db()

    def tearDown(self) -> None:
        """Cleans up the database file."""
        if Config.DB_PATH.exists():
            try:
                Config.DB_PATH.unlink()
            except PermissionError:
                pass

    def test_database_tables_exist(self) -> None:
        """Confirms that all required tables exist in the database."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row["name"] for row in cursor.fetchall()]
        conn.close()

        required_tables = ["students", "courses", "enrollments", "attendance", "admins"]
        for table in required_tables:
            self.assertIn(table, tables)

    def test_database_indexes_exist(self) -> None:
        """Confirms that search optimization indexes exist in the schema."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index';")
        indexes = [row["name"] for row in cursor.fetchall()]
        conn.close()

        required_indexes = [
            "idx_students_name", "idx_students_email", 
            "idx_enrollments_student", "idx_enrollments_course",
            "idx_attendance_student", "idx_attendance_date"
        ]
        for idx in required_indexes:
            self.assertIn(idx, indexes)

    def test_foreign_key_constraints(self) -> None:
        """Verifies that SQLite PRAGMA foreign_keys = ON is enforced."""
        conn = get_db_connection()
        # Verify pragma directly
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys;")
        fk_status = cursor.fetchone()[0]
        self.assertEqual(fk_status, 1)

        # Attempt to insert an enrollment with nonexistent student ID
        try:
            cursor.execute("INSERT INTO enrollments (student_id, course_code, grade) VALUES ('STUNONE', 'CS101', 90.0)")
            conn.commit()
            failed = False
        except sqlite3.IntegrityError:
            failed = True
        finally:
            conn.close()

        self.assertTrue(failed, "Foreign key constraint did not trigger an error on bad student_id.")

    def test_transaction_rollback_on_error(self) -> None:
        """Confirms that TransactionContext rolls back database changes when an exception is raised."""
        # 1. Verify initial count of students
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM students")
        original_count = cursor.fetchone()[0]
        conn.close()

        # 2. Execute failing transaction block
        try:
            with TransactionContext() as conn:
                conn.execute(
                    "INSERT INTO students (student_id, name, email, dob, phone) VALUES (?, ?, ?, ?, ?)",
                    ("STU999", "Failed Student", "fail@example.com", "2000-01-01", "")
                )
                # Raise dummy error to trigger rollback
                raise RuntimeError("Triggering rollback")
        except RuntimeError:
            pass

        # 3. Verify student count remains unchanged
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM students")
        after_count = cursor.fetchone()[0]
        conn.close()

        self.assertEqual(original_count, after_count, "Rollback failed: database state was modified after exception.")

if __name__ == "__main__":
    unittest.main()
