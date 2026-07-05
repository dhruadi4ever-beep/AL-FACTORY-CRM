from __future__ import annotations

import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.inventory_models import InventoryBalance
from app.job_work_models import JobWorkAssignment, JobWorkMovement, JobWorkPaymentLedgerEntry, JobWorkPendingPayment
from app.job_work_schemas import (
    JobWorkAssignmentCreate,
    JobWorkAssignmentResponse,
    JobWorkAssignmentUpdate,
    JobWorkPaymentCreate,
    JobWorkPaymentLedgerResponse,
    JobWorkPendingPaymentResponse,
    JobWorkReturnRequest,
    JobWorkValidationResult,
)
from app.models import MasterRecord

router = APIRouter(prefix="/job-work", tags=["job-work"])


@router.post("", response_model=JobWorkAssignmentResponse, status_code=status.HTTP_201_CREATED)
def create_assignment(payload: JobWorkAssignmentCreate, db: Session = Depends(get_db)):
    validation = validate_assignment(payload, db)
    if not validation.valid:
        raise HTTPException(status_code=400, detail={"errors": validation.errors, "warnings": validation.warnings})

    active_assignment = (
        db.query(JobWorkAssignment)
        .filter(JobWorkAssignment.job_worker_id == payload.job_worker_id)
        .filter(JobWorkAssignment.status == "in_progress")
        .order_by(JobWorkAssignment.assignment_date.desc())
        .first()
    )
    if active_assignment:
        complete_assignment(active_assignment, db, reason="new_assignment", created_by=payload.created_by)

    assignment = JobWorkAssignment(
        assignment_date=payload.assignment_date and datetime.datetime.fromisoformat(payload.assignment_date),
        job_worker_id=payload.job_worker_id,
        item_id=payload.item_id,
        machine_source_id=payload.machine_source_id,
        assigned_bunches=payload.assigned_bunches,
        returned_pcs=payload.returned_pcs,
        pending_bunches=payload.pending_bunches or payload.assigned_bunches,
        status=payload.status,
        notes=payload.notes,
        created_by=payload.created_by,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    adjust_inventory_for_new_assignment(payload.item_id, payload.assigned_bunches, db)
    return serialize_assignment(assignment, db)


@router.get("", response_model=list[JobWorkAssignmentResponse])
def list_assignments(db: Session = Depends(get_db)):
    assignments = db.query(JobWorkAssignment).order_by(JobWorkAssignment.assignment_date.desc()).all()
    return [serialize_assignment(item, db) for item in assignments]


@router.put("/{assignment_id}", response_model=JobWorkAssignmentResponse)
def update_assignment(assignment_id: int, payload: JobWorkAssignmentUpdate, db: Session = Depends(get_db)):
    assignment = db.query(JobWorkAssignment).filter(JobWorkAssignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    for field_name, value in payload.model_dump(exclude_unset=True).items():
        if field_name == "updated_by":
            continue
        if hasattr(assignment, field_name):
            setattr(assignment, field_name, value)

    assignment.updated_by = payload.updated_by
    db.commit()
    db.refresh(assignment)
    return serialize_assignment(assignment, db)


@router.post("/{assignment_id}/manual-return", response_model=JobWorkAssignmentResponse)
def mark_job_work_returned(assignment_id: int, payload: JobWorkReturnRequest, db: Session = Depends(get_db)):
    assignment = db.query(JobWorkAssignment).filter(JobWorkAssignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    if assignment.status == "completed":
        raise HTTPException(status_code=400, detail="Assignment already completed")

    complete_assignment(assignment, db, reason="manual_return", created_by=payload.created_by)
    return serialize_assignment(assignment, db)


@router.get("/pending-payments", response_model=list[JobWorkPendingPaymentResponse])
def list_pending_payments(db: Session = Depends(get_db)):
    payments = db.query(JobWorkPendingPayment).order_by(JobWorkPendingPayment.created_at.desc()).all()
    return [serialize_payment(payment, db) for payment in payments]


@router.post("/pending-payments/{payment_id}/pay", response_model=JobWorkPendingPaymentResponse)
def register_payment(payment_id: int, payload: JobWorkPaymentCreate, db: Session = Depends(get_db)):
    payment = db.query(JobWorkPendingPayment).filter(JobWorkPendingPayment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Pending payment not found")
    if payment.is_finalized:
        raise HTTPException(status_code=400, detail="Payment already finalized")
    if payload.amount_paid <= 0:
        raise HTTPException(status_code=400, detail="Payment amount must be greater than zero")

    payment.amount_paid = min(payment.amount_paid + payload.amount_paid, payment.payable_amount)
    payment.outstanding_balance = max(payment.payable_amount - payment.amount_paid, 0.0)
    payment.status = "paid" if payment.outstanding_balance <= 0 else "partially_paid"
    payment.payment_date = payload.payment_date and datetime.datetime.fromisoformat(payload.payment_date)
    payment.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(payment)

    transaction_type = "full_payment" if payment.outstanding_balance <= 0 else "partial_payment"
    create_payment_ledger_entry(payment, transaction_type=transaction_type, amount=payload.amount_paid, notes=payload.notes, created_by=payload.created_by, db=db)
    return serialize_payment(payment, db)


@router.post("/pending-payments/{payment_id}/finalize", response_model=JobWorkPendingPaymentResponse)
def finalize_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(JobWorkPendingPayment).filter(JobWorkPendingPayment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Pending payment not found")
    if payment.is_finalized:
        raise HTTPException(status_code=400, detail="Payment already finalized")

    payment.is_finalized = True
    payment.status = "finalized"
    payment.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(payment)
    create_payment_ledger_entry(payment, transaction_type="payment_finalization", amount=payment.amount_paid, notes="Payment finalized", created_by="admin", db=db)
    return serialize_payment(payment, db)


@router.get("/pending-payments/{payment_id}/ledger", response_model=list[JobWorkPaymentLedgerResponse])
def payment_ledger(payment_id: int, db: Session = Depends(get_db)):
    entries = db.query(JobWorkPaymentLedgerEntry).filter(JobWorkPaymentLedgerEntry.payment_id == payment_id).order_by(JobWorkPaymentLedgerEntry.transaction_date.desc()).all()
    return [serialize_ledger(entry) for entry in entries]


@router.get("/validation", response_model=JobWorkValidationResult)
def validate_job_work(payload: JobWorkAssignmentCreate, db: Session = Depends(get_db)):
    return validate_assignment(payload, db)


def validate_assignment(payload: JobWorkAssignmentCreate, db: Session) -> JobWorkValidationResult:
    warnings: list[str] = []
    errors: list[str] = []

    worker = db.query(MasterRecord).filter(MasterRecord.id == payload.job_worker_id).first()
    item = db.query(MasterRecord).filter(MasterRecord.id == payload.item_id).first()
    if not worker or not worker.is_active:
        errors.append("Job worker must be active")
    if not item or not item.is_active:
        errors.append("Item must be active")
    if payload.assigned_bunches <= 0:
        errors.append("Assigned quantity must be greater than zero")
    if payload.assigned_bunches != int(payload.assigned_bunches):
        errors.append("Bunch assignments must be whole numbers")

    if payload.assigned_bunches > 100:
        warnings.append("Large assignment quantity")

    return JobWorkValidationResult(valid=len(errors) == 0, warnings=warnings, errors=errors)


def complete_assignment(assignment: JobWorkAssignment, db: Session, reason: str, created_by: str | None) -> None:
    if assignment.status == "completed":
        return

    conversion = get_item_conversion(assignment.item_id, db)
    returned_bunches = assignment.assigned_bunches
    total_strips = returned_bunches * conversion["strips_per_bunch"]
    payable_amount = total_strips * conversion["job_work_rate_per_strip"]
    finished_pcs = returned_bunches * conversion["pcs_per_bunch"]

    payment = JobWorkPendingPayment(
        assignment_id=assignment.id,
        job_worker_id=assignment.job_worker_id,
        item_id=assignment.item_id,
        returned_bunches=returned_bunches,
        total_strips=total_strips,
        job_work_rate=conversion["job_work_rate_per_strip"],
        payable_amount=payable_amount,
        amount_paid=0.0,
        outstanding_balance=payable_amount,
        status="pending",
        remarks=f"Completed via {reason}",
        created_by=created_by,
    )
    db.add(payment)
    db.flush()

    assignment.returned_pcs = finished_pcs
    assignment.pending_bunches = 0.0
    assignment.status = "completed"
    assignment.completed_at = datetime.datetime.utcnow()
    assignment.completed_by = created_by
    assignment.completion_reason = reason
    assignment.payment_record_id = payment.id
    db.add(assignment)

    movement = JobWorkMovement(
        assignment_id=assignment.id,
        movement_type=reason,
        bunches=returned_bunches,
        pcs=finished_pcs,
        movement_date=datetime.datetime.utcnow(),
        notes=f"Assignment completed via {reason}",
    )
    db.add(movement)

    adjust_inventory_for_completion(assignment.item_id, returned_bunches, finished_pcs, db)
    create_payment_ledger_entry(payment, transaction_type="pending_payment_created", amount=payable_amount, notes=f"Pending payment created for {reason}", created_by=created_by, db=db)


def adjust_inventory_for_new_assignment(item_id: int, assigned_bunches: float, db: Session) -> None:
    balance = db.query(InventoryBalance).filter(InventoryBalance.item_id == item_id).first()
    if not balance:
        balance = InventoryBalance(item_id=item_id)
        db.add(balance)
    balance.produced_inventory = max(balance.produced_inventory - assigned_bunches, 0.0)
    balance.job_work_in_progress = balance.job_work_in_progress + assigned_bunches
    db.commit()


def adjust_inventory_for_completion(item_id: int, assigned_bunches: float, finished_pcs: float, db: Session) -> None:
    balance = db.query(InventoryBalance).filter(InventoryBalance.item_id == item_id).first()
    if not balance:
        balance = InventoryBalance(item_id=item_id)
        db.add(balance)
    balance.job_work_in_progress = max(balance.job_work_in_progress - assigned_bunches, 0.0)
    balance.finished_goods = balance.finished_goods + finished_pcs
    db.commit()


def create_payment_ledger_entry(payment: JobWorkPendingPayment, transaction_type: str, amount: float, notes: str | None, created_by: str | None, db: Session) -> None:
    entry = JobWorkPaymentLedgerEntry(
        payment_id=payment.id,
        transaction_type=transaction_type,
        transaction_date=datetime.datetime.utcnow(),
        amount=amount,
        balance_after=payment.outstanding_balance,
        notes=notes,
        created_by=created_by,
    )
    db.add(entry)
    db.commit()


def get_item_conversion(item_id: int, db: Session) -> dict[str, float]:
    item = db.query(MasterRecord).filter(MasterRecord.id == item_id).first()
    metadata = item.metadata if item else {}
    return {
        "strips_per_bunch": float(metadata.get("strips_per_bunch", 0) or 0),
        "pcs_per_bunch": float(metadata.get("pcs_per_bunch", 0) or 0),
        "job_work_rate_per_strip": float(metadata.get("job_work_rate_per_strip", 0) or 0),
    }


def serialize_assignment(assignment: JobWorkAssignment, db: Session) -> JobWorkAssignmentResponse:
    job_worker = db.query(MasterRecord).filter(MasterRecord.id == assignment.job_worker_id).first()
    item = db.query(MasterRecord).filter(MasterRecord.id == assignment.item_id).first()
    machine_source = db.query(MasterRecord).filter(MasterRecord.id == assignment.machine_source_id).first() if assignment.machine_source_id else None
    return JobWorkAssignmentResponse(
        id=assignment.id,
        assignment_date=assignment.assignment_date.isoformat() if assignment.assignment_date else None,
        job_worker_id=assignment.job_worker_id,
        item_id=assignment.item_id,
        machine_source_id=assignment.machine_source_id,
        assigned_bunches=assignment.assigned_bunches,
        returned_pcs=assignment.returned_pcs,
        pending_bunches=assignment.pending_bunches,
        status=assignment.status,
        notes=assignment.notes,
        created_by=assignment.created_by,
        created_at=assignment.created_at.isoformat(),
        updated_at=assignment.updated_at.isoformat(),
        job_worker_code=job_worker.code if job_worker else None,
        item_code=item.code if item else None,
        machine_source_code=machine_source.code if machine_source else None,
    )


def serialize_payment(payment: JobWorkPendingPayment, db: Session) -> JobWorkPendingPaymentResponse:
    job_worker = db.query(MasterRecord).filter(MasterRecord.id == payment.job_worker_id).first()
    item = db.query(MasterRecord).filter(MasterRecord.id == payment.item_id).first()
    return JobWorkPendingPaymentResponse(
        id=payment.id,
        assignment_id=payment.assignment_id,
        job_worker_id=payment.job_worker_id,
        item_id=payment.item_id,
        returned_bunches=payment.returned_bunches,
        total_strips=payment.total_strips,
        job_work_rate=payment.job_work_rate,
        payable_amount=payment.payable_amount,
        amount_paid=payment.amount_paid,
        outstanding_balance=payment.outstanding_balance,
        status=payment.status,
        payment_date=payment.payment_date.isoformat() if payment.payment_date else None,
        is_finalized=payment.is_finalized,
        remarks=payment.remarks,
        created_at=payment.created_at.isoformat(),
        updated_at=payment.updated_at.isoformat(),
        job_worker_code=job_worker.code if job_worker else None,
        item_code=item.code if item else None,
    )


def serialize_ledger(entry: JobWorkPaymentLedgerEntry) -> JobWorkPaymentLedgerResponse:
    return JobWorkPaymentLedgerResponse(
        id=entry.id,
        payment_id=entry.payment_id,
        transaction_type=entry.transaction_type,
        transaction_date=entry.transaction_date.isoformat(),
        amount=entry.amount,
        balance_after=entry.balance_after,
        notes=entry.notes,
        created_by=entry.created_by,
    )
