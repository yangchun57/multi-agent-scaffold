"""认证授权依赖：get_current_user / require_role / require_admin。"""
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.context import get_current_tenant, set_current_tenant
from app.core.security import decode_token

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(credentials=Depends(bearer_scheme)) -> dict:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="未认证或登录已过期")
    try:
        payload = decode_token(credentials.credentials)
    except jwt.PyJWTError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="未认证或登录已过期") from exc
    tenant = payload.get("tenant_id")
    if tenant is not None:
        set_current_tenant(int(tenant))
    return {"user_id": payload.get("sub"), "role": payload.get("role", ""), "tenant_id": tenant}


def current_tenant_id():
    return get_current_tenant()


def require_role(role: str):
    def checker(user: dict = Depends(get_current_user)) -> dict:
        if user.get("role") != role:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="权限不足")
        return user
    return checker


require_admin = require_role("admin")
