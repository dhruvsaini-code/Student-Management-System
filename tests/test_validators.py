import unittest
from app.utils.validators import validate_email, validate_date, validate_phone

class TestValidators(unittest.TestCase):
    """Unit tests for utility functions validating email, date, and phone structures."""

    def test_validate_email(self) -> None:
        """Tests email regex pattern matches."""
        # Valid cases
        self.assertTrue(validate_email("test@example.com"))
        self.assertTrue(validate_email("student.id@sub.domain.edu"))
        self.assertTrue(validate_email("abc_123@work-mail.org"))
        
        # Invalid cases
        self.assertFalse(validate_email("testexample.com"))
        self.assertFalse(validate_email("test@example"))
        self.assertFalse(validate_email("test@.com"))
        self.assertFalse(validate_email(""))

    def test_validate_date(self) -> None:
        """Tests calendar date matches YYYY-MM-DD pattern."""
        # Valid cases
        self.assertTrue(validate_date("2026-06-19"))
        self.assertTrue(validate_date("2000-01-01"))
        
        # Invalid cases
        self.assertFalse(validate_date("19-06-2026"))
        self.assertFalse(validate_date("2026/06/19"))
        self.assertFalse(validate_date("2026-02-30")) # Invalid day for February
        self.assertFalse(validate_date("not-a-date"))
        self.assertFalse(validate_date(""))

    def test_validate_phone(self) -> None:
        """Tests contact phone matches digits/dashes pattern."""
        # Valid cases
        self.assertTrue(validate_phone("555-0199"))
        self.assertTrue(validate_phone("123-456-7890"))
        self.assertTrue(validate_phone("+1234567890"))
        self.assertTrue(validate_phone("9876543210"))
        
        # Invalid cases
        self.assertFalse(validate_phone("phone123"))
        self.assertFalse(validate_phone("12")) # Too short
        self.assertFalse(validate_phone(""))

if __name__ == "__main__":
    unittest.main()
