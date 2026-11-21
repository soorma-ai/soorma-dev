<!-- SPDX-License-Identifier: FSL-1.1-ALv2 -->

# Claude Code transcripts

How to find and read a Claude Code session's transcript when that session is the generator.
This file is about one agent's storage format; the review procedure itself doesn't depend on it.

## Where they are

Each session is one JSON Lines file, named by its session ID:

```text
~/.claude/projects/<project-slug>/<session-id>.jsonl
```

The slug is derived from the directory the session started in, with each path separator
turned into `-`. Sessions started from a multi-folder editor workspace are stored under the
primary folder's slug, so the generator's transcript and your own can sit side by side.
`extract_turns.py --list <directory>` shows each file's working directory, branch, last
activity and first prompt, newest first.

The file grows while the session runs. Extract once the generator has finished its turn; if
you extract mid-turn, say so in your report.

## What a line holds

Each line is one JSON record. The ones a review needs:

| `type` | `message.content` | Use |
|---|---|---|
| `user` | a string, or blocks of `text` | the human's prompts and pasted instruction blocks |
| `user` | blocks of `tool_result` | what a command returned; `is_error` marks failures and refusals |
| `assistant` | blocks of `text`, `tool_use`, `thinking` | the generator's words, and the commands it ran (`tool_use.input`) |

Every record also has `timestamp` (UTC), `cwd`, `gitBranch` and `sessionId`. Skip the other
record types (attachments, request metadata, titles, file-history snapshots).

- **Subagents:** records with `isSidechain: true` come from subagents the generator started.
  Their results reach the main thread as tool results, so the extract skips them.
- **Compaction:** when the generator's context fills, a `user` record with
  `isCompactSummary: true` holds a summary of the earlier conversation, starting "This session
  is being continued from a previous conversation". It is the generator's own account: check it
  like any other claim.
- **Pasted text:** a pasted instruction block appears inside the user's text, wrapped in
  `<pasted_content>` tags. That makes the first line of your last block a good anchor.
- **Refusals:** when Claude Code's permission system or its auto-mode safety check refuses a
  command, the `tool_result` has `is_error: true` and says the permission was denied. The
  message invites the agent to try another way; the generator should stop and report instead
  (hazard 4).

## Privacy

Transcripts hold everything the session saw: file contents, command output, and sometimes
credentials and personal data. Keep digests in scratch space, never commit them, and paraphrase
rather than quote when a finding has to be written down somewhere durable.
