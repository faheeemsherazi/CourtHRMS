from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from court_hrms.models.annual_leave_account import AnnualLeaveAccount
from court_hrms.models.leave_ledger import LeaveLedgerEntry
from court_hrms.models.leave_policy import LeavePolicy, LeaveType
from court_hrms.models.leave_record import LeaveRecord


class LeaveRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_account(self, staff_id: int, leave_year: int) -> AnnualLeaveAccount | None:
        stmt = select(AnnualLeaveAccount).where(
            AnnualLeaveAccount.staff_id == staff_id,
            AnnualLeaveAccount.leave_year == leave_year,
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def add_account(self, account: AnnualLeaveAccount) -> AnnualLeaveAccount:
        self.session.add(account)
        self.session.flush()
        return account

    def get_or_create_account(
        self,
        staff_id: int,
        leave_year: int,
        entitlement_days: int,
    ) -> AnnualLeaveAccount:
        account = self.get_account(staff_id, leave_year)
        if account is not None:
            return account

        account = AnnualLeaveAccount(
            staff_id=staff_id,
            leave_year=leave_year,
            entitlement_days=entitlement_days,
            availed_days=0,
        )
        return self.add_account(account)

    def get_legacy_annual_leave_type(self) -> LeaveType | None:
        stmt = select(LeaveType).where(
            LeaveType.code == "ANNUAL_LEGACY",
            LeaveType.is_active.is_(True),
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def get_active_legacy_policy(self, leave_year: int) -> LeavePolicy | None:
        stmt = (
            select(LeavePolicy)
            .join(LeaveType, LeavePolicy.leave_type_id == LeaveType.id)
            .where(
                LeaveType.code == "ANNUAL_LEGACY",
                LeaveType.is_active.is_(True),
                LeavePolicy.is_active.is_(True),
                (LeavePolicy.leave_year.is_(None))
                | (LeavePolicy.leave_year == leave_year),
            )
            .order_by(LeavePolicy.leave_year.desc().nullslast(), LeavePolicy.id.desc())
            .limit(1)
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def add_record(self, record: LeaveRecord) -> LeaveRecord:
        self.session.add(record)
        self.session.flush()
        return record

    def add_ledger_entry(self, entry: LeaveLedgerEntry) -> LeaveLedgerEntry:
        self.session.add(entry)
        self.session.flush()
        return entry

    def list_ledger_entries(
        self,
        staff_id: int,
        leave_year: int | None = None,
    ) -> list[LeaveLedgerEntry]:
        stmt = (
            select(LeaveLedgerEntry)
            .where(LeaveLedgerEntry.staff_id == staff_id)
            .order_by(LeaveLedgerEntry.entry_date.asc(), LeaveLedgerEntry.id.asc())
        )
        if leave_year is not None:
            stmt = stmt.where(
                LeaveLedgerEntry.entry_date >= date(leave_year, 1, 1),
                LeaveLedgerEntry.entry_date <= date(leave_year, 12, 31),
            )
        return list(self.session.execute(stmt).scalars().all())

    def list_accounts_for_staff(self, staff_id: int) -> list[AnnualLeaveAccount]:
        stmt = (
            select(AnnualLeaveAccount)
            .where(AnnualLeaveAccount.staff_id == staff_id)
            .order_by(AnnualLeaveAccount.leave_year.desc())
        )
        return list(self.session.execute(stmt).scalars().all())

    def list_records_for_staff(
        self,
        staff_id: int,
        leave_year: int | None = None,
    ) -> list[LeaveRecord]:
        stmt = (
            select(LeaveRecord)
            .options(
                joinedload(LeaveRecord.leave_account),
                joinedload(LeaveRecord.processed_by_admin),
            )
            .join(
                AnnualLeaveAccount,
                LeaveRecord.leave_account_id == AnnualLeaveAccount.id,
            )
            .where(LeaveRecord.staff_id == staff_id)
            .order_by(
                LeaveRecord.start_date.desc(),
                LeaveRecord.id.desc(),
            )
        )
        if leave_year is not None:
            stmt = stmt.where(AnnualLeaveAccount.leave_year == leave_year)
        return list(self.session.execute(stmt).scalars().all())
