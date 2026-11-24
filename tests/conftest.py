import os
os.environ["DATABASE_URL"] = "sqlite:///./pytest_tmp.db"
os.environ["JWT_SECRET_KEY"] = "TEST_ONLY_SECRET_WITH_ENOUGH_LENGTH_987654321"
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.core.limiter import limiter

engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestSession = sessionmaker(bind=engine, expire_on_commit=False)

@pytest.fixture
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    def db_override():
        with TestSession() as db:
            yield db
    app.dependency_overrides[get_db] = db_override
    limiter.reset()
    with patch("app.modules.todos.router.notify_todo_created.delay") as enqueue:
        enqueue.return_value.id = "test-job-id"
        with TestClient(app) as test_client:
            yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def logged_in(client):
    client.post("/auth/register", json={"email": "alice@example.com", "password": "Password123"})
    resp = client.post("/auth/login", data={"username": "alice@example.com", "password": "Password123"})
    assert resp.status_code == 200
    return {"Authorization": "Bearer " + resp.json()["access_token"]}
