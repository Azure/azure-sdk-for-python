# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any


class AttrDict(dict):
    """A dictionary that allows attribute access to its keys."""

    def __getattr__(self, key: str) -> Any:
        return self[key]

    def __setattr__(self, key: str, value: Any) -> None:
        self[key] = value
