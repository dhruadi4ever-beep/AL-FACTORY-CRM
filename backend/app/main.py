from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.forecasting_routes import router as forecasting_router
from app.admin_routes import router as admin_router
from app.inventory_routes import router as inventory_router
from app.intelligence_routes import router as intelligence_router
from app.job_work_routes import router as job_work_router
from app.master_routes import router as master_router
from app.productivity_routes import router as productivity_router
from app.reports_routes import router as reports_router
from app.models import MasterRecord, OperationalEvent
from app.packing_routes import router as packing_router
from app.payroll_routes import router as payroll_router
from app.production_planning_routes import router as production_planning_router
from app.production_routes import router as production_router
from app.schemas import AssistantAlert, DashboardSummary, OperationalEventCreate, OperationalEventResponse

app = FastAPI(title="ARYAN LACE Manager API", version="0.1.0")
app.include_router(master_router)
app.include_router(production_planning_router)
app.include_router(forecasting_router)
app.include_router(production_router)
app.include_router(job_work_router)
app.include_router(packing_router)
app.include_router(inventory_router)
app.include_router(payroll_router)
app.include_router(intelligence_router)
app.include_router(reports_router)
app.include_router(admin_router)
app.include_router(productivity_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/events", response_model=OperationalEventResponse, status_code=status.HTTP_201_CREATED)
def create_event(payload: OperationalEventCreate, db: Session = Depends(get_db)):
    event = OperationalEvent(
        event_type=payload.event_type,
        event_date=payload.event_date and __import__("datetime").datetime.fromisoformat(payload.event_date),
        reference_type=payload.reference_type,
        reference_id=payload.reference_id,
        payload=payload.payload,
        created_by=payload.created_by,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@app.get("/dashboard", response_model=DashboardSummary)
def dashboard_summary(db: Session = Depends(get_db)):
    active_masters = db.query(MasterRecord).filter(MasterRecord.is_active.is_(True)).count()
    today = __import__("datetime").datetime.utcnow().date()
    total_events_today = db.query(OperationalEvent).filter(OperationalEvent.event_date >= today).count()
    recent_events = db.query(OperationalEvent).order_by(OperationalEvent.event_date.desc()).limit(5).all()

    workflow_status = {
        "machines": db.query(MasterRecord).filter(MasterRecord.entity_type == "machine", MasterRecord.is_active.is_(True)).count(),
        "employees": db.query(MasterRecord).filter(MasterRecord.entity_type == "employee", MasterRecord.is_active.is_(True)).count(),
        "job_workers": db.query(MasterRecord).filter(MasterRecord.entity_type == "job_worker", MasterRecord.is_active.is_(True)).count(),
        "items": db.query(MasterRecord).filter(MasterRecord.entity_type == "item", MasterRecord.is_active.is_(True)).count(),
    }

    return DashboardSummary(
        active_masters=active_masters,
        total_events_today=total_events_today,
        recent_events=recent_events,
        workflow_status=workflow_status,
    )


@app.get("/assistant/alerts", response_model=list[AssistantAlert])
def assistant_alerts(db: Session = Depends(get_db)):
    alerts: list[AssistantAlert] = []
    low_bobbin = db.query(MasterRecord).filter(MasterRecord.entity_type == "bobbin").count()
    if low_bobbin == 0:
        alerts.append(
            AssistantAlert(
                alert_type="inventory",
                title="Low bobbin inventory",
                message="No bobbin master records are currently configured.",
                severity="warning",
            )
        )

    missing_attendance = db.query(OperationalEvent).filter(OperationalEvent.event_type == "attendance").count()
    if missing_attendance == 0:
        alerts.append(
            AssistantAlert(
                alert_type="attendance",
                title="Missing attendance",
                message="No attendance events have been recorded yet.",
                severity="warning",
            )
        )

    return alerts
