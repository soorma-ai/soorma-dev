<!-- SPDX-License-Identifier: FSL-1.1-ALv2 -->

# Contracts and tags

## soorma-core's wire contract

soorma-core publishes its wire contract under `contract/` (Apache 2.0) and releases it by
annotated tag:

- **`contract-vX.Y.Z`** publishes contract version X.Y.Z. Pre-release while X is 0.
- **`contract-vX.Y.Z+core.N`** is revision N of soorma-core for the same contract version:
  the same wire contract, with clarifications or soorma-core changes a consumer should pin.
  The original tag counts as revision 0. SemVer ignores build metadata, so it ranks
  `+core.N` equal to the plain tag; the order comes from N. The definition is in
  [`contract/conventions/versioning.md`](https://github.com/soorma-ai/soorma-core/blob/contract-v0.1.0%2Bcore.2/contract/conventions/versioning.md)
  (at `contract-v0.1.0+core.2`), and each revision has a section in `contract/CHANGELOG.md`.
- **Tags never move** (hazard 8). A fix is a new revision tag. Tag a merge commit whose tree
  is the one CI tested. Write the annotation to a file, have the human approve it, create the
  tag from the file, push only that tag, and check that every earlier tag still points where it
  did: `git ls-remote --tags origin`.
- **The `+` in a tag name** is fine in git and in GitHub paths. In a URL query string it must
  be written `%2B`, or it is read as a space.

## How soorma-sdk consumes it

soorma-sdk vendors soorma-core's `contract/` at one tag:

- `contract.pin.json` records the tag, the commit, the `contract/` tree, and a SHA-256 for each
  vendored file.
- `tools/drift/write-pin.ts` writes the pin; a drift check in CI fails if the vendored files
  don't match it.
- **Re-pinning** is its own small piece of work in soorma-sdk: re-vendor at the new tag, run
  the drift check, update every file that names the old tag (test data aside), and discharge
  whatever the new revision answers. It needs the tag to exist first; never re-pin to a commit
  on `main`.

## Questions a contract leaves open

When soorma-sdk's work finds a question soorma-core's contract doesn't answer, it is raised
against soorma-core, citing the tag, file and section, and classified there. The answer comes
back as a new revision tag, and soorma-sdk re-pins. The AI-DLC rule for this route is in
`inception/prd-gap-classification.md` (see [methodology.md](methodology.md)).
