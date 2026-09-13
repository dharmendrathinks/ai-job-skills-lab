# Research contracts v1 — Phases 2–7 implementation status

The table remains the full target. Reviewed local imports, span validation,
snapshots and logical lifecycle operations are implemented in
`tools/research_evidence.py`; see [executable contracts and limits](evidence-operations.md).
Execution records, qualified automated extraction and bounded Jobicy acquisition
are implemented. Real permitted observations live outside the checkout; the
checked-in configuration and test fixtures remain synthetic. Human quality review
is pending; do not equate structural validation with semantic correctness.
Phase 3 context requests/receipts, reviewed profile proposals, four draft types and
read-only Radar conversion are implemented; see [decision contracts](decision-operations.md).
Phase 4 decision/outcome revisions, scoped profile proposals, recommendation
memory and neutral interchange are implemented; see [outcome contracts](outcome-operations.md).
Phase 5 coverage/board/segment reviews, frozen collection protocols/cohorts,
indexed translations and language evaluation are implemented; see
[global contracts](global-operations.md). Conditional sources/languages are not
promoted by the availability of these mechanisms.
The normative capability/lifecycle requirements remain in `PLAN_RESEARCH.md`.

| Contract | Required responsibilities |
|---|---|
| ResearchConfig | Explicit research mode, AI responsibility domain, independent interests/segments, source-policy references, language handling, private storage, budgets and subscription-only qualified inference. No default personal eligibility filters. |
| SourcePolicy | Exact acquisition method, permission basis/review date, allowed processing/hosted disclosure, storage classes, expiry/deletion rules, attribution and export restrictions. Unknowns cannot enable a source. |
| CollectionReceipt | Job/context kind, source/query, requested/effective filters, timestamps, pages/cursors, counts, completeness and policy; preserve failed, blocked, partial and uninspected outcomes. |
| ListingObservation | Source/employer/requisition identity, URLs, captured revision/representation/hash, original and normalized timestamps, language and availability evidence. |
| ExtractionExecution | Runtime/version, credential-free authentication category, configuration fingerprint, qualification evidence/status, bounded input revisions, versions/budgets and validation result. |
| RequirementAnalysis | Source statements and exact spans, required/preferred modality, normalized concepts, unknowns, execution/lifecycle links. Titles and stored gaps cannot establish source requirements. |
| MarketSnapshot | Conservative opening/employer groups, cohort and denominator definitions, deterministic counts, coverage limits and separately labeled inference. |
| EvidenceAcquisitionRequest | Brief/problem, category, bounded queries or explicit URLs/repositories, period, policy and retrieval limits. P3 reuses upstream research steps. |
| ContextEvidence | Source/type, original date/precision or unknown, captured revision, acquisition time, actually inspected content/locators/depth, inspector/method, import lineage, policy, contradictions and limitations. |
| Brief | One of four output types; evidence/context links, alternatives, independent judgments, limitations/abstention, assumptions, bounded deliverable, validation plan and revision. |
| ResearchProfile | Direction, self-declarations, inspected artifacts, scoped demonstrated capabilities/conditions and reviewable proposals; missing evidence is not missing ability. |
| OutcomeEvent | Brief revision, observed or self-reported decision/result, evidence/observer/date, corrections and supersession links. |

Each record has an explicit schema version and stable identity; schema revisions
and content revisions are separate. Every persisted artifact's manifest must
carry source/revision dependencies, policies, storage class, expiry, lifecycle
status and controlled copies. The helper owns IDs and validation, not the model.
Source-stated facts, normalization, cross-source inference and recommendations
remain separately labeled and traceable.

