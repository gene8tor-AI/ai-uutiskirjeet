import copy
import json
from pathlib import Path
import tempfile
import unittest
from publish import validate, render


def candidate():
    return {'date': '2026-10-24', 'title': 'Uusi näkökulma', 'topic_id': 'new-topic',
            'facts': ['new-fact'], 'search_queries': ['AI työ', 'AI work'],
            'novelty': {'archive_reviewed': True, 'rationale': 'Uusi toteutus'},
            'sources': [{'id': '1', 'url': 'https://example.org/new', 'title': 'Evidence',
                         'published': '2026-10-19', 'verified_on': '2026-10-24', 'role': 'new_evidence'}],
            'sections': [{'heading': 'Työ', 'paragraphs': ['Tulkinta'], 'sources': ['1']}]}


class Publication(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'editorial/issues').mkdir(parents=True)

    def test_old_research_cannot_be_new_issue(self):
        d = candidate()
        d['sources'][0]['published'] = '2023-04-01'
        with self.assertRaisesRegex(ValueError, 'preceding 30 days'):
            validate(d, self.root)

    def test_same_claim_new_title_is_blocked(self):
        old = candidate()
        (self.root / 'editorial/issues/2026-10-23.json').write_text(json.dumps(old))
        d = copy.deepcopy(old)
        d.update(title='Eri otsikko', topic_id='different-topic')
        with self.assertRaisesRegex(ValueError, 'Repeated'):
            validate(d, self.root)

    def test_material_update_requires_new_evidence_and_prior_reference(self):
        old = candidate()
        old['date'] = '2026-10-23'
        (self.root / 'editorial/issues/2026-10-23.json').write_text(json.dumps(old))
        d = candidate()
        d['novelty'].update(material_update=True, previous=['ai_arvoa_2026-10-23.html'])
        with self.assertRaises(ValueError):
            validate(d, self.root)
        d['sources'][0]['url'] = 'https://example.org/new-result'
        self.assertEqual(validate(d, self.root), [])

    def test_other_series_source_overlap_must_be_assessed(self):
        (self.root / 'paivan_ai_uutiset_2026-10-20.html').write_text('<a href="https://example.org/new?utm=x">Same</a>')
        d = candidate()
        fresh = copy.deepcopy(d['sources'][0])
        fresh.update(id='2', url='https://example.org/genuinely-new')
        d['sources'].append(fresh)
        with self.assertRaisesRegex(ValueError, 'overlap'):
            validate(d, self.root)
        d['novelty']['related_archive'] = ['paivan_ai_uutiset_2026-10-20.html']
        self.assertEqual(len(validate(d, self.root)), 1)

    def test_research_verification_and_citations_required(self):
        d = candidate()
        d['sources'][0]['verified_on'] = '2026-10-23'
        with self.assertRaisesRegex(ValueError, 'Open each'):
            validate(d, self.root)
        d = candidate()
        d['sections'][0]['sources'] = ['missing']
        with self.assertRaisesRegex(ValueError, 'citation'):
            validate(d, self.root)

    def test_escape_untrusted_source_and_article_text(self):
        d = candidate()
        d['title'] = '<script>alert(1)</script>'
        d['sections'][0]['paragraphs'] = ['<img src=x onerror=alert(1)>']
        html = render(d)
        self.assertNotIn('<script>', html)
        self.assertNotIn('<img', html)
        self.assertIn('&lt;script&gt;', html)
        self.assertIn('lang="fi"', html)

    def test_renaming_both_ids_does_not_make_used_evidence_new(self):
        old = candidate()
        old['date'] = '2026-10-23'
        (self.root / 'editorial/issues/2026-10-23.json').write_text(json.dumps(old))
        d = candidate()
        d.update(topic_id='renamed-topic', facts=['renamed-fact'])
        with self.assertRaisesRegex(ValueError, 'already covered'):
            validate(d, self.root)

    def test_evidence_needs_citation_but_explicit_analysis_does_not(self):
        d = candidate()
        d['sections'][0]['sources'] = []
        with self.assertRaisesRegex(ValueError, 'require citations'):
            validate(d, self.root)
        d['sections'][0]['kind'] = 'analysis'
        validate(d, self.root)

    def test_update_prior_coverage_visible(self):
        d = candidate()
        d['novelty']['previous'] = ['ai_arvoa_2026-10-20.html']
        self.assertIn('href="ai_arvoa_2026-10-20.html"', render(d))


if __name__ == '__main__':
    unittest.main()
