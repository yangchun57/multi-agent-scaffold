"""健康检查路由（公开）。"""
from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/ping")
def ping() -> dict:
    return {"pong": True}
