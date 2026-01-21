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
    ) -> dict[str, Any]:
        """Make a GET request."""
        return self._client.request("GET", path, params=params, **options)

    async def _get_async(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        **options: Any,
    ) -> dict[str, Any]:
        """Make an async GET request."""
        return await self._client.request_async(
            "GET", path, params=params, **options
        )

    def _post(
        self,
        path: str,
        json: dict[str, Any] | None = None,
        **options: Any,
    ) -> dict[str, Any]:
        """Make a POST request."""
        return self._client.request("POST", path, json=json, **options)

    async def _post_async(
        self,
        path: str,
        json: dict[str, Any] | None = None,
        **options: Any,
    ) -> dict[str, Any]:
        """Make an async POST request."""
        return await self._client.request_async(
            "POST", path, json=json, **options
        )

    def _put(
        self,
        path: str,
        json: dict[str, Any] | None = None,
        **options: Any,
    ) -> dict[str, Any]:
        """Make a PUT request."""
        return self._client.request("PUT", path, json=json, **options)

    async def _put_async(
        self,
        path: str,
        json: dict[str, Any] | None = None,
        **options: Any,
    ) -> dict[str, Any]:
        """Make an async PUT request."""
        return await self._client.request_async(
            "PUT", path, json=json, **options
        )

    def _delete(
        self,
        path: str,
        **options: Any,
    ) -> dict[str, Any]:
        """Make a DELETE request."""
        return self._client.request("DELETE", path, **options)

    async def _delete_async(
        self,
        path: str,
        **options: Any,
    ) -> dict[str, Any]:
        """Make an async DELETE request."""
        return await self._client.request_async("DELETE", path, **options)
