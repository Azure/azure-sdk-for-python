#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from ._models import LogsQueryStatus


class LogsQueryError(object):
    """The code and message for an error.

    :ivar code: A machine readable error code.
    :vartype code: str
    :ivar message: A human readable error message.
    :vartype message: str
    :ivar status: status for error item when iterating over list of
        results. Always "Failure" for an instance of a LogsQueryError.
    :vartype status: ~azure.monitor.query.LogsQueryStatus
    """

    def __init__(self, **kwargs):
        self.code = kwargs.get("code", None)
        self.message = kwargs.get("message", None)
        self.status = LogsQueryStatus.FAILURE

    @classmethod
    def _from_generated(cls, generated):
        if not generated:
            return None

        innererror = generated
        while innererror.innererror is not None:
            innererror = innererror.innererror
        message = innererror.message
        return cls(
            code=generated.code,
            message=message,
        )
