import asyncio
import feedparser
from typing import List, Dict
from datetime import datetime
from .base_parser import BaseParser
import logging

logger = logging.getLogger(__name__)

class RSSParser(BaseParser):
    """
    Универсальный парсер для RSS/Atom фидов
    """

    def __init__(self, source_name: str, source_url: str, feed_url: str):
        super().__init__(source_name, source_url)
        self.feed_url = feed_url

    async def fetch_articles(self) -> List[Dict]:
        articles = []

        try:
            feed = await asyncio.to_thread(feedparser.parse, self.feed_url)

            for entry in feed.entries:
                article = {
                    'title': self.clean_text(entry.get('title', '')),
                    'url': entry.get('link', ''),
                    'summary': self.clean_text(entry.get('summary', '')),
                    'author': entry.get('author', ''),
                    'published_at': self._parse_date(entry),
                    'content': self._extract_content(entry)
                }

                if article['url']:  # Only add if URL exists
                    articles.append(article)

        except Exception as e:
            logger.error(f"Error parsing RSS feed {self.feed_url}: {e}")

        return articles

    def _parse_date(self, entry) -> datetime:
        """Parse publication date from entry"""
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            return datetime(*entry.published_parsed[:6])
        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            return datetime(*entry.updated_parsed[:6])
        return datetime.utcnow()

    def _extract_content(self, entry) -> str:
        """Extract full content from entry"""
        if hasattr(entry, 'content') and entry.content:
            return self.clean_text(entry.content[0].value)
        elif hasattr(entry, 'summary'):
            return self.clean_text(entry.summary)
        return ""
