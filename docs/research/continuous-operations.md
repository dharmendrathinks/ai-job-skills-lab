# Continuous research operation (Phase 6)

Phase 6 adds a bounded runner, review inbox, managed offline HTML, scheduling
configuration, recovery and optional reviewed delivery. It calls P2 collection,
extraction and snapshots and P3 briefs directly; P4 decisions, deferrals, outcomes
and permission-gated interchange remain their existing interfaces. P5 coverage
and cohort commands remain independently usable. No provider, database, service,
application-profile setup or dependency was added.

## Configure and refresh

Use the existing checkout and its venv. State defaults to the private directory
outside Git. Commands below do not install a schedule or send a notification.

```sh
/Users/dhasharma/Dharmendra/Projects/ai-job-radar/.venv/bin/python -m tools.research_ops health
/Users/dhasharma/Dharmendra/Projects/ai-job-radar/.venv/bin/python -m tools.research_ops configure --input /absolute/private/operation-plan.json
python3 -m tools.research_ops run --plan PLAN_ID
python3 -m tools.research_ops inbox --limit 10
python3 -m tools.research_ops report --limit 10
```

An operation-plan/1 input has these exact fields:

```json
{
  "schema_version": 1,
  "collect": null,
  "analyze": false,
  "brief_kinds": [],
  "contexts": [],
  "profile": null,
  "analysis_limit": 2,
  "report_limit": 20,
  "backup": false,
  "interval_seconds": 86400,
  "reviewer": "actual operator"
}
```

This concrete default runs cleanup, a deterministic snapshot and local reporting.
For an explicitly requested research refresh, `collect` can be
`{"source":"jobicy","query":"machine learning","count":20}`, `analyze` can be
true and `brief_kinds` can select learning/project/product/youtube. Context and
profile IDs are explicitly selected existing P3 inputs; no automatic web discovery
or personal-profile loading occurs. Missing/expired inputs block the affected
step rather than being silently dropped. Other providers remain disabled.
Configuration is an operator action, never an instruction extracted from a job.

The runner persists intent before every step. Its nonblocking OS lock prevents
concurrent runners in the same store. A run freezes its analysis queue, processes
at most 1–20 observations, reports overflow, and leaves remaining observations
for another run. Reviewed labels and current extraction contracts are reused;
changed prompt/schema/taxonomy/validator versions become pending. Model/runtime
drift still uses P2 qualification before invocation. Brief generation reuses P3
caches and P4 feedback/repetition controls. No automatic force-refresh is used.

A failed model step stops that model batch. Further runs of the same plan pause
model work for review; cleanup, snapshots and reporting can still proceed.
Failed P2 execution records and uncertain analysis attempts are not silently
retried. A crash can leave an intent ambiguous even when the child committed its
result: inspect existing execution/receipt IDs before resolving it. Resume with:

```sh
python3 -m tools.research_ops run --plan PLAN_ID --resume RUN_ID
python3 -m tools.research_ops resolve --input /absolute/private/resolution.json
```

A resolution contains `run`, `step`, `action` (`retry` or `skip`), `reviewer` and
`reason`. Obtain actual operator review before retrying an ambiguous invocation.
Only collect/analyze/brief steps support this reconciliation. Retry records
approval but requires explicit resume; skip is not evidence of success. Existing
P2 rejected executions retain their history. Independent direct P2 commands are
still available for reviewed investigation; they are not covered by the runner's
operations lock. Run completion does not mean human acceptance or model accuracy.

## Review, inspect and record outcomes

`inbox` lists new or due brief revisions with overflow and deferral counts. An
ordinary render never marks recommendations read. `inbox --acknowledge` records
presentation of only the displayed items; it does not accept a brief or update
capabilities. Explicit P4 deferred decisions become due after their recorded date;
accepted/rejected/duplicate/superseded items leave the inbox. A new revision gets
its own presentation identity. Use the existing `research_decisions` commands to
choose work, record observed/user-reported outcomes and review profile proposals.

