# Foundation, privacy and maintenance

## Repository transition

Development uses only `/Users/dhasharma/Dharmendra/Projects/ai-job-radar`.
`origin` is `https://github.com/dharmendrathinks/ai-job-radar.git`; GitHub
inspection found it private, empty, and not a GitHub-network fork. `upstream`
is `https://github.com/MadsLorentzen/ai-job-search.git`.

Local branch `research/phase1` starts from approved commit
`8c81edc330b98db0473dcb016e34db835c2fd378`, preserving its ancestry and files.
No GitHub fork was created, no visibility changed, and nothing was pushed.
The temporary sibling checkout used during transition was moved here and its
empty directory removed at the user's request; it is not a second workspace.

`PLAN_RESEARCH.md` remains active. Original `PLAN.md` is unchanged local history,
ignored from publication (original SHA-256:
`870e78df2bf0938c9aaf9ad7cdaaf69dadee97f332db50f9b7cf1a9bbc3c6fde`).
The upstream MIT license and Mads Lorentzen copyright remain unchanged. README
attribution distinguishes the upstream author's application results from this
research fork. No AI Trend Radar or JobSpy source was imported.

## Public template and private data

`research_preflight.py` is read-only. It resolves the macOS default
`~/Library/Application Support/ai-job-radar`, with `AI_JOB_RADAR_HOME` as an
absolute override; non-macOS defaults use XDG data storage. It rejects overlapping
checkout paths, including symlink aliases, and does not create the destination.
P2 owns actual private persistence and restrictive file creation permissions.

`research-template-manifest.json` contains reviewed public-template hashes.
Preflight checks both disk and index, so retaining placeholder tokens or
restoring a staged file's worktree does not hide personal content. Tracked files
matching ignore rules fail the guard. CI enforces this even on a private origin.
These are supported-entry-point and review checks, not OS write prevention or
a complete secret scanner. Review staged exports and the manifest itself.

Application `/setup`, including `--section`, and `/expand` stop before personal
collection/writes in this publishable template. Personal application onboarding
requires a separately reviewed private workspace, outside the development
checkout, with public pushing disabled. It is not created or configured in P1.
Do not bypass this by deleting the manifest, refreshing its hashes to personal
content, or adding tracked profiles to `.gitignore`. Existing application ranking,
fit rules, templates and tools are retained; this setup restriction is explicit.

When upstream changes a protected methodology file, inspect the content and
update the reviewed hash list only for accepted public template revisions.
There is intentionally no automatic rebaseline command. Two CLAUDE.md hashes
allow the original upstream header and the reviewed fork routing header only.

## Divergence and synchronization ledger

| Area / relevant paths | Fork decision and review requirement |
|---|---|
| `AGENTS.md`, `CLAUDE.md`, `.agents/skills/research/SKILL.md`, `.claude/skills/research/SKILL.md` | Early mode routing with one canonical specification; AGENTS version bumped. Review instruction precedence and runtime discovery after merges. |
| `.claude/commands/setup.md`, `.claude/commands/expand.md` | Explicit public-template preflight before every personal-write path; retain application workflow below the gate. |
| `.claude/skills/job-scraper/SKILL.md` | Research route before state loading; portal discovery requires a CLI manifest/entrypoint. Ordinary scrape selection remains upstream. |
| `tools/research_preflight.py`, `research-template-manifest.json`, `tests/test_research_preflight.py` | Fork-owned read-only state-path, template/index and capability checks. No collection, extraction or persistence implementation. |
| `.github/workflows/ci.yml`, `.github/workflows/upstream-watch.yml`, `.gitignore` | Template/version checks active on this repository; issue reporting is manual and doubly opted in; private/dev artifacts ignored. |
| `PLAN_RESEARCH.md`, `docs/research/`, `README.md`, `.pr-ready.json` | Roadmap/contracts/runtime evidence, attribution, reproducible checks and source-path inventory; public content only. |

Keep `tools/check_upstream_updates.py` and `tools/upstream_triage.py` intact.
The first checks a limited versioned list; the second covers commits. Extend
review coverage through this ledger, not by pretending versionless research
files are recognized by the version checker. Before synchronization:

1. Fetch upstream for inspection and record its exact candidate commit; do not
   merge automatically. Work on a local integration branch in this same folder.
2. Run both existing helpers with explicit `--remote upstream` (and upstream's
   actual branch). Use `--no-fetch` on the version checker when reviewing the
   already fetched candidate.
3. Inspect changes in the ledger's paths against the approved pin, including
   versionless specs and fork-owned paths, plus any other affected upstream
   components. Review conflicts semantically; clean merges are not validation.
4. Run version/lint/security/preflight, Python regressions and touched portal
   typechecks/fixtures. Rebaseline public-template hashes only after review.
   Requalify the extraction boundary if runtime or configuration changes.
5. Keep publishing, pushes, issues and outreach behind explicit authorization.

The upstream issue workflow has no schedule. It requires manual dispatch with
`publish_issue=true` AND repository variable
`AI_JOB_RADAR_ENABLE_UPSTREAM_ISSUES=true`. Neither was enabled here. Its retained
built-in token is scoped to this repository. Local helpers need no issue writes.

## Development checks

Python 3.13 was already installed. `.venv` uses it with PyYAML 6.0.2 for upstream
lint. Bun 1.4.2 is stored in ignored `.tools/bun-v1.4.2`; its macOS arm64 release
asset SHA-256 was checked against the official release metadata:
`90987a3a16d7db556d886ac3d551e7b6d3edf0a1cf43acaed622e8676be1d12f`.
Portal dependencies use upstream manifests, installed with `--ignore-scripts`.
No JobSpy dependency or new runtime dependency was introduced.

Use the venv Python (or activate it) for upstream lint and tests. Put the local
Bun directory on PATH as well: portal fixtures spawn `bun` by name, so invoking
the parent binary by absolute path alone is insufficient. From the checkout:

```sh
source .venv/bin/activate
export PATH="$PWD/.tools/bun-v1.4.2:$PATH"
python3 tools/lint_skills.py
python3 tools/check_framework_version.py
python3 tools/security_guards.py
python3 tools/research_preflight.py --mode research --action status
python3 -m unittest discover -s tests -t .
```

In each portal CLI use Bun for `run typecheck` and `test`. Ordinary tests use
fixtures; live collection requires source qualification. LaTeX checks remain
in upstream CI but are not a research prerequisite; P1 does not change TeX.
The PR Ready configuration uses the pinned foundation as its comparison base;
update that reviewed base when adopting a new upstream checkpoint.
