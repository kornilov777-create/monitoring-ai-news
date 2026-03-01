from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.article import Article
from app.models.source import Source
from app.services.collector import collect_all

router = APIRouter(prefix="/api", tags=["articles"])


@router.get("/articles")
def list_articles(
    source_id: Optional[int] = None,
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Article).options(joinedload(Article.source))
    if source_id:
        query = query.filter(Article.source_id == source_id)
    articles = (
        query.order_by(Article.published_at.desc()).offset(offset).limit(limit).all()
    )
    return {
        "count": len(articles),
        "articles": [_article_to_dict(a) for a in articles],
    }


@router.get("/articles/latest")
def latest_articles(
    limit: int = Query(default=10, le=50),
    db: Session = Depends(get_db),
):
    articles = (
        db.query(Article)
        .options(joinedload(Article.source))
        .order_by(Article.published_at.desc())
        .limit(limit)
        .all()
    )
    return {"count": len(articles), "articles": [_article_to_dict(a) for a in articles]}


@router.get("/articles/top")
def top_articles(
    hours: int = Query(default=24, le=168),
    limit: int = Query(default=20, le=50),
    db: Session = Depends(get_db),
):
    """Топ статей за последние N часов (по дате публикации)."""
    since = datetime.utcnow() - timedelta(hours=hours)
    articles = (
        db.query(Article)
        .options(joinedload(Article.source))
        .filter(Article.published_at >= since)
        .order_by(Article.published_at.desc())
        .limit(limit)
        .all()
    )
    return {"count": len(articles), "articles": [_article_to_dict(a) for a in articles]}


@router.get("/sources")
def list_sources(db: Session = Depends(get_db)):
    sources = db.query(Source).filter(Source.is_active == True).all()
    return {
        "count": len(sources),
        "sources": [
            {
                "id": s.id,
                "name": s.name,
                "url": s.url,
                "category": s.category,
                "articles_count": s.articles_count or 0,
                "last_checked": s.last_checked.isoformat() if s.last_checked else None,
            }
            for s in sources
        ],
    }


@router.post("/collect")
async def trigger_collect():
    """Ручной запуск сбора новостей."""
    result = await collect_all()
    return result


def _article_to_dict(a: Article) -> dict:
    return {
        "id": a.id,
        "title": a.title,
        "url": a.url,
        "summary": (a.summary or "")[:300],
        "author": a.author,
        "source": a.source.name if a.source else None,
        "published_at": a.published_at.isoformat() if a.published_at else None,
    }
