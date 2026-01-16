from pydantic import BaseModel, ConfigDict


class SpotifyModel(BaseModel):
    model_config = ConfigDict(
        extra="allow",
    )
