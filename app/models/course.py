from dataclasses import dataclass

@dataclass
class Course:
    """Represents a course catalog item in the system.

    Attributes:
        course_code: Unique code for the course (e.g. CS101).
        course_name: Full descriptive name of the course.
    """
    course_code: str
    course_name: str
