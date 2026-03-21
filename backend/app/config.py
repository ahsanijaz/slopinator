from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./slopinator.db"
    GROK_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    TIKTOK_CLIENT_KEY: str = ""
    TIKTOK_CLIENT_SECRET: str = ""
    TIKTOK_ACCESS_TOKEN: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
