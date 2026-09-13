# Project identity and rename

Effective 11 September 2026: **AI Job Skills Lab**, repository
`dharmendrathinks/ai-job-skills-lab`, development directory
`/Users/dhasharma/Dharmendra/Projects/ai-job-skills-lab`.
The existing checkout is moved in place. No second development checkout or fork
is created. The GitHub repository remains private; MIT notices and upstream
attribution remain intact. AI Trend Radar is a separate, unchanged project.

## Current identifiers

| Purpose | Identifier |
|---|---|
| Display name | AI Job Skills Lab |
| Repository/slug | `ai-job-skills-lab` |
| Explicit private workspace | `AI_JOB_SKILLS_LAB_HOME` |
| Default macOS state | `~/Library/Application Support/ai-job-skills-lab` |
| Default Linux state | `$XDG_DATA_HOME/ai-job-skills-lab`, defaulting under `~/.local/share` |
| New interchange producer | `ai-job-skills-lab` |
| New schedule labels | `local.ai-job-skills-lab.*` |
| Optional upstream-issue workflow gate | `AI_JOB_SKILLS_LAB_ENABLE_UPSTREAM_ISSUES` |

## Compatibility and evidence

`AI_JOB_RADAR_HOME` remains a compatibility alias. Conflicting old/new variables
fail closed. Without an explicit variable, an existing `ai-job-radar` data directory
is used until moved; if both names exist, the user must explicitly select one.
This avoids presenting an empty new corpus as though old evidence disappeared.

Previously exported `ai-job-radar` producer identities still map echoed original
artifact IDs into the withdrawal ledger. New exports use the current producer;
existing envelope identities, schema versions, approval digests and provenance
are not rewritten. Receivers should accept the new producer identifier before
new interchange; no AI Trend Radar code or data is changed by this rename.

Historical content-addressed state, captured source text, operation receipts,
model metadata and evaluated executable paths retain their original bytes.
For example, `phase6-evaluation.json` records the old executable path because that
is the path actually tested. Git history and old release tag commits also retain
their historical identity. These and compatibility tests are intentional remaining
references to the former name, not active branding.

## Moving an existing installation

Stop writers and scheduled processes before moving directories. Move the checkout
and its default private state directory without copying either to a second working
location. Preserve permissions and withdrawal journals. Do not search-and-replace
inside `research-state.json`, backups or content-addressed artifacts.

After the move, `tools.research_report_files.relocate_default(store, previous_repo,
new_repo, previous_home)` verifies the previous binding/owner and the private,
Git-ignored report destination before changing only the three binding metadata
files. It rejects still-existing originals and unrelated report owners. An
interrupted metadata update can be resumed with the same arguments; other
operations stay blocked while bindings disagree. Regenerate reports afterward.
Custom workspaces with hashed report subdirectories need their own explicit
binding reconciliation; this helper only handles the default workspace.

Repair moved virtual-environment activation paths without installing dependencies.
Run template preflight, regression checks and local report generation from the new
directory. The public profile template's only change is its routing-header brand;
its reviewed hash is explicitly added to the allowlist, leaving all profile fields
unchanged. Runtime client branding changes its qualification identity: rerun the
existing installed-binary forced-call tests, never edit a qualification record to
make it match. This does not enable scheduling or establish new model-quality results.

Existing scheduled plists and unattended qualifications include absolute paths;
regenerate and explicitly review them before activation. This installation had no
matching launchd plist at inspection. An old workflow variable must be deliberately
carried to the current name before its optional issue-publishing gate can be used;
rename does not enable publication. Generated report paths remain
`reports/jobs.html` and `reports/workspace.html` in the renamed checkout.

## Executed verification

The bundled analyzer returned **PR READY** against `a4226da`: 659 tests ran
(658 passed, one opt-in test skipped), skill lint and security checks passed.
No build check is configured. The installed pinned runtime separately denied all
nine forced tool calls with the renamed client. No live model analysis or source
collection was needed for this rename.

The default manifest, withdrawal journal and operations ledger were verified
byte-identical across binding relocation. Normal policy-aware report regeneration
then preserved 593 displayed openings, ten project briefs and eight YouTube briefs
under the new branding; both HTML files remain mode 0600 and Git-ignored.
Preflight resolves the renamed private directory with no template errors.
GitHub confirms the renamed repository is private; the existing prerelease title
and links were updated without moving its tag. No GitHub workflow variables or
matching launchd plists needed migration.
