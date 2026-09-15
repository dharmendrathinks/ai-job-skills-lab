# Learning workspace validation — 2026-09-13

This record distinguishes implementation checks from evidence of teaching quality.
The curricula remain editorial drafts until maintainers and learners review them.

## Automated checks

The repository test suite covers legacy learning paths alongside the new curriculum
workflow. The added scenarios check:

- All three curricula and shared foundations load without private state or network
  access; every checked-in worked example executes.
- Invalid prerequisites, resources and preferences fail validation. Selected
  curriculum content stays frozen across subsequent editorial edits.
- Curriculum-only proposals and briefs need no model. Optional adaptation retains
  the syllabus and evidence boundaries; missing source permissions block inference.
- Rejection is respected before cache reuse. Correcting recorded work retracts
  dependent briefs and reports while preserving audit events.
- Exact typed aliases project into new snapshots without rewriting observations,
  analyses or historical snapshots.
- Reviewed synthetic cohorts produce within-sample shares; incompatible extraction,
  normalization or withdrawn evidence prevents changes from appearing as trends.
- Generated fragment links resolve at both full and small display limits.

`tests/workspace_ui.cjs` exercises the bundled JavaScript using a deterministic
local DOM fixture: tabs, grouped/frequency/name sorting, search, skill views, deep
links, refresh and Back routing, lesson expansion, and clipboard fallback. It
does not replace a real browser accessibility or layout test.

Run the complete checks through `.pr-ready.json`, using the repository virtual
environment on `PATH`. The final assessment output supplies the exact test count
and readiness verdict; no live collection or model qualification is implied.

## Report and visual inspection

The managed report was regenerated from existing private evidence. All 593 job
records, 10 project briefs and 8 YouTube briefs remain available. The current
30-day slice contains 37 catalog skills and 89 source terms awaiting review,
drawn from only three detailed in-domain openings. These counts describe this
local snapshot, not product coverage or market demand.

Both report files were checked for duplicate IDs and broken internal links.
A separate fresh synthetic demo demonstrates the three curricula, illustrative
progress and a clearly labelled synthetic trend comparison without private data.
Generated reports remain ignored and are not release fixtures.

An initial desktop Chrome preview was inspected through native accessibility and
a screenshot. Its excess vertical spacing led to a more compact active-path
header. A dedicated browser automation connection was unavailable, and subsequent
native preview actions were repeatedly interrupted by changes in the active
Chrome window. The final layout and mobile/tablet layouts have **not** completed
visual acceptance. Keyboard behavior has automated fixture coverage, not a full
screen-reader audit.

## Human acceptance still needed

Have a maintainer review each curriculum's prerequisite order, examples, resource
fit and effort estimates. Then ask five developers unfamiliar with the project
to choose a path, find the next exercise, explain its completion check, locate a
skill's evidence, and distinguish frequency from a learning recommendation. Record
where they get stuck and whether they complete the tasks without coaching.

Before describing the experience as release-polished, inspect the final offline
demo at desktop, tablet and phone widths; check overflow, focus, deep links and
clipboard fallback in an actual browser. No learner study, accessibility
certification or model-adaptation quality review has been performed in this change.

## Follow-up — 2026-09-14

The first-visit demo now starts with no selected path or fictional progress.
Onboarding links directly to a first lesson and its offline practice kit. All
15 lessons have expected-result, common-mistake and reflection guidance; each
worked example was executed as a standalone Python file. The three starter kits
were exported to temporary directories, their intended initial failures confirmed,
and their reference solutions run against the same tests. Existing work is not
overwritten. Exporting opens no research Store and makes no network/model call.

The JavaScript fixture also checks lesson-specific progress requests: empty input
cannot be copied as a result, a changed account is reflected before copying, the
request remains self-reported, and reload clears form inputs. No progress event
is written by these controls. Empty and three-opening sample cases have explicit
denominator explanations. No new real job analysis was performed.

A separate native Chrome window successfully displayed the revised active-path
demo. Its desktop screenshot and accessibility tree showed the syllabus, expected
results, hint, reflection, progress disclosure and next/previous links. After
attempting device-preview controls, the tool returned only the window title and
reported screenshots unavailable; reconnecting and resetting the tool did not
restore inspection. Final first-visit/mobile/tablet/zoom visual acceptance remains
pending. Do not infer that the automated DOM tests cover those checks.

The [learner acceptance protocol](learner-acceptance.md) supplies six tasks,
five blank participant records, acceptance targets and a browser checklist. No
participant sessions or independent maintainer curriculum review were performed.
