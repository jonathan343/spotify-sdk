"""Base model configuration."""

from pydantic import BaseModel, ConfigDict


class SpotifyModel(BaseModel):
    """Base model for all Spotify API objects. Allows extra fields for forward compatibility."""

    model_config = ConfigDict(
        extra="allow",
    )