The implemented subset uses private versioned JSON, a one-writer lock and one
atomic manifest, reusing upstream `rank_state.save_state` unchanged. Snapshot
JSON and Markdown remain inside managed state. P6 adds one controlled HTML copy
and an optional managed backup; neither permits unmanaged export.
Partial runs cannot masquerade as complete.
Check eligibility before capture, submission, use, output commit and export.
Withdraw first from use, delete prohibited source/derived material, invalidate
caches, recompute surviving aggregates and mark briefs/reports for regeneration.
Keep only allowed audit metadata; restore must not resurrect withdrawn evidence.
Reviewed local imports and the narrowly reviewed Jobicy API path support
indefinite local retention, logical deletion and minimal withdrawal hashes.
Hosted submission additionally requires an explicit compatible permission basis
and provider-managed retention without a deletion deadline. Generic unmanaged export/restore and hard physical deletion deadlines are
rejected. P6 adds a fixed managed local backup/restore with its current journal. P4 adds explicit reviewed projections only for export-enabled source
policies with no downstream recall/expiry obligation; current false policies stay
false. No source policy was upgraded in runtime data. Execution responses,
caches and real-description evaluation artifacts inherit source dependencies.
Policy validation cannot independently verify an operator's permission claim.
No source with an unsupported hard deletion deadline is enabled. P6 adds
scheduled cleanup/monitoring and broader recovery; it is not a grace period.

Implemented P3 context shares the same storage and receipt schema. `context-receipt`
artifacts keep non-job evidence out of corpus counts. Exact content and original
imported-quote fingerprints prevent wrapper-based resurrection; generated briefs
and profile proposals inherit all dependencies. Its optional read-only
schema-3.0 AI Trend Radar importer consumes selected report files, separates
source evidence from assessments, and preserves missing dates/content as limits.
No database access, shared state or repository mutation. P4 retains that
converter for native reports and extends the shared store with
`radar-interchange/1.0` reviewed projections and imported assessments. JSON is
authoritative, its Markdown companion must match, origin/revision identity is
idempotent, and original restrictions/withdrawal lineage are preserved. Imported
outcomes cannot automatically become observed results, profile evidence or
independent corroboration. Missing evidence requires limitation/abstention.

Application identities, fit bands, gap logic and tracker state remain separate.
No research migration reconstructs missing descriptions from application notes.
Future migrations need validation, policy-compatible backup/reversible operation,
and withdrawal-aware rollback; unsupported major versions fail clearly.

P4 is an additive state-v1 migration: new artifact kinds and brief metadata,
no rewriting of retained P2/P3 objects. Legacy brief IDs imply revision 1.
Outcome corrections retain event history and retract dependent capability
proposals/profiles. All feedback/executions inherit current source permissions;
withdrawing evidence invalidates the resulting drafts. Interchange import is
never a state/backup restore. Known tombstones block returning content in a
participating store; remote recall and hostile-producer authenticity are not
verified. Unsupported expiry/recall obligations keep the affected path disabled.

P5 adds state-v1 collection-protocol, capture-assessment, cohort/comparison,
coverage-report, employer-board/board-link, segment-review, translation proposal/
review/failure, and language-gold/evaluation artifacts. Original observations and
prior snapshots are not rewritten. Coverage reports can feed the existing P3
brief interface with period, segment, source-health and analysis-version limits.
Frozen protocols include cadence/offset/tolerance and query/collector versions;
comparison checks complete receipt counts, all expected slots and publication
unknowns. Source/analysis changes or withdrawal cannot manufacture growth.
Reviewed translations preserve exact original spans and never become source
requirements. Source registry/query packs are versioned configuration, not rights
or quality grants. Source-level board absence views do not redefine P2 snapshots.


P6 retains state schema 1 and adds these explicit contracts. Source/helper schemas
are unchanged; no source policy, application state or user profile is migrated.

