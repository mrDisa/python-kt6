from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite:///./local.db"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret_key: str = "DEV_ONLY_CHANGE_ME_BEFORE_DEPLOYMENT_1234567890"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def allowed_origins(self) -> list[str]:
        return [v.strip() for v in self.cors_origins.split(",") if v.strip()]

@lru_cache
def get_settings() -> Settings:
    return Settings()
