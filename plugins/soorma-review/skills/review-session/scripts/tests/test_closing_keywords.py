# SPDX-License-Identifier: FSL-1.1-ALv2
import importlib.util
import pathlib
import unittest

_path = pathlib.Path(__file__).resolve().parent.parent / "closing_keywords.py"
_spec = importlib.util.spec_from_file_location("closing_keywords", _path)
ck = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ck)


class ClosingKeywords(unittest.TestCase):
    def hits(self, text):
        return [mode for mode, _ in ck.find(text)]

    def test_negated_keyword_still_closes(self):
        self.assertEqual(self.hits("This PR doesn't close #34."), ["as written, line 1"])

    def test_every_keyword_form(self):
        for word in ("close", "closes", "closed", "fix", "fixes", "fixed",
                     "resolve", "resolves", "resolved", "Resolves", "FIXES"):
            with self.subTest(word=word):
                self.assertTrue(self.hits(f"{word} #7"))

    def test_colon_form(self):
        self.assertTrue(self.hits("Fixes: #9"))

    def test_cross_repository_reference(self):
        self.assertTrue(self.hits("closes soorma-ai/example-repo#5"))

    def test_issue_url(self):
        self.assertTrue(self.hits("resolves https://github.com/owner/repo/issues/12"))

    def test_line_break_is_caught_only_when_joined(self):
        self.assertEqual(self.hits("the amendment that resolves\n#25 is merged"),
                         ["only with line breaks joined"])

    def test_safe_wording_is_clean(self):
        for text in ("For #34, which stays open until the tag exists.",
                     "#34 stays open.",
                     "Closely related to #3.",
                     "prefix#4 and fixture #5",
                     "See the closed issue list."):
            with self.subTest(text=text):
                self.assertEqual(self.hits(text), [])

    def test_main_exit_codes(self):
        import io, sys, tempfile, os
        with tempfile.TemporaryDirectory() as d:
            clean = os.path.join(d, "clean.md")
            dirty = os.path.join(d, "dirty.md")
            open(clean, "w").write("for #1\n")
            open(dirty, "w").write("fixes #1\n")
            out = io.StringIO()
            old, sys.stdout = sys.stdout, out
            try:
                self.assertEqual(ck.main([clean]), 0)
                self.assertEqual(ck.main([dirty]), 1)
            finally:
                sys.stdout = old
            self.assertIn("dirty.md", out.getvalue())


if __name__ == "__main__":
    unittest.main()
