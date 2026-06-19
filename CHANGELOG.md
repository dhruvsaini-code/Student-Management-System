# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] - 2026-06-19

### Added
- **Administrative Authentication**: Added admin login page, password hashing via `bcrypt`, and session-tracking.
- **Fuzzy Search Engine**: Implemented student searching by ID, name, and email, with fuzzy matching leveraging `difflib.SequenceMatcher`.
- **PDF Report Generation**: Integrated `reportlab` to compile professional student report cards, class performance registries, and attendance sheets.
- **Data Visualizations**: Integrated `matplotlib` (running headlessly) to render grade distributions, attendance breakdowns, and course sizes.
- **Database Backup & Recovery**: Added datetime-stamped backup creation and restore functionality.
- **Activity & Error Logging**: Added rotating log handlers recording runtime activities (`data/logs/activity.log`) and error alerts (`data/logs/error.log`).
- **Interactive Rich CLI**: Replaced generic menus with vibrant banners, progress tracks, spinners, and interactive submenus using the `rich` library.
- **Type Hints & Docstrings**: Refactored the entire project to have full type hints and docstrings for every function.

### Changed
- **Architectural Restructuring**: Moved monolithic modules into a professional package directory layout (`app/database/`, `app/models/`, `app/services/`, `app/cli/`, `app/utils/`).
- **Database Schema Upgrades**: Added constraints, indexes, unique constraints, and transaction-isolated context managers.

## [1.0.0] - 2026-06-16

### Added
- Basic CRUD operations for students and courses.
- Basic enrollments and grading.
- Attendance logs checking.
- Basic CSV import/export.
- Core CLI framework.
