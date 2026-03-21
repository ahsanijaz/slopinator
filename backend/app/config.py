from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./slopinator.db"
    GROK_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    TIKTOK_CLIENT_KEY: str = ""
    TIKTOK_CLIENT_SECRET: str = ""
    TIKTOK_ACCESS_TOKEN: str = ""
    TIKTOK_REDIRECT_URI: str = "http://localhost:8000/api/tiktok/callback"
    ADMIN_PASSWORD: str = "admin"
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8  # 8 hours

    class Config:
        env_file = ".env"


settings = Settings()
