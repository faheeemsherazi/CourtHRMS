# Court HRMS Testing Data

Use this file as a practical checklist for testing District Court Orakzai HRMS. All CNICs, phone numbers, names, and addresses below are fake testing data.

## Default Login

| Field | Value |
| --- | --- |
| Username | `admin` |
| Password | `admin123` |

## Staff Profile Validation Rules

| Field | Rule |
| --- | --- |
| Personal Number | Required and unique |
| Full Name | Required, at least 3 characters, must include letters |
| Father Name | Required, at least 3 characters, must include letters |
| CNIC | Required, unique, exactly 13 digits, no dashes |
| Date of Birth | Required, employee must be at least 18 years old |
| Mobile Number | Required, exactly 11 digits |
| Emergency Contact | Optional, digits only, maximum 17 digits |
| Present Address | Required, at least 5 characters, must include letters |
| Permanent Address | Required, at least 5 characters, must include letters |
| District | Required, at least 3 characters, must include letters |
| Tehsil | Optional, but if entered must be at least 3 characters and include letters |
| Email | Optional, but must be valid if entered |
| Gender, Religion, Marital Status, Domicile, Qualification | Optional |

## Valid Staff Profiles

| Personal # | Full Name | Father Name | CNIC | DOB | Mobile | Emergency Contact | District | Tehsil | Present Address | Permanent Address | Email |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `DC-ORZ-0001` | `Muhammad Ali Khan` | `Abdul Karim Khan` | `1730112345671` | `1990-05-20` | `03001234567` | `1155` | `Orakzai` | blank | `District Courts Orakzai` | `Village Samana, District Orakzai` | `ali.khan@example.com` |
| `DC-ORZ-0002` | `Sanaullah Khan` | `Rahimullah Khan` | `1730123456782` | `1986-11-04` | `03111234567` | `92300123456789012` | `Orakzai` | `Lower Orakzai` | `Sessions Court Hangu Road` | `Kurez, District Orakzai` | blank |
| `DC-ORZ-0003` | `Ayesha Bibi` | `Gul Rahman` | `1730134567893` | `1995-02-15` | `03221234567` | blank | `Orakzai` | `Upper Orakzai` | `Judicial Complex Orakzai` | `Kalaya, District Orakzai` | `ayesha.bibi@example.com` |
| `DC-ORZ-0004` | `Naveed Ahmad` | `Sher Alam` | `1730145678904` | `1982-07-08` | `03331234567` | `1122` | `Kohat` | `Kohat` | `District Judiciary Kohat` | `Jarma, District Kohat` | `naveed.ahmad@example.com` |

## Invalid Staff Profile Tests

| Test | Change From Valid Profile | Expected Error |
| --- | --- | --- |
| Missing personal number | Set Personal # blank | `Personal number is required.` |
| Duplicate personal number | Reuse `DC-ORZ-0001` for another profile | `Personal number already exists.` |
| Missing full name | Set Full Name blank | `Full name is required.` |
| Short full name | Use `M` | `Full name must be at least 3 characters.` |
| Numeric full name | Use `123` | `Full name must include letters, not numbers only.` |
| Missing father name | Set Father Name blank | `Father name is required.` |
| Short father name | Use `A` | `Father name must be at least 3 characters.` |
| Numeric father name | Use `456` | `Father name must include letters, not numbers only.` |
| Missing CNIC | Set CNIC blank | `CNIC is required.` |
| Short CNIC | Use `173011234567` | `CNIC must be exactly 13 digits without dashes.` |
| Long CNIC | Use `17301123456712` | `CNIC must be exactly 13 digits without dashes.` |
| CNIC with dash | Use `17301-1234567-1` | `CNIC must be exactly 13 digits without dashes.` |
| Duplicate CNIC | Reuse `1730112345671` for another profile | `CNIC already exists.` |
| Underage employee | Use DOB `2010-01-01` | `Date of birth must show the employee is at least 18 years old.` |
| Missing mobile | Set Mobile blank | `Mobile number is required.` |
| Short mobile | Use `0300123456` | `Mobile number must be exactly 11 digits.` |
| Long mobile | Use `030012345678` | `Mobile number must be exactly 11 digits.` |
| Mobile with letters | Use `0300ABC4567` | `Mobile number must be exactly 11 digits.` |
| Emergency contact with letters | Use `0300ABC4567` | `Emergency contact must contain digits only.` |
| Emergency contact too long | Use `123456789012345678` | `Emergency contact cannot be more than 17 digits.` |
| Missing district | Set District blank | `District is required.` |
| Short district | Use `Or` | `District must be at least 3 characters.` |
| Numeric district | Use `123` | `District must include letters, not numbers only.` |
| Tehsil blank | Set Tehsil blank | Should save successfully |
| Short tehsil | Use `Up` | `Tehsil must be at least 3 characters.` |
| Numeric tehsil | Use `456` | `Tehsil must include letters, not numbers only.` |
| Present address too short | Use `ABCD` | `Present address must be at least 5 characters.` |
| Numeric present address | Use `12345` | `Present address must include letters, not numbers only.` |
| Permanent address too short | Use `WXYZ` | `Permanent address must be at least 5 characters.` |
| Numeric permanent address | Use `67890` | `Permanent address must include letters, not numbers only.` |
| Invalid email | Use `not-an-email` | `Email address is not valid.` |

