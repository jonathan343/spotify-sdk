"""Audiobook service for Spotify API."""

from __future__ import annotations

from ...models import Audiobook, Page, SavedAudiobook, SimplifiedChapter
from .._base_service import BaseService


class AudiobookService(BaseService):
    """Operations for Spotify audiobooks."""

    def get(self, id: str, market: str | None = None) -> Audiobook:
        """Get an audiobook by ID.

        Args:
            id: The Spotify ID for the audiobook.
            market: An ISO 3166-1 alpha-2 country code for availability.

        Returns:
            The requested audiobook.

        Raises:
            ValueError: If id is empty.
        """
        if not id:
            raise ValueError("id cannot be empty")
        params = {"market": market} if market else None
        data = self._get(f"/audiobooks/{id}", params=params)
        return Audiobook.model_validate(data)

    def get_chapters(
        self,
        id: str,
        market: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Page[SimplifiedChapter]:
        """Get an audiobook's chapters.

        Args:
            id: The Spotify ID for the audiobook.
            market: An ISO 3166-1 alpha-2 country code for availability.
            limit: Maximum number of chapters to return (1-50, default 20).
            offset: Index of the first chapter to return.

        Returns:
            Paginated list of chapters.

        Raises:
            ValueError: If id is empty.
        """
        if not id:
            raise ValueError("id cannot be empty")
        params = {"market": market, "limit": limit, "offset": offset}
        data = self._get(f"/audiobooks/{id}/chapters", params=params)
        return Page[SimplifiedChapter].model_validate(data)

    def get_saved(
        self,
        limit: int = 20,
        offset: int = 0,
    ) -> Page[SavedAudiobook]:
        """Get audiobooks saved in the current user's library.

        Args:
            limit: Maximum number of audiobooks to return (1-50, default 20).
            offset: Index of the first audiobook to return.

        Returns:
            Paginated list of saved audiobooks.
        """
        data = self._get(
            "/me/audiobooks", params={"limit": limit, "offset": offset}
        )
        return Page[SavedAudiobook].model_validate(data)
