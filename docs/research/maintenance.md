# Foundation, privacy and maintenance

## Repository transition

Development uses only `/Users/dhasharma/Dharmendra/Projects/ai-job-skills-lab`.
`origin` is `https://github.com/dharmendrathinks/ai-job-skills-lab.git`; GitHub
inspection initially found it private, empty, and not a GitHub-network fork. `upstream`
is `https://github.com/MadsLorentzen/ai-job-search.git`.

Local branch `research/phase1` starts from approved commit
`8c81edc330b98db0473dcb016e34db835c2fd378`, preserving its ancestry and files.
No GitHub fork was created and no visibility changed. After explicit approval,
Phase 1 commit `d102a88` was pushed to `origin/main` on 2026-09-08. Subsequent phases were implemented on `research/phase2` through
`research/phase7` in this same checkout; P7 is committed as `10e2ae3`.
The v0.1.0 release integrates that history into `main`. Origin remains private.
The temporary sibling checkout used during transition was moved here and its
empty directory removed at the user's request; it is not a second workspace.

`PLAN_RESEARCH.md` remains active. Original `PLAN.md` is unchanged local history,
ignored from publication (original SHA-256:
`870e78df2bf0938c9aaf9ad7cdaaf69dadee97f332db50f9b7cf1a9bbc3c6fde`).
The upstream MIT terms and Mads Lorentzen copyright are preserved; the release
adds attribution for AI Job Skills Lab additions. README attribution links to the original application guide; upstream
author results are not presented as this research fork’s evaluation. No AI Trend Radar or JobSpy source was imported.

## Public template and private data

`research_preflight.py` is read-only. It resolves the macOS default
`~/Library/Application Support/ai-job-skills-lab`, with `AI_JOB_SKILLS_LAB_HOME` as an
absolute override; non-macOS defaults use XDG data storage. It rejects overlapping
checkout paths, including symlink aliases, and does not create the destination.
P2 owns actual private persistence and restrictive file creation permissions.

`research-template-manifest.json` contains reviewed public-template hashes.
Preflight checks both disk and index, so retaining placeholder tokens or
restoring a staged file's worktree does not hide personal content. Tracked files
matching ignore rules fail the guard. CI enforces this even on a private origin.
These are supported-entry-point and review checks, not OS write prevention or
a complete secret scanner. Review staged exports and the manifest itself.

Application `/setup`, including `--section`, and `/expand` stop before personal
collection/writes in this publishable template. Personal application onboarding
requires a separately reviewed private workspace, outside the development
checkout, with public pushing disabled. It is not created or configured in P1.
Do not bypass this by deleting the manifest, refreshing its hashes to personal
content, or adding tracked profiles to `.gitignore`. Existing application ranking,
fit rules, templates and tools are retained; this setup restriction is explicit.

When upstream changes a protected methodology file, inspect the content and
update the reviewed hash list only for accepted public template revisions.
There is intentionally no automatic rebaseline command. Two CLAUDE.md hashes
allow the original upstream header and the reviewed fork routing header only.

## Divergence and synchronization ledger

