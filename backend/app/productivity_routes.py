from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import MasterRecord
from app.productivity_models import FavoriteRecord, GlobalSearchIndex, QuickAction, RecentRecord
from app.productivity_schemas import FavoriteRecordResponse, NavigationSuggestion, QuickActionResponse, RecentRecordResponse, SearchResult

router = APIRouter(prefix="/productivity", tags=["productivity"])


@router.get("/search", response_model=list[SearchResult])
def global_search(q: str = Query(...), db: Session = Depends(get_db)):
    rows = []
    if q:
        for master in db.query(MasterRecord).filter((MasterRecord.code.ilike(f"%{q}%")) | (MasterRecord.name.ilike(f"%{q}%"))).limit(20).all():
            rows.append(SearchResult(entity_type=master.entity_type, entity_id=master.id, display_text=f"{master.code} - {master.name}", metadata_json={"route": f"/masters/{master.id}"}))
    return rows


@router.get("/quick-actions", response_model=list[QuickActionResponse])
def list_quick_actions(db: Session = Depends(get_db)):
    actions = [
        QuickAction(action_code="production", label="Production", target_route="/production"),
        QuickAction(action_code="inventory", label="Inventory", target_route="/inventory"),
        QuickAction(action_code="reports", label="Reports", target_route="/reports"),
    ]
    return [QuickActionResponse(id=action.id, action_code=action.action_code, label=action.label, target_route=action.target_route) for action in actions]


@router.get("/recent", response_model=list[RecentRecordResponse])
def recent_records(user_key: str = "default", db: Session = Depends(get_db)):
    records = db.query(RecentRecord).filter(RecentRecord.user_key == user_key).order_by(RecentRecord.created_at.desc()).limit(10).all()
    return [RecentRecordResponse(id=item.id, user_key=item.user_key, entity_type=item.entity_type, entity_id=item.entity_id, display_text=item.display_text) for item in records]


@router.get("/favorites", response_model=list[FavoriteRecordResponse])
def favorite_records(user_key: str = "default", db: Session = Depends(get_db)):
    records = db.query(FavoriteRecord).filter(FavoriteRecord.user_key == user_key).order_by(FavoriteRecord.created_at.desc()).limit(10).all()
    return [FavoriteRecordResponse(id=item.id, user_key=item.user_key, entity_type=item.entity_type, entity_id=item.entity_id, display_text=item.display_text) for item in records]


@router.post("/recent")
def record_recent(entity_type: str, entity_id: int, display_text: str, user_key: str = "default", db: Session = Depends(get_db)):
    record = RecentRecord(user_key=user_key, entity_type=entity_type, entity_id=entity_id, display_text=display_text)
    db.add(record)
    db.commit()
    return {"status": "ok"}


@router.post("/favorites")
def record_favorite(entity_type: str, entity_id: int, display_text: str, user_key: str = "default", db: Session = Depends(get_db)):
    record = FavoriteRecord(user_key=user_key, entity_type=entity_type, entity_id=entity_id, display_text=display_text)
    db.add(record)
    db.commit()
    return {"status": "ok"}


@router.get("/navigation", response_model=list[NavigationSuggestion])
def navigation_suggestions(entity_type: str, entity_id: int, db: Session = Depends(get_db)):
    return [NavigationSuggestion(entity_type=entity_type, entity_id=entity_id, display_text="Related record", route=f"/{entity_type}/{entity_id}")]
