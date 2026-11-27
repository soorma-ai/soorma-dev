# SPDX-License-Identifier: FSL-1.1-ALv2
import importlib.util
import io
import json
import os
import pathlib
import sys
import tempfile
import unittest

_path = pathlib.Path(__file__).resolve().parent.parent / "extract_turns.py"
_spec = importlib.util.spec_from_file_location("extract_turns", _path)
et = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(et)


def rec(kind, content, ts, **extra):
    r = {"type": kind, "timestamp": ts, "cwd": "/work/repo", "gitBranch": "dev",
         "message": {"role": kind, "content": content}}
    r.update(extra)
    return r


FIXTURE = [
    {"type": "attachment", "timestamp": "2026-01-01T00:00:00Z"},
    rec("user", "First instruction: build the thing.", "2026-01-01T00:00:01Z"),
    rec("assistant", [{"type": "thinking", "thinking": "private"},
                      {"type": "text", "text": "Starting."},
                      {"type": "tool_use", "name": "Bash", "input": {"command": "git status"}}],
        "2026-01-01T00:00:02Z"),
    rec("user", [{"type": "tool_result", "content": "clean", "is_error": False}],
        "2026-01-01T00:00:03Z"),
    rec("assistant", [{"type": "text", "text": "subagent chatter"}],
        "2026-01-01T00:00:04Z", isSidechain=True),
    rec("user", "This session is being continued from a previous conversation. Summary...",
        "2026-01-01T00:00:05Z", isCompactSummary=True),
    rec("user", [{"type": "text", "text": "ANCHOR-LINE second instruction"}],
        "2026-01-01T00:00:06Z"),
    rec("assistant", [{"type": "tool_use", "name": "Bash", "input": {"command": "gh pr create"}}],
        "2026-01-01T00:00:07Z"),
    rec("user", [{"type": "tool_result", "content": [{"type": "text", "text": "Permission denied"}],
                  "is_error": True}], "2026-01-01T00:00:08Z"),
    rec("assistant", [{"type": "text", "text": "The PR command was refused; stopping."}],
        "2026-01-01T00:00:09Z"),
]


