import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from app.utils.config import Config

class AppLogger:
    """Manages application-wide logging configuration.

    Logs info and activity messages to activity.log, and error details
    to error.log under the data/logs/ directory.
    """
    _activity_logger: logging.Logger = None
    _error_logger: logging.Logger = None

    @classmethod
    def setup_loggers(cls) -> None:
        """Sets up the activity and error loggers with appropriate handlers."""
        if cls._activity_logger is not None and cls._error_logger is not None:
            return

        log_format = logging.Formatter(
            "%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
        )

        # Ensure directory is created
        Config.initialize_directories()

        # Set up activity logger
        activity_file = Config.LOGS_DIR / "activity.log"
        activity_handler = RotatingFileHandler(
            activity_file, maxBytes=5 * 1024 * 1024, backupCount=3
        )
        activity_handler.setFormatter(log_format)
        activity_handler.setLevel(logging.INFO)

        cls._activity_logger = logging.getLogger("activity_logger")
        cls._activity_logger.setLevel(logging.INFO)
        cls._activity_logger.addHandler(activity_handler)

        # Avoid double logging to root logger (which could print to stdout)
        cls._activity_logger.propagate = False

        # Set up error logger
        error_file = Config.LOGS_DIR / "error.log"
        error_handler = RotatingFileHandler(
            error_file, maxBytes=5 * 1024 * 1024, backupCount=3
        )
        error_handler.setFormatter(log_format)
        error_handler.setLevel(logging.WARNING)

        cls._error_logger = logging.getLogger("error_logger")
        cls._error_logger.setLevel(logging.WARNING)
        cls._error_logger.addHandler(error_handler)
        cls._error_logger.propagate = False

    @classmethod
    def get_activity_logger(cls) -> logging.Logger:
        """Returns the logger for system activities."""
        if cls._activity_logger is None:
            cls.setup_loggers()
        return cls._activity_logger

    @classmethod
    def get_error_logger(cls) -> logging.Logger:
        """Returns the logger for error events."""
        if cls._error_logger is None:
            cls.setup_loggers()
        return cls._error_logger

# Initialize loggers upon importing the module
AppLogger.setup_loggers()

# Helper access points
activity_logger = AppLogger.get_activity_logger()
error_logger = AppLogger.get_error_logger()
