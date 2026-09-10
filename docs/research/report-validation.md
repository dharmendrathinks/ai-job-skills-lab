# Two-report validation — 2026-09-10

The approved presentation change replaces the mixed report with separate jobs and
project views. No collection or model generation was run. Existing default-workspace
results rendered 20 deduplicated jobs and 3 project briefs, with no generation
limit overflow. Generated files remain ignored under `reports/`; no source content
or report screenshots are included in this validation record.

## Executed checks

Eight new behavioral cases cover separate datasets/conservative cross-source
merging, escaped hostile input and the exact script hash, bound checkout-copy
withdrawal, expiry and legacy migration, tracked/symlink destinations, lost location
markers/workspace separation, second-file write failure, and overflow/empty states.
The focused report/P6/P7 suite passed all 62 tests. Final PR Ready assessment
against `ba9c04f` returned **PR READY**: 611 tests ran, 610 passed and one opt-in
installed-runtime test was skipped. Skill lint and security guards passed; no build
check is configured. Framework-version and public-template preflight checks passed.
Both generated files were verified untracked/ignored, mode 0600, with one fixed
inline script, no source-loading elements and only sibling navigation links.

Safari opened both local HTML files. Visual inspection confirmed readable desktop
layout, navy/teal header, colored summary cards, job status chips and two-column
project sections. Search with an unmatched term changed jobs from 20 displayed to
0 with an explicit empty state. Clear reset the search; fixed sibling navigation
opened Projects. Selecting a capability changed project count from 3 to 1; Clear
restored All capability and 3 of 3. No external request, model action or acceptance
was initiated by these controls. Responsive CSS is present; mobile rendering and
other browsers were not separately exercised.

## Compatibility and limits

HTML payload version 2 remains inside the existing artifact envelope. Current
writer handles v1 until regeneration and removes its legacy local file. Corpus,
profiles, credentials and journals remain external. Only the user-approved managed
views are written in ignored `reports/`; data-export permission is unchanged.
Location markers and owner checks protect supported file operations, not arbitrary
manual filesystem changes or deliberate `git add -f`. Do not downgrade writers or
remove location markers. Physical erasure, browser caches, OS copies, multi-file
atomicity and power-loss recovery remain outside guarantees.

Reports render existing draft content without declaring it correct or useful.
Old independent proposals can overlap; the renderer does not fabricate a reviewed
duplicate decision or rewrite model recommendations. Collection and model refresh
remain separate explicitly requested operations. The v0.1.0 release is unchanged.

## YouTube tab amendment

The second file now retains Projects and YouTube experiments in separate tabs.
Regeneration used the existing 3 project briefs and 1 YouTube brief; jobs remain
20. No model or collection call was made. Each brief type has its own generation
limit, count and filter options, while both remain in the same lifecycle artifact.
Tests cover independent limits/exactly two files and withdrawal of a YouTube
brief while its tab is hidden. The fixed script was executed in a Node VM with
an owned DOM fixture: tab scoping, filter-option replacement, unmatched search,
Clear retaining the current tab, switching resetting filters and Arrow Left
navigation all passed. This is a script behavior check, not a browser engine.
Safari rendered the new tabs and switching to YouTube showed 1 of 1 and its
experiment sections; a screenshot inspection confirmed the red accent and selected
tab. Subsequent UI automation became unstable, so search/reset/keyboard checks for
this amendment rely on the executed script fixture rather than claimed Safari runs.

Final assessment including the tab amendment: **PR READY** against `ba9c04f`.
The full suite ran 614 tests: 613 passed and one opt-in runtime test was skipped.
Skill lint and security checks passed; no build check is configured. Both report
files remain ignored and untracked. The 11 report-specific tests all passed.

## Broad discovery and manual collection amendment

On 2026-09-10 the user authorized broader AI-role searches and removal of the
blanket manual cooldown. All 13 explicit versioned seed requests completed without
retry: LLM 100, AI product 100, applied AI 100, AI engineer 100, generative AI 92,
AI agent 100, retrieval 37, LLM evaluation 75, AI security 100, inference 75,
AI infrastructure 100, MLOps 33 and machine learning 100. Counts are returned
observations, not distinct openings or validated AI roles. These capped,
remote-biased results do not measure global coverage or demand growth.

