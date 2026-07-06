# District Court Orakzai HRMS Workflow

This guide explains how an administrator uses District Court Orakzai HRMS from login through UC01-UC08.

## 1. System Scope

The application supports:

- UC01: Login to the System
- UC02: Manage Staff Profiles
- UC03: Manage Service Records
- UC04: Manage Postings & Transfers
- UC05: Manage Leave Records
- UC06: Manage Seniority Lists
- UC07: Generate HR Reports
- UC08: Logout from System

The Admin Account screen is also available for changing the administrator username, display name, and password.

## 2. Start the Application

Install dependencies:

```bash
pip install -r requirements.txt
```

Run from the project root:

```bash
python3 main.py
```

Or:

```bash
python3 -m court_hrms.main
```

On Windows, use `python main.py` or the configured PyCharm run target.

Default login:

| Field | Value |
| --- | --- |
| Username | `admin` |
| Password | `admin123` |

Change the default password from `Admin Account` after first login.

## 3. Database and Migration

SQLite is created or upgraded automatically on startup.

Default database locations:

| Platform | Location |
| --- | --- |
| Windows | `%LOCALAPPDATA%\DistrictCourtOrakzaiHRMS\court_hrms.sqlite3` |
| Linux/macOS | `~/.local/share/DistrictCourtOrakzaiHRMS/court_hrms.sqlite3` |

For development or testing:

```bash
COURT_HRMS_DB_PATH=/path/to/court_hrms.sqlite3 python3 main.py
```

The built-in migration creates these leave tables if missing:

- `annual_leave_accounts`
- `leave_records`

Before the migration creates missing tables, it backs up the existing database under:

```text
<app-data>/DistrictCourtOrakzaiHRMS/backups/
```

## 4. Login and Logout

### Login

1. Open the application.
2. Enter administrator username and password.
3. Click `Login`, or press Enter while focused on the password field.
4. If credentials are valid, the main window opens.

If login fails, the application shows `Invalid credentials.`, clears the password field, and keeps the login window open.

### Logout

1. Click `Logout` in the sidebar.
2. Confirm the prompt:

```text
Logout from the system?

Any unsaved form input will be discarded.
```

3. The main window closes safely.
4. The login window appears again.

Logout clears authenticated state and protected page selections without creating a second `QApplication`.

## 5. Main Navigation

After login, the sidebar contains:

- `Dashboard`
- `Staff Profiles`
- `Service Records`
- `Postings & Transfers`
- `Leave Management`
- `Seniority Lists`
- `Reports & Printing`
- `Admin Account`
- `Logout`

Pages are created once and refreshed when opened.

## 6. Dashboard

The Dashboard is read-only.

It shows:

- Total staff profiles
- Total service records
- Total current postings
- Current system scope summary

Use it to confirm that core records and posting data exist.

## 7. Staff Profiles

Use `Staff Profiles` to create, search, view, and update employee personal information.

### Add Staff

1. Open `Staff Profiles`.
2. Fill in the profile form.
3. Review the calculated retirement date.
4. Click `Add Profile`.
5. The profile appears in the `Staff Register` table.

### Search Staff

1. Enter Personal Number in the search box.
2. Click `Search`, or press Enter.
3. The matching profile loads into the form.

### Update Staff

1. Search for a profile or select a register row.
2. Edit fields.
3. Click `Update Profile`.
4. The table refreshes.

### Required Staff Rules

| Field | Rule |
| --- | --- |
| Personal Number | Required and unique |
| Full Name | Required, at least 3 characters, must include letters |
| Father Name | Required, at least 3 characters, must include letters |
| CNIC | Required, unique, exactly 13 digits |
| Date of Birth | Required, employee must be at least 18 |
| Mobile Number | Required, exactly 11 digits |
| District | Required, at least 3 characters, must include letters |
| Present Address | Required, at least 5 characters, must include letters |
| Permanent Address | Required, at least 5 characters, must include letters |

## 8. Service Records

Use `Service Records` to maintain current and historical employment details.

Prerequisite: staff profile must exist.

### Add Service Record

1. Open `Service Records`.
2. Search staff by Personal Number.
3. Fill in designation, BPS, employment type, status, appointment date, and optional fields.
4. Click `Add Service Record`.

### Update Service Record

1. Search staff or select a service register row.
2. Edit service details.
3. Click `Update Service Record`.

### Service Rules

- Designation is required.
- BPS must be between 1 and 22.
- BPS must match the configured designation range.
- Employment Type must be `Permanent`, `Contract`, or `Temporary`.
- Employment Status must be `Active`, `Retired`, or `Suspended`.
- Current Promotion Date cannot be before Date of First Appointment.
- Merit Number must be a non-negative whole number if entered.

## 9. Postings & Transfers

Use `Postings & Transfers` for first posting and later transfers.

Prerequisites:

- Staff profile must exist.
- Service record must exist.
- First posting must exist before transfer.

### Add First Posting

1. Open `Postings & Transfers`.
2. Search staff by Personal Number.
3. Enter station, start date, reason, and remarks.
4. Click `Add First Posting`.

Rules:

- Station name is required.
- Start date cannot be before Date of First Appointment.
- If posting history already exists, use transfer instead.

### Execute Transfer

1. Search staff by Personal Number.
2. Confirm a current posting is displayed.
3. Enter new station, transfer date, reason, and remarks.
4. Click `Execute Transfer`.
5. Confirm the prompt.

When transfer succeeds:

- Previous posting is closed.
- Previous posting end date becomes the transfer date.
- New posting becomes current.
- Posting history refreshes.

