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
/Users/dhasharma/Dharmendra/Projects/ai-job-skills-lab/.venv/bin/python -m tools.research_ops health
/Users/dhasharma/Dharmendra/Projects/ai-job-skills-lab/.venv/bin/python -m tools.research_ops configure --input /absolute/private/operation-plan.json
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
`{"source":"jobicy","query":"AI product","count":100}`, `analyze` can be
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

`report` generates two managed private HTML files from existing evidence and briefs:

```sh
.venv/bin/python -m tools.research_ops report --limit 1000
```

For the default AI workspace these are `reports/jobs.html` and
`reports/projects.html` under the development checkout. This location is an
explicit user-approved exception for generated views only: corpus, profiles,
credentials, state and journals remain outside the checkout. `reports/` stays
Git-ignored. Files have 0600 permissions and the directory 0700. Do not force-add
these files, publish them, or copy them outside managed storage.

Jobs shows conservative deduplicated openings, latest captured descriptions,
source identity/revisions, availability at capture, missing data, latest analyses
and collection scope/receipts. The second file has My learning path, Skills, Projects, YouTube and Progress tabs
(secondary product hypotheses and the existing inbox remain available), including honest no-project/insufficient-evidence
outcomes and latest decision status. Rejected, accepted and deferred project
briefs remain inspectable through filters; superseded revisions are excluded.
The 1–1000 limit applies independently to jobs, project briefs and YouTube briefs,
with per-tab total/overflow displayed; YouTube shares `projects.html`, not a third file.
Search and filters cover the generated entries, not entries beyond that limit.

Both pages use responsive typography, separate color accents, metric cards and
expandable evidence. Jobs filters source/location/availability; the selected brief tab filters
disposition/decision/capability. Jobs also provide a Role family filter. Versioned
`report-title-families/1` rules group the latest displayed title into overlapping
families (machine learning, AI product engineering, applied AI, LLM/generative AI,
agents/automation, retrieval/knowledge, evaluation/reliability, AI security,
infrastructure/MLOps, research/applied science, data science, data engineering,
and general AI engineering). Unmatched titles stay Other / unclassified.
These are English title navigation hints, not validated AI relevance or requirement
classifications; no descriptions, collection queries or profiles determine them.
They do not enter market counts or extraction artifacts. Location uses the normalized country when present, otherwise the captured
`segments.source_geography`. Fallback chips are labeled source location. Regions,
Anywhere and multi-country strings stay as published, without guessed country
codes or country-count changes. Location/availability controls are omitted when
all displayed listings have unknown values; known and
unknown values remain filterable together when real values exist. Empty role
facets are also omitted. Filters reflect the generated sample, not hidden overflow.
Switching tabs resets search/filter selections and
rebuilds choices from that tab alone. Clear keeps the active tab. Tabs support
Arrow Left/Right and Home/End keyboard navigation. Search matches all terms without case sensitivity,
on each input event. Titles are searched by default; Search in → All content includes
collapsed descriptions and evidence. Clear filters resets search, scope to Titles, and
filters within the active tab. These controls
only change the current browser view and never acknowledge, accept, collect or
run a model. Source text is escaped. One fixed inline UI script is authorized by
its exact CSP SHA-256; arbitrary scripts and network connections remain denied.
Only fixed sibling-page navigation links are active. There are no remote assets,
external fonts, forms, analytics, local storage or local server.

Private `report-location.json` and `report-origin.json` bind the managed checkout
location; a workspace ownership marker prevents collisions. Nondefault workspaces
use `reports/workspace-<workspace-path-hash>/` with the same two filenames. Binding
rejects symlinks, tracked reports, lost markers and changed repository locations.
A missing binding fails closed and needs reconciliation of the existing managed
copies; never delete markers to bypass it. Moving the checkout requires deliberate
location migration, not editing source data to redirect file writes.

The `offline-report` artifact now has payload version 2 with both HTML pages and
counts, retaining transitive evidence/decision dependencies. Regenerating replaces
v1 and removes the old private `research-report.html`. Ordinary persistence removes
stale copies before state replacement, then materializes valid pages atomically
one file at a time; failure removes a partially written pair. Interrupted temporary
files are removed on next access. There is no multi-file/fsync/power-loss guarantee.
Withdrawal or expiry removes both pages conservatively when their artifact becomes
invalid; regenerate from survivors. Existing v1 artifacts remain readable until
regeneration. Do not downgrade the writer after creating v2 report artifacts.

Each page is bounded to 16 MB; lower the generation limit if needed. The browser
may retain an already-open view; close it after withdrawal/expiry. No browser-cache
recall, hosted recall or physical erasure is claimed. No source export permission
is expanded by the approved local destination.

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

Manual `run` collection passes `scheduled=False`; unattended `tick` collection
passes `scheduled=True` to the shared source helper. Only scheduled collection
uses the one-hour source guard; explicit searches no longer share that manual
cooldown. Polling cadence, intent recording, ambiguous-attempt review and no-retry
behavior remain unchanged. Existing plans keep their explicitly configured queries;
changing defaults does not mutate private plans. Use `research_global ai-query-plan`
to inspect the wider default AI discovery seeds and `research_evidence collect`
for the next seed in a user-triggered search session.

The connected learning refinement and `learn-refresh` operation are documented in
[learning operations](learning-operations.md). Legacy plans default to v1 extraction;
reviewed AI plans can enable `skill_details: true` for latest-observation v2 analysis.
