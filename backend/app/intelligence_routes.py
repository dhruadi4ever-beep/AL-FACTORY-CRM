from __future__ import annotations

import datetime
import json
import os
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.intelligence_models import DailyFactorySummary, DecisionSupportRecommendation, IntelligenceAlert
from app.intelligence_schemas import AlertResponse, DailyFactorySummaryResponse, DashboardSnapshot, DecisionSupportRequest, DecisionSupportResponse
from app.models import MasterRecord, OperationalEvent
from app.production_models import ProductionRecord
from app.job_work_models import JobWorkAssignment, JobWorkPendingPayment

router = APIRouter(prefix="/intelligence", tags=["intelligence"])


@router.get("/alerts", response_model=list[AlertResponse])
def list_alerts(db: Session = Depends(get_db), severity: str | None = None):
    query = db.query(IntelligenceAlert)
    if severity:
        query = query.filter(IntelligenceAlert.severity == severity)
    alerts = query.order_by(IntelligenceAlert.created_at.desc()).all()
    return [serialize_alert(alert) for alert in alerts]


@router.post("/alerts/generate", response_model=list[AlertResponse], status_code=status.HTTP_201_CREATED)
def generate_alerts(db: Session = Depends(get_db)):
    db.query(IntelligenceAlert).delete()
    alerts = build_alerts(db)
    db.add_all(alerts)
    db.commit()
    return [serialize_alert(alert) for alert in alerts]


@router.get("/summary/daily", response_model=DailyFactorySummaryResponse)
def get_daily_summary(db: Session = Depends(get_db)):
    summary = db.query(DailyFactorySummary).order_by(DailyFactorySummary.summary_date.desc()).first()
    if not summary:
        summary = build_daily_summary(db)
        db.add(summary)
        db.commit()
        db.refresh(summary)
    return serialize_summary(summary)


@router.get("/dashboard", response_model=DashboardSnapshot)
def dashboard_snapshot(db: Session = Depends(get_db)):
    alerts = build_alerts(db)
    summary = db.query(DailyFactorySummary).order_by(DailyFactorySummary.summary_date.desc()).first()
    if not summary:
        summary = build_daily_summary(db)
        db.add(summary)
        db.commit()
        db.refresh(summary)
    return DashboardSnapshot(
        factory_health_score=summary.factory_health_score,
        active_masters=summary.active_masters,
        active_employees=summary.active_employees,
        active_job_workers=summary.active_job_workers,
        active_machines=summary.active_machines,
        pending_jobs=summary.pending_jobs,
        production_bunches=summary.production_bunches,
        finished_goods=summary.finished_goods,
        pending_payments=summary.pending_payments,
        alerts=[serialize_alert(alert) for alert in alerts],
        summary=serialize_summary(summary),
    )


@router.post("/advisor", response_model=DecisionSupportResponse)
def decision_support(payload: DecisionSupportRequest, db: Session = Depends(get_db)):
    recommendation = build_recommendation(payload, db)
    db.add(recommendation)
    db.commit()
    db.refresh(recommendation)
    return serialize_recommendation(recommendation)


def build_alerts(db: Session) -> list[IntelligenceAlert]:
    alerts: list[IntelligenceAlert] = []
    active_machines = db.query(MasterRecord).filter(MasterRecord.entity_type == "machine", MasterRecord.is_active.is_(True)).count()
    open_assignments = db.query(JobWorkAssignment).filter(JobWorkAssignment.status == "in_progress").count()
    pending_payments = db.query(JobWorkPendingPayment).filter(JobWorkPendingPayment.status.in_(["pending", "partially_paid"])).all()

    if active_machines == 0:
        alerts.append(IntelligenceAlert(severity="critical", category="operations", title="No active machines configured", message="The factory is missing active machine masters.", recommendation="Add or activate machine masters immediately.", source="assistant"))
    if open_assignments > 0:
        alerts.append(IntelligenceAlert(severity="warning", category="jobwork", title="Active job-work assignments found", message=f"{open_assignments} job-work assignments are still active.", recommendation="Review active assignments and complete or return them if required.", source="assistant"))
    if pending_payments:
        alerts.append(IntelligenceAlert(severity="warning", category="payments", title="Pending job-worker payments", message=f"{len(pending_payments)} payment records are still outstanding.", recommendation="Review outstanding balances and plan a payment cycle.", source="assistant"))

    alerts.append(IntelligenceAlert(severity="info", category="operations", title="Factory monitoring active", message="The intelligence layer is tracking live operational signals.", recommendation="Use the dashboard and advisor to review the latest factory state.", source="assistant"))
    return alerts


