# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=redefined-builtin,disable=unused-argument

from .timestamp_column_metadata import TimestampColumnMetadata
from .delay_metadata import DelayMetadata


class SourceMetadata(object):
    def __init__(
        self, *, type: str, path: str, timestamp_column: TimestampColumnMetadata, source_delay: DelayMetadata, **kwargs
    ):
        self.type = type
        self.path = path
        self.timestamp_column = timestamp_column
        self.source_delay = source_delay
