from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str = ""

    # JWT
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Database
    database_url: str = "sqlite+aiosqlite:///./app.db"

    # API
    api_host: str = "127.0.0.1"
    api_port: int = 8000

    # SMTP (for email tool)
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_address: str = ""
    smtp_use_tls: bool = True

    # Workspace
    workspace_dir: str = "workspace"

    # Social Media APIs
    instagram_access_token: str = ""
    instagram_business_account_id: str = ""
    twitter_api_key: str = ""
    twitter_api_secret: str = ""
    twitter_access_token: str = ""
    twitter_access_token_secret: str = ""
    linkedin_access_token: str = ""
    linkedin_person_id: str = ""
    facebook_access_token: str = ""
    facebook_page_id: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
