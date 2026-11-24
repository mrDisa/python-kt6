from app.db.models import User
from tests.conftest import TestSession

def test_auth_and_conflict(client):
    body = {"email": "alice@example.com", "password": "Password123"}
    first = client.post("/auth/register", json=body)
    assert first.status_code == 201
    assert first.json()["role"] == "user"
    assert client.post("/auth/register", json=body).status_code == 409
    assert client.get("/auth/me").status_code == 401
    assert client.post("/auth/login", data={"username": body["email"], "password": body["password"]}).status_code == 200

def test_rbac(client, logged_in):
    assert client.get("/auth/admin", headers=logged_in).status_code == 403
    with TestSession() as db:
        obj = db.query(User).filter_by(email="alice@example.com").one()
        obj.role = "admin"; db.commit()
    assert client.get("/auth/admin", headers=logged_in).status_code == 200

def test_project_todo_and_queue(client, logged_in):
    project = client.post("/projects", headers=logged_in, json={"name": "Demo", "description": "KT6"})
    assert project.status_code == 201
    pid = project.json()["id"]
    assert len(client.get("/projects", headers=logged_in).json()) == 1
    created = client.post("/todos", headers=logged_in, json={"project_id": pid, "title": "Write tests"})
    assert created.status_code == 201
    assert created.json()["notification_task_id"] == "test-job-id"
    todo_id = created.json()["todo"]["id"]
    assert client.patch(f"/todos/{todo_id}", headers=logged_in, json={"is_done": True}).json()["is_done"] is True
    assert len(client.get(f"/todos?project_id={pid}", headers=logged_in).json()) == 1
    assert client.delete(f"/todos/{todo_id}", headers=logged_in).status_code == 204
    assert client.delete(f"/projects/{pid}", headers=logged_in).status_code == 204

def test_isolation(client, logged_in):
    pid = client.post("/projects", headers=logged_in, json={"name": "Private"}).json()["id"]
    client.post("/auth/register", json={"email": "bob@example.com", "password": "Password123"})
    token = client.post("/auth/login", data={"username": "bob@example.com", "password": "Password123"}).json()["access_token"]
    bob = {"Authorization": "Bearer " + token}
    assert client.get(f"/projects/{pid}", headers=bob).status_code == 403
    assert client.get("/projects", headers=bob).json() == []

def test_login_limit(client):
    for _ in range(5):
        assert client.post("/auth/login", data={"username": "nobody@example.com", "password": "bad"}).status_code == 401
    assert client.post("/auth/login", data={"username": "nobody@example.com", "password": "bad"}).status_code == 429

def test_cors(client):
    allowed = client.options("/auth/login", headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "POST"})
    assert allowed.headers.get("access-control-allow-origin") == "http://localhost:3000"
    denied = client.options("/auth/login", headers={"Origin": "https://bad.example", "Access-Control-Request-Method": "POST"})
    assert denied.headers.get("access-control-allow-origin") is None
