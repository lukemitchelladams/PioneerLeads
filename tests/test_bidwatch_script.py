"""Runs tests/test_bidwatch.py (a self-checking script, see tests/conftest.py) so `python3 -m pytest -q tests` covers it."""
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from conftest import bidwatch_is_a_script  # noqa: E402


@pytest.mark.skipif(not bidwatch_is_a_script(), reason="test_bidwatch.py is collected by pytest directly")
def test_bidwatch_script_passes():
    r = subprocess.run([sys.executable, str(HERE / "test_bidwatch.py")], cwd=str(HERE.parent), capture_output=True, text=True,
                       timeout=1200)
    tail = "\n".join((r.stdout + r.stderr).strip().splitlines()[-15:])
    assert r.returncode == 0, tail
    assert " 0 failed" in r.stdout, tail
