from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional, List

class SourceBase(BaseModel):
    name: str
    url: str
    feed_url: Optional[str] = None
    source_type: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None

class SourceCreate(SourceBase):
    pass

class SourceUpdate(BaseModel):
    authority_score: Optional[float] = None
    update_frequency_score: Optional[float] = None
    content_quality_score: Optional[float] = None
    significance_score: Optional[float] = None
    rss_availability_score: Optional[float] = None

class SourceResponse(SourceBase):
    id: int
    overall_rating: float
    authority_score: float
    update_frequency_score: float
    content_quality_score: float
    significance_score: float
    rss_availability_score: float
    is_active: bool
    articles_count: int
    last_checked: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ArticleBase(BaseModel):
    title: str
    url: str
    summary: Optional[str] = None
    author: Optional[str] = None
    published_at: datetime
    image_url: Optional[str] = None

class ArticleCreate(ArticleBase):
    source_id: int
    content: Optional[str] = None
    content_hash: Optional[str] = None

class ArticleResponse(ArticleBase):
    id: int
    source_id: int
    fetched_at: datetime
    source: SourceResponse

    class Config:
        from_attributes = True
