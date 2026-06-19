from typing import List, Tuple
from difflib import SequenceMatcher
from app.models.student import Student
from app.services.student_service import StudentService
from app.database.connection import get_db_connection
from app.utils.logger import error_logger

class SearchService:
    """Contains logic for querying students by ID, Name, Email, and fuzzy searching."""

    @staticmethod
    def search_by_id(student_id: str) -> List[Student]:
        """Finds students whose ID contains the query string.

        Args:
            student_id: The ID substring to search for.

        Returns:
            A list of matching Student records.
        """
        conn = get_db_connection()
        matches = []
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM students WHERE student_id LIKE ? ORDER BY student_id ASC",
                (f"%{student_id.strip().upper()}%",)
            )
            for row in cursor.fetchall():
                matches.append(Student(
                    student_id=row["student_id"],
                    name=row["name"],
                    email=row["email"],
                    dob=row["dob"],
                    phone=row["phone"]
                ))
        except Exception as e:
            error_logger.error(f"Error searching students by ID '{student_id}': {str(e)}")
        finally:
            conn.close()
        return matches

    @staticmethod
    def search_by_name(name_query: str) -> List[Student]:
        """Finds students whose name contains the query string (case-insensitive).

        Args:
            name_query: The name substring to search for.

        Returns:
            A list of matching Student records.
        """
        conn = get_db_connection()
        matches = []
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM students WHERE name LIKE ? ORDER BY name ASC",
                (f"%{name_query.strip()}%",)
            )
            for row in cursor.fetchall():
                matches.append(Student(
                    student_id=row["student_id"],
                    name=row["name"],
                    email=row["email"],
                    dob=row["dob"],
                    phone=row["phone"]
                ))
        except Exception as e:
            error_logger.error(f"Error searching students by name '{name_query}': {str(e)}")
        finally:
            conn.close()
        return matches

    @staticmethod
    def search_by_email(email_query: str) -> List[Student]:
        """Finds students whose email contains the query string (case-insensitive).

        Args:
            email_query: The email substring to search for.

        Returns:
            A list of matching Student records.
        """
        conn = get_db_connection()
        matches = []
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM students WHERE email LIKE ? ORDER BY email ASC",
                (f"%{email_query.strip()}%",)
            )
            for row in cursor.fetchall():
                matches.append(Student(
                    student_id=row["student_id"],
                    name=row["name"],
                    email=row["email"],
                    dob=row["dob"],
                    phone=row["phone"]
                ))
        except Exception as e:
            error_logger.error(f"Error searching students by email '{email_query}': {str(e)}")
        finally:
            conn.close()
        return matches

    @staticmethod
    def search_fuzzy(query: str, threshold: float = 0.35) -> List[Tuple[Student, float]]:
        """Performs fuzzy matching on students based on ID, Name, and Email.

        Uses built-in SequenceMatcher to compute match ratios and ranks them.

        Args:
            query: The search query string.
            threshold: Minimum score ratio (0.0 to 1.0) to qualify as a match.

        Returns:
            A sorted list of tuples (Student, match_ratio_score) descending.
        """
        query = query.strip().lower()
        if not query:
            return []

        all_students = StudentService.get_all_students()
        results = []

        for student in all_students:
            # Calculate match ratios for various fields
            id_ratio = SequenceMatcher(None, query, student.student_id.lower()).ratio()
            name_ratio = SequenceMatcher(None, query, student.name.lower()).ratio()
            email_ratio = SequenceMatcher(None, query, student.email.lower()).ratio()

            # Find matching substrings within fields for extra weight
            substring_matches = False
            if (query in student.student_id.lower() or 
                query in student.name.lower() or 
                query in student.email.lower()):
                substring_matches = True

            best_ratio = max(id_ratio, name_ratio, email_ratio)
            
            # Boost the ratio if there is an exact substring match
            if substring_matches:
                best_ratio = max(best_ratio, 0.6)

            if best_ratio >= threshold:
                results.append((student, round(best_ratio * 100, 1)))

        # Sort by match score descending
        results.sort(key=lambda x: x[1], reverse=True)
        return results
