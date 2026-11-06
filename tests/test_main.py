import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from src.config import settings
from src.joke import router as joke_router
from src.main import app
from src.summary import client as summary_client
from src.summary import router as summary_router
from src.weather import client as weather_client
from src.weather import router as weather_router

client = TestClient(app)


@pytest.fixture(autouse=True)
def test_settings(monkeypatch):
    monkeypatch.setattr(settings, "app_api_key", "test-api-key")
    monkeypatch.setattr(settings, "max_summary_text_length", 5000)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_weather_endpoint(monkeypatch):
    async def fake_get_weather(city: str):
        return {
            "city": city,
            "temperature": 24.5,
            "condition": "Clear",
            "humidity": 45,
        }

    monkeypatch.setattr(
        weather_router, "get_weather_by_city", fake_get_weather)
    response = client.get("/weather?city=London")
    assert response.status_code == 200
    assert response.json()["city"] == "London"


def test_weather_returns_404_for_unknown_city(monkeypatch):
    class FakeAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_value, traceback):
            return None

        async def get(self, url, params, timeout):
            return SimpleNamespace(status_code=404)

    monkeypatch.setattr(weather_client.httpx, "AsyncClient", FakeAsyncClient)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(weather_client.get_weather_by_city("zzqvnotacity82931"))

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "City not found"


def test_joke_endpoint(monkeypatch):
    async def fake_get_joke():
        return {
            "joke": "Why did the chicken cross the road?",
            "category": "Programming",
        }

    monkeypatch.setattr(joke_router, "get_random_joke", fake_get_joke)
    response = client.get("/joke")
    assert response.status_code == 200
    assert response.json()["category"] == "Programming"


def test_summary_requires_api_key():
    response = client.post(
        "/summary", json={"text": "This is a sample text to summarize."}
    )
    assert response.status_code == 401


def test_summary_with_valid_key(monkeypatch):
    monkeypatch.setattr(
        summary_router, "generate_summary", lambda text: "Short summary output"
    )
    response = client.post(
        "/summary",
        json={"text": "This is a sample text to summarize."},
        headers={"X-API-Key": "test-api-key"},
    )
    assert response.status_code == 200
    assert response.json() == {"summary": "Short summary output"}


def test_summary_uses_langgraph(monkeypatch):
    def fake_invoke(state):
        assert "This is a sample text" in state["text"]
        return {"summary": "Graph summary"}

    monkeypatch.setattr(
        summary_client,
        "summary_graph",
        type("GraphStub", (), {"invoke": staticmethod(fake_invoke)})(),
        raising=False,
    )

    assert summary_client.generate_summary(
        "This is a sample text to summarize."
    ) == "Graph summary"


def test_summary_rejects_empty_text():
    response = client.post(
        "/summary",
        json={"text": "   "},
        headers={"X-API-Key": "test-api-key"},
    )
    assert response.status_code == 400
