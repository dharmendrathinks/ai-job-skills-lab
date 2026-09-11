# Retained application mode

AI Job Skills Lab’s default is engineering research. Explicit application requests use
the retained AI Job Search lifecycle: `/setup` → `/scrape` → `/rank` → `/apply` →
`/interview` → `/outcome`, plus `/expand`, `/upskill` and the existing supporting
commands. Their canonical specifications remain under `.claude/`; portal CLIs
remain under `.agents/skills/`. Markdown workflow specifications are implementation.

Application ranking can use candidate fit, preferences and known skills. Those
rules do not admit or exclude research evidence. Research does not require the
candidate profile, tracker, application documents or LaTeX.

## Personal setup is blocked in this development template

The reviewed template manifest protects tracked placeholders even with a private
origin. `/setup` and `/expand` stop before personal collection/writes here. Personal
application onboarding needs a separately reviewed private application workspace
with public pushing disabled. Do not delete the manifest, change its hashes to
personal data or assume `.gitignore` makes tracked data private. Such a personal
workspace is not a second development checkout and is not created by the release.

[SETUP.md](../SETUP.md) retains the upstream application installation and document
instructions. Read this gate first. Do not install Claude Code, Bun or LaTeX merely
to run research readiness. Upstream application runtime compatibility does not
establish compatibility with the research extraction worker.

For the original user guide, command descriptions and upstream author’s own job
search results, consult the
[pinned upstream README](https://github.com/MadsLorentzen/ai-job-search/blob/8c81edc330b98db0473dcb016e34db835c2fd378/README.md).
Those results belong to the upstream author; they are not AI Job Skills Lab evaluations.
Review [security boundaries](../SECURITY.md) and source-specific conditions before
running retained portal tools. An installed portal is not automatically permitted
for research. No application, message or publication is sent just by selecting a job.
