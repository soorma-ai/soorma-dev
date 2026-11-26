---
name: review-session
description: Review another AI agent's working session (the generator) after each of its turns, acting as the reviewer for a human approver. Finds the generator's transcript, extracts what it did since your last instruction, and checks its claims against git, the code host and CI instead of trusting its report. Then reports concise findings, runs the pre-merge check and the merge with the human when a PR is ready, keeps memory notes current, and hands back a paste-ready instruction block with explicit STOP points. Use it whenever the user asks you to review, check or follow up on another session's work or progress ("review the session work", "check the other session", "the session finished, what next", "give me the prompt for it"), when another session's PR needs a pre-merge check, or when writing instructions for another agent session to run.
compatibility: Needs git and the GitHub CLI (gh). The bundled scripts need Python 3 and bash.
license: FSL-1.1-ALv2
---
<!-- SPDX-License-Identifier: FSL-1.1-ALv2 -->

# Review a working session

Work in software is split between three roles:

- **Generator**: the working session. It does the work: it writes code and documents, runs
  tests, commits, pushes and opens pull requests. It stops at the points its instructions name.
- **Reviewer**: you. You read what the generator did, check it against the real state of the
  repositories, report to the human, and write the generator's next instruction.
- **Human approver**: owns every decision that is hard to undo or belongs to them: merges,
  tags, repository and organisation settings, legal text, and choices between options.

Today a human usually carries your instruction blocks to the generator by pasting them, and
carries the generator's turns back by asking you to review. A harness may pass them as
messages instead. Either way the gates stay human: a harness that automates a merge or a tag
has removed the review, not sped it up.

**Why a reviewer exists at all:** a generator's report is a summary written by the same
process that did the work, and it is usually right. The cases where it isn't are the expensive
ones: a commit that never left the machine, a check that ran against an old head, a PR body
that silently closes an issue, a claim about a specification that the text doesn't support.
You catch those by checking the claims against sources of truth, not by re-reading the report.

The generator never merges, tags, changes settings, or decides for the human. You merge only
when the human confirms that specific merge.

## Before the first review

Read the project's reference folder: each folder under `references/`, other than the generic
files listed at the end, holds one project's specifics (its repositories, branch flow, required
checks, conventions, and where its methodology lives). Find the one for the project you are
reviewing and read its `README.md`. If none matches, ask the human for the branch flow and
required checks before you merge anything.

