import sqlite3
from typing import List, Dict, Optional, Any
from app.database.connection import get_db_connection, TransactionContext
from app.models.course import Course
from app.utils.logger import activity_logger, error_logger

class CourseService:
    """Handles business logic for courses, student enrollments, and course grades."""

    @staticmethod
    def add_course(course_code: str, course_name: str) -> bool:
        """Adds a course to the catalog.

        Args:
            course_code: Unique code identifying the course (e.g. CS101).
            course_name: Description/name of the course.

        Returns:
            True if catalog updated, False otherwise.
        """
        if not course_code or not course_name:
            return False

        try:
            with TransactionContext() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO courses (course_code, course_name) VALUES (?, ?)",
                    (course_code.strip().upper(), course_name.strip())
                )
            activity_logger.info(f"Course added successfully: '{course_code}'")
            return True
        except sqlite3.IntegrityError as e:
            activity_logger.warning(f"Integrity check failed when adding course '{course_code}': {str(e)}")
            return False
        except Exception as e:
            error_logger.error(f"Error adding course '{course_code}': {str(e)}")
            return False

    @staticmethod
    def get_course(course_code: str) -> Optional[Course]:
        """Retrieves a single course catalog item.

        Args:
            course_code: Unique identifier code.

        Returns:
            A Course object if found, else None.
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM courses WHERE course_code = ?", (course_code.strip().upper(),))
            row = cursor.fetchone()
            if row:
                return Course(course_code=row["course_code"], course_name=row["course_name"])
            return None
        except Exception as e:
            error_logger.error(f"Error retrieving course '{course_code}': {str(e)}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_all_courses() -> List[Course]:
        """Retrieves all registered courses.

        Returns:
            A list of Course objects.
        """
        conn = get_db_connection()
        courses = []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM courses ORDER BY course_code ASC")
            for row in cursor.fetchall():
                courses.append(Course(course_code=row["course_code"], course_name=row["course_name"]))
        except Exception as e:
            error_logger.error(f"Error loading course list: {str(e)}")
        finally:
            conn.close()
        return courses

    @staticmethod
    def delete_course(course_code: str) -> bool:
        """Deletes a course (and cascades to wipe enrollment records).

        Args:
            course_code: Course key to delete.

        Returns:
            True if deletion succeeded, False otherwise.
        """
        try:
            with TransactionContext() as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA foreign_keys = ON;")
                cursor.execute("DELETE FROM courses WHERE course_code = ?", (course_code.strip().upper(),))
                affected = cursor.rowcount
            if affected > 0:
                activity_logger.info(f"Course '{course_code}' deleted successfully.")
                return True
            else:
                activity_logger.warning(f"Delete failed: course '{course_code}' not found.")
                return False
        except Exception as e:
            error_logger.error(f"Error deleting course '{course_code}': {str(e)}")
            return False

    @staticmethod
    def enroll_student(student_id: str, course_code: str) -> bool:
        """Enrolls a student in a course.

        Args:
            student_id: Student code.
            course_code: Course code.

        Returns:
            True if enrollment completed, False if duplicate/integrity violation.
        """
        try:
            with TransactionContext() as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA foreign_keys = ON;")
                cursor.execute(
                    "INSERT INTO enrollments (student_id, course_code, grade) VALUES (?, ?, NULL)",
                    (student_id.strip().upper(), course_code.strip().upper())
                )
            activity_logger.info(f"Student '{student_id}' enrolled in course '{course_code}'.")
            return True
        except sqlite3.IntegrityError as e:
            activity_logger.warning(f"Failed to enroll '{student_id}' in '{course_code}': {str(e)}")
            return False
        except Exception as e:
            error_logger.error(f"Error registering enrollment: {str(e)}")
            return False

    @staticmethod
    def update_grade(student_id: str, course_code: str, grade: float) -> bool:
        """Updates or records a student's grade in an enrolled course.

        Args:
            student_id: Student ID.
            course_code: Course code.
            grade: Grade value (0.0 to 100.0).

        Returns:
            True if updated successfully, False if enrollment records don't exist.
        """
        if not (0.0 <= grade <= 100.0):
            return False

        try:
            with TransactionContext() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE enrollments SET grade = ? WHERE student_id = ? AND course_code = ?",
                    (grade, student_id.strip().upper(), course_code.strip().upper())
                )
                affected = cursor.rowcount
            if affected > 0:
                activity_logger.info(f"Grade updated for '{student_id}' in '{course_code}': {grade}%")
                return True
            else:
                activity_logger.warning(f"Failed to update grade: enrollment for '{student_id}' in '{course_code}' not found.")
                return False
        except Exception as e:
            error_logger.error(f"Error updating grade: {str(e)}")
            return False

    @staticmethod
    def get_student_enrollments(student_id: str) -> List[Dict[str, Any]]:
        """Lists courses a student is enrolled in, with their grades.

        Args:
            student_id: Student ID.

        Returns:
            A list of enrollment dictionary entries.
        """
        conn = get_db_connection()
        enrollments = []
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT e.course_code, c.course_name, e.grade 
                FROM enrollments e
                JOIN courses c ON e.course_code = c.course_code
                WHERE e.student_id = ?
                ORDER BY e.course_code ASC
            """, (student_id.strip().upper(),))
            enrollments = [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            error_logger.error(f"Error fetching enrollments for student '{student_id}': {str(e)}")
        finally:
            conn.close()
        return enrollments

    @staticmethod
    def get_course_enrollments(course_code: str) -> List[Dict[str, Any]]:
        """Lists students enrolled in a specific course.

        Args:
            course_code: Course code key.

        Returns:
            A list of dictionary records mapping students and grades.
        """
        conn = get_db_connection()
        students = []
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT e.student_id, s.name, e.grade 
                FROM enrollments e
                JOIN students s ON e.student_id = s.student_id
                WHERE e.course_code = ?
                ORDER BY s.name ASC
            """, (course_code.strip().upper(),))
            students = [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            error_logger.error(f"Error fetching students in course '{course_code}': {str(e)}")
        finally:
            conn.close()
        return students

    @staticmethod
    def get_course_analytics() -> List[Dict[str, Any]]:
        """Aggregates course performance and size statistics.

        Returns:
            A list of metrics per course, including enrolled count and average grades.
        """
        conn = get_db_connection()
        analytics = []
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.course_code, c.course_name,
                       COUNT(e.student_id) as enrolled_count,
                       AVG(e.grade) as avg_grade,
                       COUNT(CASE WHEN e.grade >= 60.0 THEN 1 END) as passing_count
                FROM courses c
                LEFT JOIN enrollments e ON c.course_code = e.course_code
                GROUP BY c.course_code
                ORDER BY c.course_code ASC
            """)
            rows = cursor.fetchall()
            for row in rows:
                rec = dict(row)
                rec["avg_grade"] = round(rec["avg_grade"], 2) if rec["avg_grade"] is not None else 0.0
                rec["passing_rate"] = round(
                    (rec["passing_count"] / rec["enrolled_count"] * 100.0), 2
                ) if rec["enrolled_count"] > 0 else 100.0
                analytics.append(rec)
        except Exception as e:
            error_logger.error(f"Error generating course analytics: {str(e)}")
        finally:
            conn.close()
        return analytics
