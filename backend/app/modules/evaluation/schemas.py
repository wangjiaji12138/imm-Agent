"""Evaluation question contracts; these do not score model answers."""

from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, model_validator


class Turn(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    role: Literal['user', 'assistant']
    content: str = Field(min_length=1)


class EvaluationQuestion(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    id: str = Field(min_length=1)
    category: Literal['concept', 'comparison', 'follow_up', 'unanswerable', 'personalized']
    split: Literal['dev', 'test']
    question: str = Field(min_length=1)
    expected_source_ids: list[UUID]
    required_points: list[str] = Field(min_length=1)
    forbidden_points: list[str] = Field(min_length=1)
    expected_behavior: Literal['answer', 'clarify', 'insufficient', 'refuse']
    history: list[Turn] = Field(default_factory=list)

    @model_validator(mode='after')
    def coherent(self):
        if any(not point.strip() for point in self.required_points + self.forbidden_points):
            raise ValueError('判断条件不能为空白')
        if len(set(self.expected_source_ids)) != len(self.expected_source_ids):
            raise ValueError('资料 ID 重复')
        if self.expected_behavior == 'answer' and not self.expected_source_ids:
            raise ValueError('可回答题必须引用资料')
        if self.category == 'follow_up' and not self.history:
            raise ValueError('多轮题必须提供 history')
        expected = {'concept': 'answer', 'comparison': 'answer',
                    'unanswerable': 'insufficient', 'personalized': 'refuse'}
        if self.category in expected and self.expected_behavior != expected[self.category]:
            raise ValueError('题目分类和预期行为不一致')
        if self.category == 'follow_up' and self.expected_behavior not in ('answer', 'clarify'):
            raise ValueError('多轮题必须回答或澄清')
        return self
