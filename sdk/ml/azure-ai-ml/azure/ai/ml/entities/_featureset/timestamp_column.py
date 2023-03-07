# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


class TimestampColumn(object):
    def __init__(self, *, name: str, format: str, **kwargs):
        self.name = name
        self.format = format
