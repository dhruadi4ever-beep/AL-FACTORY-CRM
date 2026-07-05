from __future__ import annotations

import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.business_validation import BusinessRuleEngine, ValidationContext
from app.database import get_db
from app.inventory_models import InventoryBalance, StockAdjustment, StockLedgerEntry
from app.inventory_schemas import InventoryBalanceResponse, StockAdjustmentCreate, StockAdjustmentResponse, StockLedgerEntryResponse
from app.models import MasterRecord

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("", response_model=list[InventoryBalanceResponse])
def list_balances(db: Session = Depends(get_db)):
    balances = db.query(InventoryBalance).all()
    return [serialize_balance(balance, db) for balance in balances]


@router.get("/ledger", response_model=list[StockLedgerEntryResponse])
def list_ledger(db: Session = Depends(get_db)):
    entries = db.query(StockLedgerEntry).order_by(StockLedgerEntry.entry_date.desc()).all()
    return [serialize_ledger(entry) for entry in entries]


@router.post("/adjustments", response_model=StockAdjustmentResponse, status_code=status.HTTP_201_CREATED)
def create_adjustment(payload: StockAdjustmentCreate, db: Session = Depends(get_db)):
    item = db.query(MasterRecord).filter(MasterRecord.id == payload.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    engine = BusinessRuleEngine()
    try:
        adjustment = engine.execute(
            db,
            ValidationContext(
                entity_type="stock_adjustment",
                actor=payload.created_by or "system",
                payload=payload.model_dump(),
                input_validator=lambda data: [],
                master_validator=lambda context: [],
                business_rule_validator=lambda context: [],
                inventory_validator=lambda context: [] if payload.difference_quantity >= 0 else ["Inventory cannot go negative"],
                persister=lambda context: StockAdjustment(
                    item_id=payload.item_id,
                    adjustment_date=datetime.datetime.utcnow(),
                    stage=payload.stage,
                    difference_quantity=payload.difference_quantity,
                    reason=payload.reason,
                    created_by=payload.created_by,
                ),
                metadata={"master_refs": [{"id": payload.item_id, "label": "item"}]},
                pre_save_handler=lambda session, ctx, entity: (
                    apply_adjustment(get_or_create_balance(payload.item_id, session), payload.stage, payload.difference_quantity),
                    create_ledger_entry(
                        item_id=payload.item_id,
                        transaction_type="stock_adjustment",
                        quantity=payload.difference_quantity,
                        unit="pcs",
                        source_stage=payload.stage,
                        destination_stage=payload.stage,
                        reference_transaction=f"adjustment:{entity.id}",
                        notes=payload.reason,
                        created_by=payload.created_by,
                        db=session,
                    ),
                ),
            ),
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return serialize_adjustment(adjustment)


def get_or_create_balance(item_id: int, db: Session) -> InventoryBalance:
    balance = db.query(InventoryBalance).filter(InventoryBalance.item_id == item_id).first()
    if not balance:
        balance = InventoryBalance(item_id=item_id)
        db.add(balance)
    return balance


def apply_adjustment(balance: InventoryBalance, stage: str, quantity: float) -> None:
    if stage == "produced_inventory":
        balance.produced_inventory += quantity
    elif stage == "job_work_in_progress":
        balance.job_work_in_progress += quantity
    elif stage == "finished_goods":
        balance.finished_goods += quantity
    elif stage == "packed_inventory":
        balance.packed_inventory += quantity
    elif stage == "dispatched_inventory":
        balance.dispatched_inventory += quantity


def create_ledger_entry(item_id: int, transaction_type: str, quantity: float, unit: str, source_stage: str | None, destination_stage: str | None, reference_transaction: str | None, notes: str | None, created_by: str | None, db: Session) -> None:
    entry = StockLedgerEntry(
        entry_date=datetime.datetime.utcnow(),
        item_id=item_id,
        transaction_type=transaction_type,
        quantity=quantity,
        unit=unit,
        source_stage=source_stage,
        destination_stage=destination_stage,
        reference_transaction=reference_transaction,
        notes=notes,
        created_by=created_by,
    )
    db.add(entry)


def serialize_balance(balance: InventoryBalance, db: Session) -> InventoryBalanceResponse:
    item = db.query(MasterRecord).filter(MasterRecord.id == balance.item_id).first()
    return InventoryBalanceResponse(
        item_id=balance.item_id,
        item_code=item.code if item else None,
        item_name=item.name if item else None,
        produced_inventory=balance.produced_inventory,
        job_work_in_progress=balance.job_work_in_progress,
        finished_goods=balance.finished_goods,
        packed_inventory=balance.packed_inventory,
        dispatched_inventory=balance.dispatched_inventory,
    )


def serialize_ledger(entry: StockLedgerEntry) -> StockLedgerEntryResponse:
    return StockLedgerEntryResponse(
        id=entry.id,
        entry_date=entry.entry_date.isoformat(),
        item_id=entry.item_id,
        transaction_type=entry.transaction_type,
        quantity=entry.quantity,
        unit=entry.unit,
        source_stage=entry.source_stage,
        destination_stage=entry.destination_stage,
        reference_transaction=entry.reference_transaction,
        notes=entry.notes,
        created_by=entry.created_by,
    )


def serialize_adjustment(adjustment: StockAdjustment) -> StockAdjustmentResponse:
    return StockAdjustmentResponse(
        id=adjustment.id,
        item_id=adjustment.item_id,
        stage=adjustment.stage,
        difference_quantity=adjustment.difference_quantity,
        reason=adjustment.reason,
        created_by=adjustment.created_by,
        adjustment_date=adjustment.adjustment_date.isoformat(),
    )
