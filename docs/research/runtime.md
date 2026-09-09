# Runtime decision and Phase 2 qualification

P1 decision: 2026-09-08. P2 qualification: 2026-09-09, macOS arm64,
Codex CLI 0.153.4, existing ChatGPT sign-in, gpt-5.5. No API keys, paid fallback,
top-ups, extra subscriptions or hardware. Exhaustion defers the operation.
The earlier P1 schema/hook inspection left the boundary unresolved; the pinned
source inspection and active dispatch experiment below resolve that blocker
for this exact profile. They do not qualify every Codex model or installation.

## Execution boundary

| Stage | Interface and authority |
|---|---|
| Orchestration | Canonical research spec selects approved source/query, observation IDs and budgets. Development and acquisition retain their tools. External text cannot authorize actions. |
| Acquisition | `research_sources.collect_jobicy` performs a bounded request under a current source policy; the existing import/receipt/observation contracts persist the result. No model chooses a URL or follows embedded instructions. Other upstream collectors remain conditional. |
| Extraction | `research_analysis.analyze` supplies only the captured description, fixed prompt, taxonomy and output schema to `research_runtime.CodexWorker`. No title, profile, conversation, credentials or repository contents enter that payload. |
| Validation | Code checks schema, exact quote/code-point spans, literal tool labels, known taxonomy, revision and current policy. Generic AI/LLM labels are concepts, not concrete tools; original responses remain auditable. Semantic classification still requires evaluation and human review. |
| Persistence | Code owns identities, cache keys, locks and atomic writes using unchanged upstream `rank_state.save_state`. Source/qualification dependencies and expiry propagate to executions, analyses, comparisons and reports. Model-generated paths or commands are never executed. |

The worker starts an ephemeral app-server thread with **no environments, runtime
workspace roots, dynamic tools or selected capability roots**. It disables shell,
web, image, CodeMode, agents, hooks, plugins, apps, skills, memory and utility-tool
features and disables every effective MCP server by name. Project documents and
inherited developer instructions are suppressed. The exact configuration is
`BOUNDARY_CONFIG` and `CodexWorker.__enter__` in `tools/research_runtime.py`.

Empty environments remove local execution/file tool registration; the remaining
controls remove other registrations. gpt-5.5's bundled model metadata has no
implicit tool mode or experimental tools. The client copies that record
**unchanged** through the documented `model_catalog_json` override to prevent
remote catalog drift. Newer models with mandatory CodeMode are not qualified.
An empty dynamic-tool list or read-only sandbox alone would be insufficient.

The worker rejects unexpected server requests and tool-result items. These are
additional failure checks, not the pre-execution mechanism. Pre-execution
protection is the empty registry: unknown function/custom calls are rejected
before a handler runs. Prompt instructions about distrust are instruction-only;
workflow routing and human review likewise do not constitute isolation.

## Reproducible qualification

- Binary SHA-256: `b973d440acac501fd2594a43e7ca9ce41e0a65b9dfb28d0d7a7837c99e1261e3`.
- Source tag `rust-v0.153.4`, commit `3d2ee51ca2d5db578f328aa75e20aa22c0197c9a`.
- gpt-5.5 record digest: `7935feee7a55829ad98ac4b2311f14607a04ef84f77584d2f6dd370c1d07be63`.
- Boundary configuration digest: `8985e495b46ca446694283362856f594c9a4b5cf1a8bd45d0fdc7b6343e7c884`.
- Qualification also hashes the Python runtime client and active boundary test.
  Binary/version/model/config/client/test drift requires qualification again.

