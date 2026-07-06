from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from court_hrms.models.annual_leave_account import AnnualLeaveAccount
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

    def add_record(self, record: LeaveRecord) -> LeaveRecord:
        self.session.add(record)
        self.session.flush()
        return record

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
