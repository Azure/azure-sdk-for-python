# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument


from typing import Any, Optional


class DelayMetadata(object):
    def __init__(
        self, *, days: Optional[int] = None, hours: Optional[int] = None, minutes: Optional[int] = None, **kwargs: Any
    ):
        self.days = days
        self.hours = hours
        self.minutes = minutes