class ExtractTurns(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "session.jsonl")
        with open(self.path, "w", encoding="utf-8") as f:
            for r in FIXTURE:
                f.write(json.dumps(r) + "\n")
            f.write("not json\n")

    def tearDown(self):
        self.dir.cleanup()

    def run_main(self, *args):
        out, err = io.StringIO(), io.StringIO()
        old = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = out, err
        try:
            code = et.main([self.path, *args])
        finally:
            sys.stdout, sys.stderr = old
        return code, out.getvalue(), err.getvalue()

    def test_default_keeps_text_and_skips_the_rest(self):
        code, out, _ = self.run_main()
        self.assertEqual(code, 0)
        self.assertIn("First instruction", out)
        self.assertIn("Starting.", out)
        self.assertNotIn("private", out)            # thinking
        self.assertNotIn("subagent chatter", out)   # sidechain
        self.assertNotIn("git status", out)         # tools are opt-in
        self.assertNotIn("clean", out)              # results are opt-in
        self.assertIn("COMPACTION SUMMARY", out)
        self.assertNotIn("Summary...", out)

    def test_anchor_starts_at_the_last_matching_human_message(self):
        code, out, _ = self.run_main("--anchor", "ANCHOR-LINE", "--tools", "--results", "100")
        self.assertEqual(code, 0)
        self.assertTrue(out.lstrip().startswith("## USER"))
        self.assertNotIn("First instruction", out)
        self.assertIn("tool: Bash: gh pr create", out)
        self.assertIn("result: ERROR Permission denied", out)

    def test_missing_anchor_exits_2(self):
        code, out, err = self.run_main("--anchor", "nowhere")
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn("anchor not found", err)

    def test_compaction_summary_is_not_a_human_turn(self):
        code, out, _ = self.run_main("--last-turns", "1")
        self.assertIn("ANCHOR-LINE", out)
        self.assertNotIn("First instruction", out)

    def test_since(self):
        code, out, _ = self.run_main("--since", "2026-01-01T00:00:06Z")
        self.assertNotIn("Starting.", out)
        self.assertIn("refused; stopping", out)

    def test_results_are_truncated(self):
        entries = et.digest(self.path, results=4)
        self.assertIn("  - result: clea [...]", [t for _, t in entries])

    def test_full_summaries(self):
        code, out, _ = self.run_main("--full-summaries")
        self.assertIn("Summary...", out)

    def test_list(self):
        out = io.StringIO()
        old, sys.stdout = sys.stdout, out
        try:
            self.assertEqual(et.main(["--list", self.dir.name]), 0)
        finally:
            sys.stdout = old
        self.assertIn("session.jsonl", out.getvalue())
        self.assertIn("cwd=/work/repo branch=dev", out.getvalue())
        self.assertIn("first: First instruction", out.getvalue())


    def test_list_a_projects_root(self):
        root = tempfile.TemporaryDirectory()
        self.addCleanup(root.cleanup)
        for folder, cwd, branch, prompt in (("-work-alpha", "/work/alpha", "dev", "Alpha task"),
                                            ("-work-beta", "/work/beta", "main", "Beta task")):
            os.mkdir(os.path.join(root.name, folder))
            with open(os.path.join(root.name, folder, f"{folder[6:]}.jsonl"), "w") as f:
                r = rec("user", prompt, "2026-01-02T00:00:00Z")
                r.update(cwd=cwd, gitBranch=branch)
                f.write(json.dumps(r) + "\n")
        os.mkdir(os.path.join(root.name, "-work-empty"))
        out = io.StringIO()
        old, sys.stdout = sys.stdout, out
        try:
            self.assertEqual(et.main(["--list", root.name]), 0)
        finally:
            sys.stdout = old
        text = out.getvalue()
        self.assertIn("-work-alpha  alpha.jsonl", text)
        self.assertIn("-work-beta  beta.jsonl", text)
        self.assertIn("cwd=/work/alpha branch=dev", text)
        self.assertIn("cwd=/work/beta branch=main", text)
        self.assertIn("first: Beta task", text)

    def test_list_finds_nothing(self):
        empty = tempfile.TemporaryDirectory()
        self.addCleanup(empty.cleanup)
        os.mkdir(os.path.join(empty.name, "-work-none"))
        for target in (empty.name, os.path.join(empty.name, "missing")):
            with self.subTest(target=target):
                out, err = io.StringIO(), io.StringIO()
                old = sys.stdout, sys.stderr
                sys.stdout, sys.stderr = out, err
                try:
                    code = et.main(["--list", target])
                finally:
                    sys.stdout, sys.stderr = old
                self.assertNotEqual(code, 0)
                self.assertEqual(out.getvalue(), "")
                self.assertTrue(err.getvalue())


    def list_capture(self, target):
        out, err = io.StringIO(), io.StringIO()
        old = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = out, err
        try:
            code = et.main(["--list", target])
        finally:
            sys.stdout, sys.stderr = old
        return code, out.getvalue(), err.getvalue()

    def test_list_reports_what_the_cap_hides(self):
        many = tempfile.TemporaryDirectory()
        self.addCleanup(many.cleanup)
        for i in range(18):
            with open(os.path.join(many.name, f"s{i:02}.jsonl"), "w") as f:
                f.write(json.dumps(rec("user", f"task {i}", "2026-01-03T00:00:00Z")) + "\n")
        code, out, err = self.list_capture(many.name)
        self.assertEqual(code, 0)
        self.assertEqual(out.count(".jsonl\n"), 15)
        self.assertEqual(err.strip(), "(3 more not shown)")

    def test_list_skips_an_unreadable_subfolder(self):
        root = tempfile.TemporaryDirectory()
        self.addCleanup(root.cleanup)
        good = os.path.join(root.name, "-work-good")
        locked = os.path.join(root.name, "-work-locked")
        for folder in (good, locked):
            os.mkdir(folder)
            with open(os.path.join(folder, "s.jsonl"), "w") as f:
                f.write(json.dumps(rec("user", "task", "2026-01-04T00:00:00Z")) + "\n")
        os.chmod(locked, 0)
        self.addCleanup(os.chmod, locked, 0o700)
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            self.skipTest("running as root: chmod 000 doesn't stop reading")
        try:
            os.listdir(locked)
            self.skipTest("chmod 000 had no effect on this file system")
        except PermissionError:
            pass
        code, out, err = self.list_capture(root.name)
        self.assertEqual(code, 0)
        self.assertIn("-work-good  s.jsonl", out)
        self.assertNotIn("-work-locked", out)
        self.assertIn("skipped", err)
        self.assertIn("-work-locked", err)
        self.assertNotIn("Traceback", err)


