---
icon: lucide/download
---

# Installation

Get `spotify-sdk` installed and ready to use in your Python project.

## Prerequisites

- Python 3.10 or higher

Python version support follows the [official Python release cycle](https://devguide.python.org/versions/). We support all versions that have not reached end-of-life.


## Install the package

`spotify-sdk` is available on [PyPI](https://pypi.org/project/spotify-sdk/) and can be installed with a Python package installer.

!!! tip "Virtual Environments"
    We recommend installing `spotify-sdk` in a [virtual environment](https://docs.python.org/3/tutorial/venv.html), which isolates project dependencies from system packages and other projects.

=== "uv"

    [uv](https://github.com/astral-sh/uv) is a fast Python package installer that automatically manages virtual environments:

    ```bash
    uv add spotify-sdk
    ```

=== "pip"

    [pip](https://pip.pypa.io/) is the standard Python package installer:

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install spotify-sdk
    ```

## Verify installation

Confirm the package is installed correctly:

```python
import spotify_sdk
print(spotify_sdk.__version__)
```

## Next steps

<div class="grid cards" markdown>

- :octicons-rocket-16: __Quickstart__

    ---

    Learn how to authenticate and make your first API call.

    [:octicons-arrow-right-24: Get started](quickstart.md)

</div>
