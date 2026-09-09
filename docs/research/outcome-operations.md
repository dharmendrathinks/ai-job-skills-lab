# Outcomes, recommendation memory and interchange — Phase 4

Use the existing Python 3.10+ environment, private P2 manifest and canonical
research skill. No model invocation is needed to record/review/import/export
feedback. No application tracker, CV, database, additional subscription or Radar
runtime setup is involved. Recording a project/test command does **not** run it.
These actions do not publish, contact people or write to another repository.

## Local journey and commands

Inspect a managed P3 brief first. Record the user's actual decision and work
observations in reviewed private JSON. Never turn an instruction to implement a
phase into a favorable brief rating, a customer observation or a test result.

```sh
.venv/bin/python -m tools.research_decisions inspect --id BRIEF_ID
.venv/bin/python -m tools.research_decisions decide --input /private/decision.json
.venv/bin/python -m tools.research_decisions outcome --input /private/outcome.json
.venv/bin/python -m tools.research_decisions history --id BRIEF_ID
.venv/bin/python -m tools.research_decisions outcome-profile --id OUTCOME_ID --direction 'Evaluation under the inspected conditions'
.venv/bin/python -m tools.research_decisions profile-review --id PROPOSAL_ID --decision reject --reviewer 'Actual reviewer'
```

Paths and IDs above are placeholders, not files to create inside the checkout.
`history` displays local JSON only and checks current expiry/withdrawal first.
Profile proposals remain pending until an actual explicit `profile-review`.
`--profile PREVIOUS_PROFILE_ID` on `outcome-profile` links a proposed revision.
Rejected reviews make no profile change. Old event/brief revisions stay
addressable while permitted; correcting an outcome retracts its profile
proposals, accepted profiles and derivative briefs while retaining event history.

## Executable contracts

All objects reject unknown fields/versions. Public examples are shapes, not
source permission grants. Policy validation uses the existing SourcePolicy v1.

| Record/action | Required fields and behavior |
|---|---|
| Decision v1 (`decide`) | `schema_version:1`, `brief` immutable artifact ID, `decision` accepted/rejected/deferred/duplicate/superseded, `reason`, `reviewer`, zoned `decided_at`, `defer_until` (future zoned timestamp only for deferred; otherwise null), `target` (same-type other brief for duplicate/superseded; otherwise null), `supersedes` (current decision ID or null on first review). Exact replay is idempotent; concurrent/stale revisions fail. |
| OutcomeEvent v1 (`outcome`) | `schema_version:1`, `brief`, `event_type`, `basis`, `observer`, zoned `occurred_at`, `summary`, `project`, `evidence` context IDs, `capabilities`, `conditions`, nonempty `limitations`, `supersedes` previous outcome or null, `tests` list, `policy`. Event types: project-selected, implementation, test, held-out-evaluation, correction, product-validation, published-experiment, lesson. Bases: observed, user-reported, model-inferred. |
| Project selection | `project` is null except where needed; project-selected requires `{url,revision,action}`. Credential-free HTTPS URL, immutable Git revision, action extend/contribute/new/inspect. The record retains the chosen existing project and revision; it does not clone, execute, publish or prove the stated gap. |
| Test record | Each `tests` entry has `context`, `command`, immutable `revision`, integer `exit_code`, exact `result_quote`, and `held_out` description. The context must be in outcome evidence, its revision must match, and the quote must exist in its captured content. An observed test/evaluation requires reproduced experiment-result contexts, tests, and matching documented `conditions`. A recorded command/exit code remains an inspector assertion; exact quote validation is not independent execution verification. |
| Scoped profile proposal | Only observed test/held-out outcomes with explicitly listed taxonomy capabilities can produce demonstrated-capability proposals. Evidence and conditions are copied exactly; all underlying P3 profile validators apply. README inspection, self-report and imported assessments cannot establish demonstrated capability. Semantic capability/result alignment still needs human review; failures can demonstrate investigation skills only if those specific claims are justified. |
| Reconsideration v1 | `{schema_version:1,brief,evidence:[new_context_ids],reason,reviewer}` via `reconsider --input`. Inspected/reproduced content must differ from the previous brief's content, not just metadata. Submit `brief ... --context NEW_ID --reconsideration RECONSIDERATION_ID` to generate an explicitly linked revision. No automatic interpretation of new text as commercially/materially meaningful; reviewer must explain relevance. |

An OutcomeEvent minimal self-report shape (supply a genuinely reviewed policy):

```json
{
  "schema_version": 1, "brief": "BRIEF_ID", "event_type": "lesson",
  "basis": "user-reported", "observer": "Actual observer",
  "occurred_at": "2026-09-09T12:00:00+00:00",
  "summary": "Describe what actually happened; do not invent completion.",
  "project": null, "evidence": [], "capabilities": [], "conditions": [],
  "limitations": ["Self-report; no implementation or tests inspected."],
  "supersedes": null, "tests": [], "policy": "REPLACE_WITH_REVIEWED_SOURCE_POLICY_OBJECT"
}
```

## Recommendation memory and revisions

Decision and outcome artifacts depend on the exact old brief and relevant source
policies. Future generation receives latest decisions and latest outcome
revisions for that workflow, including reason, basis, selected project, recorded
tests and limits. No market counts or learned scoring weights change. Accepted
and generated recommendations are not success metrics. Hosted permission applies
to feedback too; local-only feedback cannot be silently sent to the worker.