The existing corpus plus these requests contains 1,132 captured revisions and
593 distinct source listings/deduplicated openings. All availability and verified
employer identities remain unknown. No descriptions are missing; zero latest
observations have validated analyses. Keyword matches include unrelated work,
so description-based classification remains necessary. No model generation was
run; the existing 3 project drafts and 1 YouTube draft were retained.

Both HTML files were regenerated: jobs shows all 593 listings; projects retains
its two tabs. The report-only limit now supports 1–1000 entries per type, with a
16 MB per-page budget. Import/request limits remain unchanged. Added behavioral
checks cover consecutive manual queries, default rotation, failed requests without
retries, scheduled cooldown and trigger propagation, and reports above 100 entries.

Final assessment for this amendment returned **PR READY** against `ba9c04f`:
618 tests ran, 617 passed and one opt-in installed-runtime test was skipped.
Skill lint and security guards passed; no build check is configured. Both generated
files remain ignored and mode 0600 (jobs approximately 5.14 MB, projects 0.17 MB).
The expanded sample was not separately exercised in Safari; earlier browser and
fixed-script fixture results above describe the scope of interface verification.

## Typeahead clarity amendment

The user's open Chrome report showed `machin` and 160 of 593 results, so filtering
was active. The existing full-card index included collapsed descriptions, producing
apparently unrelated visible titles. Search now defaults to titles with an explicit
All content option, retains immediate input handling and handles the native search
clear event. Clear and tab changes restore title scope. No source evidence changes.
The fixed-script fixture exercises incremental typing without Enter/blur, case and
multi-term input, hidden-evidence exclusion/opt-in, deletion, native clearing,
tab/filter interaction, and the jobs page without tabs. Browser inspection identified
the original behavior; the new interaction is checked by the script fixture.

## Role families and unavailable filters amendment

Normalized country and availability were unknown in the captured sample. This
first amendment overlooked captured source geography; corrected below. Generated controls now omit these facets until at least one displayed
listing has a known value. Mixed known/unknown samples retain both options.
Title-based role grouping is local presentation only, with overlapping families,
a versioned rule set and Other / unclassified fallback. No claim extraction or
source fields are changed. English cue matching has limited recall; generic titles
and non-English titles may remain unclassified. Membership does not confirm AI
relevance or research-heavy responsibilities.

New behavioral fixtures cover all-unknown then mixed-value facets, specialist and
generic titles, overlapping ML/platform labels, avoiding insurance-agent/email/AI
sales matches, unchanged aggregate identity and no analysis creation. The fixed UI
script checks role selection combined with typeahead, overlapping membership and
Clear. No additional collection or model execution is involved.

Regenerated the 593-listing jobs page and unchanged 3-project/1-YouTube page.
Parsed generated controls contain only role and source for this sample. Title
memberships include 28 machine-learning, 2 AI-product-engineering and 4 applied-AI
listings; these overlap with other families and are not market classifications.
482 titles remain Other / unclassified. No new browser rendering was claimed.
Final analyzer verdict: **PR READY** against `ba9c04f`; 620 tests ran, 619 passed,
one opt-in runtime test skipped, lint/security passed, build not configured.

## Source geography correction

The user's Bulgaria example exposed a presentation omission: normalized country
was null while `segments.source_geography` was populated. The report now uses
normalized country if present and otherwise the captured source geography, labels
fallback chips as source location, and offers a Location filter. Regions and
multi-country labels stay intact. Availability and language remain independent;
the latter's unknown label is now explicitly prefixed Language.

Fixtures cover Bulgaria in both chip and filter, known-country precedence,
region/multi-country/Anywhere preservation, empty or unsupported values, hostile
HTML escaping, unchanged snapshot identity and unchanged null country fields.
Only managed HTML is regenerated; no collection, normalization or model run.

Regenerated both managed files and verified the screenshot's listing in the HTML:
Bulgaria appears in its location facet and source-location chip, with no Location
unknown chip. The generated controls are role, source and location. Final analyzer
verdict: **PR READY**; 621 tests ran, 620 passed and one opt-in runtime test skipped.
Lint/security passed; build not configured. No additional browser run was performed.
