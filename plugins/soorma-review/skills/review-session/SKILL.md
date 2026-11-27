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
  tags, repository and organisation settings, legal text, and choices between options. Where
  you carry out a merge or a tag, you do it only on the human's confirmation of that one.

Today a human usually carries your instruction blocks to the generator by pasting them, and
carries the generator's turns back by asking you to review. A harness may pass them as
messages instead. Either way the gates stay human: a harness that automates a merge or a tag
has removed the review, not sped it up.

**Why a reviewer exists at all:** a generator's report is a summary written by the same
process that did the work, and it is usually right. The cases where it isn't are the expensive
ones: a commit that never left the machine, a check that ran against an old head, a PR body
that silently closes an issue, a claim about a specification that the text doesn't support.
You catch those by checking the claims against sources of truth, not by re-reading the report.

The generator never merges, tags, changes settings, or decides for the human. You merge, or
create a tag, only when the human confirms that specific merge or tag.

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

**If you were handed the generator's session**, by a harness or by the human, use it directly
and skip the listing. That means its session ID or transcript path, together with the anchor.
For Claude Code, pass the ID as `--session <ID>` in step 2's command, in place of the
transcript path. Still confirm three things:

- the working directory and branch match the work (the extractor prints them);
- the session isn't your own;
- the anchor is the first line of your last block. If it isn't, the human edited or replaced
  the block: review against what was sent (step 2) and say so in your report.

A handed identifier is observed, not predicted (hazard 27). If it doesn't resolve, stop and
ask; don't fall back to guessing from the listing.

Otherwise, list candidates with their working directory, branch, last activity and first
prompt:

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
`--last-turns 1` takes the last human turn.

Review the generator against the block as it was pasted (the start of its turn in the
transcript), not against the block you wrote. The human may have edited it, or pasted a
replacement. If your anchor isn't found, look for what the human changed. Write digests to scratch space, never into a
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
| "The tool behaves like ..." | its code at the pinned commit, where you can read it; otherwise its documentation, or a test; otherwise it is inference and is labelled so. A README is a summary and can omit a mode |
| "Deleted the secret" / "stopped the container" | look: the file is gone, the process is gone |

Say plainly which claims you verified and which you are inferring. Re-check your own earlier
statements as well: when the generator pushes back on your instruction, check its argument
against the source before you repeat yourself. The reviewer is wrong sometimes too.

A claim that a source does *not* say something needs the whole section, not a truncated view.
Command output in the extract is cut to `--results` characters, so re-run the command or read
the file before you contradict the generator about what a source says (hazard 32).

List the choices the generator made without asking. This is the review's own check, whether or
not the generator's workflow asks it to list them. For each, say whether it was the
generator's to make or the human's, and put the human's under *Decisions for the human*,
especially where earlier, similar work put the same kind of question to the human.

### 4. Report

Keep it short and lead with the verdict. In order:

1. **Verdict**, one or two sentences: sound / needs changes / blocked, and what happens next.
2. **What I checked**, as bullets with the evidence: commit SHAs, run IDs, PR states.
3. **Problems**, each with the fix you want.
4. **Decisions for the human**, each with your recommendation and why. Where the generator
   has recommended, set yours beside its and say where they differ. It read everything the
   work depends on; you read selectively, to check claims, which suits checking and not
   design judgement. Before you recommend against it, read in full the sources its reasoning
   cites; if you haven't, defer to its recommendation and say so. Say so too when its
   reasoning is the better one.
5. **Still open**, only if it changed.
6. **The instruction block** (step 7), last, so it is easy to copy. Always write one, even
   when the next step is only the human's answer or approval: the block is the one message
   that carries the work forward, whether a human pastes it or a harness passes it. The
   human's answer or approval goes on the block's `HUMAN DECISION:` line.

Report what the generator did well when it matters to the decision (a good catch, a careful
probe), not as padding.

### 5. Merge and tag with the human

When a PR is ready, run this checklist, show the result, and ask the human to confirm the merge.
Each merge needs its own confirmation.

