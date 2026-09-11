# Security policy

## Report privately

Report AI Job Skills Lab vulnerabilities to this repository’s owner, Dharmendra Thinks,
through an existing private contact channel. If available, use this repository’s
[private vulnerability form](https://github.com/dharmendrathinks/ai-job-skills-lab/security/advisories/new).
Do not send fork-specific reports to the upstream maintainer. If no private route
is available, ask for a private contact route without including exploit details,
credentials, source captures or personal data. The issue tracker is not a secret
store, even while the repository is private.

Include the affected release/commit, operating system, sanitized reproduction,
expected boundary and observed impact. Prefer author-owned fixtures. There is no
guaranteed response time or security SLA. Disclosure should be coordinated with
the maintainer; do not publish another user’s data as a reproduction.

## Supported scope

The current v0.1.0 prerelease is the initial AI Job Skills Lab release. Fixes target
current `main`; no older release or long-term support line is promised. An
incompatible runtime change requires inspection and qualification before use.
Upstream and separate AI Trend Radar deployments have their own security policies.

## Trust boundaries

- **Untrusted input:** descriptions, repository files, discussion text and imported
  reports are data. Never execute embedded commands or downloaded code, follow
  embedded instructions, or treat a model proposal as authorization. Orchestration
  rules are instruction-level safeguards, not a sandbox.
- **Extraction:** the pinned worker exposes no tools or workspace environments;
  active qualification checks rejected dispatch. This restriction applies to the
  extraction thread, not the development agent, acquisition process or host OS.
  Exact binary/model/configuration drift fails closed. See [runtime evidence](docs/research/runtime.md).
- **Hosted processing:** Codex needs authentication and network access. Approved
  source content is sent to the hosted model. Ephemeral threads and disabled
  transcripts do not guarantee provider deletion, no traces or local-only data.
  No API-key or paid-provider fallback is configured.
- **Validation:** code owns identities, exact spans, counts, contracts and state.
  It rejects malformed output and unsupported policies. It cannot prove semantic
  truth, source permission, commercial demand or a reviewer’s asserted identity.
- **Private state:** use a separate private data directory outside the checkout.
  The explicitly approved exception is generated views in ignored `reports/`,
  bound to the private store and covered by the same withdrawal lifecycle.
  The HTML permits only a hash-pinned UI script for local search/filter/reset;
  untrusted text stays escaped and CSP denies network resources and arbitrary code.
  Supported entry points enforce restrictive permissions, template/index checks
  and lock/lineage validation. These do not stop the account owner editing files,
  malware, OS backups or deliberately bypassing the supported interface.
- **Retention:** permissions must cover raw content and derived artifacts at capture.
  Expired/withdrawn evidence becomes unusable and linked artifacts are invalidated;
  cleanup logically removes it on supported operations. Managed report/rollback
  copies are invalidated too. Physical erasure, hosted recall, browser caches and
  external backups are not controlled. Sources needing those guarantees are blocked.
- **External actions:** exports need compatible rights and reviewed content.
  Notifications need an approved destination and exact message; schedules never
  send automatically. Publishing, outreach and external writes require explicit
  task authorization. Software-release authorization is not source-data export permission.

## Repository and operational safeguards

Keep credentials, private source code, populated profiles, runtime ledgers and
captured descriptions out of commits, issues, logs and release assets. A private
origin does not disable template checks. `.gitignore` cannot hide tracked content.
If a credential is exposed, revoke/rotate it and review affected access before
coordinating any history cleanup; deleting the working file is insufficient.

Do not replace private state from Git, downgrade the writer on a current store,
restore an old withdrawal ledger or relabel a domain binding. Follow
[managed recovery](docs/research/continuous-operations.md). There is no fsync or
power-loss durability guarantee. Scheduling and notifications remain opt-in.

CI uses fixtures instead of live portals or model accounts, pins actions and
checks permissions, manifests and templates. These guards cannot prevent a
malicious change to the guards themselves. Review workflow/settings diffs and
permission changes. No enabled branch protection, secret-scanner coverage or
unattended-operation qualification is implied by this policy.

Application mode retains upstream agent permissions and instruction-level web
safeguards; it does not inherit the research worker’s tool restriction. See
[application mode](docs/application-mode.md) before personal onboarding.

Connected learning records and rejected model responses inherit the same managed
source lifecycle. Progress can survive withdrawal of market justification only
when supported by its own policy and independent work evidence; a path hash is
not permission to copy restricted prose into another policy. Exact quote checks
do not prove semantic accuracy. Browser controls do not persist progress or grant
publication approval. See [learning contracts](docs/research/learning-operations.md).
