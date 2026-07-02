# District Court Orakzai HRMS Workflow

This file explains how to use the District Court Orakzai Human Resource Management System from startup through each screen in the application. It is written for an administrator or operator who needs to understand the full workflow of the software.

## 1. What This Software Does

District Court Orakzai HRMS is a desktop application for maintaining court staff HR records. The current application supports:

- Secure administrator login.
- Staff profile registration and update.
- Service record registration and update.
- First posting entry.
- Transfer execution with posting history.
- Dashboard totals for staff, service records, and current postings.
- Administrator username, display name, and password update.

The current UI does not include delete, export, report printing, attendance, payroll, leave, or document upload functionality.

## 2. Start the Application

Install dependencies first:

```bash
pip install -r requirements.txt
```

Run from the project root:

```bash
python main.py
```

You can also run:

```bash
python -m court_hrms.main
```

When the application starts, it automatically creates the SQLite database and the default administrator account if they do not already exist.

Default login:

| Field | Value |
| --- | --- |
| Username | `admin` |
| Password | `admin123` |

Recommended first step after first login: open `Admin Account` and change the default password.

## 3. Database Location

The database is created automatically.

Default database locations:

| Platform | Location |
| --- | --- |
| Windows | `%LOCALAPPDATA%\DistrictCourtOrakzaiHRMS\court_hrms.sqlite3` |
| Linux/macOS | `~/.local/share/DistrictCourtOrakzaiHRMS/court_hrms.sqlite3` |

For development or testing, use a custom database file:

```bash
COURT_HRMS_DB_PATH=/path/to/court_hrms.sqlite3 python main.py
```

## 4. Login and Logout Workflow

1. Open the application.
2. Enter administrator username and password.
3. Click `Login`, or press Enter while focused on the password field.
4. If credentials are valid, the main window opens.
5. Use the sidebar to move between pages.
6. Click `Logout` in the sidebar to leave the main window.
7. Confirm the logout prompt.

If login fails, the application shows `Invalid credentials.`, clears the password field, and keeps the login window open.

## 5. Main Navigation

After login, the sidebar contains:

- `Dashboard`
- `Staff Profiles`
- `Service Records`
- `Postings & Transfers`
- `Admin Account`
- `Logout`

Opening a page refreshes its data automatically where refresh is supported.

## 6. Dashboard

The Dashboard is a read-only summary page.

It shows:

- Total staff profiles.
- Total service records.
- Total current postings.
- A short summary of the system scope.

Use this page to quickly confirm whether records have been entered and whether current postings exist.

## 7. Staff Profiles Workflow

Use `Staff Profiles` to create, search, view, and update employee personal information.

### 7.1 Add a Staff Profile

1. Open `Staff Profiles`.
2. Fill in the profile form.
3. Review the calculated `Retirement Date`. This is automatically calculated from `Date of Birth`.
4. Click `Add Profile`.
5. If validation succeeds, the profile is saved and appears in the `Staff Register` table.

### 7.2 Search a Staff Profile

1. Enter the staff member's personal number in the search box at the top.
2. Click `Search`, or press Enter.
3. If the personal number exists, the profile loads into the form.

### 7.3 Update a Staff Profile

1. Search for a profile, or select a row in the `Staff Register` table.
2. The selected profile loads into the form.
3. Edit the required fields.
4. Click `Update Profile`.
5. The table refreshes with the updated information.

### 7.4 Clear the Staff Form

Click `Clear` in the search area or `Clear Form` in the form area. This clears the search input, form fields, selected table row, and disables `Update Profile` until another profile is selected.

### 7.5 Staff Profile Fields

