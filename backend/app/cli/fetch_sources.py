"""Download only the reviewed NCI seed allowlist; never arbitrary input URLs."""

import argparse
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.robotparser import RobotFileParser

import httpx
from bs4 import BeautifulSoup

from app.knowledge import clean_text, document_id

ORIGIN = 'https://www.cancer.gov'
BASE = ORIGIN + '/about-cancer/treatment/types/immunotherapy'
SOURCES = {
    'nci-immunotherapy': BASE,
    'nci-checkpoint-inhibitors': BASE + '/checkpoint-inhibitors',
    'nci-t-cell-transfer': BASE + '/t-cell-transfer-therapy',
    'nci-monoclonal-antibodies': BASE + '/monoclonal-antibodies',
    'nci-treatment-vaccines': BASE + '/cancer-treatment-vaccines',
}
USER_AGENT = 'ImmAgentResearch/0.1 (educational source collection)'


def extract_nci(html: str) -> tuple[str, str, dict]:
    soup = BeautifulSoup(html, 'html.parser')
    article = soup.find('article')
    title = soup.find('h1')
    if article is None or title is None or not article.select('.cgdp-article-body'):
        raise ValueError('NCI 页面结构改变或正文缺失；停止导入，需人工检查')
    dates = {}
    for element in article.select('footer time[datetime]'):
        context = element.parent.get_text(' ', strip=True)
        for label in ('Posted', 'Updated', 'Reviewed'):
            if label in context:
                dates[label.lower()] = element['datetime'][:10]
    # Images/captions may have separate copyright. Retain only educational text.
    for element in article.select('footer, nav, aside, figure, script, style, .cgdp-related-resources, .cgdp-video, .cgdp-image, .cgdp-embed-feature-card'):
        element.decompose()
    paragraphs = []
    for element in article.find_all(['h2', 'h3', 'p', 'li']):
        if element.find_parent(['p', 'li', 'h2', 'h3']):
            continue
        value = clean_text(element.get_text(' ', strip=True))
        if value:
            prefix = '## ' if element.name == 'h2' else '### ' if element.name == 'h3' else ''
            paragraphs.append(prefix + value)
    text = clean_text('\n\n'.join(paragraphs))
    if len(text) < 500:
        raise ValueError('提取正文过短；需人工检查')
    return title.get_text(' ', strip=True), text, dates


def fetch(output: Path) -> Path:
    output.mkdir(parents=True, exist_ok=True)
    records = []
    with httpx.Client(timeout=45, headers={'User-Agent': USER_AGENT}, follow_redirects=False) as client:
        robots_response = client.get(ORIGIN + '/robots.txt')
        robots_response.raise_for_status()
        robots = RobotFileParser()
        robots.parse(robots_response.text.splitlines())
        (output / 'robots.txt').write_text(robots_response.text, encoding='utf-8')
        policy = client.get(ORIGIN + '/policies/copyright-reuse')
        policy.raise_for_status()
        (output / 'reuse-policy.html').write_text(policy.text, encoding='utf-8')
        for slug, url in SOURCES.items():
            if not robots.can_fetch(USER_AGENT, url):
                raise ValueError(f'robots.txt 不允许抓取 {url}')
            time.sleep(max(1, robots.crawl_delay(USER_AGENT) or 0))
            response = client.get(url)
            response.raise_for_status()
            title, text, dates = extract_nci(response.text)
            fetched = datetime.now(timezone.utc).isoformat()
            # Immutable hash-named snapshots preserve older versions for review.
            snapshot = output / f"{slug}-{hashlib.sha256(response.content).hexdigest()[:16]}"
            snapshot.with_suffix('.html').write_bytes(response.content)
            snapshot.with_suffix('.txt').write_text(text + '\n', encoding='utf-8')
            metadata = {'document_id': document_id(url), 'source_url': url, 'title': title,
                        'fetched_at': fetched, 'page_dates': dates,
                        'attribution': f'{title} was originally published by the National Cancer Institute.',
                        'reuse_policy': ORIGIN + '/policies/copyright-reuse',
                        'html_sha256': hashlib.sha256(response.content).hexdigest(),
                        'text_sha256': hashlib.sha256(text.encode()).hexdigest(),
                        'extraction': 'NCI article paragraphs and headings; no images, captions, footer or navigation'}
            snapshot.with_suffix('.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
            records.append({'title': title, 'organization': 'National Cancer Institute (NCI), NIH',
                            'source_url': url, 'language': 'en', 'published_at': dates.get('posted'),
                            'fetched_at': fetched, 'text_path': str(snapshot.with_suffix('.txt'))})
            print(json.dumps({'status': 'fetched', 'document_id': document_id(url), 'title': title}))
    manifest = output / 'manifest.jsonl'
    temporary = output / 'manifest.jsonl.tmp'
    temporary.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in records), encoding='utf-8')
    temporary.replace(manifest)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('data/raw/nci'))
    args = parser.parse_args()
    try:
        print(fetch(args.output))
        return 0
    except (httpx.HTTPError, OSError, ValueError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
