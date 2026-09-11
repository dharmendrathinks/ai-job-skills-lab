# Phase 6 validation — 2026-09-09

Phase 5 was committed locally as `121bdcd` before this work. Phase 6 was implemented
in the same `/Users/dhasharma/Dharmendra/Projects/ai-job-skills-lab` checkout, on branch
`research/phase6`. No fork, remote change, dependency/model installation, schedule
activation, notification send, publishing or push was performed.

## Delivered and exercised

| Capability | Evidence | Limits |
|---|---|---|
| Integrated refresh | `research_operations.py` calls existing collection/analysis/snapshot/brief helpers. Owned journey test generates all four validated P3 drafts, reuses their cache, records a fixture decision and withdraws source lineage. | Fake model outputs exercise integration, not human recommendation quality. No new live job collection. |
| Incremental/resumable runs | Tests cover persisted intent, process overlap, crash with ambiguous request, explicit reviewed retry, completed-step reuse, queue overflow, stale extraction contract, failed model batch and continued local reporting. | An ambiguous result requires operator reconciliation; no exactly-once model invocation. |
| Inbox and offline evidence | Tests cover new/due/revised briefs, explicit acknowledgment, unshown overflow, deferral, escaped source/model text, no active markup/remote assets and private managed file permissions. | Generated files are dated snapshots; already-open browser memory is not recalled. No dashboard/framework added. |
| Local scheduling | Plist structure/absolute paths/minimal environment verified; deterministic tick tests cover no duplicate slot, process crash, five-hour gap coalescing and expired model qualification with continued local reports. | No actual launchd agent was installed. Sleeping/locked Mac behavior was not measured end to end. |
| Retention and recovery | Existing P2 lifecycle tests plus managed HTML/backup expiry, transitive withdrawal, stale reintroduced backup, corrupt primary recovery, missing journal, atomic-write interruption, unsafe symlinks and orphan-file cleanup. Restore excludes active runners. | Process crash/logical deletion only; no fsync/power-loss, physical erasure, disk-loss or unmanaged-backup claim. |
| Notifications | Exact content/destination approval, source export block, no send after withdrawal, overflow, unchanged suppression, ambiguous POST and lost-ledger reset tests use an injected owned transport. | No actual webhook configured/sent. Jobicy export remains false; real export rights and user approval remain required. |
| Compatibility | Retained upstream and P2–5 test suite; skill lint and security guards through the repository PR Ready configuration. | Installed-runtime forced-tool suite remains its opt-in test; the unchanged P2 boundary was not requalified unnecessarily. |

Reproducible checks from this checkout use the existing venv/Bun PATH:

```sh
PATH="$PWD/.venv/bin:$PWD/.tools/bun-v1.4.2:$PATH" python3 -m unittest tests.test_research_operations -q
PATH="$PWD/.venv/bin:$PWD/.tools/bun-v1.4.2:$PATH" python3 -m unittest discover -s tests -t .
PATH="$PWD/.venv/bin:$PWD/.tools/bun-v1.4.2:$PATH" python3 tools/lint_skills.py
PATH="$PWD/.venv/bin:$PWD/.tools/bun-v1.4.2:$PATH" python3 tools/security_guards.py
```

The focused suite passed all 33 behavioral tests. The final full suite ran 582
tests: 581 passed and one opt-in installed-runtime test was skipped. Skill lint
and security guards passed. The analyzer returned **PR READY**; build was skipped
because no build check is configured. Final PR Ready evidence is
recorded in `.tools/validation/phase6-pr-ready.md` (ignored local check output);
`.pr-ready.json` compares this phase with committed P5 `121bdcd`.

## Actual subscription smoke

The final owned smoke passed using Codex 0.153.4 / gpt-5.5 and the unchanged P2
worker with stdin closed and a reduced environment in a fresh subprocess. The
response was `{"ok":true}`; authentication was `chatgpt`, paid fallback was false,
and only user/agent message item types were observed. It used 143 input and 15
output tokens; worker latency was 4.306 seconds and parent elapsed time 5.042
seconds. Artifact:
`6ea99db2472be56793998c5ce4b009464bf63b6ce717c9dd2fadb6e549e27662`.

This establishes awake-session technical execution only. No operator account-use
assertion, unattended qualification or schedule was activated. Personal account
suitability, future token refresh, sleeping/locked-session operation and sustained
quota behavior remain activation gates. The seven-day qualification expiry is a
local review cadence, not an OpenAI entitlement or policy claim. Official sources
and concrete activation controls are in [continuous operations](continuous-operations.md).

## Actual local-model experiment

Already-installed Ollama 0.33.2 and
`qwen3:4b-instruct-2507-q4_K_M` were evaluated through the fixed loopback endpoint.
Model digest:
`0edcdef34593eac1aa2be9c7d06c432dcf81945adca5eca2f27662c18f168ba0`.
Local sysctl reported Apple M3 Pro and 19,327,352,832 bytes (18 GiB) unified memory.
No model download, research-source disclosure or production runtime change occurred.

The original six P2 author-owned cases and research prompt/schema were reused.
Settings: temperature 0, seed 42, 4,096-token context, 1,500-token output bound.
These examples had already been evaluated in P2; they are not a new unseen set.
Labels remain provisional and human review is pending.

| Case | Structural/source validation | Observed issue against provisional labels |
|---|---|---|
| Retrieval | Passed | Omitted explicitly required Python. |
| Serving | Passed | Kubernetes preferred modality became unspecified; role/domain differed from labels. |
| Research | Passed | Correct expected research capability/class on this short example. |
| Missing description | Rejected | Unknown classifications and no claims, but omitted the required missing-evidence limitation. P2 production handles missing descriptions deterministically without inference. |
| German | Passed | Omitted the explicitly required Python skill. |
| Sales | Passed | Domain differed from the provisional adjacent label. |

Five of six passed full P2 structural validation. Among the five valid responses,
atom counts were 3 true positives, 1 false positive and 3 false negatives. Summed
wall time for all six was 20.965 seconds. Ollama reported resident/VRAM size of
3,175,339,786 bytes during these requests. That is a server estimate, not measured
peak unified-memory pressure, swap, energy or a long-context memory-fit guarantee.

The prior same-input P2 research/simple-prompt/upstream-targeted-replay summaries
are in `phase2-evaluation.json`; they used a narrower span checker and a prior
harness. This is an exploratory comparison, not a fresh blinded latency/accuracy
head-to-head. No inference-provider promotion follows from these results. Longer
inputs, all four brief workflows, multilingual held-out quality, memory pressure
and human usefulness would need evaluation before proposing local production use.

One development run was discarded as quality evidence because the harness assigned
a synthetic capture timestamp after its validation timestamp, rejecting all rows.
That sequencing bug was fixed, a real-clock regression test added and all six
requests rerun. The discarded result and corrected measurements are explicitly
identified in [the public owned-fixture record](phase6-evaluation.json); there are
no real job descriptions, private profile contents or credentials in that file.

## Remaining concrete gates

- Actual schedule/account-use review and sustained sleep/wake/token/quota evidence.
- Actual notification destination/content approval and compatible source export rights.
- Human extraction/brief/translation evaluation from earlier phases; real stable
  historical cohorts and conditional-provider permissions are still pending.
- Local-model quality and peak-memory/long-context evidence; the observed errors
  currently preclude a production recommendation.
- Missing/corrupt withdrawal or operations ledgers require manual reconciliation;
  no old backup can establish the latest deletion or external-delivery history.

These gates do not require paid services and do not block independent local
review, cleanup, permitted collection or P5 coverage work. P7 remains separate.
