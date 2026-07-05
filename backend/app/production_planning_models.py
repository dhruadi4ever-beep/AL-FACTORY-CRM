from __future__ import annotations

import datetime
from typing import Any

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class ProductionPlan(Base):
    __tablename__ = "production_plans"

    id = Column(Integer, primary_key=True, index=True)
    plan_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    machine_id = Column(Integer, ForeignKey("master_records.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("master_records.id"), nullable=True)
    employee_id = Column(Integer, ForeignKey("master_records.id"), nullable=True)
    state = Column(String(40), nullable=False, default="assigned")
    notes = Column(Text, nullable=True)
    bobbin_required = Column(Boolean, default=False)
    bobbin_issued = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    created_by = Column(String(120), nullable=True)
    updated_by = Column(String(120), nullable=True)

    machine = relationship("MasterRecord", foreign_keys=[machine_id])
    item = relationship("MasterRecord", foreign_keys=[item_id])
    employee = relationship("MasterRecord", foreign_keys=[employee_id])


class ProductionPlanChange(Base):
    __tablename__ = "production_plan_changes"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("production_plans.id", ondelete="CASCADE"), nullable=False)
    changed_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    field_name = Column(String(80), nullable=False)
    previous_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    changed_by = Column(String(120), nullable=True)
    reason = Column(Text, nullable=True)

    plan = relationship("ProductionPlan", backref="changes")
