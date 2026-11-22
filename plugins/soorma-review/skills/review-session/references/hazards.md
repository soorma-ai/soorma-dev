<!-- SPDX-License-Identifier: FSL-1.1-ALv2 -->

# Hazards

Each hazard below cost at least one round trip in practice. For each: the lesson, why it
matters, what to do, and one line of generic evidence. Project-specific incidents, where a
project records them, are in that project's reference folder.

## Contents

1. [Closing keywords](#1-closing-keywords)
2. [Trusted-trigger workflows run the default branch's copy](#2-trusted-trigger-workflows-run-the-default-branchs-copy)
3. [zsh-isms](#3-zsh-isms)
4. [A refused command is a stop](#4-a-refused-command-is-a-stop)
5. [Stale checks](#5-stale-checks)
6. [Bot commands](#6-bot-commands)
7. [Secrets in scratch files](#7-secrets-in-scratch-files)
8. [Published tags never move](#8-published-tags-never-move)
9. [The generator never merges](#9-the-generator-never-merges)
10. [Unproven explanations](#10-unproven-explanations)
11. [Bare issue references across repositories](#11-bare-issue-references-across-repositories)
12. [Required-check names](#12-required-check-names)
13. [A local gate narrower than CI](#13-a-local-gate-narrower-than-ci)
14. [Non-unique edit anchors](#14-non-unique-edit-anchors)
15. [Missing commit trailers](#15-missing-commit-trailers)
16. [A work branch behind its base](#16-a-work-branch-behind-its-base)
17. [Rules placed where they aren't loaded](#17-rules-placed-where-they-arent-loaded)
18. [The reviewer can be wrong](#18-the-reviewer-can-be-wrong)
19. [Stale PR titles and descriptions](#19-stale-pr-titles-and-descriptions)
20. ["Done" can mean local](#20-done-can-mean-local)
21. [Toolchain drift](#21-toolchain-drift)
22. [Third-party behaviour stated as fact](#22-third-party-behaviour-stated-as-fact)
23. [Settings belong to the human](#23-settings-belong-to-the-human)
24. [Gate order](#24-gate-order)
25. [Shared memory edited by more than one session](#25-shared-memory-edited-by-more-than-one-session)
26. [Decisions the human hasn't made](#26-decisions-the-human-hasnt-made)
27. [Predicted identifiers](#27-predicted-identifiers)
28. [Claiming versus checking](#28-claiming-versus-checking)
29. [Project state lives in the repositories](#29-project-state-lives-in-the-repositories)
30. [The generator's recommendation](#30-the-generators-recommendation)

## 1. Closing keywords

**Lesson:** GitHub closes an issue when a PR description, or a commit message that reaches the
default branch, puts `close`, `fix` or `resolve` (in any form) before an issue reference:
`#N`, `owner/repo#N`, or the issue's URL. It does so even in a negation ("doesn't close #N"),
and even when a line break separates the keyword from the reference.

**Why:** the issue closes silently on merge, and nobody notices until someone looks for it.

**Do:** write "for #N" or "#N stays open until ...". Before posting any PR description,
comment or commit message, run `scripts/closing_keywords.py` on it; it checks the text as
written and with line breaks joined. Before every merge, `closingIssuesReferences` must be `[]`
unless closing is intended.

**Evidence:** a merged PR whose description said an amendment "resolves" a gap closed the gap's
issue weeks early; later, two draft bodies saying "doesn't close #N" were caught before posting.

## 2. Trusted-trigger workflows run the default branch's copy

**Lesson:** workflows triggered by `pull_request_target` (and `issue_comment`) run the workflow
file from the default branch, not from the PR. A PR that changes such a workflow is tested by
the old version.

**Why:** the PR's green check proves nothing about the change, and a broken change blocks every
later PR once merged, including the revert, if the check is required.

**Do:** after merging such a change, prove it with a throwaway PR, closed unmerged. Know the
escape route before merging: who can lift the branch protection briefly if the check breaks.

**Evidence:** a fix to a sign-off check could never run on its own PR and was reverted; a later
action-pin change showed its own PR still downloading the old pin, and a throwaway PR proved the
new one.

## 3. zsh-isms

**Lesson:** when the agent's shell is zsh, POSIX habits break, for the reviewer as much as for
the generator:

- unquoted variables don't word-split (`set -- $c` leaves one argument);
- a word starting with `=` is expanded as a command path (`echo ===` fails with "== not found");
- `$VAR:x` is read as a history modifier, so `"$T:contract"` loses characters; write `"${T}:contract"`;
- `path` is tied to `PATH`, so a loop variable named `path` empties the command search path.

**Why:** the failures are quiet. A wait loop runs out its full timeout, a check reads no files
and reports nothing wrong, a revision string is silently mangled.

**Do:** run scripts with `bash` explicitly, read multiple values with
`read -r a b <<< "$line"`, brace every variable that is followed by `:` or text, and don't
name a variable `path`. macOS ships bash 3: no associative arrays.

**Evidence:** a CI wait loop timed out after 25 minutes with every check finished; a link
check passed a whole file list as one argument and read nothing; `===` separators failed in the
reviewer's own commands more than a dozen times.

## 4. A refused command is a stop

**Lesson:** an agent's permission or safety check may refuse a command, such as opening a PR.

**Why:** routing around a refusal (another command, another tool) defeats the reason for the
check, and the reason is usually not visible.

**Do:** the generator stops and reports the refusal, with the exact command and any file it
prepared. Retry the parts that are separable (push first, then open the PR). If it is still
refused, the human or the reviewer takes the step, after reading what would be posted.

**Evidence:** a combined push-and-open-PR command was refused twice; the prepared body turned
out to contain a closing keyword, which the reviewer fixed before opening the PR itself.

## 5. Stale checks

**Lesson:** a PR's checks tested its head merged with the base as it was then. Once the base
moves, the checks no longer describe what the merge will produce.

**Why:** where nothing re-tests the base branch after a merge, an untested combination ships.

**Do:** before merging, confirm the PR's tested base is the base branch's current head. If it
moved, update the branch or re-run the checks. Before tagging a merge commit, confirm its tree
is the tree CI tested.

**Evidence:** after one dependency PR merged, a second one was held for a fresh run rather than
merged on checks from the old base.

## 6. Bot commands

**Lesson:** dependency bots act on comment commands, and they are particular about them.

**Why:** several commands posted within seconds can be ignored, and an attribution line in the
comment can stop the command being recognised.

**Do:** post one command per comment, a little apart, with nothing else in the comment. If a
rebase command is ignored, the recreate command rebuilds the PR. A bot closes a PR whose update
is already on the base branch only on its next run; close it yourself with a pointer if it
matters sooner.

**Evidence:** three rebase commands posted within three seconds got one response; recreate
worked at once.

## 7. Secrets in scratch files

**Lesson:** test databases, sign-in flows and backups leave credentials in scratch files and
logs.

**Why:** scratch directories outlive the session, get copied, and get published by accident.

**Do:** keep credentials in memory or in a mode-0600 file, and delete it when done; stop the
throwaway services that used it. Before the generator finishes, have it scan its scratch space
for secret-shaped strings, and say what it deleted.

**Evidence:** a test database's connection string, password included, was left in a scratch
env file; a backup copy of a workflow file in scratch also matched the secret scan.

## 8. Published tags never move

**Lesson:** once pushed, a tag is a promise that its name means one commit. Consumers pin it,
cache it, and compare against it.

**Why:** moving or recreating a tag breaks every consumer that recorded the old target, and
nothing tells them.

**Do:** publish a new tag instead (for example a revision suffix). Write the annotation to a
file, show it to the human, create the tag from that file unchanged, push only that tag (never
`--tags`), and re-check that every earlier tag still points where it did.

**Evidence:** a contract release needed a fix; it went out as a new revision tag, and the
original tag was verified unchanged after each push.

## 9. The generator never merges

**Lesson:** merging is the human's decision, carried out with the reviewer; the generator stops
when its PR is ready and records nothing as merged until the code host shows it merged.

**Why:** a merge is the gate the whole review exists for. A generator told "merged" before the
merge either records false state or stops and costs a round trip.

**Do:** the reviewer runs the pre-merge checklist, the human confirms, the reviewer merges and
verifies, and only then does the instruction block say "merged as `<sha>`".

**Evidence:** twice, a generator was told a PR was merged when it wasn't; both times it checked,
found the PR open, and stopped.

## 10. Unproven explanations

**Lesson:** when something odd happens and you can't prove why, record it as unexplained.

**Why:** a guessed cause written down becomes a rule, and the rule outlives the guess.

**Do:** state the observation and what was ruled out. Correct any note that recorded the guess.

**Evidence:** a PR read as blocked to one token and clean anonymously; a token-scope theory was
written down, then disproven when the same token merged a workflow change.

## 11. Bare issue references across repositories

**Lesson:** `#N` links to issue N of the repository where the text is posted.

**Why:** an instruction or issue body copied from one repository to another silently points at
the wrong issue, and with a closing keyword, closes it.

**Do:** write `owner/repo#N` for any issue outside the repository the text lands in.

**Evidence:** a handover prompt saved as an issue in a consuming repository referred to the
producer's issue as a bare number, and was qualified before posting.

## 12. Required-check names

**Lesson:** branch protection requires checks by job name. Renaming a required job leaves the
required name pending for ever, so every PR is blocked. A job skipped by its own condition
counts as passing.

**Why:** the first sign is a PR that can never merge, or a required check that never really ran.

**Do:** keep required job names stable, with a comment on the job saying it is required, or
change the protection in the same change. Know which required jobs skip on which events.

**Evidence:** workflow comments in protected repositories warn that a rename blocks every PR
into the default branch.

## 13. A local gate narrower than CI

**Lesson:** if the generator's pre-commit checks skip something CI runs (an image build, an
integration suite), failures surface in CI, after the push.

**Why:** each CI round trip costs minutes to tens of minutes, and a red PR invites rushed fixes.

**Do:** run locally whatever CI runs that the change reaches, such as the image build when a
dependency of the image changes.

**Evidence:** a new workspace package was missing from a Dockerfile's copy list; the local gate
never built the image, so the failure first appeared in CI.

## 14. Non-unique edit anchors

**Lesson:** a scripted insert or replace anchored on text that also appears elsewhere edits
the wrong place.

**Why:** the damage is structural (a table split in two, a section inside another) and easy to
miss in review.

**Do:** anchor on a whole line, such as `"\n## Heading\n"`, assert it occurs exactly once,
and re-check the structure you touched.

**Evidence:** an insertion anchored on a heading's words matched the same words inside a table
row and split the table.

## 15. Missing commit trailers

**Lesson:** where a check requires a trailer on every commit (a sign-off, for example), one
commit without it fails the PR.

**Why:** the fix is a history rewrite and a force push, which needs the human's permission.

**Do:** set the trailer on every commit from the start (`git commit -s`), and check the whole
range before pushing.

**Evidence:** two early commits without a sign-off forced a one-off rebase and force push.

## 16. A work branch behind its base

**Lesson:** where work happens on a long-lived branch and reaches the default branch by PR,
that branch must contain the default branch's head before new work starts.

**Why:** a PR from elsewhere, or a bot's PR into the default branch, leaves the work branch
behind, and the next PR carries a confusing diff or a conflict.

**Do:** before committing, fetch, and check that the work branch contains `origin/<default>`
and matches its own remote. Fast-forward it after each merge.

**Evidence:** a PR merged from a feature branch left the work branch behind, and the branches
had to be re-synced.

## 17. Rules placed where they aren't loaded

**Lesson:** a rule only applies if the agent loads the file it is in, at the point it is needed.

**Why:** a rule placed in an optional module and marked "applies whether or not this module is
enabled" is never read when the module is off.

**Do:** for any change to rules or instructions, trace the loading path: which file is always
loaded, which only on opt-in, which at a later stage.

**Evidence:** a planned closing-keyword rule was first placed in an opt-in extension; it was
moved to a file every session loads.

## 18. The reviewer can be wrong

**Lesson:** your instruction can be wrong: a misread section, a convention misremembered.

**Why:** a generator that follows a wrong instruction to the letter builds the error in.

**Do:** invite push-back in your instructions. When the generator disagrees, check its argument
against the source, and say plainly when you were wrong. Re-check your own earlier claims when
a later review depends on them.

**Evidence:** reviews cited a specification section by its title and missed a subsection; a
generator spotted that an instruction contradicted a settled convention and asked instead of
following it.

## 19. Stale PR titles and descriptions

**Lesson:** as more work lands on a PR's branch, its title and description stop describing it.

**Why:** the description is the record reviewers and future readers use; a stale one misleads
both, and may overstate scope.

**Do:** re-read the title and description before every merge, and update them with the scope.

**Evidence:** a long-running PR's title still named its first stage after it had come to carry
a whole phase.

## 20. "Done" can mean local

**Lesson:** a generator may report work as done that was committed but never pushed, or pushed
to a different branch.

**Do:** compare the local branch with its remote, and look for the commit on the remote.

**Evidence:** a commit reported as ready was one ahead of its remote, because the push had been
refused.

## 21. Toolchain drift

**Lesson:** the tools on the machine (runtime, package manager, CLI) drift from the versions
the project pins.

**Why:** a local result from the wrong version proves little, and some tools refuse to work at
all on an old version.

**Do:** before trusting a local run, compare tool versions with the project's pins. Prefer
running a pinned version explicitly.

**Evidence:** a stale `PATH` ran an old runtime until the generator noticed; an old package
manager couldn't read a newer lockfile format.

## 22. Third-party behaviour stated as fact

**Lesson:** claims about how a tool, a specification or a service behaves are often stated
from memory.

**Do:** check the documentation, or test it. If you can do neither, label the claim as
inference in the report and the record.

**Evidence:** a release note claimed a version with build metadata orders after the plain one,
which SemVer contradicts; a bot configuration's grouping was assumed, and the docs said
otherwise.

## 23. Settings belong to the human

**Lesson:** repository and organisation settings (protection rules, policies, forks, Actions
permissions) change what every later PR can do.

**Do:** the generator stops before any settings change and says what it would change. The
human applies it, or the reviewer does with the human's explicit approval, and reads it back
afterwards.

**Evidence:** a generator that created a fork stopped before protecting it, and the protection
was applied and read back from the reviewing side.

## 24. Gate order

**Lesson:** when a process reviews a PR at a later gate, merging the PR early skips that review.

**Do:** know which gate each PR belongs to, and keep it open until that gate. Let later work
land on the same branch so it joins the PR.

**Evidence:** a phase's PR was kept open past an earlier recommendation to merge it, because the
phase's formal review gate came later.

## 25. Shared memory edited by more than one session

**Lesson:** generator and reviewer may both edit the same memory notes and index.

**Why:** an edit made from a copy read earlier overwrites the other session's change, and a
search-and-replace whose target changed silently matches nothing.

**Do:** re-read a note immediately before editing it, edit by exact match with a tool that fails
when the target is missing, and confirm afterwards that the edit changed what you meant. Merge
duplicate notes rather than keeping both.

**Evidence:** a scripted replacement in the memory index changed nothing, because the other
session had rewritten the line in the meantime.

## 26. Decisions the human hasn't made

**Lesson:** an instruction block states as decided only what the human actually decided.

**Why:** the generator acts on whatever the block calls a decision. A reviewer's recommendation
written as "the human's decision" becomes one without the human having made it, and the record
the generator keeps says the human chose it.

**Do:** before writing the block, separate what the human decided from what you recommend. For
an open choice, ask the human first; or, if the block has to go now, write the item as your
recommendation, marked as awaiting the human's decision, and tell the generator to stop before
acting on it.

**Evidence:** a trial review's instruction block listed two fixes under the human's decisions,
to be made before the merge, when the human had not yet decided anything.

## 27. Predicted identifiers

**Lesson:** an instruction never states an identifier that doesn't exist yet: a PR or issue
number, a run ID, a commit SHA.

**Why:** numbers are assigned when the thing is created, and anything else created first (a bot's
PR, another session's issue) takes the number you guessed. The generator then waits on, checks,
or comments on the wrong item.

**Do:** say "the new PR" or "the commit you make", and ask for the identifier the command
returns. Use that identifier from then on.

**Evidence:** an instruction for a follow-up named it by the PR number it expected to get, before
the PR existed.

## 28. Claiming versus checking

**Lesson:** keep two things apart: who did an action, and whether its result is right. The
generator doesn't claim another actor's action (a merge, a tag, a setting) as its own work. It
does verify that action's result itself.

**Why:** an instruction that says "don't re-check the merge" removes an independent check, and a
report that says "I merged" when the reviewer did misstates the record. Both errors come from
treating attribution and verification as the same thing.

**Do:** write "the reviewer merged #N as `<sha>`; don't describe it as your work, but check
main's head yourself".

**Evidence:** an instruction told the generator not to re-check a merge the reviewer had made,
where the point was only that it shouldn't claim the merge.

## 29. Project state lives in the repositories

**Lesson:** a project's current state (what is open, what is green, which milestone is in
flight) lives in its repositories: state files, briefs, the methodology's current position, and
git itself. A skill and its references hold procedure and lessons. A reviewer's memory holds
pointers to that state, lessons, and a dated record of events: "#N merged as `<sha>` on
`<date>`", "the human decided X on `<date>`". A dated event stays true; present-tense status
("open", "green", "still to be applied") is the copy that goes stale.

**Why:** a copy of state goes stale as soon as the repository moves on, and a stale copy read
with confidence is worse than none.

**Do:** record where the state is ("the brief's status line", "aidlc-state.md in that
repository"), not what it says, and record events with their date and commit. Never write
status in the present tense. Read the source when you need the state.

**Evidence:** a memory note written during the work recorded a repository's branch protection as
still to be applied; within the hour it was applied, the note was stale, and the other session
had to correct it.

## 30. The generator's recommendation

**Lesson:** when a generator puts a choice to the human, it gives its recommendation with its
reasoning. An instruction never tells it to withhold one.

**Why:** the generator has read the specifications, the earlier decisions and the code in
full; the reviewer has read parts of them. A generator told to present options "without
answering them" drops the best-informed reasoning the human would have seen, and the human is
left with the reviewer's less-informed recommendation instead. Hazard 26 keeps the decision
with the human; that rule concerns what the block states as decided, not whether anyone
recommends.

**Do:** ask the generator for a recommendation on each choice, with its reasoning and sources,
marked as its own, and tell it to stop for the human's answer. In your report, set your
recommendation beside the generator's, check its reasoning against its sources, and say where
it is better than yours.

**Evidence:** an opening instruction for a specification session told it to put the framing
questions to the human "without answering them", so it gave no recommendations. A follow-up
asked for them; its recommendations differed from the reviewer's on three of six questions,
were better grounded on at least two, and the human chose to answer with them.
