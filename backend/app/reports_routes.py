from __future__ import annotations

import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.job_work_models import JobWorkAssignment, JobWorkPendingPayment
from app.models import MasterRecord
from app.production_models import ProductionRecord
from app.reports_models import ReportSnapshot, ReportTemplate
from app.reports_schemas import (
    ReportExportRequest,
    ReportExportResponse,
    ReportGenerateRequest,
    ReportGenerateResponse,
    ReportSnapshotResponse,
    ReportTemplateCreate,
    ReportTemplateResponse,
)
from app.inventory_models import InventoryBalance
from app.payroll_models import EmployeeAttendance

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/templates", response_model=list[ReportTemplateResponse])
def list_templates(db: Session = Depends(get_db)):
    templates = db.query(ReportTemplate).order_by(ReportTemplate.created_at.desc()).all()
    return [serialize_template(item) for item in templates]


@router.post("/templates", response_model=ReportTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_template(payload: ReportTemplateCreate, db: Session = Depends(get_db)):
    template = ReportTemplate(
        report_code=payload.report_code,
        report_name=payload.report_name,
        report_category=payload.report_category,
        filters_json=payload.filters_json,
        is_default=1 if payload.is_default else 0,
        created_by=payload.created_by,
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return serialize_template(template)


@router.post("/generate", response_model=ReportGenerateResponse)
def generate_report(payload: ReportGenerateRequest, db: Session = Depends(get_db)):
    if payload.template_id:
        template = db.query(ReportTemplate).filter(ReportTemplate.id == payload.template_id).first()
        if template:
            payload.filters.update(template.filters_json or {})
    report_type = payload.report_type.lower()
    rows, summary = build_report_rows(report_type, payload, db)
    snapshot = ReportSnapshot(
        report_code=payload.report_type,
        report_name=report_name_for(payload.report_type),
        report_category=category_for(payload.report_type),
        payload_json={"summary": summary, "rows": rows},
        created_by="system",
    )
    db.add(snapshot)
    db.commit()
    return ReportGenerateResponse(
        report_type=payload.report_type,
        report_name=report_name_for(payload.report_type),
        category=category_for(payload.report_type),
        generated_at=datetime.datetime.utcnow().isoformat(),
        summary=summary,
        rows=rows,
    )


@router.get("/snapshots", response_model=list[ReportSnapshotResponse])
def list_snapshots(db: Session = Depends(get_db)):
    snapshots = db.query(ReportSnapshot).order_by(ReportSnapshot.snapshot_date.desc()).all()
    return [serialize_snapshot(item) for item in snapshots]


@router.post("/export", response_model=ReportExportResponse)
def export_report(payload: ReportExportRequest, db: Session = Depends(get_db)):
    fmt = payload.format.lower()
    if fmt not in {"excel", "pdf"}:
        raise HTTPException(status_code=400, detail="Only excel and pdf exports are supported")
    return ReportExportResponse(
        report_type=payload.report_type,
        format=fmt,
        status="ready",
        download_url=f"/reports/export/{payload.report_type}?format={fmt}",
        message="Export package prepared for download",
    )


def build_report_rows(report_type: str, payload: ReportGenerateRequest, db: Session) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    start_date = parse_date(payload.start_date)
    end_date = parse_date(payload.end_date)
    if report_type == "production":
        query = db.query(ProductionRecord)
        if start_date:
            query = query.filter(ProductionRecord.production_date >= start_date)
        if end_date:
            query = query.filter(ProductionRecord.production_date <= end_date)
        records = query.all()
        rows = [
            {
                "id": item.id,
                "date": item.production_date.isoformat() if item.production_date else None,
                "employee": item.employee_id,
                "bunches": item.bunches,
                "status": item.status,
            }
            for item in records
        ]
        return rows, {"total_records": len(rows), "total_bunches": sum(item["bunches"] for item in rows)}

    if report_type == "inventory":
        records = db.query(InventoryBalance).all()
        rows = [
            {
                "item_id": item.item_id,
                "produced_inventory": item.produced_inventory,
                "job_work_in_progress": item.job_work_in_progress,
                "finished_goods": item.finished_goods,
                "packed_inventory": item.packed_inventory,
                "dispatched_inventory": item.dispatched_inventory,
            }
            for item in records
        ]
        return rows, {"total_records": len(rows), "finished_goods": sum(item["finished_goods"] for item in rows)}

    if report_type == "employees":
        records = db.query(MasterRecord).filter(MasterRecord.entity_type == "employee").all()
        rows = [{"id": item.id, "code": item.code, "name": item.name, "active": item.is_active} for item in records]
        return rows, {"total_records": len(rows), "active": sum(1 for item in rows if item["active"])}

    if report_type == "jobwork":
        records = db.query(JobWorkAssignment).all()
        rows = [{"id": item.id, "job_worker_id": item.job_worker_id, "item_id": item.item_id, "assigned_bunches": item.assigned_bunches, "status": item.status} for item in records]
        return rows, {"total_records": len(rows), "active_assignments": sum(1 for item in rows if item["status"] == "in_progress")}

    if report_type == "bobbins":
        records = db.query(MasterRecord).filter(MasterRecord.entity_type == "bobbin").all()
        rows = [{"id": item.id, "code": item.code, "name": item.name, "active": item.is_active} for item in records]
        return rows, {"total_records": len(rows)}

    if report_type == "finance":
        records = db.query(JobWorkPendingPayment).all()
        rows = [{"id": item.id, "job_worker_id": item.job_worker_id, "payable_amount": item.payable_amount, "amount_paid": item.amount_paid, "outstanding_balance": item.outstanding_balance, "status": item.status} for item in records]
        return rows, {"total_records": len(rows), "outstanding_balance": sum(item["outstanding_balance"] for item in rows)}

    return [], {"total_records": 0}


def parse_date(value: str | None) -> datetime.datetime | None:
    if not value:
        return None
    return datetime.datetime.fromisoformat(value)


def report_name_for(report_type: str) -> str:
    return {
        "production": "Production Report",
        "inventory": "Inventory Report",
        "employees": "Employees Report",
        "jobwork": "Job Work Report",
        "bobbins": "Bobbins Report",
        "finance": "Finance Report",
    }.get(report_type, "Report")


def category_for(report_type: str) -> str:
    return {
        "production": "operations",
        "inventory": "inventory",
        "employees": "people",
        "jobwork": "jobwork",
        "bobbins": "materials",
        "finance": "finance",
    }.get(report_type, "general")


def serialize_template(template: ReportTemplate) -> ReportTemplateResponse:
    return ReportTemplateResponse(
        id=template.id,
        report_code=template.report_code,
        report_name=template.report_name,
        report_category=template.report_category,
        filters_json=template.filters_json or {},
        is_default=bool(template.is_default),
        created_by=template.created_by,
        created_at=template.created_at.isoformat(),
    )


def serialize_snapshot(snapshot: ReportSnapshot) -> ReportSnapshotResponse:
    return ReportSnapshotResponse(
        id=snapshot.id,
        report_code=snapshot.report_code,
        report_name=snapshot.report_name,
        report_category=snapshot.report_category,
        snapshot_date=snapshot.snapshot_date.isoformat(),
        payload_json=snapshot.payload_json or {},
        created_by=snapshot.created_by,
    )