| Contract | Implemented fields, dependencies and behavior |
|---|---|
| operation-plan/1 | Explicit collect/analyze/brief/context/profile selections, budgets, cadence and operator; optional unattended qualification ID. Contains user configuration and non-owning hash references, not copied source/profile prose. Missing optional inputs defer only their step. |
| operations/1 | Separate private operations.json: run/plan IDs, intent/completion/ambiguous/deferred step states, frozen analysis queue, overflow, slots/missed counts, hash-only delivery receipts and 100 bounded health events. Single nonblocking operations lock; upstream atomic writer. Independent operations-origin marker blocks silent reset after ledger loss. Never included in evidence rollback. |
| operation-review | Run/step, retry or skip, reviewer/reason/date and explicit uncertain-retry limitation. Linked to the plan; ledger carries its ID. Reviewer assertions are not authenticated identities. |
| presentation | Brief revision/evidence-basis/decision identity and explicit acknowledgment timestamp. Depends on brief and any deferral decision; does not change outcome/profile state. |
| offline-report/1 | One current manifest: creation time/revision, escaped HTML, shown/overflow counts. Depends on all briefs/decisions contributing to display or counts; private fixed HTML copy synchronized by the Store, no executable markup or unmanaged export. |
| withdrawals/1 | Monotone minimal permitted hashes outside the primary file; merged before primary replacement and on every transaction. Missing/corrupt journal blocks backup restore, never reconstructed from an old backup. |
| backup/1 | Fixed backup.json with manifest/state digest, creation time and withdrawal digest. Any withdrawal or backup expiry conservatively invalidates the entire copy. Restore verifies lineage, requires current journal and sweeps expiry; operations/delivery intents are not rolled back. |
| notification-preview/1; notification-approval | Bounded workflow/revision/ID payload, destination hash, exact review digest, selected presentation identities, reviewer/date and source dependencies. Requires existing P4 no-recall-compatible export permission; private profile lineage remains excluded. |
| delivery receipt | Destination/content identity, attempt timestamp and sent/ambiguous status. Intent before a bounded POST; no automatic resend. No source prose, webhook secret or provider exception in the ledger. |
| unattended-probe / unattended-qualification | Actual owned subprocess smoke, binary/config/client/Python/Codex path/harness identity, subscription/token/latency metadata and scope limits. Separate explicit operator account-use assertion, seven-day review expiry, enforced matching before scheduled model calls. |
| model-evaluation/1 | Owned dataset/prompt/schema/harness/model revision and settings, exact outputs, validation/atom scores, timings and resident estimates. Human review pending; local experiment cannot enable the production extractor. |

The Store adds a locked recovery entry point while preserving the upstream atomic
writer. Valid P2–5 stores acquire withdrawals.json lazily; the original manifest
schema/IDs remain stable. An old writer does not know these controlled copies:
do not downgrade active state or restore an older withdrawal/operations ledger.
Local logical-deletion guarantees cover managed copies at the next supported
operation, not hard timing, physical media, browser memory or unmanaged backups.
See [operations, failure handling and activation gates](continuous-operations.md).


## Phase 7 domain extension

The default AI envelope/schema and its historical artifact IDs remain intact.
A newly initialized non-AI workspace adds a `domain_pack` field to state schema 1
and a private `domain-binding.json` with exact domain ID, version, pack digest and
taxonomy version. P6 backups retain the header and must match that binding before
restore. Source withdrawal leaves the domain identity intact. Existing AI stores
are not migrated; foreign backups, missing bindings and in-place reclassification
fail closed. The default AI directory is reserved; choose a separate empty private
data workspace for opt-in.

Domain-pack/1 contains responsibilities, exclusions, capability IDs, aliases,
acyclic prerequisites, candidate queries, a frozen evaluation dataset reference
and limitations. The first reviewed pack is backend-platform/1. Only reviewed
built-in catalog entries can initialize a workspace; a pack cannot execute code,
load dependencies or qualify collection/model access. Another revision requires
an explicitly selected new workspace and permitted acquisition/import.

Backend analysis uses `domain_fit` and its versioned taxonomy through the shared
P2 extractor/validator. Domain, taxonomy, prompt, schema and code versions enter
cache identity. Compatible analysis/snapshot/coverage/brief/profile/outcome records
carry an explicit domain reference; source identities and receipts stay original.
All four brief schemas use that workspace's capabilities and preserve source
scope, external-evidence requirements, unknowns and P4 reviewed feedback. Backend
synthetic evaluation drafts explicitly carry synthetic scope into prompts and
rendered limits; generated scores do not establish real market demand.

