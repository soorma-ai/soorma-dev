# SPDX-License-Identifier: FSL-1.1-ALv2
"""Find GitHub closing keywords before issue references.

GitHub closes an issue when a PR description, or a commit message reaching the
default branch, puts close/fix/resolve (any form) before #N, owner/repo#N, or
the issue's URL. It does so even in a negation ("doesn't close #N") and even
across a line break. This checks text as written (line by line, as grep would)
and with line breaks joined.

    python3 -I closing_keywords.py FILE...      # or text on stdin
    git log --format=%B main..dev | python3 -I closing_keywords.py

Exits 1 and prints each hit if any is found; exits 0 and prints nothing if clean.
"""

import re
import sys

KEYWORD = r"\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\b"
REFERENCE = (
    r"(?:[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)?#\d+"
    r"|https?://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/issues/\d+"
)
PATTERN = re.compile(rf"{KEYWORD}\s*:?[ \t]+(?:{REFERENCE})", re.IGNORECASE)
JOINED = re.compile(rf"{KEYWORD}\s*:?\s+(?:{REFERENCE})", re.IGNORECASE)


def find(text):
    """Return (mode, match) pairs: 'as written' hits per line, then 'joined' hits."""
    hits = []
    for n, line in enumerate(text.splitlines(), start=1):
        for m in PATTERN.finditer(line):
            hits.append((f"as written, line {n}", m.group(0)))
    joined = " ".join(text.split())
    written = {h[1].lower() for h in hits}
    for m in JOINED.finditer(joined):
        snippet = " ".join(m.group(0).split())
        if snippet.lower() not in {" ".join(w.split()) for w in written}:
            hits.append(("only with line breaks joined", snippet))
    return hits


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    sources = [(p, open(p, encoding="utf-8").read()) for p in argv] or [("stdin", sys.stdin.read())]
    found = False
    for name, text in sources:
        for mode, snippet in find(text):
            found = True
            print(f"{name}: {mode}: {snippet!r}")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
