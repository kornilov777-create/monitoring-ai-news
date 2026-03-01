from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
)


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Основная клавиатура бота."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Последние новости"),
                KeyboardButton(text="Дайджест"),
            ],
            [
                KeyboardButton(text="Топ-20"),
                KeyboardButton(text="Источники"),
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
    )


def get_pagination_kb(page: int, total_pages: int, prefix: str = "page") -> InlineKeyboardMarkup:
    """Клавиатура пагинации."""
    buttons = []
    if page > 0:
        buttons.append(
            InlineKeyboardButton(text="← Назад", callback_data=f"{prefix}:{page - 1}")
        )
    if page < total_pages - 1:
        buttons.append(
            InlineKeyboardButton(text="Вперёд →", callback_data=f"{prefix}:{page + 1}")
        )

    if not buttons:
        return None

    return InlineKeyboardMarkup(inline_keyboard=[buttons])


def get_refresh_kb() -> InlineKeyboardMarkup:
    """Кнопка обновления."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Обновить", callback_data="refresh")]
        ]
    )
