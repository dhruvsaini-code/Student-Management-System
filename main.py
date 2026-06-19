import sys
import os

# Ensure the project root directory is in the Python load path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from app.cli.menu import start_app
from app.cli.landing import clear_screen

def main() -> None:
    """Entry point for the Student Management System application.

    Starts database verification and boots the console interactive CLI.
    Supports clean interrupts.
    """
    try:
        start_app()
    except KeyboardInterrupt:
        clear_screen()
        print("\nSystem closed by administrator. Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()
