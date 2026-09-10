"""Model output/lifecycle tests use an injected worker, never paid or live inference."""
from copy import deepcopy
from datetime import datetime, timezone, timedelta
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from tools.research_analysis import analyze, normalize_output, qualified
from tools.evaluate_research import evaluate_observation
from tools.research_evidence import EvidenceError, Store
from tools.research_sources import collect_jobicy, html_text
from tests.test_research_evidence import bundle, BODY


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.now = datetime(2026, 9, 9, 12, tzinfo=timezone.utc)
        self.store = Store(Path(self.tmp.name) / "state", clock=lambda: self.now)
        data = bundle()
        data["policy"].update(hosted_disclosure=True, hosted_retention="provider-managed-no-deletion-deadline",
                              hosted_permission_reference="author-owned synthetic fixture")
        self.observation = self.store.import_bundle(data)["observations"][0]
        with self.store.transaction() as state:
            self.qualification = self.store.put(state, "runtime-qualification", {"test_only": True})
        self.patch = patch("tools.research_analysis.qualified", return_value=(self.qualification, {"test_only": True}))
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.calls = 0
        self.output = {"ai_domain": "in-domain", "responsibility_class": "applied", "claims": [
            {"kind": "responsibility", "modality": "unspecified", "quote": "Build retrieval pipelines.",
             "capabilities": ["retrieval-knowledge"], "tools": []}], "unknowns": ["Modality unspecified."]}
        self.on_run = lambda: None
        self.on_enter = lambda: None
        owner = self

        class FakeWorker:
            def __init__(self, *args):
                pass
            def __enter__(self):
                owner.on_enter()
                return self
            def __exit__(self, *args):
                pass
            def run(self, prompt, schema):
                owner.calls += 1
                owner.on_run()
                return deepcopy(owner.output), {"authentication": "synthetic-test", "token_usage": {}}
        self.worker = FakeWorker

    def analyze(self, **kwargs):
        return analyze(self.store, self.observation, worker_factory=self.worker, **kwargs)

    def test_validated_model_path_cache_and_forced_refresh(self):
        first = self.analyze()
        second = self.analyze()
        self.assertTrue(second["cache_hit"])
        self.assertEqual(first["analysis"], second["analysis"])
        self.assertEqual(self.calls, 1)
        self.analyze(refresh=True)
        self.assertEqual(self.calls, 2)

    def test_invalid_quote_or_tool_label_never_commits_analysis(self):
        for mutation in [{"quote": "Invented job requirement"}, {"tools": ["Python"]}]:
            self.output["claims"][0].update(mutation)
            with self.assertRaises(EvidenceError):
                self.analyze()
        self.assertNotIn("analysis", self.store.status()["counts"])
        self.assertIn("execution", self.store.status()["counts"])

    def test_runtime_failure_is_deferred_without_second_call(self):
        def fail():
            raise EvidenceError("quota exhausted")
        self.on_run = fail
        with self.assertRaises(EvidenceError):
            self.analyze()
        self.assertEqual(self.calls, 1)
        self.assertNotIn("analysis", self.store.status()["counts"])

    def test_withdrawal_during_model_run_rejects_result(self):
        self.on_run = lambda: self.store.withdraw(self.observation)
        with self.assertRaises(EvidenceError):
            self.analyze()
        self.assertNotIn("analysis", self.store.status()["counts"])

    def test_local_only_policy_never_reaches_worker(self):
        other = self.store.import_bundle(bundle(native_id="local-only"))["observations"][0]
        with self.assertRaises(EvidenceError):
            analyze(self.store, other, worker_factory=self.worker)
        self.assertEqual(self.calls, 0)

    def test_prompt_change_invalidates_cache(self):
        self.analyze()
        with patch("tools.research_analysis.PROMPT_VERSION", "changed-version"):
            result = self.analyze()
        self.assertFalse(result["cache_hit"])
        self.assertEqual(self.calls, 2)

    def test_exact_unicode_offsets_are_computed_by_code(self):
        output = {"ai_domain": "in-domain", "responsibility_class": "applied", "claims": [{"kind": "skill", "modality": "required",
                  "quote": "Python requis.", "capabilities": [], "tools": ["Python"]}], "unknowns": []}
        normalized = normalize_output(output, "id", "🔎 Python requis.", self.now)
        self.assertEqual(normalized["claims"][0]["start"], 2)

    def test_missing_description_never_calls_model(self):
        data = bundle(native_id="missing")
        data["observations"][0]["description"] = None
        data["policy"].update(hosted_disclosure=True, hosted_retention="provider-managed-no-deletion-deadline",
                              hosted_permission_reference="author-owned test")
        self.observation = self.store.import_bundle(data)["observations"][0]
        self.analyze()
        self.assertEqual(self.calls, 0)

    def test_generic_concepts_are_not_concrete_tools(self):
        output = {"ai_domain": "in-domain", "responsibility_class": "applied", "claims": [
            {"kind": "skill", "modality": "unspecified", "quote": "Use LLMs with Python.",
             "capabilities": ["ai-product-engineering"], "tools": ["LLMs", "Python"]}], "unknowns": []}
        annotation = normalize_output(output, "id", "Use LLMs with Python.", self.now)
        self.assertEqual(annotation["claims"][0]["tools"], ["Python"])
        self.assertEqual(output["claims"][0]["tools"], ["LLMs", "Python"])

    def test_expiry_after_startup_prevents_disclosure(self):
        data = bundle(native_id="expiry")
        data["policy"].update(hosted_disclosure=True, hosted_retention="provider-managed-no-deletion-deadline",
                              hosted_permission_reference="owned", use_until="2026-09-09T12:01:00Z")
        self.observation = self.store.import_bundle(data)["observations"][0]
        self.on_enter = lambda: setattr(self, "now", self.now + timedelta(minutes=2))
        with self.assertRaises(EvidenceError):
            self.analyze()
        self.assertEqual(self.calls, 0)

    def test_adjacent_role_does_not_inflate_ai_capability_count(self):
        self.output["ai_domain"] = "adjacent"
        self.analyze()
        result = self.store.snapshot()
        with self.store.transaction() as state:
            report = state["artifacts"][result["snapshot"]]["payload"]
            self.assertNotIn("retrieval-knowledge", report["capabilities"])
        self.assertEqual(result["counts"]["captured_revisions"], 1)

    def test_modality_counts_deduplicate_repeated_claims(self):
        self.output["claims"] *= 2
        self.analyze()
        result = self.store.snapshot()
        with self.store.transaction() as state:
            report = state["artifacts"][result["snapshot"]]["payload"]
            self.assertEqual(report["capabilities_by_modality"]["unspecified"]["retrieval-knowledge"], 1)
            self.assertEqual(report["capabilities_by_modality"]["required"], {})

    def test_runtime_identity_drift_requires_new_qualification(self):
        with patch("tools.research_analysis.qualification_identity", return_value={"changed": True}):
            with self.store.transaction() as state, self.assertRaises(EvidenceError):
                qualified(state)

    def test_real_comparison_inherits_withdrawal(self):
        with patch("tools.evaluate_research.qualified", return_value=(self.qualification, {})):
            result = evaluate_observation(self.store, self.observation, "simple-prompt", worker_factory=self.worker)
        self.store.withdraw(self.observation)
        with self.store.transaction() as state:
            self.assertNotIn(result["evaluation"], state["artifacts"])

    def test_real_comparison_rejects_mid_run_withdrawal(self):
        self.on_run = lambda: self.store.withdraw(self.observation)
        with patch("tools.evaluate_research.qualified", return_value=(self.qualification, {})), self.assertRaises(EvidenceError):
            evaluate_observation(self.store, self.observation, "simple-prompt", worker_factory=self.worker)


class SourceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.now = datetime(2026, 9, 9, 12, tzinfo=timezone.utc)
        self.store = Store(Path(self.tmp.name) / "state", clock=lambda: self.now)
        self.job = {"id": 1, "url": "https://jobicy.com/jobs/1-fixture", "companyName": "Synthetic fixture",
                    "jobTitle": "ML Engineer", "jobDescription": "<p>Build &amp; test AI.</p><script>bad()</script>",
                    "pubDate": "2026-09-09 09:00:00", "jobGeo": "Anywhere"}
        self.calls = 0

    def fetch(self, query, count):
        self.calls += 1
        return {"jobs": [deepcopy(self.job)]}, "https://jobicy.com/api/v2/remote-jobs?count=20&tag=machine"

    def test_capture_transformation_unknowns_and_scheduled_cooldown(self):
        result = collect_jobicy(self.store, fetch=self.fetch)
        with self.store.transaction() as state:
            row = state["artifacts"][result["observations"][0]]["payload"]
            self.assertEqual(row["description"], "Build & test AI.")
            self.assertEqual(row["raw_description"], self.job["jobDescription"])
            self.assertIsNone(row["posted_at"])
            self.assertIsNone(row["country"])
            self.assertEqual(row["availability"], "unknown")
        with self.assertRaises(EvidenceError):
            collect_jobicy(self.store, scheduled=True, fetch=self.fetch)
        self.assertEqual(self.calls, 1)

    def test_failed_attempt_is_recorded_and_does_not_auto_retry(self):
        def fail(*args):
            self.calls += 1
            raise OSError("unavailable")
        with self.assertRaises(EvidenceError):
            collect_jobicy(self.store, fetch=fail)
        self.assertEqual(self.calls, 1)
        self.assertEqual(self.store.status()["counts"]["receipt"], 1)
        with self.assertRaises(EvidenceError):
            collect_jobicy(self.store, scheduled=True, fetch=fail)
        self.assertEqual(self.calls, 1)

    def test_stale_policy_stops_before_network_or_state(self):
        self.now += timedelta(days=31)
        with self.assertRaises(EvidenceError):
            collect_jobicy(self.store, fetch=self.fetch)
        self.assertEqual(self.calls, 0)
        self.assertFalse(self.store.home.exists())

    def test_unapproved_listing_url_fails_and_records_failed_receipt(self):
        self.job["url"] = "http://localhost/private"
        with self.assertRaises(EvidenceError):
            collect_jobicy(self.store, fetch=self.fetch)
        self.assertNotIn("observation", self.store.status()["counts"])


