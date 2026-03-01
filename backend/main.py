import asyncio
import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn

from app.config import settings
from app.database import init_db
from app.api.routes import api_router
from app.tasks.scheduler import start_scheduler, stop_scheduler
from app.services.collector import collect_all

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# Бот запускается только если есть токен
_bot_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _bot_task

    # Startup
    logger.info("Инициализация базы данных...")
    init_db()

    logger.info("Первоначальный сбор новостей...")
    try:
        result = await collect_all()
        logger.info(f"Первый сбор: {result}")
    except Exception as e:
        logger.error(f"Ошибка первого сбора: {e}")

    # Запуск бота
    if settings.TELEGRAM_BOT_TOKEN:
        logger.info("Запуск Telegram-бота...")
        from app.bot.bot import start_bot, setup_digest_job
        setup_digest_job()
        _bot_task = asyncio.create_task(start_bot())
    else:
        logger.warning("TELEGRAM_BOT_TOKEN не задан — бот не запущен")

    # Запуск планировщика
    start_scheduler()

    yield

    # Shutdown
    stop_scheduler()
    if _bot_task:
        _bot_task.cancel()
        try:
            await _bot_task
        except asyncio.CancelledError:
            pass
    logger.info("Приложение остановлено")


app = FastAPI(title="AI News Monitor", lifespan=lifespan)
app.include_router(api_router)


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=False,
    )
