import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import settings
from app.bot.handlers.start import router as start_router
from app.bot.handlers.news import router as news_router
from app.bot.middleware import OwnerMiddleware
from app.tasks.scheduler import set_digest_sender

logger = logging.getLogger(__name__)

bot = Bot(
    token=settings.TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

dp = Dispatcher()
dp.message.middleware(OwnerMiddleware())
dp.include_router(start_router)
dp.include_router(news_router)


async def start_bot():
    """Запустить polling бота."""
    logger.info("Telegram-бот запущен")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"Ошибка бота: {e}")


async def send_digest_to_owner():
    """Отправить дайджест владельцу."""
    from datetime import datetime, timedelta
    from sqlalchemy.orm import joinedload
    from app.database import SessionLocal
    from app.models.article import Article
    from app.bot.formatters import format_digest

    if not settings.TELEGRAM_OWNER_ID:
        return

    db = SessionLocal()
    try:
        since = datetime.utcnow() - timedelta(hours=24)
        articles = (
            db.query(Article)
            .options(joinedload(Article.source))
            .filter(Article.published_at >= since)
            .order_by(Article.published_at.desc())
            .limit(20)
            .all()
        )

        text = format_digest(articles)
        # Telegram ограничивает длину сообщения 4096 символов
        if len(text) > 4000:
            text = text[:4000] + "\n\n..."

        await bot.send_message(
            chat_id=settings.TELEGRAM_OWNER_ID,
            text=text,
            disable_web_page_preview=True,
        )
        logger.info(f"Дайджест отправлен: {len(articles)} статей")
    except Exception as e:
        logger.error(f"Ошибка отправки дайджеста: {e}")
    finally:
        db.close()


def setup_digest_job():
    """Зарегистрировать дайджест в планировщике."""
    set_digest_sender(send_digest_to_owner)
