from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class AttendanceCreate(BaseModel):
    attendance_date: Optional[str] = None
    employee_id: int
    working_hours: float
    attendance_status: str = "present"
    remarks: Optional[str] = None
    created_by: Optional[str] = None


class AttendanceResponse(AttendanceCreate):
    id: int
    is_locked: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class AttendanceUpdate(BaseModel):
    working_hours: Optional[float] = None
    attendance_status: Optional[str] = None
    remarks: Optional[str] = None
    updated_by: Optional[str] = None


class SalaryAdvanceCreate(BaseModel):
    advance_date: Optional[str] = None
    employee_id: int
    advance_amount: float
    remarks: Optional[str] = None
    created_by: Optional[str] = None


class SalaryAdvanceResponse(SalaryAdvanceCreate):
    id: int
    is_settled: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class WeeklySalaryCycleResponse(BaseModel):
    id: int
    employee_id: int
    start_date: str
    end_date: str
    working_days: int
    total_working_hours: float
    hourly_rate: float
    gross_salary: float
    status: str
    finalization_date: Optional[str] = None
    remarks: Optional[str] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class AdvanceDeductionCreate(BaseModel):
    advance_id: int
    deduction_amount: float
    remarks: Optional[str] = None


class SalaryLedgerEntryResponse(BaseModel):
    id: int
    entry_date: str
    employee_id: int
    transaction_type: str
    amount: float
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    notes: Optional[str] = None
    created_by: Optional[str] = None

    class Config:
        from_attributes = True


class MachineAssignmentHistoryResponse(BaseModel):
    id: int
    assignment_date: str
    employee_id: int
    machine_id: int
    working_hours: float
    notes: Optional[str] = None
    created_by: Optional[str] = None

    class Config:
        from_attributes = True
