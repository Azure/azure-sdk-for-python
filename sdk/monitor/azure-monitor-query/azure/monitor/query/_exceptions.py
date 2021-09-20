#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.core.exceptions import ServiceResponseError
from ._models import LogsQueryStatus


class LogsQueryError(object):
    """The code and message for an error.

    All required parameters must be populated in order to send to Azure.

    :ivar code: A machine readable error code.
    :vartype code: str
    :ivar message: A human readable error message.
    :vartype message: str
    :ivar details: error details.
    :vartype details: list[~monitor_query_client.models.ErrorDetail]
    :ivar innererror: Inner error details if they exist.
    :vartype innererror: ~azure.monitor.query.LogsQueryError
    :ivar additional_properties: Additional properties that can be provided on the error info
     object.
    :vartype additional_properties: object
    :ivar bool is_error: Boolean check for error item when iterating over list of
        results. Always True for an instance of a LogsQueryError.
    """

    def __init__(self, **kwargs):
        self.code = kwargs.get("code", None)
        self.message = kwargs.get("message", None)
        self.details = kwargs.get("details", None)
        self.innererror = kwargs.get("innererror", None)
        self.additional_properties = kwargs.get("additional_properties", None)
        self.status = LogsQueryStatus.FAILURE

    @classmethod
    def _from_generated(cls, generated):
        if not generated:
            return None
        details = None
        if generated.details is not None:
            details = [d.serialize() for d in generated.details]
        return cls(
            code=generated.code,
            message=generated.message,
            innererror=cls._from_generated(generated.innererror)
            if generated.innererror
            else None,
            additional_properties=generated.additional_properties,
            details=details,
        )
