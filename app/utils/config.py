import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    """Configuration class for the Student Management System.

    Manages database connection paths, backup folders, logging setup,
    and runtime environment properties.
    """
    # Base Project Directory
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

    # Runtime Environment
    ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = ENV == "development"

    # Database Configuration
    DB_NAME: str = os.getenv("DB_NAME", "student_management.db")
    DB_PATH: Path = BASE_DIR / DB_NAME

    # Data Directory Setup
    DATA_DIR: Path = BASE_DIR / "data"
    LOGS_DIR: Path = DATA_DIR / "logs"
    BACKUPS_DIR: Path = DATA_DIR / "backups"
    REPORTS_DIR: Path = DATA_DIR / "reports"
    CHARTS_DIR: Path = DATA_DIR / "charts"

    @classmethod
    def initialize_directories(cls) -> None:
        """Creates the necessary directories for database backups, reports, and logs."""
        for directory in [cls.DATA_DIR, cls.LOGS_DIR, cls.BACKUPS_DIR, cls.REPORTS_DIR, cls.CHARTS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)

# Ensure folders exist when loaded
Config.initialize_directories()
