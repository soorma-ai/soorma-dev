<!-- SPDX-License-Identifier: FSL-1.1-ALv2 -->

# soorma-review

A Claude Code plugin with one skill, **`review-session`**: reviewing another AI agent's working
session, turn by turn, on behalf of a human approver.

## What it does

Work is split between three roles:

- **Generator**: the working session. It writes, tests, commits, pushes and opens PRs, and
  stops where its instructions say.
- **Reviewer**: a second session running this skill. After each generator turn it finds the
  generator's transcript, extracts what happened since its last instruction, checks the claims
  against git, GitHub and CI, and reports.
- **Human approver**: owns merges, tags, settings, legal text and decisions. The reviewer merges
  only on the human's confirmation, then hands the generator a paste-ready instruction block
  with explicit STOP points.

The skill's procedure is generic. What is particular to soorma.ai's repositories (branch flow,
required checks, contract tags, where the methodology lives) is in
[`skills/review-session/references/soorma-ai/`](skills/review-session/references/soorma-ai/README.md).

## Install

```sh
claude plugin marketplace add soorma-ai/soorma-dev
claude plugin install soorma-review@soorma-dev
```

Then, in the reviewing session: `/soorma-review:review-session`, or just ask it to "review the
session work". To try a local checkout for one session without installing:
`claude --plugin-dir plugins/soorma-review`.

## What's inside

| Path | Purpose |
|---|---|
| [`skills/review-session/SKILL.md`](skills/review-session/SKILL.md) | The procedure |
| [`skills/review-session/references/hazards.md`](skills/review-session/references/hazards.md) | Recurring hazards, each with its reason and evidence |
| [`skills/review-session/references/transcripts-claude-code.md`](skills/review-session/references/transcripts-claude-code.md) | Reading Claude Code transcripts |
| `skills/review-session/scripts/extract_turns.py` | Digest a transcript from your last instruction on |
| `skills/review-session/scripts/closing_keywords.py` | Find closing keywords before issue references, as written and with line breaks joined |
| `skills/review-session/scripts/wait_for_checks.sh` | Wait for a PR's checks under bash, then list them |

The scripts need Python 3 and bash; their tests run in CI (`python3 -I tools/run_tests.py`).
