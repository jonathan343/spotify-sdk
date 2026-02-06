"""Tests for file token cache."""

from __future__ import annotations

import json

from spotify_sdk._sync.auth import FileTokenCache, TokenInfo


class TestFileTokenCache:
    def test_missing_file_returns_none(self, tmp_path):
        cache_path = tmp_path / "missing-token.json"
        cache = FileTokenCache(path=str(cache_path))
        assert cache.get() is None

    def test_set_and_get_roundtrip(self, tmp_path):
        cache_path = tmp_path / "auth" / "token.json"
        cache = FileTokenCache(path=str(cache_path))
        token = TokenInfo(
            access_token="access-token",
            expires_at=1_700_000_000.0,
            refresh_token="refresh-token",
            scope="user-read-private",
        )

        cache.set(token)
        loaded = cache.get()

        assert loaded == token

    def test_invalid_json_returns_none(self, tmp_path):
        cache_path = tmp_path / "invalid.json"
        cache_path.write_text("{not-json", encoding="utf-8")
        cache = FileTokenCache(path=str(cache_path))
        assert cache.get() is None

    def test_invalid_payload_returns_none(self, tmp_path):
        cache_path = tmp_path / "invalid-payload.json"
        cache_path.write_text(
            json.dumps({"access_token": "token-only"}),
            encoding="utf-8",
        )
        cache = FileTokenCache(path=str(cache_path))
        assert cache.get() is None

    def test_invalid_optional_fields_are_ignored(self, tmp_path):
        cache_path = tmp_path / "optional-fields.json"
        cache_path.write_text(
            json.dumps({
                "access_token": "token",
                "expires_at": 123.0,
                "refresh_token": 1,
                "scope": ["playlist-read-private"],
            }),
            encoding="utf-8",
        )
        cache = FileTokenCache(path=str(cache_path))
        loaded = cache.get()

        assert loaded is not None
        assert loaded.access_token == "token"
        assert loaded.refresh_token is None
        assert loaded.scope is None
