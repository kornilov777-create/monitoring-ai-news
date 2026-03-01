from datetime import datetime
from typing import List

from app.models.article import Article


def format_article(article: Article, index: int = 0) -> str:
    """Форматировать одну статью для Telegram (HTML)."""
    source_name = article.source.name if article.source else "Неизвестно"
    date_str = ""
    if article.published_at:
        date_str = article.published_at.strftime("%d.%m %H:%M")

    summary = (article.summary or "")[:200]
    if len(article.summary or "") > 200:
        summary += "..."

    prefix = f"<b>{index}.</b> " if index else ""
    lines = [
        f'{prefix}<a href="{article.url}">{_escape(article.title)}</a>',
        f"<i>{source_name}</i> | {date_str}",
    ]
    if summary:
        lines.append(f"{_escape(summary)}")

    return "\n".join(lines)


def format_article_list(articles: List[Article], title: str = "") -> str:
    """Форматировать список статей."""
    if not articles:
        return "Новостей пока нет."

    parts = []
    if title:
        parts.append(f"<b>{title}</b>\n")

    for i, article in enumerate(articles, 1):
        parts.append(format_article(article, index=i))

    return "\n\n".join(parts)


def format_digest(articles: List[Article]) -> str:
    """Форматировать дайджест."""
    if not articles:
        return "За последнее время новых AI-новостей не найдено."

    now = datetime.utcnow()
    header = f"<b>AI Дайджест</b> | {now.strftime('%d.%m.%Y')}\n"
    header += f"Найдено новостей: {len(articles)}\n"

    parts = [header]
    for i, article in enumerate(articles, 1):
        source_name = article.source.name if article.source else ""
        date_str = article.published_at.strftime("%H:%M") if article.published_at else ""
        parts.append(
            f'{i}. <a href="{article.url}">{_escape(article.title)}</a>\n'
            f"   <i>{source_name}</i> {date_str}"
        )

    return "\n".join(parts)


def format_sources(sources) -> str:
    """Форматировать список источников."""
    if not sources:
        return "Источники не настроены."

    parts = ["<b>Источники новостей:</b>\n"]
    for s in sources:
        count = s.articles_count or 0
        checked = ""
        if s.last_checked:
            checked = f" | обновлено {s.last_checked.strftime('%d.%m %H:%M')}"
        parts.append(f"• <b>{s.name}</b> — {count} статей{checked}")

    return "\n".join(parts)


def _escape(text: str) -> str:
    """Экранировать HTML-символы для Telegram."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
