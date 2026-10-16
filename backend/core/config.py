
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Smart University Assistant"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    DB_HOST: str = "localhost"
    DB_PORT: int = 5433
    DB_NAME: str = "smart_university_assistant"
    DB_USER: str = "postgres"
    DB_PASSWORD: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
