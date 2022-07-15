# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import concurrent.futures
from typing import List, Any, Optional
from ._operations import MonitorIngestionClientOperationsMixin as GeneratedOps
from .._models import UploadLogsStatus, UploadLogsResult
from .._helpers import _create_gzip_requests


class MonitorIngestionClientOperationsMixin(GeneratedOps):
    def upload( # pylint: disable=arguments-renamed, arguments-differ
        self,
        rule_id: str,
        stream_name: str,
        logs: List[Any],
        *,
        max_concurrency: Optional[int] = None,
        **kwargs: Any
    ) -> UploadLogsResult:
        """Ingestion API used to directly ingest data using Data Collection Rules.

        See error response code and error response message for more detail.

        :param rule_id: The immutable Id of the Data Collection Rule resource.
        :type rule_id: str
        :param stream_name: The streamDeclaration name as defined in the Data Collection Rule.
        :type stream_name: str
        :param logs: An array of objects matching the schema defined by the provided stream.
        :type logs: list[any]
        :keyword max_concurrency: Number of parallel threads to use when logs size is > 1mb.
        :paramtype max_concurrency: int
        :return: UploadLogsResult
        :rtype: UploadLogsResult
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        requests = _create_gzip_requests(logs)
        results = []
        status = UploadLogsStatus.SUCCESS
        parallel = max_concurrency and max_concurrency > 1 and len(requests) > 1
        if parallel:
            with concurrent.futures.ThreadPoolExecutor(max_concurrency) as executor:
                future_to_req = {
                    executor.submit(
                        super(MonitorIngestionClientOperationsMixin, self).upload,
                        rule_id,
                        stream=stream_name,
                        body=request,
                        content_encoding="gzip",
                        **kwargs
                    ): request
                    for request in requests
                }
                for future in concurrent.futures.as_completed(future_to_req):
                    req = future_to_req[future]
                    response = future.result()
                    if response is not None:
                        results.append(req)
                        status = UploadLogsStatus.PARTIAL_FAILURE
            return UploadLogsResult(failed_logs=results, status=status)
        for request in requests:
            response = super().upload(
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
