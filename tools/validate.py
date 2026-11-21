# SPDX-License-Identifier: FSL-1.1-ALv2
"""Repository checks for soorma-dev, run by CI's Validate job.

Run from the repository root, with the standard library only:

    python3 -I tools/validate.py

Checks every file git tracks:

1. manifests  - .claude-plugin/marketplace.json and each plugin's
                .claude-plugin/plugin.json parse, carry their required fields,
                and agree with each other; every other tracked .json parses.
2. skills     - each skills/<name>/SKILL.md opens with frontmatter whose name
                matches its directory, whose description is present, and whose
                keys are all ones every Agent Skills surface accepts.
3. links      - every relative Markdown link resolves to a tracked file or
                directory inside the repository.
4. secrets    - no private key, token, credential assignment, email address
                outside the allowlist, or local home-directory path.
5. workflows  - every action is pinned to a full commit SHA, and each
                workflow's top-level permissions are read-only.

Exits 1 and lists every finding as path:line: message.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
findings = []


def report(path, line, message):
    findings.append(f"{path}:{line}: {message}")


def tracked_files():
    out = subprocess.run(
        ["git", "ls-files", "-z"], capture_output=True, check=True, cwd=ROOT
    ).stdout
    return [p for p in out.decode().split("\0") if p]


def read_text(path):
    try:
        return (ROOT / path).read_text(encoding="utf-8")
    except (UnicodeDecodeError, FileNotFoundError):
        return None


# --- 1. manifests -----------------------------------------------------------

KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def load_json(path):
    try:
        return json.loads(read_text(path))
    except (TypeError, json.JSONDecodeError) as e:
        report(path, getattr(e, "lineno", 1), f"invalid JSON: {e}")
        return None


def check_manifests(files):
    plugin_manifests = {
        f for f in files if re.fullmatch(r"plugins/[^/]+/\.claude-plugin/plugin\.json", f)
    }
    for f in sorted(plugin_manifests):
        data = load_json(f)
        if not isinstance(data, dict):
            continue
        name = data.get("name")
        if not isinstance(name, str) or not KEBAB.match(name):
            report(f, 1, "plugin.json: 'name' must be a kebab-case string")
        elif name != f.split("/")[1]:
            report(f, 1, f"plugin.json: name '{name}' does not match its directory")

    market = ".claude-plugin/marketplace.json"
    listed = set()
    if market in files:
        data = load_json(market)
        if isinstance(data, dict):
            if not isinstance(data.get("name"), str) or not KEBAB.match(data["name"]):
                report(market, 1, "'name' must be a kebab-case string")
            owner = data.get("owner")
            if not isinstance(owner, dict) or not owner.get("name"):
                report(market, 1, "'owner.name' is required")
            plugins = data.get("plugins")
            if not isinstance(plugins, list) or not plugins:
                report(market, 1, "'plugins' must be a non-empty list")
                plugins = []
            for i, p in enumerate(plugins):
                where = f"plugins[{i}]"
                if not isinstance(p, dict) or not p.get("name") or "source" not in p:
                    report(market, 1, f"{where}: 'name' and 'source' are required")
                    continue
                src = p["source"]
                if isinstance(src, str) and src.startswith("./"):
                    manifest = f"{src[2:].rstrip('/')}/.claude-plugin/plugin.json"
                    listed.add(manifest)
                    if manifest not in files:
                        report(market, 1, f"{where}: no tracked {manifest}")
    for f in sorted(plugin_manifests - listed):
        report(f, 1, "plugin is not listed in .claude-plugin/marketplace.json")

    for f in files:
        if f.endswith(".json") and f != market and f not in plugin_manifests:
            load_json(f)


# --- 2. skills --------------------------------------------------------------

# The keys every Agent Skills surface accepts; others are rejected outside Claude Code.
PORTABLE_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}

def check_skills(files):
    for f in files:
        m = re.fullmatch(r"(?:.*/)?skills/([^/]+)/SKILL\.md", f)
        if not m:
            continue
        text = read_text(f) or ""
        lines = text.split("\n")
        if not lines or lines[0].strip() != "---":
            report(f, 1, "SKILL.md must open with '---' frontmatter")
            continue
        try:
            end = lines.index("---", 1)
        except ValueError:
            report(f, 1, "frontmatter is not closed with '---'")
            continue
        fields, key = {}, None
        for n, line in enumerate(lines[1:end], start=2):
            kv = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
            if kv:
                key = kv.group(1)
                fields[key] = kv.group(2).strip()
            elif line.startswith((" ", "\t")) and key:
                fields[key] = (fields[key] + " " + line.strip()).strip()
            elif line.strip():
                report(f, n, "frontmatter line is not 'key: value'")
        name = fields.get("name", "").strip("'\"")
        if not name:
            report(f, 1, "frontmatter: 'name' is required")
        elif not re.fullmatch(r"[a-z0-9-]{1,64}", name):
            report(f, 1, "frontmatter: 'name' must be lowercase letters, digits, hyphens, at most 64")
        elif name != m.group(1):
            report(f, 1, f"frontmatter: name '{name}' does not match directory '{m.group(1)}'")
        extra = sorted(set(fields) - PORTABLE_KEYS)
        if extra:
            report(f, 1, f"frontmatter keys outside the portable set: {', '.join(extra)}")
        desc = fields.get("description", "").strip("'\">|-").strip()
        if not desc:
            report(f, 1, "frontmatter: 'description' is required")
        elif len(desc) > 1024:
            report(f, 1, "frontmatter: 'description' exceeds 1024 characters")


# --- 3. links ---------------------------------------------------------------

INLINE = re.compile(r"!?\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
REFDEF = re.compile(r"^\s{0,3}\[[^\]]+\]:\s*<?(\S+?)>?(?:\s|$)")
SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


def check_links(files):
    tracked = set(files)
    dirs = {str(Path(f).parent) for f in files}
    for f in files:
        if not f.endswith(".md"):
            continue
        fence = False
        for n, line in enumerate((read_text(f) or "").split("\n"), start=1):
            if line.lstrip().startswith(("```", "~~~")):
                fence = not fence
                continue
            if fence:
                continue
            line = re.sub(r"`[^`]*`", "", line)
            targets = INLINE.findall(line) + REFDEF.findall(line)
            for t in targets:
                if SCHEME.match(t) or t.startswith("#"):
                    continue
                path = t.split("#", 1)[0]
                resolved = (ROOT / f).parent.joinpath(path).resolve()
                try:
                    rel = str(resolved.relative_to(ROOT.resolve()))
                except ValueError:
                    report(f, n, f"link leaves the repository: {t}")
                    continue
                if rel not in tracked and rel not in dirs:
                    report(f, n, f"broken relative link: {t}")


# --- 4. secrets and personal data -----------------------------------------

# Patterns are assembled from parts so that this file does not match itself.
AT = "@"
SECRET_PATTERNS = [
    ("private key", re.compile("-----BEGIN [A-Z ]*PRIV" + "ATE KEY-----")),
    ("GitHub token", re.compile(r"\b(gh[pousr]_[A-Za-z0-9]{30,}|github_" + r"pat_[A-Za-z0-9_]{30,})")),
    ("Anthropic key", re.compile(r"\bsk-" + r"ant-[A-Za-z0-9_-]{20,}")),
    ("API secret key", re.compile(r"\bsk-" + r"(proj-)?[A-Za-z0-9]{32,}")),
    ("AWS access key", re.compile(r"\b(AK" + r"IA|AS" + r"IA)[A-Z0-9]{16}\b")),
    ("Google API key", re.compile(r"\bAI" + r"za[0-9A-Za-z_-]{35}\b")),
    ("Slack token", re.compile(r"\bxo" + r"x[abprs]-[A-Za-z0-9-]{10,}")),
    ("JSON web token", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.")),
    ("credential assignment", re.compile(
        r"(?i)\b(pass" + r"word|passwd|sec" + r"ret|api[_-]?key|tok" + r"en)\b\s*[:=]\s*['\"][^'\"\s]{8,}['\"]")),
    ("local home path", re.compile(r"/(Us" + r"ers|ho" + r"me)/[A-Za-z0-9._-]+/")),
]
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+" + AT + r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
EMAIL_ALLOW = {
    "founders" + AT + "soorma.ai",       # the project contact, in the legal documents
    "noreply" + AT + "anthropic.com",    # the Co-Authored-By trailer convention
}


def check_secrets(files):
    for f in files:
        text = read_text(f)
        if text is None:
            continue
        for n, line in enumerate(text.split("\n"), start=1):
            for label, pattern in SECRET_PATTERNS:
                if pattern.search(line):
                    report(f, n, f"possible {label}")
            for email in EMAIL.findall(line):
                if email.lower() not in EMAIL_ALLOW and not email.lower().endswith(
                    "users.noreply.github.com"
                ):
                    report(f, n, "email address outside the allowlist")


# --- 5. workflows -----------------------------------------------------------

USES = re.compile(r"^\s*(?:-\s*)?uses:\s*([^\s#]+)")


def check_workflows(files):
    for f in files:
        if not re.fullmatch(r"\.github/workflows/[^/]+\.ya?ml", f):
            continue
        lines = (read_text(f) or "").split("\n")
        for n, line in enumerate(lines, start=1):
            m = USES.match(line)
            if m and not m.group(1).startswith("./"):
                if not re.fullmatch(r"[^@\s]+@[0-9a-f]{40}", m.group(1)):
                    report(f, n, f"action not pinned to a full commit SHA: {m.group(1)}")
        top = [i for i, l in enumerate(lines) if l.startswith("permissions:")]
        if not top:
            report(f, 1, "no top-level 'permissions:' block")
            continue
        i = top[0]
        block = [lines[i].split(":", 1)[1].strip()]
        for l in lines[i + 1:]:
            if l.startswith((" ", "\t")):
                block.append(l.strip())
            elif l.strip():
                break
        for entry in filter(None, block):
            if entry.startswith("#"):
                continue
            if entry in ("{}", "read-all") or entry.endswith(": read") or entry.endswith(": none"):
                continue
            report(f, i + 1, f"top-level permission is not read-only: {entry}")


def main():
    files = tracked_files()
    check_manifests(files)
    check_skills(files)
    check_links(files)
    check_secrets(files)
    check_workflows(files)
    if findings:
        print("\n".join(findings))
        print(f"\n{len(findings)} finding(s).")
        return 1
    print(f"Validate: {len(files)} tracked files, no findings.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
