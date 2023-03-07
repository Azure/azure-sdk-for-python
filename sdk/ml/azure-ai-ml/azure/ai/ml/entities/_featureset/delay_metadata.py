# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


class DelayMetadata(object):
    def __init__(self, *, days: int, hours: int, minutes: int, **kwargs):
        self.days = days
        self.hours = hours
        self.minutes = minutes
