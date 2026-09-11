# Domain workspaces (Phase 7)

AI engineering remains the default. Phase 7 adds one explicit opt-in pack for
backend/platform engineering, using the existing collection, extraction, four
briefs, profile/outcome, coverage, lifecycle and operations helpers. It does not
create another collector, model runtime, application architecture or repository.

## Select a workspace

Inspect the public pack before selecting it:

```sh
python3 -m tools.research_domain packs
```

The reviewed pack lives in `docs/research/domains/backend-platform-v1.json`. Its
independently versioned taxonomy has eight capability IDs: service/API design,
data storage, distributed systems, delivery automation, service reliability,
platform security, performance/capacity and developer platforms. Responsibilities,
exclusions, aliases, prerequisite edges, candidate queries, frozen evaluation
revision and limitations are part of the pack. Aliases guide normalization; they
are not evidence that a description explicitly requires a capability.

Choose an **empty private data directory outside Git**, not another development
checkout. For example:

```sh
export AI_JOB_SKILLS_LAB_HOME="$HOME/Library/Application Support/ai-job-skills-lab/backend-platform"
python3 -m tools.research_domain init --pack backend-platform
python3 -m tools.research_domain status
```

This is an explicit persistent opt-in. It cannot retag an existing AI corpus or
change a workspace's pack revision. The default AI directory is reserved even
when empty; non-AI selection requires a different data directory. Ordinary commands use that directory's pinned
binding; they do not select a domain by title, user profile or source keyword.
Unset `AI_JOB_SKILLS_LAB_HOME` to return to the original default AI data directory.
Application commands and their candidate trackers remain unchanged.

A non-AI workspace adds `domain_pack` to the version-1 state envelope and an
independent private `domain-binding.json`. Both must match by domain ID, version,
pack digest and taxonomy revision. A missing/corrupt binding fails closed rather
than interpreting remaining records as AI. Emptying or withdrawing all evidence
does not remove the domain binding. Existing unbound AI manifests remain valid;
no historical artifact or taxonomy is rewritten. Use a new empty workspace for a
new pack/revision and recollect or explicitly import permitted evidence there.
There is no automatic corpus copy or policy upgrade.

## Use the complete research loop

The existing commands apply without a separate command tree:

1. Review acquisition permission and source limitations, then use
   `research_evidence import` or explicit `collect`. Backend collect's omitted
   query defaults to the pack's first candidate query; AI keeps `machine learning`.
   All providers still use their existing gates. Jobicy's capped remote-biased
   feed is not complete backend coverage; no new provider is enabled.
2. Run the existing runtime `qualify` in the selected workspace before automated
   extraction, then `analyze --id OBSERVATION_ID`. The same pinned subscription
   worker has an empty tool registry. Domain scope and capability IDs are passed
   as data; no pack path can execute code. Backend output uses `domain_fit`, not a
   misleading `ai_domain` field. Exact quotes, modality, unknowns and applied versus
   research-heavy classification use the existing validator and source policies.
3. Generate `snapshot` or P5 `coverage`. Source identity, deduplication, freshness,
   historical/active-vacancy distinction, countries/languages and completeness
   remain independent of domain eligibility. Explicit out-of-domain source claims
   remain inspectable; automated capability aggregates include in-domain analyses.
4. Use the existing P3 `research_decisions brief` commands for learning, project,
   product and YouTube drafts. Their schemas and prerequisite validation use the
   workspace taxonomy. The pack's prerequisite graph is guidance, not proof of
   personal ability. Repository alternatives, problem/pain evidence and dated
   discussion requirements still apply; absent external evidence produces limits,
   hypothetical judgments or abstention. Four dimensions never become one score.
5. Use P4 decisions, inspected outcomes and reviewed profile proposals. Backend
   capabilities cannot enter an AI profile by adding a keyword. A declaration is
   not demonstrated ability; source/correction withdrawal still retracts drafts
   and affected profile evidence. Feedback stays in the selected workspace.
6. P6 `research_ops` runs, inbox, offline HTML, managed rollback, scheduling and
   optional notifications retain their controls. Incremental analysis checks the
   pinned domain taxonomy/schema/prompt along with existing code/runtime versions.
   No schedule, account authorization, notification or publication is activated
   by selecting a domain. Use explicit source/query/model settings in an operation
   plan; the pack does not execute a collection plan on its own.

