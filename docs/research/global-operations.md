# Global coverage, languages and comparable observations — Phase 5

Phase 5 extends the P2 evidence manifest and deterministic aggregate. It branches
from P2, independently of P3/P4 providers. No new database, programming language,
job-data subscription, JobSpy integration, collector tree or dashboard is used.
The existing upstream `/add-portal` reconnaissance/test pattern and scraper health
reporting conventions are reused, with research permission gates before probes.
Application portal behavior is unchanged. A source's access, robots directives,
or library license does not establish research-data permission.

## Commands and journey

All commands below run from this checkout using the existing environment. Inputs,
original descriptions, translations and reports remain in the private P2 store.
`inspect` displays policy-checked JSON; it does not export a file or execute links.

```sh
.venv/bin/python -m tools.research_global registry
.venv/bin/python -m tools.research_global query-pack --language de
.venv/bin/python -m tools.research_global coverage
.venv/bin/python -m tools.research_global inspect --id COVERAGE_ID
.venv/bin/python -m tools.research_global protocol --input /private/protocol.json
.venv/bin/python -m tools.research_global capture-assess --input /private/capture.json
.venv/bin/python -m tools.research_global cohort --input /private/cohort.json
.venv/bin/python -m tools.research_global compare --id COHORT_ID
.venv/bin/python -m tools.research_global vacancies --id PROTOCOL_ID
```

`coverage` defaults to the last 28 elapsed days, by capture time. `--from` and
`--to` take zoned timestamps; end is exclusive. An optional `--input` contains
expected segment lists, e.g. `{"countries":["DE","IN"],"language":["de","hi"],"arrangement":["onsite","remote"]}`.
These are analytical gap checks, never eligibility exclusions. Without selected
expected segments, no claim of a comprehensive missing-country list is made.
Country/language maps are tables of distinct openings with unknowns; there is no
geocoding or invented worldwide heat map. Source-native arrangement/employment/
seniority/industry values remain labeled source data unless separately reviewed.
Multi-valued segments overlap; their sum is not the overall opening denominator.

Reports retain sources, receipts, query/effective filters, period, sample size,
verified versus reported employers, missing descriptions, language/country
unknowns, analysis versions, employer concentration counts, translations and
source-health receipt statuses. Receipt status is observed collection evidence,
not an automatic network health probe. A cap or failure is never silently healthy.
Old P2 snapshots remain addressable; P5 views use their own versioned projection.
Use `tools.research_decisions brief --snapshot COVERAGE_ID ...` to feed a P5
coverage slice directly into the four P3 workflows. The qualified worker receives
period, segments, missing segments, source health and analysis versions with the
same evidence/policy dependencies; no new collection/profile eligibility rule is
introduced.

## Source decisions and board identity

[`source-registry-v1.json`](source-registry-v1.json) records all 16 candidates,
including every source carried from the old plan and the inherited portals.
Each has an explicit go-limited/conditional/no-go decision, exact implementation
path or absence, collection/authentication/₹0 mechanism, coverage/completeness
risks, inspected references and limitations, gap, and go/no-go validation steps.
Only existing Jobicy is go-limited; its existing source policy still validates
before capture and expires on 2026-10-09. The registry is not a permission bypass
or a live adapter enable switch. Other sources remain disabled, independently of
coverage/cohort/language work.

The actual retained sample has 20 remote openings, zero verified employer domains
and unknown country/language labels. This demonstrates an employer/onsite and
metadata gap, not that another remote feed necessarily fixes it. Lever remains
the first direct-board candidate; Freehire remains a reuse candidate. The
research retention/disclosure scope remains unresolved for those paths. No new
source was promoted merely to increase adapter count. Bounded live validation,
fixtures, supported lifecycle/export behavior and measured incremental value
are required before any future promotion; all stay within ₹0 job-data access.

For a permitted, independently inspected board, use `board --input` with
`{schema_version:1, source, instance, board, employer_domain, ownership_context,
quote, reviewer, limitations}`. The ownership context must already be captured
through P3's reviewed evidence path, with inspected content and an exact quote.
This reuses that path; it does not acquire or execute a new repository. A board
entry alone cannot establish a posting's employer or authorize collection.

