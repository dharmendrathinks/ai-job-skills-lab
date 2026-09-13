"""Behavioral P6 cases with owned fixtures; no actual schedule or external send."""
from copy import deepcopy
from datetime import timedelta
import json
import multiprocessing
import os
from pathlib import Path
import plistlib
import tempfile
import unittest
from unittest.mock import patch

from tools.research_evidence import Store, EvidenceError, digest
from tools.research_operations import (configure, execute, run_lock, ledger, save_ledger,
                                       inbox, report, tick, health, launchd)
from tools.research_recovery import backup, restore, journal
from tools.research_delivery import preview_notification, approve_notification, send_notification, destination
from tools.research_model_eval import evaluate_local, unattended_eligible, authorize_unattended
from tools.research_outcomes import decide
from tests.test_research_evidence import bundle, annotation, NOW
from tests.test_research_outcomes import export_policy


def held_lock(home, ready, release):
    with run_lock(Store(home, clock=lambda: NOW)):
        ready.set(); release.wait(5)


class OperationsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name) / 'private'
        self.now = NOW
        self.store = Store(self.home, clock=lambda: self.now)
        self.obs = self.store.import_bundle(bundle())['observations'][0]
        self.analysis = self.store.annotate(annotation(self.obs))['analysis']
        self.snap = self.store.snapshot()['snapshot']

    def plan(self, **kw):
        row = {'schema_version': 1, 'collect': None, 'analyze': False, 'brief_kinds': [],
               'contexts': [], 'profile': None, 'analysis_limit': 2, 'report_limit': 20,
               'backup': False, 'interval_seconds': 3600, 'reviewer': 'owned fixture', **kw}
        return configure(self.store, row)['plan']

    def brief(self, n=1, **kw):
        with self.store.transaction() as state:
            return self.store.put(state, 'brief', {'kind': 'project', 'revision': n,
                'recommendation_id': 'owned-'+str(n), 'evidence_basis': [self.obs], 'revises': None,
                'markdown': '<script>fetch("https://invalid.example")</script> & "quoted"', **kw}, [self.snap])

    def decision(self, brief, defer_until):
        return decide(self.store, {'schema_version': 1, 'brief': brief, 'decision': 'deferred',
                      'reason': 'fixture', 'reviewer': 'fixture', 'decided_at': self.now.isoformat(),
                      'defer_until': defer_until.isoformat(), 'target': None, 'supersedes': None})

    def test_collector_receives_manual_or_scheduled_trigger(self):
        plan=self.plan(collect={'source':'jobicy','query':'AI product','count':100},report_limit=1000)
        with patch('tools.research_sources.collect_jobicy',return_value={}) as collect:
            execute(self.store,plan)
            self.assertFalse(collect.call_args.kwargs['scheduled'])
            execute(self.store,plan,scheduled=True)
            self.assertTrue(collect.call_args.kwargs['scheduled'])
            self.assertEqual(collect.call_count,2)

    def test_inbox_acknowledgment_overflow_not_render_acceptance(self):
        self.brief(1); self.brief(2); self.brief(3)
        first = inbox(self.store, 1)
        self.assertEqual(first['overflow'], 2)
        report(self.store, 1)
        self.assertEqual(first, inbox(self.store, 1))
        shown = inbox(self.store, 1, acknowledge=True)
        self.assertEqual(first['items'], shown['items'])
        after = inbox(self.store, 1)
        self.assertEqual(after['overflow'], 1)
        self.assertNotEqual(first['items'][0]['brief'], after['items'][0]['brief'])
        self.assertNotIn('decision', self.store.status()['counts'])

    def test_deferred_due_and_revision_presentation(self):
        old = self.brief()
        self.decision(old, self.now + timedelta(days=1))
        self.assertEqual(inbox(self.store)['deferred'], 1)
        self.assertEqual(inbox(self.store)['items'], [])
        self.now += timedelta(days=2)
        self.assertEqual(inbox(self.store, acknowledge=True)['items'][0]['status'], 'due')
        self.assertFalse(inbox(self.store)['items'])
        new = self.brief(2, revises=old)
        self.assertEqual([r['brief'] for r in inbox(self.store)['items']], [new])

    def test_html_escape_no_active_links_script_or_unmanaged_assets(self):
        self.brief(); result = report(self.store)
        html = Path(result['path']).read_text()
        self.assertEqual(html.count('<script>'), 1)  # fixed hash-authorized UI script only
        self.assertIn('&lt;script&gt;', html)
        self.assertIn('default-src', html)
        from html.parser import HTMLParser
        from tools.research_curricula import library
        class Links(HTMLParser):
            def __init__(self): super().__init__(); self.links=[]
            def handle_starttag(self, tag, attrs):
                if tag == 'a': self.links.append(dict(attrs).get('href',''))
        links=Links(); links.feed(html)
        resources={r['url'] for r in library()['resources'].values()}
        self.assertTrue(all(href in {'jobs.html','workspace.html'} or href.startswith('#') or href in resources
                            for href in links.links))  # only reviewed curriculum URLs and internal navigation
        self.assertTrue(any(href in resources for href in links.links))
        self.assertNotIn('<img', html)
        self.assertIn('Captured evidence', html)
        self.assertEqual(os.stat(result['path']).st_mode & 0o777, 0o600)
        # Latest view is singular, even with frozen-clock repeated renders.
        report(self.store); report(self.store)
        self.assertEqual(self.store.status()['counts']['offline-report'], 1)

    def test_withdrawal_removes_managed_backups_html_and_derived_artifacts(self):
        b = self.brief(); report(self.store); inbox(self.store, acknowledge=True); backup(self.store)
        self.assertTrue((self.home/'backup.json').exists())
        self.store.withdraw(self.obs)
        self.assertFalse((self.home/'backup.json').exists())
        self.assertFalse((self.home/'workspace.html').exists())
        with self.store.transaction() as state:
            self.assertNotIn(b, state['artifacts'])
            self.assertNotIn('presentation', {a['kind'] for a in state['artifacts'].values()})
        with self.assertRaises((ValueError, OSError)): restore(self.store)

    def test_expiry_cleans_backups_view_and_records_on_next_operation(self):
        data = bundle('expiring'); data['policy']['use_until'] = (self.now+timedelta(hours=1)).isoformat()
        # New store prevents owned equal-body removal from confusing the assertion.
        self.store = Store(Path(self.temp.name)/'expires', clock=lambda: self.now)
        self.obs = self.store.import_bundle(data)['observations'][0]
        self.snap = self.store.snapshot()['snapshot']; self.brief(); report(self.store); backup(self.store)
        self.now += timedelta(hours=2)
        self.assertEqual(health(self.store)['counts'], {})
        self.assertFalse((self.store.home/'backup.json').exists())
        self.assertFalse((self.store.home/'workspace.html').exists())

    def test_restore_corrupt_primary_and_no_restore_without_journal(self):
        backup(self.store)
        (self.home/'research-state.json').write_text('{corrupt')
        self.assertEqual(health(self.store)['status'], 'failed')
        self.assertGreater(restore(self.store)['restored_artifacts'], 0)
        self.assertEqual(self.store.status()['counts']['observation'], 1)
        (self.home/'withdrawals.json').unlink()
        with self.assertRaises(ValueError): restore(self.store)
        with self.assertRaises(ValueError): self.store.status()

    def test_crash_after_journal_write_cannot_restore_old_backup(self):
        backup(self.store)
        from tools.rank_state import save_state as original
        def fail_primary(path, data):
            if Path(path).name == 'research-state.json' and self.obs in data['withdrawn']:
                raise OSError('simulated disk failure')
            original(path, data)
        with patch('tools.research_recovery.save_state', side_effect=fail_primary):
            with self.assertRaises(OSError): self.store.withdraw(self.obs)
        self.assertIn(self.obs, journal(self.store)['withdrawn'])
        self.assertNotIn('observation', self.store.status()['counts'])
        with self.assertRaises((ValueError, OSError)): restore(self.store)

    def test_old_backup_reintroduced_rejected_by_monotone_journal(self):
        backup(self.store); old = (self.home/'backup.json').read_bytes()
        self.store.withdraw(self.obs)
        (self.home/'backup.json').write_bytes(old); (self.home/'backup.json').chmod(0o600)
        with self.assertRaises(ValueError): restore(self.store)
        self.store.status()
        self.assertFalse((self.home/'backup.json').exists())

    def test_managed_copy_symlinks_fail_closed(self):
        other = Path(self.temp.name)/'public'; other.write_text('unchanged')
        (self.home/'backup.json').symlink_to(other)
        with self.assertRaises(ValueError): backup(self.store)
        self.assertEqual(other.read_text(), 'unchanged')

    def test_resume_does_not_repeat_completed_or_ambiguous_work(self):
        p = self.plan(collect={'source': 'jobicy', 'query': 'owned', 'count': 1})
        calls = []
        def crash():
            calls.append(1); raise KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt):
            execute(self.store, p, _handlers={'collect': crash})
        log = ledger(self.store); key = next(iter(log['runs']))
        resumed = execute(self.store, p, resume=key, _handlers={'collect': lambda: calls.append(2)})
        self.assertEqual(calls, [1]); self.assertEqual(resumed['status'], 'needs-review')
        self.assertEqual(resumed['steps']['collect']['status'], 'ambiguous')
        self.assertEqual(resumed['steps']['report']['status'], 'done')

    def test_overlap_prevented_between_processes(self):
        ready, release = multiprocessing.Event(), multiprocessing.Event()
        process = multiprocessing.Process(target=held_lock, args=(str(self.home), ready, release)); process.start()
        try:
            self.assertTrue(ready.wait(5))
            with self.assertRaises(ValueError): execute(self.store, self.plan())
            with self.assertRaises(ValueError): restore(self.store)
        finally:
            release.set(); process.join(5)
        self.assertEqual(process.exitcode, 0)

    def test_tick_coalesces_missed_slots_no_replay_or_backdated_collection(self):
        p = self.plan()
        self.assertEqual(tick(self.store, p)['status'], 'complete')
        self.assertEqual(tick(self.store, p)['status'], 'not-due')
        self.now += timedelta(hours=5)
        second = tick(self.store, p)
        self.assertEqual(second['missed_slots'], 4)
        self.assertEqual(len(ledger(self.store)['runs']), 2)
        self.assertEqual(self.store.status()['counts']['observation'], 1)

    def test_unqualified_scheduled_models_never_invoke_worker(self):
        p = self.plan(analyze=True)
        with patch('tools.research_analysis.analyze') as model:
            result = tick(self.store, p)
        model.assert_not_called()
        self.assertEqual(result['model_gate'], 'requires-unattended-qualification')
        self.assertEqual(result['steps']['report']['status'], 'done')
        self.assertEqual(ledger(self.store)['health'][-1]['status'], 'blocked')
        self.assertEqual(tick(self.store, p)['status'], 'not-due')

    def test_launchd_uses_absolute_paths_and_does_not_install(self):
        p = self.plan(); row = plistlib.loads(launchd(self.store, p).encode())
        self.assertTrue(Path(row['ProgramArguments'][0]).is_absolute())
        self.assertEqual(row['ProgramArguments'][1:4], ['-m', 'tools.research_ops', 'tick'])
        self.assertEqual(row['EnvironmentVariables']['AI_JOB_SKILLS_LAB_HOME'], str(self.home))
        self.assertEqual(row['StandardOutPath'], '/dev/null')
        self.assertNotIn('OPENAI_API_KEY', row['EnvironmentVariables'])
        self.assertNotIn('KeepAlive', row)

    def test_analysis_overflow_incremental_and_quota_stops_model_batch(self):
        p = self.plan(analyze=True, analysis_limit=1)
        for n in range(3):
            self.store.import_bundle(bundle(source='fixture-'+str(n), native_id=str(n)))
        calls = []
        def analyze(store, key):
            calls.append(key); return store.annotate(annotation(key))
        with patch('tools.research_analysis.analyze', side_effect=analyze):
            first = execute(self.store, p); second = execute(self.store, p)
        self.assertEqual(first['overflow'], 2); self.assertEqual(second['overflow'], 1)
        self.assertEqual(len(set(calls)), 2)
        p = self.plan(analyze=True, analysis_limit=20, brief_kinds=['learning', 'project'])
        with patch('tools.research_analysis.analyze', side_effect=ValueError('quota')) as worker, patch('tools.research_briefs.generate') as briefs:
            result = execute(self.store, p)
            again = execute(self.store, p)
        self.assertEqual(worker.call_count, 1)
        briefs.assert_not_called()
        # A previous unresolved model failure must not become a paid fallback.
        self.assertEqual(result['status'], 'needs-review')
        self.assertNotIn('paid', json.dumps(result))

    def test_source_failure_does_not_block_local_reporting(self):
        p = self.plan(collect={'source': 'jobicy', 'query': 'owned', 'count': 1})
        result = execute(self.store, p, _handlers={'collect': lambda: (_ for _ in ()).throw(ValueError('blocked'))})
        self.assertEqual(result['steps']['report']['status'], 'done')
        self.assertEqual(result['steps']['snapshot']['status'], 'done')

    def test_reviewed_retry_resumes_only_selected_step(self):
        from tools.research_operations import resolve_step
        p = self.plan(collect={'source': 'jobicy', 'query': 'owned', 'count': 1})
        first = execute(self.store, p, _handlers={'collect': lambda: (_ for _ in ()).throw(OSError('fixture'))})
        resolve_step(self.store, first['run'], 'collect', 'retry', 'fixture', 'Inspected failed request; owned retry allowed.')
        calls = []
        second = execute(self.store, p, resume=first['run'], _handlers={'collect': lambda: calls.append(1) or {}})
        self.assertEqual(calls, [1]); self.assertEqual(second['status'], 'complete')

    def test_overflow_brief_withdrawal_invalidates_derived_count(self):
        one, two = self.brief(1), self.brief(2)
        report(self.store, 1)
        self.store.withdraw(max(one, two))
        self.assertFalse((self.home/'workspace.html').exists())

    def test_cleanup_failure_is_recorded_without_source_or_exception_text(self):
        p = self.plan()
        with patch.object(self.store, 'status', side_effect=OSError('source-secret')):
            result = execute(self.store, p)
        self.assertEqual(result['steps']['cleanup']['status'], 'deferred')
        self.assertEqual(ledger(self.store)['health'][-1]['status'], 'blocked')
        self.assertNotIn('source-secret', (self.home/'operations.json').read_text())

    def test_corrupt_backup_and_orphan_view_never_restored(self):
        backup(self.store)
        row = json.loads((self.home/'backup.json').read_text())
        row['state']['artifacts'][self.obs]['payload']['description'] = 'tampered'
        (self.home/'backup.json').write_text(json.dumps(row))
        with self.assertRaises(ValueError): restore(self.store)
        orphan = self.home/'.research-view.interrupted'; orphan.write_text('old text')
        self.store.status(); self.assertFalse(orphan.exists())

    def test_scheduler_after_crash_preserves_consumed_slot_and_missed_count(self):
        p = self.plan()
        with patch('tools.research_operations._execute', side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt): tick(self.store, p)
        self.assertEqual(tick(self.store, p)['status'], 'not-due')
        self.assertEqual(ledger(self.store)['slots'][p]['status'], 'running')
        self.now += timedelta(hours=2)
        self.assertEqual(tick(self.store, p)['missed_slots'], 1)

    def test_changed_extraction_contract_becomes_pending(self):
        with self.store.transaction() as state:
            state['artifacts'].pop(self.analysis)
            # Remove snapshot which referenced the old label before replacing fixture label.
            state['artifacts'].pop(self.snap)
            ex = self.store.put(state, 'execution', {'versions': {'prompt_sha256': 'old'},
                   'status': 'validated', 'input_revision': self.obs}, [self.obs])
            self.store.put(state, 'analysis', {'observation': self.obs, 'method': 'codex-extraction', 'execution': ex}, [ex])
        with patch('tools.research_analysis.analyze', return_value={}) as call:
            result = execute(self.store, self.plan(analyze=True))
        call.assert_called_once_with(self.store, self.obs)

    def test_unattended_expiry_and_drift_defer_models_keep_local_operations(self):
        import shutil
        import sys
        from tools import research_model_eval as model_eval
        with self.store.transaction() as state:
            probe = self.store.put(state, 'unattended-probe', {'metadata': {'status': 'passed'},
                   'identity': {'fixture': True}, 'harness_sha256': digest(Path(model_eval.__file__).read_text()),
                   'executable': str(Path(sys.executable).absolute()), 'codex_path': shutil.which('codex')})
        with patch('tools.research_model_eval.qualification_identity', return_value={'fixture': True}), patch('tools.research_model_eval.qualified'):
            q = authorize_unattended(self.store, probe, 'fixture', 'Owned test assertion only')['qualification']
            p = self.plan(analyze=True, unattended_qualification=q)
            first = tick(self.store, p)
            self.assertEqual(first['model_gate'], 'open')
            self.now += timedelta(days=8)
            expired = tick(self.store, p)
            self.assertEqual(expired['model_gate'], 'requires-unattended-qualification')
            self.assertEqual(expired['steps']['report']['status'], 'done')
            with self.store.transaction() as state:
                self.assertIn(p, state['artifacts']); self.assertNotIn(q, state['artifacts'])


