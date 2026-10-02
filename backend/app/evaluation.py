"""Evaluation contracts and readiness checks; this does not score model answers."""

from collections import Counter
from pathlib import Path
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator
from sqlalchemy.orm import Session

from app.knowledge import content_hash, latest_version
from app.models import Document


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


def validate_evaluations(path: Path, session: Session) -> dict:
    questions = []
    errors = []
    for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if 'TODO_MISSING_SOURCE' in line:
            errors.append(f'line {number}: TODO_MISSING_SOURCE，资料未就绪')
            continue
        try:
            questions.append(EvaluationQuestion.model_validate_json(line))
        except ValidationError as exc:
            errors.append(f'line {number}: ' + '; '.join(e['msg'] for e in exc.errors(include_input=False)))
    ids = [q.id for q in questions]
    if len(ids) != len(set(ids)):
        errors.append('评测 ID 必须唯一')
    if len(questions) != 20:
        errors.append(f'需要 20 题，实际有效题数 {len(questions)}')
    if Counter(q.category for q in questions) != Counter(concept=8, comparison=4, follow_up=3, unanswerable=3, personalized=2):
        errors.append('题型数量必须为 8/4/3/3/2')
    if Counter(q.split for q in questions) != Counter(dev=15, test=5):
        errors.append('开发集/独立测试集数量必须为 15/5')
    for source_id in sorted({str(s) for q in questions for s in q.expected_source_ids}):
        doc = session.get(Document, source_id, populate_existing=True)
        if doc is None:
            errors.append(f'{source_id}: TODO_MISSING_SOURCE，数据库不存在此资料')
        elif doc.status != 'published':
            errors.append(f'{source_id}: 资料未发布（{doc.status}）')
        else:
            version = latest_version(session, source_id)
            if version is None or not version.text.strip() or content_hash(version.text) != version.content_hash:
                errors.append(f'{source_id}: 正文缺失或哈希无效')
    return {'ready': not errors, 'total': len(questions), 'dev': sum(q.split == 'dev' for q in questions),
            'test': sum(q.split == 'test' for q in questions), 'errors': errors}
