import os

__version__ = "1.8.0"

# Local preview of the “update available” footer:
#   GERMINETTE_DEBUG_REMOTE_VERSION=9.9.9 python3 -m germinette …   # pretend GitHub is newer (any current __version__)
# Or pretend you’re old: GERMINETTE_FORCE_VERSION=1.6.0 (only works if GitHub main is actually newer than 1.6.0).
if os.environ.get("GERMINETTE_FORCE_VERSION"):
    __version__ = os.environ["GERMINETTE_FORCE_VERSION"]
