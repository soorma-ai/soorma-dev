<!-- SPDX-License-Identifier: FSL-1.1-ALv2 -->

# Where the methodology lives

soorma.ai's methodology has two tracks, each defined as rules an agent follows. This plugin
points at them rather than restating them, at the commits below. Both repositories are
private: every link here is *(access-required)*. A later version of this file moves the pins
forward; until then, read these commits, not `main`.

## AI-PRD: requirements and backlog (soorma-prd at `5f16bcc`)

- [`docs/development-methodology.md`](https://github.com/soorma-ai/soorma-prd/blob/5f16bcc665c2c97c2466b450f54297310de93b46/docs/development-methodology.md) *(access-required)*:
  the methodology as a whole: the two tracks, slice briefs, the loop between a build and the
  PRDs, technology versus specification questions, how to decide what's next, and where
  everything lives. Start here.
- [`backlog/`](https://github.com/soorma-ai/soorma-prd/tree/5f16bcc665c2c97c2466b450f54297310de93b46/backlog) *(access-required)*:
  slice briefs, one per milestone. A brief names the PRDs a slice draws on, at their tags, and
  what each repository builds. AI-DLC never edits a brief.
- [`docs/redesign/04-tooling-findings.md`](https://github.com/soorma-ai/soorma-prd/blob/5f16bcc665c2c97c2466b450f54297310de93b46/docs/redesign/04-tooling-findings.md) *(access-required)*:
  the register of tooling findings (F-numbers) against both rule sets, with their status.
  A review that finds a flaw in the rules proposes a finding here.

## AI-DLC: implementation (soorma-aidlc at `dbbf034`)

- [`.github/copilot-instructions.md`](https://github.com/soorma-ai/soorma-aidlc/blob/dbbf0349fd7ce269315c993591a69b900c96e51e/.github/copilot-instructions.md) *(access-required)*:
  the spine every AI-DLC session loads (linked as `.claude/CLAUDE.md` for Claude Code): the
  stages, their gates, and the always-on rules.
- [`common/content-validation.md`](https://github.com/soorma-ai/soorma-aidlc/blob/dbbf0349fd7ce269315c993591a69b900c96e51e/.aidlc-rule-details/common/content-validation.md) *(access-required)*:
  includes the closing-keyword check for anything posted to GitHub.
- [`common/session-continuity.md`](https://github.com/soorma-ai/soorma-aidlc/blob/dbbf0349fd7ce269315c993591a69b900c96e51e/.aidlc-rule-details/common/session-continuity.md) *(access-required)*:
  how a session resumes from `aidlc-state.md`.
- [`inception/prd-intake.md`](https://github.com/soorma-ai/soorma-aidlc/blob/dbbf0349fd7ce269315c993591a69b900c96e51e/.aidlc-rule-details/inception/prd-intake.md) *(access-required)*:
  starting from a slice brief, pinning each PRD to its tag, and re-intake.
- [`inception/prd-gap-classification.md`](https://github.com/soorma-ai/soorma-aidlc/blob/dbbf0349fd7ce269315c993591a69b900c96e51e/.aidlc-rule-details/inception/prd-gap-classification.md) *(access-required)*:
  technology versus specification gaps, and contract-backed questions.
- [`extensions/pr-checkpoint/pr-checkpoint.md`](https://github.com/soorma-ai/soorma-aidlc/blob/dbbf0349fd7ce269315c993591a69b900c96e51e/.aidlc-rule-details/extensions/pr-checkpoint/pr-checkpoint.md) *(access-required)*:
  the PR gates within an initiative.
- [`docs/how-to-use.md`](https://github.com/soorma-ai/soorma-aidlc/blob/dbbf0349fd7ce269315c993591a69b900c96e51e/docs/how-to-use.md) *(access-required)*: how to run it.

## What to watch when reviewing an AI-DLC session

- **The audit log** (`audit.md`): every human input is logged verbatim, appended at the
  bottom, with a timestamp taken from the clock (`date -u`), never typed.
- **Gates:** each stage ends at an approval the human gives; the session doesn't move on
  without it. PR gates belong to their stage: keep an initiative's PR open until its gate
  (hazard 24).
- **Questions:** answers are in question files, which are git-ignored; the audit log is their
  only durable record. A *Deferred* question is registered in `aidlc-state.md`.
- **Gaps:** a question the approved PRDs leave open is classified, not answered silently. A
  specification gap is raised against soorma-prd and blocks or is worked around with the
  workaround recorded; a technology gap is decided and recorded. A question a consumed
  contract leaves open goes to that contract's repository.
- **Extensions:** enabled extensions' rules are blocking; a stage's completion message
  carries their compliance summary.
- **State edits by script** anchor on whole heading lines (hazard 14).
