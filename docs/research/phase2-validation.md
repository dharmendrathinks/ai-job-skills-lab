# Phase 2 implementation and acceptance evidence

Updated 2026-09-09. Work is in the required `ai-job-radar` checkout on
`research/phase2`, based on approved/pushed P1 commit `d102a88`.
The source-to-analysis implementation and automated validation are delivered.
**Human evaluation acceptance is still pending.** This distinction preserves the
approved scope; it does not convert model-generated labels into human evidence.

## Delivered behavior

- Bounded, reviewed Jobicy acquisition and local imports use shared policies,
  receipts, source revisions and private state. No candidate profile or tracker
  affects corpus admission or aggregate counts.
- The pinned Codex 0.153.4/gpt-5.5 subscription worker advertises an empty tool
  registry. Active forced-call tests establish pre-dispatch rejection for nine
  challenged paths. Source inspection and exact hashes are in [runtime.md](runtime.md).
  This is not OS isolation or a guarantee about provider retention.
- Versioned prompts/schema/taxonomy/model/configuration and validator hashes,
  qualification records, execution provenance, usage/latency, cache and refresh.
  No description produces unknowns without a model call. Invalid quotes or
  unsupported output cannot become accepted analysis; failures have no paid fallback.
- AI responsibility/domain classification, exact Unicode evidence spans,
  capabilities separate from tools, deterministic opening/employer/modality counts,
  captured history distinct from observed vacancy status, managed JSON/Markdown.
- Private 0700 directory/0600 state, unchanged upstream atomic writer, locking,
  pre-use/submission/commit expiry checks and transitive withdrawal. Raw HTML,
  normalized descriptions, model responses, analyses, comparison artifacts and
  reports inherit policies. Unmanaged exports/restore and unsupported physical
  deletion deadlines fail closed. Scheduled cleanup/recovery remain P6.

## Source qualification and real replay

Freehire remains conditional: its documented API is reusable but research
retention/disclosure permissions were not sufficiently established. The existing
portal and application workflows are unchanged. Jobicy fills that specific gap
through one thin adapter, not a new collection framework.

