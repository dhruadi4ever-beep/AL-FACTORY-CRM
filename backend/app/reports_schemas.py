from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class ReportTemplateCreate(BaseModel):
    report_code: str
    report_name: str
    report_category: str
    filters_json: dict[str, Any] = Field(default_factory=dict)
    is_default: bool = False
    created_by: Optional[str] = None


class ReportTemplateResponse(ReportTemplateCreate):
    id: int
    created_at: str

    class Config:
        from_attributes = True


class ReportGenerateRequest(BaseModel):
    report_type: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    filters: dict[str, Any] = Field(default_factory=dict)
    template_id: Optional[int] = None


class ReportGenerateResponse(BaseModel):
    report_type: str
    report_name: str
    category: str
    generated_at: str
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class ReportSnapshotResponse(BaseModel):
    id: int
    report_code: str
    report_name: str
    report_category: str
    snapshot_date: str
    payload_json: dict[str, Any]
    created_by: Optional[str] = None

    class Config:
        from_attributes = True


class ReportExportRequest(BaseModel):
    report_type: str
    format: str = "excel"
    include_snapshot: bool = False


class ReportExportResponse(BaseModel):
    report_type: str
    format: str
    status: str
    download_url: Optional[str] = None
    message: str
