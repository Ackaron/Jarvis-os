from fastapi.testclient import TestClient

from interfaces.api import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_classify_presentation_for_intc():
    response = client.post(
        "/api/classify", json={"text": "Нужна презентация резидентов ИНТЦ"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["task_type"] == "presentation"
    assert data["domain"] == "intc"
    assert data["autonomous"] is False
    assert data["primary_model"] == "claude-opus"


def test_classify_unclassified_falls_back_to_other():
    response = client.post("/api/classify", json={"text": "просто зайди и посмотри"})
    assert response.status_code == 200
    assert response.json()["task_type"] == "other"


def test_classify_requires_text_field():
    response = client.post("/api/classify", json={})
    assert response.status_code == 422