## Valid Service Records

First create the matching staff profile, then search by Personal # on the Service Records page.

| Staff Personal # | Designation | BPS | Employment Type | Employment Status | First Appointment | Promotion Date | Merit # | Remarks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `DC-ORZ-0001` | `Junior Clerk` | `11` | `Permanent` | `Active` | `2014-09-01` | blank | `12` | `Initial appointment after recruitment process.` |
| `DC-ORZ-0002` | `Stenographer` | `15` | `Permanent` | `Active` | `2011-03-10` | `2018-07-01` | `5` | `Promotion verified from service book.` |
| `DC-ORZ-0003` | `Naib Qasid` | `3` | `Contract` | `Active` | `2020-01-15` | blank | blank | `Contract staff profile for testing.` |
| `DC-ORZ-0004` | `Civil Judge` | `18` | `Permanent` | `Active` | `2010-06-21` | `2017-05-03` | `2` | `Judicial officer record sample.` |

## Invalid Service Record Tests

| Test | Input | Expected Error |
| --- | --- | --- |
| No staff selected | Add record before staff search | `Search and select a staff profile before adding a service record.` |
| Blank designation | Select blank Designation | `Designation is required.` |
| BPS below range | Use BPS `0` through service/API test | `BPS must be between 1 and 22.` |
| BPS above range | Use BPS `23` through service/API test | `BPS must be between 1 and 22.` |
| Wrong BPS for designation | `Junior Clerk`, BPS `16` | `Junior Clerk is compatible with BPS 7 to 11 only.` |
| Promotion before appointment | First Appointment `2014-09-01`, Promotion `2013-12-31` | `Date of current promotion cannot be before date of first appointment.` |
| Negative merit number | Merit # `-1` | `Selection merit number cannot be negative.` |
| Text merit number | Merit # `ABC` | `Selection merit number must be a whole number.` |

## Valid Posting and Transfer Data

First create a staff profile and service record. Then search the staff member on the Postings & Transfers page.

| Staff Personal # | First Station | First Start Date | First Reason | Transfer Station | Transfer Date | Transfer Reason |
| --- | --- | --- | --- | --- | --- | --- |
| `DC-ORZ-0001` | `District & Sessions Court Orakzai` | `2014-09-01` | `Initial posting after appointment.` | `Civil Court Kalaya` | `2021-04-15` | `Administrative requirement.` |
| `DC-ORZ-0002` | `Civil Court Hangu Camp` | `2011-03-10` | `Initial posting.` | `District Court Record Branch` | `2019-08-01` | `Record branch workload adjustment.` |
| `DC-ORZ-0003` | `Judicial Complex Orakzai` | `2020-01-15` | `Contract assignment.` | `Copying Agency Branch` | `2022-12-01` | `Temporary branch support.` |

