from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class ParcelItemInput(BaseModel):
    item_id: int
    pcs_quantity: float


class ParcelCreate(BaseModel):
    parcel_date: Optional[str] = None
    parcel_code: str
    items: list[ParcelItemInput]
    notes: Optional[str] = None
    created_by: Optional[str] = None


class ParcelItemResponse(BaseModel):
    item_id: int
    item_code: Optional[str] = None
    item_name: Optional[str] = None
    pcs_quantity: float
    status: str

    class Config:
        from_attributes = True


class ParcelResponse(BaseModel):
    id: int
    parcel_date: str
    parcel_code: str
    total_pcs: float
    status: str
    notes: Optional[str] = None
    items: list[ParcelItemResponse]

    class Config:
        from_attributes = True


class PackingValidationResult(BaseModel):
    valid: bool
    warnings: list[str]
    errors: list[str]