| Field | Required | Notes |
| --- | --- | --- |
| Personal Number | Yes | Must be unique. Used for searching staff throughout the system. |
| Full Name | Yes | At least 3 characters and must include letters. |
| Father Name | Yes | At least 3 characters and must include letters. |
| CNIC | Yes | Exactly 13 digits, no dashes, unique. |
| Date of Birth | Yes | Employee must be at least 18 years old. |
| Retirement Date | Automatic | Read-only; calculated from date of birth. |
| Gender | No | Select from the dropdown. |
| Religion | No | Select from the dropdown. |
| Marital Status | No | Select from the dropdown. |
| Domicile | No | Free text. |
| District | Yes | At least 3 characters and must include letters. |
| Tehsil | No | If entered, at least 3 characters and must include letters. |
| Mobile Number | Yes | Exactly 11 digits. |
| Email | No | If entered, must be a valid email address. |
| Emergency Contact | No | Digits only, maximum 17 digits. |
| Qualification | No | Free text. |
| Present Address | Yes | At least 5 characters and must include letters. |
| Permanent Address | Yes | At least 5 characters and must include letters. |

## 8. Service Records Workflow

Use `Service Records` to maintain employment details for an existing staff profile.

Important prerequisite: a staff profile must exist before a service record can be added.

### 8.1 Select Staff for a Service Record

1. Open `Service Records`.
2. Enter the staff personal number.
3. Click `Search Staff`, or press Enter.
4. If the staff profile exists, the page shows the selected staff member.
5. If a latest service record already exists for that staff member, it loads into the form.

### 8.2 Add a Service Record

1. Search and select the staff member first.
2. Fill in the service details.
3. Click `Add Service Record`.
4. If validation succeeds, the record is saved and appears in the `Service Record Register`.

The application can store more than one service record for a staff member. Searching by personal number loads the latest record. Selecting a row in the register loads that specific record.

### 8.3 Update a Service Record

1. Search for a staff member with an existing service record, or select a row in the `Service Record Register`.
2. Edit the service details.
3. Click `Update Service Record`.
4. The selected record is updated.

### 8.4 Clear the Service Record Form

Click `Clear Form` to clear the selected staff, service fields, selected table row, and update mode.

### 8.5 Service Record Fields

| Field | Required | Notes |
| --- | --- | --- |
| Staff | Yes | Search by personal number before adding. |
| Designation | Yes | Must be selected from the designation dropdown. |
| BPS | Yes | Must be between 1 and 22 and compatible with the designation. |
| Employment Type | Yes | `Permanent`, `Contract`, or `Temporary`. |
| Employment Status | Yes | `Active`, `Retired`, or `Suspended`. |
| First Appointment | Yes | Date of first appointment. |
| Current Promotion Date | No | Enable the checkbox before entering the promotion date. |
| Merit Number | No | If entered, must be a whole number and cannot be negative. |
| Remarks | No | Free text. |

### 8.6 Designation and BPS Rules

| Designation | Allowed BPS |
| --- | --- |
| Naib Qasid | 1 to 5 |
| Junior Clerk | 7 to 11 |
| Senior Clerk | 11 to 14 |
| Stenographer | 14 to 16 |
| Superintendent | 16 to 18 |
| Civil Judge | 17 to 19 |
| Additional District Judge | 20 to 21 |
| District & Sessions Judge | 21 to 22 |

The current promotion date cannot be earlier than the first appointment date.

## 9. Postings and Transfers Workflow

Use `Postings & Transfers` to enter a staff member's first posting and later execute transfers.

Important prerequisites:

- A staff profile must exist.
- A service record must exist before posting or transfer.
- A first posting must exist before a transfer can be executed.

### 9.1 Search Staff for Posting or Transfer

1. Open `Postings & Transfers`.
2. Enter the staff personal number.
3. Click `Search Staff`, or press Enter.
4. The page shows the staff name and whether a service record is available.
5. The current posting and posting history load if they exist.

### 9.2 Add First Posting

Use this only once for each staff member.

1. Search and select the staff member.
2. Confirm the staff member has a service record.
3. Enter the first posting station.
4. Select the start date.
5. Enter reason and remarks if needed.
6. Click `Add First Posting`.
7. The first posting becomes the current posting and appears in the posting history.

Rules:

