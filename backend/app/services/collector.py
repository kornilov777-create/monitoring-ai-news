import logging
from datetime import datetime
from typing import List

from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.models.article import Article
from app.models.source import Source
from app.services.parsers.openai_blog import OpenAIBlogParser
from app.services.parsers.google_ai import GoogleAIParser
from app.services.parsers.mit_news import MITNewsParser
from app.services.parsers.mit_tech_review import MITTechReviewParser
from app.services.parsers.techcrunch import TechCrunchParser
from app.services.parsers.the_verge import TheVergeParser
from app.services.parsers.venturebeat import VentureBeatParser
from app.services.parsers.ai_news import AINewsParser

logger = logging.getLogger(__name__)

# Реестр всех парсеров
PARSERS = [
    OpenAIBlogParser,
    GoogleAIParser,
    MITNewsParser,
    MITTechReviewParser,
    TechCrunchParser,
    TheVergeParser,
    VentureBeatParser,
    AINewsParser,
]


def seed_sources(db: Session) -> None:
    """Создать источники при первом запуске."""
    for parser_cls in PARSERS:
        parser = parser_cls()
        existing = db.query(Source).filter(Source.name == parser.source_name).first()
        if not existing:
            source = Source(
                name=parser.source_name,
                url=parser.source_url,
                feed_url=parser.feed_url,
                source_type="rss",
                category="AI",
                is_active=True,
            )
            db.add(source)
            logger.info(f"Добавлен источник: {parser.source_name}")
    db.commit()


async def collect_all() -> dict:
    """Собрать статьи со всех активных источников."""
    db = SessionLocal()
    try:
        seed_sources(db)

        total_found = 0
        total_new = 0
        errors = []

        sources = db.query(Source).filter(Source.is_active == True).all()
        source_map = {s.name: s for s in sources}

        for parser_cls in PARSERS:
            parser = parser_cls()
            source = source_map.get(parser.source_name)
            if not source:
                continue

            try:
                articles = await parser.fetch_articles()
                articles = articles[:settings.MAX_ARTICLES_PER_SOURCE]
                total_found += len(articles)

                new_count = _save_articles(db, source, articles)
                total_new += new_count

                source.last_checked = datetime.utcnow()
                source.articles_count = (
                    db.query(Article).filter(Article.source_id == source.id).count()
                )
                db.commit()

                logger.info(
                    f"{parser.source_name}: найдено {len(articles)}, новых {new_count}"
                )
            except Exception as e:
                errors.append(f"{parser.source_name}: {e}")
                logger.error(f"Ошибка сбора {parser.source_name}: {e}")

        result = {
            "total_found": total_found,
            "total_new": total_new,
            "errors": errors,
        }
        logger.info(
            f"Сбор завершён: найдено {total_found}, новых {total_new}, "
            f"ошибок {len(errors)}"
        )
        return result
    finally:
        db.close()


def _save_articles(db: Session, source: Source, articles: List[dict]) -> int:
    """Сохранить статьи с дедупликацией по URL."""
    new_count = 0
    for data in articles:
        url = data.get("url", "").strip()
        if not url:
            continue

        existing = db.query(Article).filter(Article.url == url).first()
        if existing:
            continue

        content = data.get("content", "") or data.get("summary", "") or ""
        article = Article(
            source_id=source.id,
            title=data.get("title", "")[:500],
            url=url,
            summary=(data.get("summary", "") or "")[:2000],
            content=content,
            author=data.get("author", ""),
            published_at=data.get("published_at", datetime.utcnow()),
            content_hash=_hash(content),
        )
        db.add(article)
        new_count += 1

    if new_count:
        db.commit()
    return new_count


def _hash(text: str) -> str:
    import hashlib
    return hashlib.sha256((text or "").encode()).hexdigest()
