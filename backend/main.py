import asyncio
import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
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


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiter per IP."""

    def __init__(self, app, max_requests: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = {}

    async def dispatch(self, request: Request, call_next) -> Response:
        import time

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        # Stricter limit for /api/collect
        if request.url.path == "/api/collect" and request.method == "POST":
            max_req = 2
            window = 3600  # 1 hour
        else:
            max_req = self.max_requests
            window = self.window_seconds

        key = f"{client_ip}:{request.url.path}" if max_req != self.max_requests else client_ip

        if key not in self._requests:
            self._requests[key] = []

        # Clean old entries
        self._requests[key] = [t for t in self._requests[key] if now - t < window]

        if len(self._requests[key]) >= max_req:
            return Response(
                content='{"error": "Too many requests"}',
                status_code=429,
                media_type="application/json",
            )

        self._requests[key].append(now)
        return await call_next(request)

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

# Security middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=60, window_seconds=60)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=["GET"],
    allow_headers=["Content-Type", "X-API-Key"],
)

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
