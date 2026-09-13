<p align="center">
  <img src="assets/mascot/pip_flight_loop.gif" alt="Pip, the upstream courier bird mascot" width="160">
</p>

# AI Job Skills Lab

**Learn the skills AI jobs require. Build useful projects. Share what you learn.**

Learn from the engineering problems organizations advertise. Turn inspected job
requirements into learning priorities, useful open-source work, product hypotheses
and engineering experiments you can explain and share.

> What engineering problems are organizations hiring people to solve, and which
> are worth learning, building for, validating commercially, or explaining through
> a real experiment?

AI Job Skills Lab extends [Mads Lorentzen’s AI Job Search](https://github.com/MadsLorentzen/ai-job-search).
Its Markdown workflows, portal tools, state helpers, conventions and tests are our
implementation foundation, pinned initially at
[`8c81edc`](https://github.com/MadsLorentzen/ai-job-search/tree/8c81edc330b98db0473dcb016e34db835c2fd378).
Application mode is retained with separate rules.

**Development version: v0.2.0 (unreleased).** This README describes current
`main`, including the connected learning workflow. The existing `v0.1.0` tag
points to `ba9c04f173ceca15e93fb2edb67b78613253f556`, before that workflow and the
rename. Do not use that tag expecting the current features. The repository remains
**private** until the owner explicitly changes visibility.

The seven roadmap phases have implementations and recorded validation; human
quality acceptance and several activation gates remain open. Start with the
[offline demo and setup guide](docs/research/quickstart.md), then consult the
[changelog](CHANGELOG.md), [next release notes](docs/releases/v0.2.0.md),
[historical v0.1.0 notes](docs/releases/v0.1.0.md) and [active roadmap](PLAN_RESEARCH.md).

## Learn, build and teach

The [learning delivery plan](PLAN_LEARN_BUILD_TEACH.md) connects specific skills
from job descriptions to one practical learning effort and its teaching experiment.
Use the [learning operations guide](docs/research/learning-operations.md) for bounded
detailed analysis, 30-day skill views, path selection, progress and cited questions.
Extraction coverage and human-quality review are shown separately; a completed
implementation does not mean every retained listing has been analysed.

Explore three starter curricula—structured outputs, document assistants and
reliable tool workflows—with a syllabus, exercises, completion checks and inspected
resource links. The **Skills tab remains independent**, grouping catalog skills
by engineering topic and offering frequency sorting, evidence and comparable-window
trends. Unresolved source phrases remain available in Observed terms.

Read the [curated workspace guide](docs/research/learning-workspace.md). The
curricula are editorial drafts pending maintainer and learner review; the offline
demo works without accounts, model calls or private research data.

## What it does

Research starts with AI product engineering, LLM applications and agents,
retrieval and data systems, evaluation, reliability, security, inference and
relevant ML infrastructure. Responsibilities matter more than titles.
Geography, language, seniority and work arrangements are analytical segments;
personal eligibility and already-known skills do not exclude market evidence.
Personalization happens after aggregation.

| Output | What you review |
|---|---|
| Learning priorities | Capabilities, prerequisites, direction and practical exercises |
| Open-source briefs | An inspected problem and alternatives, contribution versus new work, bounded architecture, tests and resource assumptions |
| Product hypotheses | User, buyer, workaround, supporting and contradicting evidence, validation and rejection criteria |
| YouTube experiment briefs | A real build, trade-offs, tests, possible failures and a separate discussion/audience validation plan |

All four are drafts. Missing repository, problem or discussion evidence can mean
insufficient evidence or no worthwhile project. Job advertisements do not prove
purchase intent, audience demand, actual employer practice or personal ability.
The four outputs are assessed separately; there is no combined popularity score.

## Start here

### 1. Clone and try the offline demo

Clone the project (collaborator access is required while it is private):

```sh
gh repo clone dharmendrathinks/ai-job-skills-lab
cd ai-job-skills-lab
python3 -m tools.research_demo
```

Open the printed HTML paths. Each run creates a fresh `reports/demo-…/` folder
with synthetic job evidence, skill cards, a learning path and project/YouTube
examples. No account, collection, model or personal setup is needed. These are
prepared examples, not measured extraction quality or successful experiments.
See the [quickstart](docs/research/quickstart.md) for supported runtime setup.

Use your own fork for contributions when repository access and GitHub permit it;
otherwise create a branch in a checkout you are authorized to write to. A clone,
contribution or release never authorizes changing repository visibility.
The upstream command `gh repo fork MadsLorentzen/ai-job-search`
creates a fork of a public repository; it is not the private-repository setup used
here. In application mode, upstream `/setup` writes personal data into tracked
files. This development template blocks those writes. See
[SETUP.md section 8](SETUP.md#8-pulling-upstream-updates-into-your-fork)
for the retained private-remote recipe and [application mode](docs/application-mode.md)
for this fork’s restrictions. Adding a tracked file to `.gitignore` does not hide it.

### 2. Check research readiness

From the checkout, use Python 3.10+ on macOS or Linux:

```sh
python3 tools/research_preflight.py --mode research --action configure
python3 -m tools.research_global registry
python3 -m tools.research_domain packs
```

These checks inspect readiness and the shipped registries; they do not collect
jobs, initialize a personal profile, run inference or activate a schedule.
Python research helpers use the standard library. Bun is for retained portal
CLIs; PyYAML is for development lint. Neither LaTeX nor a CV, application tracker,
Gmail or Notion is needed for research. See [contributor setup](CONTRIBUTING.md)
for development dependencies.

In Codex, ask it to use the `research` skill. The portable entry point refers to
[one canonical specification](.claude/skills/research/SKILL.md). Other agent
runtimes are not assumed to reproduce the complete qualified workflow.

### 3. Review permission and runtime requirements

Research state defaults outside Git: `~/Library/Application Support/ai-job-skills-lab`
on macOS, or `$XDG_DATA_HOME/ai-job-skills-lab` (default `~/.local/share/ai-job-skills-lab`)
on Linux. An absolute `AI_JOB_SKILLS_LAB_HOME` selects another private data workspace.
Existing installations retain access to the previous default and environment
variable; see the [rename and migration notes](docs/research/project-rename.md).
Do not point it at, inside, or above the development checkout. Runtime commands
can create state and apply expiry; the preflight above is read-only.

Read [evidence operations](docs/research/evidence-operations.md) before importing
or collecting. Only a narrow, capped Jobicy API path is currently reviewed for
explicit collection; its policy review expires **2026-10-09**. It is remote-biased
and does not represent complete worldwide coverage. Other provider candidates
remain gated. Default AI discovery now rotates across AI product/applied engineering,
LLMs, agents, retrieval, evaluation/security, infrastructure and relevant ML, rather
than repeatedly searching only machine learning. Inspect the plan with
`.venv/bin/python -m tools.research_global ai-query-plan`. Manual searches have no
hard hourly cooldown; scheduled polling retains the hourly guard. Collection is never activated by cloning or readiness checks.

Model analysis uses an existing ChatGPT sign-in through a **qualified Codex CLI
0.153.4 / gpt-5.5 installation**. The current qualification is for the recorded
macOS arm64 binary and configuration; arbitrary installs, upgrades and Linux model
execution are not qualified by this release. Consult the
[pinned binary setup](docs/research/quickstart.md#enable-real-analysis-on-the-supported-runtime)
and [runtime qualification procedure](docs/research/runtime.md).
No binary or model is bundled. Job-data services cost ₹0; no paid API fallback,
additional subscription or hosted service is configured. Quota exhaustion defers work.

The extraction worker has an enforced empty tool registry on that qualified
runtime. Acquisition and orchestration retain their tools. This is not OS/process
isolation. Hosted inference receives approved content and has provider-managed
retention; local storage does not imply local-only processing.

## Work through the research loop

Configure interests → collect permitted evidence → inspect descriptions → analyze
capabilities → review and select a brief → build or validate → record outcomes → refresh.

| Step | Guide |
|---|---|
| Capture, exact evidence spans, deterministic counts, withdrawal | [Evidence operations](docs/research/evidence-operations.md) |
| Inspect alternatives and other evidence; draft the four outputs | [Decision operations](docs/research/decision-operations.md) |
| Record decisions, observed versus reported outcomes, reviewed profile changes | [Outcomes and interchange](docs/research/outcome-operations.md) |
| Inspect source/language coverage and comparable time windows | [Global research](docs/research/global-operations.md) |
| Incremental runs, inbox, offline HTML, cleanup and managed recovery | [Continuous operations](docs/research/continuous-operations.md) |
| Opt into backend/platform research in a separate private data workspace | [Domain operations](docs/research/domain-operations.md) |

Generate the two local reports from existing results:

```sh
.venv/bin/python -m tools.research_ops report --limit 1000
```

Open `reports/jobs.html` for the jobs list and `reports/workspace.html` for
My learning path, Skills, Projects, YouTube and Progress tabs. `projects.html`
remains a compatibility redirect, preserving bookmarked fragments. Both report pages have offline search, filters
and a Clear filters button. Search and filters apply to the selected brief tab.
Reports are private, Git-ignored managed copies; their underlying data stays in
the private research workspace. This command does not collect or generate new
recommendations. Standalone learning drafts and secondary product hypotheses remain available; the review inbox is retained.

AI remains the default. The backend/platform pack reuses the same pipeline with
an immutable domain binding; it does not reclassify existing AI observations.
AI Trend Radar remains a separate repository, with selected read-only report
imports and reviewed Markdown/JSON exchange. Its consumer does not yet implement
the domain-aware 1.1 extension. JobSpy is not a dependency or wrapper.

## Evidence and current limits

Reports disclose sources, queries, filters, periods, receipt completeness,
deduplicated openings, employers, countries, languages and missing descriptions.
One scan cannot establish growth; added providers do not establish increasing
demand. Closed listings can be historical observations without being open vacancies.

The Phase 7 suite ran 603 tests: 602 passed and one opt-in installed-runtime test
was skipped. A separate real boundary qualification denied all nine forced tool
calls. The backend evaluation used 12 owned synthetic examples; provisional
capability/tool labels had 14 matching atoms, one extra and no missing expected
atoms. These are engineering checks, not human-adjudicated market accuracy.
See [validation details and disagreements](docs/research/phase7-validation.md).

Remaining gates include representative human extraction/brief review, useful
held-out evaluations, comparable historical windows, broader permitted coverage
and scheduled account-use/sleep/wake reliability. Scheduling and notifications
are off. Local inference has not been promoted. No market-growth, commercial or
video-performance result is claimed.

Only compatible logical deletion is supported. Withdrawal/expiry invalidates
linked artifacts and managed recovery/report copies; physical erasure, external
copies and hosted recall are not guaranteed. Sources requiring those guarantees
are blocked. Review [security](SECURITY.md) before using real evidence.

## Contribute and maintain

Read [CONTRIBUTING.md](CONTRIBUTING.md), [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
and [the contracts](docs/research/contracts.md). For updates, use the
[upstream synchronization ledger](docs/research/maintenance.md); for publishing,
use the [release procedure](docs/releases/README.md). Always select
`--repo dharmendrathinks/ai-job-skills-lab` with GitHub CLI commands: an inherited CLI
default can point at the upstream project.

## License and attribution

Project additions are [MIT licensed](LICENSE), except for the identified
Apache-2.0 runtime adaptation in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
Bundled Lato and Raleway fonts retain SIL Open Font License 1.1; their full
licenses and copyright notices are included beside the font files.
The original Mads Lorentzen copyright is preserved. Thanks also to
[Mikkel Krogholm](https://github.com/mikkelkrogsholm) for upstream portal skills.
Inherited release history is preserved [separately](docs/upstream/CHANGELOG.md).
Source-data permissions are separate from the software license.

AI Job Skills Lab is maintained by [Dharmendra Thinks](https://github.com/dharmendrathinks).
It is independent of OpenAI and Anthropic; references to their products describe
the toolchain, not endorsement.
