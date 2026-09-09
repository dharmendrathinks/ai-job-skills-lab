# Phase 3 implementation and validation

Updated 2026-09-09. P2 was committed locally as `29cca75` on explicit request.
P3 development stays in the same checkout, branch `research/phase3`. No push,
publication, dependency install, application setup or other repository mutation.
The four-workflow implementation is delivered. **Human semantic acceptance is
pending** for P2 labels and P3 drafts; generation is not reviewer approval.

## Implemented capability evidence

| Capability | Implementation and exercised behavior |
|---|---|
| Bounded context | `research_context.py`: reviewed explicit URL or pinned Git-object requests, shared receipts, exact inspected content and limitations, strict versions, failed-attempt records and policy checks before acquisition/commit. No source-suggested destinations or code execution. |
| Read-only Radar conversion | Selected schema-3.0 report topics; preserve report/topic/source lineage and imported event-time metadata. Imported assessments/quotes cannot become newly inspected primary claims. No Radar runtime/database dependency. |
| Evidence profile | `research_profile.py`: self-declared/inspected/demonstrated/not-evidenced distinctions, proposal then explicit review, documented reproduced conditions for demonstrated levels, no keyword promotion or application writes. |
| Four draft types | `research_briefs.py` and versioned `brief-v1.md`: type-specific required sections, prerequisite capabilities, exact source claims, inspected alternatives, six independent ordinal judgments, unknowns and no-project/insufficient-evidence dispositions. |
| Runtime and persistence | Reuse qualified P2 `CodexWorker` unchanged and the private manifest/atomic writer. Input ID enums prevent prose being mistaken for references; deterministic validators reject invented/misattributed quotes. Cache versions and lifecycle rechecks apply. |
| Retention | Context, proposals, profiles, executions, rejected responses and drafts inherit policy/expiry. Withdrawal invalidates derivatives; original imported-quote fingerprints prevent recapture via a changed report wrapper. |
| Canonical experience | `research_decisions.py` exposes commands through the existing research skill pointer. Managed JSON and embedded Markdown; no new dashboard or application framework. |

The upstream components actually re-read were `.claude/skills/upskill/SKILL.md`,
`.claude/commands/expand.md`, and
`.claude/skills/job-application-assistant/09-web-research.md`. Reuse covers study
order/practice, repository discovery and source verification; retained application
semantics and access escalation were not silently rewritten. New Python helpers
are additive, with no second command tree or imported broad research platform.

Radar inspection read only `src/ai_trend_radar/developer_reports.py` in the
separate local `youtube-trend-radar` checkout at HEAD
`fc96d4865ced43f9098a9272e865e96ee603ae3f`. That file had no working changes;
SHA-256 `a94c24ad2359c669c8e33db0a89e8beb356f036133456eed824468d7a1a8255f`.
It establishes the producer's
schema-3.0 field shape, not validity or permission for every linked source. Tests
use owned report-shaped fixtures. No actual Radar report, database or private
configuration was imported in validation.

## Live draft validation

The live replay used the existing P2 snapshot: 20 captured Jobicy observations,
six analyzed descriptions, five model-classified AI-domain roles and one adjacent
role. All P2 sample/employer/country/language/availability limits still apply.
No additional job request was made.

For repository context, the helper read exact Git objects from local commit
`29cca75`: `tools/research_analysis.py`, `tests/test_research_analysis.py`, and
`LICENSE`. The selected MIT-licensed code was reviewed for this narrow hosted
analysis use. These are **three file references in one repository**, not three
independent alternatives. The live project retry narrowed context to the analysis
module; its scope is a contribution proposal, not a repository-wide audit.
There is no claim that a broad alternatives search was completed.

| Workflow | Successful disposition | Valid market / context quotes | Turn latency | Reported tokens |
|---|---|---:|---:|---:|
| Learning | Propose practical production-ML/evidence-validation learning | 4 / 3 | 31.802 s | 17,198 |
| Project | Contribute to the inspected existing repository | 3 / 3 | 82.319 s | 13,359 |
| Product | Explicit hypothetical extraction-validation product | 3 / 3 | 70.570 s | 17,629 |
| YouTube | Proposed reproducible evidence-extraction experiment | 3 / 3 | 42.818 s | 17,452 |

All four drafts have commercial-validation and video-suitability judgments
**unknown**, because no inspected customer/problem or dated discussion evidence
was supplied. A useful proposed engineering experiment does not establish audience
demand. The product is a hypothesis, not a validated buyer/pain or revenue claim.
All four remain `draft-human-review`. The [machine-readable evidence](phase3-evaluation.json)
contains IDs, exact prompt/validator/schema/runtime hashes and metrics, with no
source descriptions or private profile. Full drafts stay in managed private state.

Live validation found and rejected:

- Prose in the `analysis` reference field. The schema now constrains references
  to existing artifact IDs; malformed references cannot enter a draft.
- Inspection limitations quoted as primary source content. These failed exact
  source matching. Prompt clarification separates wrapper metadata from content;
  the deterministic rejection remains in place.
- One project turn exceeding the existing 90-second worker deadline. It deferred
  without automatic retry/fallback. A separately initiated narrower-context run
  completed. No timeout limit was silently relaxed to manufacture success.

