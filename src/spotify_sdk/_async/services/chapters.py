"""Chapter service for Spotify API."""

from __future__ import annotations

from ...models import Chapter
from .._base_service import AsyncBaseService


class AsyncChapterService(AsyncBaseService):
    """Operations for Spotify chapters."""

    async def get(self, id: str, market: str | None = None) -> Chapter:
        """Get a chapter by ID.

        Args:
            id: The Spotify ID for the chapter.
            market: An ISO 3166-1 alpha-2 country code for chapter relinking.

        Returns:
            The requested chapter.

        Raises:
            ValueError: If id is empty.
        """
        if not id:
            raise ValueError("id cannot be empty")
        params = {"market": market} if market else None
        data = await self._get(f"/chapters/{id}", params=params)
        return Chapter.model_validate(data)

    async def get_several(
        self,
        ids: list[str],
        market: str | None = None,
    ) -> list[Chapter]:
        """Get multiple chapters by IDs.

        Args:
            ids: List of Spotify chapter IDs. The Spotify API enforces a
                maximum of 50 IDs per request.
            market: An ISO 3166-1 alpha-2 country code for chapter relinking.

        Returns:
            List of chapters.

        Raises:
            ValueError: If ids is empty.
        """
        if not ids:
            raise ValueError("ids cannot be empty")
        params: dict[str, str] = {"ids": ",".join(ids)}
        if market:
            params["market"] = market
        data = await self._get("/chapters", params=params)
        return [Chapter.model_validate(c) for c in data["chapters"]]
