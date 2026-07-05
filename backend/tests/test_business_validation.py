import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.admin_models import AuditTrailEntry, Base as AdminBase
from app.business_validation import BusinessRuleEngine, BusinessValidationError, ValidationContext
from app.models import Base as MainBase, OperationalEvent


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:")
    MainBase.metadata.create_all(engine)
    AdminBase.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    session = Session()
    try:
        yield session
    finally:
        session.close()


def test_engine_persists_and_records_audit_on_success(db_session):
    engine = BusinessRuleEngine()

    result = engine.execute(
        db_session,
        ValidationContext(
            entity_type="operational_event",
            actor="tester",
            payload={"event_type": "test"},
            input_validator=lambda payload: [],
            master_validator=lambda context: [],
            business_rule_validator=lambda context: [],
            inventory_validator=lambda context: [],
            persister=lambda context: OperationalEvent(event_type=context.payload["event_type"], created_by=context.actor),
        ),
    )

    assert isinstance(result, OperationalEvent)
    assert db_session.query(OperationalEvent).count() == 1
    assert db_session.query(AuditTrailEntry).count() == 1


def test_engine_rolls_back_when_inventory_validation_fails(db_session):
    engine = BusinessRuleEngine()

    with pytest.raises(BusinessValidationError):
        engine.execute(
            db_session,
            ValidationContext(
                entity_type="inventory_adjustment",
                actor="tester",
                payload={"quantity": -5},
                input_validator=lambda payload: [],
                master_validator=lambda context: [],
                business_rule_validator=lambda context: [],
                inventory_validator=lambda context: ["Inventory cannot go negative"],
                persister=lambda context: OperationalEvent(event_type="inventory", created_by=context.actor),
            ),
        )

    assert db_session.query(OperationalEvent).count() == 0
    assert db_session.query(AuditTrailEntry).count() == 0
