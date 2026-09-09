# Phase 3 decision operations

The four draft workflows extend upstream upskill's prerequisite/practice planning,
expand's selected-repository inspection and `09-web-research.md` source verification.
Research omits fit weights, known-skill removal, tracker admission and access
escalation. Canonical routing stays in `.claude/skills/research/SKILL.md`; there is
no second command/specification tree, database or broad research platform.

Use Python 3.10+ and the same private store, qualified Codex subscription and
source policies as P2. The implementation creates **drafts for human review**;
structural validation is not semantic approval or proof of usefulness.

## Commands and journey

```sh
python3 tools/research_preflight.py --mode research --action brief
python3 -m tools.research_decisions context-import --input /private/context-bundle.json
python3 -m tools.research_decisions context-acquire --input /private/request.json
python3 -m tools.research_decisions context-acquire --input /private/repository-request.json --repo /path/to/read-only/repository
python3 -m tools.research_decisions radar-import --input /private/radar-policy-bundle.json --report /path/to/selected-report.json --topic TOPIC_ID
python3 -m tools.research_decisions profile-propose --input /private/profile-proposal.json
python3 -m tools.research_decisions profile-review --id PROPOSAL_ID --decision accept --reviewer REVIEWER
python3 -m tools.research_decisions brief --kind learning --snapshot SNAPSHOT_ID --context CONTEXT_ID
python3 -m tools.research_decisions inspect --id BRIEF_ID
```

`--kind` accepts `learning`, `project`, `product` and `youtube`. Repeat `--context`
for at most ten selected contexts; optional `--profile` takes a reviewed research
profile ID. `--refresh` requests an uncached draft. Without a profile, direction
fit is conditional; no application CV/profile is loaded. Existing skills remain
market evidence and can have deeper-practice recommendations.

The preflight is read-only. Execution commands initialize/update managed private
state. Mutation commands return IDs/status. The explicit `inspect` action displays a
brief, exact source quotes, capture traces, inspected alternative paths and the
distinct source count as plain terminal text. It strips control/bidi characters,
checks current lifecycle eligibility and never opens links or executes content.
It creates no exported report file. Local display/history must be compatible with
the source policy, just as editor history must be; it cannot recall terminal logs
or prevent manual copying by the account owner. Use a policy-compatible local
editor for the complete `proposal`, `profile_evidence` and manifest. The
rendered Markdown is inside that manifest, not an unmanaged export. P6 adds the
review inbox/offline interface; no server or dashboard is introduced here.

Before profile acceptance, inspect the proposal and its cited work/results.
`profile-review` is an explicit operator action, not a model-callable tool.
`reject` records the decision and creates no profile. Reviewer names are recorded
assertions, not authenticated identities. A later explicit review can change a
prior decision; earlier events remain visible. A model-generated brief never
updates or accepts a profile.

## Executable contracts

Complete owned synthetic examples are in `tests/test_research_decisions.py`.
Do not use their fictional permission assertions for real material.

| Contract | Required fields and rules |
|---|---|
| Context bundle v1 | `schema_version`, `policy`, `request`, `receipt`, `records`. P2 source policy uses `method=reviewed-context`. Every selected source/method/content use must be covered by the recorded review. Unknown permission fails closed. |
| Acquisition request v1 | `problem`, `category`, explicit `locators`, `query`, `period.from/to` (nullable ISO times), `max_items` 1–10, schema version. One bounded request, no autonomous crawling. |
| Shared receipt v1 | P2 receipt schema with `kind=context`, query/filters/time/pages/counts/completeness/limitations. `context-receipt` artifact keeps it separate from job/synthetic corpus receipts. Pending/failed attempts remain visible. |
| ContextEvidence v1 | `source`, `evidence_type`, `original_date`, `date_precision`, `revision`, `captured_at`, `content` or null, `locator`, `inspector`, `inspection_depth`, `observation_basis`, `conditions`, `lineage`, `limitations`, schema version. Source dates use day/instant precision or unknown. Repository revisions require immutable Git hashes. |
| Context categories | `repository`, `product`, `problem`, `discussion`, `trend`, `experiment-result`, `imported-assessment`. Inspection is not reproduction; only documented reproduced experiment-result records can support a demonstrated profile level. |
| ResearchProfile proposal v1 | Policy, direction list, capability entries and nullable `supersedes`. Each entry has taxonomy capability, `self-declared`/`inspected`/`demonstrated`/`not-evidenced` level, evidence IDs, conditions and limitations. Inspection/reproduction levels require appropriate retained context. |
| Brief v1 | Type, draft status, input snapshot/context/profile IDs, version/cache/execution references, proposal, evidence limits, profile evidence, managed Markdown. Four distinct section schemas, prerequisite capability IDs and six independent ordinal judgments. No combined score. |
| Model evidence claims | Market claims reference constrained existing analysis IDs and copy validated source quotes. Context claims reference inspected retained content and exact substrings, tagged supporting/contradicting. Imported assessments cannot masquerade as primary claims. |
| Alternatives | Only referenced inspected repository/product records, with reasoning about contribution versus new work. No invented repository name/URL accepted as an alternative reference. Uninspected capabilities cannot become sourced facts. |

Context `evidence_identity` prevents repeated identical source/revision/content
from being counted as separate corroboration in model inputs. Import lineage is
preserved. No context/profile artifact enters deterministic job-market counts.
Source claims, classifications and model proposals remain distinct. Free-form
proposal prose still needs semantic human review; string/quote validation cannot
prove it contains no misleading inference. Nothing is automatically accepted,
published or used as observed commercial/content success.

## Acquisition limits

