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
  or tags only on the human's confirmation of that merge or tag, then hands the generator a
  paste-ready instruction block with explicit STOP points.

The skill's procedure is generic. What is particular to soorma.ai's repositories (branch flow,
required checks, contract tags, where the methodology lives) is in
[`skills/review-session/references/soorma-ai/`](skills/review-session/references/soorma-ai/README.md).

## Install

```sh
claude plugin marketplace add soorma-ai/soorma-dev
claude plugin install soorma-review@soorma-dev
```

`soorma-ai/soorma-dev` is GitHub's `owner/repo` shorthand. The marketplace can also be added
from a full git URL (`https://github.com/soorma-ai/soorma-dev.git`) or from a local directory
holding a checkout. Installing from GitHub reads the default branch, `main`, so changes waiting
on `dev` aren't installed until they are merged.

**To upgrade** after later merges to soorma-dev's `main`, refresh the marketplace, then update
the plugin:

```sh
claude plugin marketplace update soorma-dev
claude plugin update soorma-review@soorma-dev
```

The update takes effect in a new session, or after `/reload-plugins` in a running one. While the
plugin is pre-release it has no version number, so Claude Code uses the commit SHA of its
installed directory as its version. Claude Code doesn't auto-update third-party marketplaces by
default: run both commands when you want the latest, or turn on auto-update for soorma-dev in
`/plugin` > Marketplaces.

**From a local checkout**, for one session and without installing anything, start the reviewer
with the plugin directory's absolute path:

```sh
claude --plugin-dir <absolute path>/soorma-dev/plugins/soorma-review
```

The plugin is loaded in place: after editing it, run `/reload-plugins` in that session.

## Using it

### The setup

- **One or more generator sessions**: the sessions doing the work, for example an AI-DLC
  session or an AI-PRD session, usually one per repository. Nothing is installed in them.
- **One reviewer session** with this plugin, **on the same machine**: the reviewer reads the
  generators' transcripts from `~/.claude/projects/`, where Claude Code writes them.
- **Start the reviewer where it can run `git` and `gh` across every repository involved**, such
  as the parent directory of your checkouts or a workspace that includes them all. It needn't
  share a generator's working directory. It needs `gh` signed in with access to those
  repositories.
- **Start the reviewer from the same directory every time.** Claude Code keeps a session's
  memory per starting directory, and the reviewer's notes (merges, decisions, open items) are
  what let the next review pick up where the last one stopped. Started from a different
  directory, it has none of them and begins a separate memory store. Before its first review it
  reads its memory index, if one exists. A new reviewer session for each major piece of work
  (a stage, a milestone step) works well: each starts with a fresh context, and they all share
  the notes kept for that directory.

### The loop

1. **The reviewer writes the generator's instruction**, as a fenced text block. You paste it
   into the generator.
2. **The generator works until a STOP** that the instruction names: a plan to approve, a PR
   that is ready, a decision only you can make.
3. **You type "review the session work"** in the reviewer, or `/soorma-review:review-session`.
4. **The reviewer reports**: what it checked against git, GitHub and CI, the problems it found,
   and the decisions it needs from you. When a PR is ready it runs the pre-merge check and
   merges **only when you confirm**. Then it hands back the next instruction block, every
   time. Any decision it needs from you is on the block's one line starting
   `HUMAN DECISION:`, prefilled with its recommendation: edit that line before pasting, and
   the line as pasted is your decision. The loop starts again at 1.

The reviewer never changes repository settings. It merges or tags only when you confirm that
merge or that tag, and the generator never merges or tags at all. Those decisions stay with
you.

### The first review

Tell the reviewer which session or repository to look at, for example "review the soorma-core
session" or "the session working in soorma-sdk". It lists the candidate transcripts (working
directory, branch, last activity and first prompt, newest first) and confirms the right one by
finding its own last instruction in it. If you started the generator yourself, with a prompt the
reviewer didn't write, say so, and paste that prompt's first line: the reviewer anchors on it
instead.

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
`SKILL.md` names them through `${CLAUDE_SKILL_DIR}`, the variable Claude Code documents for
files bundled with a skill. Claude Code replaces it with the skill's directory as text when it
loads `SKILL.md`, in code blocks and inline code alike, so the paths resolve wherever the
reviewer session was started. It is not exported to the shell.
