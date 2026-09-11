# Make AI Job Radar guide what you learn, build and teach

Status: approved plan, implemented with evaluation and corpus-coverage gates still open.
See [the operations guide](docs/research/learning-operations.md) and
[validation evidence](docs/research/learning-validation.md). This document extends the active
`PLAN_RESEARCH.md` seven-phase roadmap; it does not replace its product scope,
fork-first foundation, application/research separation or evidence controls.

## Summary

The project should help you answer **“What should I learn next, and how will I practise it through a useful project?”**

A skills list is an essential missing piece. Its value comes from connecting each skill to actual requirements, a learning sequence, a practical deliverable and evidence of what you learned.

The inspected implementation has useful foundations, but the experience is disconnected:

- The generated report contains **593 listings, with only 40 analysed** through a deliberately selected sample.
- Requirements are mapped into ten broad capabilities—too coarse for deciding what to practise.
- Tool names have duplicates such as `Python`/`python`, and inappropriate entries such as `H1B` and `RSU`.
- Learning briefs are absent from the HTML report.
- Project and YouTube briefs are separate proposals, rather than stages of one learning effort.

These counts describe the inspected report, not a permanent product limit or a representative market sample.

Research supports treating skill extraction as a distinct task with explicit annotation guidelines and evaluation, rather than simply collecting keywords. [SkillSpan](https://aclanthology.org/2022.naacl-main.366/) provides a relevant methodological reference.

**Selected direction:** applied AI products; software-building experience with growing AI expertise; **10–15 hours weekly**; retain **HTML reports plus Codex**. These are user-selected planning preferences, not evidence of demonstrated skills or permission to write a personal profile without its existing review process.

## The experience to build

Keep the two existing files:

- **`jobs.html`:** inspect job descriptions, requirements and their evidence.
- **`projects.html`:** become the learning workspace, with **My learning path, Skills, Projects, YouTube and Progress** tabs. Open on the learning path.

Before selecting a path, show up to three justified options. After selection, foreground one active path and its next practical milestone. Do not fill a recommendation quota when evidence is weak.

Each path connects:

**Job requirements → specific skills → prerequisites → practice → useful build → evaluation → teaching → recorded learning.**

For example, an *illustrative* path could be “Build a document assistant that knows when it lacks an answer.” It could connect retrieval, structured responses and evaluation to a working application, failure tests and an eventual explanation of the results. This is an example of the desired structure, not a claim that it is currently the best project.

The report must show:

| View | What it helps the user decide |
|---|---|
| Skills | What organizations explicitly request, how frequently it appears in this sample, and what the work involves |
| My learning path | What to practise next, prerequisites, useful resources and completion checks |
| Projects | Whether to practise an existing implementation, contribute to a repository or create a justified new artifact |
| YouTube | What engineering question and actual results can become a useful lesson |
| Progress | What was attempted, tested, understood, corrected and still needs practice |

Keep product and monetization hypotheses available as secondary assessments attached to relevant projects. They must not drive learning priorities or imply customer demand.

Static report controls handle browsing, filtering and navigation. Selections and progress updates go through Codex and the managed state helpers; the HTML must not pretend that clicking a checkbox saves authoritative progress.

## Implementation changes and delivery order

These are improvements within the approved seven-phase roadmap, not a replacement architecture.

### 1. Deliver trustworthy skills and a visible Skills view

*Extends Phases 2, 3 and 6.*

**Improve extraction.** Version the existing extraction contract to add specific skill mentions while retaining the ten capability categories and compatibility with historical analyses.

Distinguish:

- Engineering practices: designing evaluation datasets, handling tool failures.
- Knowledge: retrieval methods, model-selection leakage.
- Technologies: Python, PostgreSQL, LangGraph.
- Other requirements: experience, qualifications, work conditions.

Retain exact description spans, required/preferred/unspecified status and supporting section context. Benefits, immigration terms, negated requirements and company aspirations must not become technical skills.

Add a versioned **SkillCatalog** with canonical names, aliases, definitions and relationships to broader capabilities. Preserve original wording; uncertain mappings remain unresolved. Model suggestions cannot silently merge concepts. Use ESCO’s distinction between concepts and their alternative labels as a reference, without importing its entire taxonomy or adding an API dependency. [ESCO skills pillar](https://esco.ec.europa.eu/en/about-esco/escopedia/escopedia/skills-pillar)

**Complete analysis systematically.** Extend the existing resumable queue to prioritize the latest retained descriptions missing the required analysis version. Expose pending, failed, excluded and analysed counts. Process the eligible corpus in bounded batches, preserving quota and runtime controls; do not silently substitute another selected sample.

**Add SkillSnapshot.** For each skill, calculate:

- Distinct openings mentioning it, counted once per opening.
- Required/preferred/unspecified counts, with overlap disclosed.
- Share of successfully analysed, in-domain openings in the selected slice.
- Reported employer-name breadth separately from verified employer identities.
- Relevant responsibilities, co-occurring skills and linked quotations.

Keep collection coverage and analysis coverage visible beside every ranking. Missing analysis is unknown, not absence of a skill.

Default to **skills observed during the last 30 days**, using capture dates and explicitly showing actual collection coverage. Offer a separate publication-date view; never substitute capture dates for missing publication dates.

**Completion:** the user can explore specific skills, inspect supporting jobs and understand the denominator without opening raw JSON. Historical v1 analyses remain readable and are visibly distinguished from the new extraction coverage.

### 2. Connect skills to learning, projects and teaching

*Depends on step 1; extends Phases 3, 4 and 6.*

Add a versioned **LearningPath** linking its skill snapshot, selected skills, prerequisites, milestones, resources, project brief and YouTube experiment.

Each milestone specifies:

- What to understand and what to implement.
- A small practical self-check.
- Inspected documentation, examples or papers.
- Expected artifact and tests.
- Effort range and hardware/cost assumptions.
- What completion would—and would not—demonstrate.

Add `learning-resource` to the existing reviewed context acquisition contract. Reuse bounded page/repository inspection, provenance and retention handling. Do not create another research crawler or invent resource links.

Separate **market frequency** from **personal learning priority**. Learning recommendations explain direction fit, prerequisite readiness, transferable value and feasibility. Preserve known skills and offer deeper practice. Missing profile evidence does not establish missing ability.

Generate project and teaching briefs from the **same selected path and experiment**. Inspect alternatives relevant to that problem, rather than repeatedly drawing from a fixed group of evaluation repositories.

Permit three honest outcomes: practice an existing solution, contribute a meaningful extension, or create a justified new artifact. Practice does not require novelty; an open-source contribution needs a demonstrated additional benefit.

Add **LearningProgress** events for attempts, self-checks, inspected changes, tests, failures and lessons. Reuse existing decision/outcome mechanisms. Keep user-owned work evidence independently attributable so withdrawing job evidence removes its market justification without falsely erasing independently supported learning.

YouTube planning begins with a proposed question; results and final teaching claims are added only after inspected work. Discussion/trend evidence can inform audience relevance through existing context/Radar imports, but its absence does not prevent an honestly labelled learning experiment.

**Completion:** one selected path works end to end through reports and Codex, including a recorded failed test, corrected implementation and evidence-scoped learning update.

### 3. Add longitudinal views and questions over the evidence

*Branches from step 1 and can progress alongside step 2; extends Phases 5 and 6.*

**Monthly observations:** reuse existing coverage, cohort and scheduling components. Display collection gaps, provider/query changes, analysis versions and missing descriptions alongside time buckets.

Keep descriptive monthly observations separate from comparable demand changes. Online job advertisements have occupational and geographic coverage biases; they are not a complete market census. [Cedefop representativeness assessment](https://www.cedefop.europa.eu/en/publications/6217)

Use adjacent 30-day windows for the new comparison option while preserving existing 28-day cohorts. Enable change indicators only when the existing completeness and comparability requirements pass. Jobicy’s current partial receipts must not be relabelled complete to enable charts.

**Evidence questions:** add an `ask` action to the existing research command interface:

- Counts and rankings use deterministic SkillSnapshot queries over the complete selected slice.
- Explanations retrieve relevant retained descriptions and skill evidence, then use the qualified tool-free worker to produce cited answers.
- Recommendations use the learning workflow and its reviewed preferences.

Start retrieval with canonical skills, aliases, metadata filters and lexical matching. This supports useful questions without a vector database. RAG retrieves relevant material for an answer; it is not the mechanism that maintains historical demand counts. [Anthropic’s retrieval explanation](https://www.anthropic.com/engineering/contextual-retrieval)

Embedding-based retrieval remains a bounded experiment: adopt it only if held-out questions demonstrate a useful retrieval improvement within the existing cost and machine constraints.

**Completion:** “How often was skill X requested?” reproduces the skills table exactly; “What work involves skill X?” returns relevant citations; insufficient evidence produces an explicit limitation.

## Validation, defaults and remaining blockers

### Validation

- Build a human-reviewed, held-out description set covering the AI role families, indirect skill wording, aliases, requirements versus preferences, negation and irrelevant mentions.
- Proposed extraction targets: **≥95% precision and ≥85% recall**; exact citation/span validation remains mandatory. These are targets, not measured results.
- Test deduplication, denominators, repeated mentions, employer uncertainty, date boundaries, partial analysis and provider changes.
- Test expiry and withdrawal across skill snapshots, retrieved answers, paths, reports and caches.
- Compare learning paths with the current report and a straightforward LLM prompt over identical evidence. Review usefulness, prerequisite order, feasibility, repetition and consideration of existing projects.
- Verify typeahead, filters, clear controls, keyboard navigation, cross-report links and honest progress behaviour in the generated HTML.
- Retain upstream application and existing research regression checks.

### Defaults

One active learning effort; up to three initial alternatives; 10–15 hours weekly including teaching preparation. Collection stays broad across AI responsibilities; applied AI preferences affect recommendations afterward. Preserve the private repository, two managed reports, existing Python/state/runtime architecture, ₹0 job-data budget and separate AI Trend Radar project.

### Concrete blockers

There is no blocker to implementing the skills view and connected learning workflow. Reliable demand-change claims remain blocked by incomplete collection history and partial source coverage. Human-reviewed extraction quality and recommendation usefulness remain unestablished. The inspected Jobicy authorization expires **9 October 2026**; permitted continued use and historical retention need review before promising multi-month comparisons.

The implementation delivers specific skill evidence in the report and connects it
to draft learning paths, shared project/teaching briefs and independently sourced
progress. Remaining extraction batches and the evidence gates above must be
reported separately from feature delivery; generating a path does not select it
or record actual learning.
