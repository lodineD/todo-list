from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./todos.db"
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173"]
    API_V1_PREFIX: str = "/api/v1"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()