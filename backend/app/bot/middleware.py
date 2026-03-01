from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message

from app.config import settings


class OwnerMiddleware(BaseMiddleware):
    """Пропускает только владельца бота."""

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        if not settings.TELEGRAM_OWNER_ID:
            return await handler(event, data)

        if event.from_user and event.from_user.id == settings.TELEGRAM_OWNER_ID:
            return await handler(event, data)

        await event.answer("Доступ запрещён.")
