"""Base service class for API resources."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ._base_client import BaseClient


class BaseService:
    """Base class for API resource services."""

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    def _get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        **options: Any,
    ) -> Any:
        """Make a GET request."""
        return self._client.request("GET", path, params=params, **options)

    def _post(
        self,
        path: str,
        json: dict[str, Any] | None = None,
        **options: Any,
    ) -> Any:
        """Make a POST request."""
        return self._client.request("POST", path, json=json, **options)

    def _put(
        self,
        path: str,
        json: dict[str, Any] | None = None,
        **options: Any,
    ) -> Any:
        """Make a PUT request."""
        return self._client.request("PUT", path, json=json, **options)

    def _delete(
        self,
        path: str,
        **options: Any,
    ) -> Any:
        """Make a DELETE request."""
        return self._client.request("DELETE", path, **options)