class DeliveryTests(unittest.TestCase):
    brief = OperationsTests.brief
    # Separate methods below use their own explicit export permission on owned data.
    def setUp(self):
        OperationsTests.setUp(self)
        self.webhook = 'https://hooks.slack.com/services/Tfixture/Bfixture/owned'
        self.store = Store(Path(self.temp.name)/'export', clock=lambda: self.now)
        data = bundle(); data['policy'] = export_policy()
        self.obs = self.store.import_bundle(data)['observations'][0]
        self.snap = self.store.snapshot()['snapshot']

    def test_exact_content_destination_approval_before_send(self):
        self.brief(); p = preview_notification(self.store, self.webhook)
        calls = []
        with self.assertRaises(ValueError): send_notification(self.store, p['preview'], self.webhook, transport=lambda *a: calls.append(a))
        with self.assertRaises(ValueError): approve_notification(self.store, p['preview'], 'bad', self.webhook, 'fixture')
        a = approve_notification(self.store, p['preview'], p['review_digest'], self.webhook, 'fixture')['approval']
        with self.assertRaises(ValueError): send_notification(self.store, a, self.webhook+'different', transport=lambda *a: calls.append(a))
        self.assertFalse(calls)
        self.assertEqual(send_notification(self.store, a, self.webhook, transport=lambda *a: calls.append(a))['status'], 'sent')
        self.assertEqual(len(calls), 1)
        with self.assertRaises(ValueError): preview_notification(self.store, self.webhook)
        with self.assertRaises(ValueError): send_notification(self.store, a, self.webhook, transport=lambda *a: calls.append(a))
        self.assertEqual(len(calls), 1)

    def test_ambiguous_delivery_not_retried_even_new_preview(self):
        self.brief(); p = preview_notification(self.store, self.webhook)
        a = approve_notification(self.store, p['preview'], p['review_digest'], self.webhook, 'fixture')['approval']
        with self.assertRaisesRegex(ValueError, 'unconfirmed'):
            send_notification(self.store, a, self.webhook, transport=lambda *a: (_ for _ in ()).throw(OSError('secret')))
        self.assertNotIn('secret', (self.store.home/'operations.json').read_text())
        with self.assertRaises(ValueError): preview_notification(self.store, self.webhook)

    def test_withdrawal_invalidates_approval_and_no_send(self):
        self.brief(); p = preview_notification(self.store, self.webhook)
        a = approve_notification(self.store, p['preview'], p['review_digest'], self.webhook, 'fixture')['approval']
        self.store.withdraw(self.obs)
        calls = []
        with self.assertRaises(ValueError): send_notification(self.store, a, self.webhook, transport=lambda *a: calls.append(a))
        self.assertFalse(calls)

    def test_notification_overflow_preserves_unshown(self):
        self.brief(1); self.brief(2)
        p = preview_notification(self.store, self.webhook, 1)
        self.assertEqual(p['overflow'], 1)
        a = approve_notification(self.store, p['preview'], p['review_digest'], self.webhook, 'fixture')['approval']
        send_notification(self.store, a, self.webhook, transport=lambda *a: None)
        second = preview_notification(self.store, self.webhook)
        self.assertFalse(set(second['items']) & set(p['items']))
        self.assertEqual(second['overflow'], 0)

    def test_lost_delivery_ledger_cannot_reset_sent_identity(self):
        self.brief(); p = preview_notification(self.store, self.webhook)
        a = approve_notification(self.store, p['preview'], p['review_digest'], self.webhook, 'fixture')['approval']
        send_notification(self.store, a, self.webhook, transport=lambda *args: None)
        (self.store.home/'operations.json').unlink()
        with self.assertRaisesRegex(ValueError, 'ledger lost'):
            preview_notification(self.store, self.webhook)
        with self.assertRaisesRegex(ValueError, 'ledger lost'):
            send_notification(self.store, a, self.webhook, transport=lambda *args: self.fail('replayed send'))

    def test_source_export_policy_and_destination_validation(self):
        self.store = Store(self.home, clock=lambda: self.now)
        self.snap = self.store.snapshot()['snapshot']; self.brief()
        with self.assertRaises(ValueError): preview_notification(self.store, self.webhook)
        for value in ('http://hooks.slack.com/services/a/b/c', 'https://example.com/', self.webhook+'?token=secret'):
            with self.assertRaises(ValueError): destination(value)


