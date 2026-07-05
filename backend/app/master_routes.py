from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.business_validation import BusinessRuleEngine, ValidationContext
from app.database import get_db
from app.models import MasterChangeHistory, MasterRecord
from app.schemas import ChangeHistoryResponse, MasterCreate, MasterResponse, MasterUpdate

router = APIRouter(prefix="/masters", tags=["masters"])


@router.post("", response_model=MasterResponse, status_code=status.HTTP_201_CREATED)
def create_master(master: MasterCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(MasterRecord)
        .filter(MasterRecord.entity_type == master.entity_type, MasterRecord.code == master.code)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Master record already exists")

    engine = BusinessRuleEngine()
    try:
        record = engine.execute(
            db,
            ValidationContext(
                entity_type="master_record",
                actor=master.created_by or "system",
                payload=master.model_dump(),
                input_validator=lambda data: [] if data.get("code") and data.get("name") else ["Code and name are required"],
                master_validator=lambda context: [],
                business_rule_validator=lambda context: [],
                inventory_validator=lambda context: [],
                persister=lambda context: MasterRecord(
                    entity_type=master.entity_type,
                    code=master.code,
                    name=master.name,
                    description=master.description,
                    is_active=master.is_active,
                    metadata=master.metadata,
                    created_by=master.created_by,
                    updated_by=master.created_by,
                ),
            ),
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return record


@router.get("", response_model=list[MasterResponse])
def list_masters(
    entity_type: str | None = None,
    search: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(MasterRecord)
    if entity_type:
        query = query.filter(MasterRecord.entity_type == entity_type)
    if search:
        query = query.filter(
            (MasterRecord.code.ilike(f"%{search}%")) | (MasterRecord.name.ilike(f"%{search}%"))
        )
    if status:
        is_active = status.lower() == "active"
        query = query.filter(MasterRecord.is_active.is_(is_active))
    return query.order_by(MasterRecord.created_at.desc()).all()


@router.get("/{master_id}", response_model=MasterResponse)
def get_master(master_id: int, db: Session = Depends(get_db)):
    record = db.query(MasterRecord).filter(MasterRecord.id == master_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Master record not found")
    return record


@router.put("/{master_id}", response_model=MasterResponse)
def update_master(master_id: int, payload: MasterUpdate, db: Session = Depends(get_db)):
    record = db.query(MasterRecord).filter(MasterRecord.id == master_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Master record not found")

    for field_name, value in payload.model_dump(exclude_unset=True).items():
        if field_name == "updated_by":
            continue
        if hasattr(record, field_name):
            previous_value = getattr(record, field_name)
            if previous_value != value:
                history = MasterChangeHistory(
                    master_id=record.id,
                    field_name=field_name,
                    previous_value=str(previous_value),
                    new_value=str(value),
                    changed_by=payload.updated_by,
                    reason="Updated via API",
                )
                db.add(history)
            setattr(record, field_name, value)

    record.updated_by = payload.updated_by
    db.commit()
    db.refresh(record)
    return record


@router.get("/{master_id}/history", response_model=list[ChangeHistoryResponse])
def master_history(master_id: int, db: Session = Depends(get_db)):
    record = db.query(MasterRecord).filter(MasterRecord.id == master_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Master record not found")
    return db.query(MasterChangeHistory).filter(MasterChangeHistory.master_id == master_id).order_by(MasterChangeHistory.changed_at.desc()).all()
