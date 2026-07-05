from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class ProductionPlanCreate(BaseModel):
    plan_date: Optional[str] = None
    machine_id: int
    item_id: Optional[int] = None
    employee_id: Optional[int] = None
    state: str = "assigned"
    notes: Optional[str] = None
    bobbin_required: bool = False
    bobbin_issued: bool = False
    created_by: Optional[str] = None


class ProductionPlanUpdate(BaseModel):
    machine_id: Optional[int] = None
    item_id: Optional[int] = None
    employee_id: Optional[int] = None
    state: Optional[str] = None
    notes: Optional[str] = None
    bobbin_required: Optional[bool] = None
    bobbin_issued: Optional[bool] = None
    updated_by: Optional[str] = None


class ProductionPlanResponse(ProductionPlanCreate):
    id: int
    created_at: str
    updated_at: str
    machine_code: Optional[str] = None
    item_code: Optional[str] = None
    employee_code: Optional[str] = None

    class Config:
        from_attributes = True


class ProductionPlanChangeResponse(BaseModel):
    id: int
    field_name: str
    previous_value: Optional[str]
    new_value: Optional[str]
    changed_at: str
    changed_by: Optional[str]
    reason: Optional[str]

    class Config:
        from_attributes = True


class PlanningValidationResult(BaseModel):
    valid: bool
    warnings: list[str]
    errors: list[str]


class PlanningAssistantAlert(BaseModel):
    alert_type: str
    title: str
    message: str
    severity: str
    metadata: dict[str, Any] = Field(default_factory=dict)
