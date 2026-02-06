from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime
import hashlib

class BaseParser(ABC):
    """
    Базовый класс для всех парсеров новостных источников
    """

    def __init__(self, source_name: str, source_url: str):
        self.source_name = source_name
        self.source_url = source_url

    @abstractmethod
    async def fetch_articles(self) -> List[Dict]:
        """
        Получить список статей из источника
        Returns: List of dicts with keys: title, url, summary, author, published_at, content
        """
        pass

    def generate_content_hash(self, content: str) -> str:
        """Generate SHA256 hash for deduplication"""
        return hashlib.sha256(content.encode()).hexdigest()

    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        return " ".join(text.split()).strip()
