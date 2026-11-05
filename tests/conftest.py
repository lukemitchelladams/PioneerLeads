"""pytest setup for tests/.

tests/test_bidwatch.py is a script, not a pytest module: its checks run at import and it ends with sys.exit(), which aborts the
whole `python3 -m pytest -q tests` run ("no tests ran"). While it keeps that shape, pytest skips collecting it and
tests/test_bidwatch_script.py runs it as a subprocess instead, so the canonical command runs both suites. If it is ever turned
into ordinary pytest tests (no module-level sys.exit), pytest collects it directly again.
"""
import re
from pathlib import Path

_BIDWATCH = Path(__file__).with_name("test_bidwatch.py")


def bidwatch_is_a_script():
    try:
        return re.search(r"(?m)^sys\.exit\(", _BIDWATCH.read_text(encoding="utf-8")) is not None
    except OSError:
        return False


collect_ignore = ["test_bidwatch.py"] if bidwatch_is_a_script() else []
