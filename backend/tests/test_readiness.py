"""Readiness endpoint contract tests."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import app, check_mysql, check_qdrant


@pytest.fixture(autouse=True)
def clear_dependency_overrides() -> Iterator[None]:
    yield
    app.dependency_overrides.clear()


def test_ready_when_all_dependencies_are_available() -> None:
    app.dependency_overrides[check_mysql] = lambda: True
    app.dependency_overrides[check_qdrant] = lambda: True

    response = TestClient(app).get("/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "checks": {"mysql": "ok", "qdrant": "ok"},
    }


def test_not_ready_identifies_each_unavailable_dependency() -> None:
    app.dependency_overrides[check_mysql] = lambda: False
    app.dependency_overrides[check_qdrant] = lambda: True

    response = TestClient(app).get("/ready")

    assert response.status_code == 503
    assert response.json() == {
        "status": "not_ready",
        "checks": {"mysql": "unavailable", "qdrant": "ok"},
    }

