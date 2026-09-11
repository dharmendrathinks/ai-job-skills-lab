# Phase 5 implementation and validation — 2026-09-09

Phase 4 was committed locally as **`ff5babf`** before this work. Phase 5 was
implemented on `research/phase5`, in the same required `ai-job-skills-lab` folder.
No new worktree, dependency installation, JobSpy integration, provider data
subscription, extra model spending, publishing or push occurred. AI Trend Radar
and upstream application workflows were not modified.

## Inspected foundation and source decisions

The implementation reuses `tools/research_evidence.py:aggregate` and `Store`,
unchanged upstream `tools/rank_state.py:save_state`, P3 context/brief contracts,
`tools/evaluate_research.py` scoring, and the pinned qualified Codex worker.
The inspected upstream `.claude/commands/add-portal.md` and
`.claude/skills/job-scraper/SKILL.md` supply reconnaissance, bounded testing and
honest health-status conventions. Research keeps permission before probes; it
does not inherit a personal-use exception to blocked automated collection.

[`source-registry-v1.json`](source-registry-v1.json) covers all 16 candidates.
Fresh documentation inspection revisited these primary references on 2026-09-09:

- [Freehire terms](https://freehire.me/terms): documented API boundary and listing
  uncertainty; intended retained/hosted research use remains unresolved.
- [Lever postings API](https://github.com/lever/postings-api): global/EU board GET,
  pagination and public-posting access; independent retained/hosted research scope
  still needs qualification for the selected employer boards.
- [Greenhouse board API](https://docs.greenhouse.io/job-board.html) and
  [Ashby public posting API](https://developers.ashbyhq.com/docs/public-job-posting-api):
  API shape does not establish all independent-use permissions.
- [Himalayas API documentation](https://himalayas.app/docs/remote-jobs-api): intended
  researcher/AI use and public endpoints; a remote feed alone does not fill the
  onsite/employer-authority gap. Any additional capture needs its specific policy
  and incremental-value validation.

Other records explicitly carry forward the earlier audit and its limitations;
no new terms, authentication, freshness or health result is claimed for them.
Only the existing Jobicy path is go-limited under its unchanged P2 policy, whose
review expires 2026-10-09. No new adapter was promoted; conditional source work
is not required to deliver unrelated Phase 5 mechanisms.

## Actual retained sample and time-window result

The new coverage workflow inspected the existing 20 Jobicy observations:

| Measure | Observed value |
|---|---:|
| Deduplicated captured openings | 20 |
| Verified employer domains | 0 |
| Missing descriptions | 0 |
| Analyzed descriptions | 6 |
| Country / language / availability unknown | 20 each |
| Remote arrangement | 20 |
| Full-Time / Part-Time source labels | 19 / 1 |
| Human-accepted translations | 0 |

These are sample/metadata results, not 20 validated AI roles, currently open
vacancies, or worldwide demand. Source-reported seniority values also remain
visible. Lists such as employment types are counted without increasing the
opening denominator. Selected country/language gaps mean unrepresented or
unreviewed labels, not evidence that those markets lack jobs.

Managed coverage ID after the current projection integration:
`7c545bba7e983dab807d57b2d1eadf3090d06fde569892ab05b15332c468febb`.
The selected-gap example is
`43a3248ce70e9a7c7088d5982e8236d2703a60e5bdaac33f399b0115bf6a5614`.
Reports are immutable observations of that implementation version/time; regenerate
for current state rather than overwriting them.

A real cohort definition used two elapsed adjacent 28-day windows and the retained
Jobicy protocol. Its capture remains explicitly partial, not a complete/fresh
inventory. Comparison `c50ee385e25591cda8b098f45c804e2a19b56e5d91a014c1a64d34164bec9c90`
returned **insufficient-longitudinal-evidence**, with **null opening delta** and
missing cadence slots in both windows. The definition does not invent historical
captures. No new provider call was needed or made for this assessment.

## Live translation and its limits

The same P2 hosted-use policy and qualified `codex-cli 0.153.4` / `gpt-5.5` worker
processed one retained 2,357-character description into a proposed Hindi
translation. The source language is asserted English for that request; this did
not become a reviewed corpus language label.

Three manually invoked development checks occurred across contract fixes; there
was no automatic retry/fallback loop. The first was deferred with limited failure
diagnostics. The second retained a model response with correct indexed segments
but an empty limitations list, rejected by an overly strict validator. Code now
adds the invariant human-review notice itself rather than requiring the model to
invent a limitation. The third passed alignment validation:

- Proposal: `d6ecda16554c2e4c2696131c210191695cbb15fdfc58987f262323b9f6deb77c`.
- Two indexed segments preserve all 2,357 original code points and exact offsets.
- Status: **pending-human-review**. No review was accepted or source/profile changed.
- Recorded successful-call latency: **76.286 seconds**; reported tokens: **1,601**
  (815 input, 786 output). These are one successful call's metrics, not total
  development usage or a reliable latency/cost distribution.
- Prompt hash: `4c8cacfdf2b33ee0f5ef412bc4e8c788730b681a339ba140962a7af4377d8096`.
- Validator hash for that execution: `b620f6993979ac16cc34f1fcb310146a5f64cfcfa888fba5028c19035e85e381`.

Source/translation/failure data stays in the existing private manifest with P2
expiry/withdrawal dependencies. The unchanged worker's active tool-boundary test
was not rerun; its prior qualification matched. Successful alignment proves the
model interface worked, **not Hindi fidelity**, full semantic translation,
new-language extraction quality or readiness for automatic language promotion.

## Behavioral evaluation

`tests/test_research_global.py` adds 24 owned-fixture tests. Coverage includes:

- Full candidate inventory; revision/deduplicated opening counts; missing segments
  and source-health reporting; multi-valued source labels and original-text retention.
- Sufficient equal-window fixture comparisons, separate added-source coverage,
  and insufficiency for absent sources, missing slots, changed query/schedule,
  stale/partial/failed captures and withdrawn observations.
- Publication unknowns never use discovery dates; model versions resolve through
  execution artifacts and incompatible versions suppress capability deltas.
- Reviewed board ownership/requisition lineage; two 24h-separated complete board
  absences versus capped feeds, outages and one absence; transitive withdrawal.
- Readable Unicode review without terminal control execution; indexed translation
  cache, omission/withdrawal rejection, exact long-text chunk
  preservation, empty model-limit handling, and accepted/rejected review isolation.
- Language-specific frozen labels, existing atom scoring, recorded held-out order,
  duplicate/version control and lifecycle invalidation. The four owned multilingual
  examples resolve exact original spans but remain provisionally labeled, with
  human language review pending.

`tests/test_research_decisions.py` adds a coverage-to-brief integration test:
P3 consumes the P5 evidence slice and its period/segment limits. Preflight checks
also cover coverage/comparison/translation readiness without runtime writes.
No fixture score is reported as actual model/human performance. There is no new
claim that the pending P2/P3 quality targets have been achieved.

## Remaining evidence and next phase

New provider permission and measured incremental value; human translation and
multilingual gold-label review; broad extraction/recommendation usefulness; and
actual comparable 28-day histories remain unestablished. The implementation
keeps those as explicit conditional gates. Phase 6 can use the completed
protocol/cohort interfaces for operation and scheduling without waiting for all
providers or silently pretending the missing evidence exists.

## Final PR readiness

The required deterministic analyzer returned **PR READY** against `ff5babf`.
It ran **549 tests: 548 passed, one opt-in live-boundary test skipped**. Skill
lint and security guards passed; no suspicious files or blockers were detected.
Build was skipped because no build command is configured. CLI help and read-only
coverage preflight also passed. The full local result is in ignored
`.tools/validation/phase5-pr-ready.md`.

Phase 5 changes are staged, uncommitted and unpushed. The Phase 4 commit requested
at the start is `ff5babf`. This status does not imply human quality acceptance or
promotion of a conditional provider/language.
