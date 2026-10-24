"""Acceptance tests: run python3 -m unittest discover -s rss -v."""
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
from export_feed import Item, MEDIA, export, parse_feed, render, safe_url, select

NOW = datetime(2026, 10, 24, 3, tzinfo=timezone.utc)
DATE = 'Fri, 23 Oct 2026 10:00:00 GMT'


def rss(body):
    return ('<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/"><channel>' + body + '</channel></rss>').encode()


def entry(url='https://example.com/original?a=1&amp;b=2', title='Original &amp; unchanged', published=DATE, extra=''):
    return '<item><title>' + title + '</title><link>' + url + '</link><pubDate>' + published + '</pubDate>' + extra + '</item>'


class ExportTests(unittest.TestCase):
    def test_original_content_and_roundtrip(self):
        item = parse_feed(rss(entry(extra='<description><![CDATA[<b>Publisher snippet</b><script>evil()</script><img src="https://images.example.com/1.jpg">]]></description>')), 'Publisher', NOW)[0]
        self.assertEqual(item.title, 'Original & unchanged')
        self.assertEqual(item.url, 'https://example.com/original?a=1&b=2')
        self.assertEqual(item.published, datetime(2026, 10, 23, 10, tzinfo=timezone.utc))
        self.assertEqual(item.description, 'Publisher snippet')
        root = ET.fromstring(render([item], NOW))
        self.assertEqual(root.findtext('channel/item/title'), item.title)
        self.assertEqual(root.find('channel/item/{' + MEDIA + '}thumbnail').get('url'), item.image)
        self.assertIn('<img src="https://images.example.com/1.jpg"', root.findtext('channel/item/description'))
        self.assertEqual(parse_feed(render([item], NOW), None, NOW)[0], item)

    def test_source_feed_url_attribution_roundtrip(self):
        item = parse_feed(rss(entry()), 'Publisher', NOW, 'https://example.com/rss')[0]
        data = render([item], NOW)
        source = ET.fromstring(data).find('channel/item/source')
        self.assertEqual(source.text, 'Publisher')
        self.assertEqual(source.get('url'), 'https://example.com/rss')
        self.assertEqual(parse_feed(data, None, NOW)[0], item)
        legacy = rss(entry(extra='<source>Legacy publisher</source>'))
        self.assertEqual(parse_feed(legacy, None, NOW)[0].source, 'Legacy publisher')

    def test_atom_alternate_not_self_and_google_unchanged(self):
        data = b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Untranslated title</title><link rel="self" href="https://example.com/atom/1"/><link rel="alternate" href="https://news.google.com/rss/articles/ABC?oc=5"/><published>2026-10-23T10:00:00Z</published><updated>2026-10-24T01:00:00Z</updated><summary type="html">A &lt;b&gt;snippet&lt;/b&gt;</summary></entry></feed>'
        item = parse_feed(data, 'Google', NOW)[0]
        self.assertEqual(item.url, 'https://news.google.com/rss/articles/ABC?oc=5')
        self.assertEqual(item.published.hour, 10)
        self.assertEqual(item.description, 'A snippet')

    def test_atom_xhtml_content_thumbnail(self):
        data = b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>XHTML title</title><link href="https://example.com/a"/><published>2026-10-23T10:00:00Z</published><content type="xhtml"><div xmlns="http://www.w3.org/1999/xhtml"><p>Original <b>snippet</b></p><img src="https://example.com/pic.png"/></div></content></entry></feed>'
        item = parse_feed(data, 'Atom', NOW)[0]
        self.assertEqual(item.description, 'Original snippet')
        self.assertEqual(item.image, 'https://example.com/pic.png')

    def test_image_variants_and_no_invention(self):
        for extra in ['<enclosure type="image/jpeg" url="https://example.com/a.jpg"/>', '<media:thumbnail url="https://example.com/a.jpg"/>', '<media:content type="image/jpeg" url="https://example.com/a.jpg"/>', '<media:content url="https://example.com/a.jpg"/>']:
            self.assertEqual(parse_feed(rss(entry(extra=extra)), 'P', NOW)[0].image, 'https://example.com/a.jpg')
        for extra in ['', '<enclosure type="audio/mpeg" url="https://example.com/a.mp3"/>', '<media:thumbnail url="http://example.com/a.jpg"/>', '<description><![CDATA[<img src="javascript:alert(1)"><script>bad</script>text & raw]]></description>']:
            self.assertEqual(parse_feed(rss(entry(extra=extra)), 'P', NOW)[0].image, '')

    def test_unsafe_urls_dates_and_xml(self):
        for url in ['javascript:alert(1)', 'data:text/html,x', 'https://u:secret@example.com/x', 'https://127.0.0.1/x', 'https://example.com:bad/x', 'https://example.com/\nx', '//example.com/a']:
            self.assertEqual(safe_url(url), '')
            self.assertEqual(parse_feed(rss(entry(url=url)), 'P', NOW), [])
        for d in ['not a date', '2026-10-25T10:00:00Z', '2026-10-16T10:00:00Z', '2026-10-23T10:00:00']:
            self.assertEqual(parse_feed(rss(entry(published=d)), 'P', NOW), [])
        for data in [b'<!DOCTYPE rss [<!ENTITY x "boom">]><rss/>', b'<rss><broken>', b'<html/>']:
            with self.assertRaises((ValueError, ET.ParseError)):
                parse_feed(data, 'P', NOW)

    def test_xml_and_description_injection(self):
        item = parse_feed(rss(entry(title='&lt;script&gt;not markup&lt;/script&gt;', extra='<description><![CDATA[<a href="javascript:x">A & B</a><img src="https://example.com/a.jpg?x=&quot; onerror=&quot;x">]]></description>')), 'P', NOW)[0]
        data = render([item], NOW)
        root = ET.fromstring(data)
        self.assertIsNone(root.find('.//script'))
        self.assertIsNone(root.find('.//img'))
        self.assertNotIn('onerror', root.findtext('channel/item/description'))
        self.assertEqual(root.findtext('channel/item/title'), '<script>not markup</script>')

    def test_dedup_stable_guid_and_caps(self):
        old = Item('Old', 'https://example.com/one', NOW - timedelta(hours=2), 'P')
        new = Item('New', old.url, NOW - timedelta(hours=1), 'P')
        self.assertEqual(old.guid, new.guid)
        self.assertEqual(select([old, new], NOW), [new])
        items = [Item(str(i), 'https://example.com/' + str(i), NOW - timedelta(minutes=i), 'source' + str(i // 20)) for i in range(240)]
        chosen = select(items, NOW)
        self.assertEqual(len(chosen), 100)
        self.assertTrue(all(sum(i.source == s for i in chosen) <= 10 for s in {i.source for i in chosen}))
        self.assertEqual(select([Item('expired', old.url, NOW - timedelta(days=8), 'P')], NOW), [])

    def test_partial_failure_retains_previous_and_total_outage_preserves_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            out, status = Path(d)/'feed.xml', Path(d)/'status.json'
            sources = [{'name': 'A', 'url': 'https://a.example/rss'}, {'name': 'B', 'url': 'https://b.example/rss'}]
            previous = Item('Previous', 'https://b.example/old', NOW - timedelta(days=1), 'B')
            out.write_bytes(render([previous], NOW))
            def partial(url):
                if 'b.example' in url:
                    raise OSError('secret must never appear')
                return rss(entry())
            self.assertEqual(export(sources, out, status, NOW, partial), 0)
            self.assertEqual(len(parse_feed(out.read_bytes(), None, NOW)), 2)
            self.assertNotIn('secret', status.read_text())
            self.assertEqual(json.loads(status.read_text())['sources'][1]['status'], 'failed')
            before = out.read_bytes()
            def failure(url):
                raise OSError('outage')
            self.assertEqual(export(sources, out, status, NOW, failure), 1)
            self.assertEqual(out.read_bytes(), before)
            self.assertEqual(json.loads(status.read_text())['status'], 'failed')

    def test_zero_eligible_does_not_replace_previous_and_expiry(self):
        with tempfile.TemporaryDirectory() as d:
            out, status = Path(d)/'feed.xml', Path(d)/'status.json'
            out.write_bytes(render([Item('Old', 'https://example.com/a', NOW - timedelta(days=8), 'A')], NOW))
            before = out.read_bytes()
            sources = [{'name': 'A', 'url': 'https://example.com/rss'}]
            self.assertEqual(export(sources, out, status, NOW, lambda _: rss('')), 1)
            self.assertEqual(out.read_bytes(), before)
            self.assertEqual(json.loads(status.read_text())['items'], 0)


if __name__ == '__main__':
    unittest.main()
