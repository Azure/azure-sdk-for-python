# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint: skip-file
# skipping because of https://github.com/PyCQA/astroid/issues/713
from typing import List, Any
from six import with_metaclass
from enum import Enum
from azure.core.exceptions import HttpResponseError
from azure.core import CaseInsensitiveEnumMeta


class UploadLogsStatus(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    SUCCESS = "Success"
    PARTIAL_FAILURE = "PartialFailure"
    FAILURE = "Failure"

class UploadLogsError:
    """The errors for any failed logs
    """
    def __init__(self, **kwargs) -> None:
        self.failed_logs: List[Any] = kwargs.get("failed_logs", None)
        self.error: HttpResponseError = kwargs.get("error", None)

class UploadLogsResult:
    """The response for upload API.

    :ivar UploadLogsStatus status: Inditcates if the result is a success or a partial failure.
    :ivar list[UploadLogsError] errors: The list of errors and the failed logs.
    """

    def __init__(self, **kwargs):
        self.status: UploadLogsStatus = kwargs.get("status", None)
        self.errors: List[UploadLogsError] = kwargs.get("errors", None)
