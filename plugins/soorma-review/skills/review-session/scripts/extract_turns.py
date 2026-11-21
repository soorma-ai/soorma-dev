# SPDX-License-Identifier: FSL-1.1-ALv2
"""Extract a digest of a Claude Code session transcript for review.

Keeps the human's messages and the agent's text. Skips thinking and subagent
(sidechain) records. Tool calls and tool results are opt-in.

List candidate transcripts, newest first, with each one's working directory,
branch, last activity and first prompt. DIR is one project folder, or a root
such as ~/.claude/projects, whose project folders are then scanned (exit 1 if
none is found):
    python3 -I extract_turns.py --list DIR

Extract a turn:
    python3 -I extract_turns.py TRANSCRIPT [--anchor TEXT | --since ISO | --last-turns N]
                                [--tools] [--results N] [--full-summaries]

--anchor TEXT   start at the last human message containing TEXT (exit 2 if none)
--since ISO     keep records at or after this UTC timestamp
--last-turns N  keep only the last N human turns
--tools         one line per tool call: its name and command or path
--results N     each tool result, cut to N characters (errors are marked)
"""

import argparse
import json
import os
import sys

COMPACT_PREFIX = "This session is being continued from a previous conversation"


def records(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def flat(text, limit=None):
    text = " ".join(str(text).split())
    return text if limit is None or len(text) <= limit else text[:limit] + " [...]"


def result_text(block):
    c = block.get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return " ".join(x.get("text", "") for x in c if isinstance(x, dict))
    return ""


def tool_line(block):
    inp = block.get("input") or {}
    detail = ""
    for key in ("command", "file_path", "pattern", "url", "description", "skill", "prompt"):
        if inp.get(key):
            detail = inp[key]
            break
    return f"  - tool: {block.get('name', '?')}: {flat(detail, 300)}"


def user_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(b.get("text", "") for b in content
                         if isinstance(b, dict) and b.get("type") == "text")
    return ""


def digest(path, tools=False, results=None, full_summaries=False, since=None):
    """Return a list of (is_human_turn, text) entries in transcript order."""
    out = []
    for r in records(path):
        if since and r.get("timestamp", "") < since:
            continue
        kind = r.get("type")
        if kind not in ("user", "assistant") or r.get("isSidechain"):
            continue
        ts = r.get("timestamp", "")[:19]
        content = (r.get("message") or {}).get("content")
        if kind == "user":
            text = user_text(content).strip()
            if text:
                summary = r.get("isCompactSummary") or text.startswith(COMPACT_PREFIX)
                if summary and not full_summaries:
                    out.append((False, f"\n## COMPACTION SUMMARY {ts} ({len(text)} chars omitted;"
                                       " use --full-summaries to include)\n"))
                else:
                    out.append((not summary, f"\n## USER {ts}\n{text}\n"))
            if results is not None and isinstance(content, list):
                for b in content:
                    if isinstance(b, dict) and b.get("type") == "tool_result":
                        mark = "ERROR " if b.get("is_error") else ""
                        out.append((False, f"  - result: {mark}{flat(result_text(b), results)}"))
        else:
            for b in content or []:
                if not isinstance(b, dict):
                    continue
                if b.get("type") == "text" and b.get("text", "").strip():
                    out.append((False, f"\n### ASSISTANT {ts}\n{b['text'].strip()}\n"))
                elif tools and b.get("type") == "tool_use":
                    out.append((False, tool_line(b)))
    return out


def select(entries, anchor=None, last_turns=None):
    human = [i for i, (h, _) in enumerate(entries) if h]
    if anchor is not None:
        hits = [i for i in human if anchor in entries[i][1]]
        if not hits:
            return None
        return entries[hits[-1]:]
    if last_turns:
        return entries[human[-last_turns]:] if len(human) >= last_turns else entries
    return entries


def summarise(path):
    """Return (cwd, branch, last activity, first human prompt) for a transcript."""
    cwd = branch = first = last = ""
    for r in records(path):
        if r.get("type") not in ("user", "assistant") or r.get("isSidechain"):
            continue
        cwd = r.get("cwd") or cwd
        branch = r.get("gitBranch") or branch
        last = r.get("timestamp", last)
        if not first and r["type"] == "user" and not r.get("isCompactSummary"):
            first = flat(user_text((r.get("message") or {}).get("content")), 80)
    return cwd, branch, last[:19], first


def list_dir(directory, limit=15):
    """List transcripts, newest first. DIR may be one project folder, or a
    root (such as ~/.claude/projects) whose immediate subdirectories hold them."""
    try:
        names = sorted(os.listdir(directory))
    except OSError as e:
        print(f"cannot list {directory}: {e.strerror}", file=sys.stderr)
        return 1
    found = [(None, os.path.join(directory, n)) for n in names if n.endswith(".jsonl")]
    if not found:
        for sub in names:
            folder = os.path.join(directory, sub)
            if not os.path.isdir(folder):
                continue
            try:
                inside = sorted(os.listdir(folder))
            except OSError as e:
                print(f"skipped {folder}: {e.strerror}", file=sys.stderr)
                continue
            found += [(sub, os.path.join(folder, n)) for n in inside if n.endswith(".jsonl")]
    if not found:
        print(f"no transcripts (*.jsonl) in {directory} or its immediate subdirectories",
              file=sys.stderr)
        return 1
    found.sort(key=lambda f: os.path.getmtime(f[1]), reverse=True)
    if len(found) > limit:
        print(f"({len(found) - limit} more not shown)", file=sys.stderr)
    for folder, path in found[:limit]:
        cwd, branch, last, first = summarise(path)
        name = os.path.basename(path)
        where = f"{folder}  {name}" if folder else name
        print(f"{where}\n    cwd={cwd} branch={branch} last={last}\n    first: {first}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("transcript", nargs="?")
    ap.add_argument("--list", metavar="DIR")
    group = ap.add_mutually_exclusive_group()
    group.add_argument("--anchor")
    group.add_argument("--since")
    group.add_argument("--last-turns", type=int)
    ap.add_argument("--tools", action="store_true")
    ap.add_argument("--results", type=int, metavar="N")
    ap.add_argument("--full-summaries", action="store_true")
    a = ap.parse_args(argv)

    if a.list:
        return list_dir(a.list)
    if not a.transcript:
        ap.error("a transcript path is required unless --list is given")

    entries = digest(a.transcript, a.tools, a.results, a.full_summaries, a.since)
    picked = select(entries, a.anchor, a.last_turns)
    if picked is None:
        print(f"anchor not found in any human message: {a.anchor!r}", file=sys.stderr)
        return 2
    sys.stdout.write("\n".join(t for _, t in picked) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
