# Release procedure

AI Job Skills Lab releases belong to **dharmendrathinks/ai-job-skills-lab**. This repository
is private and must remain private until the owner explicitly authorizes a change.
Publishing a GitHub release does not require changing visibility. Use explicit
`--repo` on every GitHub CLI operation: the inherited default may select upstream.

Releases follow the fork’s own `vMAJOR.MINOR.PATCH` sequence; upstream tags and
`framework_version` markers have independent meanings. v0.1.0 is a prerelease for
engineering evaluation, not a claim that human acceptance targets are met.

## Prepare and validate

1. Inspect `git status`, origin, branch ancestry, tags and the target repository’s
   visibility/default branch. Commit only reviewed phase work. Never force push,
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

## Publish after authorization

The commands below are a template; select the actual reviewed version and commit.
Never let `gh release create` manufacture a tag at an unintended branch tip.

```sh
gh repo view dharmendrathinks/ai-job-skills-lab --json visibility,defaultBranchRef
git tag -a v0.1.0 -m 'AI Job Skills Lab v0.1.0' RELEASE_COMMIT_SHA
git push origin refs/tags/v0.1.0
gh release create v0.1.0 --repo dharmendrathinks/ai-job-skills-lab \
  --verify-tag --prerelease --title 'AI Job Skills Lab v0.1.0' \
  --notes-file docs/releases/v0.1.0.md
```

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
