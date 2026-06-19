import shutil
import datetime
from pathlib import Path
from typing import List, Tuple
from app.utils.config import Config
from app.utils.logger import activity_logger, error_logger

class BackupService:
    """Manages SQLite database backup creation and restore procedures."""

    @staticmethod
    def create_backup() -> Tuple[bool, str]:
        """Copies the active database file to a timestamped backup file in the backups folder.

        Returns:
            A tuple of (success_status, backup_file_name_or_error_message).
        """
        # Ensure directories exist
        Config.initialize_directories()

        if not Config.DB_PATH.exists():
            return False, "Database file does not exist to back up."

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_{Config.DB_NAME.replace('.db', '')}_{timestamp}.db"
        dest_path = Config.BACKUPS_DIR / backup_filename

        try:
            shutil.copy2(str(Config.DB_PATH), str(dest_path))
            activity_logger.info(f"Database backup created successfully: '{backup_filename}'")
            return True, backup_filename
        except Exception as e:
            msg = f"Failed to copy database file to '{dest_path}': {str(e)}"
            error_logger.error(msg)
            return False, str(e)

    @staticmethod
    def list_backups() -> List[Tuple[str, str, int]]:
        """Lists available backup files sorted by creation date descending.

        Returns:
            A list of tuples: (filename, formatted_modification_time, size_in_bytes).
        """
        Config.initialize_directories()
        backups = []
        try:
            for file_path in Config.BACKUPS_DIR.glob("backup_*.db"):
                stat = file_path.stat()
                mod_time = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                backups.append((file_path.name, mod_time, stat.st_size))
            
            # Sort by filename descending (which effectively sorts by timestamp)
            backups.sort(key=lambda x: x[0], reverse=True)
        except Exception as e:
            error_logger.error(f"Error listing database backups: {str(e)}")
        return backups

    @staticmethod
    def restore_backup(backup_filename: str) -> Tuple[bool, str]:
        """Restores the database to a selected backup version.

        Forces database overwriting.

        Args:
            backup_filename: The name of the file under data/backups/ to restore.

        Returns:
            A tuple of (success_status, status_message).
        """
        source_path = Config.BACKUPS_DIR / backup_filename
        if not source_path.exists():
            return False, f"Backup file '{backup_filename}' not found."

        try:
            # Create a backup of the current database before overwriting, in case of emergency
            emergency_filename = f"pre_restore_emergency_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            emergency_path = Config.BACKUPS_DIR / emergency_filename
            if Config.DB_PATH.exists():
                shutil.copy2(str(Config.DB_PATH), str(emergency_path))
                activity_logger.info(f"Pre-restore emergency backup created: '{emergency_filename}'")

            # Restore the selected backup file by copying it over Config.DB_PATH
            shutil.copy2(str(source_path), str(Config.DB_PATH))
            activity_logger.info(f"Database successfully restored from backup: '{backup_filename}'")
            return True, f"Successfully restored database from '{backup_filename}'. Emergency rollback file created: '{emergency_filename}'."
        except Exception as e:
            msg = f"Failed to restore database from backup '{backup_filename}': {str(e)}"
            error_logger.error(msg)
            return False, str(e)
