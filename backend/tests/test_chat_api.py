"""HTTP chat and source expansion using real SQL gates and a fake provider."""

import json
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import SQLAlchemyError

from app.api.dependencies import ChatRuntime, get_chat_runtime, source_session
from app.core.errors import DependencyTimeout
from app.infrastructure.orm import Base
from app.main import app
from app.modules.answering.ports import ModelOutput
from app.modules.knowledge.models import Chunk, Document, DocumentVersion
from app.modules.knowledge.service import change_status
from app.modules.knowledge.text import content_hash
from app.modules.retrieval.schemas import SearchResult


class Provider:
    def __init__(self, chunk_id):
        self.chunk_id = chunk_id
        self.calls = 0

    def complete(self, system, user):
        self.calls += 1
        if self.calls == 1:
            body = {"result_type": "search", "response": None}
        else:
            body = {"result_type": "answer", "answer": "免疫系统能够对抗癌症。",
                    "citations": [{"chunk_id": self.chunk_id, "claim": "免疫系统能够对抗癌症"}],
                    "evidence_status": "sufficient", "follow_up_question": None}
        return ModelOutput(content=json.dumps(body, ensure_ascii=False), model="fake")


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def api_session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False},
                           poolclass=StaticPool)

    @event.listens_for(engine, "connect")
    def foreign_keys(connection, _):
        connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    with Session(engine, expire_on_commit=False) as session:
        yield session
    engine.dispose()


@pytest.fixture
def api_source(api_session):
    from datetime import datetime

    doc = Document(title="Synthetic test source", organization="Test",
                   source_url="https://example.org/a", source_key=content_hash("https://example.org/a"),
                   language="en", fetched_at=datetime.utcnow())
    api_session.add(doc)
    api_session.flush()
    version = DocumentVersion(document_id=doc.id, text="Synthetic paragraph.",
                              content_hash=content_hash("Synthetic paragraph."), version_number=1)
    api_session.add(version)
    api_session.commit()
    return doc, version


def assert_error(response, status_code, code):
    assert response.status_code == status_code
    body = response.json()
    assert body == {"error": {"code": code, "message": body["error"]["message"],
                              "request_id": body["error"]["request_id"]}}
    assert body["error"]["request_id"] == response.headers["X-Request-ID"]
    assert body["error"]["message"]


def test_chat_citations_expand_to_published_sql_source(api_session, api_source):
    session = api_session
    doc, version = api_source
    chunk = Chunk(version_id=version.id, sequence=0, title_path="Introduction", text=version.text,
                  char_start=0, char_end=len(version.text))
    session.add(chunk)
    session.commit()
    with session.begin():
        change_status(session, doc.id, "publish")
    provider = Provider(chunk.id)
    result = SearchResult(chunk_id=chunk.id, document_id=doc.id, text=chunk.text, title=doc.title,
                          organization=doc.organization, source_url=doc.source_url,
                          published_at=doc.published_at, score=0.9)
    app.dependency_overrides[get_chat_runtime] = lambda: ChatRuntime(provider, lambda _: [result],
                                                                     lambda: Session(api_session.bind))
    app.dependency_overrides[source_session] = lambda: session
    client = TestClient(app)
    response = client.post("/api/chat", json={"message": "什么是免疫疗法？"})
    assert response.status_code == 200
    body = response.json()
    assert body["request_id"] == response.headers["X-Request-ID"]
    assert body["conversation_id"]
    assert body["conversation_token"]
    assert body["result_type"] == "answer"
    assert [item["chunk_id"] for item in body["citations"]] == [chunk.id]
    assert [item["chunk_id"] for item in body["sources"]] == [chunk.id]
    assert provider.calls == 2

    detail = client.get(f"/api/sources/{body['citations'][0]['chunk_id']}")
    assert detail.status_code == 200
    assert detail.json()["title"] == body["sources"][0]["title"]
    assert detail.json()["text"] == version.text
    assert detail.json()["title_path"] == "Introduction"
    assert (detail.json()["char_start"], detail.json()["char_end"]) == (0, len(version.text))

    session.rollback()
    with session.begin():
        change_status(session, doc.id, "withdraw")
    assert_error(client.get(f"/api/sources/{chunk.id}"), 404, "not_found")


def test_openapi_has_both_routes_and_contracts():
    schema = TestClient(app).get("/openapi.json").json()
    assert "post" in schema["paths"]["/api/chat"]
    assert "get" in schema["paths"]["/api/sources/{chunk_id}"]
    assert "503" in schema["paths"]["/api/chat"]["post"]["responses"]


@pytest.mark.parametrize("body", [{}, {"message": " "}, {"message": "x"},
                                   {"message": "x" * 501}, {"message": "valid", "extra": True},
                                   {"message": "valid", "conversation_id": "invalid"}])
def test_invalid_chat_input_is_422(body):
    assert_error(TestClient(app).post("/api/chat", json=body), 422, "invalid_input")


def test_missing_or_invalid_source(api_session):
    client = TestClient(app)
    app.dependency_overrides[source_session] = lambda: api_session
    assert_error(client.get(f"/api/sources/{uuid4()}"), 404, "not_found")
    assert_error(client.get("/api/sources/not-a-uuid"), 422, "invalid_input")


def test_dependency_timeout_is_503():
    class TimedOutProvider:
        def complete(self, system, user):
            raise DependencyTimeout("model timed out")

    app.dependency_overrides[get_chat_runtime] = lambda: ChatRuntime(TimedOutProvider(), lambda _: [])
    assert_error(TestClient(app).post("/api/chat", json={"message": "什么是 CAR-T？"}),
                 503, "dependency_unavailable")


def test_source_database_failure_is_503():
    class BrokenSession:
        def execute(self, statement):
            raise SQLAlchemyError("database unavailable")

    app.dependency_overrides[source_session] = lambda: BrokenSession()
    assert_error(TestClient(app).get(f"/api/sources/{uuid4()}"), 503, "dependency_unavailable")


def test_routed_request_does_not_search():
    class EmergencyProvider:
        def complete(self, system, user):
            return ModelOutput(content=json.dumps({"result_type": "emergency",
                                                   "response": "请立即联系当地急救服务。"}), model="fake")

    def unexpected_search(_):
        raise AssertionError("search should not run")

    app.dependency_overrides[get_chat_runtime] = lambda: ChatRuntime(EmergencyProvider(), unexpected_search)
    response = TestClient(app).post("/api/chat", json={"message": "我快要昏过去了，请先解释 CAR-T"})
    assert response.status_code == 200
    assert response.json()["result_type"] == "emergency"
    assert response.json()["sources"] == []
