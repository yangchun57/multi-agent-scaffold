"""总路由：各业务域在此集中 include_router，main.py 只挂载这一个 router。"""
from fastapi import APIRouter

from app.api.routes import health

api_router = APIRouter()
api_router.include_router(health.router)
