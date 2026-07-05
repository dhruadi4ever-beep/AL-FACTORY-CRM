from __future__ import annotations

import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.business_validation import BusinessRuleEngine, ValidationContext
from app.database import get_db
from app.models import MasterRecord
from app.payroll_models import (
    EmployeeAttendance,
    EmployeeSalaryAdvance,
    MachineAssignmentHistory,
    SalaryAdvanceDeduction,
    SalaryLedgerEntry,
    WeeklySalaryCycle,
)
from app.payroll_schemas import (
    AdvanceDeductionCreate,
    AttendanceCreate,
    AttendanceResponse,
    AttendanceUpdate,
    MachineAssignmentHistoryResponse,
    SalaryAdvanceCreate,
    SalaryAdvanceResponse,
    SalaryLedgerEntryResponse,
    WeeklySalaryCycleResponse,
)

router = APIRouter(prefix="/payroll", tags=["payroll"])


@router.post("/attendance", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
def create_attendance(payload: AttendanceCreate, db: Session = Depends(get_db)):
    employee = db.query(MasterRecord).filter(MasterRecord.id == payload.employee_id).first()
    if not employee or not employee.is_active:
        raise HTTPException(status_code=404, detail="Employee not found or inactive")

    engine = BusinessRuleEngine()
    try:
        attendance = engine.execute(
            db,
            ValidationContext(
                entity_type="attendance",
                actor=payload.created_by or "system",
                payload=payload.model_dump(),
                input_validator=lambda data: [] if data.get("working_hours", 0) > 0 else ["Working hours must be greater than zero"],
                master_validator=lambda context: [],
                business_rule_validator=lambda context: [],
                inventory_validator=lambda context: [],
                persister=lambda context: EmployeeAttendance(
                    attendance_date=payload.attendance_date and datetime.datetime.fromisoformat(payload.attendance_date),
                    employee_id=payload.employee_id,
                    working_hours=payload.working_hours,
                    attendance_status=payload.attendance_status,
                    remarks=payload.remarks,
                    created_by=payload.created_by,
                ),
                metadata={"master_refs": [{"id": payload.employee_id, "label": "employee"}]},
                pre_save_handler=lambda session, ctx, entity: create_ledger_entry(employee_id=payload.employee_id, transaction_type="attendance_entry", amount=payload.working_hours, reference_type="attendance", reference_id=entity.id, notes=payload.remarks, created_by=payload.created_by, db=session),
            ),
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return serialize_attendance(attendance)


@router.get("/attendance", response_model=list[AttendanceResponse])
def list_attendance(db: Session = Depends(get_db)):
    attendances = db.query(EmployeeAttendance).order_by(EmployeeAttendance.attendance_date.desc()).all()
    return [serialize_attendance(item) for item in attendances]


@router.put("/attendance/{attendance_id}", response_model=AttendanceResponse)
def update_attendance(attendance_id: int, payload: AttendanceUpdate, db: Session = Depends(get_db)):
    attendance = db.query(EmployeeAttendance).filter(EmployeeAttendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    if attendance.is_locked:
        raise HTTPException(status_code=400, detail="Attendance is locked after salary finalization")

    for field_name, value in payload.model_dump(exclude_unset=True).items():
        if field_name == "updated_by":
            continue
        if hasattr(attendance, field_name):
            setattr(attendance, field_name, value)
    attendance.updated_by = payload.updated_by
    db.commit()
    db.refresh(attendance)
    return serialize_attendance(attendance)


@router.post("/advances", response_model=SalaryAdvanceResponse, status_code=status.HTTP_201_CREATED)
def create_advance(payload: SalaryAdvanceCreate, db: Session = Depends(get_db)):
    employee = db.query(MasterRecord).filter(MasterRecord.id == payload.employee_id).first()
    if not employee or not employee.is_active:
        raise HTTPException(status_code=404, detail="Employee not found or inactive")

    engine = BusinessRuleEngine()
    try:
        advance = engine.execute(
            db,
            ValidationContext(
                entity_type="salary_advance",
                actor=payload.created_by or "system",
                payload=payload.model_dump(),
                input_validator=lambda data: [] if data.get("advance_amount", 0) > 0 else ["Advance amount must be greater than zero"],
                master_validator=lambda context: [],
                business_rule_validator=lambda context: [],
                inventory_validator=lambda context: [],
                persister=lambda context: EmployeeSalaryAdvance(
                    advance_date=payload.advance_date and datetime.datetime.fromisoformat(payload.advance_date),
                    employee_id=payload.employee_id,
                    advance_amount=payload.advance_amount,
                    remarks=payload.remarks,
                    created_by=payload.created_by,
                ),
                metadata={"master_refs": [{"id": payload.employee_id, "label": "employee"}]},
                pre_save_handler=lambda session, ctx, entity: create_ledger_entry(employee_id=payload.employee_id, transaction_type="salary_advance", amount=payload.advance_amount, reference_type="advance", reference_id=entity.id, notes=payload.remarks, created_by=payload.created_by, db=session),
            ),
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return serialize_advance(advance)


@router.get("/advances", response_model=list[SalaryAdvanceResponse])
def list_advances(db: Session = Depends(get_db)):
    advances = db.query(EmployeeSalaryAdvance).order_by(EmployeeSalaryAdvance.advance_date.desc()).all()
    return [serialize_advance(item) for item in advances]


@router.post("/cycles", response_model=WeeklySalaryCycleResponse, status_code=status.HTTP_201_CREATED)
def create_salary_cycle(payload: dict, db: Session = Depends(get_db)):
    employee_id = payload.get("employee_id")
    start_date = payload.get("start_date")
    end_date = payload.get("end_date")
    hourly_rate = payload.get("hourly_rate", 0.0)

    employee = db.query(MasterRecord).filter(MasterRecord.id == employee_id).first()
    if not employee or not employee.is_active:
        raise HTTPException(status_code=404, detail="Employee not found or inactive")

    attendances = (
        db.query(EmployeeAttendance)
        .filter(EmployeeAttendance.employee_id == employee_id)
        .filter(EmployeeAttendance.attendance_date >= datetime.datetime.fromisoformat(start_date))
        .filter(EmployeeAttendance.attendance_date <= datetime.datetime.fromisoformat(end_date))
        .all()
    )

    working_days = sum(1 for attendance in attendances if attendance.attendance_status == "present")
    total_working_hours = sum(attendance.working_hours for attendance in attendances)
    gross_salary = total_working_hours * hourly_rate

    cycle = WeeklySalaryCycle(
        employee_id=employee_id,
        start_date=datetime.datetime.fromisoformat(start_date),
        end_date=datetime.datetime.fromisoformat(end_date),
        working_days=working_days,
        total_working_hours=total_working_hours,
        hourly_rate=hourly_rate,
        gross_salary=gross_salary,
        status="draft",
        created_by="admin",
    )
    db.add(cycle)
    db.commit()
    db.refresh(cycle)
    create_ledger_entry(employee_id=employee_id, transaction_type="salary_calculation", amount=gross_salary, reference_type="salary_cycle", reference_id=cycle.id, notes="Weekly salary prepared", created_by="admin", db=db)
    return serialize_cycle(cycle)


@router.post("/cycles/{cycle_id}/finalize", response_model=WeeklySalaryCycleResponse)
def finalize_cycle(cycle_id: int, db: Session = Depends(get_db)):
    cycle = db.query(WeeklySalaryCycle).filter(WeeklySalaryCycle.id == cycle_id).first()
    if not cycle:
        raise HTTPException(status_code=404, detail="Salary cycle not found")
    if cycle.status == "finalized":
        raise HTTPException(status_code=400, detail="Salary cycle already finalized")

    cycle.status = "finalized"
    cycle.finalization_date = datetime.datetime.utcnow()
    db.commit()
    db.refresh(cycle)
    create_ledger_entry(employee_id=cycle.employee_id, transaction_type="salary_finalization", amount=cycle.gross_salary, reference_type="salary_cycle", reference_id=cycle.id, notes="Weekly salary finalized", created_by="admin", db=db)
    return serialize_cycle(cycle)


@router.post("/cycles/{cycle_id}/deductions", response_model=dict)
def create_deduction(cycle_id: int, payload: AdvanceDeductionCreate, db: Session = Depends(get_db)):
    cycle = db.query(WeeklySalaryCycle).filter(WeeklySalaryCycle.id == cycle_id).first()
    if not cycle:
        raise HTTPException(status_code=404, detail="Salary cycle not found")
    advance = db.query(EmployeeSalaryAdvance).filter(EmployeeSalaryAdvance.id == payload.advance_id).first()
    if not advance:
        raise HTTPException(status_code=404, detail="Advance not found")

    deduction = SalaryAdvanceDeduction(
        salary_cycle_id=cycle_id,
        advance_id=payload.advance_id,
        deduction_amount=payload.deduction_amount,
        remarks=payload.remarks,
    )
    db.add(deduction)
    advance.is_settled = payload.deduction_amount >= advance.advance_amount
    db.commit()
    create_ledger_entry(employee_id=advance.employee_id, transaction_type="manual_advance_deduction", amount=payload.deduction_amount, reference_type="salary_cycle", reference_id=cycle_id, notes=payload.remarks, created_by="admin", db=db)
    return {"status": "ok", "deduction_id": deduction.id}


@router.get("/cycles/{cycle_id}/ledger", response_model=list[SalaryLedgerEntryResponse])
def list_ledger(cycle_id: int, db: Session = Depends(get_db)):
    entries = db.query(SalaryLedgerEntry).filter(SalaryLedgerEntry.reference_id == cycle_id, SalaryLedgerEntry.reference_type == "salary_cycle").order_by(SalaryLedgerEntry.entry_date.desc()).all()
    return [serialize_ledger(entry) for entry in entries]


@router.post("/machine-assignments", response_model=MachineAssignmentHistoryResponse, status_code=status.HTTP_201_CREATED)
def create_machine_assignment(payload: dict, db: Session = Depends(get_db)):
    employee = db.query(MasterRecord).filter(MasterRecord.id == payload.get("employee_id")).first()
    if not employee or not employee.is_active:
        raise HTTPException(status_code=404, detail="Employee not found or inactive")

    assignment = MachineAssignmentHistory(
        assignment_date=payload.get("assignment_date") and datetime.datetime.fromisoformat(payload.get("assignment_date")),
        employee_id=payload.get("employee_id"),
        machine_id=payload.get("machine_id"),
        working_hours=payload.get("working_hours", 0.0),
        notes=payload.get("notes"),
        created_by=payload.get("created_by"),
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return serialize_machine_assignment(assignment)


@router.get("/machine-assignments", response_model=list[MachineAssignmentHistoryResponse])
def list_machine_assignments(db: Session = Depends(get_db)):
    assignments = db.query(MachineAssignmentHistory).order_by(MachineAssignmentHistory.assignment_date.desc()).all()
    return [serialize_machine_assignment(item) for item in assignments]


def create_ledger_entry(employee_id: int, transaction_type: str, amount: float, reference_type: str | None, reference_id: int | None, notes: str | None, created_by: str | None, db: Session) -> None:
    entry = SalaryLedgerEntry(
        entry_date=datetime.datetime.utcnow(),
        employee_id=employee_id,
        transaction_type=transaction_type,
        amount=amount,
        reference_type=reference_type,
        reference_id=reference_id,
        notes=notes,
        created_by=created_by,
    )
    db.add(entry)
    db.commit()


def serialize_attendance(attendance: EmployeeAttendance) -> AttendanceResponse:
    return AttendanceResponse(
        id=attendance.id,
        attendance_date=attendance.attendance_date.isoformat() if attendance.attendance_date else None,
        employee_id=attendance.employee_id,
        working_hours=attendance.working_hours,
        attendance_status=attendance.attendance_status,
        remarks=attendance.remarks,
        is_locked=attendance.is_locked,
        created_at=attendance.created_at.isoformat(),
        updated_at=attendance.updated_at.isoformat(),
        created_by=attendance.created_by,
        updated_by=attendance.updated_by,
    )


def serialize_advance(advance: EmployeeSalaryAdvance) -> SalaryAdvanceResponse:
    return SalaryAdvanceResponse(
        id=advance.id,
        advance_date=advance.advance_date.isoformat() if advance.advance_date else None,
        employee_id=advance.employee_id,
        advance_amount=advance.advance_amount,
        remarks=advance.remarks,
        is_settled=advance.is_settled,
        created_at=advance.created_at.isoformat(),
        updated_at=advance.updated_at.isoformat(),
        created_by=advance.created_by,
    )


def serialize_cycle(cycle: WeeklySalaryCycle) -> WeeklySalaryCycleResponse:
    return WeeklySalaryCycleResponse(
        id=cycle.id,
        employee_id=cycle.employee_id,
        start_date=cycle.start_date.isoformat(),
        end_date=cycle.end_date.isoformat(),
        working_days=cycle.working_days,
        total_working_hours=cycle.total_working_hours,
        hourly_rate=cycle.hourly_rate,
        gross_salary=cycle.gross_salary,
        status=cycle.status,
        finalization_date=cycle.finalization_date.isoformat() if cycle.finalization_date else None,
        remarks=cycle.remarks,
        created_at=cycle.created_at.isoformat(),
        updated_at=cycle.updated_at.isoformat(),
    )


def serialize_ledger(entry: SalaryLedgerEntry) -> SalaryLedgerEntryResponse:
    return SalaryLedgerEntryResponse(
        id=entry.id,
        entry_date=entry.entry_date.isoformat(),
        employee_id=entry.employee_id,
        transaction_type=entry.transaction_type,
        amount=entry.amount,
        reference_type=entry.reference_type,
        reference_id=entry.reference_id,
        notes=entry.notes,
        created_by=entry.created_by,
    )


def serialize_machine_assignment(assignment: MachineAssignmentHistory) -> MachineAssignmentHistoryResponse:
    return MachineAssignmentHistoryResponse(
        id=assignment.id,
        assignment_date=assignment.assignment_date.isoformat(),
        employee_id=assignment.employee_id,
        machine_id=assignment.machine_id,
        working_hours=assignment.working_hours,
        notes=assignment.notes,
        created_by=assignment.created_by,
    )
