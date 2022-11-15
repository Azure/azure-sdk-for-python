# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


class SearchSpace:
    """SearchSpace class for AutoML verticals."""

    def __init__(self, **kwargs) -> None:
        for k in kwargs:
            self.__setattr__(k, kwargs[k])
