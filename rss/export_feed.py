#!/usr/bin/env python3
"""Public-source RSS export. No Notion, credentials, or third-party packages."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime, parsedate_to_datetime
import hashlib
import html
from html.parser import HTMLParser
import ipaddress
import json
from pathlib import Path
import re
import tempfile
import os
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request
import xml.etree.ElementTree as ET

UTC = timezone.utc
MEDIA = 'http://search.yahoo.com/mrss/'
FEED_URL = 'https://gene8tor-ai.github.io/ai-uutiskirjeet/feeds/ai-news.xml'
MAX_BYTES = 8 * 1024 * 1024
ET.register_namespace('media', MEDIA)
ET.register_namespace('atom', 'http://www.w3.org/2005/Atom')


def safe_url(value, image=False):
    value = (value or '').strip()
    if not value or re.search(r'[\x00-\x20\x7f]', value):
        return ''
    try:
        p = urlsplit(value)
        if p.scheme not in (('https',) if image else ('http', 'https')) or not p.hostname or p.username or p.password:
            return ''
        _ = p.port
        if p.hostname.lower() == 'localhost' or p.hostname.lower().endswith(('.localhost', '.local')):
            return ''
        try:
            if not ipaddress.ip_address(p.hostname).is_global:
                return ''
        except ValueError:
            pass
        return value
    except ValueError:
        return ''


def xml_text(value):
    return ''.join(c for c in value if c in '\t\n\r' or 0x20 <= ord(c) <= 0xD7FF or 0xE000 <= ord(c) <= 0xFFFD or 0x10000 <= ord(c) <= 0x10FFFF)


class Snippet(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.images, self.hidden = [], [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'iframe'):
            self.hidden += 1
        if self.hidden:
            return
        if tag == 'img':
            u = safe_url(dict(attrs).get('src'), image=True)
            if u:
                self.images.append(u)
        if tag in ('p', 'br', 'div', 'li'):
            self.parts.append(' ')

    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'iframe') and self.hidden:
            self.hidden -= 1
        if tag in ('p', 'div', 'li'):
            self.parts.append(' ')

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def snippet(value):
    p = Snippet()
    p.feed(value or '')
    return xml_text(' '.join(''.join(p.parts).split()))[:4000], p.images


def date(value):
    try:
        d = parsedate_to_datetime(value)
    except (ValueError, TypeError, IndexError, OverflowError):
        try:
            d = datetime.fromisoformat(value.strip().replace('Z', '+00:00'))
        except (ValueError, TypeError, AttributeError):
            return None
    if d.tzinfo is None:
        return None  # Never guess a publisher timezone.
    return d.astimezone(UTC)


def local(tag):
    return tag.rsplit('}', 1)[-1]


def child_text(node, names):
    for name in names:
        for c in node:
            if local(c.tag) == name and c.text:
                return ''.join(c.itertext()).strip()
    return ''


@dataclass(frozen=True)
class Item:
    title: str
    url: str
    published: datetime
    source: str
    description: str = ''
    image: str = ''
    source_url: str = ''

    @property
    def guid(self):
        return 'urn:sha256:' + hashlib.sha256(self.url.encode('utf-8')).hexdigest()


def parse_feed(data, source, now, source_url=''):
    # ElementTree expands internal entities; forbid all DTD/entity declarations.
    # Reject alternate encodings with embedded NULs, which could disguise a DTD.
    if len(data) > MAX_BYTES or b'\x00' in data or re.search(br'<!\s*(DOCTYPE|ENTITY)\b', data, re.I):
        raise ValueError('unsafe or oversized XML')
    root = ET.fromstring(data)
    if local(root.tag) not in ('rss', 'feed', 'RDF'):
        raise ValueError('not RSS or Atom')
    items = []
    for node in root.iter():
        if local(node.tag) not in ('item', 'entry'):
            continue
        atom = local(node.tag) == 'entry'
        title = xml_text(child_text(node, ['title']))
        link = ''
        if atom:
            for c in node:
                if local(c.tag) == 'link' and c.get('rel', 'alternate') == 'alternate' and c.get('type', 'text/html') in ('text/html', 'application/xhtml+xml'):
                    link = safe_url(c.get('href'))
                    if link:
                        break
        else:
            link = safe_url(child_text(node, ['link']))
        published = date(child_text(node, ['published', 'pubDate', 'date', 'updated']))
        if not title or not link or not published or not now - timedelta(days=7) <= published <= now:
            continue
        raw = child_text(node, ['description', 'summary', 'encoded', 'content'])
        # Atom XHTML stores markup as real XML children, not escaped text.
        for name in ('description', 'summary', 'encoded', 'content'):
            content = next((c for c in node if local(c.tag) == name), None)
            if content is not None:
                if len(content):
                    raw = (content.text or '') + ''.join(ET.tostring(c, encoding='unicode') for c in content)
                    # HTMLParser must recognize XHTML tags serialized with prefixes.
                    raw = re.sub(r'(<\/?)(?:[A-Za-z_][\w.-]*):', r'\1', raw)
                break
        desc, images = snippet(raw)
        image = ''
        for c in node.iter():
            if c.tag in ('{' + MEDIA + '}thumbnail', '{' + MEDIA + '}content'):
                # media:content may be audio/video; do not invent an image.
                if local(c.tag) == 'thumbnail' or c.get('medium') == 'image' or c.get('type', '').startswith('image/') or (not c.get('type') and not c.get('medium') and re.search(r'\.(?:jpe?g|png|gif|webp|avif)(?:[?#]|$)', c.get('url', ''), re.I)):
                    image = safe_url(c.get('url'), image=True)
            elif local(c.tag) == 'enclosure' and c.get('type', '').startswith('image/'):
                image = safe_url(c.get('url'), image=True)
            if image:
                break
        if not image and images:
            image = images[0]
        attributed_source = child_text(node, ['source', 'category']) if source is None else source
        attributed_url = safe_url(source_url)
        if source is None:
            source_node = next((c for c in node if local(c.tag) == 'source'), None)
            attributed_url = safe_url(source_node.get('url')) if source_node is not None else ''
        items.append(Item(title, link, published, attributed_source or '', desc, image, attributed_url))
    return items


def select(items, now):
    seen, counts, out = set(), {}, []
    for item in sorted(items, key=lambda i: i.published, reverse=True):
        if item.url in seen or not now - timedelta(days=7) <= item.published <= now:
            continue
        if counts.get(item.source, 0) >= 10:
            continue
        seen.add(item.url)
        counts[item.source] = counts.get(item.source, 0) + 1
        out.append(item)
        if len(out) == 100:
            break
    return out


def render(items, now):
    root = ET.Element('rss', {'version': '2.0'})
    channel = ET.SubElement(root, 'channel')
    for key, value in [('title', 'Loitsu AI — alkuperäiset uutiset'), ('link', FEED_URL), ('description', 'Alkuperäisten julkisten RSS- ja Atom-lähteiden uutiset.'), ('language', 'fi'), ('lastBuildDate', format_datetime(now, usegmt=True))]:
        ET.SubElement(channel, key).text = value
    ET.SubElement(channel, '{http://www.w3.org/2005/Atom}link', {'href': FEED_URL, 'rel': 'self', 'type': 'application/rss+xml'})
    for item in items:
        e = ET.SubElement(channel, 'item')
        for key, value in [('title', item.title), ('link', item.url), ('pubDate', format_datetime(item.published, usegmt=True))]:
            ET.SubElement(e, key).text = value
        if safe_url(item.source_url):
            ET.SubElement(e, 'source', {'url': item.source_url}).text = item.source
        else:
            ET.SubElement(e, 'category').text = item.source
        ET.SubElement(e, 'guid', {'isPermaLink': 'false'}).text = item.guid
        desc = html.escape(item.description)
        if item.image:
            desc = '<img src="' + html.escape(item.image, quote=True) + '" alt="" /> ' + desc
            ET.SubElement(e, '{' + MEDIA + '}thumbnail', {'url': item.image})
        ET.SubElement(e, 'description').text = desc
    ET.indent(root)
    return ET.tostring(root, encoding='utf-8', xml_declaration=True) + b'\n'


class PublicRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not safe_url(newurl):
            raise ValueError('unsafe redirect')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(url):
    if not safe_url(url):
        raise ValueError('unsafe source URL')
    from urllib.request import build_opener
    request = Request(url, headers={'User-Agent': 'Loitsu-Original-RSS/1.0', 'Accept': 'application/rss+xml, application/atom+xml, application/xml, text/xml', 'Accept-Encoding': 'identity'})
    with build_opener(PublicRedirects()).open(request, timeout=20) as r:
        if not safe_url(r.geturl()):
            raise ValueError('unsafe redirect')
        data = r.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError('oversized source')
    return data


def atomic_write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.' + path.name, dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(data)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def export(sources, output, status_path, now=None, fetcher=fetch):
    now = now or datetime.now(UTC)
    names = [s['name'] for s in sources]
    if not sources or len(set(names)) != len(names) or any(not n or not safe_url(s['url']) for n, s in zip(names, sources)):
        raise ValueError('invalid source registry')
    previous = []
    if Path(output).exists():
        try:
            previous = [i for i in parse_feed(Path(output).read_bytes(), None, now) if i.source in names]
        except (ValueError, ET.ParseError):
            pass
    def get(s):
        try:
            parsed = parse_feed(fetcher(s['url']), s['name'], now, s['url'])
            return parsed, {'name': s['name'], 'status': 'ok', 'eligible': len(parsed)}
        except Exception:
            # Never expose exception messages/URLs, which may contain tokens.
            return [], {'name': s['name'], 'status': 'failed', 'eligible': 0}
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(get, sources))
    selected = select([i for items, _ in results for i in items] + previous, now)
    ok = any(s['status'] == 'ok' for _, s in results) and bool(selected)
    status = {'updated': now.isoformat(), 'status': 'ok' if ok else 'failed', 'items': len(selected), 'sources': [s for _, s in results]}
    if ok:
        atomic_write(output, render(selected, now))
    atomic_write(status_path, (json.dumps(status, ensure_ascii=False, indent=2) + '\n').encode())
    return 0 if ok else 1


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sources', default='rss/sources.json')
    p.add_argument('--output', default='feeds/ai-news.xml')
    p.add_argument('--status', default='feeds/status.json')
    args = p.parse_args()
    try:
        sources = json.loads(Path(args.sources).read_text())['sources']
        return export(sources, args.output, args.status)
    except Exception:
        # Configuration errors do not overwrite the last known-good XML.
        atomic_write(args.status, b'{"status":"failed","error":"configuration or output failure"}\n')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
