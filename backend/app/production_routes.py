from __future__ import annotations

import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.business_validation import BusinessRuleEngine, ValidationContext
from app.database import get_db
from app.models import MasterRecord
from app.production_models import ProducedInventoryBalance, ProductionRecord
from app.production_schemas import (
    ProducedInventorySummary,
    ProductionEntryCreate,
    ProductionEntryResponse,
    ProductionEntryUpdate,
    ProductionValidationResult,
)

router = APIRouter(prefix="/production", tags=["production"])


@router.post("", response_model=ProductionEntryResponse, status_code=status.HTTP_201_CREATED)
def create_production_entry(payload: ProductionEntryCreate, db: Session = Depends(get_db)):
    validation = validate_production(payload, db)
    if not validation.valid:
        raise HTTPException(status_code=400, detail={"errors": validation.errors, "warnings": validation.warnings})

    engine = BusinessRuleEngine()
    try:
        entry = engine.execute(
            db,
            ValidationContext(
                entity_type="production_record",
                actor=payload.created_by or "system",
                payload=payload.model_dump(),
                input_validator=lambda data: [],
                master_validator=lambda context: [],
                business_rule_validator=lambda context: [],
                inventory_validator=lambda context: [],
                persister=lambda context: ProductionRecord(
                    production_date=payload.production_date and datetime.datetime.fromisoformat(payload.production_date),
                    machine_id=payload.machine_id,
                    item_id=payload.item_id,
                    employee_id=payload.employee_id,
                    bunches=payload.bunches,
                    entry_timestamp=payload.entry_timestamp and datetime.datetime.fromisoformat(payload.entry_timestamp),
                    status=payload.status,
                    notes=payload.notes,
                    created_by=payload.created_by,
                ),
                metadata={"master_refs": [{"id": payload.machine_id, "label": "machine"}, {"id": payload.item_id, "label": "item"}]},
                pre_save_handler=lambda session, ctx, entity: update_inventory_balance(payload.item_id, payload.bunches, payload.status, session),
            ),
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    db.refresh(entry)
    return serialize_production(entry, db)


@router.get("", response_model=list[ProductionEntryResponse])
def list_entries(db: Session = Depends(get_db)):
    entries = db.query(ProductionRecord).order_by(ProductionRecord.production_date.desc(), ProductionRecord.entry_timestamp.desc()).all()
    return [serialize_production(entry, db) for entry in entries]


@router.get("/validation", response_model=ProductionValidationResult)
def validate_production_entry(payload: ProductionEntryCreate, db: Session = Depends(get_db)):
    return validate_production(payload, db)


@router.get("/inventory", response_model=list[ProducedInventorySummary])
def list_inventory(db: Session = Depends(get_db)):
    balances = db.query(ProducedInventoryBalance).all()
    return [serialize_balance(balance, db) for balance in balances]


@router.put("/{entry_id}", response_model=ProductionEntryResponse)
def update_entry(entry_id: int, payload: ProductionEntryUpdate, db: Session = Depends(get_db)):
    entry = db.query(ProductionRecord).filter(ProductionRecord.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Production entry not found")
    if entry.is_locked:
        raise HTTPException(status_code=400, detail="Production entry is locked")

    for field_name, value in payload.model_dump(exclude_unset=True).items():
        if field_name == "updated_by":
            continue
        if hasattr(entry, field_name):
            setattr(entry, field_name, value)

    entry.updated_by = payload.updated_by
    db.commit()
    db.refresh(entry)
    return serialize_production(entry, db)


@router.post("/{entry_id}/lock", response_model=ProductionEntryResponse)
def lock_entry(entry_id: int, db: Session = Depends(get_db)):
    entry = db.query(ProductionRecord).filter(ProductionRecord.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Production entry not found")
    entry.is_locked = True
    db.commit()
    db.refresh(entry)
    return serialize_production(entry, db)


def validate_production(payload: ProductionEntryCreate, db: Session) -> ProductionValidationResult:
    warnings: list[str] = []
    errors: list[str] = []

    machine = db.query(MasterRecord).filter(MasterRecord.id == payload.machine_id).first()
    item = db.query(MasterRecord).filter(MasterRecord.id == payload.item_id).first()

    if not machine or not machine.is_active:
        errors.append("Machine must be active")
    if not item or not item.is_active:
        errors.append("Item must be active")
    if payload.bunches <= 0:
        errors.append("Production quantity must be greater than zero")

    if payload.bunches > 200:
        warnings.append("Entered production is significantly higher than expected forecast. Please verify before saving.")

    return ProductionValidationResult(valid=len(errors) == 0, warnings=warnings, errors=errors)


def update_inventory_balance(item_id: int, bunches: float, status: str, db: Session) -> None:
    balance = db.query(ProducedInventoryBalance).filter(ProducedInventoryBalance.item_id == item_id).first()
    if not balance:
        balance = ProducedInventoryBalance(item_id=item_id)
        db.add(balance)
    balance.total_bunches += bunches
    if status == "available":
        balance.available_bunches += bunches
    elif status == "partially_assigned":
        balance.partially_assigned_bunches += bunches
    elif status == "fully_assigned":
        balance.fully_assigned_bunches += bunches


def serialize_production(entry: ProductionRecord, db: Session) -> ProductionEntryResponse:
    machine = db.query(MasterRecord).filter(MasterRecord.id == entry.machine_id).first()
    item = db.query(MasterRecord).filter(MasterRecord.id == entry.item_id).first()
    employee = db.query(MasterRecord).filter(MasterRecord.id == entry.employee_id).first() if entry.employee_id else None
    return ProductionEntryResponse(
        id=entry.id,
        production_date=entry.production_date.isoformat() if entry.production_date else None,
        machine_id=entry.machine_id,
        item_id=entry.item_id,
        employee_id=entry.employee_id,
        bunches=entry.bunches,
        entry_timestamp=entry.entry_timestamp.isoformat() if entry.entry_timestamp else None,
        status=entry.status,
        notes=entry.notes,
        created_by=entry.created_by,
        is_locked=entry.is_locked,
        created_at=entry.created_at.isoformat(),
        updated_at=entry.updated_at.isoformat(),
        machine_code=machine.code if machine else None,
        item_code=item.code if item else None,
        employee_code=employee.code if employee else None,
    )


def serialize_balance(balance: ProducedInventoryBalance, db: Session) -> ProducedInventorySummary:
    item = db.query(MasterRecord).filter(MasterRecord.id == balance.item_id).first()
    return ProducedInventorySummary(
        item_id=balance.item_id,
        item_code=item.code if item else None,
        item_name=item.name if item else None,
        total_bunches=balance.total_bunches,
        available_bunches=balance.available_bunches,
        partially_assigned_bunches=balance.partially_assigned_bunches,
        fully_assigned_bunches=balance.fully_assigned_bunches,
    )
