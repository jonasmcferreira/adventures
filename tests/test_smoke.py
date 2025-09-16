from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from novelgen import __version__  # noqa: E402  (import after path tweak)


def test_version_string() -> None:
    assert isinstance(__version__, str)
    assert __version__
