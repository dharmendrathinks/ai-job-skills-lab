# Evidence operations — Phase 2

`tools/research_evidence.py` coordinates permanent imports, annotations,
qualified model analysis, snapshots and logical withdrawal. Bounded Jobicy
acquisition and the Codex worker use the same state/lineage contracts. No
application profile is loaded. Recommendation briefs begin in P3.

## Supported storage policy

Before importing, the acquisition method and permission for the exact input
must be reviewed and the reviewer/method recorded honestly. The validator checks the recorded policy and rejects unsupported
behavior; it cannot establish legal permission from a boolean or reviewer name.
The Jobicy API path has a dated document review and bounded live capture.
Other providers remain conditional. Checked-in fixtures are author-owned
synthetic content; real observations stay in private state outside the checkout.

Contract v1 accepts `reviewed-local-import` or `jobicy-api-v2` with
`indefinite-logical-deletion`: permission to store raw and derived local content
without a physical deletion deadline, plus permission to retain minimal hashed
withdrawal metadata. A `use_until` ends authorization to use the stored content;
it is **not** a promise to erase physical copies at that instant. Sources needing
deadline deletion, backup recall or physical erasure cannot use this path.
Unmanaged export must be false. Hosted disclosure is false by default; enabling
it requires `hosted_retention=provider-managed-no-deletion-deadline` and an
explicit `hosted_permission_reference`. This records a compatible permission
basis, not a provider deletion or training-settings guarantee. Review includes
whether OS backups, snapshots, original input files and local inspection are
compatible with the permission basis. Do not enable a source requiring control
of those copies; this helper cannot control them.

The store creates a directory with mode 0700 and files with mode 0600. It refuses
nonprivate existing paths and symlinked state/lock files. The CLI reuses the P1
preflight to reject checkout-overlapping storage and unsafe public templates.
These are supported-entry-point checks, not an OS sandbox or protection against
the account owner manually changing files.

## Local commands

From this checkout, with Python 3.10+ on macOS/Linux:

```sh
python3 tools/research_preflight.py --mode research --action import
python3 -m tools.research_evidence import --input /absolute/private/bundle.json
python3 -m tools.research_evidence annotate --input /absolute/private/annotation.json
python3 -m tools.research_evidence collect --query "machine learning" --count 20
python3 -m tools.research_evidence qualify
python3 -m tools.research_evidence analyze --id OBSERVATION_SHA256
python3 -m tools.research_evidence snapshot
python3 -m tools.research_evidence status
python3 -m tools.research_evidence withdraw --id ARTIFACT_SHA256
```

Use `AI_JOB_RADAR_HOME` for an absolute private destination outside the checkout.
The preflight is read-only. Evidence helper operations initialize state when
needed and apply pending expiry, including `status`. Stdout carries IDs/counts
only; detailed errors omit imported content. Invalid input produces a blocked
exit code. Use the contracts below to diagnose it locally, without disclosing
restricted input to a model.

Private state lives in `research-state.json`. It contains the artifact manifest,
source data, annotations, snapshot JSON and its `markdown` field. Inspect it with
a local editor only where the policy permits. A local editor may retain its own
history; restrictive sources needing that history recalled remain unsupported.
There is no public report generation or unmanaged file export. `export`,
`restore` on the P2 entry point fail closed. P6 offers only its fixed managed rollback copy. `analyze`/`extract` require an observation ID, a matching
qualification and hosted-compatible current policy. Failures defer without a paid
fallback. `--refresh` requests one uncached extraction; ordinary reruns reuse
validated analysis keyed by observation, prompt, schema, taxonomy, validator and
qualified runtime versions. Profile changes do not invalidate market extraction.

## Executable contracts v1

Validation lives in `tools/research_evidence.py`; representative complete inputs
are `bundle()` and `annotation()` in `tests/test_research_evidence.py`. Tests use
temporary directories, not your actual research state. Unknown fields at the
record boundary and unknown schema/taxonomy versions fail rather than migrate
silently. Imports are limited to 2 MB and 100 observations through the CLI.

| Record | Fields and interpretation |
|---|---|
| Import bundle | `schema_version`, `policy`, `receipt`, `observations`. Synthetic/job receipt kinds cannot coexist in a store. |
| SourcePolicy | `source`, `method`, `reviewed_by`, `reviewed_at`, `permission_basis`, `permission_reference`, `local_processing`, `retention`, `hosted_disclosure`, `export`, `audit_hashes`, `limitations`, optional `use_until`, `hosted_retention`, `hosted_permission_reference`, schema version. Applies to raw and all descendant artifacts. |
| CollectionReceipt | Source, job/synthetic kind, query, requested/effective filters, start/end times, pages (`locator`, status, returned count, next cursor), bounded-request completeness and limitations. Empty failed/blocked attempts are retained. “Complete request” never means a complete market. Page count must match imported observations. |
| ListingObservation | Native source ID; employer name/domain/requisition; URL/title; nullable description; capture time; source revision; original and parsed posting time; nullable language/country; availability and its evidence; analytical segments; limitations. Optional raw HTML and `description_transform=html-text/1` preserve the source representation; spans target normalized text. The helper adds source, receipt and description hash. Parsed timestamps include zones. Unknowns remain null. |
| Human annotation | Observation ID, method (`human-reviewed` or `synthetic-fixture`), reviewer/date, taxonomy version, applied/research-heavy/mixed/unknown responsibility class, claims, unknowns, schema version. Reviewer fields are provenance assertions, not independent verification. Model-origin imports are unavailable; the qualified worker creates `codex-extraction` analyses with pending human review. |
| Claim | Skill/responsibility/constraint kind; required/preferred/unspecified modality; start/end **Unicode code-point** offsets into the exact captured description; exact quote; capability IDs and separate tool names. Classification/modality correctness still requires human review. No description requires no claims and unknown classification. |
| Artifact envelope | Content-derived ID, schema version, kind, payload, dependencies, inherited earliest use expiry. Source and policy lineage are transitive. State verifies content hashes and dependency presence before use. |
| Market snapshot | Captured revisions and latest source listings; conservative opening groups; employer counts; observed-open/closed/unknown/conflicting availability; missing descriptions; countries/languages and unknown counts; analysis methods; original receipts/queries/filters/periods; capability, modality and tool counts; limitations and Markdown. |

