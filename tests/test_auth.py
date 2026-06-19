import unittest
import os
import shutil
from pathlib import Path

# Set environment variable before importing config
os.environ["APP_ENV"] = "test"
os.environ["DB_NAME"] = "test_student_management_auth.db"

from app.utils.config import Config
# Manually override to guarantee test database isolate
Config.DB_NAME = "test_student_management_auth.db"
Config.DB_PATH = Config.BASE_DIR / Config.DB_NAME

from app.database.schema import init_db
from app.services.auth_service import AuthService

class TestAuthService(unittest.TestCase):
    """Unit tests verifying admin user registration, login authentication, and sessions."""

    @classmethod
    def setUpClass(cls) -> None:
        """Bootstraps database schema configurations."""
        Config.initialize_directories()

    def setUp(self) -> None:
        """Wipes database file and recreates clean tables."""
        if Config.DB_PATH.exists():
            try:
                Config.DB_PATH.unlink()
            except PermissionError:
                pass
        init_db()
        AuthService.logout()

    def tearDown(self) -> None:
        """Cleans up database files after tests."""
        AuthService.logout()
        if Config.DB_PATH.exists():
            try:
                Config.DB_PATH.unlink()
            except PermissionError:
                pass

    def test_default_admin_seeded(self) -> None:
        """Verifies default admin credentials 'admin'/'admin123' are active."""
        self.assertTrue(AuthService.login("admin", "admin123"))
        self.assertTrue(AuthService.is_authenticated())
        self.assertEqual(AuthService.get_current_user(), "admin")

    def test_login_invalid_credentials(self) -> None:
        """Verifies incorrect passwords or usernames fail validation."""
        self.assertFalse(AuthService.login("admin", "wrongpassword"))
        self.assertFalse(AuthService.is_authenticated())
        self.assertFalse(AuthService.login("nonexistent", "somepassword"))

    def test_admin_registration(self) -> None:
        """Verifies registering new administrators and using their credentials."""
        # Register new admin
        success = AuthService.register_admin("superadmin", "securepass99")
        self.assertTrue(success)

        # Login with new admin
        self.assertTrue(AuthService.login("superadmin", "securepass99"))
        self.assertTrue(AuthService.is_authenticated())
        self.assertEqual(AuthService.get_current_user(), "superadmin")

    def test_admin_registration_duplicate(self) -> None:
        """Verifies that duplicate admin usernames fail registration."""
        AuthService.register_admin("manager", "pass1")
        # Attempt duplicate
        success = AuthService.register_admin("manager", "pass2")
        self.assertFalse(success)

    def test_logout(self) -> None:
        """Verifies admin session removal."""
        AuthService.login("admin", "admin123")
        self.assertTrue(AuthService.is_authenticated())
        
        AuthService.logout()
        self.assertFalse(AuthService.is_authenticated())
        self.assertIsNone(AuthService.get_current_user())

if __name__ == "__main__":
    unittest.main()
