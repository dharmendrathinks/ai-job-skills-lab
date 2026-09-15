# Curated learning workspace

Open `reports/workspace.html` (Skills & Learning Workspace). The former
`projects.html` address redirects locally, preserving the query string and fragment.

The offline report keeps My learning path, Skills, Projects, YouTube experiments
and Progress. Skills is an independent explorer with Browse skills, Trends and
Observed terms. It does not require selecting a curriculum.

See the [validation record](learning-workspace-validation.md) for implemented
checks and the remaining browser and learner acceptance work.

## Start without a model or private research data

Use Python 3.10+ (the repository virtual environment is suitable):

```sh
python3 -m tools.research_demo
python3 -m tools.research_demo --first-visit
python3 -m tools.research_decisions curricula
python3 -m tools.research_decisions curriculum-inspect --curriculum structured-output
```

The demo creates a fresh ignored directory and includes all three curricula,
fictional job evidence, illustrative progress, and an explicitly synthetic trend
comparison. It opens no Store and makes no model or network calls. The trend
illustration is not a qualified cohort; it also explains an unavailable scenario.
The two curriculum inspection commands do not open a private Store either.

The `--first-visit` variant omits the selected path, fictional work and generated
briefs. It opens the onboarding guide and keeps Skills available independently.
See the [first-exercise walkthrough](quickstart.md#finish-your-first-exercise-without-an-account).

Each curriculum offers a first-lesson practice kit. For example:

```sh
python3 -m tools.research_practice --curriculum structured-output --output ../structured-output-practice
```

This exports only repository-authored starter code, tests, a separate reference
solution, instructions and a blank work log. It requires a new output directory
outside the checkout and never overwrites existing work. It does not open a Store,
run the exported code, call a model, install packages or record progress.

Create an unselected curriculum draft in your normal private research workspace:

```sh
python3 -m tools.research_decisions path-propose --curriculum structured-output
python3 -m tools.research_decisions path-propose --curriculum document-assistant --preferences /private/learning-preferences.json
```

Optional preference fields are `direction`, `starting_point`, `hours_per_week`
(an ordered integer pair, 1–80), `hardware`, and `additional_spending_inr` (0).
Defaults are applied AI products, software-building experience as an assumption,
10–15 hours per week, unspecified hardware and no additional spending. These are
planning inputs, not a capability profile. Do not store personal preferences in
this checkout.

To request evidence-based adaptation, add `--snapshot SKILL_SNAPSHOT_ID` and
optionally reviewed `--context` inputs. When the snapshot includes curriculum
skills, the existing qualified worker proposes an application context and lesson
emphasis. It cannot replace the syllabus, examples, completion checks or resources.
The draft remains subject to semantic review. If no curriculum skill overlaps,
the original curriculum remains an editorial draft with no inferred market fit.
No model is called without relevant evidence. Existing qualification, source
permissions, quota, failure-intent and `--retry-review` checks remain in force.

Use the returned path ID with the existing `path-select`, `progress`,
`path-decision`, `path-briefs` and report commands. Selection still requires the
user's actual choice. Without a market snapshot, `path-briefs` creates offline
curriculum planning drafts; they claim neither market relevance nor a novel
contribution. With a market snapshot it uses the existing evidence-bound workflow.
`path-compare` remains for model-generated v1 paths; inspect v2 curricula and their
adaptations directly rather than treating an editorial syllabus as a model baseline.

## Skills and trends

Browse groups catalog skills by their primary learning topic, then distinct-opening
frequency, with alphabetic tie-breaks. Global frequency and A–Z sorting are also
available. Observed terms preserves unresolved source wording for inspection and
review. Counts and percentages use the complete snapshot denominator; limiting
HTML cards does not change those counts. The report discloses omitted cards.

A newly generated snapshot can project a former unresolved phrase through a
current exact alias of the same type. Its evidence retains the original skill ID
and normalization revision. Explicit source-dependent mappings take precedence.
No semantic similarity merge or rewriting of historical analyses occurs.

```sh
python3 -m tools.research_decisions skill-history --days 30 --basis capture
python3 -m tools.research_decisions skill-history --cohort REVIEWED_COHORT_ID
python3 -m tools.research_ops report --limit 1000
```

Without a cohort, adjacent windows are descriptive only. With a cohort, its exact
windows and date basis govern the comparison. The P5 collection checks must pass,
all openings need compatible detailed analysis, both denominators must be nonzero,
and normalization/extraction versions must agree. Only reviewed catalog identities
receive changes in observed share, expressed in percentage points. A skill absent
from an otherwise complete window has zero observations; an unanalysed window is
unknown. Partial feeds, extra sources, missing publication dates and withdrawal
must not create growth. Reports display the latest retained comparison for the
report's date basis, with its own explicit historical dates.

## Presentation and compatibility

Content lives in the [curriculum library](curricula/README.md). Python components
produce escaped markup; CSS and JavaScript under `tools/report_assets` are bundled
into each page. No server, CDN, analytics, browser database or JavaScript framework
is needed. CSP authorizes the exact bundled script hash and prohibits connections.

Browser controls browse, expand, filter and prepare a named request for Codex.
Clipboard failure selects the request for keyboard copying. No browser action
records selection, completion or capability. Deep links open the containing tab
and disclosures; refresh and Back use the same fragment routing. With JavaScript
disabled all generated content remains available through native disclosures.

Saved curriculum lessons also provide a **Record this lesson** form. Its inputs
prepare a named request containing the path, lesson, event and learner's account.
The request treats that account as self-reported, asks for missing conditions and
dates, and requires checking completion before saving. The form has no persistent
storage; copy the request or keep work in the kit's work log before reloading.
With JavaScript disabled, its generic request still supports a guided conversation.

LearningPath v2 freezes the curriculum, resources, foundation lessons, preferences
and optional adaptation/evidence references. Existing v1 paths remain readable;
they are not silently converted into curated lessons. Existing selection and
progress events retain their schemas and stable milestone associations. Withdrawal
removes market-derived paths/reports; independently sourced work keeps its existing
lifecycle. A corrected progress event retracts dependent curriculum briefs too.
Do not downgrade writers or copy older managed reports around these controls.
