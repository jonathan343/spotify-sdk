"""Episode service for Spotify API."""

from __future__ import annotations

from ...models import Episode, Page, SavedEpisode
from .._base_service import BaseService


class EpisodeService(BaseService):
    """Operations for Spotify episodes."""

    def get(self, id: str, market: str | None = None) -> Episode:
        """Get an episode by ID.

        Args:
            id: The Spotify ID for the episode.
            market: An ISO 3166-1 alpha-2 country code for availability.

        Returns:
            The requested episode.

        Raises:
            ValueError: If id is empty.
        """
        if not id:
            raise ValueError("id cannot be empty")
        params = {"market": market} if market else None
        data = self._get(f"/episodes/{id}", params=params)
        return Episode.model_validate(data)

    def get_saved(
        self,
        limit: int = 20,
        offset: int = 0,
        market: str | None = None,
    ) -> Page[SavedEpisode]:
        """Get episodes saved in the current user's library.

        Args:
            limit: Maximum number of episodes to return (1-50, default 20).
            offset: Index of the first episode to return.
            market: An ISO 3166-1 alpha-2 country code.

        Returns:
            Paginated list of saved episodes.
        """
        params: dict[str, int | str] = {"limit": limit, "offset": offset}
        if market is not None:
            params["market"] = market
        data = self._get("/me/episodes", params=params)
        return Page[SavedEpisode].model_validate(data)
