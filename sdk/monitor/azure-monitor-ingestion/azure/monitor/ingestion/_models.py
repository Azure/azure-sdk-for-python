# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint: skip-file
# skipping because of https://github.com/PyCQA/astroid/issues/713
from typing import List, Any
from six import with_metaclass
from enum import Enum
from azure.core import CaseInsensitiveEnumMeta


class UploadLogsStatus(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    SUCCESS = "Success"
    PARTIAL_FAILURE = "PartialFailure"


class UploadLogsResult:
    """The response for send_logs API.

    :ivar UploadLogsStatus status: Inditcates if the result is a success or a partial failure.
    :ivar list failed_logs: If there is a failure, returns the request.
    """

    def __init__(self, **kwargs):
        self.status: UploadLogsStatus = kwargs.get("status", None)
        self.failed_logs: List[Any] = kwargs.get("failed_logs", None)
