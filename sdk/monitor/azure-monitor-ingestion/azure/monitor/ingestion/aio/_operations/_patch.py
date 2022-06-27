# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Any, Optional
from ._operations import MonitorIngestionClientOperationsMixin as GeneratedOps
from ..._models import SendLogsStatus, SendLogsResult
from ..._helpers import _create_gzip_requests

class MonitorIngestionClientOperationsMixin(GeneratedOps):
    async def upload(self, rule_id: str, stream_name: str, logs: List[Any], *, max_concurrency: Optional[int] = None, **kwargs: Any) -> SendLogsResult:
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
        requests = _create_gzip_requests(logs)
        results = []
        status = SendLogsStatus.SUCCESS
        for ind, request in enumerate(requests):
            response = await super().upload(rule_id, stream=stream_name, body=request, content_encoding='gzip', **kwargs)
            if response is not None:
                results.append(ind)
                status = SendLogsStatus.PARTIAL_FAILURE
        return SendLogsResult(failed_logs_index=results, status=status)

__all__: List[str] = ['MonitorIngestionClientOperationsMixin']  # Add all objects you want publicly available to users at this package level

def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
