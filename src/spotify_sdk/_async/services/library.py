"""Library service for Spotify API."""

from __future__ import annotations

from .._base_service import AsyncBaseService


class AsyncLibraryService(AsyncBaseService):
    """Operations for saving, removing, and checking library items."""

    async def save_items(self, uris: list[str]) -> None:
        """Save one or more items to the current user's library.

        Args:
            uris: Spotify URIs to save (max 40).

        Raises:
            ValueError: If uris is empty, contains empty values, or exceeds 40.
        """
        self._validate_uris(uris)
        await self._put("/me/library", params={"uris": ",".join(uris)})

    async def remove_items(self, uris: list[str]) -> None:
        """Remove one or more items from the current user's library.

        Args:
            uris: Spotify URIs to remove (max 40).

        Raises:
            ValueError: If uris is empty, contains empty values, or exceeds 40.
        """
        self._validate_uris(uris)
        await self._delete("/me/library", params={"uris": ",".join(uris)})

    async def check_contains(self, uris: list[str]) -> list[bool]:
        """Check if items are saved in the current user's library.

        Args:
            uris: Spotify URIs to check (max 40).

        Returns:
            A list of booleans aligned to input uris.

        Raises:
            ValueError: If uris is empty, contains empty values, exceeds 40, or
                the response shape is not `list[bool]`.
        """
        self._validate_uris(uris)
        data = await self._get(
            "/me/library/contains",
            params={"uris": ",".join(uris)},
        )
        return self._validate_bool_list_response(
            data,
            endpoint="/me/library/contains",
        )

    def _validate_uris(self, uris: list[str]) -> None:
        if not uris:
            raise ValueError("uris cannot be empty")
        if len(uris) > 40:
            raise ValueError("A maximum of 40 URIs are allowed")
        if any(not uri for uri in uris):
            raise ValueError("uris cannot contain empty values")
