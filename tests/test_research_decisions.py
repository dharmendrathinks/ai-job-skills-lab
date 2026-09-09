"""Behavioral P3 checks with owned evidence and injected model outputs, no inference."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tools.research_evidence import Store, EvidenceError
from tools.research_context import import_context, acquire, import_radar
from tools.research_profile import propose, review
from tools.research_briefs import SECTIONS, DIMENSIONS, generate, schema, inputs
from tools.research_decisions import inspect_brief
from tests.test_research_evidence import bundle, annotation, BODY

NOW = datetime(2026, 9, 9, 12, tzinfo=timezone.utc)


def context_bundle(category='repository', content='Owned fixture: improve retrieval evaluation.', locator=None):
    locator = locator or ('a' * 40 + ':README.md' if category == 'repository' else 'https://owned.example/context')
    policy = bundle()['policy']
    policy.update(method='reviewed-context', hosted_disclosure=True,
                  hosted_retention='provider-managed-no-deletion-deadline', hosted_permission_reference='author-owned fixture')
    receipt = bundle()['receipt']
    receipt.update(kind='context', query='owned-context', started_at=NOW.isoformat(), finished_at=NOW.isoformat(),
                   pages=[{'locator': locator, 'status': 'ok', 'returned': 1, 'next_cursor': None}])
    return {'schema_version': 1, 'policy': policy,
        'request': {'schema_version': 1, 'problem': 'retrieval evaluation', 'category': category, 'locators': [locator],
                    'query': 'owned-context', 'period': {'from': None, 'to': None}, 'max_items': 1},
        'receipt': receipt, 'records': [{'schema_version': 1, 'source': 'owned-fixture', 'evidence_type': category,
                    'original_date': None, 'date_precision': 'unknown', 'revision': 'a' * 40 if category == 'repository' else None,
                    'captured_at': NOW.isoformat(), 'content': content, 'locator': locator,
                    'inspector': 'fixture author', 'inspection_depth': 'README-only inspection; no tests run',
                    'observation_basis': 'inspected', 'conditions': [], 'lineage': [locator],
                    'limitations': ['Owned fixture, not market or audience evidence.']}]}


class DecisionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.now = NOW
        self.store = Store(Path(self.temp.name) / 'state', clock=lambda: self.now)
        data = bundle()
        data['policy'].update(hosted_disclosure=True, hosted_retention='provider-managed-no-deletion-deadline', hosted_permission_reference='owned')
        self.obs = self.store.import_bundle(data)['observations'][0]
        self.analysis = self.store.annotate(annotation(self.obs))['analysis']
        self.snapshot = self.store.snapshot()['snapshot']
        with self.store.transaction() as state:
            self.qualification = self.store.put(state, 'runtime-qualification', {'test_only': True})
        self.runtime = patch('tools.research_briefs.qualified', return_value=(self.qualification, {'test_only': True}))
        self.runtime.start(); self.addCleanup(self.runtime.stop)
        self.calls = 0
        self.on_run = lambda: None
        self.output = None
        owner = self
        class Worker:
            def __init__(self, *args): pass
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def run(self, prompt, schema):
                owner.calls += 1
                owner.on_run()
                return deepcopy(owner.output), {'latency_seconds': 0, 'authentication': 'fixture'}
        self.worker = Worker

    def output_for(self, kind):
        return {'title': 'Test retrieval with held-out failures', 'disposition': 'insufficient-evidence' if kind == 'project' else 'propose',
                'capabilities': ['retrieval-knowledge'], 'prerequisites': ['data-pipelines'],
                'market_claims': [{'analysis': self.analysis, 'quote': BODY[:26]}],
                'context_claims': [], 'alternatives': [],
                'sections': {name: 'Proposed: compare a baseline on owned held-out examples; no result claimed.' for name in SECTIONS[kind]},
                'judgments': {name: {'rating': 'unknown', 'reason': 'Insufficient inspected context.'} for name in DIMENSIONS},
                'limitations': ['Unknown human usefulness; source sample only.']}

    def brief(self, kind='learning', contexts=(), profile=None, refresh=False):
        return generate(self.store, kind, self.snapshot, contexts, profile, worker_factory=self.worker, refresh=refresh)

    def context(self, category='repository', **kwargs):
        return import_context(self.store, context_bundle(category, **kwargs))['contexts'][0]

    def test_four_distinct_outputs_with_missing_context_limits(self):
        for kind in SECTIONS:
            self.output = self.output_for(kind)
            result = self.brief(kind)
            with self.store.transaction() as state:
                record = state['artifacts'][result['brief']]['payload']
                self.assertEqual(set(record['proposal']['sections']), set(SECTIONS[kind]))
                self.assertEqual(record['status'], 'draft-human-review')
        self.assertEqual(self.calls, 4)

    def test_invented_market_quote_or_alternative_rejected(self):
        self.output = self.output_for('project')
        self.output['market_claims'][0]['quote'] = 'Invented explicit requirement'
        with self.assertRaises(EvidenceError): self.brief('project')
        self.output = self.output_for('project')
        self.output['alternatives'] = [{'context': 'uninspected-library', 'reason': 'popular'}]
        with self.assertRaises(EvidenceError): self.brief('project')

    def test_contribution_uses_inspected_repository_and_propagates_limits(self):
        ctx = self.context()
        self.output = self.output_for('project')
        self.output.update(disposition='contribute', alternatives=[{'context': ctx, 'reason': 'Extend inspected evaluation fixture.'}])
        result = self.brief('project', [ctx])
        with self.store.transaction() as state:
            self.assertIn('Owned fixture, not market or audience evidence.', state['artifacts'][result['brief']]['payload']['evidence_limits'])
        self.store.withdraw(ctx)
        with self.store.transaction() as state: self.assertNotIn(result['brief'], state['artifacts'])

    def test_propose_project_without_alternatives_is_rejected(self):
        self.output = self.output_for('project'); self.output['disposition'] = 'propose'
        with self.assertRaises(EvidenceError): self.brief('project')

    def test_no_project_is_valid(self):
        self.output = self.output_for('project'); self.output['disposition'] = 'no-project'
        self.brief('project')

    def test_commercial_and_video_claims_need_external_support(self):
        for dimension in ('commercial_validation', 'video_suitability'):
            self.output = self.output_for('product')
            self.output['judgments'][dimension]['rating'] = 'high'
            with self.assertRaises(EvidenceError): self.brief('product')

    def test_stale_discussion_does_not_establish_current_video_suitability(self):
        data = context_bundle('discussion')
        data['records'][0].update(original_date='2020-01-01', date_precision='day')
        ctx = import_context(self.store, data)['contexts'][0]
        self.output = self.output_for('youtube'); self.output['judgments']['video_suitability']['rating'] = 'high'
        with self.assertRaises(EvidenceError): self.brief('youtube', [ctx])

    def test_contradictory_product_context_is_preserved(self):
        ctx = self.context('problem', content='Owned fixture: this workflow is not painful.')
        self.output = self.output_for('product')
        self.output['context_claims'] = [{'context': ctx, 'quote': 'this workflow is not painful.', 'relation': 'contradicts'}]
        result = self.brief('product', [ctx])
        with self.store.transaction() as state:
            self.assertEqual(state['artifacts'][result['brief']]['payload']['proposal']['context_claims'][0]['relation'], 'contradicts')

    def test_cache_repeat_and_mid_run_withdrawal(self):
        self.output = self.output_for('learning')
        first = self.brief(); second = self.brief()
        self.assertEqual(first['brief'], second['brief']); self.assertEqual(self.calls, 1)
        self.on_run = lambda: self.store.withdraw(self.obs)
        with self.assertRaises(EvidenceError): self.brief(refresh=True)
        with self.store.transaction() as state: self.assertNotIn(first['brief'], state['artifacts'])

    def test_context_expiry_removes_derivatives_and_blocks_reimport(self):
        data = context_bundle()
        data['policy']['use_until'] = (NOW + timedelta(minutes=1)).isoformat()
        ctx = import_context(self.store, data)['contexts'][0]
        self.output = self.output_for('learning')
        result = self.brief(contexts=[ctx])
        self.now += timedelta(minutes=2)
        with self.store.transaction() as state: self.assertNotIn(result['brief'], state['artifacts'])
        data['policy'].pop('use_until')
        with self.assertRaises(EvidenceError): import_context(self.store, data)

    def test_missing_rights_unknown_version_and_missing_date_rejected(self):
        for change in ('rights', 'version', 'date'):
            data = context_bundle()
            if change == 'rights': data['policy']['permission_basis'] = ''
            if change == 'version': data['schema_version'] = 2
            if change == 'date': data['records'][0]['date_precision'] = 'instant'
            with self.assertRaises(EvidenceError): import_context(self.store, data)

    def test_profile_requires_review_and_does_not_change_market(self):
        data = {'schema_version': 1, 'policy': context_bundle()['policy'], 'direction': ['Deeper retrieval testing'],
                'capabilities': [{'capability': 'retrieval-knowledge', 'level': 'self-declared', 'evidence': [], 'conditions': [], 'limitations': ['No inspected results.']}], 'supersedes': None}
        proposal = propose(self.store, data)['proposal']
        before = self.store.snapshot()
        self.output = self.output_for('learning')
        with self.assertRaises(EvidenceError): self.brief(profile=proposal)
        result = review(self.store, proposal, 'reject', 'synthetic reviewer')
        self.assertEqual(result['status'], 'rejected-no-profile-change')
        profile = review(self.store, proposal, 'accept', 'synthetic reviewer')['profile']
        brief = self.brief(profile=profile)
        self.assertEqual(before, self.store.snapshot())
        with self.store.transaction() as state:
            record = state['artifacts'][brief['brief']]['payload']
            self.assertEqual(record['profile_evidence']['capabilities'][0]['level'], 'self-declared')

    def test_keyword_or_readme_cannot_prove_demonstrated_ability(self):
        ctx = self.context()
        data = {'schema_version': 1, 'policy': context_bundle()['policy'], 'direction': ['Learn'],
                'capabilities': [{'capability': 'retrieval-knowledge', 'level': 'demonstrated', 'evidence': [ctx], 'conditions': ['README'], 'limitations': ['No test run.']}], 'supersedes': None}
        with self.assertRaises(EvidenceError): propose(self.store, data)

    def test_direct_acquisition_failure_receipt_no_retry(self):
        data = context_bundle('product'); data['records'] = []
        calls = []
        def fail(url): calls.append(url); raise OSError('blocked')
        with self.assertRaises(EvidenceError): acquire(self.store, data, fetch=fail)
        self.assertEqual(len(calls), 1)
        with self.store.transaction() as state:
            receipts = [a['payload'] for a in state['artifacts'].values() if a['kind'] == 'context-receipt']
            self.assertIn('failed', [r['completeness'] for r in receipts])

    def test_direct_acquisition_records_unknown_dates(self):
        data = context_bundle('product'); data['records'] = []
        result = acquire(self.store, data, fetch=lambda url: ('Owned product document.', 'utf8-text/1'))
        with self.store.transaction() as state:
            self.assertIsNone(state['artifacts'][result['contexts'][0]]['payload']['original_date'])

    def test_read_only_radar_import_idempotence_and_no_primary_upgrade(self):
        report = {'schema_version': '3.0', 'scan_id': 'owned-scan', 'generated_at': NOW.isoformat(),
                  'recommendations': [{'topic_id': 'owned-topic', 'revision': 1, 'title': 'Owned topic',
                                       'what_changed': 'Generated assessment', 'source_links': ['https://owned.example/context'],
                                       'evidence_quotes': [{'quote': 'Unverified quote.', 'source_url': 'https://owned.example/context'}]}], 'watch': []}
        data = context_bundle('imported-assessment', locator='radar:owned-scan:owned-topic')
        data['records'] = []
        first = import_radar(self.store, report, data, ['owned-topic'])
        second = import_radar(self.store, report, data, ['owned-topic'])
        self.assertEqual(first, second)
        ctx = first['contexts'][0]
        self.output = self.output_for('learning')
        self.output['context_claims'] = [{'context': ctx, 'quote': 'Unverified quote.', 'relation': 'supports'}]
        with self.assertRaises(EvidenceError): self.brief(contexts=[ctx])
        self.store.withdraw(ctx)
        report['recommendations'][0]['what_changed'] = 'Changed generated wrapper, same withdrawn original quote.'
        with self.assertRaises(EvidenceError): import_radar(self.store, report, data, ['owned-topic'])
        report['schema_version'] = '4.0'
        with self.assertRaises(EvidenceError): import_radar(self.store, report, data, ['owned-topic'])

    def test_schema_binds_artifact_ids_instead_of_freeform_analysis(self):
        with self.store.transaction() as state:
            data = inputs(state, self.snapshot, [], None, self.now)
        generated = schema('learning', data)
        choices = generated['properties']['market_claims']['items']['properties']['analysis']['enum']
        self.assertEqual(choices, [self.analysis])

    def test_inspection_metadata_is_not_a_source_quote(self):
        ctx = self.context()
        self.output = self.output_for('learning')
        self.output['context_claims'] = [{'context': ctx, 'quote': 'Owned fixture, not market or audience evidence.', 'relation': 'supports'}]
        with self.assertRaises(EvidenceError): self.brief(contexts=[ctx])
        with self.store.transaction() as state:
            rejected = [a for a in state['artifacts'].values() if a['kind'] == 'brief-execution' and a['payload']['status'] == 'rejected']
            self.assertEqual(len(rejected), 1)

    def test_quota_failure_is_recorded_without_retry(self):
        self.output = self.output_for('learning')
        def fail(): raise EvidenceError('quota exhausted')
        self.on_run = fail
        with self.assertRaises(EvidenceError): self.brief()
        self.assertEqual(self.calls, 1)
        self.assertEqual(self.store.status()['counts']['brief-failure'], 1)

    def test_missing_context_content_cannot_supply_alternative(self):
        ctx = self.context(content=None)
        self.output = self.output_for('project')
        self.output.update(disposition='contribute', alternatives=[{'context': ctx, 'reason': 'Uninspected'}])
        with self.assertRaises(EvidenceError): self.brief('project', [ctx])

    def test_repository_acquisition_reads_pinned_objects_without_execution(self):
        repo = Path(self.temp.name) / 'repo'; repo.mkdir()
        def git(*args):
            return subprocess.check_output(['git', '-C', str(repo), *args], stderr=subprocess.DEVNULL, text=True).strip()
        git('init', '-q')
        (repo / 'README.md').write_text('Owned source fixture, no execution.')
        git('add', 'README.md')
        git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.test', '-c', 'core.hooksPath=/dev/null', 'commit', '-qm', 'fixture')
        rev = git('rev-parse', 'HEAD')
        data = context_bundle(locator=rev + ':README.md'); data['records'] = []
        result = acquire(self.store, data, repo=repo)
        with self.store.transaction() as state:
            row = state['artifacts'][result['contexts'][0]]['payload']
            self.assertEqual(row['revision'], rev)
            self.assertEqual(row['content'], 'Owned source fixture, no execution.')
        self.assertEqual(git('status', '--porcelain'), '')

    def test_inspected_results_support_only_scoped_profile_demonstration(self):
        data = context_bundle('experiment-result')
        data['records'][0].update(observation_basis='reproduced', conditions=['Owned fixture, exact revision and held-out inputs.'])
        ctx = import_context(self.store, data)['contexts'][0]
        proposal = propose(self.store, {'schema_version': 1, 'policy': data['policy'], 'direction': ['Evaluation'],
                'capabilities': [{'capability': 'retrieval-knowledge', 'level': 'demonstrated', 'evidence': [ctx],
                                  'conditions': ['Owned fixture only'], 'limitations': ['Not production experience.']}], 'supersedes': None})['proposal']
        profile = review(self.store, proposal, 'accept', 'synthetic reviewer')['profile']
        self.store.withdraw(ctx)
        with self.store.transaction() as state: self.assertNotIn(profile, state['artifacts'])

    def test_no_extra_market_evidence_from_duplicate_contexts_or_profiles(self):
        before = self.store.snapshot()
        ctx = self.context()
        self.output = self.output_for('learning')
        self.brief(contexts=[ctx, ctx])
        self.assertEqual(before, self.store.snapshot())

    def test_inspection_shows_source_trace_and_rejects_withdrawn_brief(self):
        self.output = self.output_for('learning')
        self.output['title'] = 'Review \x1b[31mtext\u202e'
        result = self.brief()
        viewed = inspect_brief(self.store, result['brief'])
        self.assertIn(BODY[:26], viewed)
        self.assertIn('https://employer.example/jobs/req-1', viewed)
        self.assertNotIn('\x1b', viewed)
        self.assertNotIn('\u202e', viewed)
        self.store.withdraw(self.obs)
        with self.assertRaises(EvidenceError): inspect_brief(self.store, result['brief'])

    def test_inspection_does_not_count_repository_files_as_distinct_alternatives(self):
        first = self.context()
        second = self.context(content='Second inspected file.', locator='a' * 40 + ':tests/test_example.py')
        self.output = self.output_for('project')
        self.output.update(disposition='contribute', alternatives=[{'context': c, 'reason': 'Review one repository.'} for c in (first, second)])
        result = self.brief('project', [first, second])
        self.assertIn('Distinct alternative sources: 1', inspect_brief(self.store, result['brief']))

    def test_phase5_coverage_is_a_grounded_brief_input(self):
        from tools.research_coverage import coverage
        self.snapshot = coverage(self.store, expected={'language':['de']})['coverage']
        self.output = self.output_for('learning')
        result = self.brief()
        with self.store.transaction() as state:
            self.assertEqual(state['artifacts'][result['brief']]['payload']['snapshot'], self.snapshot)
            data = inputs(state, self.snapshot, [], None, self.now)
            self.assertIn('period',data['coverage'])
            self.assertEqual(data['coverage']['missing_segments']['language'],['de'])


if __name__ == '__main__': unittest.main()
