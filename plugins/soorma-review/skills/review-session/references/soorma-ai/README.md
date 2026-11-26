<!-- SPDX-License-Identifier: FSL-1.1-ALv2 -->

# soorma-ai: project references

Read this folder before the first review of a soorma-ai working session. It holds what is
particular to soorma.ai's repositories; the procedure itself is in the skill's `SKILL.md`.

| File | What it covers |
|---|---|
| [repositories.md](repositories.md) | The repositories, their visibility and roles, and the dev→main flow |
| [protection-and-checks.md](protection-and-checks.md) | Required checks per repository, DCO, the CLA setup, Dependabot |
| [contracts-and-tags.md](contracts-and-tags.md) | Contract tags, `+core.N` revisions, how a consumer re-pins, and PRD tags |
| [methodology.md](methodology.md) | Where AI-PRD and AI-DLC are defined, at pinned commits, and what to watch in their sessions |
| [hazard-evidence.md](hazard-evidence.md) | The soorma-ai incidents behind each hazard |

**Access:** soorma-prd, soorma-aidlc and soorma-ccw are private. Links into them are marked
*(access-required)* and open only for members of the soorma-ai organisation.

**Commit and PR conventions in every soorma-ai repository:**
- Commit messages end with a `Co-Authored-By:` trailer naming the model.
- PR descriptions and comments end with the "Generated with Claude Code" attribution line.
  Comments that are commands to a bot (Dependabot) are posted bare, with no attribution line.
- Issues are referred to as "for #N", never with a closing keyword (hazard 1), except where a
  workflow means the PR to close one: in soorma-prd, a specification gap's resolving PR (see
  [methodology.md](methodology.md)).
- In soorma-sdk, every commit is also signed off (`git commit -s`).
