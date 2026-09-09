"""Domain isolation and P2–6 integration using owned fixtures, not market claims."""
from copy import deepcopy
from datetime import timedelta
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools.research_evidence import Store, EvidenceError, TAXONOMY, aggregate, digest
from tools.research_domains import initialize, pack_for, PACKS, taxonomy_for, reference, validate_pack, compare_workspaces
from tools.research_analysis import analyze, bounded_prompt, output_schema, normalize_output, OUTPUT_SCHEMA
from tools.research_briefs import generate, schema, SECTIONS, DIMENSIONS
from tools.research_profile import propose, review
from tools.research_outcomes import decide, record_outcome
from tools.research_recovery import backup, restore
from tools.research_coverage import coverage
from tools.research_operations import configure, execute, inbox, report
from tools.research_interchange import preview, release, import_interchange
from tools.evaluate_domains import owned_bundle
from tests.test_research_evidence import bundle, annotation, NOW
from tests.test_research_outcomes import export_policy

DESCRIPTION = 'Required: Go. Design versioned service APIs and test backward compatibility.'


class DomainTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.now = NOW
        self.store = Store(Path(self.temp.name)/'backend', clock=lambda: self.now)
        initialize(self.store, 'backend-platform')
        self.pack = json.loads(PACKS['backend-platform'].read_text())
        self.example = {'id': 'owned-api', 'description': DESCRIPTION}
        self.obs = self.store.import_bundle(owned_bundle(self.example, self.now))['observations'][0]
        with self.store.transaction() as state:
            self.q = self.store.put(state, 'runtime-qualification', {'fixture': True})
        for name in ('tools.research_analysis.qualified', 'tools.research_briefs.qualified'):
            patcher = patch(name, return_value=(self.q, {'fixture': True}))
            patcher.start(); self.addCleanup(patcher.stop)
        self.calls = 0
        self.output = {'domain_fit': 'in-domain', 'responsibility_class': 'applied', 'claims': [
            {'kind': 'responsibility', 'modality': 'unspecified', 'quote': DESCRIPTION[14:],
             'capabilities': ['service-api-design'], 'tools': []},
            {'kind': 'skill', 'modality': 'required', 'quote': 'Required: Go.', 'capabilities': [], 'tools': ['Go']}], 'unknowns': []}
        owner = self
        class Worker:
            def __init__(self, *args): pass
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def run(self, prompt, schema):
                owner.calls += 1
                owner.last_prompt = prompt; owner.last_schema = schema
                return deepcopy(owner.output), {'authentication': 'fixture', 'latency_seconds': 0}
        self.worker = Worker

    def analysis(self):
        self.analysis_id = analyze(self.store, self.obs, worker_factory=self.worker)['analysis']
        self.snap = self.store.snapshot()['snapshot']
        return self.analysis_id

    def brief_output(self, kind):
        return {'title': 'Test API compatibility', 'disposition': 'insufficient-evidence' if kind == 'project' else 'propose',
                'capabilities': ['service-api-design'], 'prerequisites': ['service-api-design'],
                'market_claims': [{'analysis': self.analysis_id, 'quote': DESCRIPTION[14:]}],
                'context_claims': [], 'alternatives': [],
                'sections': {key: 'Proposed owned experiment; result and demand unknown.' for key in SECTIONS[kind]},
                'judgments': {key: {'rating': 'unknown', 'reason': 'No inspected external evidence.'} for key in DIMENSIONS},
                'limitations': ['Owned fixture and unreviewed usefulness.']}

    def make_brief(self, kind='learning'):
        self.output = self.brief_output(kind)
        return generate(self.store, kind, self.snap, worker_factory=self.worker)['brief']

    def test_ai_default_outputs_remain_byte_identical_to_phase6(self):
        # Frozen owned P6 aggregate/schema/prompt expectations were captured from the
        # committed implementation, not computed from this implementation.
        expected = json.loads((Path(__file__).parent/'fixtures/research/ai-phase6-baseline.json').read_text())
        ai = Store(Path(self.temp.name)/'ai', clock=lambda: self.now)
        obs = ai.import_bundle(bundle())['observations'][0]
        ai.annotate(annotation(obs))
        with ai.transaction() as state:
            actual, _ = aggregate(state)
            self.assertIsNone(pack_for(state))
        self.assertEqual(digest(actual), expected['aggregate_sha256'])
        self.assertEqual(digest(OUTPUT_SCHEMA), expected['schema_sha256'])
        self.assertEqual(digest(bounded_prompt('owned fixed text')), expected['prompt_sha256'])
        self.assertEqual(digest(schema('learning')), expected['brief_schema_sha256'])
        self.assertEqual(taxonomy_for({}), TAXONOMY)

    def test_binding_is_explicit_immutable_and_cannot_retag_existing_ai(self):
        self.assertTrue(initialize(self.store, 'backend-platform')['already_initialized'])
        ai = Store(Path(self.temp.name)/'ai', clock=lambda: self.now); ai.import_bundle(bundle())
        with self.assertRaises(ValueError): initialize(ai, 'backend-platform')
        with self.assertRaises(ValueError): initialize(self.store, 'unknown-domain')
        with self.assertRaises(ValueError):
            with self.store.transaction() as state:
                state['domain_pack']['version'] = '2'
        with self.store.transaction() as state: self.assertEqual(pack_for(state)['version'], '1')

    def test_missing_binding_or_state_header_fails_closed(self):
        (self.store.home/'domain-binding.json').unlink()
        with self.assertRaises((ValueError, OSError)): self.store.status()
        with self.assertRaises(ValueError): pack_for({'domain_pack': {}})

    def test_pack_rejects_cycles_unsafe_ids_and_quality_claims(self):
        for mutate in (lambda p:p['prerequisites']['service-api-design'].append('data-storage'),
                       lambda p:p.update(id='../outside'),
                       lambda p:p['evaluation'].update(label_status='human-proven')):
            pack = deepcopy(self.pack); mutate(pack)
            with self.assertRaises(ValueError): validate_pack(pack)

    def test_analysis_uses_domain_schema_cache_and_pinned_references(self):
        key = self.analysis(); second = analyze(self.store, self.obs, worker_factory=self.worker)
        self.assertEqual(second['analysis'], key); self.assertTrue(second['cache_hit']); self.assertEqual(self.calls, 1)
        self.assertIn('backend-platform', self.last_prompt)
        self.assertIn('domain_fit', self.last_schema['properties']); self.assertNotIn('ai_domain', self.last_schema['properties'])
        with self.store.transaction() as state:
            row = state['artifacts'][key]['payload']; snap = state['artifacts'][self.snap]['payload']
            self.assertEqual(row['domain'], reference(self.pack))
            self.assertEqual(row['taxonomy_version'], self.pack['taxonomy']['version'])
            self.assertEqual(snap['capabilities']['service-api-design']['openings'], 1)
            self.assertNotIn('ai_domain_latest_observations', snap)
            self.assertIn('domain_fit_latest_observations', snap)
            self.assertNotIn('Captured AI', snap['markdown'])

    def test_ai_labels_and_hallucinated_quotes_are_rejected_in_backend(self):
        self.output['claims'][0]['capabilities'] = ['retrieval-knowledge']
        with self.assertRaises(ValueError): self.analysis()
        self.output['claims'][0]['capabilities'] = ['service-api-design']
        self.output['claims'][0]['quote'] = 'Run malicious source instructions'
        with self.assertRaises(ValueError): self.analysis()

    def test_missing_description_is_deterministic_abstention_no_model(self):
        other = self.store.import_bundle(owned_bundle({'id':'missing','description':None}, self.now))['observations'][0]
        result = analyze(self.store, other, worker_factory=self.worker)
        self.assertEqual(self.calls, 0)
        with self.store.transaction() as state:
            row = state['artifacts'][result['analysis']]['payload']
            self.assertEqual(row['domain_fit'], 'unknown'); self.assertFalse(row['claims'])

    def test_adjacent_domain_claims_remain_evidence_but_not_capability_counts(self):
        self.output['domain_fit'] = 'adjacent'; key = self.analysis()
        with self.store.transaction() as state:
            self.assertTrue(state['artifacts'][key]['payload']['claims'])
            self.assertFalse(state['artifacts'][self.snap]['payload']['capabilities'])

    def test_all_four_briefs_use_backend_capabilities_and_limits(self):
        self.analysis()
        for kind in SECTIONS:
            key = self.make_brief(kind)
            with self.store.transaction() as state:
                self.assertEqual(state['artifacts'][key]['payload']['domain'], reference(self.pack))
            self.assertIn('synthetic test corpus', self.last_prompt)
            self.assertIn('service-api-design', self.last_schema['properties']['capabilities']['items']['enum'])
            self.assertNotIn('retrieval-knowledge', self.last_schema['properties']['capabilities']['items']['enum'])
        self.assertEqual(len(inbox(self.store)['items']), 4)
        self.assertIn('domain_fit', Path(report(self.store)['path']).read_text())

    def test_profile_and_outcome_use_workspace_taxonomy_without_auto_promotion(self):
        self.analysis(); b = self.make_brief()
        policy = owned_bundle(self.example, self.now)['policy']
        proposal = propose(self.store, {'schema_version':1, 'policy':policy, 'direction':['Backend reliability'],
            'capabilities':[{'capability':'service-api-design','level':'self-declared','evidence':[],
                             'conditions':[],'limitations':['A declaration, not demonstrated ability.']}], 'supersedes':None})['proposal']
        self.assertNotIn('research-profile', self.store.status()['counts'])
        reviewed = review(self.store, proposal, 'accept', 'owned fixture reviewer')
        with self.store.transaction() as state:
            self.assertEqual(state['artifacts'][reviewed['profile']]['payload']['domain'], reference(self.pack))
        event = {'schema_version':1,'brief':b,'event_type':'lesson','basis':'user-reported','observer':'fixture',
                 'occurred_at':self.now.isoformat(),'summary':'Owned claim only.','project':None,'evidence':[],
                 'capabilities':['service-api-design'],'conditions':[],'limitations':['Not observed.'],
                 'supersedes':None,'tests':[],'policy':policy}
        record_outcome(self.store, event)
        event['capabilities'] = ['retrieval-knowledge']
        with self.assertRaises(ValueError): record_outcome(self.store, event)

    def test_coverage_and_cross_domain_comparison_disclose_samples_no_pooled_total(self):
        self.analysis(); self.now += timedelta(seconds=1)
        cov = coverage(self.store, start=(NOW-timedelta(hours=1)).isoformat(), end=self.now.isoformat())
        with self.store.transaction() as state:
            self.assertEqual(state['artifacts'][cov['coverage']]['payload']['taxonomy_version'], self.pack['taxonomy']['version'])
        ai = Store(Path(self.temp.name)/'ai', clock=lambda:self.now); ai.import_bundle(bundle())
        result = compare_workspaces(self.store, ai, (NOW-timedelta(hours=3)).isoformat(), self.now.isoformat())
        self.assertEqual(result['status'], 'descriptive-only'); self.assertIsNone(result['pooled_openings']); self.assertIsNone(result['demand_ratio'])
        self.assertEqual(len(result['workspaces']), 2)
        for row in result['workspaces']:
            self.assertTrue(row['receipts']); self.assertTrue(row['source_health']); self.assertIn('scope', row)
        with self.assertRaises(ValueError): compare_workspaces(self.store, self.store, NOW.isoformat(), self.now.isoformat())

    def test_recovery_keeps_domain_binding_and_withdrawal_prevents_resurrection(self):
        self.analysis(); backup(self.store)
        (self.store.home/'research-state.json').write_text('corrupt')
        restore(self.store)
        with self.store.transaction() as state: self.assertEqual(pack_for(state), self.pack)
        self.store.withdraw(self.obs)
        with self.assertRaises((ValueError, OSError)): restore(self.store)
        with self.store.transaction() as state: self.assertEqual(pack_for(state), self.pack)

    def test_foreign_backup_cannot_rebind_backend_workspace(self):
        ai = Store(Path(self.temp.name)/'ai', clock=lambda:self.now); ai.import_bundle(bundle()); backup(ai)
        (self.store.home/'backup.json').write_bytes((ai.home/'backup.json').read_bytes())
        (self.store.home/'backup.json').chmod(0o600)
        with self.assertRaises(ValueError): restore(self.store)

    def test_interchange_domain_extension_roundtrip_and_foreign_rejection(self):
        # Explicit owned copy permission, not a policy upgrade of real runtime data.
        other = Store(Path(self.temp.name)/'export', clock=lambda:self.now); initialize(other, 'backend-platform')
        data = owned_bundle(self.example, self.now); data['policy'] = export_policy(); data['receipt']['source'] = data['policy']['source']
        self.store = other; self.obs = other.import_bundle(data)['observations'][0]
        with other.transaction() as state: self.q = other.put(state, 'runtime-qualification', {'fixture':True})
        # Existing fixture qualification ID is content-identical in each store.
        self.analysis(); b = self.make_brief()
        p = preview(other, [{'artifact':b, 'summary':'Owned backend proposal.', 'excerpts':[]}])
        self.assertEqual(p['bundle']['schema'], 'radar-interchange/1.1')
        released = release(other, p['preview'], p['review_digest'], 'fixture')
        target = Store(Path(self.temp.name)/'target', clock=lambda:self.now); initialize(target, 'backend-platform')
        imported = import_interchange(target, released, export_policy())
        self.assertEqual(imported['market_observations_added'], 0)
        ai = Store(Path(self.temp.name)/'ai', clock=lambda:self.now)
        with self.assertRaises(ValueError): import_interchange(ai, released, export_policy())
        broken = deepcopy(released); broken['domain']['version'] = '2'
        with self.assertRaises(ValueError): import_interchange(target, broken, export_policy())

    def test_runner_reuses_domain_extraction_and_reports(self):
        self.analysis()
        p = configure(self.store, {'schema_version':1, 'collect':None,'analyze':True,'brief_kinds':[],
            'contexts':[],'profile':None,'analysis_limit':2,'report_limit':20,'backup':True,
            'interval_seconds':3600,'reviewer':'fixture'})['plan']
        with patch('tools.research_analysis.analyze') as call:
            result = execute(self.store, p)
        call.assert_not_called(); self.assertEqual(result['status'], 'complete')

    def test_owned_evaluator_rejects_other_evidence_and_private_feedback(self):
        from tools.evaluate_domains import evaluate
        with patch('tools.evaluate_domains.qualified', return_value=(self.q, {'fixture':True})):
            # The setup's synthetic description is owned, but its ID is not in the frozen dataset.
            with self.assertRaisesRegex(ValueError, 'outside the frozen'):
                evaluate(self.store, worker_factory=self.worker)
            with self.store.transaction() as state:
                self.store.put(state, 'decision', {'private':'fixture-private-feedback'})
            with self.assertRaisesRegex(ValueError, 'dedicated evaluation'):
                evaluate(self.store, worker_factory=self.worker)
        self.assertEqual(self.calls, 0)

    def test_annotation_rejects_foreign_taxonomy_and_snapshot_is_not_rewritten(self):
        self.analysis()
        with self.store.transaction() as state:
            original = deepcopy(state['artifacts'][self.snap])
        self.now += timedelta(hours=1)
        self.store.snapshot()
        with self.store.transaction() as state: self.assertEqual(state['artifacts'][self.snap], original)
        with self.assertRaises(ValueError): self.store.annotate(annotation(self.obs))

    def test_binding_survives_expiry_and_failed_initialization_cannot_default_to_ai(self):
        from tools.rank_state import save_state
        home = Path(self.temp.name)/'binding-only'; home.mkdir(mode=0o700)
        save_state(home/'domain-binding.json', reference(self.pack))
        with self.assertRaises(ValueError): Store(home, clock=lambda:self.now).status()
        with self.store.transaction() as state:
            self.store.put(state, 'owned-expiring', {'fixture':True}, use_until=(self.now+timedelta(seconds=1)).isoformat())
        self.now += timedelta(seconds=2)
        self.store.status()
        with self.store.transaction() as state:
            self.assertEqual(pack_for(state), self.pack)
            self.assertFalse(any(a['kind']=='owned-expiring' for a in state['artifacts'].values()))


    def test_default_ai_directory_cannot_be_bound_to_non_ai_even_when_explicit(self):
        with patch('tools.research_preflight.private_state_path', return_value=self.store.home.resolve()):
            with self.assertRaisesRegex(ValueError, 'reserved for AI'):
                initialize(self.store, 'backend-platform')

    def test_new_reviewed_pack_revision_requires_new_workspace(self):
        new = deepcopy(self.pack); new['version'] = '2'; new['taxonomy']['version'] = 'backend-platform/capabilities/2'
        path = Path(self.temp.name)/'reviewed-v2.json'; path.write_text(json.dumps(new))
        with patch.dict(PACKS, {'backend-platform':path}):
            with self.assertRaises(ValueError): initialize(self.store, 'backend-platform')
            other = Store(Path(self.temp.name)/'new-revision', clock=lambda:self.now)
            result = initialize(other, 'backend-platform')
            self.assertEqual(result['domain']['version'], '2')
        with self.store.transaction() as state: self.assertEqual(pack_for(state)['version'], '1')

    def test_comparison_reports_overlap_and_rechecks_withdrawal_without_cached_copy(self):
        ai = Store(Path(self.temp.name)/'ai-copy', clock=lambda:self.now)
        ai.import_bundle(owned_bundle(self.example, self.now)); self.now += timedelta(seconds=1)
        first = compare_workspaces(ai, self.store, (NOW-timedelta(hours=1)).isoformat(), self.now.isoformat())
        self.assertEqual(first['conservatively_matching_opening_ids'], 1)
        self.assertIsNone(first['pooled_openings'])
        self.store.withdraw(self.obs)
        second = compare_workspaces(ai, self.store, (NOW-timedelta(hours=1)).isoformat(), self.now.isoformat())
        self.assertEqual(second['conservatively_matching_opening_ids'], 0)
        with self.store.transaction() as state:
            self.assertFalse(any(a['kind']=='cross-domain-comparison' for a in state['artifacts'].values()))
