<!-- SPDX-License-Identifier: FSL-1.1-ALv2 -->

# soorma-ai repositories

| Repository | Visibility | Role |
|---|---|---|
| [soorma-prd](https://github.com/soorma-ai/soorma-prd) *(access-required)* | private | AI-PRD: the product requirements (PRDs), slice briefs (the backlog), the methodology, and the tooling-findings register |
| [soorma-aidlc](https://github.com/soorma-ai/soorma-aidlc) *(access-required)* | private | AI-DLC: the rules an agent follows to build from approved requirements |
| [soorma-core](https://github.com/soorma-ai/soorma-core) | public | The server-side substrate, and the wire contract under `contract/` |
| [soorma-sdk](https://github.com/soorma-ai/soorma-sdk) | public | The client harness SDKs, built against a pinned soorma-core contract tag |
| [soorma-dev](https://github.com/soorma-ai/soorma-dev) | public | This tooling: Claude Code plugins for working by the methodology |
| [cla-assistant-action](https://github.com/soorma-ai/cla-assistant-action) | public | soorma-ai's fork of the archived CLA assistant action, pinned by SHA in the CLA workflows |
| soorma-ccw *(access-required)* | private | The agent-harness library a later generator/reviewer harness will build on |

Other soorma-ai repositories (the portal, the cloud platform, shared assets and the
organisation profile) follow the same branch flow.

## Branch flow

- **Work happens on `dev`; `main` changes only by a PR from `dev`.** Don't create feature
  branches off `main`. Before committing, `dev` must match `origin/dev` and contain
  `origin/main` (hazard 16).
- **Merges are merge commits** (`gh pr merge N --merge`), run from the review side with the
  human's confirmation. `dev` is never deleted.
- **Tags** (contract and PRD tags) are created from the review side too, each only on the
  human's confirmation of that tag, and pushed alone. See [contracts-and-tags.md](contracts-and-tags.md).
- **After a merge**, `dev` is fast-forwarded to the merge commit and pushed.
- **A docs-only commit left on `dev`** after a merge (an initiative's close-out record, say)
  rides with that repository's next PR; it doesn't need a PR of its own.
- **`cla-signatures`** (soorma-core, soorma-dev) is the CLA signature store. It diverges from
  `main` by design: never merge, rebase or sync it, and never open a PR from it. Its
  ahead/behind counts mean nothing.
- **Dependabot** opens PRs into `main` in soorma-core and soorma-dev, and into `dev` in
  soorma-sdk. A Dependabot PR into `main` moves `main` under `dev` (hazard 5).

## Working sessions

Each working session runs in one repository and stops at the points its instruction names. A
review covers the session's work since the last instruction, across every repository it
touched. A session's own memory notes and the reviewer's are shared (hazard 25).
