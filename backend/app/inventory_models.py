from __future__ import annotations

import datetime
from typing import Any

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class StockLedgerEntry(Base):
    __tablename__ = "stock_ledger_entries"

    id = Column(Integer, primary_key=True, index=True)
    entry_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    item_id = Column(Integer, ForeignKey("master_records.id"), nullable=False)
    transaction_type = Column(String(80), nullable=False)
    quantity = Column(Float, nullable=False, default=0.0)
    unit = Column(String(40), nullable=False)
    source_stage = Column(String(80), nullable=True)
    destination_stage = Column(String(80), nullable=True)
    reference_transaction = Column(String(120), nullable=True)
    notes = Column(Text, nullable=True)
    created_by = Column(String(120), nullable=True)

    item = relationship("MasterRecord", foreign_keys=[item_id])


class InventoryBalance(Base):
    __tablename__ = "inventory_balances"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("master_records.id"), nullable=False, unique=True)
    produced_inventory = Column(Float, nullable=False, default=0.0)
    job_work_in_progress = Column(Float, nullable=False, default=0.0)
    finished_goods = Column(Float, nullable=False, default=0.0)
    packed_inventory = Column(Float, nullable=False, default=0.0)
    dispatched_inventory = Column(Float, nullable=False, default=0.0)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    item = relationship("MasterRecord", foreign_keys=[item_id])


class StockAdjustment(Base):
    __tablename__ = "stock_adjustments"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("master_records.id"), nullable=False)
    adjustment_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    stage = Column(String(80), nullable=False)
    difference_quantity = Column(Float, nullable=False, default=0.0)
    reason = Column(Text, nullable=True)
    created_by = Column(String(120), nullable=True)

    item = relationship("MasterRecord", foreign_keys=[item_id])
