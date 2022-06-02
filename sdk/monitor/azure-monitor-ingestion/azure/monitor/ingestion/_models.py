# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import List
from enum import Enum

class SendLogsStatus(str, Enum):
    SUCCESS = 'Success'
    PARTIAL_FAILURE = 'PartialFailure'

class SendLogsResult():
    """The response for send_logs API.

    :ivar SendLogsStatus status: Inditcates if the result is a success or a partial failure.
    :ivar list failed_logs_index: If there is a failure, returns the index of the request.
    """
    def __init__(self, **kwargs):
        self.status: SendLogsStatus = kwargs.get("status", None)
        self.failed_logs_index: List[int] = kwargs.get('failed_logs_index', None)
