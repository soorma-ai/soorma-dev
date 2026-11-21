# SPDX-License-Identifier: FSL-1.1-ALv2
"""wait_for_checks.sh against a fake gh on PATH.

The fake answers the script's three gh calls the way gh would after applying
--jq. The PR head is a full 40-character SHA, while the expected head is given
as the 7-character form people type: the case that once made the script wait
until its timeout with every check finished.
"""

import os
import pathlib
import stat
import subprocess
import tempfile
import textwrap
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "wait_for_checks.sh"
HEAD = "dffaa48c0ffee0123456789abcdef0123456789a"

FAKE_GH = textwrap.dedent('''\
    #!/usr/bin/env python3
    import os, sys
    args = sys.argv[1:]
    jq = args[args.index("--jq") + 1] if "--jq" in args else ""
    head = os.environ["FAKE_HEAD"]
    failed = os.environ.get("FAKE_FAILED", "0")
    if "headRefOid" in args[args.index("--json") + 1]:
        # The summary query: head, total checks, pending checks, as @tsv.
        shown = head[0:12] if ".headRefOid[0:12]" in jq else head
        print(f"{shown}\\t4\\t0")
    elif "length" in jq:
        # The failed-check count.
        print(failed)
    else:
        # The per-check listing.
        for name in ("Validate", "Dependency review", "cla-assistant"):
            print(f"{name}\\tSUCCESS\\tCI\\thttps://example.invalid/{name}")
    ''')


class WaitForChecks(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        gh = pathlib.Path(self.dir.name, "gh")
        gh.write_text(FAKE_GH)
        gh.chmod(gh.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    def tearDown(self):
        self.dir.cleanup()

    def run_script(self, expected, failed="0", timeout=10):
        env = dict(os.environ, PATH=f"{self.dir.name}{os.pathsep}{os.environ['PATH']}",
                   FAKE_HEAD=HEAD, FAKE_FAILED=failed)
        return subprocess.run(
            ["bash", str(SCRIPT), "owner/repo", "1", expected, "60"],
            env=env, capture_output=True, text=True, timeout=timeout)

    def test_short_expected_sha_matches_the_full_head(self):
        try:
            result = self.run_script(HEAD[:7])
        except subprocess.TimeoutExpired:
            self.fail("the script was still waiting after 10 s with every check finished")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"head {HEAD[:12]}: 4 checks finished", result.stdout)

    def test_full_expected_sha_matches(self):
        self.assertEqual(self.run_script(HEAD).returncode, 0)

    def test_a_failed_check_exits_1(self):
        self.assertEqual(self.run_script(HEAD[:7], failed="1").returncode, 1)


if __name__ == "__main__":
    unittest.main()
