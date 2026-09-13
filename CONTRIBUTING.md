# Contributing to AI Job Skills Lab

AI Job Skills Lab extends the AI Job Search foundation for global AI engineering
research. Follow [PLAN_RESEARCH.md](PLAN_RESEARCH.md) and [AGENTS.md](AGENTS.md).
Contributions can improve code, documentation, evidence quality and usability.
While the repository is private, access requires an invitation. Once accessible,
use a fork and pull request where GitHub permits, or an authorized topic branch.
Contributing does not authorize a repository visibility change.

## Scope and design

Fix demonstrated problems, improve grounded decisions and retain upstream behavior.
Reuse shared Markdown specifications, portal contracts, state helpers and tests.
The canonical research specification lives in `.claude/skills/research/SKILL.md`;
`.agents/skills/research/SKILL.md` is a thin pointer. Do not duplicate command trees
or introduce a new framework/database without a concrete need and design review.

Research must remain independent of candidate fit, application trackers and known
skills. Preserve explicit application workflows. AI is the default; broader domains
use reviewed versioned packs. Provider candidates need demonstrated coverage gaps,
permission review and working retention behavior before activation. Successful
access or a collector’s license does not establish data-use permission.
No JobSpy dependency, access-control evasion or mandatory paid data service.

## Development setup

Use one development checkout. Keep personal profiles, source captures, credentials,
and generated research state outside it. Managed HTML reports and the synthetic
offline demo belong in the Git-ignored `reports/` directory.
Read [maintenance](docs/research/maintenance.md) and [security](SECURITY.md).
Never rebaseline the public-template manifest to accept personal content.

Try the [offline quickstart](docs/research/quickstart.md) before model setup.

Research tools use Python 3.10+ on macOS/Linux and the standard library. To prepare
a contributor environment, if these tools are not already installed:

```sh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install PyYAML==6.0.2
```

Bun is needed for portal fixtures/typechecks. Use a reviewed installation on PATH;
this checkout was tested with Bun 1.4.2. In a portal CLI you change, install its
existing dev dependencies with `bun install --ignore-scripts`. Do not add lifecycle
scripts or run downloaded source code as part of research inspection. LaTeX is
only needed when changing retained application document templates; see [SETUP.md](SETUP.md).
No model account is required for the ordinary fixture suite.

Run from the root, with the venv and Bun on PATH:

```sh
python3 tools/lint_skills.py
python3 tools/check_release.py
python3 -m unittest discover -s tests -t .
```

For each touched `.agents/skills/<portal>/cli`, run `bun run typecheck` and
`bun test`. CI also retains LaTeX smoke tests. The installed-runtime boundary test
is opt-in; follow [qualification](docs/research/runtime.md) when changing the
runtime or its contract. Never use real source collection, model inference or
external sends in ordinary CI. Synthetic fixtures must be identified as such.

## Propose and review a change

1. Check existing work in this repository. For a substantial change, describe the
   concrete gap and how the existing implementation fails to cover it.
2. Keep a change focused. Reproduce fixes through the actual supported interface
   where possible and add meaningful regression coverage. Preserve unknowns and
   distinguish executed validation from inspected code or proposed targets.
3. Update affected operations guides, contracts, source/domain versions, migration
   behavior and validation evidence. State what existing private state can safely
   read or restore; never silently reclassify historical evidence.
4. Review staged files for private content, source permissions and third-party
   provenance. Tests do not replace human review of model semantics or security.
5. Open the PR against **dharmendrathinks/ai-job-skills-lab**, not upstream. Use
   `gh pr create --repo dharmendrathinks/ai-job-skills-lab` only when authorized to
   publish the PR. Include the problem, resulting behavior, checks and limitations.

For maintainers with the PR Ready skill installed, run its analyzer using
`.pr-ready.json` before reporting completion. The baseline is a recorded review
checkpoint, not a release version; update it deliberately for a new review scope.
`check_release.py` runs security, template preflight and the framework-version
check against that same explicit base, including committed changes. A bad or
unavailable base fails; update `.pr-ready.json` to the intended review base before
a new review. This avoids a clean working tree hiding a committed version error.
The plugin is not a repository runtime dependency. Contributors without it can
run the listed checks and attach their results for maintainer review.

## Learning content and skill terminology

Read the [curriculum contribution guide](docs/research/curricula/README.md) to
improve a lesson, exercise or resource. Use the learning-content issue template
for a concrete learner problem and the skill-alias template for terminology or
topic corrections. Examples must be owned or suitably licensed; do not copy
private report content. Resource inspection, automated checks and human learner
review must be reported separately.

## Reports, conduct and licensing

Use this repository’s issue tracker for sanitized defects and proposals. Do not
include source descriptions, personal state or credentials. Report security findings
through [SECURITY.md](SECURITY.md), and follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

Contributions follow the [MIT license](LICENSE) unless explicitly identified
otherwise. Changes to the Apache-2.0 Codex adaptation must preserve its license
and [notices](THIRD_PARTY_NOTICES.md). Bundled Lato/Raleway fonts retain their
SIL Open Font License and copyright notices. Identify copied/adapted code, the source
revision and license; credit reports and coauthors accurately. Do not submit data
whose license or retention requirements are incompatible with distribution.

When a fix also benefits upstream, prepare a focused contribution under
[upstream’s own policy](https://github.com/MadsLorentzen/ai-job-search/blob/8c81edc330b98db0473dcb016e34db835c2fd378/CONTRIBUTING.md).
Sending it is a separate authorized action. Synchronize using the existing update
helpers and [conflict-review ledger](docs/research/maintenance.md).
