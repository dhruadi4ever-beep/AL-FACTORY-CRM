from __future__ import annotations

import datetime
from typing import Any

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class EmployeeAttendance(Base):
    __tablename__ = "employee_attendances"

    id = Column(Integer, primary_key=True, index=True)
    attendance_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    employee_id = Column(Integer, ForeignKey("master_records.id"), nullable=False)
    working_hours = Column(Float, nullable=False, default=0.0)
    attendance_status = Column(String(80), nullable=False, default="present")
    remarks = Column(Text, nullable=True)
    is_locked = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    created_by = Column(String(120), nullable=True)
    updated_by = Column(String(120), nullable=True)

    employee = relationship("MasterRecord", foreign_keys=[employee_id])


class EmployeeSalaryAdvance(Base):
    __tablename__ = "employee_salary_advances"

    id = Column(Integer, primary_key=True, index=True)
    advance_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    employee_id = Column(Integer, ForeignKey("master_records.id"), nullable=False)
    advance_amount = Column(Float, nullable=False, default=0.0)
    remarks = Column(Text, nullable=True)
    is_settled = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    created_by = Column(String(120), nullable=True)

    employee = relationship("MasterRecord", foreign_keys=[employee_id])


class WeeklySalaryCycle(Base):
    __tablename__ = "weekly_salary_cycles"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("master_records.id"), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    working_days = Column(Integer, nullable=False, default=0)
    total_working_hours = Column(Float, nullable=False, default=0.0)
    hourly_rate = Column(Float, nullable=False, default=0.0)
    gross_salary = Column(Float, nullable=False, default=0.0)
    status = Column(String(40), nullable=False, default="draft")
    finalization_date = Column(DateTime, nullable=True)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    created_by = Column(String(120), nullable=True)
    updated_by = Column(String(120), nullable=True)

    employee = relationship("MasterRecord", foreign_keys=[employee_id])


class SalaryAdvanceDeduction(Base):
    __tablename__ = "salary_advance_deductions"

    id = Column(Integer, primary_key=True, index=True)
    salary_cycle_id = Column(Integer, ForeignKey("weekly_salary_cycles.id"), nullable=False)
    advance_id = Column(Integer, ForeignKey("employee_salary_advances.id"), nullable=False)
    deduction_amount = Column(Float, nullable=False, default=0.0)
    deduction_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    remarks = Column(Text, nullable=True)

    salary_cycle = relationship("WeeklySalaryCycle", foreign_keys=[salary_cycle_id])
    advance = relationship("EmployeeSalaryAdvance", foreign_keys=[advance_id])


class SalaryLedgerEntry(Base):
    __tablename__ = "salary_ledger_entries"

    id = Column(Integer, primary_key=True, index=True)
    entry_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    employee_id = Column(Integer, ForeignKey("master_records.id"), nullable=False)
    transaction_type = Column(String(80), nullable=False)
    amount = Column(Float, nullable=False, default=0.0)
    reference_type = Column(String(120), nullable=True)
    reference_id = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    created_by = Column(String(120), nullable=True)

    employee = relationship("MasterRecord", foreign_keys=[employee_id])


class MachineAssignmentHistory(Base):
    __tablename__ = "machine_assignment_history"

    id = Column(Integer, primary_key=True, index=True)
    assignment_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    employee_id = Column(Integer, ForeignKey("master_records.id"), nullable=False)
    machine_id = Column(Integer, ForeignKey("master_records.id"), nullable=False)
    working_hours = Column(Float, nullable=False, default=0.0)
    notes = Column(Text, nullable=True)
    created_by = Column(String(120), nullable=True)

    employee = relationship("MasterRecord", foreign_keys=[employee_id])
    machine = relationship("MasterRecord", foreign_keys=[machine_id])
