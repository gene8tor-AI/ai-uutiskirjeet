"""SPEC-3.6.1: publisher previews without changing original news identity."""
from dataclasses import replace
from datetime import datetime, timezone
from io import BytesIO
import json
from pathlib import Path
import socket
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs
from urllib.request import Request
import xml.etree.ElementTree as ET

from export_feed import Item, MEDIA, export, parse_feed, render
from preview_images import (MAX_HTML, GOOGLE_RPC, PreviewMetadata, PublicRedirects,
                            article_image, enrich_images, fetch_metadata,
                            public_destination, resolved_google_url)

NOW = datetime(2026, 10, 24, 4, tzinfo=timezone.utc)
URL = 'https://publisher.example/news/story'
IMAGE = 'https://cdn.example/preview.jpg'
ITEM = Item('Original headline', URL, NOW, 'Original source', 'Original snippet')


class PreviewTests(unittest.TestCase):
    def test_metadata_precedence_relative_and_html_entities(self):
        p = PreviewMetadata()
        p.feed('<meta name="twitter:image" content="https://cdn.example/twitter.jpg">'
               '<meta content="/preview.jpg?a=1&amp;b=2" property="og:image">')
        self.assertEqual(p.image(URL), 'https://publisher.example/preview.jpg?a=1&b=2')
        p.feed('<meta property="og:image:secure_url" content="//cdn.example/secure.jpg">')
        self.assertEqual(p.image(URL), 'https://cdn.example/secure.jpg')

    def test_twitter_and_unsafe_or_absent_metadata(self):
        for value in ['javascript:x', 'data:image/png,abc', 'http://cdn.example/image.jpg', 'https://127.0.0.1/x']:
            p = PreviewMetadata()
            p.feed(f'<meta property="og:image" content="{value}"><meta name="twitter:image:src" content="{IMAGE}">')
            self.assertEqual(p.image(URL), IMAGE)
        p = PreviewMetadata()
        p.feed('<html><img src="https://cdn.example/unrelated-ad.jpg"></html>')
        self.assertEqual(p.image(URL), '')

    @patch('preview_images.public_destination', side_effect=lambda u, **kw: u)
    def test_direct_article_uses_final_page_base(self, _):
        def fetcher(url, deadline):
            return '<meta property="og:image" content="preview.jpg">', 'https://publisher.example/moved/story'
        self.assertEqual(article_image(URL, 100, fetcher), 'https://publisher.example/moved/preview.jpg')

    @patch('preview_images.public_destination', side_effect=lambda u, **kw: u)
    def test_google_resolves_publisher_and_does_not_replace_article_link(self, _):
        wrapper = 'https://news.google.com/rss/articles/ABC?oc=5'
        calls = []
        def fetcher(url, deadline, data=None):
            calls.append((url, data))
            if url == wrapper:
                return '<meta property="og:image" content="https://cdn.example/google-logo.png"><div data-n-a-sg="sig" data-n-a-ts="123"></div>', wrapper
            if url == GOOGLE_RPC:
                envelope = json.loads(parse_qs(data.decode())['f.req'][0])
                inner = json.loads(envelope[0][0][1])
                self.assertEqual(inner[2:], ['ABC', 123, 'sig'])
                return ")]}'\n\n" + json.dumps([['wrb.fr', 'Fbv4je', json.dumps(['garturlres', URL, 1])]]), GOOGLE_RPC
            self.assertEqual(url, URL)
            return f'<meta property="og:image" content="{IMAGE}">', URL
        image = article_image(wrapper, 100, fetcher)
        original = replace(ITEM, url=wrapper)
        enriched, counts = enrich_images([original], lookup=lambda *a: image)
        self.assertEqual(enriched, [replace(original, image=IMAGE)])
        self.assertEqual(enriched[0].guid, original.guid)
        self.assertEqual(counts['article'], 1)
        self.assertEqual(len(calls), 3)
        data = render(enriched, NOW)
        root = ET.fromstring(data)
        self.assertEqual(root.find('./channel/item/{' + MEDIA + '}thumbnail').get('url'), IMAGE)
        self.assertIn(IMAGE, root.findtext('./channel/item/description'))
        self.assertEqual(parse_feed(data, None, NOW), enriched)

    def test_google_without_signature_or_bad_resolution_does_not_use_logo(self):
        wrapper = 'https://news.google.com/rss/articles/ABC'
        for body in ['', '<meta property="og:image" content="https://cdn.example/google-logo.png">']:
            self.assertEqual(article_image(wrapper, 100, lambda *a: (body, wrapper)), '')
        self.assertEqual(resolved_google_url(")]}'\n\n12\n[]"), '')
        self.assertEqual(resolved_google_url(json.dumps([['wrb.fr', 'Fbv4je', json.dumps(['garturlres', 'https://127.0.0.1/private'])]])), '')

    def test_lookup_failures_keep_original_order_and_every_item(self):
        items = [replace(ITEM, url=URL + str(i)) for i in range(4)]
        def lookup(url, deadline):
            if url.endswith('0'):
                raise HTTPError(url, 403, 'blocked', {}, None)
            if url.endswith('1'):
                raise TimeoutError('slow')
            if url.endswith('2'):
                raise ValueError('malformed response with private detail')
            return 'javascript:bad'
        enriched, counts = enrich_images(items, lookup=lookup)
        self.assertEqual(enriched, items)
        self.assertEqual(counts['unavailable'], 4)

    def test_existing_and_previous_images_avoid_article_requests(self):
        with_image = replace(ITEM, image=IMAGE)
        def never(*args):
            self.fail('must not request article')
        enriched, counts = enrich_images([with_image], [replace(ITEM, image=IMAGE + 'old')], lookup=never)
        self.assertEqual(enriched, [with_image])
        self.assertEqual(counts['source'], 1)
        enriched, counts = enrich_images([ITEM], [with_image], lookup=never)
        self.assertEqual(enriched, [with_image])
        self.assertEqual(counts['reused'], 1)

    def test_expired_budget_starts_no_lookups(self):
        enriched, counts = enrich_images([ITEM], lookup=lambda *a: self.fail('budget exceeded'), budget=0)
        self.assertEqual(enriched, [ITEM])
        self.assertEqual(counts['budget'], 1)

    def test_queued_work_obeys_budget_and_four_worker_limit(self):
        lock = threading.Lock()
        active = peak = requests = 0
        def lookup(url, deadline):
            nonlocal active, peak, requests
            with lock:
                active += 1
                peak = max(peak, active)
                requests += 1
            time.sleep(.025)
            with lock:
                active -= 1
            return IMAGE
        items = [replace(ITEM, url=URL + str(i)) for i in range(20)]
        enriched, counts = enrich_images(items, lookup=lookup, budget=.01)
        self.assertEqual(len(enriched), 20)
        self.assertLessEqual(peak, 4)
        self.assertLessEqual(requests, 4)
        self.assertGreater(counts['budget'], 0)

    @patch('public_metadata_http.socket.getaddrinfo')
    def test_dns_private_alias_mixed_dns_and_unsafe_redirect_rejected(self, dns):
        for address in ['127.0.0.1', '10.0.0.1', '169.254.169.254', '::1']:
            dns.return_value = [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (address, 443))]
            with self.assertRaises(ValueError):
                public_destination('https://attacker.example/path')
        dns.return_value = [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('93.184.216.34', 443)),
                            (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('10.0.0.1', 443))]
        with self.assertRaises(ValueError):
            public_destination('https://mixed.example/path')
        with self.assertRaises(ValueError):
            PublicRedirects().redirect_request(Request(URL), None, 302, '', {}, 'http://169.254.169.254/latest')

    @patch('preview_images.public_destination', side_effect=lambda u, **kw: u)
    @patch('preview_images.build_opener')
    def test_transport_caps_html_and_has_no_cookie_header(self, opener, _):
        class Headers:
            def get_content_type(self): return 'text/html'
            def get_content_charset(self): return 'utf-8'
        class Response(BytesIO):
            headers = Headers()
            def geturl(self): return URL
        opener.return_value.open.return_value = Response(b'x' * (MAX_HTML + 100))
        body, final = fetch_metadata(URL, time.monotonic() + 90)
        self.assertEqual(len(body), MAX_HTML)
        request = opener.return_value.open.call_args.args[0]
        self.assertIsNone(request.get_header('Cookie'))
        self.assertLessEqual(opener.return_value.open.call_args.kwargs['timeout'], 8)

    def test_export_enricher_failure_does_not_break_news(self):
        with tempfile.TemporaryDirectory() as d:
            output, status = Path(d)/'feed.xml', Path(d)/'status.json'
            data = render([ITEM], NOW)
            def failure(*args): raise RuntimeError('private detail')
            self.assertEqual(export([{'name': ITEM.source, 'url': 'https://publisher.example/rss'}], output, status,
                                    NOW, lambda _: data, image_enricher=failure), 0)
            self.assertEqual(parse_feed(output.read_bytes(), None, NOW)[0].url, URL)
            self.assertEqual(json.loads(status.read_text())['images'], {'status': 'failed'})
            self.assertNotIn('private detail', status.read_text())


if __name__ == '__main__':
    unittest.main()