1. The PR is open, its base is the branch you expect, and its head is the commit you reviewed.
   Nothing was pushed after your review.
2. `mergeStateStatus` is CLEAN.
3. Every required check passed on that head commit, by its exact name.
4. The checks are fresh: the base the PR was tested against is the base branch's current head.
   If the base moved, update the branch or re-run the checks first.
5. `closingIssuesReferences` is `[]`, or lists exactly the issues the PR is meant to close. Check the body
   and every commit message for closing keywords, both as written and with line breaks joined:
   `python3 -I "${CLAUDE_SKILL_DIR}/scripts/closing_keywords.py" <file>...`
6. The project's commit conventions hold (sign-off, attribution trailers).
7. The title and description still describe what the PR does.

On confirmation, merge with a merge commit (`gh pr merge N --merge`), and keep long-lived
branches. Then verify: the PR reads MERGED, the merge commit is on the remote base branch, its
tree is the tree CI tested when that matters (before a tag), and no issue closed that should
not have. Only then tell the generator it is merged, quoting the merge commit. A generator told
"merged" before the merge either records a false state or stops and costs a round trip.

**Tags** belong to the human as merges do. Where the human has you create them, create each
one only on the human's confirmation of that tag, after the merge it marks is verified: an
annotated tag on the merge commit, with its message shown to the human first and written in
the project's form, pushed alone (`git push origin refs/tags/<tag>`, never `--tags`). Then
check with `git ls-remote --tags origin` that it peels to the merge commit and that no other
tag moved (hazard 8). The project's tag names and message forms are in its reference folder.

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
- **A lesson about this skill goes to memory, not into the skill.** Record it with its date,
  trigger and evidence. Don't edit the skill or its references during a review, even for a
  small fix: the skill changes through its own loop, in which a separate working session folds
  accumulated lessons into it and a review checks that change. That way no reviewer reviews
  its own change.

### 7. Write the next instruction block

The generator reads the block and nothing else of your reply, so it must stand alone.

- **Start with the verified state**, as the review's claims, each checked at its source: "#12
  is merged as `abc1234`", "the tag is pushed". A fact a decision rests on goes here, not on
  the decision line (hazard 33).
- **Then the decision line.** The human's decision for this block goes on one line that
  starts with the exact marker `HUMAN DECISION:`, placed after the verified state. A block has
  at most one such line, and has none only when nothing in it waits on or carries a decision
  of the human's. The text after the marker, as sent (pasted by the human or released by a
  harness), is the human's decision, whether they have made it already or are still to make
  it:
  - **Already decided:** write their decision, in their own words where they gave them.
  - **Still to decide:** prefill it with the recommendation your report gives. The human
    edits it before sending, so the line as sent is their decision; your report still calls
    it a recommendation. Where the human's own words are required (an acknowledgment, a
    sign-off), write `HUMAN DECISION: <in your own words>`, and tell the generator that a
    line still holding the placeholder is no decision, and to stop.

  The line carries decisions only: several answers share it, separated by semicolons. It holds
  no instruction to the human (the report says what to edit) and no factual premise (hazard
  33). A choice the human hasn't made is stated as decided nowhere else in the block: the
  generator acts on whatever the block states as decided. Tell the generator to record the
  whole block as sent as the human's input, wherever its workflow records human input, and to
  quote the decision line in its reply. Recording only the line drops the rest of what the
  human sent.
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
- **Say where each constraint comes from.** A generator running a workflow already loads that
  workflow's rules, so the block must not become a second rulebook that competes with them.
  Before writing a block for a stage, read that stage's section of the generator's rules.
  Then give each constraint its source:
  - **the workflow's own rule**: restate it only as a reminder, citing its section, and never
    reword it into something stricter;
  - **this review procedure, or the human's ownership** (no merging, tagging or settings
    changes; hazards 8, 9, 23), which the workflow may not say: label it as the review's;
  - **the human's own decision**, such as pacing ("don't start the next stage until told"):
    label it as the human's.

  The rules that bite most often still belong in the block, with their source: refer to
  issues as "for #N", never with a closing keyword; the project's commit trailers; bash for
  wait scripts.
