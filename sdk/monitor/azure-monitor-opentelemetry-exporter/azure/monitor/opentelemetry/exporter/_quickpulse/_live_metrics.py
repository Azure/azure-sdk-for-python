# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.


def enable_live_metrics(connection_string: str) -> None:
    QuickpulseStateManager(connection_string)


class QuickpulseStateManager:

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls._instance = super(QuickpulseStateManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, connection_string):
        self._connection_string = connection_string
        # TODO
