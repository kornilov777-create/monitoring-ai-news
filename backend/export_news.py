"""
Standalone скрипт: сбор новостей + экспорт в JSON для GitHub Pages.
Запуск: python export_news.py
"""
import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings
from app.database import init_db, SessionLocal
from app.models.article import Article
from app.models.source import Source
from app.services.collector import collect_all
from sqlalchemy.orm import joinedload

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

DATA_DIR = settings.BASE_DIR / "data"


def export_news():
    """Экспортировать новости из БД в JSON-файлы."""
    db = SessionLocal()
    try:
        # Последние 200 статей
        articles = (
            db.query(Article)
            .options(joinedload(Article.source))
            .order_by(Article.published_at.desc())
            .limit(200)
            .all()
        )

        news = []
        for a in articles:
            news.append({
                "id": a.id,
                "title": a.title,
                "url": a.url,
                "summary": (a.summary or "")[:300],
                "author": a.author or "",
                "source": a.source.name if a.source else "",
                "published_at": a.published_at.isoformat() if a.published_at else "",
            })

        # Источники
        sources_list = db.query(Source).filter(Source.is_active == True).all()
        sources = []
        for s in sources_list:
            sources.append({
                "id": s.id,
                "name": s.name,
                "url": s.url,
                "articles_count": s.articles_count or 0,
                "last_checked": s.last_checked.isoformat() if s.last_checked else "",
            })

        total_articles = db.query(Article).count()

        # Метаданные
        meta = {
            "updated_at": datetime.utcnow().isoformat() + "Z",
            "total_articles": total_articles,
            "exported_articles": len(news),
            "sources_count": len(sources),
        }

        # Записать файлы
        DATA_DIR.mkdir(exist_ok=True)

        with open(DATA_DIR / "news.json", "w", encoding="utf-8") as f:
            json.dump(news, f, ensure_ascii=False, indent=2)

        with open(DATA_DIR / "sources.json", "w", encoding="utf-8") as f:
            json.dump(sources, f, ensure_ascii=False, indent=2)

        with open(DATA_DIR / "meta.json", "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

        logger.info(
            f"Экспорт завершён: {len(news)} статей, {len(sources)} источников → data/"
        )

    finally:
        db.close()


async def main():
    logger.info("Инициализация БД...")
    init_db()

    logger.info("Сбор новостей...")
    result = await collect_all()
    logger.info(f"Сбор: {result}")

    logger.info("Экспорт в JSON...")
    export_news()

    logger.info("Готово!")


if __name__ == "__main__":
    asyncio.run(main())
