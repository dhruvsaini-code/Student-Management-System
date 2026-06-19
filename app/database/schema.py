import sqlite3
import datetime
import bcrypt
from app.database.connection import get_db_connection, TransactionContext
from app.utils.logger import activity_logger, error_logger

def init_db() -> None:
    """Initializes the database schema and structures.

    Creates tables, indexes, and seeds the base default records (like courses,
    students, and admin accounts) if the database is empty.
    """
    try:
        with TransactionContext() as conn:
            # Enable Foreign Key constraints explicitly in this session
            conn.execute("PRAGMA foreign_keys = ON;")
            
            # Create students table
            conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                dob TEXT,
                phone TEXT,
                CONSTRAINT chk_email CHECK (email LIKE '%_@_%._%')
            );
            """)

            # Create courses table
            conn.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                course_code TEXT PRIMARY KEY,
                course_name TEXT NOT NULL
            );
            """)

            # Create enrollments table
            conn.execute("""
            CREATE TABLE IF NOT EXISTS enrollments (
                student_id TEXT,
                course_code TEXT,
                grade REAL CHECK (grade IS NULL OR (grade >= 0.0 AND grade <= 100.0)),
                PRIMARY KEY (student_id, course_code),
                FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
                FOREIGN KEY (course_code) REFERENCES courses(course_code) ON DELETE CASCADE
            );
            """)

            # Create attendance table
            conn.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                student_id TEXT,
                date TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('Present', 'Absent', 'Late')),
                PRIMARY KEY (student_id, date),
                FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
            );
            """)

            # Create admin table
            conn.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """)

            # Indexes for search optimization
            conn.execute("CREATE INDEX IF NOT EXISTS idx_students_name ON students (name);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_students_email ON students (email);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_enrollments_student ON enrollments (student_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_enrollments_course ON enrollments (course_code);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_attendance_student ON attendance (student_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance (date);")

            activity_logger.info("Database schema initialized/verified successfully.")

        # Seed initial demo data
        seed_demo_data()

    except sqlite3.Error as e:
        error_logger.critical(f"Failed to initialize database: {str(e)}")
        raise e

def seed_demo_data() -> None:
    """Seeds sample student, course, enrollment, attendance, and admin credentials.

    Ensures that default admin login is created.
    """
    try:
        with TransactionContext() as conn:
            # 1. Seed Default Admin Account if none exists
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM admins")
            admin_count = cursor.fetchone()[0]
            if admin_count == 0:
                raw_password = "admin123"
                salt = bcrypt.gensalt()
                hashed = bcrypt.hashpw(raw_password.encode('utf-8'), salt).decode('utf-8')
                now_str = datetime.datetime.now().isoformat()
                cursor.execute(
                    "INSERT INTO admins (username, password_hash, created_at) VALUES (?, ?, ?)",
                    ("admin", hashed, now_str)
                )
                activity_logger.info("Default admin account created (username: admin, password: admin123).")

            # 2. Seed Default Courses
            cursor.execute("SELECT COUNT(*) FROM courses")
            if cursor.fetchone()[0] == 0:
                courses_to_seed = [
                    ("CS101", "Introduction to Computer Science"),
                    ("MATH201", "Calculus II"),
                    ("CS202", "Data Structures & Algorithms"),
                    ("PHY101", "Physics for Engineers"),
                    ("CHEM101", "General Chemistry")
                ]
                cursor.executemany(
                    "INSERT INTO courses (course_code, course_name) VALUES (?, ?)",
                    courses_to_seed
                )
                activity_logger.info("Sample courses seeded.")

            # 3. Seed Default Students
            cursor.execute("SELECT COUNT(*) FROM students")
            if cursor.fetchone()[0] == 0:
                students_to_seed = [
                    ("STU001", "John Doe", "john.doe@example.com", "2001-04-12", "555-0199"),
                    ("STU002", "Jane Smith", "jane.smith@example.com", "2002-11-23", "555-0144"),
                    ("STU003", "Alex Carter", "alex.c@example.com", "2001-08-30", "555-0177"),
                    ("STU004", "Emily Davis", "emily.davis@example.com", "2002-05-14", "555-0122"),
                    ("STU005", "Michael Brown", "michael.b@example.com", "2000-12-05", "555-0166")
                ]
                cursor.executemany(
                    "INSERT INTO students (student_id, name, email, dob, phone) VALUES (?, ?, ?, ?, ?)",
                    students_to_seed
                )
                activity_logger.info("Sample students seeded.")

                # Seed enrollments & grades
                enrollments_to_seed = [
                    ("STU001", "CS101", 88.5),
                    ("STU001", "MATH201", 92.0),
                    ("STU001", "CS202", 95.0),
                    ("STU002", "CS101", 95.0),
                    ("STU002", "MATH201", 85.5),
                    ("STU003", "MATH201", 78.0),
                    ("STU003", "CS202", 82.5),
                    ("STU004", "PHY101", 91.0),
                    ("STU004", "CHEM101", 89.0),
                    ("STU005", "CS101", 62.0),
                    ("STU005", "PHY101", 58.5)
                ]
                cursor.executemany(
                    "INSERT INTO enrollments (student_id, course_code, grade) VALUES (?, ?, ?)",
                    enrollments_to_seed
                )

                # Seed attendance
                # John Doe and Jane Smith have perfect attendance, Alex has mixed attendance
                dates = ["2026-06-15", "2026-06-16", "2026-06-17", "2026-06-18", "2026-06-19"]
                attendance_to_seed = []
                for d in dates:
                    attendance_to_seed.append(("STU001", d, "Present"))
                    attendance_to_seed.append(("STU002", d, "Present"))
                    attendance_to_seed.append(("STU004", d, "Present"))

                # Alex Carter's attendance
                attendance_to_seed.extend([
                    ("STU003", "2026-06-15", "Present"),
                    ("STU003", "2026-06-16", "Absent"),
                    ("STU003", "2026-06-17", "Late"),
                    ("STU003", "2026-06-18", "Present"),
                    ("STU003", "2026-06-19", "Present"),
                ])

                # Michael Brown's attendance
                attendance_to_seed.extend([
                    ("STU005", "2026-06-15", "Absent"),
                    ("STU005", "2026-06-16", "Absent"),
                    ("STU005", "2026-06-17", "Present"),
                    ("STU005", "2026-06-18", "Late"),
                    ("STU005", "2026-06-19", "Present"),
                ])

                cursor.executemany(
                    "INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)",
                    attendance_to_seed
                )
                activity_logger.info("Sample enrollments and attendance records seeded.")

    except sqlite3.Error as e:
        error_logger.error(f"Error seeding database: {str(e)}")
        # Rollback is automatically handled by the TransactionContext exit handler
