# Skills → learning → building → teaching

The delivery plan is [PLAN_LEARN_BUILD_TEACH.md](../../PLAN_LEARN_BUILD_TEACH.md).
It extends the active seven-phase roadmap using the existing Python helpers,
qualified worker, context acquisition, private manifest and managed report pair.
No new database, web server, embedding provider or paid dependency is required.

## The practical workflow

Use the existing Python environment and a matching qualified Codex binary. A newer
CLI is not automatically qualified. If an already-installed binary matches the
recorded version and hash, select its `bin` directory on PATH for these commands
and run qualification; do not change the global CLI installation or bypass the
hash check. Installed-runtime qualification and live model success are separate.

```sh
.venv/bin/python -m tools.research_evidence qualify
.venv/bin/python -m tools.research_ops learn-refresh --limit 20
.venv/bin/python -m tools.research_decisions skills --days 30 --basis capture
.venv/bin/python -m tools.research_decisions learning-inspect --id SKILL_SNAPSHOT_ID
.venv/bin/python -m tools.research_decisions path-propose --snapshot SKILL_SNAPSHOT_ID --skill python --skill rag --context REVIEWED_RESOURCE_ID --context REVIEWED_REPOSITORY_ID
.venv/bin/python -m tools.research_decisions path-select --id PATH_ID --reviewer YOUR_NAME
.venv/bin/python -m tools.research_decisions path-briefs --id PATH_ID
.venv/bin/python -m tools.research_decisions progress --input /private/observed-work.json
.venv/bin/python -m tools.research_ops report --limit 1000
```

Choose actual skill IDs from the snapshot; the examples above do not claim that
Python/RAG are the user's best next skills. Optional `--profile` uses an already
reviewed research profile. Missing profile evidence is not missing ability.

`learn-refresh` collects no jobs. It reuses the P6 operations ledger and processes
at most 20 current observations per invocation, prioritizing earlier description-verified
AI roles while keeping every other latest observation queued, creating skill analysis, a snapshot
and reports. The run returns its queue/overflow status. Continue explicitly with a
new invocation after a successful batch. Use the existing `--plan`/`--resume` and
`resolve` controls for interrupted runs; prior failed/ambiguous calls are not
automatically retried. Existing v1 operation plans retain their semantics; set
`skill_details: true` in a reviewed AI operation plan to use the new extraction.
Unattended activation still needs its separate qualification.

The two HTML files remain in Git-ignored `reports/`. `projects.html` opens on
My learning path, with Skills, Projects, YouTube and Progress tabs. With no selected
path, it shows at most three available options; selecting one foregrounds that
effort. Static controls only browse. Tell Codex to select/record and regenerate
the reports; there is no browser persistence or implied completion.

Historical standalone learning briefs remain readable until replaced by the
connected path view. Product hypotheses remain secondary report evidence and
remain available through the existing inbox/inspection commands.

## Contracts and compatibility

| Contract | Meaning and required boundary |
|---|---|
| Analysis v2 | Existing claims/domain/responsibility fields plus `skill_mentions`. Exact `surface`, `quote`, optional exact `section_context`, kind and modality are model extraction; code assigns character spans and catalog aliases. v1 readers remain supported; the detailed view labels missing/legacy analysis explicitly. |
| SkillCatalog v1 | Maintainer-authored IDs, labels, definitions, typed exact aliases and broad capability relationships. It is terminology, not hiring evidence. Unrecognized phrases get stable unresolved IDs. No model-controlled merge. |
| SkillMapping v1 | Explicit reviewer/reason, source analysis IDs, source skill ID and target catalog ID of the same kind. It inherits those analyses' lifecycle. Global phrase equivalence is a review assertion, not an automatic embedding match. |
| SkillSnapshot v1 | Explicit half-open window, date basis/filters, current-in-window revisions, distinct-opening denominators, modality counts, verified identities versus reported names, co-occurrences and exact evidence references. Original observations are immutable. |
| LearningPath v1 | Skill and scoped market snapshots, selected skills, one experiment, ordered milestones, self-checks, inspected resources, effort assumptions, teaching question, limits and optional reviewed profile. It is a draft. |
| LearningSelection / LearningDecision v1 | One active selection; rejected/deferred/duplicate/archived decisions carry actual operator reasons. Matching rejected/duplicate or not-yet-due skills cannot be regenerated as a fresh path. Decisions are not success ratings. |
| LearningProgress v1 | Explicit path hash and milestone, event, self-reported/observed basis, observer/date, summary, conditions, capability claims, retained result contexts/quotes, policy and optional correction ID. No model-inferred progress. |
| EvidenceAnswer v1 | Deterministic counts or a bounded cited explanation, input snapshot, question, retrieval basis and limitations. Explanation prose is pending semantic review; numeric aggregation stays in count mode. |
| LearningIntent v1 | Durable input/version/cache identity before inference, with exact supplied inputs under the same source policies. An unresolved earlier intent needs an explicit `--retry-review` reason before another model attempt. |
| LearningFailure v1 | Bounded failure stage, model response when returned, execution metadata and intent dependency. It inherits input retention/withdrawal and never counts as a recommendation. |
| PathBriefIntent / PathBriefResult v1 | Intent and completion for each half of the linked project/video pair. Reuse completed briefs for unchanged progress; interrupted work requires an explicit retry reason. Both inherit path and work-evidence lifecycle. |

Detailed extraction is additive and explicitly selected (`skill_details=True` in
the Python API). Existing API callers and other domain workspaces retain v1
behaviour. The fine-grained catalog and learning path workflow are currently
AI-specific; backend workspaces retain their existing four workflows.

