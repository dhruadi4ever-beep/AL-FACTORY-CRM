from __future__ import annotations

import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.forecasting_models import ForecastAlert, ForecastRecord
from app.forecasting_schemas import ForecastAlertResponse, ForecastCreate, ForecastResponse, ForecastSummary
from app.models import MasterRecord
from app.production_planning_models import ProductionPlan

router = APIRouter(prefix="/forecasting", tags=["forecasting"])


@router.post("", response_model=ForecastResponse, status_code=status.HTTP_201_CREATED)
def create_forecast(payload: ForecastCreate, db: Session = Depends(get_db)):
    plan = db.query(ProductionPlan).filter(ProductionPlan.id == payload.plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Production plan not found")

    if not plan.item_id:
        raise HTTPException(status_code=400, detail="Forecast requires an assigned item")

    item = db.query(MasterRecord).filter(MasterRecord.id == plan.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Assigned item not found")

    metadata = item.metadata or {}
    standard_time_per_bunch_minutes = float(metadata.get("standardTimePerBunch", 0) or 0)
    forecast_bunches = round(payload.running_hours * 60 / standard_time_per_bunch_minutes, 2) if standard_time_per_bunch_minutes else 0.0

    record = ForecastRecord(
        plan_id=plan.id,
        machine_id=plan.machine_id,
        item_id=plan.item_id,
        running_hours=payload.running_hours,
        standard_time_per_bunch_minutes=standard_time_per_bunch_minutes,
        forecast_bunches=forecast_bunches,
        actual_bunches=0.0,
        difference_bunches=0.0 - forecast_bunches,
        forecast_date=datetime.datetime.utcnow(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return serialize_forecast(record, db)


@router.get("", response_model=list[ForecastResponse])
def list_forecasts(db: Session = Depends(get_db)):
    forecasts = db.query(ForecastRecord).order_by(ForecastRecord.forecast_date.desc()).all()
    return [serialize_forecast(item, db) for item in forecasts]


@router.get("/summary", response_model=ForecastSummary)
def forecast_summary(db: Session = Depends(get_db)):
    forecasts = db.query(ForecastRecord).all()
    alerts = db.query(ForecastAlert).order_by(ForecastAlert.created_at.desc()).all()
    summary = ForecastSummary(
        total_forecast_bunches=sum(item.forecast_bunches for item in forecasts),
        total_actual_bunches=sum(item.actual_bunches for item in forecasts),
        total_difference_bunches=sum(item.difference_bunches for item in forecasts),
        forecasts=[serialize_forecast(item, db) for item in forecasts],
        alerts=[ForecastAlertResponse.from_orm(alert) for alert in alerts],
    )
    return summary


@router.post("/{forecast_id}/actual", response_model=ForecastResponse)
def update_actual_production(forecast_id: int, actual_bunches: float, db: Session = Depends(get_db)):
    record = db.query(ForecastRecord).filter(ForecastRecord.id == forecast_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Forecast not found")

    record.actual_bunches = actual_bunches
    record.difference_bunches = actual_bunches - record.forecast_bunches
    db.commit()
    db.refresh(record)
    return serialize_forecast(record, db)


@router.get("/alerts", response_model=list[ForecastAlertResponse])
def list_alerts(db: Session = Depends(get_db)):
    alerts = db.query(ForecastAlert).order_by(ForecastAlert.created_at.desc()).all()
    return [ForecastAlertResponse.from_orm(alert) for alert in alerts]


@router.post("/alerts", response_model=ForecastAlertResponse, status_code=status.HTTP_201_CREATED)
def create_alert(payload: dict, db: Session = Depends(get_db)):
    alert = ForecastAlert(
        forecast_id=payload.get("forecast_id"),
        alert_type=payload.get("alert_type", "forecast"),
        title=payload.get("title", "Forecast review"),
        message=payload.get("message", "Review forecast data"),
        severity=payload.get("severity", "info"),
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return ForecastAlertResponse.from_orm(alert)


def serialize_forecast(record: ForecastRecord, db: Session) -> ForecastResponse:
    machine = db.query(MasterRecord).filter(MasterRecord.id == record.machine_id).first()
    item = db.query(MasterRecord).filter(MasterRecord.id == record.item_id).first()

    return ForecastResponse(
        id=record.id,
        plan_id=record.plan_id,
        machine_id=record.machine_id,
        item_id=record.item_id,
        running_hours=record.running_hours,
        standard_time_per_bunch_minutes=record.standard_time_per_bunch_minutes,
        forecast_bunches=record.forecast_bunches,
        actual_bunches=record.actual_bunches,
        difference_bunches=record.difference_bunches,
        forecast_date=record.forecast_date.isoformat(),
        machine_code=machine.code if machine else None,
        item_code=item.code if item else None,
        item_name=item.name if item else None,
    )
