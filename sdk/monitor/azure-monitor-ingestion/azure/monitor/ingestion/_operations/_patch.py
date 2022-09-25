# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import sys
import concurrent.futures
from typing import List, Any, Optional, Union, IO
from ._operations import MonitorIngestionClientOperationsMixin as GeneratedOps
from .._models import UploadLogsStatus, UploadLogsResult, UploadLogsError
from .._helpers import _create_gzip_requests

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore  # pylint: disable=ungrouped-imports

JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object

class MonitorIngestionClientOperationsMixin(GeneratedOps):
    def upload( # pylint: disable=arguments-renamed, arguments-differ
        self,
        rule_id: str,
        stream_name: str,
        logs: Union[List[JSON], IO],
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
        :type logs: list[JSON] or IO
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
                    try:
                        req = future_to_req[future]
                        response = future.result()
                    except Exception as err: # pylint: disable=bare-exception
                        results.append(UploadLogsError(
                            error = err,
                            failed_logs = req
                        ))
        else:
            for request in requests:
                try:
                    response = super().upload(
                        rule_id,
                        stream=stream_name,
                        body=request,
                        content_encoding="gzip",
                        **kwargs
                    )
                except Exception as err: # pylint: disable=bare-exception
                    results.append(UploadLogsError(
                        error = err,
                        failed_logs = request
                    ))

        if not results:
            status = UploadLogsStatus.SUCCESS
        elif 0 < len(results) < len(requests):
            status = UploadLogsStatus.PARTIAL_FAILURE
        else:
            status = UploadLogsStatus.FAILURE
        return UploadLogsResult(errors=results, status=status)

__all__: List[str] = [
    "MonitorIngestionClientOperationsMixin"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