`report` returns the path of one managed private `research-report.html`. It reuses
upstream `.claude/commands/html-report.md` single-file/escaping conventions with
an additive research view. All imported/model text is HTML-escaped, including
captured provenance and source spans. There are no scripts, active source links,
forms, external assets or network resources; CSP denies them. Expand the evidence
sections to inspect source observations, analyses, context and snapshot limits.
The file has 0600 permissions and is bounded to 4 MB; lower the limit if necessary.
No local web server or dashboard framework is required. Saved content is a dated
snapshot, not a live inbox: refresh after decisions or new evidence. The browser
may retain an already-open view; close it after withdrawal/expiry. No browser-cache
recall or physical erasure is claimed. Never move the file outside managed storage.

P4 JSON/Markdown interchange stays the reviewed export route. Current Jobicy
policies prohibit export, including external notification of derived brief data.
A local report is not permission to publish it.

## Scheduling and monitoring

`launchd --plan PLAN_ID` emits a reviewable plist with an absolute venv executable,
checkout, private state directory and minimal PATH containing the discovered
Codex executable directory. It never runs `launchctl`. The user-level agent uses
a 300-second heartbeat; the plan's UTC epoch cadence decides whether work is due.
No shell interpolation, API key environment, terminal input, KeepAlive restart
loop, automatic login or paid fallback is configured. Plist output contains no
source prose or credentials. Review these paths after moving/updating the checkout.

To activate **only after explicitly choosing the reviewed plan and schedule**:

1. Save the emitted plist as a private file in `~/Library/LaunchAgents/`.
2. Inspect ProgramArguments, WorkingDirectory, environment and interval.
3. Bootstrap that exact file with `launchctl bootstrap gui/$(id -u) ABSOLUTE_PLIST`.
4. Use `launchctl print gui/$(id -u)/LABEL` to inspect exit status; use
   `launchctl bootout gui/$(id -u) ABSOLUTE_PLIST` to disable it.

These are instructions, not actions performed during implementation. A user
LaunchAgent depends on a logged-in user session. The installed macOS
`launchd.plist(5)` documents that StartInterval events may be missed while asleep
or already running. On the next heartbeat, `tick` coalesces elapsed slots into one
current refresh and records the missed count; it never creates backdated captures.
The first tick has an unknown missed count because no prior baseline exists.
A consumed slot is not repeated after a crash. Inspect/resume its run explicitly.
Clock rollback causes a wait until a later slot. No hard deadline is guaranteed.

`health` and `cleanup` perform the P2 sweep, inspect state and expose safe run/slot
status and the last 100 operational check results. Tick failures are recorded
without exception/source text. A blocked model qualification does not block local
cleanup/reporting. Missing source authorization does not enable another provider.
Launchd stdout/stderr go to `/dev/null`; commands exit nonzero for blocked runs.
If filesystem/ledger failure prevents recording health itself, inspect launchd's
exit status and repair private storage manually. No independent always-on monitor
can alert while this laptop is asleep. The hash-only run/delivery ledger is retained
for reconciliation; it is not automatically pruned or restored from an older copy.

## Managed backup, restore and retention

```sh
python3 -m tools.research_ops backup
python3 -m tools.research_ops restore
```

P6 supports one fixed, private `backup.json` inside the same state directory. It
contains only the local manifest, under the existing indefinite-retention/logical-
deletion contract. It is a local rollback copy, not disk-loss recovery, external
export, an encrypted cloud backup or permission to use Time Machine for restricted
data. `backup: true` makes it the last refresh step. No source permission is widened.

Every Store transaction now synchronizes a monotone `withdrawals.json` journal
before replacing the primary manifest. It applies journal withdrawals and expiry
before returning content. A withdrawal conservatively removes the entire managed
backup and retracts dependent offline-report/presentation/notification artifacts;
the HTML copy is removed before the primary deletion is advertised. Reports also
depend on undisplayed items contributing to overflow/defer counts. Expiry checks
invalidate stale backups and derived views on the next transaction/tick. Orphan
atomic JSON and HTML temporary files are removed on the next transaction.

Restore excludes active runners and takes the same Store lock, verifies envelopes/lineage and the backup hash,
and requires the existing journal digest to match. It can replace a corrupt
primary, but cannot reconstruct a missing journal from a backup. It reapplies
expiry before exposing anything. A stale reintroduced backup is rejected. The
operations/delivery ledger stays current and is never rolled back with evidence;
its separate operations-origin marker makes a missing ledger fail closed, requiring
manual reconciliation before further sends. Removing both is not supported recovery.