def build_daily_summary(db: Session) -> DailyFactorySummary:
    active_masters = db.query(MasterRecord).filter(MasterRecord.is_active.is_(True)).count()
    active_employees = db.query(MasterRecord).filter(MasterRecord.entity_type == "employee", MasterRecord.is_active.is_(True)).count()
    active_job_workers = db.query(MasterRecord).filter(MasterRecord.entity_type == "job_worker", MasterRecord.is_active.is_(True)).count()
    active_machines = db.query(MasterRecord).filter(MasterRecord.entity_type == "machine", MasterRecord.is_active.is_(True)).count()
    pending_jobs = db.query(JobWorkAssignment).filter(JobWorkAssignment.status == "in_progress").count()
    production_bunches = sum(item.bunches for item in db.query(ProductionRecord).all())
    finished_goods = 0.0
    pending_payments = sum(payment.outstanding_balance for payment in db.query(JobWorkPendingPayment).filter(JobWorkPendingPayment.status.in_(["pending", "partially_paid"])).all())
    alerts = db.query(IntelligenceAlert).count()

    health_score = 100
    if active_machines == 0:
        health_score -= 30
    if pending_jobs > 0:
        health_score -= 10
    if pending_payments > 0:
        health_score -= 10
    if alerts > 0:
        health_score -= min(15, alerts * 3)

    summary_text = f"Factory health score {health_score}. Active masters {active_masters}, employees {active_employees}, job workers {active_job_workers}, machines {active_machines}."
    return DailyFactorySummary(
        summary_date=datetime.datetime.utcnow().date(),
        factory_health_score=max(0, health_score),
        active_masters=active_masters,
        active_employees=active_employees,
        active_job_workers=active_job_workers,
        active_machines=active_machines,
        pending_jobs=pending_jobs,
        production_bunches=production_bunches,
        finished_goods=finished_goods,
        pending_payments=pending_payments,
        alert_count=alerts,
        summary_text=summary_text,
    )


def build_recommendation(payload: DecisionSupportRequest, db: Session) -> DecisionSupportRecommendation:
    context = payload.context or {}
    if context.get("pending_jobs", 0) > 0:
        recommendation_text = "Prioritize completion of active job-work assignments to reduce workflow congestion."
        recommendation_type = "resource"
    else:
        recommendation_text = "Maintain current operating cadence and review the latest dashboard signals."
        recommendation_type = "operations"
    return DecisionSupportRecommendation(
        scenario_name=payload.scenario_name,
        recommendation_type=recommendation_type,
        recommendation_text=recommendation_text,
        confidence=0.86,
        metadata={"provider": payload.provider or "rule-based", **context},
    )


def serialize_alert(alert: IntelligenceAlert) -> AlertResponse:
    return AlertResponse(
        id=alert.id,
        severity=alert.severity,
        category=alert.category,
        title=alert.title,
        message=alert.message,
        recommendation=alert.recommendation,
        related_entity_type=alert.related_entity_type,
        related_entity_id=alert.related_entity_id,
        metadata=alert.metadata or {},
        created_at=alert.created_at.isoformat(),
        is_acknowledged=alert.is_acknowledged,
        source=alert.source,
    )


def serialize_summary(summary: DailyFactorySummary) -> DailyFactorySummaryResponse:
    return DailyFactorySummaryResponse(
        id=summary.id,
        summary_date=summary.summary_date.isoformat(),
        factory_health_score=summary.factory_health_score,
        active_masters=summary.active_masters,
        active_employees=summary.active_employees,
        active_job_workers=summary.active_job_workers,
        active_machines=summary.active_machines,
        pending_jobs=summary.pending_jobs,
        production_bunches=summary.production_bunches,
        finished_goods=summary.finished_goods,
        pending_payments=summary.pending_payments,
        alert_count=summary.alert_count,
        summary_text=summary.summary_text,
        created_at=summary.created_at.isoformat(),
    )


def serialize_recommendation(recommendation: DecisionSupportRecommendation) -> DecisionSupportResponse:
    return DecisionSupportResponse(
        scenario_name=recommendation.scenario_name,
        recommendation_type=recommendation.recommendation_type,
        recommendation_text=recommendation.recommendation_text,
        confidence=recommendation.confidence,
        metadata=recommendation.metadata or {},
        created_at=recommendation.created_at.isoformat(),
    )
