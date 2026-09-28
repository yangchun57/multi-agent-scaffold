"""engine / SessionLocal / get_db；before_flush 自动填充 tenant_id。"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.core.context import get_current_tenant
from app.models.base import TenantMixin

_connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(settings.DATABASE_URL, connect_args=_connect_args, future=True, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, future=True)


def _autofill_tenant(session, _ctx, instances):
    for obj in instances:
        if isinstance(obj, TenantMixin) and getattr(obj, "tenant_id", None) is None:
            tenant = get_current_tenant()
            if tenant is not None:
                obj.tenant_id = tenant


event.listen(SessionLocal, "before_flush", _autofill_tenant)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
