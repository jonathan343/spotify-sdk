from spotify_sdk.models import SimplifiedAlbum, Track
from spotify_sdk.models.artist import SimplifiedArtist
from spotify_sdk.models.common import ExternalIds, ExternalUrls


def test_track_from_json_payload(load_fixture):
    """Test that Track model correctly parses a full track JSON response."""
    payload = load_fixture("tracks/wesleys_theory.json")

    track = Track(**payload)

    # Basic track fields
    assert track.id == "7Ks4VCY1wFebnOdJrM13t6"
    assert track.name == "Wesley's Theory"
    assert track.type_ == "track"
    assert track.uri == "spotify:track:7Ks4VCY1wFebnOdJrM13t6"
    assert (
        track.href
        == "https://api.spotify.com/v1/tracks/7Ks4VCY1wFebnOdJrM13t6"
    )

    # Track metadata
    assert track.duration_ms == 287360
    assert track.explicit is True
    assert track.popularity == 70
    assert track.track_number == 1
    assert track.disc_number == 1
    assert track.is_local is False
    assert track.preview_url is None

    # External URLs
    assert track.external_urls == ExternalUrls(
        spotify="https://open.spotify.com/track/7Ks4VCY1wFebnOdJrM13t6"
    )

    # External IDs
    assert track.external_ids == ExternalIds(
        isrc="USUM71502491", ean=None, upc=None
    )

    # Available markets
    assert "US" in track.available_markets
    assert len(track.available_markets) > 0


def test_track_artists(load_fixture):
    """Test that Track correctly parses nested artist objects."""
    payload = load_fixture("tracks/wesleys_theory.json")

    track = Track(**payload)

    assert len(track.artists) == 3
    assert all(isinstance(a, SimplifiedArtist) for a in track.artists)

    # First artist
    assert track.artists[0].name == "Kendrick Lamar"
    assert track.artists[0].id == "2YZyLoL8N0Wb9xBt1NhZWg"
    assert track.artists[0].type_ == "artist"

    # Featured artists
    assert track.artists[1].name == "George Clinton"
    assert track.artists[2].name == "Thundercat"


def test_track_album(load_fixture):
    """Test that Track correctly parses nested album object."""
    payload = load_fixture("tracks/wesleys_theory.json")

    track = Track(**payload)

    assert isinstance(track.album, SimplifiedAlbum)
    assert track.album.id == "7ycBtnsMtyVbbwTfJwRjSP"
    assert track.album.name == "To Pimp A Butterfly"
    assert track.album.album_type == "album"
    assert track.album.release_date == "2015-03-16"
    assert track.album.release_date_precision == "day"
    assert track.album.total_tracks == 16
    assert len(track.album.images) == 3
    assert len(track.album.artists) == 1
    assert track.album.artists[0].name == "Kendrick Lamar"


def test_track_optional_fields(load_fixture):
    """Test that optional fields default to None when not present."""
    payload = load_fixture("tracks/wesleys_theory.json")

    track = Track(**payload)

    # These fields are only present during track relinking
    assert track.is_playable is None
    assert track.linked_from is None
    assert track.restrictions is None