Then read your memory index, if the agent keeps one (for Claude Code, `MEMORY.md` in the
project's memory folder): it holds what earlier reviews recorded, and step 6 keeps it current.

## The review, step by step

One review covers one generator turn: everything since your last instruction.

### 1. Find the generator's transcript

Read the transcript rather than relying on what the human relays: it holds the commands the
generator ran and what they returned, not just its summary. Where transcripts live depends on
the agent; for Claude Code see [references/transcripts-claude-code.md](references/transcripts-claude-code.md).
To list candidates with their working directory, branch, last activity and first prompt:

```sh
python3 -I "${CLAUDE_SKILL_DIR}/scripts/extract_turns.py" --list ~/.claude/projects
```

For Claude Code, list the whole `~/.claude/projects` root, as above, and match by the `cwd`
column rather than by folder name. A session started from a multi-folder editor workspace is
stored under the primary folder's slug, not its own working directory, so the generator's
transcript can sit in a folder named after a different repository.

Pick by last activity, then confirm it is the right session: its working directory and branch
match the work, and your last instruction appears in it. Several sessions may be live at once,
and your own session's transcript is in the same place; never review yourself.

On the first review there is no instruction of yours to find. If the human hasn't said which
session or repository to review, ask. If the human started the generator with a prompt you
didn't write, ask for that prompt's first line and anchor on it.

### 2. Extract what it did since your last instruction

Anchor on a phrase that appears once, near the start of your last instruction block (its first
line usually works), and extract from there:

```sh
python3 -I "${CLAUDE_SKILL_DIR}/scripts/extract_turns.py" <transcript> --anchor "<phrase>" --tools --results 1500 > <scratch>/turn.md
```

`--tools` adds one line per command; `--results N` adds each command's output, cut to N
characters, which is what lets you check a claim against what actually ran. Without an anchor,
`--last-turns 1` takes the last human turn. Write digests to scratch space, never into a
repository: transcripts can hold secrets and personal data.

If the generator's context was compacted since your last instruction, the extract shows a
marker where the summary was; the summary is the generator's own account, so check it like any
other claim.

### 3. Verify, don't trust

List the claims the turn makes, then check each against its source of truth. Fetch first
(`git fetch --tags`) so you are not checking a stale local copy.

| Claim | Check it with |
|---|---|
| "Committed and pushed" | `git rev-parse origin/<branch>` equals the commit; `git branch -r --contains <sha>` |
| "The PR is open and green" | `gh pr view N --json state,headRefOid,baseRefOid,mergeStateStatus,statusCheckRollup,closingIssuesReferences` |
| "CI passed" | the run is for the PR's current head SHA, and every required check is in it by its exact name |
| "Tagged" | `git ls-remote --tags origin`: the tag exists, points where claimed, and no other tag moved |
| "Only X changed" | `git diff --stat <base>..<head>`, and the diff itself for anything that matters |
| "Merged" | the PR's state is MERGED and the merge commit is on the base branch of the remote |
| "The spec says ..." | the specification at the version the work is pinned to, not at its main branch |
| "The tool behaves like ..." | the tool's documentation, or a test; otherwise it is inference and is labelled so |
| "Deleted the secret" / "stopped the container" | look: the file is gone, the process is gone |

Say plainly which claims you verified and which you are inferring. Re-check your own earlier
statements as well: when the generator pushes back on your instruction, check its argument
against the source before you repeat yourself. The reviewer is wrong sometimes too.

### 4. Report

Keep it short and lead with the verdict. In order:

1. **Verdict**, one or two sentences: sound / needs changes / blocked, and what happens next.
2. **What I checked**, as bullets with the evidence: commit SHAs, run IDs, PR states.
3. **Problems**, each with the fix you want.
4. **Decisions for the human**, each with your recommendation and why. Where the generator
   has recommended, set yours beside its and say where they differ. It has usually read the
   sources in full and you have not, so check its reasoning against those sources before you
   disagree, and say so when its reasoning is the better one.
5. **Still open**, only if it changed.
6. **The instruction block** (step 7), last, so it is easy to copy. Always write one, even
   when the next step is only the human's answer or approval: the block is the one message
   that carries the work forward, whether a human pastes it or a harness passes it.

Report what the generator did well when it matters to the decision (a good catch, a careful
probe), not as padding.

### 5. Merge with the human

When a PR is ready, run this checklist, show the result, and ask the human to confirm the merge.
Each merge needs its own confirmation.

1. The PR is open, its base is the branch you expect, and its head is the commit you reviewed.
   Nothing was pushed after your review.
2. `mergeStateStatus` is CLEAN.
3. Every required check passed on that head commit, by its exact name.
4. The checks are fresh: the base the PR was tested against is the base branch's current head.
   If the base moved, update the branch or re-run the checks first.
5. `closingIssuesReferences` is `[]`, unless the PR is meant to close an issue. Check the body
   and every commit message for closing keywords, both as written and with line breaks joined:
   `python3 -I "${CLAUDE_SKILL_DIR}/scripts/closing_keywords.py" <file>...`
6. The project's commit conventions hold (sign-off, attribution trailers).
7. The title and description still describe what the PR does.

On confirmation, merge with a merge commit (`gh pr merge N --merge`), and keep long-lived
branches. Then verify: the PR reads MERGED, the merge commit is on the remote base branch, its
tree is the tree CI tested when that matters (before a tag), and no issue closed that should
not have. Only then tell the generator it is merged, quoting the merge commit. A generator told
"merged" before the merge either records a false state or stops and costs a round trip.

To wait for checks, use the bundled script, which runs under bash whatever the user's shell is:
`bash "${CLAUDE_SKILL_DIR}/scripts/wait_for_checks.sh" <owner/repo> <pr> [expected-head-sha]`.

### 6. Keep memory honest

If the agent has persistent memory, it tells the next review, or the next session, where to
find the state of the work and what has already happened. Keep it accurate rather than long:

- Project state lives in the repositories: their state files, briefs, the methodology's
  current position, and git itself. Memory points to where that state lives, and keeps a dated
  record of events (each merge, tag and decision, with its date and commit) plus lessons
  learned. A dated event never goes stale; present-tense status ("open", "green", "still to be
  applied") does, so memory doesn't hold it. (This skill and its references likewise hold
  procedure and lessons, never a project's current state.)
- When a note turns out wrong, correct it in place; do not append a contradiction below it.
- An explanation you could not prove is recorded as unexplained, not as the cause.
- The generator may edit the same notes. Read its edits, reconcile duplicates, and re-read a
  note immediately before you change it; then confirm your edit changed what you meant.
- Memory is often tied to the directory the reviewer starts in (Claude Code keeps it per
  project directory). Start the reviewer from the same directory each time, or it begins with
  none of its earlier notes and starts a separate store.
- No secrets, tokens, or personal data in notes.

### 7. Write the next instruction block

The generator reads the block and nothing else of your reply, so it must stand alone.

- **Start with the verified state**: "#12 is merged as `abc1234`", "the tag is pushed".
- **Then the human's decisions**: only what the human actually decided, in their own words
  where they gave them. A choice the human hasn't made yet is not a decision: ask first, or
  give it a decision slot (next bullet). The generator acts on whatever the block states as
  decided.
- **Give the human's decision a slot.** When the next step waits on the human, put a clearly
  marked line near the top of the block, such as `Human's answer (edit before pasting): ...`,
  prefilled with the recommendation your report gives. The human edits it before pasting, so
  the line as pasted is their decision; your report still calls it a recommendation. Where
  the human's own words are required (an acknowledgment, a sign-off), leave the line empty
  with a placeholder instead. Tell the generator to record the whole pasted block as the
  human's input, wherever its workflow records human input, and to name the slot's answer in
  its reply. Recording only the slot drops the rest of what the human sent.
- **Ask for the generator's recommendations.** When the generator will put a choice to the
  human, ask it for its recommendation on each one, with its reasoning and sources, marked as
  its own. Never tell it to withhold one ("without answering them", "make no
  recommendation"). It has read the sources in full, so its reasoning is usually the
  best-informed the human will see. Keeping a decision with the human means the generator
  stops for the answer, not that it stays silent.
- **Then numbered steps**, each one small enough to check.
- **Put explicit STOP points** where the human must look or decide, and say what is out of
  bounds: no merging, no tags, no settings, no fixes pushed past a failing gate.
- **Ask for evidence back**: commit SHAs, run IDs, `git ls-remote` output,
  `closingIssuesReferences`. Evidence requested is evidence you don't have to dig for.
- **Don't predict identifiers.** Never state a PR number, run ID or SHA that doesn't exist
  yet: say "the new PR", and ask for the number the command returns. A guessed number is
  wrong as soon as anything else is opened first, and the generator will use it.
- **Separate claiming from checking.** Tell the generator not to present another actor's
  action (your merge, the human's tag or setting) as its own work, but let it verify that
  action's result itself. "Don't re-check the merge" throws away a check; "don't claim the
  merge" keeps the record straight.
- **Restate the rules that bite**: refer to issues as "for #N", never with a closing keyword;
  the project's commit trailers; bash for wait scripts.
- **Make the first line distinctive**, so the next extraction can anchor on it.
- Put the block in one fenced `text` block, with no fence nested inside it.

## Hazards

Each line is a lesson that cost a round trip at least once. The reasons and the generic
evidence are in [references/hazards.md](references/hazards.md); read it before your first review.

1. Closing keywords close issues even when negated or split across lines; write "for #N".
2. Trusted-trigger workflows run the default branch's copy: prove a change after merge.
3. zsh-isms: no word splitting, `=word` expansion, `$VAR:x` modifiers, `path` tied to `PATH`.
4. A refused command is a stop, not an obstacle to route around.
5. Checks are only as fresh as the base they ran against.
6. Bot commands: one per comment, spaced out, no attribution line.
7. Secrets left in scratch files.
8. Never move or recreate a published tag.
9. The generator never merges, and never reports a merge it hasn't seen.
10. An unproven explanation is recorded as unexplained.
11. A bare `#N` links to the repository the text is posted in.
12. Renaming a required-check job blocks every PR; a skipped job counts as passing.
13. A local gate narrower than CI ships failures CI finds first.
14. Scripted edits anchored on non-unique text corrupt files.
15. A missing commit trailer means rewriting history.
16. The work branch must contain the base branch before you commit.
17. A rule placed where it isn't loaded never applies.
18. The reviewer can be wrong; invite push-back and re-check.
19. PR titles and descriptions go stale as scope grows.
20. "Done" can mean committed locally.
21. Local tool versions drift from the project's pins.
22. Third-party behaviour stated as fact.
23. Settings and organisation actions belong to the human.
24. Gate order: a PR that a later gate reviews stays open until that gate.
25. Shared memory edited by more than one session.
26. An instruction block states as decided only what the human decided; an open choice goes in a slot the human edits.
27. Don't predict identifiers: no PR number, run ID or SHA before it exists.
28. Separate claiming from checking: never claim another actor's action, always verify its result.
29. Project state lives in the repositories, not in the skill or in memory.
30. Keeping a decision with the human never means silencing the generator's recommendation.

## Reference files

- [references/hazards.md](references/hazards.md): each hazard's lesson, why it matters, and generic evidence.
- [references/transcripts-claude-code.md](references/transcripts-claude-code.md): where Claude Code keeps transcripts and how to read them.
- `references/<project>/`: one project's specifics, starting from its `README.md`.
- `scripts/extract_turns.py`, `scripts/closing_keywords.py`, `scripts/wait_for_checks.sh`: run them; they don't need reading first.
  The commands above already carry this skill's directory, filled in when this file was loaded.
  The shell has no variable holding it, so copy the full path from those commands.
