"""Static import boundaries for real application code, including relative imports."""

import ast
import sys
from importlib.util import resolve_name
from pathlib import Path

import pytest

APP = Path(__file__).resolve().parents[1] / 'app'


def within(module, prefix):
    return module == prefix or module.startswith(prefix + '.')


def allowed(source, target):
    """Allow explicit public entry points; unknown external clients fail closed."""
    if target.split('.')[0] in sys.stdlib_module_names:
        return True
    if within(source, 'app.core'):
        return any(within(target, prefix) for prefix in ('app.core', 'pydantic', 'pydantic_settings'))
    if within(source, 'app.modules'):
        owner = '.'.join(source.split('.')[:3])
        if within(target, owner) or within(target, 'app.core') or within(target, 'pydantic'):
            return True
        module = owner.rsplit('.', 1)[-1]
        public = {
            'knowledge': ('app.infrastructure.orm', 'app.infrastructure.database', 'sqlalchemy'),
            'retrieval': ('app.modules.knowledge.service', 'app.modules.knowledge.evidence',
                          'app.modules.knowledge.schemas'),
            'answering': ('app.modules.knowledge.schemas', 'app.modules.retrieval.schemas'),
            'agent': tuple('app.modules.' + name + '.' + entry
                           for name in ('retrieval', 'answering', 'conversations')
                           for entry in ('service', 'schemas')),
            'conversations': ('app.infrastructure.orm', 'app.infrastructure.database', 'sqlalchemy'),
            'feedback': ('app.infrastructure.orm', 'app.infrastructure.database', 'sqlalchemy',
                         'app.modules.conversations.service', 'app.modules.conversations.schemas'),
            'evaluation': ('app.modules.knowledge.service', 'app.modules.knowledge.schemas',
                           'app.modules.retrieval.service', 'app.modules.retrieval.schemas',
                           'app.modules.agent.workflow', 'app.modules.agent.state',
                           'sqlalchemy.orm.Session'),
        }
        prefixes = public.get(module, ())
        if source == 'app.modules.knowledge.acquisition':
            prefixes += ('httpx', 'bs4')
        return any(within(target, prefix) for prefix in prefixes)
    if within(source, 'app.infrastructure'):
        if within(target, 'app.modules'):
            parts = target.split('.')
            return len(parts) >= 4 and parts[3] in ('ports', 'schemas')
        return any(within(target, prefix) for prefix in (
            'app.core', 'app.infrastructure', 'sqlalchemy', 'httpx', 'pymysql'))
    if source == 'app.main' or within(source, 'app.api') or within(source, 'app.cli'):
        if within(target, 'app.modules'):
            parts = target.split('.')
            if source == 'app.cli.reindex' and target == 'app.modules.retrieval.indexing.reindex_document':
                return True
            return len(parts) >= 4 and parts[3] in (
                'service', 'schemas', 'evidence', 'dataset', 'acquisition', 'workflow')
        return any(within(target, prefix) for prefix in (
            'app.core', 'app.infrastructure', 'app.api', 'app.cli.backup', 'fastapi', 'pydantic',
            'httpx', 'sqlalchemy.exc', 'sqlalchemy.orm.Session'))
    return False


def imports(path, module):
    package = module if path.name == '__init__.py' else module.rpartition('.')[0]
    for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield node.lineno, alias.name
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ''
            if node.level:
                base = resolve_name('.' * node.level + base, package)
            for alias in node.names:
                yield node.lineno, base + '.' + alias.name


def check_imports(app):
    modules = {}
    for path in app.rglob('*.py'):
        parts = list(path.relative_to(app.parent).with_suffix('').parts)
        if parts[-1] == '__init__':
            parts.pop()
        modules['.'.join(parts)] = path
    graph = {module: set() for module in modules}
    errors = []
    for source, path in modules.items():
        for line, target in imports(path, source):
            if target.endswith('.*') or not allowed(source, target):
                errors.append(f'{source}:{line} -> {target}')
            dependency = target
            while dependency and dependency not in modules:
                dependency = dependency.rpartition('.')[0]
            if dependency:
                graph[source].add(dependency)

    visited, active = set(), set()

    def visit(module):
        if module in active:
            errors.append(f'import cycle: {module}')
            return
        if module in visited:
            return
        active.add(module)
        for dependency in sorted(graph[module]):
            visit(dependency)
        active.remove(module)
        visited.add(module)

    for module in sorted(graph):
        visit(module)
    return errors


def test_application_import_boundaries():
    assert check_imports(APP) == []


@pytest.mark.parametrize(('module', 'statement'), [
    ('core/settings', 'from app.modules.knowledge import service'),
    ('modules/evaluation/dataset', 'from ..knowledge.models import Document'),
    ('modules/agent/workflow', 'from fastapi import Request'),
    ('modules/agent/workflow', 'from sqlalchemy.orm import Session'),
    ('modules/agent/workflow', 'import openai'),
    ('modules/retrieval/service', 'from ..knowledge import repository'),
    ('modules/answering/service', 'import httpx'),
    ('cli/documents', 'from app.modules.knowledge.models import Document'),
    ('infrastructure/database', 'from app.api import dependencies'),
    ('modules/knowledge/service', 'from app.knowledge import change_status'),
])
def test_checker_rejects_boundary_violations(tmp_path, module, statement):
    app = tmp_path / 'app'
    path = app / (module + '.py')
    path.parent.mkdir(parents=True)
    path.write_text(statement)
    assert check_imports(app)


def test_checker_rejects_import_cycles(tmp_path):
    app = tmp_path / 'app'
    core = app / 'core'
    core.mkdir(parents=True)
    (core / 'settings.py').write_text('from . import errors')
    (core / 'errors.py').write_text('from . import settings')
    assert any('import cycle' in error for error in check_imports(app))
