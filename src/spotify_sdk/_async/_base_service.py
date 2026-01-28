"""Base service class for API resources."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ._base_client import AsyncBaseClient


class AsyncBaseService:
    """Base class for API resource services."""

    def __init__(self, client: AsyncBaseClient) -> None:
        self._client = client

    async def _get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        **options: Any,
    ) -> dict[str, Any]:
        """Make a GET request."""
        return await self._client.request(
            "GET", path, params=params, **options
        )

    async def _post(
        self,
        path: str,
        json: dict[str, Any] | None = None,
        **options: Any,
    ) -> dict[str, Any]:
        """Make a POST request."""
        return await self._client.request("POST", path, json=json, **options)

    async def _put(
        self,
        path: str,
        json: dict[str, Any] | None = None,
        **options: Any,
    ) -> dict[str, Any]:
        """Make a PUT request."""
        return await self._client.request("PUT", path, json=json, **options)

    async def _delete(
        self,
        path: str,
        **options: Any,
    ) -> dict[str, Any]:
        """Make a DELETE request."""
        return await self._client.request("DELETE", path, **options)
