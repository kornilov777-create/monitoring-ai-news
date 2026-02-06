from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    url = Column(String(500), nullable=False)
    feed_url = Column(String(500))
    source_type = Column(String(50))
    category = Column(String(100))

    # Ratings
    authority_score = Column(Float, default=0.0)
    update_frequency_score = Column(Float, default=0.0)
    content_quality_score = Column(Float, default=0.0)
    significance_score = Column(Float, default=0.0)
    rss_availability_score = Column(Float, default=0.0)
    overall_rating = Column(Float, default=0.0)

    description = Column(Text)
    is_active = Column(Boolean, default=True)
    last_checked = Column(DateTime)
    articles_count = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    articles = relationship("Article", back_populates="source")
