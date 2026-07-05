from __future__ import annotations

import datetime

from sqlalchemy import Column, DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class GlobalSearchIndex(Base):
    __tablename__ = "global_search_index"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(80), nullable=False)
    entity_id = Column(Integer, nullable=False)
    display_text = Column(String(255), nullable=False)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class QuickAction(Base):
    __tablename__ = "quick_actions"

    id = Column(Integer, primary_key=True, index=True)
    action_code = Column(String(80), nullable=False, unique=True)
    label = Column(String(160), nullable=False)
    target_route = Column(String(160), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class RecentRecord(Base):
    __tablename__ = "recent_records"

    id = Column(Integer, primary_key=True, index=True)
    user_key = Column(String(120), nullable=False)
    entity_type = Column(String(80), nullable=False)
    entity_id = Column(Integer, nullable=False)
    display_text = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class FavoriteRecord(Base):
    __tablename__ = "favorite_records"

    id = Column(Integer, primary_key=True, index=True)
    user_key = Column(String(120), nullable=False)
    entity_type = Column(String(80), nullable=False)
    entity_id = Column(Integer, nullable=False)
    display_text = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
