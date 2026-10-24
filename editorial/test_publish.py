import copy
import json
from pathlib import Path
import tempfile
import unittest
from publish import validate, render, validate_digest, render_digest, issue_stem


def candidate():
    return {'date': '2026-10-24', 'title': 'Uusi näkökulma', 'topic_id': 'new-topic',
            'facts': ['new-fact'], 'search_queries': ['AI työ', 'AI work'],
            'novelty': {'archive_reviewed': True, 'rationale': 'Uusi toteutus'},
            'sources': [{'id': '1', 'url': 'https://example.org/new', 'title': 'Evidence',
                         'published': '2026-10-19', 'verified_on': '2026-10-24', 'role': 'new_evidence'}],
            'sections': [{'heading': 'Työ', 'paragraphs': ['Tulkinta'], 'sources': ['1']}]}


def digest():
    items = []
    for n in range(3):
        d = candidate()
        d.update(topic_id=f'topic-{n}', facts=[f'fact-{n}'], source_ids=['1'])
        d['sources'][0]['url'] = f'https://example.org/new-{n}'
        d.update(new='New result', impact='Work', benefit='Measured benefit', limits='Limit')
        items.append(d)
    return {'format': 'digest-v2', 'date': '2026-10-24', 'edition': 'b', 'title': '3nostoa',
            'search_queries': ['AI work', 'AI työ'], 'items': items, 'synthesis': ['Next step']}


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

    def test_three_to_five_items_not_single_essay(self):
        d = digest()
        validate_digest(d, self.root)
        for count in (1, 2, 6):
            d['items'] = digest()['items'][:1] * count
            with self.assertRaises(ValueError):
                validate_digest(d, self.root)

    def test_every_item_needs_novel_evidence_not_only_digest(self):
        d = digest()
        d['items'][1]['sources'][0]['published'] = '2023-01-01'
        with self.assertRaisesRegex(ValueError, 'preceding 30 days'):
            validate_digest(d, self.root)

    def test_multi_item_history_blocks_repeat_in_any_later_item(self):
        old = digest()
        (self.root / 'editorial/issues/2026-10-24_b.json').write_text(json.dumps(old))
        d = digest()
        d['date'] = '2026-10-25'
        for item in d['items']:
            for s in item['sources']:s['verified_on'] = '2026-10-25'
        with self.assertRaisesRegex(ValueError, 'Repeated'):
            validate_digest(d, self.root)

    def test_no_same_story_split_into_three(self):
        d = digest()
        d['items'][1]['sources'][0]['url'] = d['items'][0]['sources'][0]['url']
        with self.assertRaisesRegex(ValueError, 'distinct fresh evidence'):
            validate_digest(d, self.root)

    def test_legacy_history_still_blocks_repeat_in_digest(self):
        old = candidate()
        old['topic_id'] = 'topic-1'
        (self.root / 'editorial/issues/2026-10-23.json').write_text(json.dumps(old))
        with self.assertRaisesRegex(ValueError, 'Repeated'):
            validate_digest(digest(), self.root)

    def test_suffix_and_complete_readable_digest(self):
        d = digest()
        self.assertEqual(issue_stem(d), '2026-10-24_b')
        html = render_digest(d)
        self.assertIn('3. Uusi näkökulma', html)
        self.assertIn('Mitä tästä kannattaa viedä käytäntöön', html)
        self.assertIn('Vaikutus työhön ja johtamiseen', html)
        d['edition'] = '../x'
        with self.assertRaises(ValueError):issue_stem(d)

    def test_material_digest_update_renders_edition_specific_prior_link(self):
        old = digest()
        (self.root / 'editorial/issues/2026-10-24_b.json').write_text(json.dumps(old))
        d = digest()
        for n, item in enumerate(d['items']):
            item['sources'][0]['url'] = f'https://example.org/new-result-{n}'
            item['novelty'].update(material_update=True, previous=['ai_arvoa_2026-10-24_b.html'])
        validate_digest(d, self.root)
        self.assertEqual(render_digest(d).count('href="ai_arvoa_2026-10-24_b.html"'), 3)


if __name__ == '__main__':
    unittest.main()
