# First-visit learner acceptance

Status: **not run with human participants**. This is the study protocol and blank
record, not evidence that the experience is usable. Maintainers can run it without
collecting personal job data, account details or private work.

## Setup

Invite five developers who have not used the project. Include people unfamiliar
with applied AI and people who already work with APIs and tests. Use anonymous
participant labels P1–P5 and record Python/browser versions and approximate screen
width. Ask permission before recording the session; written observations suffice.

Start from a fresh checkout and the quickstart. Use only the fictional first-visit
demo (`python3 -m tools.research_demo --first-visit`) and a new practice directory.
Do not show the reference solution or explain navigation before the tasks.

## Tasks to give participants

1. Generate and open the learning workspace. Explain what is fictional and whether
   any work has already been recorded for you.
2. Choose a suitable first lesson. Explain the prerequisite and the artifact you
   expect to produce.
3. Export the first-lesson kit, run its tests and explain the initial failure.
   Implement the contract and add one case of your own. The exercise can continue
   after the navigation session; do not coach to meet a time limit.
4. Explain the completion check and one limitation of the tests. Use the reference
   only after attempting the exercise, and record that it was consulted.
5. Find Python in Skills, follow one count to its exact captured source, and explain
   why frequency is different from learning priority or market growth.
6. Write an actual result in the local work log. In a separate active-path demo,
   prepare a Record this lesson request using a clearly labelled practice account.
   Explain whether the browser saved anything. Do not submit a synthetic result
   to a real research workspace.

Observe wrong turns, uncertainty, inaccessible controls, ambiguous copy and lost
work. If a participant asks for help, record the request and give help only after
marking the task as assisted. Distinguish product defects from missing prerequisites.

## Record results

| Participant | Setup/browser/width | Tasks completed without help | Blocker or wrong turn | Reference consulted | Follow-up issue |
|---|---|---|---|---|---|
| P1 | Not run | — | — | — | — |
| P2 | Not run | — | — | — | — |
| P3 | Not run | — | — | — | — |
| P4 | Not run | — | — | — | — |
| P5 | Not run | — | — | — | — |

Record timings as observations, not as a score of the participant. Preserve exact
confusing labels and their expected behavior; avoid storing identifying details.

## Acceptance decision

Before calling onboarding validated, all five participants should open the report,
reach an appropriate exercise and interpret the sample without coaching. At least
four should finish the first contract exercise and explain its completion boundary
without implementation hints. All five should understand that preparing a progress
request does not save it. Resolve any loss of work, false completion claim or
inaccessible primary action before accepting the flow. These are project targets,
not a scientific usability benchmark; repeat affected tasks with fresh participants
after material fixes.

Separately have a maintainer review each curriculum's sequence, prerequisite fit,
resource sections, hints and effort estimates. A five-person study cannot establish
curriculum effectiveness or market relevance.

## Browser acceptance checklist

At widths 1440, 768 and 390 CSS pixels, inspect the first visit, an expanded lesson,
its practice command, the Skills group list and a progress request. Check wrapping,
horizontal overflow, visible focus, Tab order, arrow-key tabs, next/previous lesson
links, direct bookmarks, reload, Back, and clipboard failure. Also check 200% zoom
and JavaScript disabled. Record browser/version, actual viewport and each result;
an automated DOM fixture is not a visual or screen-reader audit.