The pre-invocation gate suppresses blocked recommendations when the same workflow
uses the same inspected content. Changing capture time, snapshot metadata,
profile keywords, prompt or model does not reopen it. For changed inputs, an
output with overlapping capabilities is also suppressed unless the operator
supplies reviewed new-context reconsideration. This is deliberately conservative:
it can suppress distinct ideas sharing a capability. It is not semantic novelty
proof; review material differences explicitly. Active deferrals remain blocked
until their date or an explicit decision revision. `--refresh` is no bypass.
Changes to feedback during inference prevent the old output being committed.
At most 100 current memory records are admitted per workflow; larger histories
fail for review rather than silently truncating. P6 can add a review inbox and
bounded selection; it does not own the first repetition gate.

New briefs include `recommendation_id`, `revision`, `revises`, `evidence_basis`,
and selected `exchanges`. Reconsidered revisions retain the previous family ID;
legacy P3 briefs use their immutable artifact ID and revision 1 as the fallback.
No old object is rewritten. A fresh family identity derives from workflow,
title and source-content basis; human-reviewed duplicate links connect separately
named families. Cross-capability semantic duplicates can still need human review.

## Reviewed interchange

The supported neutral contract is exactly **radar-interchange/1.0**. Unknown
major or minor versions fail; there is no implicit compatibility claim. P3
`radar-import --report ... --topic ...` remains the bounded schema-3.0 converter.
Use it for selected native Radar reports. The neutral importer/exporter adds
problem/experiment/brief/decision/outcome projections over the same state;
no second acquisition engine, shared database or circular trigger is introduced.
Implementing the consumer in AI Trend Radar remains a separate repository task.

Default `export:false` policies remain blocked, including the current Jobicy
corpus and its dependent drafts. A source can use controlled interchange only
with **explicit** `export:true`, `export_permission_reference`, and
`export_retention:"no-recall-required"`, plus the existing local/audit permissions.
There may be no `use_until` anywhere in exported lineage. Unknown rights,
required downstream expiry/deletion, or profile lineage block export. No source
policy was changed in the user's runtime data for Phase 4. Synthetic tests use
owned unlimited-copy material, which establishes behavior, not third-party rights.

1. Create a private request list: `[{"artifact":"ID","summary":"Exact reviewed summary","excerpts":[]}]`.
   At most 20 items. Supported artifacts: briefs, decisions, outcomes, non-repository
   contexts, and already imported neutral items. No generic raw state export.
2. Run `interchange-preview --input /private/selections.json`. It stores a managed
   preview and prints **the exact JSON and embedded Markdown**, its ID and digest.
   Inspect all content, including public URLs and policy attribution references.
   Summaries are explicitly selected text; selection is not factual verification.
3. After real approval, run `interchange-release --id PREVIEW_ID --review-digest DIGEST --reviewer 'Actual reviewer'`.
   It checks current policies/lineage and exact digest, records the release,
   and returns that envelope on stdout. It makes no network or other-repository
   write. An operator may save/share the approved no-recall copy under separate
   task authorization. The general P2 `export`/`restore` commands remain blocked.
4. Import through `interchange-import --input /private/reviewed-import.json`,
   whose shape is `{bundle: ENVELOPE, policy: REVIEWED_CONTEXT_POLICY}`.
   The importer preserves no-recall restrictions; it currently requires a
   compatible no-expiry/export-capable local policy too. More restrictive imports
   use P3's reviewed context path instead of weakening original restrictions.
5. Use `interchange-inspect --id IMPORT_ID` for current local viewing. Optionally
   pass `brief ... --exchange IMPORT_ID` (at most 10) for qualified synthesis.
   Imported items are **assessments only**, even when their producer claimed
   `observed`; they cannot become market observations, primary alternatives,
   demonstrated profile evidence, accepted decisions or verified local outcomes.
   Independent inspection must go through the P3 acquisition/contracts.

The envelope contains `schema`, `producer`, `exported_at`, `items`, `markdown`.
Each item preserves `origin:{producer,id,revision}`, `producer_schema`, immutable
`parents`, original hash `lineage`, `kind`, producer-asserted `basis`,
`observed_at` or unknown, `sources`, `restrictions`, and `content`.
`content` allows only title, selected summary, capability links, decision,
outcome type and limitations. Sources record HTTPS locator, evidence type,
original date/revision or unknown, and optional explicitly selected permitted
excerpt. Excerpt requests use `{context,quote}` from the selected artifact's
lineage; exact content must match. Source-code and imported-assessment excerpts
are refused. Job source URLs/dates/revisions are preserved without descriptions.
Selected excerpts are not required; missing inspected source content is disclosed.

Private profile lineage is blocked entirely. Reviewer names, credentials fields,
raw descriptions, source files, test logs and internal payloads are never copied
by the projection. An allowlist cannot detect every private string a person puts
in `summary`, title or a permission reference. **Review the exact preview**;
there is no claim of an automatic secret classifier. HTTPS locators exclude
credentials/query/fragment; they are displayed, not fetched or proven public.
Markdown escapes executable markup; the JSON is authoritative and its companion
must match the deterministic renderer exactly.

Round trips preserve origin IDs and restrictions; imports are idempotent and
record a transport receipt. The same origin/revision with changed content fails.
Returning local lineage depends on the still-retained original. Withdrawal of
an imported record retains permitted origin/content hashes and removes linked
copies/derivatives; old envelopes and metadata rewrapping cannot restore them.
Shared lineage may conservatively withdraw other dependent imports. Correctly
maintained participating stores refuse known withdrawn lineage. A disconnected
recipient cannot learn a withdrawal automatically, and a fresh store has no
previous tombstones. No remote recall, authenticity signature, malicious-producer
provenance verification or backup restoration guarantee is claimed. Sources
requiring such guarantees remain blocked; never erase tombstones or restore an
old state file to evade withdrawal. P6 adds monitoring and broader recovery.
