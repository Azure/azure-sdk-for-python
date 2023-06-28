# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=redefined-builtin,disable=unused-argument


class TimestampColumnMetadata(object):
    def __init__(self, *, name: str, format: str = None, **kwargs):
        self.name = name
        self.format = format
