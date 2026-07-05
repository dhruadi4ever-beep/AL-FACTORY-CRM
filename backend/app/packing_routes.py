from __future__ import annotations

import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.business_validation import BusinessRuleEngine, ValidationContext
from app.database import get_db
from app.models import MasterRecord
from app.packing_models import Parcel, ParcelItem
from app.packing_schemas import ParcelCreate, ParcelItemInput, ParcelItemResponse, ParcelResponse, PackingValidationResult

router = APIRouter(prefix="/packing", tags=["packing"])


@router.post("", response_model=ParcelResponse, status_code=status.HTTP_201_CREATED)
def create_parcel(payload: ParcelCreate, db: Session = Depends(get_db)):
    validation = validate_parcel(payload, db)
    if not validation.valid:
        raise HTTPException(status_code=400, detail={"errors": validation.errors, "warnings": validation.warnings})

    engine = BusinessRuleEngine()
    try:
        parcel = engine.execute(
            db,
            ValidationContext(
                entity_type="parcel",
                actor=payload.created_by or "system",
                payload=payload.model_dump(),
                input_validator=lambda data: [],
                master_validator=lambda context: [],
                business_rule_validator=lambda context: [],
                inventory_validator=lambda context: [],
                persister=lambda context: Parcel(
                    parcel_date=payload.parcel_date and datetime.datetime.fromisoformat(payload.parcel_date),
                    parcel_code=payload.parcel_code,
                    total_pcs=sum(item.pcs_quantity for item in payload.items),
                    status="packed",
                    notes=payload.notes,
                    created_by=payload.created_by,
                ),
                metadata={"master_refs": [{"id": item_input.item_id, "label": "item"} for item_input in payload.items]},
                post_save_handler=lambda session, ctx, entity: [
                    session.add(
                        ParcelItem(
                            parcel_id=entity.id,
                            item_id=item_input.item_id,
                            pcs_quantity=item_input.pcs_quantity,
                            status="packed",
                        )
                    )
                    for item_input in payload.items
                ],
            ),
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    db.refresh(parcel)
    return serialize_parcel(parcel, db)


@router.get("", response_model=list[ParcelResponse])
def list_parcels(db: Session = Depends(get_db)):
    parcels = db.query(Parcel).order_by(Parcel.parcel_date.desc()).all()
    return [serialize_parcel(parcel, db) for parcel in parcels]


@router.get("/validation", response_model=PackingValidationResult)
def validate_parcel_input(payload: ParcelCreate, db: Session = Depends(get_db)):
    return validate_parcel(payload, db)


def validate_parcel(payload: ParcelCreate, db: Session) -> PackingValidationResult:
    warnings: list[str] = []
    errors: list[str] = []

    if not payload.parcel_code:
        errors.append("Parcel code is required")

    if not payload.items:
        errors.append("At least one item is required")

    for item_input in payload.items:
        item = db.query(MasterRecord).filter(MasterRecord.id == item_input.item_id).first()
        if not item or not item.is_active:
            errors.append(f"Item {item_input.item_id} must be active")
        if item_input.pcs_quantity <= 0:
            errors.append(f"Quantity for item {item_input.item_id} must be greater than zero")
        if item_input.pcs_quantity > 1000:
            warnings.append("Large parcel size")

    return PackingValidationResult(valid=len(errors) == 0, warnings=warnings, errors=errors)


def serialize_parcel(parcel: Parcel, db: Session) -> ParcelResponse:
    items = []
    for parcel_item in parcel.items:
        item = db.query(MasterRecord).filter(MasterRecord.id == parcel_item.item_id).first()
        items.append(
            ParcelItemResponse(
                item_id=parcel_item.item_id,
                item_code=item.code if item else None,
                item_name=item.name if item else None,
                pcs_quantity=parcel_item.pcs_quantity,
                status=parcel_item.status,
            )
        )

    return ParcelResponse(
        id=parcel.id,
        parcel_date=parcel.parcel_date.isoformat() if parcel.parcel_date else None,
        parcel_code=parcel.parcel_code,
        total_pcs=parcel.total_pcs,
        status=parcel.status,
        notes=parcel.notes,
        items=items,
    )