Skill kinds are practice, knowledge, technology and other-requirement. Immigration
and compensation tokens are not technical skills. Unknown phrases are visible,
not silently discarded. Catalog matching does not prove semantic correctness,
and section/source matching alone cannot detect every negated or misclassified
requirement. Use held-out review before interpreting quality targets as results.

## Windows and evidence questions

```sh
.venv/bin/python -m tools.research_decisions skills --days 30 --basis publication
.venv/bin/python -m tools.research_decisions skills --days 30 --source jobicy --responsibility applied
.venv/bin/python -m tools.research_ops report --limit 1000 --days 30 --basis publication
.venv/bin/python -m tools.research_decisions skill-history --days 30
.venv/bin/python -m tools.research_decisions ask --snapshot SKILL_SNAPSHOT_ID --question 'How often is Python requested?' --intent count
.venv/bin/python -m tools.research_decisions ask --snapshot SKILL_SNAPSHOT_ID --question 'What work involves retrieval?' --intent explain --skill rag
```

The default is observations captured within 30 days. A publication slice uses
known publication dates and excludes descriptions captured after the historical
window endpoint. Neither means newly opened positions or market growth. Unknown
publication dates never fall back to discovery dates. Last-month observations
include closed/historical jobs where retained use is permitted; they are not an
active-vacancy count.

Skill history produces two adjacent descriptive windows with no change badge.
The existing P5 `cohort` accepts adjacent 30-day windows as well as existing
28-day definitions; `compare` enforces complete stable collection and compatible
analysis before emitting its existing capability changes. Capped Jobicy receipts
remain partial. More elapsed time cannot make them complete.

Counts query the entire selected skill snapshot. Explanations use lexical matching
plus exact catalog aliases, at most one quoted example per opening, and a bounded
qualified worker. Citations point to actual captured descriptions. Retrieval is
not an exhaustive count or proof of employer independence. Missing matches return
insufficient evidence without a model call. `--intent recommend` routes to choosing
skills for the learning path workflow. `auto` only recognizes explicit count
phrases; the response records its interpretation and explicit intent overrides it.

Embedding retrieval is conditional on a useful held-out improvement under the
existing budget. No embedding index or paid model is enabled by this workflow.

## Recording work and corrections

Progress input fields are `schema_version:1`, `path`, `milestone`, `event`, `basis`,
`summary`, `observer`, timezone-aware `occurred_at`, `evidence`, `conditions`,
`capabilities`, `result_quotes`, nullable `supersedes`, and a reviewed `policy`.
Events: attempt, self-check, implementation, test, failure, lesson, correction, completed.
Only an explicit completed event advances the suggested next milestone; passing a
test never silently records completion or accepts a capability profile.
Self-reports stay self-reported. Observed records require reproduced experiment
contexts, exact result quotes and conditions no broader than those contexts.

Only independently attributable user work belongs in progress summaries under an
own-work policy. Do not paste restricted job prose into an unrelated policy.
The path association is a hash, not a copy of its market argument. Progress depends
on its own policy and inspected work, so market withdrawal removes the path and
its claims while independent work can survive. Withdrawing the work itself removes
its progress/proposal descendants. Existing P4 outcome records remain unchanged.

`progress-profile --id PROGRESS_ID` proposes only explicitly recorded capabilities
under the observed conditions. It does not accept a profile; use existing actual
`profile-review` after inspection. Correcting that progress retracts dependent
profile proposals/reviews. A failed experiment or green test suite is not automatic
evidence of general mastery; capability/result alignment still needs review.

## Evaluation

`python -m tools.evaluate_skills --input /private/heldout-labels.json` scores a
bounded set of detailed analyses against explicit exact-surface/type/modality
labels. Supply a dataset revision, reviewer, provisional/human-reviewed label basis
and held-out examples. Unknown provenance or preliminary labels must stay
provisional. Freeze labels before examining model outputs; record the process.
The evaluator reports errors and proposed precision/recall targets (95%/85%); it
cannot authenticate the review assertion or manufacture semantic approval.

`path-compare --id PATH_ID` generates a straightforward-prompt baseline from the
exact frozen path inputs/preferences and the same schema, runtime and policy
checks. It is stored separately from recommendations. Compare both with the
existing standalone briefs on that scoped market snapshot. Human review should
cover usefulness, prerequisite order, effort, existing-project consideration,
repetition and unsupported content/commercial claims. Record actual outcomes
separately from model judgments. Owned unit fixtures are not market/model results.

Detailed extraction and learning-path synthesis permit a bounded 240-second worker
turn; extraction emits both legacy requirements and typed mentions, while paths
include ordered milestone contracts. Linked project/video synthesis uses the same
240-second budget; unrelated legacy briefs retain their existing budget. Explanatory answers retain the shorter
existing worker budget. Runtime, schema and source gates are
unchanged. Rejected responses remain in managed source-dependent execution
records for diagnosis; source withdrawal removes them. Operator retry invalidates
local snapshot/report steps so resumed analysis cannot leave the old view cached.

The extractor receives the maintained catalog's type guidance, which is terminology
and cannot establish that a job requests a skill. Path inputs preserve full counts
but supply at most two evidence examples and twenty co-occurring counts per chosen
skill. These limits are saved with each path. An abstained path may have no milestones;
the report requests more evidence and does not show completion or permit selection.
`path-briefs` resumes a partially completed pair: it reuses an existing brief for
the same path/progress and requires `--retry-review` for an unfinished attempt.
New progress changes that basis. Explicit `--refresh` requests reassessment of
otherwise unchanged evidence; refresh does not convert old context into fresh evidence.

See [implementation validation](learning-validation.md) for executed checks and
the remaining human evaluation and coverage gates.
