# Phase 4 implementation and validation — 2026-09-09

Phase 3 was already committed as `5d8fc8f` when Phase 4 began. Phase 4 was
implemented on `research/phase4` in the same required `ai-job-skills-lab` checkout.
No sibling worktree, dependency installation, new provider collection, personal
profile setup, real feedback fabrication, repository push or publication occurred.
The tests use temporary owned fixtures; the existing private Jobicy policies,
briefs and pending human-review records were not modified.

## Reuse and inspected evidence

- `.claude/commands/outcome.md` at the P3 base: record outcomes separately from
  profile interpretation, preserve archive history, use explicit review and
  idempotent updates. Research uses those semantics through its existing CLI;
  no tracker/application command was altered or duplicated.
- Unchanged `tools/rank_state.py:save_state` and P2 `Store`: same atomic private
  manifest, dependency/expiry sweep and logical withdrawal. P4 extends policy
  validation additively for explicitly permitted no-recall projections. Default
  false export policies remain blocked. General state export/restore is unchanged.
- P3 `research_context.py` native schema-3.0 Radar conversion, `research_profile.py`
  validators and `research_briefs.py` qualified synthesis. No second collector,
  database, runtime or command/specification tree was introduced.
- Read-only Git-object inspection in the separate `youtube-trend-radar` reference,
  pinned at `fc96d4865ced43f9098a9272e865e96ee603ae3f`:
  `src/ai_trend_radar/feedback.py` and `src/ai_trend_radar/topic_state.py`.
  These establish explicit feedback separated from precision/ranking claims,
  latest judgment per revision, deferred decisions and source-content revision
  patterns. P3 previously inspected `developer_reports.py` at the same revision.
  No Radar database, private config or actual report was read; no code imported,
  tests executed in that repository, or producer compatibility result invented.

## Implemented acceptance coverage

`tests/test_research_outcomes.py` adds 22 behavioral integration tests using
private temporary stores and injected model responses:

- Decision idempotence, explicit supersession and stale-update refusal; separate
  accepted/rejected/deferred/duplicate semantics and dated deferral checks.
- Rejection blocks refresh/metadata changes; changed inspected evidence needs
  explicit reconsideration; rewrapped same content is not material evidence.
- Feedback changes during generation prevent stale output commit. Outcome basis,
  chosen work and conditions enter the next generation without altering counts.
- Self-report cannot establish observation. Recorded test commands/revisions,
  exact result quotes and conditions constrain scoped profile proposals; rejecting
  them leaves the profile unchanged. Corrections retract previously accepted
  derived profiles while keeping immutable event history.
- Source withdrawal invalidates outcome/brief derivatives; withdrawal of an echo
  removes its original/derived copies without deleting unrelated ancestors.
- Default forbidden export and incompatible expiry fail closed. Exact preview
  digest/review and current lineage are required for release; projection excludes
  private observer/internal fields and rejects profile lineage or unknown quotes.
- Neutral round trips are idempotent; unknown schema versions, differing Markdown,
  extra private fields, conflicting immutable origins and removed restrictions
  fail. Echoes remain imported assessments, add no observations, and cannot enter
  the primary context/analysis maps. Old/rewrapped withdrawn bundles are rejected.

Validation commands run from the required checkout with the existing `.venv`
and ignored Bun directory on PATH:

```sh
python3 -m unittest discover -s tests -t .
python3 -m tools.research_decisions --help
python3 tools/research_preflight.py --mode research --action outcome
```

The full Python run executed **524 tests: 523 passed, one opt-in live runtime test
skipped**. CLI help exposed the new routes; read-only outcome readiness passed
without initializing state. The pinned extraction worker/config/qualification
mechanism was unchanged, so its previously recorded active test was not rerun.
No additional hosted inference was required for these deterministic features.
A changed brief prompt/validator is versioned in future executions; these tests
are not a live semantic evaluation of that new prompt.

## Acceptance limits and remaining evidence

The implementation supplies review controls; it does not supply real user
judgments. P2 extraction adjudication and P3 usefulness review remain pending.
No completed project, customer validation, publication, profile capability,
human score or improvement in model quality was asserted by fixture setup.

P4 has no real-source exchange result: the current Jobicy corpus has export false
and a use-until limit. Real interchange requires genuinely compatible permission,
an exact reviewed projection and a participating consumer; changes to AI Trend
Radar remain a separate repository task. Unknown/deletion-bound sources do not
block local decisions or independent P5 work.

Reviewer/observer identities and interpretation of test scope are assertions;
exact quotes/revisions and explicit controls do not authenticate them. Capability
suppression is conservative, not semantic duplicate detection. Export allowlists
do not classify arbitrary private prose, so exact content review remains required.
Known tombstones protect participating stores; disconnected recipients, hostile
provenance forgery, a new store without withdrawal history, physical deletion and
backup recovery are not solved by this interchange contract. Only sources without
those downstream obligations qualify. P6 retains scheduling/monitoring/recovery.

## PR readiness result

The required deterministic PR Ready analyzer returned **PR READY** against
`5d8fc8f`: full tests passed (524 run, one opt-in skip), skill lint passed,
security guards passed, and no suspicious files/blockers were detected. Build
was skipped because no build check is configured. The local full output is in
ignored `.tools/validation/phase4-pr-ready.md`. Phase 4 changes are staged,
uncommitted and unpushed; Phase 3's existing commit is unchanged.
