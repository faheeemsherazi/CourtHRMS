# District Court Orakzai HR Management System

Standalone Windows desktop HR Management System for District Court Orakzai administrative staff.

## Technology Stack

- Python 3.11 or newer
- PySide6 desktop UI
- SQLAlchemy ORM
- SQLite database
- bcrypt password hashing
- Native Qt print preview, PDF export, and print dialogs

## Features

- UC01: Login to the System
- UC02: Manage Staff Profiles
- UC03: Manage Service Records
- UC04: Manage Postings & Transfers
- UC05: Manage Leave Records
- UC06: Manage Seniority Lists
- UC07: Generate HR Reports
- UC08: Logout from System

The existing Admin Account screen is preserved for changing the administrator username, display name, and password.

## Installation

Windows:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
python main.py
```

Linux/macOS development:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
python3 main.py
```

You may also run:

```bash
python3 -m court_hrms.main
```

## Default Login

- Username: `admin`
- Password: `admin123`

The default administrator is created automatically on first run. The password is stored as a bcrypt hash. Change the default password from `Admin Account` after first login.

## Database

SQLite is created automatically on first run.

Default database location:

- Windows: `%LOCALAPPDATA%\DistrictCourtOrakzaiHRMS\court_hrms.sqlite3`
- Linux/macOS: `~/.local/share/DistrictCourtOrakzaiHRMS/court_hrms.sqlite3`

For development, override the database file:

```bash
COURT_HRMS_DB_PATH=/path/to/court_hrms.sqlite3 python3 main.py
```

## Migration and Backup

The application uses an idempotent schema-upgrade function because Alembic is not configured in this project. On startup, the migration creates the UC05 leave tables if missing:

- `annual_leave_accounts`
- `leave_records`

Before creating missing tables, the app copies the existing database to:

```text
<app-data>/DistrictCourtOrakzaiHRMS/backups/
```

The migration is safe to run repeatedly and does not drop or recreate existing UC01-UC04 tables.

## Architecture

```text
Presentation -> Controller -> Service -> Repository -> Database
```

- `presentation/`: PySide6 windows, pages, forms, tables, dialogs, and theme.
- `controllers/`: UI-facing coordination, session opening, and safe result messages.
- `services/`: Business rules, validation, and multi-step transaction boundaries.
- `repositories/`: SQLAlchemy queries and persistence operations.
- `models/`: SQLAlchemy ORM mappings.
- `database/`: Engine, session factory, schema initialization, migration, and default admin seed.
- `reporting/`: Report DTOs, HTML templates, and Qt document/PDF builder.
- `utils/`: Validation, date helpers, logging, leave rules, seniority rules, and message boxes.

Services own business validation and write transactions. UI code never runs raw SQL or manages database sessions.

## Leave Policy

Each staff member receives 25 annual leave days per calendar year. Leave days are calendar days calculated inclusively:

```text
(end_date - start_date).days + 1
```

Leave requests cannot cross calendar years. The system blocks requests that exceed the remaining annual balance. Leave processing inserts history and updates annual balance in one transaction.

## Seniority Ranking Policy

Official seniority lists are generated dynamically and do not store editable rank values. The deterministic order is:

1. Selected designation only.
2. Active employees only.
3. Earlier Date of First Appointment ranks higher.
4. Earlier Date of Current Promotion ranks higher; missing promotion dates sort last.
5. Lower Selection Merit Number ranks higher; missing merit numbers sort last.
6. Earlier Date of Birth ranks higher.
7. Personal Number ascending as the final tie-breaker.

Employees missing Date of First Appointment are excluded and shown in an exclusions panel.

## Reports and Printing

Reports are generated with `QTextDocument` HTML templates and Qt printing support:

- Individual Staff Profile
- Leave History
- Seniority List

Each report supports preview, PDF export, and printing through the operating system print dialog. PDF filenames are suggested automatically and sanitized before use. Existing output files require user confirmation before overwrite.

## Logging

The app uses Python `logging` with a rotating file handler. Logs are written under:

```text
<app-data>/DistrictCourtOrakzaiHRMS/logs/
```

Logs include startup, migration, leave transactions, seniority generation, report generation/export/print, and logout. Passwords and sensitive report data are not logged.

## Tests

Run all tests:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

If `pytest` is installed:

```bash
.venv/bin/python -m pytest -q
```

## Quality Checks

```bash
.venv/bin/python -m compileall court_hrms tests main.py
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m black --check .
```

Run mypy if desired:

```bash
.venv/bin/python -m mypy court_hrms
```

PySide6 typing is not made strict in this project.

## Windows Executable Packaging

Build the `.exe` on Windows:

```powershell
build_windows.bat
```

The output is:

```text
dist\DistrictCourtOrakzaiHRMS.exe
```

The executable creates or upgrades the SQLite database under `%LOCALAPPDATA%\DistrictCourtOrakzaiHRMS`.

## Data Security Precautions

- Change the default administrator password after first login.
- Keep database backups before production upgrades.
- Do not email or publish the SQLite database.
- Restrict OS-level access to the application data folder.
- Do not store authentication tokens or passwords in reports.

## Known Limitations

- SQLite is intended for standalone desktop use, not concurrent multi-user network access.
- The project does not include Alembic; schema upgrades are handled by the built-in idempotent migration.
- Missing Date of First Appointment is excluded by the seniority rules, but the current service-record form requires the date for newly entered records.
