# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint: skip-file
# skipping because of https://github.com/PyCQA/astroid/issues/713
import sys
from typing import Iterable, List, Any, Tuple
from six import with_metaclass
from enum import Enum
from azure.core.exceptions import HttpResponseError
from azure.core import CaseInsensitiveEnumMeta

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore  # pylint: disable=ungrouped-imports

JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object

class UploadLogsStatus(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    SUCCESS = "Success"
    PARTIAL_FAILURE = "PartialFailure"
    FAILURE = "Failure"

class UploadLogsError:
    """The errors for any failed logs

    :ivar List[JSON] failed_logs: The list of the failed logs.
    :ivar ~azure.core.exceptions.HttpResponseError error: The error with which
     the logs failed.
    """
    def __init__(self, **kwargs) -> None:
        self.failed_logs: List[JSON] = kwargs.get("failed_logs", None)
        self.error: HttpResponseError = kwargs.get("error", None)

class UploadLogsResult:
    """The response for upload API.

    :ivar UploadLogsStatus status: Inditcates if the result is a success or a partial failure.
    :ivar list[UploadLogsError] errors: The list of errors and the failed logs.
    """

    def __init__(self, **kwargs):
        self.status: UploadLogsStatus = kwargs.get("status", None)
        self.errors: List[UploadLogsError] = kwargs.get("errors", None)

    def __iter__(self) -> Iterable[Tuple[HttpResponseError, List[JSON]]]:
        """This will iterate over the errors directly.
        """
        return iter((err.error, err.failed_logs) for err in self.errors)
    
    def __len__(self):
        """This will return the length of the errors"""
        return len(self.errors)
