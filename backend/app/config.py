from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"

    # Database
    @property
    def DATABASE_URL(self) -> str:
        db_path = self.DATA_DIR / "ai_news.db"
        return f"sqlite:///{db_path}"

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # Monitoring
    COLLECT_INTERVAL_HOURS: int = 4
    MAX_ARTICLES_PER_SOURCE: int = 50

    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_OWNER_ID: int = 0

    class Config:
        env_file = ".env"


settings = Settings()
