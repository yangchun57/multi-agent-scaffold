"""请求级租户上下文（contextvar）。"""
from contextvars import ContextVar, Token

_current_tenant: ContextVar = ContextVar("current_tenant", default=None)


def set_current_tenant(tenant_id):
    return _current_tenant.set(tenant_id)


def reset_current_tenant(token: Token) -> None:
    _current_tenant.reset(token)


def get_current_tenant():
    return _current_tenant.get()
