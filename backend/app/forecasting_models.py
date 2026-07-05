from __future__ import annotations

import datetime
from typing import Any

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class ForecastRecord(Base):
    __tablename__ = "forecast_records"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("production_plans.id", ondelete="CASCADE"), nullable=False)
    machine_id = Column(Integer, ForeignKey("master_records.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("master_records.id"), nullable=False)
    running_hours = Column(Float, nullable=False, default=0.0)
    standard_time_per_bunch_minutes = Column(Float, nullable=False, default=0.0)
    forecast_bunches = Column(Float, nullable=False, default=0.0)
    actual_bunches = Column(Float, nullable=False, default=0.0)
    difference_bunches = Column(Float, nullable=False, default=0.0)
    forecast_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    plan = relationship("ProductionPlan", backref="forecast")
    machine = relationship("MasterRecord", foreign_keys=[machine_id])
    item = relationship("MasterRecord", foreign_keys=[item_id])


class ForecastAlert(Base):
    __tablename__ = "forecast_alerts"

    id = Column(Integer, primary_key=True, index=True)
    forecast_id = Column(Integer, ForeignKey("forecast_records.id", ondelete="CASCADE"), nullable=False)
    alert_type = Column(String(80), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(40), nullable=False, default="info")
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    forecast = relationship("ForecastRecord", backref="alerts")
