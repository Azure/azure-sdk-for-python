# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Concrete cursor type; other extension exports retain their dynamic boundary."""

from typing import Any

class ItemFeedCursor:
    def __init__(self) -> None: ...
    @property
    def has_more(self) -> bool: ...
    @property
    def continuation_supported(self) -> bool: ...

def __getattr__(name: str) -> Any: ...
