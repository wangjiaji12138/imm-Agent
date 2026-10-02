"""Conversation credentials, bounded history and reference resolution."""

import json

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api.dependencies import ChatRuntime, get_chat_runtime, source_session
from app.infrastructure.orm import Base
from app.main import app
from app.modules.answering.ports import ModelOutput
from app.modules.conversations import models  # noqa: F401


class RoutingProvider:
    def __init__(self):
        self.inputs = []

    def complete(self, system, user):
        data = json.loads(user)
        self.inputs.append(data)
        question = data["question"]
        if question == "它与 PD-L1 有什么关系？":
            query = "PD-1 与 PD-L1 有什么关系？" if data["history"] else None
            body = ({"result_type": "search", "response": None, "search_query": query}
                    if query else {"result_type": "clarify", "response": "你说的“它”指什么？", "search_query": None})
        else:
            body = {"result_type": "search", "response": None, "search_query": question}
        return ModelOutput(content=json.dumps(body, ensure_ascii=False), model="fake")


def test_three_turns_topic_switch_and_isolation():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    provider = RoutingProvider()
    searched = []

    def search(query):
        searched.append(query)
        return []

    app.dependency_overrides[get_chat_runtime] = lambda: ChatRuntime(provider, search, lambda: Session(engine))
    client = TestClient(app)
    try:
        first = client.post("/api/chat", json={"message": "什么是 PD-1？"}).json()
        assert first["conversation_id"] and first["conversation_token"]
        conversation_id, token = first["conversation_id"], first["conversation_token"]
        headers = {"X-Conversation-Token": token}
        second = client.post("/api/chat", headers=headers, json={"message": "它与 PD-L1 有什么关系？",
                                                               "conversation_id": conversation_id})
        assert second.status_code == 200
        assert searched[-1] == "PD-1 与 PD-L1 有什么关系？"
        third = client.post("/api/chat", headers=headers, json={"message": "CAR-T 如何识别癌细胞？",
                                                              "conversation_id": conversation_id})
        assert third.status_code == 200
        assert searched[-1] == "CAR-T 如何识别癌细胞？"
        assert len(provider.inputs[-1]["history"]) == 2
        assert second.json()["conversation_token"] is None
        with Session(engine) as session:
            from app.modules.conversations.models import Message, Conversation
            assert session.query(Message).filter_by(conversation_id=conversation_id).count() == 3
            assert session.query(Conversation).count() == 1
            assert token not in session.get(Conversation, conversation_id).credential_hash

        for bad_headers in ({}, {"X-Conversation-Token": "wrong"}):
            rejected = client.post("/api/chat", headers=bad_headers,
                                   json={"message": "继续解释", "conversation_id": conversation_id})
            assert rejected.status_code == 404
        fresh = client.post("/api/chat", json={"message": "它与 PD-L1 有什么关系？"})
        assert fresh.status_code == 200
        assert fresh.json()["result_type"] == "clarify"
        assert fresh.json()["conversation_id"] != conversation_id
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_feedback_ownership_validation_and_idempotent_update():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    from app.modules.feedback import models as feedback_models  # noqa: F401
    Base.metadata.create_all(engine)
    provider = RoutingProvider()
    app.dependency_overrides[get_chat_runtime] = lambda: ChatRuntime(provider, lambda _: [], lambda: Session(engine))

    def feedback_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[source_session] = feedback_session
    client = TestClient(app)
    try:
        answer = client.post("/api/chat", json={"message": "什么是 PD-1？"}).json()
        headers = {"X-Conversation-ID": answer["conversation_id"],
                   "X-Conversation-Token": answer["conversation_token"]}
        body = {"request_id": answer["request_id"], "rating": "helpful", "note": "清晰"}
        assert client.post("/api/feedback", headers=headers, json=body).status_code == 200
        body.update(rating="not_helpful", note="还需要更多解释")
        changed = client.post("/api/feedback", headers=headers, json=body)
        assert changed.status_code == 200
        assert changed.json()["rating"] == "not_helpful"
        with Session(engine) as session:
            from app.modules.feedback.models import Feedback
            rows = session.query(Feedback).all()
            assert len(rows) == 1
            assert rows[0].note == "还需要更多解释"
        assert client.post("/api/feedback", headers=headers,
                           json={**body, "request_id": "00000000-0000-0000-0000-000000000000"}).status_code == 404
        assert client.post("/api/feedback", headers={**headers, "X-Conversation-Token": "wrong"},
                           json=body).status_code == 404
        assert client.post("/api/feedback", headers=headers, json={**body, "note": "x" * 501}).status_code == 422
        assert client.post("/api/feedback", headers=headers, json={**body, "extra": True}).status_code == 422
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
