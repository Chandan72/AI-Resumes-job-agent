from __future__ import annotations

import os
import datetime as dt
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Float,
    UniqueConstraint,
    create_engine,
    text,
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/news.db")

# Ensure data directory exists for sqlite file path like data/news.db
if DATABASE_URL.startswith("sqlite"):
    db_path = DATABASE_URL.split("///")[-1]
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(1024), nullable=False)
    url = Column(String(2048), nullable=False, index=True)
    summary = Column(String(8192), nullable=True)
    published_at = Column(DateTime, nullable=True, index=True)
    source = Column(String(128), nullable=False, index=True)

    industry = Column(String(256), nullable=True, index=True)
    confidence = Column(Float, nullable=True)

    created_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow, index=True)

    __table_args__ = (
        UniqueConstraint("url", name="uq_articles_url"),
    )


class MetaKV(Base):
    __tablename__ = "meta_kv"

    id = Column(Integer, primary_key=True)
    k = Column(String(255), unique=True, nullable=False, index=True)
    v = Column(String(4096), nullable=True)
    updated_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db_session() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def upsert_meta(db: Session, key: str, value: str) -> None:
    existing = db.query(MetaKV).filter(MetaKV.k == key).one_or_none()
    now = dt.datetime.utcnow()
    if existing:
        existing.v = value
        existing.updated_at = now
    else:
        entry = MetaKV(k=key, v=value, updated_at=now)
        db.add(entry)
    db.commit()


def get_meta(db: Session, key: str) -> Optional[str]:
    row = db.query(MetaKV).filter(MetaKV.k == key).one_or_none()
    return row.v if row else None


def insert_articles(db: Session, articles: List[Dict[str, Any]]) -> int:
    """Insert articles; ignore duplicates by URL. Returns number inserted."""
    inserted = 0
    for art in articles:
        try:
            article = Article(
                title=art.get("title", "").strip()[:1024],
                url=art.get("url", "").strip()[:2048],
                summary=(art.get("summary") or None),
                published_at=art.get("published_at"),
                source=art.get("source", "unknown"),
                industry=art.get("industry"),
                confidence=art.get("confidence"),
            )
            db.add(article)
            db.commit()
            inserted += 1
        except Exception:
            db.rollback()
            # Likely unique constraint violation or other error; skip
            continue
    return inserted


def fetch_industry_counts(db: Session) -> Dict[str, int]:
    rows = db.execute(text(
        """
        SELECT COALESCE(industry, 'Uncategorized') as industry, COUNT(1) as cnt
        FROM articles
        GROUP BY COALESCE(industry, 'Uncategorized')
        """
    ))
    return {r[0]: r[1] for r in rows}


def fetch_recent_articles_by_industry(db: Session, industry: Optional[str], limit: int = 5) -> List[Dict[str, Any]]:
    q = db.query(Article)
    if industry:
        q = q.filter(Article.industry == industry)
    q = q.order_by(Article.published_at.desc().nullslast(), Article.created_at.desc()).limit(limit)
    results = []
    for a in q.all():
        results.append({
            "id": a.id,
            "title": a.title,
            "url": a.url,
            "summary": a.summary,
            "published_at": a.published_at.isoformat() if a.published_at else None,
            "source": a.source,
            "industry": a.industry,
            "confidence": a.confidence,
        })
    return results


def fetch_articles(db: Session, industry: Optional[str] = None, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
    q = db.query(Article)
    if industry:
        q = q.filter(Article.industry == industry)
    q = q.order_by(Article.published_at.desc().nullslast(), Article.created_at.desc())
    q = q.offset(offset).limit(limit)
    results = []
    for a in q.all():
        results.append({
            "id": a.id,
            "title": a.title,
            "url": a.url,
            "summary": a.summary,
            "published_at": a.published_at.isoformat() if a.published_at else None,
            "source": a.source,
            "industry": a.industry,
            "confidence": a.confidence,
        })
    return results