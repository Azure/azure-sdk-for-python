# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=redefined-builtin,disable=unused-argument


from typing import Any, Optional


class TimestampColumnMetadata(object):
    def __init__(self, *, name: str, format: Optional[str] = None, **kwargs: Any):
        self.name = name
        self.format = format
