#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.core.exceptions import HttpResponseError

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
    def __init__(
        self,
        **kwargs
    ):
        self.code = kwargs.get('code', None)
        self.message = kwargs.get('message', None)
        self.details = kwargs.get('details', None)
        self.innererror = kwargs.get('innererror', None)
        self.additional_properties = kwargs.get('additional_properties', None)
        self.is_error = True

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
            innererror=cls._from_generated(generated.innererror) if generated.innererror else None,
            additional_properties=generated.additional_properties,
            details=details,
            is_error=True
        )

class QueryPartialErrorException(HttpResponseError):
    """There is a partial failure in query operation. This is thrown for a single query operation
     when allow_partial_errors is set to False.

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
        error = kwargs.pop('error', None)
        if error:
            self.code = error.code
            self.message = error.message
            self.details = [d.serialize() for d in error.details] if error.details else None
            self.innererror = LogsQueryError._from_generated(error.innererror) if error.innererror else None
            self.additional_properties = error.additional_properties
            self.is_error = True
        super(QueryPartialErrorException, self).__init__(message=self.message)
