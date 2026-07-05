from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class MasterBase(BaseModel):
    entity_type: str
    code: str
    name: str
    description: Optional[str] = None
    is_active: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class MasterSearchQuery(BaseModel):
    entity_type: Optional[str] = None
    search: Optional[str] = None
    status: Optional[str] = None


class MasterCreate(MasterBase):
    created_by: Optional[str] = None


class MasterUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    metadata: Optional[dict[str, Any]] = None
    updated_by: Optional[str] = None


class MasterResponse(MasterBase):
    id: int

    class Config:
        from_attributes = True


class ChangeHistoryResponse(BaseModel):
    id: int
    field_name: str
    previous_value: Optional[str]
    new_value: Optional[str]
    changed_at: str
    changed_by: Optional[str]
    reason: Optional[str]

    class Config:
        from_attributes = True


class OperationalEventCreate(BaseModel):
    event_type: str
    event_date: Optional[str] = None
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    payload: dict[str, Any] = Field(default_factory=dict)
    created_by: Optional[str] = None


class OperationalEventResponse(OperationalEventCreate):
    id: int

    class Config:
        from_attributes = True


class DashboardSummary(BaseModel):
    active_masters: int
    total_events_today: int
    recent_events: list[OperationalEventResponse]
    workflow_status: dict[str, int]


class AssistantAlert(BaseModel):
    alert_type: str
    title: str
    message: str
    severity: str
    metadata: dict[str, Any] = Field(default_factory=dict)
