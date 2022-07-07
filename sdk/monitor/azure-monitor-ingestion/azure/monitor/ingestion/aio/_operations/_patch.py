# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Any
from ._operations import MonitorIngestionClientOperationsMixin as GeneratedOps
from ..._models import UploadLogsStatus, UploadLogsResult
from ..._helpers import _create_gzip_requests


class MonitorIngestionClientOperationsMixin(GeneratedOps):
    async def upload( # pylint: disable=arguments-renamed, arguments-differ
        self, rule_id: str, stream_name: str, logs: List[Any], **kwargs: Any
    ) -> UploadLogsResult:
        """Ingestion API used to directly ingest data using Data Collection Rules.

        See error response code and error response message for more detail.

        :param rule_id: The immutable Id of the Data Collection Rule resource.
        :type rule_id: str
        :param stream: The streamDeclaration name as defined in the Data Collection Rule.
        :type stream: str
        :param body: An array of objects matching the schema defined by the provided stream.
        :type body: list[any]
        :return: UploadLogsResult
        :rtype: UploadLogsResult
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        requests = _create_gzip_requests(logs)
        results = []
        status = UploadLogsStatus.SUCCESS
        for request in requests:
            response = await super().upload(
                rule_id,
                stream=stream_name,
                body=request,
                content_encoding="gzip",
                **kwargs
            )
            if response is not None:
                results.append(request)
                status = UploadLogsStatus.PARTIAL_FAILURE
        return UploadLogsResult(failed_logs=results, status=status)


__all__: List[str] = [
    "MonitorIngestionClientOperationsMixin"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
