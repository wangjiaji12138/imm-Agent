"""Read-only validation of architecture paths, task coverage and local Markdown links.

Run from any working directory. Standard library only. This checks the design
inventory; backend/tests/test_architecture.py checks actual import boundaries.
"""

import ast
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {'.git', 'node_modules', '__pycache__', '.pytest_cache', '.venv',
            'venv', 'dist', 'build', 'raw', 'backups', 'artifacts', 'logs'}
LINK = re.compile(r'\[[^\]\n]*\]\((<[^>]+>|[^\s)]+)(?:\s+"[^"]*")?\)')
EXPECTED = {'01', '02', '03', '04', '10', '11', '12', '13', '20', '21', '22', '23',
            '30', '31', '32', '40', '41', '42', 'ARCH-01', 'ARCH-02'}


def walk_markdown(folder):
    for path in sorted(folder.iterdir()):
        if path.is_symlink() or path.name in EXCLUDED or path.name.endswith('.egg-info'):
            continue
        if path.is_dir():
            yield from walk_markdown(path)
        elif path.suffix == '.md':
            yield path


def check():
    errors = []
    entries = json.loads((ROOT / 'docs/architecture/layout.json').read_text())['entries']
    tasks = json.loads((ROOT / 'docs/tasks/catalog.json').read_text())
    if set(tasks) != EXPECTED:
        errors.append('任务目录未覆盖原 01—42 与 ARCH-01/02')
    seen = set()
    covered = set()
    for entry in entries:
        path = ROOT / entry['path']
        if path in seen:
            errors.append(f'重复文件条目：{entry["path"]}')
        seen.add(path)
        if not path.is_file() or not path.resolve().is_relative_to(ROOT):
            errors.append(f'缺少文件或路径越界：{entry["path"]}')
            continue
        if entry['status'] not in ('implemented', 'planned'):
            errors.append(f'未知状态：{entry["path"]}')
        content = path.read_text(encoding='utf-8')
        if entry['status'] == 'planned' and 'PLANNED' not in content:
            errors.append(f'占位标记缺失：{entry["path"]}')
        if not entry['tasks'] or set(entry['tasks']) - set(tasks):
            errors.append(f'任务关联无效：{entry["path"]}')
        covered.update(entry['tasks'])
        if path.suffix == '.py':
            try:
                ast.parse(content, filename=entry['path'])
            except SyntaxError as exc:
                errors.append(str(exc))
    if EXPECTED - covered:
        errors.append('缺少文件落点的任务：' + ', '.join(sorted(EXPECTED - covered)))
    for task, target in tasks.items():
        filename, anchor = target.split('#', 1)
        path = ROOT / filename
        if not path.is_file() or f'id="{anchor}"' not in path.read_text():
            errors.append(f'任务锚点缺失：{task}')
    for task in EXPECTED - {'ARCH-01', 'ARCH-02'}:
        cards = list((ROOT / 'docs/tasks').glob('*.md'))
        occurrences = sum(len(re.findall(r'^### '+task+r'｜', p.read_text(), re.M)) for p in cards)
        if occurrences != 1:
            errors.append(f'任务 {task} 必须只有一张验收卡，实际 {occurrences}')
    documents = list(walk_markdown(ROOT))
    link_count = 0
    for document in documents:
        # Ignore command examples and diagrams when finding real Markdown links.
        text = re.sub(r'^```.*?^```[^\n]*', '', document.read_text(encoding='utf-8'), flags=re.M | re.S)
        for match in LINK.finditer(text):
            target = match.group(1).strip('<>')
            parts = urlsplit(target)
            if parts.scheme or parts.netloc or target.startswith('#'):
                continue
            path = document.parent / unquote(parts.path)
            link_count += 1
            if not path.exists():
                errors.append(f'{document.relative_to(ROOT)}: 链接不存在 {target}')
            elif parts.fragment.startswith('task-') and f'id="{parts.fragment}"' not in path.read_text():
                errors.append(f'{document.relative_to(ROOT)}: 任务锚点不存在 {target}')
    print(json.dumps({'ok': not errors, 'architecture_entries': len(entries),
                      'tasks': len(tasks), 'markdown_files': len(documents),
                      'local_links': link_count, 'errors': errors}, ensure_ascii=False, indent=2))
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(check())
