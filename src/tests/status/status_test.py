from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.v1.status import router as status_router_module

app = FastAPI()
app.include_router(status_router_module.router)

client = TestClient(app)


def test_status_page_returns_online_payload(monkeypatch):
    monkeypatch.setattr(
        status_router_module,
        "get_db_status",
        lambda: {
            "status": "online",
            "database": "lysis",
            "current_user": "sa",
            "version": "SQL Server",
        },
    )

    response = client.get("/api/v1/status")

    assert response.status_code == 200
    assert response.json()["status"] == "online"


def test_status_page_returns_503_when_dependency_fails(monkeypatch):
    def raise_error():
        raise RuntimeError("database unavailable")

    monkeypatch.setattr(status_router_module, "get_db_status", raise_error)

    response = client.get("/api/v1/status")

    assert response.status_code == 503
    assert response.json() == {
        "status": "offline",
        "error": "database unavailable",
    }