- Station name is required.
- Start date cannot be before the staff member's date of first appointment.
- If a current posting or posting history already exists, use `Execute Transfer` instead.

### 9.3 Execute Transfer

1. Search and select the staff member.
2. Confirm a current posting is shown.
3. Enter the new station.
4. Select the transfer date.
5. Enter reason and remarks if needed.
6. Click `Execute Transfer`.
7. Confirm the transfer prompt.

When a transfer succeeds:

- The previous current posting is closed.
- Its end date is set to the transfer date.
- A new current posting is created for the new station.
- The posting history table refreshes.

Rules:

- A current posting must exist before transfer.
- New station is required.
- Transfer date cannot be before the current posting start date.
- Transfer date cannot be before the staff member's date of first appointment.

### 9.4 Posting History

The posting history table shows:

- Station.
- Start date.
- End date.
- Whether the row is current.
- Transfer reason.
- Remarks.

The current UI does not provide editing or deletion of posting history records. Corrections require a code/database-level change or a future UI feature.

## 10. Admin Account Workflow

Use `Admin Account` to change the signed-in administrator details.

### 10.1 Change Username or Display Name

1. Open `Admin Account`.
2. Edit `Username` or `Full Name`.
3. Enter the current password.
4. Leave new password fields blank if you do not want to change the password.
5. Click `Save Account`.

Rules:

- Username is required.
- Username must be at least 3 characters.
- Username must be unique.
- Current password is required for any account update.

### 10.2 Change Password

1. Open `Admin Account`.
2. Enter the current password.
3. Enter the new password.
4. Repeat the same value in `Confirm Password`.
5. Click `Save Account`.

Rules:

- New password must be at least 8 characters.
- New password and confirmation must match.
- If new password fields are left blank, the existing password is kept.

After a successful account update, the sidebar signed-in label refreshes. Use the updated username and password for future logins.

## 11. Recommended End-to-End Daily Workflow

For a new employee:

1. Login as administrator.
2. Open `Staff Profiles`.
3. Add the staff profile.
4. Open `Service Records`.
5. Search the staff member by personal number.
6. Add the service record.
7. Open `Postings & Transfers`.
8. Search the staff member by personal number.
9. Add the first posting.
10. Return to `Dashboard` and confirm totals updated.

For an employee transfer:

1. Login as administrator.
2. Open `Postings & Transfers`.
3. Search the staff member by personal number.
4. Confirm the current posting.
5. Enter transfer details.
6. Click `Execute Transfer`.
7. Confirm the transfer.
8. Review posting history.

For updating existing data:

1. Open the relevant page.
2. Search by personal number, or select a row from the register table.
3. Edit the fields.
4. Click the update button on that page.
5. Confirm the register table refreshes.

## 12. Common Validation Messages

| Situation | Message |
| --- | --- |
| Wrong login | `Invalid credentials.` |
| Staff personal number not found | `No staff profile found for this personal number.` |
| Duplicate staff personal number | `Personal number already exists.` |
| Duplicate CNIC | `CNIC already exists.` |
| CNIC format wrong | `CNIC must be exactly 13 digits without dashes.` |
| Mobile format wrong | `Mobile number must be exactly 11 digits.` |
| Service record without staff | `Search and select a staff profile before adding a service record.` |
| Posting before service record | `A service record must exist before posting or transfer.` |
| Transfer before first posting | `No current posting was found. Add the first posting before transfer.` |
| Account update without current password | `Current password is required.` |

## 13. Current Functional Boundaries

The software currently focuses on record creation, search, update, and posting history. Keep these boundaries in mind:

- Staff profiles can be added and updated, but not deleted from the UI.
- Service records can be added and updated, but not deleted from the UI.
- Posting history can be created through first posting and transfer, but not edited or deleted from the UI.
- The dashboard is read-only.
- Only administrator login is implemented.
- There is no role management or multi-user permission screen.
- There is no built-in backup/restore screen. Backups should be handled by copying the SQLite database file while the app is closed.