class ModelEvaluationTests(unittest.TestCase):
    def test_local_requires_installed_model_no_download(self):
        with tempfile.TemporaryDirectory() as home:
            with self.assertRaises(ValueError): evaluate_local(Store(home), 'missing', request=lambda path: {'models': []})

    def test_runtime_qualification_cannot_be_replaced_with_boolean(self):
        with tempfile.TemporaryDirectory() as home:
            with self.assertRaises(ValueError): unattended_eligible({'artifacts': {}}, True, Store(home))
            with self.assertRaises(ValueError): authorize_unattended(Store(home), 'missing', 'fixture', 'fixture')


    def test_local_harness_uses_one_validation_timestamp_and_real_validator(self):
        from tools.research_model_eval import DATASET
        dataset = {'examples': [{'id': 'owned-case', 'description': None, 'expected_atoms': [],
                                 'expected_class': 'unknown', 'expected_domain': 'unknown'}]}
        def request(path, body=None):
            if path in ('tags', 'ps'):
                return {'models': [{'name': 'owned-model', 'digest': 'fixture'}]}
            if path == 'version': return {'version': 'fixture'}
            return {'done': True, 'response': json.dumps({'ai_domain': 'unknown', 'responsibility_class': 'unknown',
                                                        'claims': [], 'unknowns': ['No description.']})}
        with tempfile.TemporaryDirectory() as home:
            original = Path.read_text
            def reader(path, *args, **kw):
                return json.dumps(dataset) if path == DATASET else original(path, *args, **kw)
            with patch.object(Path, 'read_text', reader):
                result = evaluate_local(Store(home), 'owned-model', request=request)
        self.assertEqual(result['valid'], 1)


