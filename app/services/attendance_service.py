import sqlite3
from typing import List, Dict, Any
from app.database.connection import get_db_connection, TransactionContext
from app.utils.logger import activity_logger, error_logger

class AttendanceService:
    """Manages recording and viewing of daily student attendance records."""

    @staticmethod
    def record_attendance(student_id: str, date_str: str, status: str) -> bool:
        """Records or updates a student's attendance on a specific calendar date.

        Args:
            student_id: Student ID string.
            date_str: Date (YYYY-MM-DD).
            status: Attendance state ('Present', 'Absent', 'Late').

        Returns:
            True if recording completes successfully, False otherwise.
        """
        if not student_id or not date_str or status not in ('Present', 'Absent', 'Late'):
            return False

        try:
            with TransactionContext() as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA foreign_keys = ON;")
                # Upsert query
                cursor.execute("""
                    INSERT INTO attendance (student_id, date, status) 
                    VALUES (?, ?, ?)
                    ON CONFLICT(student_id, date) 
                    DO UPDATE SET status = excluded.status
                """, (student_id.strip().upper(), date_str.strip(), status))
            activity_logger.info(f"Attendance recorded: '{student_id}' on {date_str} as '{status}'")
            return True
        except sqlite3.IntegrityError as e:
            activity_logger.warning(f"Failed to record attendance for student '{student_id}' on {date_str}: {str(e)}")
            return False
        except Exception as e:
            error_logger.error(f"Error recording attendance: {str(e)}")
            return False

    @staticmethod
    def get_student_attendance(student_id: str) -> List[Dict[str, Any]]:
        """Retrieves attendance history logs for a specific student.

        Args:
            student_id: Student ID.

        Returns:
            A list of attendance log entries sorted by date descending.
        """
        conn = get_db_connection()
        logs = []
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT date, status FROM attendance WHERE student_id = ? ORDER BY date DESC",
                (student_id.strip().upper(),)
            )
            logs = [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            error_logger.error(f"Error fetching attendance history for student '{student_id}': {str(e)}")
        finally:
            conn.close()
        return logs

    @staticmethod
    def get_attendance_by_date(date_str: str) -> List[Dict[str, Any]]:
        """Retrieves attendance logs for a specific calendar date across all students.

        Args:
            date_str: Target date (YYYY-MM-DD).

        Returns:
            A list of attendance details matching the date.
        """
        conn = get_db_connection()
        logs = []
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT a.student_id, s.name, a.status 
                FROM attendance a
                JOIN students s ON a.student_id = s.student_id
                WHERE a.date = ?
                ORDER BY s.name ASC
            """, (date_str.strip(),))
            logs = [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            error_logger.error(f"Error fetching attendance log for date '{date_str}': {str(e)}")
        finally:
            conn.close()
        return logs
