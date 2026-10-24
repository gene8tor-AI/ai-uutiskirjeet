"""Render a researched issue; network, research and release are explicit separate steps."""
import argparse
from datetime import date
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urlsplit, urlunsplit

SERIES = 'AI:sta arvoa'
TAGLINE = 'Työn muutoksesta skaalautuvaan hyötyyn'


def canonical(url):
    p = urlsplit(url)
    if p.scheme != 'https' or not p.hostname or p.username or p.password:
        raise ValueError('Source must be an absolute public HTTPS URL')
    return urlunsplit((p.scheme, p.netloc.lower(), p.path.rstrip('/'), '', ''))


class Article(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.links = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in ('style', 'script'):
            self.hidden += 1
        if tag == 'a':
            href = dict(attrs).get('href', '')
            if href.startswith('https://'):
                self.links.append(canonical(href))

    def handle_endtag(self, tag):
        if tag in ('style', 'script'):
            self.hidden = max(0, self.hidden - 1)

    def handle_data(self, value):
        if not self.hidden:
            self.text.append(value)


def archive(root):
    result = []
    for path in sorted(root.glob('*.html')):
        if path.name == 'index.html' or not re.search(r'\d{4}-\d{2}-\d{2}', path.name):
            continue
        parser = Article()
        parser.feed(path.read_text(encoding='utf-8'))
        result.append({'file': path.name, 'text': ' '.join(' '.join(parser.text).split()),
                       'sources': sorted(set(parser.links))})
    return result


def validate(data, root):
    date.fromisoformat(data['date'])
    for key in ('title', 'topic_id', 'novelty', 'search_queries', 'facts', 'sources', 'sections'):
        if not data.get(key):
            raise ValueError('Missing ' + key)
    if not re.fullmatch(r'[a-z0-9-]+', data['topic_id']):
        raise ValueError('Invalid topic id')
    if not data['novelty'].get('rationale') or data['novelty'].get('archive_reviewed') is not True:
        raise ValueError('Archive comparison and editorial novelty rationale required')
    source_ids = [s['id'] for s in data['sources']]
    if len(set(source_ids)) != len(source_ids):
        raise ValueError('Duplicate source id')
    evidence = set()
    source_urls = set()
    for source in data['sources']:
        source_urls.add(canonical(source['url']))
        if source.get('verified_on') != data['date']:
            raise ValueError('Open each original source on issue date')
        if source.get('role') not in ('new_evidence', 'background'):
            raise ValueError('Source role required')
        if source['role'] == 'new_evidence':
            published = date.fromisoformat(source['published'])
            age = (date.fromisoformat(data['date']) - published).days
            if not 0 <= age <= 30:
                raise ValueError('New evidence must be from preceding 30 days')
            evidence.add(canonical(source['url']))
    if not evidence:
        raise ValueError('No fresh evidence; do not republish old research')
    if len(data['facts']) != len(set(data['facts'])):
        raise ValueError('Duplicate fact id')
    for section in data['sections']:
        if not section.get('heading') or not section.get('paragraphs'):
            raise ValueError('Empty section')
        if not set(section.get('sources', [])).issubset(source_ids):
            raise ValueError('Unknown citation')
        if not section.get('sources') and section.get('kind') != 'analysis':
            raise ValueError('Evidence sections require citations; mark own analysis explicitly')
    history = []
    for path in sorted((root / 'editorial/issues').glob('*.json')):
        history.append(json.loads(path.read_text(encoding='utf-8')))
    repeated = [x for x in history if x['topic_id'] == data['topic_id'] or set(x['facts']) & set(data['facts'])]
    previously_new = {canonical(s['url']) for x in history for s in x['sources'] if s['role'] == 'new_evidence'}
    prior_files = {f"ai_arvoa_{x['date']}.html" for x in repeated}
    if repeated and (not data['novelty'].get('material_update') or not evidence - previously_new
                     or not prior_files.issubset(set(data['novelty'].get('previous', [])))):
        raise ValueError('Repeated topic/fact requires material update, all prior references and fresh evidence')
    archived = archive(root)
    used_sources = {url for x in archived for url in x['sources']} | previously_new
    if not evidence - used_sources:
        raise ValueError('Fresh evidence already covered: changing topic/fact IDs does not make it new')
    overlaps = [x['file'] for x in archived if source_urls.intersection(x['sources'])]
    if not set(overlaps).issubset(set(data['novelty'].get('related_archive', []))):
        raise ValueError('Source overlap with archive must be explicitly assessed: ' + ', '.join(overlaps))
    return overlaps


def render(data):
    e = escape
    sources = {s['id']: s for s in data['sources']}
    blocks = []
    for section in data['sections']:
        paragraphs = ''.join('<p>' + e(p) + '</p>' for p in section['paragraphs'])
        refs = ' '.join(f'<a href="#source-{e(i)}">[{e(i)}]</a>' for i in section.get('sources', []))
        blocks.append(f'<section><h2>{e(section["heading"])}</h2>{paragraphs}<p class="refs">{refs}</p></section>')
    refs = ''.join(f'<li id="source-{e(i)}"><a href="{e(s["url"], quote=True)}">{e(s["title"])}</a> — {e(s["published"])}. '
                   f'{"Uusi näyttö" if s["role"] == "new_evidence" else "Taustalähde"}. Tarkistettu {e(s["verified_on"])}.</li>'
                   for i, s in sources.items())
    previous = data['novelty'].get('previous', [])
    if any(not re.fullmatch(r'[a-z0-9_\-]+\.html', name) for name in previous):
        raise ValueError('Invalid prior coverage filename')
    prior = '<p>Aiempi käsittely: ' + ' · '.join(f'<a href="{e(name)}">{e(name)}</a>' for name in previous) + '</p>' if previous else ''
    return f'''<!doctype html>
<html lang="fi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(SERIES)} — {e(data['title'])}</title>
<style>body{{margin:0;background:#f2f4f8;color:#182235;font:18px/1.75 system-ui,sans-serif}}main{{max-width:800px;margin:36px auto;padding:32px;background:white;border-top:6px solid #5733a3;border-radius:12px}}h1{{font-size:2.1em;line-height:1.2}}h2{{line-height:1.3;margin-top:2em}}a{{color:#493087}}.series{{color:#5733a3;font-weight:700}}.meta,.refs{{font-size:.85em;color:#586174}}aside{{padding:18px;background:#f1edf9;border-left:4px solid #5733a3}}li{{margin:12px 0}}@media(max-width:600px){{main{{margin:0;padding:22px;border-radius:0}}h1{{font-size:1.65em}}}}</style></head>
<body><main><header><p class="series">{SERIES}</p><p>{TAGLINE}</p><p class="meta"><time datetime="{e(data['date'])}">{e(data['date'])}</time> · Lähteistetty katsaus</p><h1>{e(data['title'])}</h1></header>
<aside><strong>Mikä on uutta?</strong><p>{e(data['novelty']['rationale'])}</p>{prior}</aside>
{''.join(blocks)}<section><h2>Lähteet ja rajaus</h2><ol>{refs}</ol><p class="meta">Toimituksellinen synteesi julkisista lähteistä. Esimerkit ja suositukset eivät kuvaa minkään yksittäisen työnantajan sisäisiä toteutuksia. Tutkimuksen havainto, asiantuntijan suositus ja oma esimerkki erotetaan tekstissä.</p></section>
<footer><a href="index.html">Kaikki katsaukset</a></footer></main></body></html>'''


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument('--inventory', action='store_true')
    p.add_argument('--input', type=Path)
    a = p.parse_args()
    if a.inventory:
        print(json.dumps(archive(a.root), ensure_ascii=False, indent=2))
        return
    if a.input is None:
        p.error('--input or --inventory required')
    data = json.loads(a.input.read_text(encoding='utf-8'))
    validate(data, a.root)
    output = a.root / f"ai_arvoa_{data['date']}.html"
    issue = a.root / 'editorial/issues' / f"{data['date']}.json"
    if output.exists() or issue.exists():
        raise ValueError('Issue already exists; no overwrite or duplicate publication')
    html = render(data)
    issue.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding='utf-8')
    issue.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'file': output.name, 'topic': data['topic_id'], 'status': 'rendered_not_published'}))


if __name__ == '__main__':
    main()
