from spotify_sdk.models.artist import Artist
from spotify_sdk.models.common import ExternalUrls, Followers, Image


def test_artist_from_json_payload(load_fixture):
    """Test that Artist model correctly parses a full artist JSON response."""
    payload = load_fixture("artists/kendrick_lamar.json")

    artist = Artist(**payload)

    assert artist.id == "2YZyLoL8N0Wb9xBt1NhZWg"
    assert artist.name == "Kendrick Lamar"
    assert artist.type_ == "artist"
    assert artist.uri == "spotify:artist:2YZyLoL8N0Wb9xBt1NhZWg"
    assert (
        artist.href
        == "https://api.spotify.com/v1/artists/2YZyLoL8N0Wb9xBt1NhZWg"
    )
    assert artist.popularity == 91
    assert artist.genres == ["hip hop", "west coast hip hop"]
    assert artist.external_urls == ExternalUrls(
        spotify="https://open.spotify.com/artist/2YZyLoL8N0Wb9xBt1NhZWg"
    )
    assert artist.followers == Followers(href=None, total=45978576)
    assert len(artist.images) == 3
    assert artist.images[0] == Image(
        url="https://i.scdn.co/image/ab6761610000e5eb39ba6dcd4355c03de0b50918",
        height=640,
        width=640,
    )
