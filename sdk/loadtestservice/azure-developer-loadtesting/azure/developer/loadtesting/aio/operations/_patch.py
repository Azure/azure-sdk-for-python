# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import cast, List, BinaryIO

from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    map_error,
)
from azure.core.utils import case_insensitive_dict

from ._operations import LoadTestRunOperations as LoadTestRunOperationsGenerated, JSON, ClsType
from ...operations._patch import build_upload_test_file_request


class LoadTestRunOperations(LoadTestRunOperationsGenerated):
    """
    for performing the operations on test
    """

    def __init__(self, *args, **kwargs):
        super(LoadTestRunOperations, self).__init__(*args, **kwargs)

    async def upload_test_file(self, test_id: str, file_id: str, file: BinaryIO, **kwargs) -> JSON:
        """Upload test file and link it to a test.

        Upload a test file to an existing test.

        :param test_id: Unique id for the test
        :type test_id: str
        :param file_id: Unique id for the file
        :type file_id: str
        :param file_content: dictionary containing file contet
        :type file: BinaryIO (file opened in Binary read mode)
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        error_map = {401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError}
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        cls = kwargs.pop("cls", None)  # type: ClsType[JSON]

        _content = file

        request = build_upload_test_file_request(
            test_id=test_id,
            file_id=file_id,
            file=file,
            api_version=self._config.api_version,
            headers=_headers,
            params=_params,
        )

        path_format_arguments = {
            "Endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }
        request.url = self._client.format_url(request.url, **path_format_arguments)  # type: ignore

        request.method = "PUT"

        pipeline_response = await self._client._pipeline.run(  # type: ignore # pylint: disable=protected-access
            request, stream=False, **kwargs
        )
        response = pipeline_response.http_response

        if response.status_code not in [201]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)
        if response.content:
            deserialized = response.json()
        else:
            deserialized = None
        if cls:
            return cls(pipeline_response, cast(JSON, deserialized), {})
        return cast(JSON, deserialized)


__all__: List[str] = ["LoadTestRunOperations"]


# Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
