# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import logging
import sys
from typing import Callable, List, Any, Awaitable, Optional

from ._operations import LogsIngestionClientOperationsMixin as GeneratedOps
from ..._helpers import _create_gzip_requests

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore  # pylint: disable=ungrouped-imports


_LOGGER = logging.getLogger(__name__)
JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object


class LogsIngestionClientOperationsMixin(GeneratedOps):
    async def upload(  # pylint: disable=arguments-renamed, arguments-differ
        self,
        rule_id: str,
        stream_name: str,
        logs: List[JSON],
        *,
        on_error: Optional[Callable[[Exception, List[JSON]], Awaitable[None]]] = None,
        **kwargs: Any
    ) -> None:
        """Ingestion API used to directly ingest data using Data Collection Rules.

        Logs are divided into chunks of 1MB or less, then each chunk is gzip-compressed and uploaded.

        :param rule_id: The immutable ID of the Data Collection Rule resource.
        :type rule_id: str
        :param stream: The streamDeclaration name as defined in the Data Collection Rule.
        :type stream: str
        :param logs: An array of objects matching the schema defined by the provided stream.
        :type logs: list[JSON]
        :param on_error: The asynchronous callback function that is called when a chunk of logs fails to upload.
            This function should expect two arguments that correspond to the error encountered and
            the list of logs that failed to upload. If no function is provided, then the first exception
            encountered will be raised.
        :type on_error: Optional[Callable[[Exception, List[JSON]], None]]
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        for gzip_data, log_chunk in _create_gzip_requests(logs):
            try:
                await super().upload(
                    rule_id, stream=stream_name, body=gzip_data, content_encoding="gzip", **kwargs
                )
            except Exception as err:  # pylint: disable=broad-except
                if on_error:
                    await on_error(err, log_chunk)
                else:
                    _LOGGER.error( "Failed to upload chunk containing %d log entries", len(log_chunk))
                    raise err


__all__: List[str] = [
    "LogsIngestionClientOperationsMixin"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
