from __future__ import annotations

import datetime
from typing import Any

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class ProductionRecord(Base):
    __tablename__ = "production_records"

    id = Column(Integer, primary_key=True, index=True)
    production_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    machine_id = Column(Integer, ForeignKey("master_records.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("master_records.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("master_records.id"), nullable=True)
    bunches = Column(Float, nullable=False, default=0.0)
    entry_timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    status = Column(String(40), nullable=False, default="available")
    is_locked = Column(Boolean, nullable=False, default=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    created_by = Column(String(120), nullable=True)
    updated_by = Column(String(120), nullable=True)

    machine = relationship("MasterRecord", foreign_keys=[machine_id])
    item = relationship("MasterRecord", foreign_keys=[item_id])
    employee = relationship("MasterRecord", foreign_keys=[employee_id])


class ProducedInventoryBalance(Base):
    __tablename__ = "produced_inventory_balances"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("master_records.id"), nullable=False)
    total_bunches = Column(Float, nullable=False, default=0.0)
    available_bunches = Column(Float, nullable=False, default=0.0)
    partially_assigned_bunches = Column(Float, nullable=False, default=0.0)
    fully_assigned_bunches = Column(Float, nullable=False, default=0.0)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    item = relationship("MasterRecord", foreign_keys=[item_id])