The taxonomy is `ai-capabilities/1` in the helper. Capability counts are not
framework counts. The source statement is its exact quote; capability labels
and modality/classification are reviewed normalization. Cross-source inference
and model recommendations are empty here. No fit score or known-skill removal
changes admission or aggregates. Keep application ranking untouched.

Per-source native IDs retain revisions. For cross-source deduplication, a human
must establish a real employer domain and employer-issued requisition from
inspected source metadata. Do not populate them from a guess or an ATS domain.
Only their joint equality permits a merge; names/titles alone never do. Missing
employer identity is reported and excluded from verified-domain counts. Domain
identity is a conservative proxy, not a corporate-entity registry. Reposts with
new requisitions remain distinct; ambiguous same-time conflicting revisions are
rejected for review. Availability reflects capture evidence, not a fresh check.

## Atomicity, expiry and withdrawal

Reuse upstream `tools/rank_state.py:save_state` unchanged for atomic replacement,
under a research-only `fcntl` writer lock. There is a single content manifest,
so a failed write leaves the prior complete state; orphan temporary writes are
discarded on the next operation. No multi-file partial report is served. This
does not promise fsync/power-loss durability; broader recovery is P6.

Every operation checks expiry before work, persists any removals, checks again
before final commit, and fails if evidence expires during the operation.
Withdrawal removes the selected artifact and all descendants, including reports
and their excerpts. Minimal hashed tombstones prevent exact artifact replay and
recapture of the identical withdrawn description in a changed source envelope.
Text altered to evade those hashes is not detectable; do not claim semantic
deduplication or protection against deliberate manual store replacement.
Snapshots containing removed evidence disappear and must be regenerated from
survivors, with changed denominators visible. No external copies are emitted.

Expiry is enforced on supported access, with logical removal on the next
operation. P6 implements scheduled cleanup/monitoring and a managed rollback copy; see
[continuous operations](continuous-operations.md). Generic unmanaged `restore`
remains unavailable. P6 restore requires the current independent withdrawal journal.
Do not replace the state file manually or bypass its withdrawal ledger.

## Enabled source and evaluation

The Jobicy path performs one capped API request and records failures. Explicit
user-triggered searches have no application-imposed hourly cooldown. Scheduled
polling retains a one-hour guard after any attempt, including failures. This
separates our scheduler policy from an undocumented request-level API quota.
Source errors still stop the action; there is no automatic retry or bypass. The narrow policy review
expires on 2026-10-09. It permits only compatible logical retention and hosted
processing, preserves source/canonical attribution and forbids unmanaged exports.
A policy update needs a fresh review, not a date-only extension. Remote sampling,
unknown country/language/employer domains and unverified vacancy status are
explicit limitations. Unknown publication timezones are not guessed.

`python3 -m tools.evaluate_research` runs opt-in synthetic comparisons using the
qualified subscription worker. `--observation ID` compares the same retained
real description; those comparison artifacts inherit its lifecycle and are
withdrawn with it. The upstream arm replays the unchanged targeted upskill rules
with supplied inputs; it is not a complete application-workflow replay. Real
accuracy and recommendation usefulness cannot be claimed without human labels.
See `phase2-validation.md` for actual results, repeatability and remaining review.

P3 and P5 branch independently from P2. Conditional sources do not gate unrelated
capabilities. Scheduled cleanup, monitoring and broader recovery remain P6.

## Broad AI discovery and manual searches

```sh
.venv/bin/python -m tools.research_global ai-query-plan
.venv/bin/python -m tools.research_evidence collect --count 100
.venv/bin/python -m tools.research_evidence collect --query "AI product" --count 100
```

The default AI collection rotates through the least recently attempted seed in
`ai-engineering-queries/1`, defined in `tools/research_sources.py`: LLM, AI product,
applied AI, AI engineer, generative AI, AI agent, retrieval, LLM evaluation, AI
security, inference, AI infrastructure, MLOps and machine learning. Backend/domain
workspaces retain their own query selection. Explicit `--query` remains exact.
Each call makes one request, defaults to 100, and preserves its query, count,
source receipt, attempt trigger and (for rotation) query-pack revision. Different
queries are not sent as an undocumented Boolean or comma-separated expression.

The query-plan view reports actual attempts, returned observations and pending
queries. None of these establish that a role has been found: classification must
use captured responsibilities, not query keywords or titles. Empty results and
failed requests are not evidence of market absence. Cross-query repeats use the
existing source ID/revision deduplication. Expanded sampling cannot show growth.
Retained old observations/briefs are not silently reclassified or regenerated.

On 2026-09-10 the official Jobicy README was rechecked for keyword and polling
semantics: `tag` searches available content, has length 3–50, and the fair-use
text restricts automated polling frequency. It does not specify a per-query hourly
HTTP quota for a finite user-triggered search session. The reviewed decision
removes our blanket manual cooldown, keeps periodic polling hourly, and treats
server refusals/errors as stopping conditions. This does not grant unlimited
request volume or relax source/retention policy. No scheduler is activated.
[Source documentation](https://github.com/Jobicy/remote-jobs-api#fair-use).
