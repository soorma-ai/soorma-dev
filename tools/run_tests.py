# SPDX-License-Identifier: FSL-1.1-ALv2
"""Run every plugin's bundled unit tests (each scripts/tests/ directory).

    python3 -I tools/run_tests.py
"""

import sys
import unittest
from pathlib import Path


def main():
    dirs = sorted(Path("plugins").glob("*/skills/*/scripts/tests"))
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for d in dirs:
        suite.addTests(loader.discover(str(d), pattern="test_*.py", top_level_dir=str(d)))
    print(f"Test directories: {', '.join(map(str, dirs)) or 'none'}")
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
