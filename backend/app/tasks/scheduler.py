import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.config import settings
from app.services.collector import collect_all

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

# Ссылка на функцию отправки дайджеста (устанавливается из bot.py)
_digest_sender = None


def set_digest_sender(func):
    """Зарегистрировать функцию отправки дайджеста."""
    global _digest_sender
    _digest_sender = func


async def _job_collect():
    """Задача сбора новостей."""
    logger.info("Запуск планового сбора новостей...")
    try:
        result = await collect_all()
        logger.info(f"Сбор завершён: {result}")
    except Exception as e:
        logger.error(f"Ошибка планового сбора: {e}")


async def _job_morning_digest():
    """Задача отправки утреннего дайджеста."""
    if _digest_sender:
        logger.info("Отправка утреннего дайджеста...")
        try:
            await _digest_sender()
        except Exception as e:
            logger.error(f"Ошибка отправки дайджеста: {e}")
    else:
        logger.warning("Функция отправки дайджеста не зарегистрирована")


def start_scheduler():
    """Запустить планировщик задач."""
    # Сбор новостей каждые N часов
    scheduler.add_job(
        _job_collect,
        IntervalTrigger(hours=settings.COLLECT_INTERVAL_HOURS),
        id="collect_news",
        replace_existing=True,
    )

    # Утренний дайджест в 07:00 UTC = 10:00 MSK
    scheduler.add_job(
        _job_morning_digest,
        CronTrigger(hour=7, minute=0),
        id="morning_digest",
        replace_existing=True,
    )

    scheduler.start()
    logger.info(
        f"Планировщик запущен: сбор каждые {settings.COLLECT_INTERVAL_HOURS}ч, "
        f"дайджест в 10:00 MSK"
    )


def stop_scheduler():
    """Остановить планировщик."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Планировщик остановлен")
