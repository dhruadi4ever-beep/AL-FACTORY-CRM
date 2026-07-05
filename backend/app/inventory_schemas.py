from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class StockLedgerEntryResponse(BaseModel):
    id: int
    entry_date: str
    item_id: int
    transaction_type: str
    quantity: float
    unit: str
    source_stage: Optional[str]
    destination_stage: Optional[str]
    reference_transaction: Optional[str]
    notes: Optional[str]
    created_by: Optional[str]

    class Config:
        from_attributes = True


class InventoryBalanceResponse(BaseModel):
    item_id: int
    item_code: Optional[str] = None
    item_name: Optional[str] = None
    produced_inventory: float
    job_work_in_progress: float
    finished_goods: float
    packed_inventory: float
    dispatched_inventory: float


class StockAdjustmentCreate(BaseModel):
    item_id: int
    stage: str
    difference_quantity: float
    reason: Optional[str] = None
    created_by: Optional[str] = None


class StockAdjustmentResponse(StockAdjustmentCreate):
    id: int
    adjustment_date: str

    class Config:
        from_attributes = True