The [Jobicy fair-use documentation](https://github.com/Jobicy/remote-jobs-api/blob/c38dc5308768d7a9c0228c4831b453530f4788d9/README.md#fair-use)
was inspected at the pinned revision on 2026-09-09. It expressly addresses research,
AI products, summaries and appropriate caching with attribution. This basis is
separate from its example-code license; it does not transfer ownership of employer
content or guarantee hosted deletion/training settings. The recorded review is
Codex document inspection, not a human/legal sign-off. No hard physical deletion
period was asserted. The narrow logical-retention/hosted-processing policy expires
for use on **2026-10-09** and forbids unmanaged export; fresh review is required.

One free unauthenticated API request used query `machine learning`, count 20,
without personal geography/experience/employment filters. It produced:

| Observation | Result |
|---|---:|
| Captured descriptions / native source listings | 20 / 20 |
| Conservatively deduplicated openings | 20 |
| Distinct source-reported employer names | 14 |
| Verified employer domains | 0 |
| Missing descriptions | 0 |
| Country / language unknown | 20 / 20 |
| Availability unknown | 20 |
| Real descriptions analyzed | 6 |
| Model AI-domain classification: in-domain / adjacent | 5 / 1 |

The single capped remote feed has no pagination/total proof; these are historical
observations, not 20 verified open vacancies or global demand. Source-reported
employer names are not verified corporate identities. Raw and deterministic
`html-text/1` representations are retained; unzoned publication times stay unknown.
Canonical URLs and attribution are preserved in the receipt/observations.
Receipt ID: `c84cde98c189aca226ee6b5f644b4113bf07a61f7e8e6ea1260d41092fe9f6c5`.
Real source content exists only in the private research store outside Git.

## Model comparison: actual results and limitations

The frozen prompt preceded six author-created synthetic held-out snippets from
six fictional employer families. Each arm used the same descriptions, model and
output schema. [Machine-readable scores and version hashes](phase2-evaluation.json)
preserve the original run. Human labels are **provisional, pending review**.

| Arm | Examples | TP / FP / FN atoms | Precision / recall | Valid span examples | Turn latency total | Reported tokens |
|---|---:|---|---|---:|---:|---:|
| Research prompt | 6 | 6 / 1 / 0 | 85.7% / 100% | 6 | 41.177 s | 5,007 |
| Straightforward prompt | 6 | 6 / 2 / 0 | 75.0% / 100% | 6 | 42.013 s | 2,659 |
| Upstream targeted replay | 6 | 5 / 4 / 1 | 55.6% / 83.3% | 6 | 54.262 s | 25,084 |

Atoms combine capability labels and literal tool/modality pairs; these figures
are **not** full human-labeled requirement precision. The reference is sparse:
research's extra `ai-product-engineering` mapping may be a valid broader label,
but it remains a false positive under the frozen provisional scoring rule until
adjudication. It was not removed from results to improve the score. All three
arms matched the four specified responsibility classes and five specified domain
labels. Research/simple-prompt retained required Python in English and German
and preferred Kubernetes; upstream replay omitted known Python in one English
case but retained it in German. That exposes variability rather than proving a
uniform upstream behavior. Missing descriptions produced no explicit claims.

The upstream arm loads the **unchanged** canonical targeted `/upskill <URL>` spec
and supplies a synthetic profile (already knows Python) and fetched-description
input, with JSON presentation adaptation. This exercises its analytical rules,
not end-to-end application setup, portal fetching or every upstream workflow.
Preserved application behavior is also covered by the retained regression suite.

All three arms also ran on the **same real retained Applied AI description**.
They passed exact-quote validation; measured turn latencies were 21.616 s
(research), 68.876 s (simple), and 25.346 s (upstream replay). These artifacts
inherit source withdrawal/expiry. Human accuracy labels for that description
remain pending, so no real-source precision/recall is reported.

An uncached research repeat on that fixed real description had 4 common atoms,
4 original atoms and 6 repeat atoms: Jaccard agreement **66.7%**. This one-example
measure exposes variation; it is not a population stability estimate. A separate
process-restart cache replay returned the identical analysis ID in **0.129 s**
with no new model turn. Controlled tests verify profile-free input and revision,
prompt/version and runtime drift behavior. Code-point span validity does not
prove required/preferred modality or capability correctness.

One earlier evaluation stopped on an unclassified model-turn failure and was
not automatically retried. Later explicitly initiated runs succeeded. Generic
LLM concept labels found in an early response now normalize separately from
concrete tools; raw responses and earlier results remain auditable. The prompt
was not tuned after exposure to the six examples. These examples are now exposed
and must be treated as regression/evaluation-history cases, not an untouched
future held-out set. A future prompt change needs new held-out examples.

Incremental job-data/API purchases: **₹0**. Model turns used existing ChatGPT
sign-in; no API billing route/top-up was used. Token counts above cover the final
18 synthetic turns, not all diagnostic attempts or the whole development session.
They are runtime-reported usage, not a billing reconciliation. Unattended quota
behavior and local-model memory/quality were not evaluated. No paid fallback is
configured. Recommendations/alternatives/commercial or video usefulness start
with P3 outputs and have no fabricated scores here.

## Executed regression evidence

- Full Python suite: **477 tests, 476 passed, one opt-in runtime test skipped**.
- That installed-binary qualification test separately **passed**, exercising nine
  forced calls against a loopback fixture and verifying no tool side effects.
- Skill/command lint and security guards passed. Framework version guard passed;
  its local invocation compares HEAD to HEAD, so the AGENTS 1.0.2 bump was also
  inspected in the staged diff, not inferred from that command.
- Tests cover concurrent writers, failed atomic commits, state corruption,
  revisions/deduplication, missing/invalid spans, source cooldown/failure, policy
  expiry before submission, mid-run withdrawal, derivative invalidation,
  non-resurrection, cache/refresh, timeout/quota/protocol errors and runtime drift.
- No portal implementation/dependency manifest/application rank helper/private
  profile changed. Their P1 Bun baseline remains applicable; Python regressions
  were rerun. No LaTeX work was needed. Original MIT license is intact; the
  runtime adaptation includes its Apache-2.0 notice/license.

PR Ready assessment: **PR READY**, against `d102a88`. Tests, lint and static
checks passed; no suspicious files or repository blockers were detected. Build
was skipped because no build command is configured. The exact transcript is
retained locally in `.tools/validation/phase2-pr-ready-final.md`. This repository
verdict is separate from human evaluation acceptance.

## Remaining acceptance work

1. Human review of the six proposed labels, ambiguous extra capability mappings
   and the real-description extraction/comparison. The review request is pending;
   record the actual reviewer, corrections and scope before claiming acceptance.
2. The approved 120-description/40-employer and ≥95% precision targets are not
   achieved by this diagnostic sample. They remain targets, not release-size
   requirements. Expand independently grouped held-out evidence and adjudication
   before broad quality claims; do not lower denominators to manufacture success.

The implementation enables P3 decision workflows and P5 source expansion as
independent branches. Conditional providers do not block unrelated capabilities.
