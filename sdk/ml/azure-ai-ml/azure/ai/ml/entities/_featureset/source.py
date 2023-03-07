# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


from .timestamp_column import TimestampColumn
from .delay import Delay


class Source(object):
    def __init__(self, *, type: str, path: str, timestamp_column: TimestampColumn, source_delay: Delay, **kwargs):
        self.type = type
        self.path = path
        self.timestamp_column = timestamp_column
        self.source_delay = source_delay
