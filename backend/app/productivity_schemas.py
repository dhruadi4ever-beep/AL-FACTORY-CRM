from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel


class SearchResult(BaseModel):
    entity_type: str
    entity_id: int
    display_text: str
    metadata_json: dict[str, Any]


class QuickActionResponse(BaseModel):
    id: int
    action_code: str
    label: str
    target_route: str

    class Config:
        from_attributes = True


class RecentRecordResponse(BaseModel):
    id: int
    user_key: str
    entity_type: str
    entity_id: int
    display_text: str

    class Config:
        from_attributes = True


class FavoriteRecordResponse(BaseModel):
    id: int
    user_key: str
    entity_type: str
    entity_id: int
    display_text: str

    class Config:
        from_attributes = True


class NavigationSuggestion(BaseModel):
    entity_type: str
    entity_id: int
    display_text: str
    route: str
