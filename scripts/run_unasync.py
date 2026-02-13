"""Generate sync code from async source using the unasync library."""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import unasync

ROOT_DIR = Path(__file__).absolute().parent.parent

ADDITIONAL_REPLACEMENTS = {
    "AsyncSpotifyClient": "SpotifyClient",
    "AsyncBaseClient": "BaseClient",
    "AsyncBaseService": "BaseService",
    "AsyncAuthProvider": "AuthProvider",
    "AsyncClientCredentials": "ClientCredentials",
    "AsyncAuthorizationCode": "AuthorizationCode",
    "async_authorize_local": "authorize_local",
    "AsyncAlbumService": "AlbumService",
    "AsyncTrackService": "TrackService",
    "AsyncArtistService": "ArtistService",
    "AsyncPlaylistService": "PlaylistService",
    "AsyncChapterService": "ChapterService",
    "AsyncAudiobookService": "AudiobookService",
    "AsyncLibraryService": "LibraryService",
    "AsyncUserService": "UserService",
    # Override unasync default Async→Sync prefix to get httpx.Client
    # (not httpx.SyncClient).
    "AsyncClient": "Client",
    "anyio.Lock": "threading.Lock",
    "aclose": "close",
    "_async": "_sync",
}

TEST_ADDITIONAL_REPLACEMENTS = {
    **ADDITIONAL_REPLACEMENTS,
    "assert_awaited_once_with": "assert_called_once_with",
}

SOURCE_RULES = [
    {
        "fromdir": "src/spotify_sdk/_async/",
        "todir": "src/spotify_sdk/_sync/",
        "replacements": ADDITIONAL_REPLACEMENTS,
    },
]

TEST_RULES = [
    {
        "fromdir": "tests/_async/",
        "todir": "tests/_sync/",
        "replacements": TEST_ADDITIONAL_REPLACEMENTS,
    },
]

ALL_RULES = SOURCE_RULES + TEST_RULES

# Post-processing patterns applied to every generated file.
POST_PROCESS_PATTERNS = [
    # Remove bare 'import anyio' lines.
    (re.compile(r"^import anyio\n", re.MULTILINE), ""),
    # Replace anyio.sleep with time.sleep.
    (re.compile(r"anyio\.sleep"), "time.sleep"),
    # Replace anyio.Lock with threading.Lock.
    (re.compile(r"anyio\.Lock"), "threading.Lock"),
    # Remove @pytest.mark.anyio decorator lines (and trailing newline).
    (re.compile(r"^\s*@pytest\.mark\.anyio\n", re.MULTILINE), ""),
    # Replace patched anyio.sleep in test decorators.
    (
        re.compile(r"""@patch\(["']anyio\.sleep["']\)"""),
        '@patch("time.sleep")',
    ),
]


def collect_filepaths(source_dir: Path) -> list[str]:
    """Collect all .py and .pyi files under source_dir."""
    filepaths = []
    for root, _, filenames in os.walk(source_dir):
        for filename in filenames:
            if filename.rpartition(".")[-1] in {"py", "pyi"}:
                filepaths.append(os.path.join(root, filename))
    return filepaths


def post_process(output_dir: Path) -> None:
    """Apply regex-based post-processing to all generated files."""
    for root, _, filenames in os.walk(output_dir):
        for filename in filenames:
            if not filename.endswith((".py", ".pyi")):
                continue
            filepath = Path(root) / filename
            content = filepath.read_text()
            for pattern, replacement in POST_PROCESS_PATTERNS:
                content = pattern.sub(replacement, content)
            # Add 'import time' if time.sleep is used but time isn't imported.
            if "time.sleep" in content and "import time" not in content:
                # Insert after the last __future__ or top-level import block.
                content = re.sub(
                    r"(from __future__ import annotations\n)",
                    r"\1\nimport time\n",
                    content,
                )
                if "import time" not in content:
                    content = "import time\n" + content
            if (
                "threading.Lock" in content
                and "import threading" not in content
            ):
                content = re.sub(
                    r"(from __future__ import annotations\n)",
                    r"\1\nimport threading\n",
                    content,
                )
                if "import threading" not in content:
                    content = "import threading\n" + content
            filepath.write_text(content)


def format_output(output_dir: Path) -> None:
    """Run ruff format and fix on the output directory."""
    subprocess.run(
        ["ruff", "check", "--fix", str(output_dir)],
        check=False,
        capture_output=True,
    )
    subprocess.run(
        ["ruff", "format", "--preview", str(output_dir)],
        check=True,
        capture_output=True,
    )


def run(check: bool = False) -> None:
    """Generate sync code from async sources using unasync."""
    for rule_config in ALL_RULES:
        source_dir = ROOT_DIR / rule_config["fromdir"]
        committed_dir = ROOT_DIR / rule_config["todir"]

        if not source_dir.exists():
            print(f"Skipping {source_dir} (does not exist)")
            continue

        if check:
            output_dir = committed_dir.parent / (committed_dir.name + "_check")
        else:
            output_dir = committed_dir

        rule = unasync.Rule(
            fromdir=rule_config["fromdir"],
            todir=str(output_dir.relative_to(ROOT_DIR)) + "/",
            additional_replacements=rule_config["replacements"],
        )

        filepaths = collect_filepaths(source_dir)
        unasync.unasync_files(filepaths, [rule])
        post_process(output_dir)
        format_output(output_dir)

        if check:
            try:
                subprocess.check_call([
                    "diff",
                    "-r",
                    "--exclude=__pycache__",
                    str(committed_dir),
                    str(output_dir),
                ])
            except subprocess.CalledProcessError:
                shutil.rmtree(output_dir)
                print(
                    f"DRIFT DETECTED: {committed_dir} is out of date. "
                    f"Run 'python scripts/run_unasync.py' to regenerate."
                )
                sys.exit(1)
            finally:
                if output_dir.exists():
                    shutil.rmtree(output_dir)

    if check:
        print("Sync check passed: no drift detected.")
    else:
        print("Sync code generated successfully.")


if __name__ == "__main__":
    run(check="--check" in sys.argv)
