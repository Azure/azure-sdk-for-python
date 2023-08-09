# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument


class DelayMetadata(object):
    def __init__(self, *, days: int = None, hours: int = None, minutes: int = None, **kwargs):
        self.days = days
        self.hours = hours
        self.minutes = minutes
