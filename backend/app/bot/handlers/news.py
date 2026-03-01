import math
from datetime import datetime, timedelta

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from sqlalchemy.orm import joinedload

from app.database import SessionLocal
from app.models.article import Article
from app.models.source import Source
from app.bot.formatters import format_article_list, format_digest, format_sources
from app.bot.keyboards import get_main_keyboard, get_pagination_kb, get_refresh_kb
from app.services.collector import collect_all

router = Router()

ARTICLES_PER_PAGE = 10


def _get_articles(limit: int = 10, offset: int = 0):
    db = SessionLocal()
    try:
        articles = (
            db.query(Article)
            .options(joinedload(Article.source))
            .order_by(Article.published_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        total = db.query(Article).count()
        # Eagerly load all needed data before closing session
        for a in articles:
            _ = a.source.name if a.source else None
        return articles, total
    finally:
        db.close()


def _get_articles_since(hours: int = 24, limit: int = 20):
    db = SessionLocal()
    try:
        since = datetime.utcnow() - timedelta(hours=hours)
        articles = (
            db.query(Article)
            .options(joinedload(Article.source))
            .filter(Article.published_at >= since)
            .order_by(Article.published_at.desc())
            .limit(limit)
            .all()
        )
        for a in articles:
            _ = a.source.name if a.source else None
        return articles
    finally:
        db.close()


def _get_sources():
    db = SessionLocal()
    try:
        sources = db.query(Source).filter(Source.is_active == True).all()
        # Force load before closing session
        for s in sources:
            _ = s.articles_count
        return sources
    finally:
        db.close()


# --- Команды ---


@router.message(Command("latest"))
@router.message(F.text == "Последние новости")
async def cmd_latest(message: Message):
    articles, total = _get_articles(limit=ARTICLES_PER_PAGE, offset=0)
    text = format_article_list(articles, title="Последние новости AI")
    total_pages = math.ceil(total / ARTICLES_PER_PAGE)
    kb = get_pagination_kb(0, total_pages, prefix="latest")

    if len(text) > 4000:
        text = text[:4000] + "\n\n..."

    await message.answer(text, reply_markup=kb, disable_web_page_preview=True)


@router.message(Command("digest"))
@router.message(F.text == "Дайджест")
async def cmd_digest(message: Message):
    articles = _get_articles_since(hours=24, limit=20)
    text = format_digest(articles)

    if len(text) > 4000:
        text = text[:4000] + "\n\n..."

    await message.answer(text, reply_markup=get_refresh_kb(), disable_web_page_preview=True)


@router.message(Command("top20"))
@router.message(F.text == "Топ-20")
async def cmd_top20(message: Message):
    articles = _get_articles_since(hours=48, limit=20)
    text = format_article_list(articles, title="Топ-20 AI новостей за 48 часов")

    if len(text) > 4000:
        text = text[:4000] + "\n\n..."

    await message.answer(text, reply_markup=get_refresh_kb(), disable_web_page_preview=True)


@router.message(Command("sources"))
@router.message(F.text == "Источники")
async def cmd_sources(message: Message):
    sources = _get_sources()
    text = format_sources(sources)
    await message.answer(text, disable_web_page_preview=True)


@router.message(Command("collect"))
async def cmd_collect(message: Message):
    msg = await message.answer("Запускаю сбор новостей...")
    try:
        result = await collect_all()
        await msg.edit_text(
            f"Сбор завершён!\n\n"
            f"Найдено статей: {result['total_found']}\n"
            f"Новых: {result['total_new']}\n"
            f"Ошибок: {len(result['errors'])}"
        )
    except Exception as e:
        await msg.edit_text(f"Ошибка сбора: {e}")


# --- Callbacks ---


@router.callback_query(F.data.startswith("latest:"))
async def cb_latest_page(callback: CallbackQuery):
    await callback.answer()
    page = int(callback.data.split(":")[1])
    offset = page * ARTICLES_PER_PAGE

    articles, total = _get_articles(limit=ARTICLES_PER_PAGE, offset=offset)
    total_pages = math.ceil(total / ARTICLES_PER_PAGE)

    text = format_article_list(articles, title=f"Новости AI (стр. {page + 1}/{total_pages})")
    kb = get_pagination_kb(page, total_pages, prefix="latest")

    if len(text) > 4000:
        text = text[:4000] + "\n\n..."

    await callback.message.edit_text(
        text, reply_markup=kb, disable_web_page_preview=True
    )


@router.callback_query(F.data == "refresh")
async def cb_refresh(callback: CallbackQuery):
    await callback.answer("Обновляю...")
    articles = _get_articles_since(hours=24, limit=20)
    text = format_digest(articles)

    if len(text) > 4000:
        text = text[:4000] + "\n\n..."

    await callback.message.edit_text(
        text, reply_markup=get_refresh_kb(), disable_web_page_preview=True
    )