## 10. Leave Management

Use `Leave Management` to record annual leave and view balances.

Policy:

- Each staff member receives 25 annual leave days per calendar year.
- Leave days are counted inclusively.
- A leave request cannot cross calendar years.
- Requests exceeding remaining balance are blocked.

### Search Staff

1. Open `Leave Management`.
2. Enter Personal Number.
3. Click `Search`.
4. Staff details, service status, balance summary, and history load.

### Process Leave

1. Select Leave Year.
2. Select Start Date and End Date.
3. Confirm the calculated day count.
4. Enter Reason.
5. Enter Remarks if needed.
6. Click `Process Leave`.

On success:

```text
Leave recorded successfully.
New remaining balance: X days.
```

On insufficient balance:

```text
Insufficient leave balance.
Requested: X days
Remaining: Y days
```

The history row and balance update are saved in one transaction.

## 11. Seniority Lists

Use `Seniority Lists` to generate official designation-wise active-staff seniority.

### Generate List

1. Open `Seniority Lists`.
2. Select Designation.
3. Click `Generate List`.
4. Review ranked staff, summary counts, and exclusions.

Ranking order:

1. Selected designation only.
2. Active staff only.
3. Date of First Appointment ascending.
4. Date of Current Promotion ascending, missing values last.
5. Selection Merit Number ascending, missing values last.
6. Date of Birth ascending.
7. Personal Number ascending.

Staff missing Date of First Appointment are excluded and shown in the exclusions panel.

## 12. Reports & Printing

Use `Reports & Printing` for preview, PDF export, and print dispatch.

Available reports:

- Individual Staff Profile
- Leave History
- Seniority List

### Individual Staff Profile

1. Select `Individual Staff Profile`.
2. Enter Personal Number.
3. Click `Preview Report`, `Export PDF`, or `Print`.

Report includes identity, contact, service, posting, and leave summary sections.

### Leave History

1. Select `Leave History`.
2. Enter Personal Number.
3. Select a year or `All Years`.
4. Preview, export, or print.

Leave totals match the same leave service used by `Leave Management`.

### Seniority List

1. Select `Seniority List`.
2. Select Designation.
3. Preview, export, or print.

Ranks match the same seniority service used by `Seniority Lists`.

### PDF Export

1. Click `Export PDF`.
2. Choose save location.
3. Confirm overwrite if the file already exists.

On success:

```text
PDF report exported successfully.
```

### Print

1. Click `Print`.
2. Select a printer in the operating system print dialog.
3. Print or cancel.

Cancelling the print dialog is not an error.

## 13. Admin Account

Use `Admin Account` to change signed-in administrator details.

### Change Username or Display Name

1. Open `Admin Account`.
2. Edit `Username` or `Full Name`.
3. Enter current password.
4. Leave new password fields blank if password should not change.
5. Click `Save Account`.

### Change Password

1. Open `Admin Account`.
2. Enter current password.
3. Enter new password.
4. Repeat it in `Confirm Password`.
5. Click `Save Account`.

Rules:

- Username is required and unique.
- Username must be at least 3 characters.
- Current password is required for account updates.
- New password must be at least 8 characters.
- New password confirmation must match.

## 14. Recommended Daily Workflows

### New Employee

1. Login.
2. Add Staff Profile.
3. Add Service Record.
4. Add First Posting.
5. Confirm dashboard totals.

### Leave Request

1. Open `Leave Management`.
2. Search staff.
3. Select year and dates.
4. Confirm calculated days.
5. Process leave.
6. Confirm remaining balance and history.

### Seniority List

1. Ensure staff service records are current.
2. Open `Seniority Lists`.
3. Select designation.
4. Generate list.
5. Review exclusions.
6. Export or print from `Reports & Printing` if needed.

### HR Report

1. Open `Reports & Printing`.
2. Select report type.
3. Enter required filters.
4. Preview.
5. Export PDF or print.

### End Session

1. Click `Logout`.
2. Confirm.
3. Verify login screen appears.

## 15. Common Validation Messages

| Situation | Message |
| --- | --- |
| Wrong login | `Invalid credentials.` |
| Staff personal number not found | `No staff profile found for this personal number.` |
| Duplicate staff personal number | `Personal number already exists.` |
| Duplicate CNIC | `CNIC already exists.` |
| Service record without staff | `Search and select a staff profile before adding a service record.` |
| Posting before service record | `A service record must exist before posting or transfer.` |
| Transfer before first posting | `No current posting was found. Add the first posting before transfer.` |
| Leave without staff | `Search and select a staff profile before processing leave.` |
| Cross-year leave | `A leave request cannot cross calendar years. Record each year separately.` |
| Insufficient leave | `Insufficient leave balance.` |
| Missing report staff | `No records found for the supplied Personal Number.` |
| Account update without current password | `Current password is required.` |

## 16. Functional Boundaries

- Staff profiles can be added and updated, but not deleted from the UI.
- Service records can be added and updated, but not deleted from the UI.
- Posting history is created through first posting and transfer, but not edited or deleted from the UI.
- Leave records can be added and viewed, but not deleted from the UI.
- Seniority ranks are generated dynamically and are not manually editable.
- Reports are read-only and do not modify database data.
- SQLite is intended for standalone desktop use.
- Backup and restore are handled by copying the SQLite database while the app is closed, plus automatic pre-migration backups.

## 17. Verification Commands

```bash
.venv/bin/python -m compileall court_hrms tests main.py
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m black --check .
```
