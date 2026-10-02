"""Answering contract with a deterministic fake model."""

import json

import pytest

from app.core.errors import DependencyTimeout
from app.modules.answering.ports import ModelOutput
from app.modules.answering.service import InvalidModelResponse, generate_answer, route_request
from app.modules.retrieval.schemas import SearchResult


def evidence(chunk_id="chunk-1", text="免疫疗法帮助免疫系统对抗癌症。"):
    return SearchResult(chunk_id=chunk_id, document_id="doc-1", text=text, title="资料标题",
                        organization="机构", source_url="https://example.org/a", published_at=None, score=0.9)


class FakeProvider:
    def __init__(self, *outputs):
        self.outputs = list(outputs)
        self.calls = []

    def complete(self, system, user):
        self.calls.append((system, user))
        next_output = self.outputs.pop(0)
        if isinstance(next_output, Exception):
            raise next_output
        return ModelOutput(content=json.dumps(next_output, ensure_ascii=False) if isinstance(next_output, dict)
                           else next_output, model="fake", input_tokens=8, output_tokens=10)


def answer(**overrides):
    result = {"result_type": "answer", "answer": "免疫疗法帮助免疫系统对抗癌症。",
              "citations": [{"chunk_id": "chunk-1", "claim": "帮助免疫系统对抗癌症"}],
              "evidence_status": "sufficient", "follow_up_question": None}
    return result | overrides


def test_grounded_answer_uses_only_supplied_evidence():
    provider = FakeProvider(answer())
    result = generate_answer("什么是免疫疗法？", [evidence()], provider)
    assert result.result_type == "answer"
    assert result.citations[0].chunk_id == "chunk-1"
    assert len(provider.calls) == 1
    assert json.loads(provider.calls[0][1])["evidence"][0]["text"] == evidence().text


def test_empty_retrieval_skips_model():
    provider = FakeProvider()
    result = generate_answer("什么是免疫疗法？", [], provider)
    assert result.result_type == "insufficient"
    assert result.answer.startswith("当前资料不足以回答这个问题。")
    assert provider.calls == []


@pytest.mark.parametrize("output", [answer(citations=[{"chunk_id": "invented", "claim": "伪造"}]),
                                      "not json", answer(citations=[]),
                                      answer(result_type="refuse", evidence_status="not_applicable", citations=[])])
def test_forged_or_malformed_response_fails_closed(output):
    with pytest.raises(InvalidModelResponse):
        generate_answer("什么是免疫疗法？", [evidence()], FakeProvider(output))


def test_timeout_retries_once():
    provider = FakeProvider(DependencyTimeout("timeout"), answer())
    assert generate_answer("什么是免疫疗法？", [evidence()], provider).result_type == "answer"
    assert len(provider.calls) == 2
    provider = FakeProvider(DependencyTimeout("timeout"), DependencyTimeout("timeout"))
    with pytest.raises(DependencyTimeout):
        generate_answer("什么是免疫疗法？", [evidence()], provider)
    assert len(provider.calls) == 2


def test_conflicting_sources_require_separate_citations():
    conflict = answer(evidence_status="conflicting", citations=[
        {"chunk_id": "chunk-1", "claim": "资料 A 的观点"},
        {"chunk_id": "chunk-2", "claim": "资料 B 的观点"}])
    results = [evidence(), evidence("chunk-2", "另一资料给出不同适用条件。")]
    assert generate_answer("两份资料的差异？", results, FakeProvider(conflict)).evidence_status == "conflicting"
    with pytest.raises(InvalidModelResponse):
        generate_answer("两份资料的差异？", results, FakeProvider(answer(evidence_status="conflicting")))


def test_pre_retrieval_routing():
    provider = FakeProvider({"result_type": "emergency", "response": "请立即联系当地急救服务或医疗机构。"})
    result = route_request("我呼吸困难，快昏过去了，还想问 CAR-T", provider)
    assert result.result_type == "emergency" and result.citations == []
    assert route_request("什么是 CAR-T？", FakeProvider({"result_type": "search", "response": None})) is None
    clarification = route_request("这个呢？", FakeProvider({"result_type": "clarify", "response": "你想了解哪个疗法或概念？"}))
    assert clarification.follow_up_question == clarification.answer
