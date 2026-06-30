# District Court Orakzai HR Management System

Standalone Windows desktop HR Management System built with Python, PySide6, SQLite, SQLAlchemy, and bcrypt.

This version implements the first four SRS use cases:

- UC01: Login to the System
- UC02: Manage Staff Profiles
- UC03: Manage Service Records
- UC04: Manage Postings & Transfers

## Default Login

- Username: `admin`
- Password: `admin123`

The default administrator is created automatically on first run. The password is stored as a bcrypt hash.

After login, open `Admin Account` from the sidebar to change the username, display name, or password. The current password is required before any account change is saved.

## Installation

On Windows:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

On Linux/macOS for development:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

You may also run:

```bash
python -m court_hrms.main
```

## Database

SQLite is created automatically on first run.

Default database location:

- Windows: `%LOCALAPPDATA%\DistrictCourtOrakzaiHRMS\court_hrms.sqlite3`
- Linux/macOS: `~/.local/share/DistrictCourtOrakzaiHRMS/court_hrms.sqlite3`

For development, you can override the database file:

```bash
COURT_HRMS_DB_PATH=/path/to/court_hrms.sqlite3 python main.py
```

## Architecture

The project uses a layered MVC style:

- `presentation/`: PySide6 windows, pages, forms, tables, dialogs, and theme.
- `controllers/`: UI-facing coordination layer. Controllers open sessions and call services.
- `services/`: Business rules and validation.
- `repositories/`: SQLAlchemy CRUD and query access.
- `models/`: SQLAlchemy ORM table models.
- `database/`: Engine, session factory, schema creation, and default admin seed.
- `utils/`: Validators, date helpers, and message box helpers.

## Running in PyCharm Professional

1. Open the project folder in PyCharm.
2. Select Python 3.11+ as the interpreter.
3. Install `requirements.txt`.
4. Create a run configuration for `main.py`.
5. Run the application and login with the default admin account.

## Building a Windows EXE

Build the `.exe` on a Windows machine, Windows VM, or Windows CI runner. PyInstaller creates an executable for the operating system where it runs, so running PyInstaller on Ubuntu creates a Linux binary, not a Windows `.exe`.

On Windows:

```powershell
build_windows.bat
```

The generated file will be:

```text
dist\DistrictCourtOrakzaiHRMS.exe
```

You can transfer that `.exe` to another Windows computer for testing. The SQLite database will be created automatically on that Windows computer under `%LOCALAPPDATA%\DistrictCourtOrakzaiHRMS`.
