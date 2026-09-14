from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_tutorials() -> None:
    response = client.get("/tutorials")
    assert response.status_code == 200
    assert response.json()["tutorials"] == ["getting-started"]