`board-link --input` takes `{schema_version:1,observation,board,source_field,quote,
employer_requisition,reviewer}`. `source_field` is the original URL or source
segments, with exact quoted evidence; a non-null requisition must occur in that
quote. The source must match the reviewed board. Use instance/board-specific
source identities in imported evidence (e.g. `lever:eu:employer-board`) so native
IDs cannot collide across boards. Registering conflicting instance/board identities
under one source, or conflicting ownership for that source, is refused. The P5 projection reuses P2 conservative
employer-domain-plus-requisition deduplication; an unproved requisition stays null.
Names/titles alone cannot merge employers/openings. Withdraw an incorrect mapping
before relinking; its derived views are invalidated. Existing observations and
application state are not rewritten. Reviewers' semantic ownership claims are
not independently authenticated by substring checks.

## Frozen protocols, captures and cohorts

All contracts use schema version 1; unknown fields/versions fail closed.

| Contract | Required data and validation |
|---|---|
| CollectionProtocol | `source`, `instance`, `board`, `query`, `requested_filters`, `effective_filters`, `collector_version`, `query_pack_version`, `scope` bounded-sample/board-inventory, `cadence_seconds` (1h–7d), `reviewer`, nonempty `limitations`. Optional `capture_offset_seconds` defaults to 0; `capture_tolerance_seconds` defaults to 300, at most one quarter cadence. Offsets are measured inside each cadence slot. They are persisted in new definitions; legacy missing values use those defaults. |
| CaptureAssessment | `receipt`, `protocol`, boolean `fresh` and `terminal`, `evidence`, `reviewer`, `changes` list. Source/query/filters must exactly match protocol. Terminal requires complete-request, successful pages and a null final next cursor. A manual claim cannot turn a P2 partial receipt into complete. Freshness/terminal meaning still requires real evidence; unknown is false. Immutable assessments cannot be relabeled in place. |
| CohortDefinition | `name`, explicit `protocols`, `basis` capture/publication, exactly two `windows:[{from,to},{from,to}]`, `reviewer`, nonempty `limitations`. Windows must be elapsed, adjacent, equal, nonoverlapping and whole cadence slots. Target: two adjacent 28-day windows. Explicit shorter windows are exploratory sample comparisons, not achievement of that target. |
| CohortComparison | Both window reports, exact protocols, current generator hash, source additions separately, collection issues, sufficiency, and nullable opening/capability deltas. Every expected slot needs exactly one matching, fresh, complete, unchanged capture at the specified offset/tolerance. Missing, duplicate, unassessed, partial, stale, failed, boundary-crossing or changed captures make the comparison insufficient. |

All receipts for the chosen source/window are checked: changed queries cannot be
cherry-picked out of a comparison. Protocols sharing a provider must have explicit
board/instance source identities and assessments. Added sources are reported
separately; adding one to the cohort requires coverage in both windows. Captured
counts are checked against receipts so withdrawn/missing observations cannot
be interpreted as fewer vacancies. Publication-based slices require actual
publication dates; capture/discovery is never substituted for unknown publication.

P2 aggregation handles revisions/deduplication for each selected slice.
Capability deltas additionally require every latest listing to be assessed, one
common extraction/taxonomy/model/prompt version, and no unknown version. Version
identity follows the analysis execution artifact, not a title or receipt. Counts
may be comparable while capability analysis is insufficient. Neither a positive
delta nor sufficient windows is proof of global growth, new hires, new requisitions
or willingness to pay: these are observations within a sampled source cohort.

`vacancies` supplies a source-level historical view. For board-inventory protocols
only, two fresh complete unfiltered absence receipts at least 24h apart can
establish no-longer-listed. A reappearance resets absence evidence; explicit
closed status is preserved. Capped/filtered feeds, cache/304/stale receipts,
outages and a single failed detail cannot close a listing. Older non-closed
observations become stale after two protocol cadences. Source health is reported
separately. Secondary aggregators cannot reopen this authoritative board view;
no global merge of their activity is asserted. The retained P2 snapshot remains
its original at-capture view; neither view claims live verification.

