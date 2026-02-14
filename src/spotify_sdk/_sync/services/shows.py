"""Show service for Spotify API."""

from __future__ import annotations

from ...models import Page, SavedShow, Show, SimplifiedEpisode
from .._base_service import BaseService


class ShowService(BaseService):
    """Operations for Spotify shows and episodes."""

    def get(self, id: str, market: str | None = None) -> Show:
        """Get a show by ID.

        Args:
            id: The Spotify ID for the show.
            market: An ISO 3166-1 alpha-2 country code for availability.

        Returns:
            The requested show.

        Raises:
            ValueError: If id is empty.
        """
        if not id:
            raise ValueError("id cannot be empty")
        params = {"market": market} if market else None
        data = self._get(f"/shows/{id}", params=params)
        return Show.model_validate(data)

    def get_episodes(
        self,
        id: str,
        market: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Page[SimplifiedEpisode]:
        """Get a show's episodes.

        Args:
            id: The Spotify ID for the show.
            market: An ISO 3166-1 alpha-2 country code for availability.
            limit: Maximum number of episodes to return (1-50, default 20).
            offset: Index of the first episode to return.

        Returns:
            Paginated list of episodes.

        Raises:
            ValueError: If id is empty.
        """
        if not id:
            raise ValueError("id cannot be empty")
        params = {"market": market, "limit": limit, "offset": offset}
        data = self._get(f"/shows/{id}/episodes", params=params)
        return Page[SimplifiedEpisode].model_validate(data)

    def get_saved(self, limit: int = 20, offset: int = 0) -> Page[SavedShow]:
        """Get shows saved in the current user's library.

        Args:
            limit: Maximum number of shows to return (1-50, default 20).
            offset: Index of the first show to return.

        Returns:
            Paginated list of saved shows.
        """
        data = self._get(
            "/me/shows", params={"limit": limit, "offset": offset}
        )
        return Page[SavedShow].model_validate(data)
