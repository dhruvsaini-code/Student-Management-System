from dataclasses import dataclass
from typing import Optional

@dataclass
class Enrollment:
    """Represents a student's course enrollment and corresponding grade.

    Attributes:
        student_id: Reference to the student's ID.
        course_code: Reference to the course's code.
        grade: Numeric grade (0.0 to 100.0), optional if not yet graded.
    """
    student_id: str
    course_code: str
    grade: Optional[float] = None