MANUAL_NOW = datetime(2026, 9, 10, 12, tzinfo=timezone.utc)


class ManualDiscoveryTests(unittest.TestCase):
    def test_manual_queries_do_not_have_one_hour_gate(self):
        from tools.research_sources import ai_query_plan
        with tempfile.TemporaryDirectory() as tmp:
            store=Store(Path(tmp)/'private',clock=lambda: MANUAL_NOW)
            calls=[]
            def fetch(query,count):
                calls.append((query,count))
                return {'jobs':[]}, 'https://jobicy.com/api/v2/remote-jobs'
            collect_jobicy(store,fetch=fetch)
            collect_jobicy(store,fetch=fetch)
            self.assertEqual(calls,[('LLM',100),('AI product',100)])
            with store.transaction() as state:
                plan=ai_query_plan(state,MANUAL_NOW)
                self.assertTrue(plan['manual_ready']);self.assertFalse(plan['scheduled_ready'])
                self.assertEqual(plan['next_query'],'applied AI')
                attempts=[a['payload'] for a in state['artifacts'].values() if a['kind']=='collection-attempt']
                self.assertTrue(all(a['trigger']=='manual' for a in attempts))
            with self.assertRaises(EvidenceError):collect_jobicy(store,scheduled=True,fetch=fetch)
            self.assertEqual(len(calls),2)

    def test_manual_failure_has_no_automatic_retry(self):
        with tempfile.TemporaryDirectory() as tmp:
            store=Store(Path(tmp)/'private',clock=lambda: MANUAL_NOW)
            calls=[]
            def fail(*args):
                calls.append(1);raise OSError('owned failure')
            with self.assertRaises(EvidenceError):collect_jobicy(store,'LLM',fetch=fail)
            self.assertEqual(calls,[1])
            self.assertEqual(store.status()['counts']['receipt'],1)
