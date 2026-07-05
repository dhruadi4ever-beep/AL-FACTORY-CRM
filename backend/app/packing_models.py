from __future__ import annotations

import datetime
from typing import Any

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Parcel(Base):
    __tablename__ = "parcels"

    id = Column(Integer, primary_key=True, index=True)
    parcel_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    parcel_code = Column(String(120), nullable=False, unique=True)
    total_pcs = Column(Float, nullable=False, default=0.0)
    status = Column(String(40), nullable=False, default="packed")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    created_by = Column(String(120), nullable=True)
    updated_by = Column(String(120), nullable=True)

    items = relationship("ParcelItem", back_populates="parcel", cascade="all, delete-orphan")


class ParcelItem(Base):
    __tablename__ = "parcel_items"

    id = Column(Integer, primary_key=True, index=True)
    parcel_id = Column(Integer, ForeignKey("parcels.id", ondelete="CASCADE"), nullable=False)
    item_id = Column(Integer, ForeignKey("master_records.id"), nullable=False)
    pcs_quantity = Column(Float, nullable=False, default=0.0)
    status = Column(String(40), nullable=False, default="packed")

    parcel = relationship("Parcel", back_populates="items")
    item = relationship("MasterRecord", foreign_keys=[item_id])
