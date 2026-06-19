import sqlite3
import datetime
from typing import Optional
import bcrypt
from app.database.connection import get_db_connection, TransactionContext
from app.utils.logger import activity_logger, error_logger

class AuthService:
    """Manages administrative authentication, registration, and active session tracking."""

    _current_user: Optional[str] = None

    @classmethod
    def register_admin(cls, username: str, raw_password: str) -> bool:
        """Hashes raw password and saves the admin account in the database.

        Args:
            username: The unique administrator username.
            raw_password: The raw password text to register.

        Returns:
            True if the admin account is successfully created, False if username exists or error occurs.
        """
        if not username or not raw_password:
            return False

        username = username.strip().lower()
        try:
            salt = bcrypt.gensalt()
            hashed_pw = bcrypt.hashpw(raw_password.encode('utf-8'), salt).decode('utf-8')
            now_str = datetime.datetime.now().isoformat()

            with TransactionContext() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO admins (username, password_hash, created_at) VALUES (?, ?, ?)",
                    (username, hashed_pw, now_str)
                )
                activity_logger.info(f"Admin account registered successfully: '{username}'")
                return True
        except sqlite3.IntegrityError:
            activity_logger.warning(f"Registration failed: admin username '{username}' already exists.")
            return False
        except Exception as e:
            error_logger.error(f"Error during admin registration for '{username}': {str(e)}")
            return False

    @classmethod
    def login(cls, username: str, raw_password: str) -> bool:
        """Verifies admin credentials and establishes a session.

        Args:
            username: The username entered.
            raw_password: The raw password text.

        Returns:
            True if login succeeds, False otherwise.
        """
        if not username or not raw_password:
            return False

        username = username.strip().lower()
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT password_hash FROM admins WHERE username = ?", (username,))
            row = cursor.fetchone()
            if not row:
                activity_logger.info(f"Failed login attempt: username '{username}' not found.")
                return False

            hashed_pw = row["password_hash"]
            if bcrypt.checkpw(raw_password.encode('utf-8'), hashed_pw.encode('utf-8')):
                cls._current_user = username
                activity_logger.info(f"Admin login successful: '{username}'")
                return True
            else:
                activity_logger.info(f"Failed login attempt: incorrect password for '{username}'.")
                return False
        except Exception as e:
            error_logger.error(f"Authentication database error for '{username}': {str(e)}")
            return False
        finally:
            conn.close()

    @classmethod
    def logout(cls) -> None:
        """Destroys the current user session."""
        user = cls._current_user
        cls._current_user = None
        if user:
            activity_logger.info(f"Admin logout successful: '{user}'")

    @classmethod
    def get_current_user(cls) -> Optional[str]:
        """Returns the username of the logged-in administrator, if any.

        Returns:
            The username if logged in, otherwise None.
        """
        return cls._current_user

    @classmethod
    def is_authenticated(cls) -> bool:
        """Checks if a session is currently active.

        Returns:
            True if an admin session is active, False otherwise.
        """
        return cls._current_user is not None