class SessionById(unittest.TestCase):
    SID = "0a1b2c3d-0000-4000-8000-000000000001"

    def setUp(self):
        self.root = tempfile.TemporaryDirectory()
        self.addCleanup(self.root.cleanup)
        self.folder = os.path.join(self.root.name, "-work-primary")
        os.mkdir(self.folder)
        self.write(self.folder, self.SID, "ANCHOR-LINE handed over")

    def write(self, folder, sid, prompt):
        with open(os.path.join(folder, f"{sid}.jsonl"), "w", encoding="utf-8") as f:
            f.write(json.dumps(rec("user", prompt, "2026-01-05T00:00:00Z")) + "\n")
            f.write(json.dumps(rec("assistant", [{"type": "text", "text": "Done."}],
                                   "2026-01-05T00:00:01Z")) + "\n")

    def run_main(self, *args):
        out, err = io.StringIO(), io.StringIO()
        old = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = out, err
        try:
            code = et.main(list(args))
        finally:
            sys.stdout, sys.stderr = old
        return code, out.getvalue(), err.getvalue()

    def test_session_resolves_and_extracts(self):
        code, out, err = self.run_main("--session", self.SID, "--root", self.root.name,
                                       "--anchor", "ANCHOR-LINE")
        self.assertEqual(code, 0)
        self.assertIn("ANCHOR-LINE handed over", out)
        self.assertIn("Done.", out)

    def test_extraction_reports_the_session_on_stderr(self):
        path = os.path.join(self.folder, f"{self.SID}.jsonl")
        for args in (("--session", self.SID, "--root", self.root.name), (path,)):
            with self.subTest(args=args):
                code, out, err = self.run_main(*args)
                self.assertEqual(code, 0)
                self.assertIn(f"transcript: {path}", err)
                self.assertIn("cwd=/work/repo branch=dev last=2026-01-05T00:00:01", err)
                self.assertNotIn("transcript:", out)

    def test_session_not_found_exits_1(self):
        code, out, err = self.run_main("--session", "missing", "--root", self.root.name)
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("no transcript named missing.jsonl", err)

    def test_session_in_two_folders_is_ambiguous(self):
        other = os.path.join(self.root.name, "-work-secondary")
        os.mkdir(other)
        self.write(other, self.SID, "the same ID elsewhere")
        code, out, err = self.run_main("--session", self.SID, "--root", self.root.name)
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("2 transcripts", err)
        self.assertIn("-work-primary", err)
        self.assertIn("-work-secondary", err)

    def test_session_id_must_be_a_bare_name(self):
        outside = os.path.join(self.root.name, "outside.jsonl")
        self.write(self.root.name, "outside", "must not be read")
        self.assertTrue(os.path.exists(outside))
        # Without the check, "../outside" would resolve from -work-primary to that file.
        for bad in ("../outside", "-work-primary/" + self.SID, ".hidden", ""):
            with self.subTest(bad=bad):
                code, out, err = self.run_main(f"--session={bad}", "--root", self.root.name)
                self.assertEqual(code, 1)
                self.assertEqual(out, "")
                self.assertNotIn("must not be read", out + err)

    def test_session_and_path_together_is_an_error(self):
        path = os.path.join(self.folder, f"{self.SID}.jsonl")
        err = io.StringIO()
        old, sys.stderr = sys.stderr, err
        try:
            with self.assertRaises(SystemExit) as cm:
                et.main([path, "--session", self.SID, "--root", self.root.name])
        finally:
            sys.stderr = old
        self.assertEqual(cm.exception.code, 2)
        self.assertIn("not both", err.getvalue())


if __name__ == "__main__":
    unittest.main()
