from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class ForecastCreate(BaseModel):
    plan_id: int
    running_hours: float


class ForecastResponse(BaseModel):
    id: int
    plan_id: int
    machine_id: int
    item_id: int
    running_hours: float
    standard_time_per_bunch_minutes: float
    forecast_bunches: float
    actual_bunches: float
    difference_bunches: float
    forecast_date: str
    machine_code: Optional[str] = None
    item_code: Optional[str] = None
    item_name: Optional[str] = None

    class Config:
        from_attributes = True


class ForecastAlertResponse(BaseModel):
    id: int
    alert_type: str
    title: str
    message: str
    severity: str

    class Config:
        from_attributes = True


class ForecastSummary(BaseModel):
    total_forecast_bunches: float
    total_actual_bunches: float
    total_difference_bunches: float
    forecasts: list[ForecastResponse]
    alerts: list[ForecastAlertResponse]
