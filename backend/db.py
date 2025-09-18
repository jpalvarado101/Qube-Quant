from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    DATABASE_URL: str = "sqlite:///./data/market.db"

settings = Settings()

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {},
    pool_pre_ping=True,
    future=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