| Area / relevant paths | Fork decision and review requirement |
|---|---|
| `AGENTS.md`, `CLAUDE.md`, `.agents/skills/research/SKILL.md`, `.claude/skills/research/SKILL.md` | Early mode routing with one canonical specification; AGENTS version bumped. Review instruction precedence and runtime discovery after merges. |
| `.claude/commands/setup.md`, `.claude/commands/expand.md` | Explicit public-template preflight before every personal-write path; retain application workflow below the gate. |
| `.claude/skills/job-scraper/SKILL.md` | Research route before state loading; portal discovery requires a CLI manifest/entrypoint. Ordinary scrape selection remains upstream. |
| `tools/research_preflight.py`, `research-template-manifest.json`, `tests/test_research_preflight.py` | Fork-owned read-only state-path, template/index and capability checks. No collection, extraction or persistence implementation. |
| `tools/research_evidence.py`, `tests/test_research_evidence.py` | Additive reviewed imports, validation, deterministic snapshots and lifecycle controls. Directly imports unchanged `tools/rank_state.py:save_state`; retain upstream behavior and run both test suites when synchronizing. No portal source fork or second workflow tree. |
| `tools/research_runtime.py`, `tools/research_analysis.py`, `tests/test_research_runtime_live.py`, `tests/test_research_runtime_protocol.py`, `tests/test_research_analysis.py` | Qualified subscription worker, execution/cache/validation and adversarial tests. Runtime upgrades fail closed; inspect pinned source and rerun active qualification before source disclosure. Apache-2.0 provenance for the runtime adaptation is preserved in `THIRD_PARTY_NOTICES.md` and `licenses/Apache-2.0-Codex.txt`. |
| `tools/research_sources.py`, `tools/evaluate_research.py`, `tests/fixtures/research/`, `docs/research/prompts/` | Thin Jobicy source path and shared-store comparisons; preserve policy restrictions, frozen prompt/dataset identities and honest human-review status. No provider code, dependencies or second command tree replaced. |
| `tools/research_context.py`, `tools/research_profile.py`, `tools/research_briefs.py`, `tools/research_decisions.py`, `tests/test_research_decisions.py`, `tools/evaluate_decisions.py` | Additive P3 contracts, selected acquisition, schema-3.0 report conversion, reviewed profile and four draft workflows. Reuses P2 state/runtime; preserve context/quote withdrawal, profile independence and constrained evidence IDs. No third-party code copied. |
| `tools/research_outcomes.py`, `tools/research_interchange.py`, `tests/test_research_outcomes.py` | Additive P4 event/revision memory and neutral projections. Reuses upstream outcome semantics and inspected Radar revision patterns, no code/database imports. Preserve old IDs, source/assessment separation, profile review, explicit export permissions and withdrawal hashes during synchronization. |
| `tools/research_coverage.py`, `tools/research_languages.py`, `tools/research_global.py`, `tests/test_research_global.py`, `docs/research/source-registry-v1.json`, `docs/research/query-packs-v1.json` | P5 extends P2 aggregate/state, P3 context/brief integration and the qualified worker. Preserve protocol/cadence/version sufficiency, board identity provenance, original-language spans and withdrawal lineage; registry entries are not permission grants. |
| `.github/workflows/ci.yml`, `.github/workflows/upstream-watch.yml`, `.gitignore` | Template/version checks active on this repository; issue reporting is manual and doubly opted in; private/dev artifacts ignored. |
| `PLAN_RESEARCH.md`, `docs/research/`, `README.md`, `.pr-ready.json` | Roadmap/contracts/runtime evidence, attribution, reproducible checks and source-path inventory; public content only. |

Keep `tools/check_upstream_updates.py` and `tools/upstream_triage.py` intact.
The first checks a limited versioned list; the second covers commits. Extend
review coverage through this ledger, not by pretending versionless research
files are recognized by the version checker. Before synchronization:

1. Fetch upstream for inspection and record its exact candidate commit; do not
   merge automatically. Work on a local integration branch in this same folder.
2. Run both existing helpers with explicit `--remote upstream` (and upstream's
   actual branch). Use `--no-fetch` on the version checker when reviewing the
   already fetched candidate.
3. Inspect changes in the ledger's paths against the approved pin, including
   versionless specs and fork-owned paths, plus any other affected upstream
   components. Review conflicts semantically; clean merges are not validation.
4. Run version/lint/security/preflight, Python regressions and touched portal
   typechecks/fixtures. Rebaseline public-template hashes only after review.
   Requalify the extraction boundary if runtime or configuration changes.
5. Keep publishing, pushes, issues and outreach behind explicit authorization.

The upstream issue workflow has no schedule. It requires manual dispatch with
`publish_issue=true` AND repository variable
`AI_JOB_SKILLS_LAB_ENABLE_UPSTREAM_ISSUES=true`. Neither was enabled here. Its retained
built-in token is scoped to this repository. Local helpers need no issue writes.

## Development checks

Python 3.13 was already installed. `.venv` uses it with PyYAML 6.0.2 for upstream
lint. Bun 1.4.2 is stored in ignored `.tools/bun-v1.4.2`; its macOS arm64 release
asset SHA-256 was checked against the official release metadata:
`90987a3a16d7db556d886ac3d551e7b6d3edf0a1cf43acaed622e8676be1d12f`.
Portal dependencies use upstream manifests, installed with `--ignore-scripts`.
No JobSpy dependency or new runtime dependency was introduced.