## Invalid Posting and Transfer Tests

| Test | Input | Expected Error |
| --- | --- | --- |
| Posting before service record | Search staff with no service record and add posting | `A service record must exist before posting or transfer.` |
| Blank first station | First Station blank | `Station name is required.` |
| First posting before appointment | Start Date earlier than service First Appointment | `Start date cannot be before date of first appointment.` |
| Add first posting twice | Add a second first posting for same staff | `This staff member already has a current posting. Use transfer instead.` |
| Transfer without first posting | Execute transfer before first posting exists | `No current posting was found. Add the first posting before transfer.` |
| Blank transfer station | New Station blank | `Station name is required.` |
| Transfer before current start date | Transfer Date before current posting Start Date | `Transfer date cannot be before the current posting start date.` |

## Valid Leave Management Data

First create the matching staff profile and service record. Then search the staff member on the Leave Management page.

| Staff Personal # | Leave Year | Start Date | End Date | Calculated Days | Reason | Expected Balance |
| --- | --- | --- | --- | --- | --- | --- |
| `DC-ORZ-0001` | `2026` | `2026-01-01` | `2026-01-05` | `5` | `Family work` | Remaining becomes `20` |
| `DC-ORZ-0002` | `2026` | `2026-03-10` | `2026-03-10` | `1` | `Personal work` | Remaining becomes `24` |
| `DC-ORZ-0003` | `2026` | `2026-07-01` | `2026-07-25` | `25` | `Annual leave` | Remaining becomes `0` |

## Invalid Leave Management Tests

| Test | Input | Expected Error or Result |
| --- | --- | --- |
| No staff selected | Click `Process Leave` before staff search | `Search and select a staff profile before processing leave.` |
| Unknown personal number | Search `UNKNOWN-001` | `No staff profile found for this personal number.` |
| Blank reason | Valid dates but empty reason | `Reason is required.` |
| End date before start | Start `2026-01-05`, End `2026-01-04` | `End date cannot be before start date.` |
| Cross-year leave | Start `2026-12-31`, End `2027-01-01` | `A leave request cannot cross calendar years. Record each year separately.` |
| 26-day request | Start `2026-01-01`, End `2026-01-26` | `Insufficient leave balance.` |
| Exceed remaining balance | Record 5 days, then request 21 more days | `Insufficient leave balance.` and balance remains `20` |
| Same-day leave | Start and End both `2026-03-10` | Saves as `1` day |
| Restart persistence | Record 5 days, restart app, search same staff/year | Remaining still shows `20` |

## Seniority List Testing Data

Use the same designation for multiple active employees to verify official ranking.

| Personal # | Name | Designation | Status | First Appointment | Promotion Date | Merit # | DOB | Expected Rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `DC-ORZ-0101` | `Senior First` | `Junior Clerk` | `Active` | `2010-01-01` | `2018-01-01` | `2` | `1980-01-01` | Earlier appointment ranks higher |
| `DC-ORZ-0102` | `Junior First` | `Junior Clerk` | `Active` | `2012-01-01` | `2016-01-01` | `1` | `1975-01-01` | Later appointment ranks lower |
| `DC-ORZ-0103` | `Promotion Tie A` | `Junior Clerk` | `Active` | `2010-01-01` | `2017-01-01` | `5` | `1982-01-01` | Earlier promotion wins tie |
| `DC-ORZ-0104` | `Promotion Tie B` | `Junior Clerk` | `Active` | `2010-01-01` | `2019-01-01` | `1` | `1970-01-01` | Later promotion ranks lower |
| `DC-ORZ-0105` | `Inactive Sample` | `Junior Clerk` | `Retired` | `2001-01-01` | blank | `1` | `1965-01-01` | Excluded because not Active |
| `DC-ORZ-0106` | `Other Designation` | `Stenographer` | `Active` | `2000-01-01` | blank | `1` | `1960-01-01` | Not mixed into Junior Clerk list |

