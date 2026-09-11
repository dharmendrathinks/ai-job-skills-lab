"""P4 behavioral integration with owned fixtures; no real feedback invented."""
from copy import deepcopy
from datetime import timedelta
import json
from pathlib import Path
import tempfile
import unittest

from tools.research_evidence import Store, EvidenceError, digest
from tools.research_context import import_context
from tools.research_outcomes import decide, record_outcome, reconsider, propose_from_outcome, history
from tools.research_profile import review
from tools.research_interchange import preview, release, import_interchange, markdown
from tools.research_briefs import generate
from tests import test_research_decisions as fixtures
from tests.test_research_decisions import context_bundle, NOW


class OutcomeTests(unittest.TestCase):
    setUp = fixtures.DecisionTests.setUp
    output_for = fixtures.DecisionTests.output_for
    brief = fixtures.DecisionTests.brief
    context = fixtures.DecisionTests.context

    def test_renamed_producer_preserves_legacy_echo_withdrawal(self):
        from tools.research_interchange import PRODUCER, withdrawal_tokens
        self.assertEqual(PRODUCER,'ai-job-skills-lab')
        for producer in (PRODUCER,'ai-job-radar'):
            row={'origin':{'producer':producer,'id':'a'*64,'revision':'a'*64},'content':{},'sources':[]}
            self.assertIn('a'*64,withdrawal_tokens(row))
    def make_brief(self):
        self.output = self.output_for('learning')
        return self.brief()['brief']

    def decision(self, brief, decision='rejected', supersedes=None, **kw):
        return {'schema_version': 1, 'brief': brief, 'decision': decision, 'reason': 'Owned fixture review, not user feedback.',
                'reviewer': 'fixture', 'decided_at': self.now.isoformat(), 'defer_until': None,
                'target': None, 'supersedes': supersedes, **kw}

    def event(self, brief, **kw):
        return {'schema_version': 1, 'brief': brief, 'event_type': 'lesson', 'basis': 'user-reported',
                'observer': 'private observer canary', 'occurred_at': self.now.isoformat(),
                'summary': 'Owned fixture lesson; not actual work.', 'project': None, 'evidence': [],
                'capabilities': [], 'conditions': [], 'limitations': ['Owned scenario only.'],
                'supersedes': None, 'tests': [], 'policy': context_bundle()['policy'], **kw}

    def enable_owned_exports(self):
        # Create a fresh owned corpus with explicit unlimited copy permission.
        from tests.test_research_evidence import bundle, annotation
        self.store = Store(Path(self.temp.name) / 'export-state', clock=lambda: self.now)
        data = bundle(); data['policy'] = export_policy()
        self.obs = self.store.import_bundle(data)['observations'][0]
        self.analysis = self.store.annotate(annotation(self.obs))['analysis']
        self.snapshot = self.store.snapshot()['snapshot']
        with self.store.transaction() as state:
            self.store.put(state, 'runtime-qualification', {'test_only': True})

    def request(self, key):
        return [{'artifact': key, 'summary': 'Reviewed owned experiment summary.', 'excerpts': []}]

    def test_decisions_idempotent_and_explicit_correction(self):
        b = self.make_brief(); row = self.decision(b)
        first = decide(self.store, row); self.assertEqual(first, decide(self.store, row))
        with self.assertRaises(EvidenceError): decide(self.store, self.decision(b, 'accepted'))
        second = decide(self.store, self.decision(b, 'accepted', first['decision']))
        log = history(self.store, b)
        self.assertEqual(len(log['events']), 2); self.assertEqual(list(log['latest_decisions']), [second['decision']])
        self.assertNotIn('research-profile', self.store.status()['counts'])

    def test_rejection_blocks_refresh_and_changed_profile_or_prompt(self):
        b = self.make_brief(); decide(self.store, self.decision(b))
        self.now += timedelta(days=1)
        with self.assertRaises(EvidenceError): self.brief(refresh=True)
        self.assertEqual(self.calls, 1)

    def test_material_evidence_needs_review_before_reconsideration(self):
        b = self.make_brief(); decide(self.store, self.decision(b))
        ctx = self.context(content='Owned new baseline failure evidence.')
        with self.assertRaises(EvidenceError): self.brief(contexts=[ctx])
        rec = reconsider(self.store, {'schema_version': 1, 'brief': b, 'evidence': [ctx],
                                     'reason': 'New inspected baseline failure.', 'reviewer': 'fixture'})['reconsideration']
        result = generate(self.store, 'learning', self.snapshot, [ctx], worker_factory=self.worker, reconsideration=rec)
        with self.store.transaction() as state:
            self.assertEqual(state['artifacts'][result['brief']]['payload']['revises'], b)
        self.store.withdraw(ctx)
        with self.store.transaction() as state: self.assertNotIn(result['brief'], state['artifacts'])

    def test_rewrapped_existing_context_is_not_material(self):
        ctx = self.context(); self.output = self.output_for('learning'); b = self.brief(contexts=[ctx])['brief']
        other = self.context(locator='b' * 40 + ':README.md')
        with self.assertRaises(EvidenceError):
            reconsider(self.store, {'schema_version': 1, 'brief': b, 'evidence': [other], 'reason': 'Same content.', 'reviewer': 'fixture'})

    def test_defer_until_and_duplicate_targets(self):
        b = self.make_brief(); decide(self.store, self.decision(b, 'deferred', defer_until=(self.now + timedelta(days=1)).isoformat()))
        with self.assertRaises(EvidenceError): self.brief(refresh=True)
        self.now += timedelta(days=2); self.brief(refresh=True)
        with self.assertRaises(EvidenceError): decide(self.store, self.decision(b, 'duplicate', target=b))

    def test_feedback_changed_during_generation_discards_output(self):
        b = self.make_brief()
        self.on_run = lambda: decide(self.store, self.decision(b))
        with self.assertRaises(EvidenceError): self.brief(refresh=True)
        self.assertEqual(self.store.status()['counts']['brief'], 1)

    def test_outcome_does_not_change_counts_or_profile(self):
        b = self.make_brief(); before = self.store.snapshot()
        row = self.event(b); first = record_outcome(self.store, row)
        self.assertEqual(first, record_outcome(self.store, row))
        corrected = record_outcome(self.store, self.event(b, summary='Correction: not completed.', supersedes=first['outcome'], event_type='correction'))
        self.assertNotEqual(first['outcome'], corrected['outcome']); self.assertEqual(before, self.store.snapshot())
        with self.assertRaises(EvidenceError): propose_from_outcome(self.store, first['outcome'], ['Evaluation'])
        self.assertNotIn('research-profile', self.store.status()['counts'])

    def test_observation_and_test_scoping_fail_closed(self):
        b = self.make_brief()
        with self.assertRaises(EvidenceError): record_outcome(self.store, self.event(b, basis='observed'))
        ctx = self.context()
        with self.assertRaises(EvidenceError): record_outcome(self.store, self.event(b, basis='observed', event_type='test', evidence=[ctx], conditions=['production']))

    def test_test_outcome_proposes_only_scoped_capability_and_reject_changes_nothing(self):
        b = self.make_brief(); data = context_bundle('experiment-result')
        data['records'][0].update(observation_basis='reproduced', revision='a' * 40, conditions=['Owned held-out fixture, revision a, command test, exit 0.'])
        ctx = import_context(self.store, data)['contexts'][0]
        row = self.event(b, basis='observed', event_type='held-out-evaluation', evidence=[ctx],
                         conditions=data['records'][0]['conditions'], capabilities=['evaluation'],
                         tests=[{'context': ctx, 'command': 'python -m unittest owned_fixture', 'revision': 'a' * 40,
                                 'exit_code': 0, 'result_quote': data['records'][0]['content'],
                                 'held_out': 'Owned held-out fixture only; no production or general benchmark claim.'}])
        outcome = record_outcome(self.store, row)['outcome']
        proposal = propose_from_outcome(self.store, outcome, ['Evaluation'])['proposal']
        with self.store.transaction() as state:
            caps = state['artifacts'][proposal]['payload']['capabilities']
            self.assertEqual([c['capability'] for c in caps], ['evaluation'])
            self.assertEqual(caps[0]['conditions'], row['conditions'])
        review(self.store, proposal, 'reject', 'fixture')
        self.assertNotIn('research-profile', self.store.status()['counts'])
        self.store.withdraw(outcome)
        with self.store.transaction() as state: self.assertNotIn(proposal, state['artifacts'])

    def test_source_withdrawal_cascades_to_events(self):
        b = self.make_brief(); result = record_outcome(self.store, self.event(b))
        self.store.withdraw(self.obs)
        with self.store.transaction() as state: self.assertNotIn(result['outcome'], state['artifacts'])

    def test_export_forbidden_by_default_and_expiry(self):
        b = self.make_brief()
        with self.assertRaises(EvidenceError): preview(self.store, self.request(b))
        p = export_policy(); p['use_until'] = (self.now + timedelta(days=1)).isoformat()
        from tools.research_evidence import validate_policy
        with self.assertRaises(EvidenceError): validate_policy(p, self.now)

    def test_exact_preview_review_and_private_fields_excluded(self):
        self.enable_owned_exports(); b = self.make_brief()
        event = record_outcome(self.store, self.event(b, policy=export_policy()))['outcome']
        p = preview(self.store, self.request(event)); raw = json.dumps(p['bundle'])
        self.assertNotIn('private observer canary', raw); self.assertNotIn('raw_description', raw)
        self.assertNotIn('profile_evidence', raw); self.assertNotIn('Owned fixture lesson', raw)
        with self.assertRaises(EvidenceError): release(self.store, p['preview'], 'wrong', 'fixture')
        self.assertEqual(release(self.store, p['preview'], p['review_digest'], 'fixture'), p['bundle'])
        self.store.withdraw(self.obs)
        with self.assertRaises(EvidenceError): release(self.store, p['preview'], p['review_digest'], 'fixture')

    def test_roundtrip_idempotence_and_echo_not_corroboration(self):
        self.enable_owned_exports(); b = self.make_brief(); before = self.store.snapshot()
        p = preview(self.store, self.request(b)); remote = Store(Path(self.temp.name) / 'remote', clock=lambda: self.now)
        first = import_interchange(remote, p['bundle'], export_policy())
        self.assertEqual(first, import_interchange(remote, p['bundle'], export_policy()))
        self.assertNotIn('observation', remote.status()['counts']); self.assertNotIn('context', remote.status()['counts'])
        again = preview(remote, self.request(first['imports'][0]))
        local = import_interchange(self.store, again['bundle'], export_policy())
        self.assertEqual(self.store.snapshot(), before)
        self.assertEqual(local, import_interchange(self.store, again['bundle'], export_policy()))
        self.store.withdraw(self.obs)
        with self.assertRaises(EvidenceError): import_interchange(self.store, again['bundle'], export_policy())
        with self.store.transaction() as state: self.assertNotIn(local['imports'][0], state['artifacts'])

    def test_unknown_version_companion_or_private_field_rejected(self):
        self.enable_owned_exports(); p = preview(self.store, self.request(self.make_brief()))
        for change in ('version', 'markdown', 'private'):
            bad = deepcopy(p['bundle'])
            if change == 'version': bad['schema'] = 'radar-interchange/2.0'
            if change == 'markdown': bad['markdown'] += '<script>attack</script>'
            if change == 'private': bad['items'][0]['content']['credentials'] = 'secret'
            with self.assertRaises(EvidenceError): import_interchange(self.store, bad, export_policy())

    def test_import_withdrawal_blocks_old_and_rewrapped_copies(self):
        self.enable_owned_exports(); p = preview(self.store, self.request(self.make_brief()))
        remote = Store(Path(self.temp.name) / 'remote', clock=lambda: self.now)
        key = import_interchange(remote, p['bundle'], export_policy())['imports'][0]
        remote.withdraw(key)
        with self.assertRaises(EvidenceError): import_interchange(remote, p['bundle'], export_policy())
        bad = deepcopy(p['bundle']); bad['items'][0]['origin']['revision'] = 'changed'
        bad['markdown'] = markdown(bad)
        with self.assertRaises(EvidenceError): import_interchange(remote, bad, export_policy())

    def test_echo_withdrawal_does_not_corrupt_local_manifest(self):
        self.enable_owned_exports(); b = self.make_brief(); p = preview(self.store, self.request(b))
        key = import_interchange(self.store, p['bundle'], export_policy())['imports'][0]
        self.store.withdraw(key)
        with self.store.transaction() as state:
            self.assertNotIn(b, state['artifacts'])
            self.assertFalse(set(state['artifacts']) & set(state['withdrawn']))

    def test_export_rejects_profile_lineage_and_uninspected_excerpts(self):
        self.enable_owned_exports(); b = self.make_brief()
        req = self.request(b); req[0]['excerpts'] = [{'context': 'missing', 'quote': 'Invented'}]
        with self.assertRaises(EvidenceError): preview(self.store, req)
        from tools.research_profile import propose
        prop = propose(self.store, {'schema_version': 1, 'policy': export_policy(), 'direction': ['Private direction'], 'capabilities': [], 'supersedes': None})['proposal']
        profile = review(self.store, prop, 'accept', 'fixture')['profile']
        self.output = self.output_for('learning'); personalized = self.brief(profile=profile)['brief']
        with self.assertRaises(EvidenceError): preview(self.store, self.request(personalized))


    def test_corrected_outcome_retracts_profile_and_keeps_history(self):
        b = self.make_brief(); data = context_bundle('experiment-result')
        data['records'][0].update(observation_basis='reproduced', revision='a' * 40, conditions=['owned fixture'])
        ctx = import_context(self.store, data)['contexts'][0]
        row = self.event(b, basis='observed', event_type='test', evidence=[ctx], conditions=['owned fixture'],
                        capabilities=['evaluation'], tests=[{'context': ctx, 'command': 'owned-test', 'revision': 'a' * 40,
                        'exit_code': 0, 'result_quote': data['records'][0]['content'], 'held_out': 'Owned inputs only.'}])
        out = record_outcome(self.store, row)['outcome']
        prop = propose_from_outcome(self.store, out, ['Evaluate'])['proposal']
        profile = review(self.store, prop, 'accept', 'fixture')['profile']
        corrected = record_outcome(self.store, self.event(b, event_type='correction', supersedes=out))['outcome']
        with self.store.transaction() as state:
            self.assertNotIn(profile, state['artifacts']); self.assertNotIn(prop, state['artifacts'])
            self.assertIn(out, state['artifacts']); self.assertIn(corrected, state['artifacts'])
        with self.assertRaises(EvidenceError): propose_from_outcome(self.store, out, ['Evaluate'])

    def test_outcome_memory_enters_next_generation_with_basis_and_no_count_change(self):
        b = self.make_brief(); before = self.store.snapshot()
        event = record_outcome(self.store, self.event(b))['outcome']
        captured = []
        class Capture(self.worker):
            def run(self, prompt, schema):
                captured.append(json.loads(prompt.split('Untrusted evidence JSON:\n')[1]))
                return super().run(prompt, schema)
        result = generate(self.store, 'learning', self.snapshot, worker_factory=Capture)
        self.assertEqual(captured[0]['outcome_memory'][0]['basis'], 'user-reported')
        self.assertEqual(captured[0]['outcome_memory'][0]['id'], event)
        self.assertNotIn('observer', captured[0]['outcome_memory'][0])
        self.assertEqual(self.store.snapshot(), before)
        self.store.withdraw(event)
        with self.store.transaction() as state: self.assertNotIn(result['brief'], state['artifacts'])

    def test_imported_assessment_is_optional_synthesis_input_not_primary_evidence(self):
        self.enable_owned_exports(); b = self.make_brief()
        p = preview(self.store, self.request(b)); item = import_interchange(self.store, p['bundle'], export_policy())['imports'][0]
        captured = []
        class Capture(self.worker):
            def run(self, prompt, schema):
                captured.append(json.loads(prompt.split('Untrusted evidence JSON:\n')[1]))
                return super().run(prompt, schema)
        generate(self.store, 'learning', self.snapshot, worker_factory=Capture, exchanges=[item])
        self.assertIn(item, captured[0]['interchange_assessments'])
        self.assertNotIn(item, captured[0]['contexts']); self.assertNotIn(item, captured[0]['analyses'])
        with self.assertRaises(EvidenceError): self.brief(contexts=[item])

    def test_restrictions_cannot_be_stripped_and_conflicting_origin_fails(self):
        self.enable_owned_exports(); p = preview(self.store, self.request(self.make_brief()))
        remote = Store(Path(self.temp.name) / 'remote', clock=lambda: self.now)
        import_interchange(remote, p['bundle'], export_policy())
        bad = deepcopy(p['bundle']); bad['items'][0]['content']['summary'] = 'Changed immutable revision'
        bad['markdown'] = markdown(bad)
        with self.assertRaises(EvidenceError): import_interchange(remote, bad, export_policy())
        bad = deepcopy(p['bundle']); bad['items'][0]['restrictions'] = []
        bad['markdown'] = markdown(bad)
        with self.assertRaises(EvidenceError): import_interchange(remote, bad, export_policy())

    def test_withdrawal_of_echo_preserves_unrelated_ancestors(self):
        self.enable_owned_exports(); b = self.make_brief()
        p = preview(self.store, self.request(b)); item = import_interchange(self.store, p['bundle'], export_policy())['imports'][0]
        self.store.withdraw(item)
        with self.store.transaction() as state:
            self.assertIn(self.obs, state['artifacts']); self.assertNotIn(b, state['artifacts'])


def export_policy():
    p = context_bundle()['policy']
    p.update(export=True, export_permission_reference='Author-owned test data; unlimited copies permitted.', export_retention='no-recall-required')
    return p


if __name__ == '__main__': unittest.main()
