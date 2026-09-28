"""pytest 夹具：内存 SQLite + StaticPool + 依赖覆盖 + TestClient。"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_db
from app.main import app as fastapi_app
from app.models.base import Base

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
Base.metadata.create_all(bind=engine)
TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


fastapi_app.dependency_overrides[get_db] = override_get_db


@pytest.fixture()
def db_session():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client() -> TestClient:
    return TestClient(fastapi_app)
