from __future__ import annotations

import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import MasterRecord
from app.production_planning_models import ProductionPlan, ProductionPlanChange
from app.production_planning_schemas import (
    PlanningAssistantAlert,
    PlanningValidationResult,
    ProductionPlanChangeResponse,
    ProductionPlanCreate,
    ProductionPlanResponse,
    ProductionPlanUpdate,
)

router = APIRouter(prefix="/production-planning", tags=["production-planning"])


@router.post("", response_model=ProductionPlanResponse, status_code=status.HTTP_201_CREATED)
def create_plan(payload: ProductionPlanCreate, db: Session = Depends(get_db)):
    plan = ProductionPlan(
        plan_date=payload.plan_date and datetime.datetime.fromisoformat(payload.plan_date),
        machine_id=payload.machine_id,
        item_id=payload.item_id,
        employee_id=payload.employee_id,
        state=payload.state,
        notes=payload.notes,
        bobbin_required=payload.bobbin_required,
        bobbin_issued=payload.bobbin_issued,
        created_by=payload.created_by,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return serialize_plan(plan, db)


@router.get("", response_model=list[ProductionPlanResponse])
def list_plans(db: Session = Depends(get_db)):
    plans = db.query(ProductionPlan).order_by(ProductionPlan.plan_date.desc(), ProductionPlan.created_at.desc()).all()
    return [serialize_plan(plan, db) for plan in plans]


@router.get("/{plan_id}", response_model=ProductionPlanResponse)
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(ProductionPlan).filter(ProductionPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Production plan not found")
    return serialize_plan(plan, db)


@router.put("/{plan_id}", response_model=ProductionPlanResponse)
def update_plan(plan_id: int, payload: ProductionPlanUpdate, db: Session = Depends(get_db)):
    plan = db.query(ProductionPlan).filter(ProductionPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Production plan not found")

    for field_name, value in payload.model_dump(exclude_unset=True).items():
        if field_name == "updated_by":
            continue
        if hasattr(plan, field_name):
            previous_value = getattr(plan, field_name)
            if previous_value != value:
                change = ProductionPlanChange(
                    plan_id=plan.id,
                    field_name=field_name,
                    previous_value=str(previous_value),
                    new_value=str(value),
                    changed_by=payload.updated_by,
                    reason="Updated via API",
                )
                db.add(change)
            setattr(plan, field_name, value)

    plan.updated_by = payload.updated_by
    db.commit()
    db.refresh(plan)
    return serialize_plan(plan, db)


@router.get("/{plan_id}/history", response_model=list[ProductionPlanChangeResponse])
def plan_history(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(ProductionPlan).filter(ProductionPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Production plan not found")
    return db.query(ProductionPlanChange).filter(ProductionPlanChange.plan_id == plan_id).order_by(ProductionPlanChange.changed_at.desc()).all()


@router.get("/validation", response_model=PlanningValidationResult)
def validate_planning(db: Session = Depends(get_db)):
    warnings: list[str] = []
    errors: list[str] = []
    plans = db.query(ProductionPlan).all()
    for plan in plans:
        if plan.state == "assigned" and not plan.item_id:
            errors.append(f"Plan {plan.id} is assigned without an item")
        if plan.state == "assigned" and plan.bobbin_required and not plan.bobbin_issued:
            warnings.append(f"Plan {plan.id} requires bobbins but no issue has been recorded")
        if plan.machine_id:
            machine = db.query(MasterRecord).filter(MasterRecord.id == plan.machine_id).first()
            if machine and not machine.is_active:
                errors.append(f"Plan {plan.id} uses an inactive machine")
    return PlanningValidationResult(valid=len(errors) == 0, warnings=warnings, errors=errors)


@router.get("/assistant-alerts", response_model=list[PlanningAssistantAlert])
def planning_assistant_alerts(db: Session = Depends(get_db)):
    alerts: list[PlanningAssistantAlert] = []
    assigned_plans = db.query(ProductionPlan).filter(ProductionPlan.state == "assigned").all()
    if not assigned_plans:
        alerts.append(
            PlanningAssistantAlert(
                alert_type="planning",
                title="No active planning entries",
                message="No production plans have been created for the current period.",
                severity="info",
            )
        )
    for plan in assigned_plans:
        if plan.item_id is None:
            alerts.append(
                PlanningAssistantAlert(
                    alert_type="planning",
                    title="Machine missing assigned item",
                    message=f"Plan {plan.id} is assigned but has no item selected.",
                    severity="warning",
                    metadata={"plan_id": plan.id},
                )
            )
    return alerts


def serialize_plan(plan: ProductionPlan, db: Session) -> ProductionPlanResponse:
    machine = db.query(MasterRecord).filter(MasterRecord.id == plan.machine_id).first()
    item = db.query(MasterRecord).filter(MasterRecord.id == plan.item_id).first() if plan.item_id else None
    employee = db.query(MasterRecord).filter(MasterRecord.id == plan.employee_id).first() if plan.employee_id else None

    return ProductionPlanResponse(
        id=plan.id,
        plan_date=plan.plan_date.isoformat() if plan.plan_date else None,
        machine_id=plan.machine_id,
        item_id=plan.item_id,
        employee_id=plan.employee_id,
        state=plan.state,
        notes=plan.notes,
        bobbin_required=plan.bobbin_required,
        bobbin_issued=plan.bobbin_issued,
        created_by=plan.created_by,
        created_at=plan.created_at.isoformat(),
        updated_at=plan.updated_at.isoformat(),
        machine_code=machine.code if machine else None,
        item_code=item.code if item else None,
        employee_code=employee.code if employee else None,
    )
