from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class JobWorkAssignmentCreate(BaseModel):
    assignment_date: Optional[str] = None
    job_worker_id: int
    item_id: int
    machine_source_id: Optional[int] = None
    assigned_bunches: float
    returned_pcs: float = 0.0
    pending_bunches: float = 0.0
    status: str = "in_progress"
    notes: Optional[str] = None
    created_by: Optional[str] = None


class JobWorkAssignmentUpdate(BaseModel):
    job_worker_id: Optional[int] = None
    item_id: Optional[int] = None
    machine_source_id: Optional[int] = None
    assigned_bunches: Optional[float] = None
    returned_pcs: Optional[float] = None
    pending_bunches: Optional[float] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    updated_by: Optional[str] = None


class JobWorkAssignmentResponse(JobWorkAssignmentCreate):
    id: int
    created_at: str
    updated_at: str
    job_worker_code: Optional[str] = None
    item_code: Optional[str] = None
    machine_source_code: Optional[str] = None

    class Config:
        from_attributes = True


class JobWorkValidationResult(BaseModel):
    valid: bool
    warnings: list[str]
    errors: list[str]


class JobWorkReturnRequest(BaseModel):
    confirmed: bool = True
    notes: Optional[str] = None
    created_by: Optional[str] = None


class JobWorkPendingPaymentResponse(BaseModel):
    id: int
    assignment_id: int
    job_worker_id: int
    item_id: int
    returned_bunches: float
    total_strips: float
    job_work_rate: float
    payable_amount: float
    amount_paid: float
    outstanding_balance: float
    status: str
    payment_date: Optional[str] = None
    is_finalized: bool
    remarks: Optional[str] = None
    created_at: str
    updated_at: str
    job_worker_code: Optional[str] = None
    item_code: Optional[str] = None

    class Config:
        from_attributes = True


class JobWorkPaymentCreate(BaseModel):
    payment_date: Optional[str] = None
    amount_paid: float
    notes: Optional[str] = None
    created_by: Optional[str] = None


class JobWorkPaymentLedgerResponse(BaseModel):
    id: int
    payment_id: int
    transaction_type: str
    transaction_date: str
    amount: float
    balance_after: float
    notes: Optional[str] = None
    created_by: Optional[str] = None

    class Config:
        from_attributes = True
