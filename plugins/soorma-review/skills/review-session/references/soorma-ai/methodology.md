<!-- SPDX-License-Identifier: FSL-1.1-ALv2 -->

# Where the methodology lives

soorma.ai's methodology has two tracks, each defined as rules an agent follows. This plugin
points at them rather than restating them, at the commits below. Both repositories are
private: every link here is *(access-required)*.

**Before a review, check the pins.** Compare each pin with the repository's current main
(`git rev-parse origin/main`). If main is ahead, read what changed in the files listed here
(`git diff {pin}..origin/main -- {paths}`), review against the version the session actually
used, and say in the report that the pin is behind, so the human can schedule the bump.

## AI-PRD: requirements and backlog (soorma-prd at `545e4bc`)

- [`docs/development-methodology.md`](https://github.com/soorma-ai/soorma-prd/blob/545e4bcebcb901a3c9e6d5b9d85819be649a2268/docs/development-methodology.md) *(access-required)*:
  the methodology as a whole: the two tracks, slice briefs, the loop between a build and the
  PRDs, technology versus specification questions, how to decide what's next, and where
  everything lives. Start here.
- [`.github/copilot-instructions.md`](https://github.com/soorma-ai/soorma-prd/blob/545e4bcebcb901a3c9e6d5b9d85819be649a2268/.github/copilot-instructions.md) *(access-required)*:
  the AI-PRD spine every AI-PRD session loads (linked as `.claude/CLAUDE.md`): the stages,
  their gates, the always-on rules, and what happens after a PRD is approved or amended.
- [`.aiprd-rule-details/`](https://github.com/soorma-ai/soorma-prd/tree/545e4bcebcb901a3c9e6d5b9d85819be649a2268/.aiprd-rule-details) *(access-required)*: the stage and
  layer rule files the spine loads, including `common/question-format-guide.md`.
- [`backlog/`](https://github.com/soorma-ai/soorma-prd/tree/545e4bcebcb901a3c9e6d5b9d85819be649a2268/backlog) *(access-required)*:
  slice briefs, one per milestone. A brief names the PRDs a slice draws on, at their tags, and
  what each repository builds. AI-DLC never edits a brief.
- [`docs/redesign/04-tooling-findings.md`](https://github.com/soorma-ai/soorma-prd/blob/545e4bcebcb901a3c9e6d5b9d85819be649a2268/docs/redesign/04-tooling-findings.md) *(access-required)*:
  the register of tooling findings (F-numbers) against both rule sets, with their status.
  A review that finds a flaw in the rules proposes a finding here.

## AI-DLC: implementation (soorma-aidlc at `ea8ce8c`)

- [`.github/copilot-instructions.md`](https://github.com/soorma-ai/soorma-aidlc/blob/ea8ce8cd50443e4479775d29193f4eb725020bbf/.github/copilot-instructions.md) *(access-required)*:
  the spine every AI-DLC session loads (linked as `.claude/CLAUDE.md` for Claude Code): the
  stages, their gates, and the always-on rules.
- [`common/content-validation.md`](https://github.com/soorma-ai/soorma-aidlc/blob/ea8ce8cd50443e4479775d29193f4eb725020bbf/.aidlc-rule-details/common/content-validation.md) *(access-required)*:
  includes the closing-keyword check for anything posted to GitHub.
- [`common/session-continuity.md`](https://github.com/soorma-ai/soorma-aidlc/blob/ea8ce8cd50443e4479775d29193f4eb725020bbf/.aidlc-rule-details/common/session-continuity.md) *(access-required)*:
  how a session resumes from `aidlc-state.md`.
- [`inception/prd-intake.md`](https://github.com/soorma-ai/soorma-aidlc/blob/ea8ce8cd50443e4479775d29193f4eb725020bbf/.aidlc-rule-details/inception/prd-intake.md) *(access-required)*:
  starting from a slice brief, pinning each PRD to its tag, and re-intake.
- [`inception/reverse-engineering.md`](https://github.com/soorma-ai/soorma-aidlc/blob/ea8ce8cd50443e4479775d29193f4eb725020bbf/.aidlc-rule-details/inception/reverse-engineering.md) *(access-required)*:
  how Reverse Engineering chooses its mode (Full, Baseline and delta, Not needed: scope read
  in full), reuses earlier initiatives' artifacts at a recorded commit, and records
  corrections.
- [`inception/prd-gap-classification.md`](https://github.com/soorma-ai/soorma-aidlc/blob/ea8ce8cd50443e4479775d29193f4eb725020bbf/.aidlc-rule-details/inception/prd-gap-classification.md) *(access-required)*:
  technology versus specification gaps, and contract-backed questions.
- [`extensions/pr-checkpoint/pr-checkpoint.md`](https://github.com/soorma-ai/soorma-aidlc/blob/ea8ce8cd50443e4479775d29193f4eb725020bbf/.aidlc-rule-details/extensions/pr-checkpoint/pr-checkpoint.md) *(access-required)*:
  the PR gates within an initiative.
- [`docs/how-to-use.md`](https://github.com/soorma-ai/soorma-aidlc/blob/ea8ce8cd50443e4479775d29193f4eb725020bbf/docs/how-to-use.md) *(access-required)*: how to run it.

## What to watch when reviewing an AI-PRD session

Each line names the rule's place in the spine (or a rule file) at `545e4bc`, and what a reviewer
checks against it. The rules are in those sections; read them there.

- **Audit log** (*Audit Trail*): every human input is appended verbatim, with a timestamp from
  the clock.
- **Questions** (*Open Questions as Artifacts*): every question is in its `open-questions.md`
  with a status, and an `Awaiting Answer` question blocks the gate.
- **Option sets** (*Question Format*; `common/question-format-guide.md`, *Before Drafting
  Options*): what determines the answer is stated before the options, composite options are
  decomposed, and a rule over two or more conditions is shown as a truth table.
- **Answers written back** (*Resolutions Are Written Back*): the artifact that raised the
  question carries the decision and its premises, not only the question file.
- **Gates and commits** (*Commit at Every Gate*): one commit per approved gate, pushed to `dev`;
  the PR to `main` opens only at Stage 3.2b.
- **Amendments to approved work** (*The mechanism*; *Back-edges within an initiative*): a dated
  Amendment section and a header note, surfaced at the next gate.
- **Packaging sign-off** (*P7: Packaging and Seam*): the count by kind sums to the total, and
  the human's acknowledgment is recorded verbatim.
- **Specification gaps** (*Specification gaps raised by a build*): the resolving PR closes the
  gap's issue on purpose. Check that `closingIssuesReferences` lists exactly those issues
  (hazard 1).
- **An approved PRD amended** (*The answer belongs to an existing PRD*, steps 5 and 7): the
  packaging re-take follows step 5's test, and only slice briefs that aren't Done are re-cited.
- **A later PRD amending an earlier one** (*An approved PRD amended by a later PRD*): the
  amendment is in its own commits in the approving PR, and both PRDs are tagged on the merge
  commit.
- **After the merge** (*Stage 3.2b*, step 7; *After a PRD Merges*): the merge commit is tagged,
  then the briefs and snapshots are brought up to date in one short PR of their own, before the
  next PRD's Stage 1.1.
- **Stage 1.1 givens** (*Stage 1.1*, step 5): a session serving a slice brief checks the brief's
  latest *Status* revision against its tags' dates, and stops if the brief is behind.
- **Not a rule:** the human's standing preference for AI-PRD sessions (2026-11-22) is a
  recommendation, marked as the AI's, on every open question. The AI-PRD rules assume a
  recommendation but don't require one, so don't cite this preference to them.

## What to watch when reviewing an AI-DLC session

- **The audit log** (`audit.md`): every human input is logged verbatim, appended at the
  bottom, with a timestamp taken from the clock (`date -u`), never typed.
- **Gates:** each stage ends at an approval the human gives; the session doesn't move on
  without it. PR gates belong to their stage: keep an initiative's PR open until its gate
  (hazard 24).
- **Questions and plans:** answers are in question files and plans in `working/`, both
  git-ignored; the audit log is their only durable record. A *Deferred* question is registered
  in `aidlc-state.md`.
- **Gaps:** a question the approved PRDs leave open is classified, not answered silently. A
  specification gap is raised against soorma-prd and blocks or is worked around with the
  workaround recorded; a technology gap is decided and recorded. A question a consumed
  contract leaves open goes to that contract's repository.
- **Reverse Engineering, in a brownfield initiative:** the mode is recorded under
  `## Reverse Engineering Status`, with the commit it was analysed at. A *Baseline and delta*
  run has a `baseline.md` naming its sources and their commits. A reused artifact is a claim to
  check against the code: contradictions are recorded under *Corrections*, never fixed in the
  other initiative's files.
- **Extensions:** enabled extensions' rules are blocking; a stage's completion message
  carries their compliance summary.
- **State edits by script** anchor on whole heading lines (hazard 14).
- **Close-outs on `dev`:** an initiative's close-out commit stays on `dev` until the
  repository's next PR, so on `main` the newest finished initiative's `aidlc-state.md` still
  reads as if its PR were open. Read `dev` before calling it stale.
