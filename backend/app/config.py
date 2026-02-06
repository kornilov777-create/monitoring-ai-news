from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///../data/ai_news.db"

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # Monitoring
    MONITORING_INTERVAL_HOURS: int = 24
    MAX_ARTICLES_PER_SOURCE: int = 50

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"

    class Config:
        env_file = ".env"

settings = Settings()
