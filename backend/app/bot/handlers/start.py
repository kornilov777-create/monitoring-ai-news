from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.bot.keyboards import get_main_keyboard

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "<b>AI News Monitor</b>\n\n"
        "Мониторинг новостей искусственного интеллекта "
        "из 8 ведущих мировых источников.\n\n"
        "Команды:\n"
        "/latest — последние 10 новостей\n"
        "/digest — дайджест за 24 часа\n"
        "/top20 — топ-20 новостей\n"
        "/sources — источники\n"
        "/collect — запустить сбор вручную\n"
        "/help — помощь",
        reply_markup=get_main_keyboard(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "<b>Справка</b>\n\n"
        "/latest — последние 10 новостей\n"
        "/digest — дайджест за последние 24 часа\n"
        "/top20 — топ-20 новостей за 48 часов\n"
        "/sources — список источников и статистика\n"
        "/collect — запустить сбор новостей вручную\n\n"
        "Новости собираются автоматически каждые 4 часа.\n"
        "Утренний дайджест приходит в 10:00 МСК.",
        reply_markup=get_main_keyboard(),
    )
