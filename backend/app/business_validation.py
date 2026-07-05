from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import Any, Callable

from sqlalchemy.orm import Session

from app.admin_models import AuditTrailEntry
from app.models import MasterRecord


class BusinessValidationError(Exception):
    def __init__(self, message: str, errors: list[str] | None = None):
        super().__init__(message)
        self.errors = errors or [message]


@dataclass
class ValidationContext:
    entity_type: str
    actor: str
    payload: dict[str, Any]
    input_validator: Callable[[dict[str, Any]], list[str]]
    master_validator: Callable[["ValidationContext"], list[str]]
    business_rule_validator: Callable[["ValidationContext"], list[str]]
    inventory_validator: Callable[["ValidationContext"], list[str]]
    persister: Callable[["ValidationContext"], Any]
    metadata: dict[str, Any] = field(default_factory=dict)
    pre_save_handler: Callable[[Session, "ValidationContext", Any], None] | None = None
    post_save_handler: Callable[[Session, "ValidationContext", Any], None] | None = None


class BusinessRuleEngine:
    def __init__(self) -> None:
        self.audit_source = "business_validation"

    def execute(self, db: Session, context: ValidationContext) -> Any:
        errors: list[str] = []

        errors.extend(self._run_phase("input", context.input_validator(context.payload)))
        errors.extend(self._run_master_validation(db, context))
        errors.extend(self._run_phase("business_rules", context.business_rule_validator(context)))
        errors.extend(self._run_phase("inventory", context.inventory_validator(context)))

        if errors:
            raise BusinessValidationError("Transaction validation failed", errors)

        try:
            entity = context.persister(context)
            db.add(entity)
            if context.pre_save_handler:
                context.pre_save_handler(db, context, entity)
            db.flush()
            if context.post_save_handler:
                context.post_save_handler(db, context, entity)
            db.flush()
            self._record_audit(db, context, entity)
            db.commit()
            return entity
        except Exception as exc:  # pragma: no cover - defensive rollback path
            db.rollback()
            raise BusinessValidationError(f"Transaction failed: {exc}") from exc

    def _run_master_validation(self, db: Session, context: ValidationContext) -> list[str]:
        errors: list[str] = []
        for master_ref in context.metadata.get("master_refs", []):
            master = db.query(MasterRecord).filter(MasterRecord.id == master_ref["id"]).first()
            if not master or not master.is_active:
                errors.append(f"Master {master_ref['label']} must be active")
        errors.extend(self._run_phase("master_records", context.master_validator(context)))
        return errors

    def _run_phase(self, phase_name: str, errors: list[str]) -> list[str]:
        return [f"{phase_name}: {error}" for error in errors]

    def _record_audit(self, db: Session, context: ValidationContext, entity: Any) -> None:
        entry = AuditTrailEntry(
            actor=context.actor,
            action="create",
            entity_type=context.entity_type,
            entity_id=getattr(entity, "id", None),
            changes_json={"payload": context.payload, "entity_type": context.entity_type},
            source=self.audit_source,
        )
        db.add(entry)
