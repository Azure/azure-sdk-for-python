# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


from typing import Any


class SearchSpace:
    """SearchSpace class for AutoML verticals."""

    def __init__(self, **kwargs: Any) -> None:
        for k, v in kwargs.items():
            self.__setattr__(k, v)