The AI prompt, default output schema and default aggregation output were checked
against executed functions from committed P6 `09bc20d` using owned fixtures.
Default source filters and application eligibility behavior are unchanged. Shared
helper code hashes change with this implementation, so future AI analysis/brief
invocations may legitimately invalidate a cache; old captured results remain
historical, not automatically reclassified or silently relabeled.

## Compare domains without claiming relative market demand

```sh
python3 -m tools.research_domain compare \
  --other-home /absolute/private/ai-workspace \
  --from 2026-09-01T00:00:00Z --to 2026-09-09T00:00:00Z
```

Use an elapsed time window (`--to` must not be in the future). Both stores are
locked in stable path order and swept before a comparison is returned. Results
include each pack revision, sample scope (including synthetic versus historical),
queries/filters/receipts, period, sample/employer/opening counts, segment coverage,
missing descriptions, analysis versions, source health and limitations.

This is **descriptive local inspection**, not relative demand, growth or a common
cohort claim. Taxonomies differ; capability counts cannot be summed or compared
as interchangeable concepts. Shared conservative opening IDs reveal some overlap;
unknown cross-source identity can hide more. A role may solve problems in both
domains. Pooled opening counts and demand ratios are deliberately null. P5's
stable-source/time-window tests remain required for any longitudinal analysis.

The comparison is not stored or copied into either workspace, so cross-store
withdrawal obligations are not bypassed by a cached derivative. Do not redirect
restricted local inspection to an unmanaged report/export. A future durable
cross-workspace report would require an explicit shared-lifecycle contract or
compatible export permission; no such permission is inferred from collection.

## Interchange and recovery

AI's neutral `radar-interchange/1.0` remains unchanged. Non-AI exports use the
explicit `radar-interchange/1.1` extension with an exact domain reference in JSON
and its matching Markdown companion. Release/import require the receiving
workspace's matching pack digest and taxonomy revision. Unknown or mismatched
versions fail closed. Existing export permissions, no-recall restrictions,
profile exclusion, origin identity, source lineage and exact-preview approval
remain mandatory. Importing a matching assessment never creates observed work,
a market observation or demonstrated capability.

AI Trend Radar is still separate and has not been modified. Its native reviewed
report import remains context; its consumer would need separate reviewed support
for the 1.1 domain extension. Do not downgrade a backend bundle to 1.0 to force an
import, or relabel an AI assessment as backend evidence.

P6 backup/restore retains the pack header and checks the independent binding
before committing restored state. A foreign AI backup cannot rebind a backend
workspace. Withdrawal still invalidates source-derived artifacts and managed
copies. Keep domain binding, withdrawal journal and operations ledger current;
never restore or downgrade them from an older copy to make recovery pass.
Unsupported physical deletion deadlines and unmanaged copies remain unsupported. Each workspace has its own withdrawal ledger. When a source removal
applies to material held in multiple workspaces, withdraw it in every affected
workspace; never use a new workspace to bypass a prior withdrawal. There is no
automatic global deletion registry or cross-workspace corpus replication.

## Evaluation and further packs

The backend dataset has twelve author-owned cases, frozen before model runs,
covering the eight capabilities, research-heavy work, adjacent AI work, missing
text and an embedded malicious instruction. Labels are provisional. In an empty
**owned evaluation** workspace, initialize the pack, run the existing `qualify`,
then `python3 -m tools.research_domain evaluate`. This sends only those owned
fixtures through the real shared extractor and all four brief workflows. It
refuses a real-job corpus, checks the dataset digest, versions the execution and
caches matching completed cases. A runtime/quota failure stops the evaluation
batch; no paid or local-model fallback is attempted.

Behavioral tests additionally cover invalid quotes, taxonomy mismatch, immutable
bindings, foreign restores, all four bounded briefs, profile/outcome controls,
cross-domain disclosure and permission-gated interchange. The baseline fixture
records hashes from committed P6 implementations, not expectations recomputed
from the modified code. Actual results and remaining human review are in
[Phase 7 validation](phase7-validation.md).

Targets for promotion are a larger held-out employer-diverse corpus, reviewed
extraction accuracy, useful/feasible/nonrepetitive briefs and justified existing-
project contribution choices under the roadmap's evaluation criteria. Twelve
synthetic examples and structural checks do not meet those targets. More packs
require reviewed scope, independent versioned taxonomies, meaningful prerequisite
checks, licensed/permitted fixtures and their own human evaluation. Add reviewed
JSON/catalog entries and tests; do not import arbitrary executable plugins or
expand the default AI experience silently.
