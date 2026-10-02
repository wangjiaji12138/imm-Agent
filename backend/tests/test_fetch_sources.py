import pytest

from app.cli.fetch_sources import extract_nci


def test_extraction_excludes_navigation_media_footer_and_keeps_paragraphs():
    body = 'A synthetic paragraph about a fictional concept. ' * 15
    html = f'''<h1>Test title</h1><article><nav><p>Navigation</p></nav>
    <div class="cgdp-article-body"><h2><p>Section title</p></h2><p>{body}</p>
    <figure><p>Copyrighted caption</p></figure><ul><li>List item</li></ul></div>
    <footer><ul><li><strong>Reviewed:</strong><time datetime="2024-08-05T12:00:00Z">date</time></li></ul>
    <p>Footer</p></footer></article>'''
    title, text, dates = extract_nci(html)
    assert title == 'Test title'
    assert dates == {'reviewed': '2024-08-05'}
    assert dates.get('posted') is None
    assert text.count('Section title') == 1
    assert 'List item' in text
    assert all(word not in text for word in ['Navigation', 'Copyrighted', 'Footer'])


def test_changed_page_structure_fails_closed():
    with pytest.raises(ValueError):
        extract_nci('<html><h1>Access denied</h1></html>')
