"""应用入口：只做装配（日志/CORS/异常/总路由/建表）。"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.config import settings
from app.core.exceptions import register_handlers
from app.database import engine
from app.models.base import Base


def _setup_logging() -> None:
    if not logging.getLogger("app").handlers:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def create_app() -> FastAPI:
    _setup_logging()
    app = FastAPI(title=settings.APP_NAME)
    app.add_middleware(
        CORSMiddleware, allow_origins=settings.CORS_ORIGINS, allow_credentials=True,
        allow_methods=["*"], allow_headers=["*"],
    )
    register_handlers(app)
    app.include_router(api_router, prefix="/api")

    @app.on_event("startup")
    def _startup() -> None:
        Base.metadata.create_all(bind=engine)

    return app


app = create_app()
