from __future__ import annotations

import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class JobWorkAssignment(Base):
    __tablename__ = "job_work_assignments"

    id = Column(Integer, primary_key=True, index=True)
    assignment_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    job_worker_id = Column(Integer, ForeignKey("master_records.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("master_records.id"), nullable=False)
    machine_source_id = Column(Integer, ForeignKey("master_records.id"), nullable=True)
    assigned_bunches = Column(Float, nullable=False, default=0.0)
    returned_pcs = Column(Float, nullable=False, default=0.0)
    pending_bunches = Column(Float, nullable=False, default=0.0)
    status = Column(String(40), nullable=False, default="in_progress")
    notes = Column(Text, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    completed_by = Column(String(120), nullable=True)
    completion_reason = Column(String(120), nullable=True)
    payment_record_id = Column(Integer, ForeignKey("job_work_pending_payments.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    created_by = Column(String(120), nullable=True)
    updated_by = Column(String(120), nullable=True)

    job_worker = relationship("MasterRecord", foreign_keys=[job_worker_id])
    item = relationship("MasterRecord", foreign_keys=[item_id])
    machine_source = relationship("MasterRecord", foreign_keys=[machine_source_id])
    payment_record = relationship("JobWorkPendingPayment", foreign_keys=[payment_record_id])


class JobWorkMovement(Base):
    __tablename__ = "job_work_movements"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("job_work_assignments.id", ondelete="CASCADE"), nullable=False)
    movement_type = Column(String(40), nullable=False)
    bunches = Column(Float, nullable=False, default=0.0)
    pcs = Column(Float, nullable=False, default=0.0)
    movement_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    notes = Column(Text, nullable=True)

    assignment = relationship("JobWorkAssignment", backref="movements")


class JobWorkPendingPayment(Base):
    __tablename__ = "job_work_pending_payments"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("job_work_assignments.id"), nullable=False)
    job_worker_id = Column(Integer, ForeignKey("master_records.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("master_records.id"), nullable=False)
    returned_bunches = Column(Float, nullable=False, default=0.0)
    total_strips = Column(Float, nullable=False, default=0.0)
    job_work_rate = Column(Float, nullable=False, default=0.0)
    payable_amount = Column(Float, nullable=False, default=0.0)
    amount_paid = Column(Float, nullable=False, default=0.0)
    outstanding_balance = Column(Float, nullable=False, default=0.0)
    status = Column(String(40), nullable=False, default="pending")
    payment_date = Column(DateTime, nullable=True)
    is_finalized = Column(Boolean, nullable=False, default=False)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    created_by = Column(String(120), nullable=True)

    assignment = relationship("JobWorkAssignment", foreign_keys=[assignment_id])
    job_worker = relationship("MasterRecord", foreign_keys=[job_worker_id])
    item = relationship("MasterRecord", foreign_keys=[item_id])


class JobWorkPaymentLedgerEntry(Base):
    __tablename__ = "job_work_payment_ledger_entries"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("job_work_pending_payments.id"), nullable=False)
    transaction_type = Column(String(80), nullable=False)
    transaction_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    amount = Column(Float, nullable=False, default=0.0)
    balance_after = Column(Float, nullable=False, default=0.0)
    notes = Column(Text, nullable=True)
    created_by = Column(String(120), nullable=True)

    payment = relationship("JobWorkPendingPayment", foreign_keys=[payment_id])
