"""全局配置（pydantic-settings）与路径常量。"""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BACKEND_DIR / "data"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env", extra="ignore")

    APP_NAME: str = "{{PROJECT_NAME}}"
    DATABASE_URL: str = "sqlite:///" + str(DATA_DIR / "app.db")
    JWT_SECRET: str = "change-me-in-prod"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    # CORS：开发环境 uni-app/H5 直连需要放行；生产由网关统一处理
    CORS_ORIGINS: list[str] = ["*"]


settings = Settings()
