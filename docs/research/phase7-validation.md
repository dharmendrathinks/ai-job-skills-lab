# Phase 7 validation — 2026-09-09

Phase 6 was committed locally as `09bc20d` before this work. Phase 7 was implemented
on `research/phase7` in the same development checkout. No new checkout, dependency,
provider, model runtime, public deployment, schedule, notification or push was
created. A separate private **data** directory held only owned evaluation fixtures;
the default AI corpus and application profile/tracker were not retagged or copied.

## Implemented behavior and checks

| Capability | Evidence | Limit |
|---|---|---|
| AI remains default | Frozen P6 aggregate, extraction schema/prompt and brief-schema hashes match on an owned example; reserved default directory rejects backend binding. | Shared helper changes invalidate future code-version caches; historical artifacts are unchanged, not reclassified. This is not a claim of byte-identical stochastic model responses. |
| Explicit domain selection | Empty-store opt-in, immutable binding, malformed/cyclic pack rejection, new revision in a new workspace and missing-header/binding failures tested. | One backend/platform pack is shipped; further packs require review. |
| Shared extraction | Exact quotes, literal tools, backend capability enum, domain-fit field, missing-text deterministic abstention, cache reuse and foreign taxonomy rejection tested. | Structural validation is not semantic accuracy. |
| Four workflows and feedback | Backend briefs pass the existing P3 validators; P4 outcome/profile controls accept backend capability IDs and reject AI taxonomy intrusion. P6 inbox/report/runner reuse tested. | No human usefulness/feasibility rating or demonstrated user capability is invented. |
| Coverage and comparisons | P5 coverage retains pack revision; local comparison discloses scopes, receipts, filters, segments, periods, model versions and conservative overlap; pooled totals/ratios stay null. Withdrawal is rechecked. | Descriptive samples, not matched cohorts or relative worldwide demand. No cached cross-store derivative. |
| Recovery/interchange | Binding survives recovery/expiry; foreign backup cannot rebind a workspace. Domain-aware 1.1 interchange round-trips only with matching receiver/permissions; AI remains 1.0. | No Radar consumer modification or automatic global withdrawal registry. Withdraw applicable material in every affected workspace. |
| Owned evaluation guard | Real/mixed content and private feedback/context/profile stores cannot be used as the backend evaluation workspace. | The dedicated harness uses its frozen known fixture path, not arbitrary pack paths or downloaded code. |

All 21 focused behavioral tests passed. The final full repository suite ran 603
tests: 602 passed and one opt-in installed-runtime test was skipped. Skill lint
and security guards passed. The analyzer returned **PR READY**; build was skipped
because no build check is configured. Final PR Ready evidence is `.tools/validation/phase7-pr-ready.md`; the phase's
`.pr-ready.json` baseline is committed P6 `09bc20d`. Reproduce checks using the
existing venv and ignored Bun directory:

```sh
PATH="$PWD/.venv/bin:$PWD/.tools/bun-v1.4.2:$PATH" python3 -m unittest tests.test_research_domains -q
PATH="$PWD/.venv/bin:$PWD/.tools/bun-v1.4.2:$PATH" python3 -m unittest discover -s tests -t .
```

The frozen AI expectations in `tests/fixtures/research/ai-phase6-baseline.json`
were obtained by executing relevant functions read with `git show 09bc20d:PATH`.
No old project files were imported or overwritten to obtain the baseline. The
ordinary retained upstream tests remain part of the full suite.

## Actual bounded model evaluation

The selected private owned-evaluation workspace ran the existing installed-binary
qualification: all nine forced tool-call attempts were denied before execution.
Qualification artifact:
`5c70f8f47208c0291a805edc9bb8f59acf3de0e5dc7faec7ebf920aceb585852`.
The same pinned Codex 0.153.4 / gpt-5.5 ChatGPT worker then processed the frozen
backend-platform/1 dataset. No API key, paid fallback or real job input was used.

Twelve author-owned examples cover eight backend/platform capability areas,
research-heavy responsibilities, adjacent AI work, missing descriptions and an
embedded malicious instruction. The missing-description case abstained in code
without a model call. The other eleven cases used the real worker. Across all
twelve, structural validation passed; agreement with **provisional author labels**
was 14 capability/tool atoms correct, one extra atom and zero omitted expected
atoms. Applied/research-heavy class agreement was 12/12; domain-fit agreement was
10/12. These are small synthetic-set observations, not achieved market-quality
targets or human-adjudicated precision estimates.

The disagreements were:

- Performance/capacity example also received `service-api-design`, absent from
  the provisional expected capability set.
- Novel distributed-consensus research was classified adjacent rather than the
  provisional in-domain label.
- AI retrieval/agent work was classified out-of-domain rather than the
  provisional adjacent label.

Labels and taxonomy boundaries were not changed to erase these disagreements.
They need human adjudication and broader examples. Extraction used 13,514 reported
tokens and 97.997 summed worker seconds; these are measurements for this run, not
latency/cost promises. The same existing subscription was used throughout.

All four initial backend briefs passed structural validation. Assistant inspection
then found generic job-evidence wording where the input was fictional: the shared
brief input had not carried snapshot scope. Backend `source_scope` was added to
inputs and deterministic rendered evidence limits without changing the default
AI prompt/schema. All four briefs were regenerated over the same extracted data.
The final model proposals explicitly identify their inputs as synthetic:

| Workflow | Final disposition | Commercial/audience judgment |
|---|---|---|
| Learning | Propose practice | Unknown / unknown |
| Open-source project | Insufficient evidence | Unknown / unknown |
| Product | Insufficient evidence | Unknown / unknown |
| YouTube | Insufficient evidence | Unknown / unknown |

The final scoped-brief evaluation artifact is
`bb711aafa8fb31288fa420670bc9818bdce618db9f95d377bcf57b52c84efce9`;
the original extraction evaluation is
`d26f6965532c953da5e4eb4e70499776c68034904a722e86ff3be602ff62fcc1`.
The later dedicated-workspace preflight guards were added after the initial run;
that run's stored inputs were inspected as owned fixtures only. Per-case metrics,
exact versions, final draft IDs and evidence limitations are recorded in
[the development evaluation summary](phase7-evaluation.json). That file contains
no real source descriptions, private profile, credentials or purported outcomes.

## Remaining evidence gates

- Representative permitted backend descriptions across distinct employers, human
  gold-label adjudication and human recommendation usefulness/feasibility review.
- Same-input backend comparison with unmodified upstream analytical rules and a
  straightforward prompt; prior AI baseline results do not prove backend benefit.
- Real source coverage and language quality; the pack's queries are candidates,
  not proof of coverage, current availability or demand.
- A reviewed common taxonomy/cohort before inferential cross-domain comparison;
  durable cross-workspace derivatives would need an explicit lifecycle contract.
- Separate Radar 1.1 consumer support, compatible export rights and actual user
  approval before external delivery. Prior scheduling/account-use gates remain.

The seven-phase engineering map is implemented. These open gates remain part of
its acceptance work; no human acceptance, market result or additional phase is
invented to close them.
