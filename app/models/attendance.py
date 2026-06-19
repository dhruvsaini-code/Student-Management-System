from dataclasses import dataclass

@dataclass
class Attendance:
    """Represents a student's daily attendance entry.

    Attributes:
        student_id: Reference to the student's ID.
        date: Calendar date of attendance log (YYYY-MM-DD).
        status: Value from ('Present', 'Absent', 'Late').
    """
    student_id: str
    date: str
    status: str
