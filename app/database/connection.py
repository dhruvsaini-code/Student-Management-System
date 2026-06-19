import sqlite3
from typing import Generator
from app.utils.config import Config
from app.utils.logger import error_logger, activity_logger

def get_db_connection() -> sqlite3.Connection:
    """Establishes and configures a connection to the SQLite database.

    Configures foreign keys support and Row mapping.

    Returns:
        A sqlite3.Connection object ready for use.
    """
    try:
        conn = sqlite3.connect(str(Config.DB_PATH))
        conn.row_factory = sqlite3.Row
        
        # Enable Foreign Key constraints explicitly
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as e:
        error_logger.critical(f"Failed to connect to database at {Config.DB_PATH}: {str(e)}")
        raise e

class TransactionContext:
    """Context manager to handle database transactions safely.

    Automatically commits if successful, or rolls back on exceptions.
    """
    def __init__(self) -> None:
        self.conn: sqlite3.Connection = None

    def __enter__(self) -> sqlite3.Connection:
        self.conn = get_db_connection()
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.conn:
            try:
                if exc_type is not None:
                    self.conn.rollback()
                    activity_logger.warning("Database transaction rolled back due to error.")
                else:
                    self.conn.commit()
            finally:
                self.conn.close()
