import csv
import os
import sqlite3
from typing import List, Dict, Optional, Tuple, Any
from app.database.connection import get_db_connection, TransactionContext
from app.models.student import Student
from app.utils.logger import activity_logger, error_logger
from app.utils.validators import validate_email, validate_date

class StudentService:
    """Provides service layer for student database operations, CSV reports, and performance analytics."""

    @staticmethod
    def add_student(student_id: str, name: str, email: str, dob: Optional[str] = None, phone: Optional[str] = None) -> bool:
        """Adds a student record to the database.

        Args:
            student_id: Unique identifier for the student.
            name: Full name.
            email: Unique email address.
            dob: Optional birthdate YYYY-MM-DD.
            phone: Optional phone contact.

        Returns:
            True if student added successfully, False otherwise.
        """
        if not student_id or not name or not email:
            return False

        try:
            with TransactionContext() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO students (student_id, name, email, dob, phone) VALUES (?, ?, ?, ?, ?)",
                    (student_id.strip().upper(), name.strip(), email.strip(), dob.strip() if dob else None, phone.strip() if phone else None)
                )
            activity_logger.info(f"Student added successfully: '{student_id}'")
            return True
        except sqlite3.IntegrityError as e:
            activity_logger.warning(f"Integrity check failed when adding student '{student_id}': {str(e)}")
            return False
        except Exception as e:
            error_logger.error(f"Error adding student '{student_id}': {str(e)}")
            return False

    @staticmethod
    def get_student(student_id: str) -> Optional[Student]:
        """Retrieves a single student by identifier.

        Args:
            student_id: The ID of the student.

        Returns:
            A Student instance if found, else None.
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id.strip().upper(),))
            row = cursor.fetchone()
            if row:
                return Student(
                    student_id=row["student_id"],
                    name=row["name"],
                    email=row["email"],
                    dob=row["dob"],
                    phone=row["phone"]
                )
            return None
        except Exception as e:
            error_logger.error(f"Error retrieving student '{student_id}': {str(e)}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_all_students() -> List[Student]:
        """Retrieves all student records from the database.

        Returns:
            A list of Student instances.
        """
        conn = get_db_connection()
        students = []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students ORDER BY name ASC")
            rows = cursor.fetchall()
            for row in rows:
                students.append(Student(
                    student_id=row["student_id"],
                    name=row["name"],
                    email=row["email"],
                    dob=row["dob"],
                    phone=row["phone"]
                ))
        except Exception as e:
            error_logger.error(f"Error retrieving all students: {str(e)}")
        finally:
            conn.close()
        return students

    @staticmethod
    def update_student(student_id: str, name: str, email: str, dob: Optional[str] = None, phone: Optional[str] = None) -> bool:
        """Updates an existing student record.

        Args:
            student_id: The ID of the student to modify.
            name: New name value.
            email: New email value.
            dob: Optional birthdate.
            phone: Optional phone.

        Returns:
            True if records updated successfully, False if failure or not found.
        """
        try:
            with TransactionContext() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE students SET name = ?, email = ?, dob = ?, phone = ? WHERE student_id = ?",
                    (name.strip(), email.strip(), dob.strip() if dob else None, phone.strip() if phone else None, student_id.strip().upper())
                )
                affected = cursor.rowcount
            if affected > 0:
                activity_logger.info(f"Student '{student_id}' updated successfully.")
                return True
            else:
                activity_logger.warning(f"Update failed: student ID '{student_id}' not found.")
                return False
        except sqlite3.IntegrityError as e:
            activity_logger.warning(f"Integrity constraint violation updating student '{student_id}': {str(e)}")
            return False
        except Exception as e:
            error_logger.error(f"Error updating student '{student_id}': {str(e)}")
            return False

    @staticmethod
    def delete_student(student_id: str) -> bool:
        """Deletes a student record (and cascades deletion to grades/attendance).

        Args:
            student_id: The ID of the student to delete.

        Returns:
            True if deletion succeeded, False otherwise.
        """
        try:
            with TransactionContext() as conn:
                cursor = conn.cursor()
                # Enforce foreign key constraints explicitly
                cursor.execute("PRAGMA foreign_keys = ON;")
                cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id.strip().upper(),))
                affected = cursor.rowcount
            if affected > 0:
                activity_logger.info(f"Student '{student_id}' and all associations deleted.")
                return True
            else:
                activity_logger.warning(f"Delete failed: Student '{student_id}' not found.")
                return False
        except Exception as e:
            error_logger.error(f"Error deleting student '{student_id}': {str(e)}")
            return False

    @staticmethod
    def get_student_report_card(student_id: str) -> Optional[Dict[str, Any]]:
        """Calculates statistics and retrieves reports for a single student.

        Includes course lists, grades, and attendance metrics.

        Args:
            student_id: The ID of the student.

        Returns:
            A report dictionary if student exists, else None.
        """
        student = StudentService.get_student(student_id)
        if not student:
            return None

        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Fetch enrollments
            cursor.execute("""
                SELECT e.course_code, c.course_name, e.grade 
                FROM enrollments e
                JOIN courses c ON e.course_code = c.course_code
                WHERE e.student_id = ?
            """, (student.student_id,))
            enrollment_rows = cursor.fetchall()
            enrollments = [dict(row) for row in enrollment_rows]
            
            # Fetch attendance
            cursor.execute("""
                SELECT date, status FROM attendance 
                WHERE student_id = ? 
                ORDER BY date DESC
            """, (student.student_id,))
            attendance_rows = cursor.fetchall()
            attendance = [dict(row) for row in attendance_rows]
            
            # Calculations
            grades = [r["grade"] for r in enrollments if r["grade"] is not None]
            avg_grade = sum(grades) / len(grades) if grades else 0.0
            
            total_attendance = len(attendance)
            present_or_late = sum(1 for a in attendance if a["status"] in ("Present", "Late"))
            attendance_rate = (present_or_late / total_attendance * 100.0) if total_attendance > 0 else 100.0

            return {
                "student": student,
                "enrollments": enrollments,
                "attendance": attendance,
                "average_grade": round(avg_grade, 2),
                "attendance_rate": round(attendance_rate, 2),
                "total_courses": len(enrollments)
            }
        except Exception as e:
            error_logger.error(f"Error compiling report card for '{student_id}': {str(e)}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_system_stats() -> Dict[str, Any]:
        """Gathers system-wide dashboard statistics.

        Returns:
            A dictionary containing counts and averages.
        """
        conn = get_db_connection()
        stats = {
            "total_students": 0,
            "total_courses": 0,
            "average_grade": 0.0,
            "overall_attendance": 100.0
        }
        try:
            cursor = conn.cursor()
            
            # Totals
            cursor.execute("SELECT COUNT(*) FROM students")
            stats["total_students"] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM courses")
            stats["total_courses"] = cursor.fetchone()[0]
            
            # Grades
            cursor.execute("SELECT AVG(grade) FROM enrollments WHERE grade IS NOT NULL")
            avg_g = cursor.fetchone()[0]
            stats["average_grade"] = round(avg_g, 2) if avg_g is not None else 0.0

            # Attendance
            cursor.execute("SELECT status, COUNT(*) as cnt FROM attendance GROUP BY status")
            rows = cursor.fetchall()
            attendance_counts = {r["status"]: r["cnt"] for r in rows}
            total_days = sum(attendance_counts.values())
            present_or_late = attendance_counts.get("Present", 0) + attendance_counts.get("Late", 0)
            
            stats["overall_attendance"] = round((present_or_late / total_days * 100.0), 2) if total_days > 0 else 100.0
        except Exception as e:
            error_logger.error(f"Error loading system metrics: {str(e)}")
        finally:
            conn.close()
        return stats

    @staticmethod
    def get_top_performing_students(limit: int = 5) -> List[Dict[str, Any]]:
        """Identifies top performing students by average grade.

        Args:
            limit: Maximum records to return.

        Returns:
            A list of dictionary records with average grades.
        """
        conn = get_db_connection()
        results = []
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.student_id, s.name, AVG(e.grade) as avg_grade
                FROM enrollments e
                JOIN students s ON e.student_id = s.student_id
                WHERE e.grade IS NOT NULL
                GROUP BY e.student_id
                ORDER BY avg_grade DESC
                LIMIT ?
            """, (limit,))
            results = [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            error_logger.error(f"Error fetching top performing students: {str(e)}")
        finally:
            conn.close()
        return results

    @staticmethod
    def get_lowest_performing_students(limit: int = 5) -> List[Dict[str, Any]]:
        """Identifies lowest performing students by average grade.

        Args:
            limit: Maximum records to return.

        Returns:
            A list of dictionary records with average grades.
        """
        conn = get_db_connection()
        results = []
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.student_id, s.name, AVG(e.grade) as avg_grade
                FROM enrollments e
                JOIN students s ON e.student_id = s.student_id
                WHERE e.grade IS NOT NULL
                GROUP BY e.student_id
                ORDER BY avg_grade ASC
                LIMIT ?
            """, (limit,))
            results = [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            error_logger.error(f"Error fetching lowest performing students: {str(e)}")
        finally:
            conn.close()
        return results

    @staticmethod
    def get_attendance_analytics() -> Dict[str, Any]:
        """Aggregates attendance statistics by student.

        Returns:
            A dictionary containing low attendance lists and status distributions.
        """
        conn = get_db_connection()
        analytics = {"low_attendance": [], "counts": {"Present": 0, "Absent": 0, "Late": 0}}
        try:
            cursor = conn.cursor()
            
            # Load distribution
            cursor.execute("SELECT status, COUNT(*) FROM attendance GROUP BY status")
            for row in cursor.fetchall():
                analytics["counts"][row[0]] = row[1]
                
            # Find low attendance (<75% attendance)
            cursor.execute("""
                SELECT s.student_id, s.name,
                       COUNT(CASE WHEN a.status IN ('Present', 'Late') THEN 1 END) * 100.0 / COUNT(a.student_id) as rate
                FROM attendance a
                JOIN students s ON a.student_id = s.student_id
                GROUP BY a.student_id
                HAVING rate < 75.0
                ORDER BY rate ASC
            """)
            analytics["low_attendance"] = [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            error_logger.error(f"Error compiling attendance analytics: {str(e)}")
        finally:
            conn.close()
        return analytics

    @staticmethod
    def get_gpa_ranking_table() -> List[Dict[str, Any]]:
        """Generates a complete list of students ranked by average grade/GPA.

        Returns:
            A list of dictionary records with ranking indices.
        """
        conn = get_db_connection()
        rankings = []
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.student_id, s.name, AVG(e.grade) as avg_grade, COUNT(e.course_code) as courses_count
                FROM students s
                LEFT JOIN enrollments e ON s.student_id = e.student_id
                GROUP BY s.student_id
                ORDER BY avg_grade DESC, s.name ASC
            """)
            rows = cursor.fetchall()
            for idx, row in enumerate(rows, 1):
                rec = dict(row)
                rec["rank"] = idx
                rec["avg_grade"] = round(rec["avg_grade"], 2) if rec["avg_grade"] is not None else 0.0
                rankings.append(rec)
        except Exception as e:
            error_logger.error(f"Error compiling GPA ranking table: {str(e)}")
        finally:
            conn.close()
        return rankings

    @staticmethod
    def export_students_to_csv(filepath: str) -> bool:
        """Exports all student profiles and aggregate statistics to a CSV.

        Args:
            filepath: Target output file location.

        Returns:
            True if export succeeded, False otherwise.
        """
        students = StudentService.get_all_students()
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Student ID', 'Name', 'Email', 'DOB', 'Phone',
                    'Average Grade', 'Attendance Rate'
                ])
                
                for s in students:
                    card = StudentService.get_student_report_card(s.student_id)
                    writer.writerow([
                        s.student_id,
                        s.name,
                        s.email,
                        s.dob or '',
                        s.phone or '',
                        card['average_grade'] if card else 0.0,
                        f"{card['attendance_rate']}%" if card else "100.0%"
                    ])
            activity_logger.info(f"Successfully exported {len(students)} student records to '{filepath}'.")
            return True
        except IOError as e:
            error_logger.error(f"File IO Error exporting students to '{filepath}': {str(e)}")
            return False

    @staticmethod
    def import_students_from_csv(filepath: str) -> Tuple[bool, Dict[str, Any]]:
        """Imports student records from a CSV file.

        Header expectations: 'Student ID', 'Name', 'Email', 'DOB' (optional), 'Phone' (optional)

        Args:
            filepath: Path to input CSV.

        Returns:
            A tuple of (success_status, details_dictionary).
        """
        imported_count = 0
        errors = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                if not reader.fieldnames:
                    return False, {"errors": ["Empty CSV file."]}
                
                # Normalize column headers
                headers = [h.strip().lower() for h in reader.fieldnames]
                required = ['student id', 'name', 'email']
                if not all(r in headers for r in required):
                    return False, {
                        "errors": ["CSV headers must include 'Student ID', 'Name', and 'Email'."]
                    }
                
                # Map headers back to actual case-sensitive names in the file
                header_map = {h.strip().lower(): h for h in reader.fieldnames}
                
                for row_idx, row in enumerate(reader, start=2):
                    student_id = row[header_map['student id']].strip()
                    name = row[header_map['name']].strip()
                    email = row[header_map['email']].strip()
                    
                    dob = row.get(header_map.get('dob', ''), '').strip()
                    phone = row.get(header_map.get('phone', ''), '').strip()
                    
                    # Validations
                    if not student_id or not name or not email:
                        errors.append(f"Row {row_idx}: Missing required field (ID, Name, or Email).")
                        continue
                    
                    if not validate_email(email):
                        errors.append(f"Row {row_idx}: Invalid email format for email '{email}'.")
                        continue
                    
                    if dob and not validate_date(dob):
                        errors.append(f"Row {row_idx}: Invalid DOB format ({dob}), expected YYYY-MM-DD.")
                        continue
                    
                    # Insert
                    success = StudentService.add_student(
                        student_id=student_id,
                        name=name,
                        email=email,
                        dob=dob if dob else None,
                        phone=phone if phone else None
                    )
                    
                    if success:
                        imported_count += 1
                    else:
                        errors.append(f"Row {row_idx}: Student ID '{student_id}' or email '{email}' already exists or DB error.")
            
            activity_logger.info(f"CSV import completed. Imported: {imported_count}. Errors/Warnings: {len(errors)}.")
            return True, {"imported": imported_count, "errors": errors}
            
        except FileNotFoundError:
            activity_logger.warning(f"CSV import file not found at '{filepath}'.")
            return False, {"errors": [f"File '{filepath}' not found."]}
        except Exception as e:
            error_logger.error(f"Unexpected error importing students CSV from '{filepath}': {str(e)}")
            return False, {"errors": [f"Error reading CSV: {str(e)}"]}
