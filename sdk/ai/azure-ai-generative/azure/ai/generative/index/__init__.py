# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Index Creation and Operation Functions."""

__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from ._build_mlindex import build_index

__all__ = [
    "build_index",
]
