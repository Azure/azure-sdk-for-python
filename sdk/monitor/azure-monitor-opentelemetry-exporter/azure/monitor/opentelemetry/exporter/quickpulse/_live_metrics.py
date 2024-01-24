# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.


def enable_live_metrics(connection_string: str) -> None:
    QuickpulseStateManager(connection_string)


class QuickpulseStateManager:

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(QuickpulseStateManager, cls).__new__(cls)
        return cls.instance
    
    def __init__(self, connection_string):
        self._connection_string = connection_string
        # TODO