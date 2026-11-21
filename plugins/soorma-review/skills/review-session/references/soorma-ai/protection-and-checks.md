<!-- SPDX-License-Identifier: FSL-1.1-ALv2 -->

# Protection, required checks, and contributor agreements

Settings are the human's (hazard 23). Read them back with `gh api`; never change them from a
working session.

## `main` protection

The public repositories protect `main` with a ruleset: no deletion or force push, changes by
pull request only, merge commits only, the required checks below, and no bypass. `dev` is
unprotected; sessions push to it directly.

| Repository | Required checks on `main` (exact job names) |
|---|---|
| soorma-core | `cla-assistant`; `Build, check, and test`; `Images, image secret scans, stack smoke test, and the S1-stopped demonstration`; `Dependency review` |
| soorma-sdk | `Check sign-off` |
| soorma-dev | `cla-assistant`; `Validate`; `Dependency review` |
| soorma-prd, soorma-aidlc | none: private repositories on the current plan can't have rulesets, and neither has CI. Their PRs have no checks, so the pre-merge check rests on the diff, `mergeStateStatus` and `closingIssuesReferences` |

Renaming any of these jobs blocks every PR until the ruleset changes (hazard 12). A job skipped
by its own `if` counts as passing: soorma-core's image job skips when every changed path is
under `aidlc-docs/`, and `Dependency review` skips on pushes.

**Nothing re-tests soorma-core's `main` after a merge**: its push run only builds the SBOM. So
before merging there, the PR's tested base must be `main`'s current head (hazard 5).

To read a repository's rules: `gh api repos/soorma-ai/<repo>/rules/branches/main`.

## DCO in soorma-sdk

soorma-sdk is Apache 2.0 and uses a Developer Certificate of Origin, not a CLA. Its
`Check sign-off` job fails a PR if any commit lacks a `Signed-off-by:` line matching the commit
author. Every commit uses `git commit -s`, and keeps the `Co-Authored-By:` trailer. Dependabot's
verified commits are exempt. A missing sign-off means a history rewrite, which needs the human
(hazard 15).

## The CLA in soorma-core and soorma-dev

Both are FSL-1.1-ALv2 and take contributions under the CLA in `CLA.md` (individuals) and
`CCLA.md` (organisations).

- **The workflow**, `.github/workflows/cla.yml`, runs on `pull_request_target` and
  `issue_comment`. It pins `soorma-ai/cla-assistant-action` by full SHA. Its allowlist covers
  the maintainer and bots, so their PRs pass without a signature.
- **Signatures** are committed to `signatures/version1/cla.json` on the `cla-signatures`
  branch, which has its own ruleset (no deletion or force push), not to `main`.
- **An Actions policy** allows `pull_request_target` and `issue_comment` for `cla.yml` only:
  GitHub blocks `pull_request_target` by default in public repositories from 2026-12-02.
- **Because of `pull_request_target`, a PR that changes `cla.yml` is checked by `main`'s copy**
  (hazard 2). Prove a change after merge with a throwaway PR, closed unmerged. If the merged
  workflow breaks, the required `cla-assistant` check fails every PR, including the revert, and
  the human has to lift the ruleset briefly.

## Dependabot

- Every Dependabot configuration holds updates to a 7-day release cooldown. When verifying a
  dependency PR, check that the release is past it.
- Command etiquette (hazard 6): one `@dependabot` command per comment, a little apart, with no
  attribution line. `@dependabot recreate` works when `rebase` is ignored.
- soorma-core's pinned images have companion edits Dependabot can't make (for example a
  PostgreSQL bump needs the matching pin in `ci.yml` and the test-database helper); guard tests
  fail the PR until the companion edit is made.
