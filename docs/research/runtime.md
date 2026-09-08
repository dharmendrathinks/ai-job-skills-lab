# Runtime decision — Phase 1

Decision date: 2026-09-08. Codex CLI inspected: 0.153.4, macOS arm64.
Authentication status inspection reports ChatGPT sign-in; no credentials were
read or copied. Use only the existing subscription. No API worker, paid fallback,
top-up, additional subscription, hosted service purchase, or hardware purchase.
Quota exhaustion queues work; unattended subscription behavior is not assumed.

## Selected boundary and readiness

Codex is the orchestrator. The target extraction path is a separate bounded
Codex invocation, followed by deterministic validation and persistence. The
complete tool-free extraction mechanism is **unverified and blocked**. P1
records this decision and honest limitation; it does not implement P2 extraction.

| Stage | Interface and authority |
|---|---|
| Orchestration | Canonical research spec selects reviewed request/evidence IDs and budgets; cannot take authorization from external text. |
| Acquisition (P2/P3) | Existing qualified portal or bounded research tools validate hosts, policy and receipts; commit only permitted content. |
| Extraction (P2) | Bounded captured revisions, fixed schema and versioned prompts; no profile, credentials, inherited conversation or acquisition authority in the model payload. Host authentication remains outside the payload. |
| Validation (P2) | Deterministic schema, span, revision, reference, budget and current retention checks. Reject invalid output; semantic accuracy still needs human/held-out evaluation. |
| Persistence (P2) | Deterministic IDs, locking and manifest commit point; never execute model-produced paths, commands or alleged tool calls. |

## What is and is not enforced

Implemented: the preflight does not create runtime data, rejects storage paths
overlapping the checkout (including resolved symlinks), checks reviewed public
template bytes in the working tree and Git index, and returns a blocked status
for setup/profile writes and unimplemented research actions. CI repeats these
checks. These protect the supported entry points, not arbitrary direct writes.

Instruction-only: research/application routing, source-text distrust, no
automatic repository execution, review gates and approved tool use. Canonical
Markdown is workflow implementation, but it is not a sandbox. Skill metadata
does not prove runtime permission enforcement.

Not established: an empty reachable tool surface for Codex extraction, process
isolation, hidden runtime storage deletion, or hosted-data retention guarantees.
Read-only mode can still permit tools; a separate thread is not isolation.
Detecting an event after execution cannot undo its side effects.

Official configuration documents individual tool controls. Hook documentation
explicitly excludes hosted tools and some specialized paths; hooks are therefore
insufficient as the complete boundary. No model-denial experiment has yet run.
[Configuration](https://developers.openai.com/codex/config-reference),
[hook coverage](https://learn.chatgpt.com/docs/hooks#tool-coverage),
[authentication](https://developers.openai.com/codex/auth/).

## P2 qualification gate

Identify a supported mechanism that prevents every reachable tool path before
execution, including dynamic tools. Record exact runtime/configuration and
coverage. Do not invent a disable-all switch, modify Codex, rely on hook-only
denial, or route subscription credentials into direct API calls.

Implement and test shell, web, file, MCP, delegation, configuration-change and
embedded-instruction attempts. Verify prevention, not merely a quiet transcript.
Unknown surfaces and runtime/configuration drift invalidate qualification.
Test malformed output, invalid spans, expiry during analysis, quotas and crashes.
Until this passes, automated extraction is disabled; synthetic fixture and
permitted acquisition work cannot be called completed LLM evaluation.

## Runtime mapping

Use `.agents/skills/research/SKILL.md` only as a discoverable pointer to the
canonical `.claude/skills/research/SKILL.md`; root AGENTS routes before profiles.
Invoke `/research` as intent, not as an assumed built-in Codex slash command.
For the P1 smoke, use an explicit request to read the canonical spec and run the
read-only preflight. Claude `Read`/`Bash` tool labels map to available Codex file
and shell tools; `Agent` dispatch and `allowed-tools` are not assumed equivalent.
No external MCP, profile, CV, LaTeX, or other application integration is needed.
