#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Any

from ._models import LogsQueryStatus



class LogsQueryError(object):
    """The code and message for an error.

    :ivar code: A machine readable error code.
    :vartype code: str
    :ivar message: A human readable error message.
    :vartype message: str
    :ivar details: A list of additional details about the error.
    :vartype details: list[JSON]
    :ivar status: status for error item when iterating over list of
        results. Always "Failure" for an instance of a LogsQueryError.
    :vartype status: ~azure.monitor.query.LogsQueryStatus
    """

    def __init__(self, **kwargs: Any) -> None:
        self.code = kwargs.get("code", None)
        self.message = kwargs.get("message", None)
        self.details = kwargs.get("details", None)
        self.status = LogsQueryStatus.FAILURE

    def __str__(self):
        return str(self.__dict__)

    @classmethod
    def _from_generated(cls, generated):
        if not generated:
            return None
        innererror = generated
        while innererror.get("innererror"):
            innererror = innererror["innererror"]
        message = innererror.get("message")
        return cls(
            code=generated.get("code"),
            message=message,
            details=generated.get("details"),
        )
