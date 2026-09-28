"""租户安全查询与分页助手（SQLAlchemy 无隐式全局过滤器，需显式过滤）。"""
from typing import TypeVar

from sqlalchemy import Select, func, select

from app.core.context import get_current_tenant
from app.models.base import Base, TenantMixin
from app.schemas.common import Page

M = TypeVar("M", bound=Base)


def secure_select(model):
    stmt = select(model)
    if issubclass(model, TenantMixin):
        tenant = get_current_tenant()
        if tenant is not None:
            stmt = stmt.where(model.tenant_id == tenant)
    return stmt


def paginate(db, stmt: Select, page: int, size: int, mapper=None) -> Page:
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = db.scalars(stmt.offset((page - 1) * size).limit(size)).all()
    items = [mapper(r) for r in rows] if mapper else list(rows)
    return Page(items=items, total=total, page=page, size=size)
