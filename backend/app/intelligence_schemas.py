from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class AlertResponse(BaseModel):
    id: int
    severity: str
    category: str
    title: str
    message: str
    recommendation: str
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str
    is_acknowledged: bool
    source: Optional[str] = None

    class Config:
        from_attributes = True


class DailyFactorySummaryResponse(BaseModel):
    id: int
    summary_date: str
    factory_health_score: int
    active_masters: int
    active_employees: int
    active_job_workers: int
    active_machines: int
    pending_jobs: int
    production_bunches: float
    finished_goods: float
    pending_payments: float
    alert_count: int
    summary_text: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


class DecisionSupportRequest(BaseModel):
    scenario_name: str
    context: dict[str, Any] = Field(default_factory=dict)
    provider: Optional[str] = None


class DecisionSupportResponse(BaseModel):
    scenario_name: str
    recommendation_type: str
    recommendation_text: str
    confidence: float
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str

    class Config:
        from_attributes = True


class DashboardSnapshot(BaseModel):
    factory_health_score: int
    active_masters: int
    active_employees: int
    active_job_workers: int
    active_machines: int
    pending_jobs: int
    production_bunches: float
    finished_goods: float
    pending_payments: float
    alerts: list[AlertResponse]
    summary: Optional[DailyFactorySummaryResponse] = None
