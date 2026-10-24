"""Best-effort public publisher preview metadata; no cookies or page storage."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from html.parser import HTMLParser
import json
import re
import time
from urllib.parse import urlencode, urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from export_feed import safe_url
from public_metadata_http import public_destination, PublicHTTPHandler, PublicHTTPSHandler

MAX_HTML = 1024 * 1024
REQUEST_TIMEOUT = 8
IMAGE_BUDGET = 90
USER_AGENT = 'Loitsu-Original-RSS/1.1 (+https://gene8tor-ai.github.io/ai-uutiskirjeet/)'
GOOGLE_RPC = 'https://news.google.com/_/DotsSplashUi/data/batchexecute?rpcids=Fbv4je'


class PublicRedirects(HTTPRedirectHandler):
    max_redirections = 5
    max_repeats = 2

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # The connection handler resolves, checks and pins every actual hop.
        if not safe_url(newurl):
            raise ValueError('unsafe redirect')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch_metadata(url, deadline, data=None):
    if not safe_url(url):
        raise ValueError('unsafe URL')
    remaining = min(REQUEST_TIMEOUT, deadline - time.monotonic())
    if remaining <= 0:
        raise TimeoutError('metadata budget expired')
    request = Request(url, data=data, headers={
        'User-Agent': USER_AGENT, 'Accept': 'text/html, application/xhtml+xml, application/json',
        'Accept-Encoding': 'identity',
        **({'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'} if data is not None else {}),
    })
    request_deadline = min(deadline, time.monotonic() + REQUEST_TIMEOUT)
    opener = build_opener(ProxyHandler({}), PublicRedirects(),
                          PublicHTTPHandler(request_deadline), PublicHTTPSHandler(request_deadline))
    with opener.open(request, timeout=remaining) as response:
        content_type = response.headers.get_content_type()
        if content_type not in ('text/html', 'application/xhtml+xml', 'application/json', 'text/plain'):
            raise ValueError('not preview metadata')
        chunks, size = [], 0
        # The preview is in the HTML head; truncate large pages, never store bodies.
        while size < MAX_HTML:
            if time.monotonic() >= request_deadline:
                raise TimeoutError('metadata request expired')
            chunk = response.read1(min(65536, MAX_HTML - size))
            if not chunk:
                break
            chunks.append(chunk)
            size += len(chunk)
        encoding = response.headers.get_content_charset() or 'utf-8'
        return b''.join(chunks).decode(encoding, errors='replace'), response.geturl()


class PreviewMetadata(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.images, self.signature, self.timestamp = {}, '', ''

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'meta':
            key = (a.get('property') or a.get('name') or '').lower()
            if key in ('og:image:secure_url', 'og:image', 'og:image:url', 'twitter:image', 'twitter:image:src'):
                self.images.setdefault(key, a.get('content', ''))
        if a.get('data-n-a-sg') and a.get('data-n-a-ts'):
            self.signature, self.timestamp = a['data-n-a-sg'], a['data-n-a-ts']

    def image(self, page_url):
        for key in ('og:image:secure_url', 'og:image', 'og:image:url', 'twitter:image', 'twitter:image:src'):
            candidate = urljoin(page_url, self.images.get(key, '').strip()) if self.images.get(key, '').strip() else ''
            if safe_url(candidate, image=True):
                return candidate
        return ''


def google_request(article_id, metadata):
    # Public URL-resolution RPC used by the article page, not a paid API.
    context = [['en-US', 'US', ['FINANCE_TOP_INDICES', 'WEB_TEST_1_0_0'], None, None, 1, 1,
                'US:en', None, 180, None, None, None, None, None, 0, None, None,
                [1608992183, 723341000]], 'en-US', 'US', 1, [2, 3, 4, 8], 1, 0,
               '655000234', 0, 0, None, 0]
    inner = ['garturlreq', context, article_id, int(metadata.timestamp), metadata.signature]
    envelope = [[['Fbv4je', json.dumps(inner), None, 'generic']]]
    return urlencode({'f.req': json.dumps(envelope)}).encode()


def resolved_google_url(text):
    # batchexecute may include an anti-XSSI prefix and length-framed JSON lines.
    decoder = json.JSONDecoder()
    for line in text.splitlines():
        if not line.startswith('['):
            continue
        rows, _ = decoder.raw_decode(line)
        for row in rows:
            if isinstance(row, list) and len(row) >= 3 and row[:2] == ['wrb.fr', 'Fbv4je']:
                payload = json.loads(row[2])
                if isinstance(payload, list) and len(payload) >= 2 and payload[0] == 'garturlres':
                    return safe_url(payload[1])
    return ''


def google_host(url):
    host = (urlsplit(url).hostname or '').lower()
    return host == 'google.com' or host.endswith('.google.com')


def article_image(url, deadline, fetcher=fetch_metadata):
    body, final_url = fetcher(url, deadline)
    metadata = PreviewMetadata()
    metadata.feed(body)
    if google_host(final_url):
        # A Google wrapper's og:image is a generic logo, not this news story.
        path = urlsplit(url).path
        if urlsplit(url).hostname != 'news.google.com' or not re.fullmatch(r'/(?:rss/)?(?:articles|read)/[A-Za-z0-9_-]+', path):
            return ''
        if not metadata.signature or not metadata.timestamp.isdigit():
            return ''
        response, _ = fetcher(GOOGLE_RPC, deadline, data=google_request(path.rsplit('/', 1)[1], metadata))
        publisher = resolved_google_url(response)
        if not publisher or google_host(publisher):
            return ''
        body, final_url = fetcher(publisher, deadline)
        if google_host(final_url):
            return ''
        metadata = PreviewMetadata()
        metadata.feed(body)
    image = metadata.image(final_url)
    return public_destination(image, image=True, deadline=min(deadline, time.monotonic() + REQUEST_TIMEOUT)) if image else ''


def enrich_images(items, previous=(), lookup=article_image, budget=IMAGE_BUDGET, clock=time.monotonic):
    """Preserve every item's identity/order on failures and budget exhaustion."""
    cached = {i.url: i.image for i in previous if safe_url(i.image, image=True)}
    deadline = clock() + budget

    def enrich(item):
        if item.image:
            return item, 'source'
        if item.url in cached:
            return replace(item, image=cached[item.url]), 'reused'
        if clock() >= deadline:
            return item, 'budget'
        try:
            image = lookup(item.url, deadline)
            if safe_url(image, image=True):
                return replace(item, image=image), 'article'
        except Exception:
            pass  # Metadata failures must never remove news or expose response bodies.
        return item, 'unavailable'

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(enrich, items))
    counts = {key: sum(state == key for _, state in results) for key in ('source', 'reused', 'article', 'unavailable', 'budget')}
    counts['withImage'] = sum(bool(i.image) for i, _ in results)
    return [i for i, _ in results], counts
