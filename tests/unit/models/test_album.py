from spotify_sdk.models import Album, SimplifiedTrack
from spotify_sdk.models.artist import SimplifiedArtist
from spotify_sdk.models.common import (
    Copyright,
    ExternalIds,
    ExternalUrls,
    Image,
    Page,
)


def test_album_from_json_payload(load_fixture):
    """Test that Album model correctly parses a full album JSON response."""
    payload = load_fixture("albums/tpab.json")

    album = Album(**payload)

    # Basic album fields
    assert album.id == "7ycBtnsMtyVbbwTfJwRjSP"
    assert album.name == "To Pimp A Butterfly"
    assert album.type_ == "album"
    assert album.uri == "spotify:album:7ycBtnsMtyVbbwTfJwRjSP"
    assert (
        album.href
        == "https://api.spotify.com/v1/albums/7ycBtnsMtyVbbwTfJwRjSP"
    )

    # Album metadata
    assert album.album_type == "album"
    assert album.total_tracks == 16
    assert album.release_date == "2015-03-16"
    assert album.release_date_precision == "day"
    assert album.label == "Aftermath"
    assert album.popularity == 79

    # External URLs
    assert album.external_urls == ExternalUrls(
        spotify="https://open.spotify.com/album/7ycBtnsMtyVbbwTfJwRjSP"
    )

    # External IDs
    assert album.external_ids == ExternalIds(
        upc="00602547289049", isrc=None, ean=None
    )

    # Available markets
    assert "US" in album.available_markets
    assert len(album.available_markets) > 0


def test_album_artists(load_fixture):
    """Test that Album correctly parses nested artist objects."""
    payload = load_fixture("albums/tpab.json")

    album = Album(**payload)

    assert len(album.artists) == 1
    assert all(isinstance(a, SimplifiedArtist) for a in album.artists)

    assert album.artists[0].name == "Kendrick Lamar"
    assert album.artists[0].id == "2YZyLoL8N0Wb9xBt1NhZWg"
    assert album.artists[0].type_ == "artist"


def test_album_images(load_fixture):
    """Test that Album correctly parses image objects."""
    payload = load_fixture("albums/tpab.json")

    album = Album(**payload)

    assert len(album.images) == 3
    assert all(isinstance(img, Image) for img in album.images)

    # Images are typically ordered by size (largest first)
    assert album.images[0].width == 640
    assert album.images[0].height == 640
    assert album.images[0].url.startswith("https://i.scdn.co/image/")


def test_album_copyrights(load_fixture):
    """Test that Album correctly parses copyright objects."""
    payload = load_fixture("albums/tpab.json")

    album = Album(**payload)

    assert len(album.copyrights) == 2
    assert all(isinstance(c, Copyright) for c in album.copyrights)

    # Copyright (C) and Performance (P) rights
    types = [c.type_ for c in album.copyrights]
    assert "C" in types
    assert "P" in types


def test_album_tracks(load_fixture):
    """Test that Album correctly parses paginated tracks."""
    payload = load_fixture("albums/tpab.json")

    album = Album(**payload)

    # Tracks is a Page object, not a list
    assert isinstance(album.tracks, Page)
    assert album.tracks.total == 16
    assert len(album.tracks.items) > 0

    # Each item is a SimplifiedTrack
    assert all(isinstance(t, SimplifiedTrack) for t in album.tracks.items)

    # First track
    first_track = album.tracks.items[0]
    assert first_track.name == "Wesley's Theory"
    assert first_track.track_number == 1
    assert first_track.disc_number == 1


def test_album_optional_fields(load_fixture):
    """Test that optional fields default to None when not present."""
    payload = load_fixture("albums/tpab.json")

    album = Album(**payload)

    # Restrictions only present when content is restricted
    assert album.restrictions is None
