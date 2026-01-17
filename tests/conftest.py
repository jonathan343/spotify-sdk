import json
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def load_fixture():
    """Return a function that loads JSON fixtures by path relative to fixtures dir."""

    def _load(relative_path: str) -> dict:
        fixture_path = FIXTURES_DIR / relative_path
        return json.loads(fixture_path.read_text())

    return _load
