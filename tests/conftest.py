"""pytest setup for tests/.

tests/test_bidwatch.py and tests/test_outbox_status.py are scripts, not pytest modules: their checks run at import and they end
with sys.exit(), which aborts the whole `python3 -m pytest -q tests` run ("no tests ran"). While a test file keeps that shape,
pytest skips collecting it and tests/test_bidwatch_script.py runs it as a subprocess instead, so the canonical command runs every
suite. A script turned into ordinary pytest tests (no module-level sys.exit) is collected directly again.
"""
import re
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_BIDWATCH = _HERE / "test_bidwatch.py"


def is_a_script(path):
    try:
        return re.search(r"(?m)^sys\.exit\(", Path(path).read_text(encoding="utf-8")) is not None
    except OSError:
        return False


def script_tests():
    """tests/test_*.py files that are self-checking scripts (module-level sys.exit), sorted."""
    return sorted(p for p in _HERE.glob("test_*.py") if is_a_script(p))


def bidwatch_is_a_script():
    return is_a_script(_BIDWATCH)


collect_ignore = [p.name for p in script_tests()]