`context-acquire` fills an empty-record request skeleton. Before I/O it records a
pending attempt and validates the policy. It rechecks policy before each item and
before commit. HTTP performs only the explicit reviewed public HTTPS request,
with no credentials, environment proxies, redirects, browser-header retries or
fallback URLs. HTML becomes labeled `html-text/1`; plain UTF-8 is retained directly.
A response is limited to 60 KB, ten items per request and 20 seconds per HTTP read.
DNS addresses are checked for public routing; this is not a network sandbox or a
DNS-rebinding isolation guarantee. Enable this path only for reviewed destinations.
Source-specific frequency/terms requirements remain part of the review; paths
requiring unsupported enforcement cannot be enabled via a permission assertion.

Repository acquisition reads exact `COMMIT:relative-path` Git objects, bounded to
60 KB each. No clone, checkout, dependency install, test/script execution or hooks.
Object replacements are disabled; partial/promisor repositories are rejected to
avoid implicit materialization. Test-file inspection is explicitly not a test
run. Capturing a README alone does not validate code behavior or all alternatives.
Publication dates stay unknown unless a reviewed import supplies actual dates.
Failed access is an unavailable context receipt, never proof a source closed.

## AI Trend Radar import

The read-only converter implements the inspected schema `3.0` shape in
`src/ai_trend_radar/developer_reports.py`: scan ID, generated time, recommendations
and watch topic IDs/revisions, quotes, source links, source event-time metadata,
assessment status and caveats. It reads **only the selected JSON report file**;
no database, runtime, dependency, source execution or repository writes. It does
not need AI Trend Radar installed. Unsupported versions and missing selected
IDs are rejected. Full interchange/outcomes remain P4.

The policy must cover the selected report content **and its third-party excerpts**;
report ownership does not establish those rights. Imported statements remain
`imported-assessment`, with original source links and report digest/revision.
Source event-time values/bases are preserved as imported metadata, not upgraded
to independently verified publication dates. Generated time and the YouTube
appendix cannot validate freshness or audience demand. Missing rights reject the
import; missing primary content/dates produce explicit limits. To corroborate a
claim, separately inspect and capture the permitted original source.

## Workflow-specific review

- Learning: direction fit, prerequisites, practical exercises, completion checks,
  and deepening known skills; no automatic claim of missing ability.
- Project: actual user/problem, inspected alternatives and contribution option,
  bounded architecture/deliverable, trade-offs, tests/baseline/benchmarks/held-out
  failures, demonstration limits, effort/hardware/cost/maintenance/license
  assumptions. Without repository alternatives, abstain or choose no project.
- Product: explicitly hypothetical buyer/workflow/workaround/pain, differentiation,
  support and contradiction, job-evidence limits, validation and success/rejection
  criteria. Without inspected problem/product context, commercial judgment is unknown.
- YouTube: proposed problem/build/trade-offs/test/failure/fix/useful-artifact story,
  reproducibility and separate audience validation. Without inspected dated
  discussion/trend evidence in the declared **90-day review window**, video
  suitability is unknown. This conservative window is a review policy, not proof
  of freshness or audience demand. Old material remains historical context.

All sections are labeled model proposals. Numeric effort/benchmark targets are
assumptions or proposed acceptance criteria, never observed results. Outreach,
publishing, customer experiments and external writes need explicit authorization.

## Cache, lifecycle, privacy and maintenance

Reuse P2 policy traversal, qualified runtime and atomic store. Every input must
permit hosted processing; profile privacy restrictions apply as well as source
permissions. Check again after worker startup and before commit. A changed
snapshot/context/profile/prompt/schema/validator/runtime or date changes the cache
key. Date inclusion makes the discussion review window explicit. The existing
100 KB worker input/output and 90-second turn budget still apply; oversized inputs
must be narrowed explicitly, not silently truncated. No automatic paid fallback.

Brief executions, rejected responses, drafts, profiles and context all inherit
source expiry/withdrawal. Deleting context invalidates linked drafts/profiles;
removed market evidence invalidates snapshots and their drafts. Context content
hashes and original imported-quote fingerprints prevent reuse through a new report
wrapper; exact shared quotes also withdraw related retained imported copies.
Paraphrased/evasive reimports and manual store replacement are outside this exact
identity mechanism. No unmanaged export, restore, hidden duplicate archive or
physical erasure claim. P6 adds scheduled cleanup/recovery; current unsupported
retention deadlines remain blocked.

## Completion scenarios

`python3 -m tools.evaluate_decisions` explicitly runs two live owned-fixture
scenarios using the qualified subscription worker: an already-known retrieval
capability that should receive deeper practice, and a project request with no
inspected alternatives that must abstain. It uses a separate private child store
`phase3-evaluation`, never the real corpus or user profile. Its synthetic profile
review is fixture setup, not a human evaluation claim. Inspect a resulting draft
by setting `AI_JOB_RADAR_HOME` to that child directory and using `inspect --id`.
No scenario result establishes market demand or the user's demonstrated ability.

New project drafts must distinguish existing behavior from a concrete addition.
If selected inspection does not establish a worthwhile gap, no-project or
insufficient-evidence is the correct result. Reproducing existing behavior may be
useful learning practice but must not be sold as a new contribution. The brief
prompt enforces this as an instruction; human semantic review remains necessary.

## Phase 4 integration

[Outcome operations](outcome-operations.md) now provide decisions, correction
history, recommendation memory, scoped outcome-to-profile proposals and neutral
reviewed interchange. P3 native schema-3.0 Radar conversion is unchanged. New
briefs add revision links and optionally selected `--exchange` assessments;
old artifact IDs remain addressable. Generic export is still blocked. Only P4's
exact reviewed projections with compatible source permissions can be released.
Human-review status is independent of implementation/commit authorization.
