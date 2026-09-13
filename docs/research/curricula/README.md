# Contributing a learning path

This library contains original editorial drafts for developers moving into applied
AI. It is available offline; following external resource links requires internet.
The curricula have not yet passed maintainer review or the five-learner acceptance
study. Resource inspection is not the same as curriculum approval.

Each path JSON specifies its audience, outcome, skills, topics, prerequisites and
ordered lessons. Lessons have stable IDs, an explanation, an original worked
example, an exercise, a completion check, an artifact, effort estimates and one
or two resource IDs. Prerequisite IDs must refer to earlier lessons. Keep the
examples runnable with the standard library where possible; clearly identify
optional libraries, model setup and hardware needs.

Resources live in `resources.json`. Record a descriptive title, the exact section,
why it helps, the inspected date, inspection limits and access requirements.
Read the primary page before updating its checked date. Write original summaries;
do not copy course chapters or vendor examples into this repository. A working
URL alone does not establish that the content teaches the lesson.

For a change:

1. Explain the learner problem and the intended observable outcome.
2. Edit the smallest relevant lesson, resource or foundation refresher.
3. Increment that document's revision. Keep existing lesson IDs stable unless the
   lesson's meaning changes; selected paths retain their frozen previous content.
4. Run `python3 -m unittest tests.test_research_curricula tests.test_research_demo`.
5. Generate `python3 -m tools.research_demo`, inspect the rendered lessons, and
   record whether examples were run and whether a human reviewed the explanation.

Resource links were inspected on 2026-09-13 using their primary documentation or
course pages. The examples here are original, small teaching examples. Following
a linked notebook may require additional libraries, accounts or hardware; none is
installed or enabled by browsing the report.

Topic assignments in `../skill-topics-v1.json` are editorial navigation. Catalog
aliases in `../skill-catalog-v1.json` are terminology assertions, not evidence that
a job requests a skill. Preserve ambiguous terms until their meaning is reviewed.
A new projection may apply an exact alias of the same type; existing observations,
analyses and persisted snapshots are never rewritten.
