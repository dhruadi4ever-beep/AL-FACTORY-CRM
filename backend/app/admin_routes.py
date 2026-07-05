from __future__ import annotations

import datetime
import os
import secrets
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.admin_models import AdminSession, AuditTrailEntry, SystemSetting
from app.admin_schemas import AdminLoginRequest, AdminSessionResponse, AuditTrailEntryResponse, BackupResponse, SystemSettingCreate, SystemSettingResponse
from app.database import get_db

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/auth/login", response_model=AdminSessionResponse)
def login(payload: AdminLoginRequest, db: Session = Depends(get_db)):
    expected_user = os.getenv("ADMIN_USERNAME", "admin")
    expected_password = os.getenv("ADMIN_PASSWORD", "admin123")
    if payload.username != expected_user or payload.password != expected_password:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")

    db.query(AdminSession).filter(AdminSession.is_active.is_(True)).update({"is_active": False})
    session = AdminSession(
        username=payload.username,
        session_token=secrets.token_urlsafe(16),
        expires_at=datetime.datetime.utcnow() + datetime.timedelta(hours=8),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    record_audit(payload.username, "admin_login", "session", session.id, {"username": payload.username}, db)
    return AdminSessionResponse(username=session.username, session_token=session.session_token, expires_at=session.expires_at.isoformat(), is_active=session.is_active)


@router.post("/auth/logout")
def logout(session_token: str, db: Session = Depends(get_db)):
    session = db.query(AdminSession).filter(AdminSession.session_token == session_token).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session.is_active = False
    db.commit()
    return {"status": "logged_out"}


@router.get("/settings", response_model=list[SystemSettingResponse])
def list_settings(db: Session = Depends(get_db)):
    return [serialize_setting(item) for item in db.query(SystemSetting).all()]


@router.put("/settings/{key}", response_model=SystemSettingResponse)
def update_setting(key: str, payload: SystemSettingCreate, db: Session = Depends(get_db)):
    setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    if not setting:
        setting = SystemSetting(key=key)
        db.add(setting)
    setting.value_json = payload.value_json
    setting.description = payload.description
    setting.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(setting)
    record_audit("admin", "update_setting", "setting", setting.id, {"key": key, "value": payload.value_json}, db)
    return serialize_setting(setting)


@router.get("/audit", response_model=list[AuditTrailEntryResponse])
def list_audit(db: Session = Depends(get_db)):
    entries = db.query(AuditTrailEntry).order_by(AuditTrailEntry.created_at.desc()).limit(100).all()
    return [serialize_audit(item) for item in entries]


@router.post("/backup", response_model=BackupResponse)
def create_backup(db: Session = Depends(get_db)):
    backup_id = str(uuid.uuid4())
    payload = {
        "settings": [serialize_setting(item).__dict__ for item in db.query(SystemSetting).all()],
        "audit": [serialize_audit(item).__dict__ for item in db.query(AuditTrailEntry).order_by(AuditTrailEntry.created_at.desc()).limit(100).all()],
    }
    record_audit("admin", "backup_created", "system", None, {"backup_id": backup_id}, db)
    return BackupResponse(backup_id=backup_id, created_at=datetime.datetime.utcnow().isoformat(), payload=payload)


@router.post("/restore")
def restore_backup(payload: dict[str, Any], db: Session = Depends(get_db)):
    for item in payload.get("settings", []):
        key = item.get("key")
        if not key:
            continue
        setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
        if not setting:
            setting = SystemSetting(key=key)
            db.add(setting)
        setting.value_json = item.get("value_json")
        setting.description = item.get("description")
        setting.updated_at = datetime.datetime.utcnow()
    db.commit()
    record_audit("admin", "restore_completed", "system", None, {"backup_id": payload.get("backup_id")}, db)
    return {"status": "restored"}


def record_audit(actor: str, action: str, entity_type: str | None, entity_id: int | None, changes: dict[str, Any], db: Session) -> None:
    entry = AuditTrailEntry(actor=actor, action=action, entity_type=entity_type, entity_id=entity_id, changes_json=changes, source="api")
    db.add(entry)
    db.commit()


def serialize_setting(setting: SystemSetting) -> SystemSettingResponse:
    return SystemSettingResponse(
        id=setting.id,
        key=setting.key,
        value_json=setting.value_json,
        description=setting.description,
        updated_at=setting.updated_at.isoformat(),
    )


def serialize_audit(entry: AuditTrailEntry) -> AuditTrailEntryResponse:
    return AuditTrailEntryResponse(
        id=entry.id,
        actor=entry.actor,
        action=entry.action,
        entity_type=entry.entity_type,
        entity_id=entry.entity_id,
        changes_json=entry.changes_json or {},
        created_at=entry.created_at.isoformat(),
        source=entry.source,
    )