Cross-domain-comparison/1 is an ephemeral local read with both lifecycle locks,
separately disclosed sample scopes/windows/receipts/segments/versions, conservative
matching opening IDs and null pooled counts/demand ratios. It is not stored across
independent lifecycles or exported by default. A shared taxonomy/cohort, missing
employer identities or non-overlap is never inferred. P5 longitudinal sufficiency
rules remain unchanged.

AI neutral interchange 1.0 is retained. Backend uses an explicit 1.1 envelope with
matching domain reference and Markdown; receiver pack digest/taxonomy mismatch is
rejected before import. Existing source export/no-recall/profile/lineage controls
apply. Radar 1.1 consumer support remains separate and conditional. Owned domain
case/evaluation artifacts link to source observations/executions and retain actual
scores, runtime versions and pending human review; the public evaluation record
contains only development results over author-owned fixtures.

## Managed HTML report payload v2

`offline-report` payload 2 contains `schema_version`, `revision`, `created_at`,
`pages` (fixed `jobs.html` and `projects.html` strings), and `counts` for jobs, projects and YouTube. The projects page contains both brief
tabs; each has its own shown/total counts and generation limit.
The outer content-addressed artifact envelope remains v1. Both pages depend on
all observations/receipts/latest analyses contributing to counts plus current
project/YouTube evidence and decisions, including nonselected tabs and overflow. Withdrawal invalidates the pair conservatively.
The CLI binds private output-location/origin records to the ignored checkout
`reports/`; corpus persistence remains external. Nondefault workspaces receive
separate path-hash subdirectories. See [continuous operations](continuous-operations.md)
for migration, permissions, interrupted-write cleanup and limits. Report content
is escaped; one exact-hash-authorized script controls local search/filter/reset,
without network, storage or execution of source instructions. This approved local
view location does not grant unmanaged export or publication rights.

## Discovery query revision and collection trigger

`collection-attempt` records may include `trigger` (`manual` or `scheduled`) and
`query_pack_revision` for default rotating AI seeds. Older records remain readable
and still inform the scheduled guard. Receipts keep exact request/effective query
parameters; the selected pack revision is also in limitations. The query-plan view
separates manual readiness from scheduled eligibility. It counts attempted queries
and returned observations, not classified roles, openings or market growth. No
corpus/analysis migration or automatic source activation is implied.

Report role facets use `report-title-families/1`, recorded in the jobs page's
presentation provenance. They derive solely from the displayed captured title,
can overlap, and never write RequirementAnalysis, profile or market classifications.
Unknown-only location/availability facets are omitted from generated controls,
without filling missing evidence or changing observation values. No state-schema
migration is required; regenerate the managed v2 HTML artifact to update its UI.

The report's location facet uses captured `country`, falling back to a nonempty
string in `segments.source_geography`. Source geography is explicitly labeled on
the card and preserved as a region/multi-country label without parsing it into
normalized countries. This presentation fallback does not mutate source fields,
coverage counts or availability. Missing language is labeled separately.

## Connected learning contracts

The additive Analysis v2, SkillCatalog/SkillSnapshot, LearningPath, independently
sourced LearningProgress and EvidenceAnswer contracts are specified in
[learning operations](learning-operations.md). Existing v1 analyses stay readable.
All new derived records, model intents and managed report copies inherit their
actual dependencies and expiry. Hash-only path associations do not copy job prose
into independent work records. No new unmanaged export permission is implied.

## Learning correction lifecycle

LearningProgress v1 keeps `supersedes` as retained history. All non-history
consumers of superseded progress are invalidated through existing transitive
withdrawal, including briefs and reports, on write and on the next supported
operation for older stores. New reports depend only on current progress records.
Independent result contexts require explicit withdrawal if their content is also
invalid. This changes lifecycle enforcement without changing the v1 schema.
