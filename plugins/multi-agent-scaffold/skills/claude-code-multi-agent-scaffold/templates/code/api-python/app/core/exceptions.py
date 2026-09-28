"""业务异常与全局异常处理器（HTTPException 语义，符合 Python 规范 6.3）。"""
import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class BusinessException(HTTPException):
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST) -> None:
        super().__init__(status_code=status_code, detail=message)


def register_handlers(app: FastAPI) -> None:
    @app.exception_handler(BusinessException)
    async def _business(_request: Request, exc: BusinessException) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(Exception)
    async def _unhandled(_request: Request, exc: Exception) -> JSONResponse:
        logger.exception("未处理异常")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "服务器内部错误"})
