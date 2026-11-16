"""Runs each self-checking test script (tests/test_bidwatch.py, tests/test_outbox_status.py; see tests/conftest.py) so
`python3 -m pytest -q tests` covers them."""
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from conftest import script_tests  # noqa: E402

SCRIPTS = script_tests()


@pytest.mark.skipif(not SCRIPTS, reason="every test file is collected by pytest directly")
@pytest.mark.parametrize("script", SCRIPTS, ids=[p.name for p in SCRIPTS])
def test_script_passes(script):
    r = subprocess.run([sys.executable, str(script)], cwd=str(HERE.parent), capture_output=True, text=True, timeout=1200)
    tail = "\n".join((r.stdout + r.stderr).strip().splitlines()[-15:])
    assert r.returncode == 0, tail
    assert " 0 failed" in r.stdout, tail
