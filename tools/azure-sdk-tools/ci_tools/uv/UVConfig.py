import os

class UVConfig:
    """
    Static configuration for UV checks.
    This class holds the static configuration values used in UV checks.
    """

    # The path to the UV checks configuration file
    REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
