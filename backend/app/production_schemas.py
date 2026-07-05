from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class ProductionEntryCreate(BaseModel):
    production_date: Optional[str] = None
    machine_id: int
    item_id: int
    employee_id: Optional[int] = None
    bunches: float
    entry_timestamp: Optional[str] = None
    status: str = "available"
    notes: Optional[str] = None
    created_by: Optional[str] = None


class ProductionEntryUpdate(BaseModel):
    machine_id: Optional[int] = None
    item_id: Optional[int] = None
    employee_id: Optional[int] = None
    bunches: Optional[float] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    updated_by: Optional[str] = None


class ProductionEntryResponse(ProductionEntryCreate):
    id: int
    is_locked: bool
    created_at: str
    updated_at: str
    machine_code: Optional[str] = None
    item_code: Optional[str] = None
    employee_code: Optional[str] = None

    class Config:
        from_attributes = True


class ProductionValidationResult(BaseModel):
    valid: bool
    warnings: list[str]
    errors: list[str]


class ProducedInventorySummary(BaseModel):
    item_id: int
    item_code: Optional[str] = None
    item_name: Optional[str] = None
    total_bunches: float
    available_bunches: float
    partially_assigned_bunches: float
    fully_assigned_bunches: float
