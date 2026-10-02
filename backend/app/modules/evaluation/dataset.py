"""Validate dataset composition and published source readiness via knowledge service."""

from collections import Counter
from pathlib import Path
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.modules.evaluation.schemas import EvaluationQuestion
from app.modules.knowledge.service import source_readiness_error


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
        error = source_readiness_error(session, source_id)
        if error:
            errors.append(error)
    return {'ready': not errors, 'total': len(questions), 'dev': sum(q.split == 'dev' for q in questions),
            'test': sum(q.split == 'test' for q in questions), 'errors': errors}