The existing upstream atomic JSON writer remains unchanged. This orders process
crash recovery; it does not add fsync, power-loss transactions, secure deletion,
hostile same-user isolation, browser-cache recall or third-party backup control.
Hard deletion deadlines and unmanaged backup-recall obligations still fail before
capture. A missing/corrupt journal is a concrete manual recovery blocker. Old P2
stores acquire the journal lazily from their validated manifest; never downgrade
an active P6 store to a writer that ignores the journal/managed copies.

## Optional notifications

Slack is an optional private destination, not a dependency of research. The design
selectively reuses the pinned Radar `slack.py` destination identity, bounded cards,
no-unfurl and separate delivery-state ideas, without importing its SQLite/httpx
stack or touching that project. Actual sends are never invoked by refresh/tick.

Use `notify-preview --input PRIVATE_JSON` with an explicit `webhook` and optional
CLI `--limit` (1–10). Only compatible P4-exportable brief lineage is eligible.
The preview shows the exact destination hash and payload: workflow names, revision
numbers and local IDs, with no source text or private profile. Overflow stays
pending. Review the actual message and destination with the user before invoking
`notify-approve`: its input contains `preview`, `review_digest`, `webhook` and
`reviewer`. Then `notify-send` takes the resulting `approval` and same `webhook`.
Keep webhook files private and outside Git; never put credentials on the command
line. Source descriptions and models cannot issue approval themselves.

The sender enforces the reviewed digest and destination, current source/export
permissions and non-withdrawn lineage. Only the exact Slack HTTPS incoming-webhook
host/path is accepted; proxies and redirects are disabled and transport is bounded
by 10 seconds. Intent is persisted before POST, under an independent operations
lock. Only a 200/`ok` response is confirmed. Ambiguous delivery is never retried
automatically, including through a newly generated preview. Inspect the destination
manually; P6 deliberately has no force-resend switch. Ledger loss or a delivered
message cannot be repaired by restoring the evidence backup. Exactly-once delivery
and authenticated reviewer identity are not claimed. No destination or send was
configured during implementation.

## Subscription automation and local inference

The unchanged qualified Codex worker remains the sole production extractor.
`python3 -m tools.research_model_eval probe` runs an owned one-response smoke in a
child process with stdin closed and reduced environment. It records the exact
binary/config/client identity, Python/Codex paths, harness version and token/latency
metadata. It sends no research descriptions. A successful awake-session smoke
is not permission or proof of future unattended reliability.

After reviewing actual account suitability and the probe, `authorize --probe ID
--reviewer NAME --permission-reference REFERENCE` records an explicit operator
assertion, valid for seven days (a conservative review cadence, not a provider
rule). Add its ID as `unattended_qualification` in an explicitly reviewed plan.
Scheduled model steps require matching paths/hashes and active qualification;
otherwise they defer while local operation continues. Authentication/quota failure
halts the model batch and never selects an API key, paid tier or local fallback.
No schedule/model qualification was activated here.

Official documentation inspected 2026-09-09 distinguishes subscription sign-in
from usage-billed API keys, documents cached authentication, recommends API keys
for general programmatic CI workflows, and describes enterprise access tokens
for trusted automation. It does not establish this personal account's entitlement
to a long-running schedule: [authentication](https://developers.openai.com/codex/auth/),
[non-interactive mode](https://developers.openai.com/codex/noninteractive/).
That account/use review remains a genuine activation gate under the no-extra-cost
constraint; do not buy API access to resolve it.

`research_model_eval local --model INSTALLED_NAME` is a separate owned-fixture
experiment using an already-installed loopback Ollama server. It cannot pull a
model, fetch a repository, call tools, read research descriptions or become an
automatic fallback. Request settings and response timing/resident estimates are
recorded; prompts/schema and the original six-case P2 dataset are reused. See
[Ollama's generate contract](https://docs.ollama.com/api/generate), inspected
2026-09-09, and [measured results](phase6-validation.md). No new inference-quality,
18-GB memory-fit or held-out claim follows from model weight size alone.
