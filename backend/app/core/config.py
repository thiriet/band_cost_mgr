import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Hongre API"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Configuration PostgreSQL (Ex: Neon.tech)
    # Exemple: postgresql://user:password@hostname:5432/dbname?sslmode=require
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./hongre_local.db")
    
    # Secrets & Sécurité
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super-secret-key-change-me-in-production")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 jours
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_WEBHOOK_SECRET: str = os.getenv("TELEGRAM_WEBHOOK_SECRET", "my-secret-webhook-token")
    
    # Gemini
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', case_sensitive=True)

settings = Settings()
