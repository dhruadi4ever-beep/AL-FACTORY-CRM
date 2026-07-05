from __future__ import annotations

import datetime
import enum
from typing import Any

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import declarative_base, relationship

from app.forecasting_models import ForecastAlert, ForecastRecord
from app.admin_models import AdminSession, AuditTrailEntry, SystemSetting
from app.inventory_models import InventoryBalance, StockAdjustment, StockLedgerEntry
from app.intelligence_models import DailyFactorySummary, DecisionSupportRecommendation, IntelligenceAlert
from app.job_work_models import JobWorkAssignment, JobWorkMovement, JobWorkPaymentLedgerEntry, JobWorkPendingPayment
from app.productivity_models import FavoriteRecord, GlobalSearchIndex, QuickAction, RecentRecord
from app.reports_models import ReportSnapshot, ReportTemplate
from app.packing_models import Parcel, ParcelItem
from app.production_models import ProducedInventoryBalance, ProductionRecord
from app.production_planning_models import ProductionPlan, ProductionPlanChange
from app.payroll_models import EmployeeAttendance, EmployeeSalaryAdvance, MachineAssignmentHistory, SalaryAdvanceDeduction, SalaryLedgerEntry, WeeklySalaryCycle

Base = declarative_base()


class MasterStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class MasterRecord(Base):
    __tablename__ = "master_records"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(80), nullable=False, index=True)
    code = Column(String(120), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    data_json = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    created_by = Column(String(120), nullable=True)
    updated_by = Column(String(120), nullable=True)

    change_history = relationship("MasterChangeHistory", back_populates="master", cascade="all, delete-orphan")

    def __getattribute__(self, name: str) -> Any:
        if name == "metadata":
            return object.__getattribute__(self, "data_json") or {}
        return object.__getattribute__(self, name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "metadata":
            object.__setattr__(self, "data_json", value or {})
            return
        object.__setattr__(self, name, value)


class MasterChangeHistory(Base):
    __tablename__ = "master_change_history"

    id = Column(Integer, primary_key=True, index=True)
    master_id = Column(Integer, ForeignKey("master_records.id", ondelete="CASCADE"), nullable=False)
    field_name = Column(String(120), nullable=False)
    previous_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    changed_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    changed_by = Column(String(120), nullable=True)
    reason = Column(Text, nullable=True)

    master = relationship("MasterRecord", back_populates="change_history")


class OperationalEvent(Base):
    __tablename__ = "operational_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(80), nullable=False, index=True)
    event_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    reference_type = Column(String(120), nullable=True)
    reference_id = Column(Integer, nullable=True)
    payload = Column(JSON, default=dict)
    created_by = Column(String(120), nullable=True)
