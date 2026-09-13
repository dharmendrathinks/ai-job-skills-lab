# Release procedure

AI Job Skills Lab releases belong to **dharmendrathinks/ai-job-skills-lab**. This repository
is private and must remain private until the owner explicitly authorizes a change.
Publishing a GitHub release does not require changing visibility. Use explicit
`--repo` on every GitHub CLI operation: the inherited default may select upstream.

Releases follow the fork’s own `vMAJOR.MINOR.PATCH` sequence; upstream tags and
`framework_version` markers have independent meanings. v0.1.0 is a prerelease for
engineering evaluation, not a claim that human acceptance targets are met.

The next prepared release is [v0.2.0](v0.2.0.md), currently **unreleased**.
The existing v0.1.0 tag remains at `ba9c04f173ceca15e93fb2edb67b78613253f556`;
it does not contain the later rename and connected learning workflow.

## Prepare and validate

1. Inspect `git status`, origin, branch ancestry, tags and the target repository’s
   visibility/default branch. Commit only reviewed work. Never force push,
   overwrite an existing tag or change remotes to work around a failure.
2. Update README, CHANGELOG, relevant operations/contracts, contribution/security
   guidance and `docs/releases/<version>.md`. Preserve licenses, notices and
   upstream history. State actual tests, pending human gates and compatibility.
3. Keep runtime data, private descriptions/profiles, credentials, machine-generated
   schedules and model outputs out of source/release assets. Review the staged
   diff and run CONTRIBUTING checks, public-template preflight and the PR Ready
   analyzer when available. Record exact results and any skipped checks.
4. Integrate into `main` with a fast-forward when ancestry permits; otherwise
   review conflicts in this same checkout. Push only to origin after authorization.
   Inspect the GitHub Actions result for that exact commit. Do not treat a queued,
   missing or failed run as a pass; fix failures or explicitly record an unavailable
   external check before making a release decision.

5. Confirm a maintainer-approved private security/conduct contact is documented
   and reachable. Public vulnerability reporting was not confirmed by the private
   repository API during this review (404); do not advertise an unverified form.
   If a public launch is authorized later, update the visibility note and verify
   reporting access from a non-collaborator account before announcing the project.

## Publish after authorization

The commands below are a template; select the actual reviewed version and commit.
Never let `gh release create` manufacture a tag at an unintended branch tip.

```sh
gh repo view dharmendrathinks/ai-job-skills-lab --json visibility,defaultBranchRef
# Replace this with the full SHA whose CI and diff were actually reviewed.
release_commit=REVIEWED_FULL_COMMIT_SHA
# Stop unless the checkout is clean and the intended commit is on main.
test -z "$(git status --porcelain)"
test "$(git rev-parse main)" = "$release_commit"
git tag -a v0.2.0 -m 'AI Job Skills Lab v0.2.0' "$release_commit"
git push origin refs/tags/v0.2.0
gh release create v0.2.0 --repo dharmendrathinks/ai-job-skills-lab \
  --verify-tag --prerelease --title 'AI Job Skills Lab v0.2.0' \
  --notes-file REVIEWED_RELEASE_NOTES_FILE
```

Prepare `REVIEWED_RELEASE_NOTES_FILE` from the unreleased notes, replacing its
status with the actual release date, full target SHA and CI URL.
GitHub release notes should use repository/revision-qualified links when rendered
outside the repository; prepare the exact notes file accordingly. Do not attach
private runtime data or outputs. Verify remote main/tag object IDs, release target,
prerelease status, published URL and **PRIVATE** visibility afterward. Record the
commit/tag and report any unavailable CI checks. No schedule, provider activation,
notification, public visibility change or upstream PR is part of releasing software.

## Update and recovery

Use [the upstream maintenance ledger](../research/maintenance.md) for synchronization.
Review state-contract and runtime qualifications before upgrades. Git rollback
is not a private-state recovery procedure. Use the current writer’s managed
recovery with its current withdrawal journal. Fix a bad release with a new version;
do not silently move an already published tag.