Earlier diagnostic versions and failure evidence remain labeled; successful
learning/video and corrected product/project runs have different prompt/validator
hashes, recorded explicitly. The metrics are observations of these four successful
turns, not total diagnostic usage or a controlled model-quality comparison. P2's
same-input upstream/simple-prompt extraction comparison remains separate.
Additional data/API purchases were **₹0**; all model turns used existing ChatGPT
sign-in. No API billing route or new subscription was introduced.

## Automated checks and practical limits

Full regression suite: **502 tests; 501 passed, one opt-in runtime test skipped**.
P2's installed-binary forced-call test remains applicable: runtime client and its
qualification test are unchanged. Skill/command lint and security guards passed.

PR Ready assessment: **PR READY**, against `29cca75`. Tests, lint and static
checks passed; no suspicious files or repository blockers. Build was skipped
because no build command is configured. The complete local transcript is
`.tools/validation/phase3-pr-ready.md`; repository readiness does not establish
human acceptance.

The 25 new behavioral cases exercise all four schemas, valid contribution and
no-project cases, source/metadata quote rejection, unknown commercial/video
judgments, stale dates, contradiction retention, replay/cache, mid-run withdrawal,
expiry/non-resurrection, permissions/versions, read-only pinned Git acquisition,
failed acquisition/no retry, Radar idempotence/original-quote withdrawal, profile
review rejection, known-skill retention in the corpus, and scoped demonstration.
They use owned fixtures and injected responses; they are not human usefulness
ratings. The real model runs above separately establish active draft generation.

The shared state changes preserve existing job imports/counts, application tools,
upstream skill behavior and protected profile templates. Context/profile imports
cannot inflate job observations or market counts. Ordinary tests remain network-
free; the Git inspection test creates an owned temporary repository and executes
no repository code. Generic HTTPS acquisition is exercised through an injected
fetcher, not asserted universally permitted or live-qualified across destinations.

Limits remain explicit: structural/quote checks cannot establish semantic quality
or detect every false inference in proposal prose. DNS checking is not a network
sandbox. Logical expiry is not physical/hosted erasure. A 90-day discussion review
window is a conservative policy, not evidence of popularity or freshness.
Unmanaged exports and restore stay disabled. Full outcomes/interchange are P4;
scheduling/review inbox/recovery are P6. Conditional sources do not gate these drafts.

## Human acceptance still required

Review all four actual drafts for usefulness, feasibility, grounding, trade-offs,
source limitations and unsupported commercial/content claims. Review a known-skill
deepening example and an insufficient-evidence/no-project example as well as the
live contribution case. Automated fixtures exercise those paths but cannot supply
human acceptance. No 70% usefulness target, source-wide accuracy claim, customer
interview, successful experiment or video-performance result is reported.

The pending P2 human labels are also preserved as pending; authorizing code work
or committing it does not fabricate those reviews. P4 outcome/interchange work
and P5 measured source expansion remain distinct next implementation branches.

## Completion follow-up

The live known-skill and no-alternatives cases now run through the actual qualified
worker in a separate private synthetic store. [Scenario identities and versions](phase3-scenarios.json)
retain their provenance. The learning output deepens self-declared retrieval
knowledge through hard negatives, query/corpus mismatch and failure explanations;
it does not promote that declaration to demonstrated ability. The project output
chooses `insufficient-evidence`, names no alternative and labels any retrieval
exercise as practice, not an established contribution opportunity. The real corpus
and user profile remain unchanged by these fictional scenarios.

Assistant semantic inspection of the earlier real drafts identified repetitive
suggestions for validation/tests already present in the inspected repository.
The prompt now requires a concrete addition or abstention, distinguishes learning
reproduction from contributions, and avoids default UI/export packaging. This is
an **assistant finding**, not the required human review. Existing versioned drafts
remain historical unreviewed artifacts; generation does not silently approve them.

`inspect --id` now provides policy-checked local plain-text review with exact
source/capture traces and alternative inspection paths. Multiple files from the
same repository count as one alternative source. Withdrawal blocks viewing;
terminal control/bidi sequences are stripped. No exported file or dashboard is
created. Supported policies must tolerate local viewing history; no physical
recall of terminal/editor copies is promised.

The refreshed real contribution run additionally inspected
`tools/evaluate_research.py` and `tests/fixtures/research/heldout-v1.json` at
`29cca75`. It now proposes a policy-bound human-adjudication layer over existing
real-description evaluation records, rather than rebuilding the extractor or its
current tests. [Run identity and metrics](phase3-existing-work-evaluation.json)
record the exact version and limits. This is still a proposal, not a maintainer
request or an independently verified repository-wide absence claim.

The concrete six-case [human review checklist](phase3-review.md) provides current
brief IDs and local inspection commands. Direction-only feedback is deliberately
not equated with source-accuracy or full usefulness adjudication.

A subsequent product refresh under the stronger reuse prompt was rejected because
an escaped multiline quote did not exactly match the inspected source. It was not
silently repaired or accepted; the rejected response remains policy-bound in
private state. The earlier structurally valid product draft remains available
for review with its version and packaging limitations explicitly identified in
the checklist. Occasional model rejection is a supported failure path, not a
successful draft or a fabricated quality result. No automatic retry occurred.

Final repository assessment: **PR READY** against `29cca75`; **502 tests run,
501 passed and one opt-in runtime test skipped**. Lint and static guards passed;
no build command is configured. This verifies engineering readiness, while the
six-case human acceptance checklist remains open.