Read-only inspection used these exact paths in
[the pinned OpenAI Codex revision](https://github.com/openai/codex/tree/3d2ee51ca2d5db578f328aa75e20aa22c0197c9a):
`codex-rs/tui/src/temporary_structured_request.rs`,
`codex-rs/core/src/tools/spec_plan.rs`, `tools/mod.rs`, `tools/registry.rs`,
`tools/spec_plan_tests.rs` (the latter three under `codex-rs/core/src/`),
`codex-rs/core/src/config/mod.rs`, its tests, and
`codex-rs/config/src/config_toml.rs`. The temporary structured-request helper
provides the no-environment configuration pattern. Registry code establishes
unsupported-call rejection before dispatch. The partial archive and separately
fetched complete relevant files are inspection evidence, not a full built source
checkout. Rust tests were inspected, not executed. Adaptation provenance and
Apache-2.0 terms are in `THIRD_PARTY_NOTICES.md`.

`python3 -m tools.research_evidence qualify` runs the installed binary against a
loopback-only anonymous Responses fixture. It forces nine calls: shell execute,
shell stdin, file/image read, web, MCP, delegation, configuration/thread creation,
CodeMode, and custom apply_patch. The test asserts all advertised tool lists are
empty, all calls receive unsupported errors, no canary content is disclosed or
modified, no marker is created and no authorization header reaches the fixture.
This test passed. A separate real ChatGPT-provider extraction passed; the local
fixture alone would not establish subscription compatibility. Production never
uses that fixture backend as a fallback.

## Privacy and limits

This is a **tool-registry restriction**, not OS/process isolation. Codex itself
still needs host authentication and network access. Authentication remains within
Codex; this client neither reads token files nor routes tokens into a direct API.
The environment omits API/proxy keys, requires ChatGPT account type, rejects
custom OpenAI-provider settings and external telemetry, and disables analytics,
prompt telemetry and persistent transcript history. Runtime stderr is discarded
because it can contain snippets. The temporary worker directory is removed.

Ephemeral mode is not a guarantee of zero internal traces, provider training
settings or hosted deletion. Only policies compatible with provider-managed
retention and no physical erasure deadline can permit submission. Sources needing
recall of hosted copies, backups or OS snapshots are rejected. Use expiry is
rechecked after startup, before submission and before commit; a response received
after withdrawal is discarded and never becomes an analysis.

Input/output limits are 100 KB, source response/import limits 2 MB, and worker
turn timeout 90 seconds. Errors are sanitized and no application-level retry or
paid fallback occurs. The Codex transport may have its own internal retry behavior;
this implementation does not promise one network request per turn. Unattended
operation and broader recovery remain P6.

The app-server experimental API is version-sensitive. Official references:
[app-server protocol](https://developers.openai.com/codex/app-server),
[configuration](https://learn.chatgpt.com/docs/config-file/config-reference),
[hook coverage](https://learn.chatgpt.com/docs/hooks#tool-coverage).
Hooks do not cover every tool and are not used as the boundary.

## Runtime mapping

`.agents/skills/research/SKILL.md` points to the canonical `.claude` research spec;
AGENTS routes research before candidate data. `/research` denotes intent, not an
assumed built-in Codex command. No CV, LaTeX, application tracker, external MCP or
profile setup is required. Application workflows retain their upstream semantics.


## Phase 6 automation and optional model experiment

The P2 extractor and its empty tool registry are unchanged. P6's runner persists
step intent before calling the same acquisition/extraction/brief functions;
source selection, validation and persistence remain deterministic code. It has
no generic shell/model-tool executor. Failed/ambiguous model work pauses for
review and cannot trigger a paid API or local-model fallback.

Unattended smoke, explicit account-use review, seven-day qualification and exact
runtime/Python/Codex/harness matching are separate from interactive extraction
qualification. Unqualified scheduled model steps defer while cleanup/reporting
continue. The awake-session probe does not verify locked/sleeping laptop access,
future tokens or account entitlement. No schedule was activated. See
[actual operational gates and official references](continuous-operations.md) and
[Phase 6 evidence](phase6-validation.md).

Existing Ollama is used only for the checked-in owned-fixture experiment through
a fixed loopback, no-proxy/no-redirect endpoint. Its client exposes no tool dispatch
or model download route and sends no research sources. This is not an OS sandbox
or a qualified replacement for the production worker. Quality, long-context,
multilingual and peak-memory evaluation would precede any proposed promotion.


## Phase 7 domain dispatch

The registered tools, binary, ChatGPT authentication, source-disclosure checks and
no-paid-fallback boundary are unchanged. Shared extraction selects the immutable
workspace taxonomy and the domain prompt/schema before invoking the same worker.
Backend `domain_fit` and exact evidence spans are validated deterministically;
pack aliases are guidance, never source statements. Pack data cannot install code
or activate an adapter/runtime. The AI prompt and default schema remain unchanged.

The owned backend evaluation workspace ran the existing installed-binary forced-
call qualification and real subscription extraction/briefs. Results, scope limits
and semantic disagreements are in `phase7-validation.md`. The evaluation harness
uses only its frozen owned examples and rejects mixed/private context, feedback
or profile stores. No real corpus, application data or private repository was
submitted for Phase 7 evaluation. See `domain-operations.md` for explicit selection.