## Original language, translations and evaluation

[`query-packs-v1.json`](query-packs-v1.json) provides versioned English, German,
Hindi and Spanish AI query candidates. No new language is quality-promoted by
those strings. Inspect the pack, explicitly select a supported query, then use
the already reviewed collector or permitted local import; freeze the pack/version
and effective filters in the capture protocol. There is no automatic multi-query
scrape, profile-language filter, location inference or silent query translation.

`segments --input` takes `{schema_version:1,observation,reviewer,reviewed_at,values,
evidence,limitations,supersedes}`. Supported values: countries (reviewed alpha-2
code list), language (language tag), industry, seniority, arrangement, employment
type. Every value needs `{source_field,quote,reason}` referencing the original
`description`, `segments`, `country` or `language` value. Profile/title-only inference
is refused; the human/inspector must justify the normalized value. Original source
fields are retained; corrections explicitly supersede the previous review.

```sh
.venv/bin/python -m tools.research_global translate --id OBSERVATION_ID --language en --target hi
.venv/bin/python -m tools.research_global inspect --id TRANSLATION_PROPOSAL_ID
.venv/bin/python -m tools.research_global translation-review --input /private/review.json
.venv/bin/python -m tools.research_global language-gold --input /private/reviewed-gold.json
.venv/bin/python -m tools.research_global language-evaluate --input /private/evaluation-pairs.json
```

Translation uses the same qualified empty-tool-registry Codex worker, current
source hosted-disclosure policy and subscription budget. Code splits the entire
original into bounded indexed segments, retains exact original offsets/text,
and requires one translation per index. Model omissions/reordering/duplicate IDs
fail. Code always records that fidelity and the asserted source language need
human review, even if the model reports no additional limitations. Model/config/
prompt/validator/segmentation versions and usage are recorded. Failures defer
without automatic retries or paid fallback. Reviewed translations remain separate
from original-language extraction and cannot establish an explicit requirement
from translated wording; original exact source spans remain authoritative.

TranslationReview is `{schema_version:1,proposal,decision:accept|reject,reviewer,notes}`.
Only actual user review authorizes acceptance. Accepted translations affect only
reviewed-translation coverage; rejection leaves the source unchanged. Corrections
use a fresh proposal/review. No accepted review here establishes language-wide
model quality. Untranslated and unassessed evidence stays in the corpus.

LanguageGold is `{schema_version:1,language,split:held-out|development,annotation,
limitations}`. `annotation` uses the existing P2 human-reviewed or synthetic-fixture
span contract; it is stored as gold, not as an extra analysis. Freeze gold before
evaluation. Language evaluation takes `[{gold:GOLD_ID,analysis:ANALYSIS_ID}]`,
reuses `tools/evaluate_research.py` atom scoring, and reports required/preferred
atom errors, class correctness, label basis, frozen-before-analysis order and
language/version breakdown. Duplicate description/version pairs are refused.
95% precision / 85% recall remain **targets**, not claims or automatic promotions.
Recorded order does not prove absence of training contamination. Translation
fidelity needs its own human review; extraction metrics cannot establish it.

[`multilingual-v1.json`](../../tests/fixtures/research/multilingual-v1.json) contains
owned German, Spanish, Hindi and English/negation examples with provisional
exact-span labels. Human review is pending; these are not customer descriptions,
measured language quality or a completed held-out model evaluation.

## Lifecycle and limits

Every review, translation, board mapping and report is linked to original source
artifacts. Withdrawal/expiry invalidates derived views, accepted translations and
evaluations. A refreshed comparison checks missing data against retained receipts;
old reports are never silently recomputed or rewritten. Unmanaged export/restore
remains blocked; P4 controlled interchange still requires every source ancestor's
explicit compatible permission. No current provider permission was upgraded.

P6 owns unattended scheduling, monitoring, presentation queues and broader recovery.
P5 does not promise captures occurred when the machine was asleep, worldwide
coverage, remote recall, authentic reviewer identity or automatic semantic
correctness. Conditional providers do not block these deterministic capabilities
or unrelated work.
