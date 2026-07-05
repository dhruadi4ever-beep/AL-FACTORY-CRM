from __future__ import annotations

import datetime
import secrets

from sqlalchemy import Boolean, Column, DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class SystemSetting(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(120), nullable=False, unique=True)
    value_json = Column(JSON, default=dict)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class AuditTrailEntry(Base):
    __tablename__ = "audit_trail_entries"

    id = Column(Integer, primary_key=True, index=True)
    actor = Column(String(120), nullable=False)
    action = Column(String(120), nullable=False)
    entity_type = Column(String(120), nullable=True)
    entity_id = Column(Integer, nullable=True)
    changes_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    source = Column(String(80), nullable=True)


class AdminSession(Base):
    __tablename__ = "admin_sessions"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(120), nullable=False)
    session_token = Column(String(255), nullable=False, unique=True)
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
