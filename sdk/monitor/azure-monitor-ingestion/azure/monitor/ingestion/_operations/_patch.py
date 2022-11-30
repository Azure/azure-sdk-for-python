# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import sys
from typing import List, Any, Union, IO, Iterable, Tuple
from azure.core.exceptions import HttpResponseError
from ._operations import LogsIngestionClientOperationsMixin as GeneratedOps
from .._helpers import _create_gzip_requests

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore  # pylint: disable=ungrouped-imports
JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object


class LogsIngestionClientOperationsMixin(GeneratedOps):
    def upload(  # pylint: disable=arguments-renamed, arguments-differ
        self,
        rule_id: str,
        stream_name: str,
        logs: Union[List[JSON], IO],
        **kwargs: Any
    ) -> Iterable[Tuple[HttpResponseError, List[JSON]]]:
        """Ingestion API used to directly ingest data using Data Collection Rules.

        See error response code and error response message for more detail.

        :param rule_id: The immutable Id of the Data Collection Rule resource.
        :type rule_id: str
        :param stream_name: The streamDeclaration name as defined in the Data Collection Rule.
        :type stream_name: str
        :param logs: An array of objects matching the schema defined by the provided stream.
        :type logs: list[JSON] or IO
        :return: Iterable[Tuple[HttpResponseError, List[JSON]]]
        :rtype: Iterable[Tuple[HttpResponseError, List[JSON]]]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        requests = _create_gzip_requests(logs)
        results = []
        for request in requests:
            try:
                super().upload(
                    rule_id, stream=stream_name, body=request, content_encoding="gzip", **kwargs
                )
            except Exception as err:  # pylint: disable=broad-except
                results.append((err, request))
        return results

__all__: List[str] = [
    "LogsIngestionClientOperationsMixin"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
