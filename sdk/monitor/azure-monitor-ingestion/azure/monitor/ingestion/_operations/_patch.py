# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Any
from enum import Enum
from ._operations import MonitorIngestionClientOperationsMixin as GeneratedOps

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

class MonitorIngestionClientOperationsMixin(GeneratedOps):
    def send_logs(self, rule_id: str, stream: str, body: List[Any], *, max_concurrency: int = None, **kwargs: Any) -> SendLogsResult:
        """Ingestion API used to directly ingest data using Data Collection Rules.

        See error response code and error response message for more detail.

        :param rule_id: The immutable Id of the Data Collection Rule resource.
        :type rule_id: str
        :param stream: The streamDeclaration name as defined in the Data Collection Rule.
        :type stream: str
        :param body: An array of objects matching the schema defined by the provided stream.
        :type body: list[any]
        :keyword max_concurrency: Number of parallel threads to use when logs size is > 1mb.
        :paramtype max_concurrency: int
        :return: SendLogsResult
        :rtype: SendLogsResult
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        response = super().send_logs(rule_id, stream, body, **kwargs)
        return response

__all__: List[str] = ["MonitorIngestionClientOperationsMixin", "SendLogsResult", "SendLogsStatus"]  # Add all objects you want publicly available to users at this package level

def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
