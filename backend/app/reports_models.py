from __future__ import annotations

import datetime

from sqlalchemy import Column, DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ReportTemplate(Base):
    __tablename__ = "report_templates"

    id = Column(Integer, primary_key=True, index=True)
    report_code = Column(String(80), nullable=False, unique=True)
    report_name = Column(String(160), nullable=False)
    report_category = Column(String(80), nullable=False)
    filters_json = Column(JSON, default=dict)
    is_default = Column(Integer, default=0)
    created_by = Column(String(120), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class ReportSnapshot(Base):
    __tablename__ = "report_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    report_code = Column(String(80), nullable=False)
    report_name = Column(String(160), nullable=False)
    report_category = Column(String(80), nullable=False)
    snapshot_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    payload_json = Column(JSON, default=dict)
    created_by = Column(String(120), nullable=True)
