# Contributing to Student Management System

Thank you for showing interest in improving this project! We welcome contributions from everyone.

## Code of Conduct

Please be respectful, professional, and collaborative in all communications.

## How to Contribute

1. **Fork the Repository**: Create your own copy of this repository on GitHub.
2. **Clone the Fork**: Clone the project locally on your machine.
   ```bash
   git clone https://github.com/your-username/student-management-system.git
   ```
3. **Set Up Environment**: Install the required dependencies in a virtual environment.
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
4. **Create a Branch**: Create a descriptive branch name for your changes.
   ```bash
   git checkout -b feature/your-feature-name
   ```
5. **Implement and Document**: Write clean, type-hinted Python code. Ensure every new function has descriptive docstrings.
6. **Run Tests**: Verify your changes against the test suites.
   ```bash
   python -m unittest discover -s tests
   ```
7. **Commit and Push**: Push your changes to your fork and submit a Pull Request (PR) to the main branch of this repository.

## Coding Style Guidelines

- Adhere to PEP 8 standards.
- Add type hints to all function signatures.
- Write explanatory docstrings for all classes and functions.
- Keep terminal UI layouts consistent with the Rich framework styles.
