# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


class DelayMetadata(object):
    def __init__(self, *, days: int, hours: int, minutes: int, **kwargs):  # pylint: disable=unused-argument
        self.Days = days
        self.Hours = hours
        self.Minutes = minutes