Note: the UI requires Date of First Appointment for new service records. Missing-appointment exclusion is covered by automated tests and by upgraded/imported data scenarios.

## Seniority List Tests

| Test | Input | Expected Result |
| --- | --- | --- |
| Generate active designation list | Designation `Junior Clerk` | Only Active Junior Clerk records appear |
| Appointment order | Earlier First Appointment vs later First Appointment | Earlier appointment has lower rank number |
| Promotion tie | Same appointment, different promotion dates | Earlier promotion ranks higher |
| Merit tie | Same appointment and promotion, merit `1` vs `5` | Merit `1` ranks higher |
| Age tie | Same appointment, promotion, merit, different DOB | Older employee ranks higher |
| Personal number tie | All other fields same | Lower Personal Number ranks higher |
| Inactive employee | `Retired` or `Suspended` status | Excluded from active seniority list |
| Other designation | Different designation | Not mixed into selected designation |

## Reports and Printing Tests

| Report | Filter | Expected Result |
| --- | --- | --- |
| Individual Staff Profile | Personal # `DC-ORZ-0001` | Preview shows identity, contact, service, posting, and leave summary |
| Leave History | Personal # `DC-ORZ-0001`, Year `2026` | Totals match Leave Management balance |
| Leave History All Years | Personal # `DC-ORZ-0001`, `All Years` | Shows all recorded leave rows |
| Seniority List | Designation `Junior Clerk` | Ranks match Seniority Lists page |
| PDF export | Any valid report | Non-empty PDF file is created |
| Print cancel | Any valid report, click Print then Cancel | No error is shown |
| Unknown personal number | Personal # `UNKNOWN-001` | `No records found for the supplied Personal Number.` |

## Logout Tests

| Test | Expected Result |
| --- | --- |
| Click `Logout` then `Cancel` | Main window remains open |
| Click `Logout` then confirm | Main window closes and login window appears |
| Login again after logout | Application remains stable |
| Repeat login/logout five times | No duplicate windows or event loops |
| Protected action after logout | Requires login again |

## Admin Account Tests

| Test | Input | Expected Result |
| --- | --- | --- |
| Valid login | `admin` / `admin123` | Login succeeds |
| Wrong password | `admin` / `wrongpass` | Login fails |
| Missing username on account update | Username blank | `Username is required.` |
| Short username | Username `ab` | `Username must be at least 3 characters.` |
| Missing current password | Current Password blank | `Current password is required.` |
| Wrong current password | Current Password `wrongpass` | `Current password is incorrect.` |
| Short new password | New Password `short` | `New password must be at least 8 characters.` |
| Password confirmation mismatch | New Password `newpass123`, Confirm `newpass124` | `New password and confirmation do not match.` |

## End-to-End Test Workflow

1. Login with `admin` / `admin123`.
2. Add `DC-ORZ-0001` from the valid staff table. Confirm tehsil can be blank and emergency contact `1155` saves.
3. Try each invalid staff profile test by changing one field at a time.
4. Add a service record for `DC-ORZ-0001`.
5. Try the invalid service record tests, especially designation/BPS mismatch and promotion date before appointment.
6. Add the first posting for `DC-ORZ-0001`.
7. Execute one valid transfer.
8. Try the invalid posting and transfer tests.
9. Open `Leave Management`, search `DC-ORZ-0001`, record 5 days for 2026, and confirm remaining balance becomes 20.
10. Attempt 21 additional leave days and confirm the request is blocked and no failed-history row appears.
11. Open `Seniority Lists`, generate `Junior Clerk`, and confirm active staff ranking is deterministic.
12. Open `Reports & Printing`, preview Individual Profile, Leave History, and Seniority List reports.
13. Export one report to PDF and confirm the file is non-empty.
14. Open Print, cancel the dialog, and confirm no error is shown.
15. Logout, confirm the login screen returns, then login again.

## Automated Verification Commands

From the project root:

```bash
.venv/bin/python -m compileall court_hrms tests main.py
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m black --check .
```
