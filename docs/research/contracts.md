# Research contracts v1 — Phase 2 implementation status

The table remains the full target. Reviewed local imports, span validation,
snapshots and logical lifecycle operations are implemented in
`tools/research_evidence.py`; see [executable contracts and limits](evidence-operations.md).
Execution records, qualified automated extraction and bounded Jobicy acquisition
are implemented. Real permitted observations live outside the checkout; the
checked-in configuration and test fixtures remain synthetic. Human quality review
is pending; do not equate structural validation with semantic correctness.
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
JSON and Markdown remain inside managed state, without separate exported copies.
Partial runs cannot masquerade as complete.
Check eligibility before capture, submission, use, output commit and export.
Withdraw first from use, delete prohibited source/derived material, invalidate
caches, recompute surviving aggregates and mark briefs/reports for regeneration.
Keep only allowed audit metadata; restore must not resurrect withdrawn evidence.
Reviewed local imports and the narrowly reviewed Jobicy API path support
indefinite local retention, logical deletion and minimal withdrawal hashes.
Hosted submission additionally requires an explicit compatible permission basis
and provider-managed retention without a deletion deadline. Unmanaged export,
restore and hard physical deletion deadlines are rejected. Execution responses,
caches and real-description evaluation artifacts inherit source dependencies.
Policy validation cannot independently verify an operator's permission claim.
No source with an unsupported hard deletion deadline is enabled. P6 adds
scheduled cleanup/monitoring and broader recovery; it is not a grace period.

P3 context shares the same storage and receipts. Its optional read-only
schema-3.0 AI Trend Radar importer consumes selected report files, separates
source evidence from assessments, and preserves missing dates/content as limits.
No database access, shared state or repository mutation. P4 reuses that conversion
for `radar-interchange/1.0` JSON and Markdown outcome exchange with restrictions
and original lineage preserved. Missing evidence requires limitation/abstention.

Application identities, fit bands, gap logic and tracker state remain separate.
No research migration reconstructs missing descriptions from application notes.
Future migrations need validation, policy-compatible backup/reversible operation,
and withdrawal-aware rollback; unsupported major versions fail clearly.
