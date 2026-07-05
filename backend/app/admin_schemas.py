from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class SystemSettingCreate(BaseModel):
    key: str
    value_json: Any = None
    description: Optional[str] = None


class SystemSettingResponse(SystemSettingCreate):
    id: int
    updated_at: str

    class Config:
        from_attributes = True


class AuditTrailEntryResponse(BaseModel):
    id: int
    actor: str
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    changes_json: dict[str, Any] = Field(default_factory=dict)
    created_at: str
    source: Optional[str] = None

    class Config:
        from_attributes = True


class AdminLoginRequest(BaseModel):
    username: str
    password: str


class AdminSessionResponse(BaseModel):
    username: str
    session_token: str
    expires_at: str
    is_active: bool


class BackupResponse(BaseModel):
    backup_id: str
    created_at: str
    payload: dict[str, Any]
