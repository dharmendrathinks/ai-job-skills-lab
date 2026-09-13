# Readiness fixes — 2026-09-11

Scope: working-tree fixes based on `40cc0b06601bff703bfd85d6007c7ce30beef2a8`.
This record is not a release tag, a successful remote CI run or authorization to
change repository visibility. The repository remains private.

| Finding | Change and completion evidence |
|---|---|
| Latest CI rejected an unbumped AGENTS edit | Marker is now 1.0.3. Local `check_release.py` includes the same version guard with the explicit PR Ready base, plus security guards and template preflight. Regression tests distinguish committed unbumped changes from a clean worktree and reject missing bases. |
| Corrected experiment still appeared in a YouTube brief | Store transactions retract non-history consumers of superseded progress and descendants. Regression fixtures verify report-file deletion, regenerated reports without stale success claims, preserved audit chains/unrelated records, old-writer reconciliation, and managed restore before rendering. |
| Bundled font notices incomplete | Read every Lato/Raleway font's embedded copyright notices; retained all notice variants and added full official OFL-1.1 text beside both families. Font binaries, MIT attribution and Apache-2.0 provenance remain unchanged. |
| No reproducible contributor experience | `python3 -m tools.research_demo` generates two labelled synthetic HTML pages using the existing renderer, with a connected path, skill and project/YouTube examples. An isolated test forbids model, network and Store access and checks existing reports survive. The quickstart documents a command-scoped binary installation and qualification procedure. |
| Development features attributed to an older release | README now labels v0.2.0 unreleased; v0.1.0 remains pinned to ba9c04f. Prepared v0.2.0 notes and exact-commit release instructions preserve the existing tag. Contribution guidance supports forks/PRs where access permits without changing visibility. |

## Executed verification

- Focused regressions: 45 tests passed (correction/history/restore, demo, onboarding
  privacy and framework-version checks).
- Full suite: 665 tests ran; 664 passed and the opt-in installed-runtime test was
  skipped in the ordinary suite. That test was executed separately with the
  qualified 0.153.4 binary: all nine forced tool calls were rejected.
- Lint, security guards, explicit-base framework guard, template preflight and
  the push-CI framework comparison (`HEAD~1`) passed locally. Markdown link
  targets and `git diff --check` passed.
- The first PR Ready run passed every configured check but reported NOT PR READY
  solely because the newly created source/documentation files were untracked.
  Final verdict after adding the reviewed files to the index: **PR READY**.
  All configured checks passed; no suspicious files or blockers. The standalone
  build check is not configured (this is a Python/Markdown workflow project).
- Offline CLI demo executed successfully into a fresh ignored `reports/demo-…/`
  directory. No real research store or live reports were modified.
- Fresh official Codex release archive: 87,323,149 bytes, SHA-256
  `8cf911ea676523bfb2121ec561848d2aba564890ad536db4d8a3353f2b9850b1`.
  Inspected archive member `codex-aarch64-apple-darwin` hashes to the required
  `b973d440acac501fd2594a43e7ca9ce41e0a65b9dfb28d0d7a7837c99e1261e3`.
  Downloaded for inspection; no CLI installation or authentication was changed.
- No hosted model generation, provider collection, dependency installation,
  publishing, outreach or private-profile setup was performed.

## Remaining release decisions

1. Maintainer-approved private security/conduct contact is still needed. The
   repository's private-vulnerability-reporting API returned 404; this does not
   verify an available intake form. SECURITY.md explicitly records that limitation.
2. Commit and push only reviewed changes, then verify GitHub Actions for that exact
   SHA. The previously reviewed run for 40cc0b0 failed the framework-version guard;
   local fixes cannot turn that historical run into a pass.
3. After release authorization, create a new v0.2.0 tag at the reviewed SHA and
   publish notes naming it. Do not move v0.1.0 or change visibility as part of this.

Fixtures establish behavior on owned examples, not human acceptance of real
recommendations, broad model quality or market coverage. Public launch remains
separate from code readiness and requires explicit owner authorization.
