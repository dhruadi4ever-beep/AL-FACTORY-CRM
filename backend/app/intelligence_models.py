from __future__ import annotations

import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, JSON, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class IntelligenceAlert(Base):
    __tablename__ = "intelligence_alerts"

    id = Column(Integer, primary_key=True, index=True)
    severity = Column(String(20), nullable=False, default="info")
    category = Column(String(80), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=False)
    related_entity_type = Column(String(80), nullable=True)
    related_entity_id = Column(Integer, nullable=True)
    data_json = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    is_acknowledged = Column(Boolean, default=False, nullable=False)
    source = Column(String(80), nullable=True)

    def __getattribute__(self, name: str) -> object:
        if name == "metadata":
            return object.__getattribute__(self, "data_json") or {}
        return object.__getattribute__(self, name)

    def __setattr__(self, name: str, value: object) -> None:
        if name == "metadata":
            object.__setattr__(self, "data_json", value or {})
            return
        object.__setattr__(self, name, value)


class DailyFactorySummary(Base):
    __tablename__ = "daily_factory_summaries"

    id = Column(Integer, primary_key=True, index=True)
    summary_date = Column(DateTime, nullable=False)
    factory_health_score = Column(Integer, nullable=False, default=0)
    active_masters = Column(Integer, nullable=False, default=0)
    active_employees = Column(Integer, nullable=False, default=0)
    active_job_workers = Column(Integer, nullable=False, default=0)
    active_machines = Column(Integer, nullable=False, default=0)
    pending_jobs = Column(Integer, nullable=False, default=0)
    production_bunches = Column(Float, nullable=False, default=0.0)
    finished_goods = Column(Float, nullable=False, default=0.0)
    pending_payments = Column(Float, nullable=False, default=0.0)
    alert_count = Column(Integer, nullable=False, default=0)
    summary_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class DecisionSupportRecommendation(Base):
    __tablename__ = "decision_support_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    scenario_name = Column(String(120), nullable=False)
    recommendation_type = Column(String(80), nullable=False)
    recommendation_text = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False, default=0.0)
    data_json = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    def __getattribute__(self, name: str) -> object:
        if name == "metadata":
            return object.__getattribute__(self, "data_json") or {}
        return object.__getattribute__(self, name)

    def __setattr__(self, name: str, value: object) -> None:
        if name == "metadata":
            object.__setattr__(self, "data_json", value or {})
            return
        object.__setattr__(self, name, value)