- **Add a precedence line**: where the block conflicts with the generator's rules, the rules
  win, and the generator stops and reports the conflict rather than following either silently.
- **Make the first line distinctive**, so the next extraction can anchor on it.
- Put the block in one fenced `text` block, with no fence nested inside it.

This skeleton shows where things go, not wording to copy:

```text
<distinctive first line: what this block is, and which round>

VERIFIED STATE (review, <date>)
- <each fact the review checked, with its source: SHAs, PR states, run IDs>

HUMAN DECISION: <the human's decision, or the recommendation for them to edit>

STEPS
1. <a step small enough to check>
2. STOP. Report: <the evidence to send back>

RULES AND WHERE THEY COME FROM
- <each constraint, labelled as the workflow's, the review's, or the human's>
- Precedence: where this block conflicts with your rules, the rules win; stop and report.

OUT OF BOUNDS: <merging, tagging, settings, and anything else this turn must not do>
```

## Hazards

Each line is a lesson that cost a round trip at least once. The reasons and the generic
evidence are in [references/hazards.md](references/hazards.md); read it before your first review.

1. Closing keywords close issues even when negated or split across lines; write "for #N", and leave an intended close alone.
2. Trusted-trigger workflows run the default branch's copy: prove a change after merge.
3. zsh-isms: no word splitting, `=word` expansion, `$VAR:x` modifiers, `path` tied to `PATH`.
4. A refused command is a stop, not an obstacle to route around.
5. Checks are only as fresh as the base they ran against.
6. Bot commands: one per comment, spaced out, no attribution line.
7. Secrets left in scratch files.
8. Never move or recreate a published tag.
9. The generator never merges or tags, and never reports a merge or tag it hasn't seen; the reviewer does either only on the human's confirmation.
10. An unproven explanation is recorded as unexplained.
11. A bare `#N` links to the repository the text is posted in.
12. Renaming a required-check job blocks every PR; a skipped job counts as passing.
13. A local gate narrower than CI ships failures CI finds first.
14. Scripted edits anchored on non-unique text corrupt files.
15. A missing commit trailer means rewriting history.
16. The work branch must contain the base branch before you commit.
17. A rule placed where it isn't loaded never applies.
18. The reviewer can be wrong; invite push-back, re-check, and test the rules you propose.
19. PR titles and descriptions go stale as scope grows.
20. "Done" can mean committed locally.
21. Local tool versions drift from the project's pins.
22. Third-party behaviour stated as fact.
23. Settings and organisation actions belong to the human.
24. Gate order: a PR that a later gate reviews stays open until that gate.
25. Shared memory edited by more than one session.
26. An instruction block states as decided only what the human decided, on its one `HUMAN DECISION:` line; an open choice is prefilled there for the human to edit.
27. Don't predict identifiers: no PR number, run ID or SHA before it exists.
28. Separate claiming from checking: never claim another actor's action, always verify its result.
29. Project state lives in the repositories, not in the skill or in memory.
30. Keeping a decision with the human never means silencing the generator's recommendation; disagree only after reading its sources in full.
31. An instruction block restates the generator's own rules only with their source, never stricter.
32. "The source doesn't say X" needs the whole text; a truncated view hides the sentence that does.
33. The decision line carries decisions only: a fact goes in the verified state, checked at its source.

## Reference files

- [references/hazards.md](references/hazards.md): each hazard's lesson, why it matters, and generic evidence.
- [references/transcripts-claude-code.md](references/transcripts-claude-code.md): where Claude Code keeps transcripts and how to read them.
- `references/<project>/`: one project's specifics, starting from its `README.md`.
- `scripts/extract_turns.py`, `scripts/closing_keywords.py`, `scripts/wait_for_checks.sh`: run them; they don't need reading first.
  The commands above already carry this skill's directory, filled in when this file was loaded.
  The shell has no variable holding it, so copy the full path from those commands.
