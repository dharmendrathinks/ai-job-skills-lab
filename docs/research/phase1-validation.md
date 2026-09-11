# Phase 1 completion evidence

Validation date: 2026-09-08. Development and all deliverables are in the
user-requested `ai-job-skills-lab` checkout. Branch: `research/phase1`.
Foundation: `8c81edc330b98db0473dcb016e34db835c2fd378`.

## Delivered and verified

| P1 acceptance | Evidence |
|---|---|
| Pinned foundation and ancestry | Local HEAD starts at the approved upstream commit, with upstream history intact. Supplied origin is an existing empty private independent repository; no GitHub fork metadata is claimed. Upstream license and collector source are unchanged. |
| One development folder and preserved plans | Checkout moved into the original folder at user direction; sibling removed. `PLAN_RESEARCH.md` is active; original `PLAN.md` checksum matches the preserved value in maintenance.md. |
| Canonical routing | Root AGENTS and portable research pointer route to one `.claude/skills/research/SKILL.md`. Research scrape exits before application state; portal discovery excludes the pointer. |
| Public/private boundary | Read-only preflight resolves private external storage, keeps sources/extraction disabled and creates no data. Real temporary-Git tests catch tracked-ignored files, staged personal content, placeholder-preserving additions, and unsafe state paths. |
| Safe onboarding | Setup and expansion specifications require the blocked preflight before collecting/writing personal details, including section updates. The supported preflight does not initialize profiles; arbitrary tool/OS writes are not claimed prevented. |
| Contracts and runtime decision | v1 definitions/config example defined in source documents only. Existing subscription selected; complete tool-free extraction remains explicitly unverified for P2. No model-denial result is claimed. |
| Maintenance and CI | Visible upstream attribution, divergence/path ledger, retained update helpers, unconditional template/version CI checks, and manually opted-in issue reporting. No workflow was triggered remotely. |
| Codex discovery/routing smoke | CLI 0.153.4, ChatGPT sign-in, ephemeral read-only invocation. Executed portable-pointer read, canonical-spec read, then the preflight. No candidate-profile content was fetched through the smoke's tool calls. |

## Executed checks

The original Python baseline ran before source changes on the pinned checkout:

```text
python3.13 -m unittest discover -s tests -t .
Ran 413 tests in 6.909s
OK (skipped=6)
```

After configuring the local Python 3.13.14 venv with PyYAML 6.0.2:

| Check | Observed result |
|---|---|
| `python3 -m unittest discover -s tests -t .` | 423 tests passed, no skips; includes 10 new Phase 1 behavior tests |
| `python3 tools/lint_skills.py` | Passed: 11 skills, 12 commands, settings JSON |
| `python3 tools/check_framework_version.py` | Passed; AGENTS version bumped |
| `python3 tools/security_guards.py` | Passed: permissions, hooks, ignore rules and package manifests |
| `python3 tools/research_preflight.py --mode research --action status` | `ready_for_phase_1_only`, no template errors, no enabled sources, extraction unverified/disabled |
| All six portal `bun run typecheck` invocations | Passed against unchanged upstream CLI sources |
| Freehire / Jobbank / Jobdanmark Bun tests | 44 / 41 / 50 passed |
| Jobindex / Jobnet / LinkedIn Bun tests | 51 / 47 / 62 passed |
| Total portal fixtures | 295 passed, zero failures after PATH correction |
| CI YAML inspection | Public-template job unconditional; issue workflow has no schedule, read-only default token and explicit dispatch/variable gate |
| `git diff --check` | Passed |

Bun 1.4.2 was installed locally from the hash-verified official arm64 release.
Upstream CLI dependencies were installed with lifecycle scripts disabled;
manifests were not changed. The first fixture invocation failed because child
processes could not find `bun` on PATH. Adding the local binary directory to the
test environment resolved that failure without collector/test changes.

The Codex smoke executed these commands successfully:

```text
cat .agents/skills/research/SKILL.md
cat .claude/skills/research/SKILL.md
.venv/bin/python tools/research_preflight.py --mode research --action configure
```

It returned research mode, no template errors, no enabled sources and unverified,
disabled extraction. Raw smoke events/output and portal test logs are under
ignored `.tools/validation/`. A tool-using orchestration smoke is not evidence
of tool-free extraction. Local checks confirmed that the default research data
directory and the removed sibling development directory do not exist.

## Limits and next gate

P1 supplies foundation, routing, privacy preflight, contracts and a recorded
runtime decision. It does not implement P2 collection, retention operations,
extraction, validation/persistence, or later brief/outcome workflows. Those
remain disabled, including sources whose exact use/retention rights are unclear.

The concrete P2 inference blocker is a supported complete pre-execution tool-free
mechanism for subscription Codex. P1 acceptance permits an explicit blocker;
it does not permit falsely declaring extraction readiness. Source-policy and
fixture work can proceed independently. Paid inference is not a fallback.

LaTeX compilation and remote GitHub Actions were not run; no TeX source changed,
and LaTeX is not a research prerequisite. Live portal collection, personal setup,
publishing, pushes and external issue writes were not performed. The final local
PR Ready assessment is saved separately in ignored `.tools/validation/pr-ready.md`.
