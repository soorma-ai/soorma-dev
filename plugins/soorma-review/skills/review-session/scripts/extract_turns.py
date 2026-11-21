# SPDX-License-Identifier: FSL-1.1-ALv2
"""Extract a digest of a Claude Code session transcript for review.

Keeps the human's messages and the agent's text. Skips thinking and subagent
(sidechain) records. Tool calls and tool results are opt-in.

List candidate transcripts in a directory, newest first:
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


def list_dir(directory):
    rows = []
    for name in os.listdir(directory):
        if not name.endswith(".jsonl"):
            continue
        path = os.path.join(directory, name)
        cwd = branch = first = last = ""
        for r in records(path):
            if r.get("type") not in ("user", "assistant") or r.get("isSidechain"):
                continue
            cwd = r.get("cwd") or cwd
            branch = r.get("gitBranch") or branch
            last = r.get("timestamp", last)
            if not first and r["type"] == "user" and not r.get("isCompactSummary"):
                first = flat(user_text((r.get("message") or {}).get("content")), 80)
        rows.append((os.path.getmtime(path), name, cwd, branch, last[:19], first))
    rows.sort(reverse=True)
    for _, name, cwd, branch, last, first in rows[:15]:
        print(f"{name}\n    cwd={cwd} branch={branch} last={last}\n    first: {first}")


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
        list_dir(a.list)
        return 0
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
