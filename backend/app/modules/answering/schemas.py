"""Strict response contracts for grounded answers and request routing."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Citation(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    chunk_id: str = Field(min_length=1)
    claim: str = Field(min_length=1)


class AnswerResult(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, frozen=True)

    result_type: Literal["answer", "clarify", "insufficient", "refuse", "out_of_scope", "emergency"]
    answer: str = Field(min_length=1)
    citations: list[Citation]
    evidence_status: Literal["sufficient", "insufficient", "conflicting", "not_applicable"]
    follow_up_question: str | None

    @model_validator(mode="after")
    def coherent(self):
        if self.result_type == "answer":
            if self.evidence_status not in ("sufficient", "conflicting") or not self.citations:
                raise ValueError("回答需要充分或冲突证据及引用")
        elif self.result_type == "insufficient":
            if self.evidence_status not in ("insufficient", "conflicting") or not self.answer.startswith("当前资料不足以回答这个问题。"):
                raise ValueError("证据不足响应格式无效")
        elif self.evidence_status != "not_applicable" or self.citations:
            raise ValueError("非知识结论响应不能附带引用")
        if self.result_type == "clarify":
            if self.follow_up_question != self.answer:
                raise ValueError("澄清问题必须与回答一致")
        elif self.follow_up_question is not None:
            raise ValueError("非澄清响应不能附带追问")
        return self


class RouteResult(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    result_type: Literal["search", "clarify", "refuse", "out_of_scope", "emergency"]
    response: str | None = None
    search_query: str | None = None

    @model_validator(mode="after")
    def coherent(self):
        if self.result_type == "search" and self.response is not None:
            raise ValueError("检索分支不能包含响应")
        if self.result_type == "search" and self.search_query is not None and not 2 <= len(self.search_query) <= 500:
            raise ValueError("独立检索问题长度无效")
        if self.result_type != "search" and not self.response:
            raise ValueError("分流响应不能为空")
        if self.result_type != "search" and self.search_query is not None:
            raise ValueError("非检索分支不能包含检索问题")
        return self
