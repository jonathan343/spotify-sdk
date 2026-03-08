"""Chapter service for Spotify API."""

from __future__ import annotations

from ...models import Chapter
from .._base_service import BaseService


class ChapterService(BaseService):
    """Operations for Spotify chapters."""

    def get(self, id: str, market: str | None = None) -> Chapter:
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
        data = self._get(f"/chapters/{id}", params=params)
        return Chapter.model_validate(data)
