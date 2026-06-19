import re
from datetime import datetime

def validate_email(email: str) -> bool:
    """Validates email format using regular expressions.

    Args:
        email: The email string to validate.

    Returns:
        True if the email format is valid, False otherwise.
    """
    if not email:
        return False
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email.strip()))

def validate_date(date_str: str) -> bool:
    """Validates date format to confirm it adheres to YYYY-MM-DD.

    Args:
        date_str: The date string to validate.

    Returns:
        True if the date format is valid and matches a real calendar date, False otherwise.
    """
    if not date_str:
        return False
    try:
        datetime.strptime(date_str.strip(), "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_phone(phone_str: str) -> bool:
    """Validates a phone number pattern.

    Accepts international patterns, digits, spaces, and hyphens (e.g. 555-0199, 123-456-7890, +1 234 567 8900).

    Args:
        phone_str: The phone number string to validate.

    Returns:
        True if the phone number pattern is valid, False otherwise.
    """
    if not phone_str:
        # If optional, validation might pass elsewhere; this checks format if provided
        return False
    # Matches optional +, followed by digits, spaces, or dashes
    pattern = r"^\+?[0-9\s\-]{7,15}$"
    return bool(re.match(pattern, phone_str.strip()))