class JourneyTests(unittest.TestCase):
    from tests.test_research_decisions import DecisionTests as Fixtures
    setUp = Fixtures.setUp
    output_for = Fixtures.output_for
    plan = OperationsTests.plan

    def test_runner_integrates_four_validated_briefs_cache_inbox_and_feedback(self):
        from tools.research_briefs import generate as original, SECTIONS
        def generate(store, kind, snapshot, contexts, profile):
            self.output = self.output_for(kind)
            return original(store, kind, snapshot, contexts, profile, worker_factory=self.worker)
        plan = self.plan(brief_kinds=list(SECTIONS))
        with patch('tools.research_briefs.generate', side_effect=generate):
            first = execute(self.store, plan)
            self.assertEqual(first['status'], 'complete')
            self.assertEqual(self.calls, 4)
            execute(self.store, plan)
            self.assertEqual(self.calls, 4)
        rows = inbox(self.store)['items']; self.assertEqual(len(rows), 4)
        self.assertEqual({r['kind'] for r in rows}, set(SECTIONS))
        decide(self.store, {'schema_version': 1, 'brief': rows[0]['brief'], 'decision': 'accepted',
               'reason': 'Owned fixture choice, not real user feedback.', 'reviewer': 'fixture',
               'decided_at': self.now.isoformat(), 'defer_until': None, 'target': None, 'supersedes': None})
        self.assertEqual(len(inbox(self.store)['items']), 3)
        html = Path(report(self.store)['path']).read_text()
        self.assertIn('Unknown human usefulness', html)
        self.assertNotIn('research-profile', self.store.status()['counts'])
        self.store.withdraw(self.obs)
        self.assertFalse(inbox(self.store)['items'])
        self.assertFalse((self.store.home/'workspace.html').exists())
