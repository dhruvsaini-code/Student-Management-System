from dataclasses import dataclass
from typing import Optional

@dataclass
class Student:
    """Represents a student record in the system.

    Attributes:
        student_id: Unique string identifier for the student (e.g. STU001).
        name: Full name of the student.
        email: Unique email address of the student.
        dob: Date of birth (YYYY-MM-DD), optional.
        phone: Contact phone number, optional.
    """
    student_id: str
    name: str
    email: str
    dob: Optional[str] = None
    phone: Optional[str] = None