Use the venv Python (or activate it) for upstream lint and tests. Put the local
Bun directory on PATH as well: portal fixtures spawn `bun` by name, so invoking
the parent binary by absolute path alone is insufficient. From the checkout:

```sh
source .venv/bin/activate
export PATH="$PWD/.tools/bun-v1.4.2:$PATH"
python3 tools/lint_skills.py
python3 tools/check_framework_version.py
python3 tools/security_guards.py
python3 tools/research_preflight.py --mode research --action status
python3 -m unittest discover -s tests -t .
```

In each portal CLI use Bun for `run typecheck` and `test`. Ordinary tests use
fixtures; live collection requires source qualification. LaTeX checks remain
in upstream CI but are not a research prerequisite; P1 does not change TeX.
The release documentation review compares against P7 `10e2ae3`; the P7
implementation review compared against P6 `09bc20d`. P6
was compared with P5 `121bdcd`, and P5
was compared with P4 `ff5babf`, and P4
was compared with P3 `5d8fc8f`, and P3
was compared with P2 `29cca75`, and P2 with P1 `d102a88`. The upstream foundation remains the separate
synchronization pin. Earlier phase-only commit requests did not push their work. The authorized
v0.1.0 release pushes the integrated history to the private origin.


## Phase 6 maintenance surface

Preserve upstream `rank_state.save_state` and application HTML/report/state tools.
P6 adds `research_operations.py`, `research_ops.py`, `research_recovery.py`,
`research_delivery.py`, `research_model_eval.py` and behavioral tests in
`tests/test_research_operations.py`. `research_evidence.Store` adds a reusable lock
and recovery-journal/copy synchronization hooks; review that boundary first on
upstream merges. Run the entire P2–5 regression suite after any lifecycle change.

Read-only Radar reference inspected 2026-09-09: commit
`fc96d4865ced43f9098a9272e865e96ee603ae3f`,
`src/ai_trend_radar/slack.py` (bounded payload/destination identity/delivery intent).
No code, dependency, runtime data, webhook or SQLite state was imported. Research
uses a separate explicit-approval sender and the existing JSON helper. Upstream
`.claude/commands/html-report.md` supplies the single-file/escaping conventions;
its candidate tracker semantics and application command remain unchanged.

Keep an active P6 writer paired with its withdrawal and operations ledgers. Never
roll these back with a Git revision. Do not downgrade runtime state to the upstream
writer or restore a ledger from an older backup. Review machine-specific launchd
paths after an update; new binary/config/client/harness paths invalidate scheduled
model qualification. Generated schedules and private reports stay outside Git.


## Phase 7 maintenance surface

Review `research_domains.py`, `research_domain.py`, `evaluate_domains.py`, the
versioned domain-pack/fixture JSON and `tests/test_research_domains.py`. Taxonomy
lookup is explicit from each workspace state; never mutate global TAXONOMY or
copy the command/specification tree for another domain. Shared changes are in
analysis/brief/profile/outcome/coverage/interchange/operations helpers and Store
binding checks. Preserve the unmodified runtime boundary and source providers.

Frozen AI regression expectations were produced by executing relevant functions
from `git show 09bc20d:tools/{research_evidence,research_analysis,research_briefs}.py`
on an owned fixture. `tests/fixtures/research/ai-phase6-baseline.json` records that
origin. Update it only for an intentional, reviewed change to AI behavior.

A domain revision is not a rewrite of historical classifications. Version packs,
prompts and evaluation fixtures independently, retain their hashes, use a new
workspace for another revision and inspect both cohort definitions before a
cross-domain comparison. Missing domain bindings fail closed during access or
restore. Do not downgrade backend interchange 1.1 into AI 1.0 or assume that the
separate Radar repository implements the new consumer contract.

## Two-report presentation update

`research_reports.py` owns escaped presentation and the fixed CSP-hashed UI script;
`research_report_files.py` owns the approved ignored destination, ownership binding
and atomic file writes. Review `research_recovery.persist` whenever changing either:
withdrawal, expiry, failed writes and legacy-view migration must remove every
managed copy. Keep `reports/` ignored and untracked even on the private origin.
Corpus and credentials remain external; only generated views use this exception.
Behavioral checks live in `tests/test_research_reports.py` alongside retained P6/P7
regressions. The report update review baseline is release commit `ba9c04f`.
