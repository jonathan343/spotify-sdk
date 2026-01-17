import json
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def load_fixture():
    """Return a function that loads JSON fixtures by path relative to fixtures dir."""

    def _load(relative_path: str) -> dict:
        fixture_path = FIXTURES_DIR / relative_path
        try:
            raw_text = fixture_path.read_text()
        except OSError as e:
            raise FileNotFoundError(f"Failed to read fixture file '{fixture_path}': {e}") from e

        try:
            return json.loads(raw_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON in fixture file '{fixture_path}': {e}") from e
    return _load
