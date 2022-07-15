# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import List, cast
from msrest import Serializer
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError, ResourceExistsError, ResourceNotFoundError, map_error
from azure.core.rest import HttpRequest
from azure.core.utils import case_insensitive_dict
from ._operations import TestOperations as TestOperationsGenerated, JSON, ClsType
from ...operations._patch import build_upload_test_file_request

_SERIALIZER = Serializer()
_SERIALIZER.client_side_validation = False

class TestOperations(TestOperationsGenerated):
    """
    for performing the operations on test
    """
    def __init__(self, *args, **kwargs):
        super(TestOperations, self).__init__(*args, **kwargs)

    async def upload_test_file(
        self,
        test_id,
        file_id,
        file_content,
        **kwargs
    ) -> JSON:
        """
        Uploading a test file
        """

        error_map = {
            401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError
        }
        error_map.update(kwargs.pop('error_map', {}) or {})

        _headers = kwargs.pop("headers", {}) or {}
        _params = case_insensitive_dict(kwargs.pop("params", {}) or {})
        api_version = kwargs.pop('api_version', _params.pop('api-version', "2022-06-01-preview"))
        cls = kwargs.pop('cls', None)  # type: ClsType[JSON]

        _content=file_content

        request = build_upload_test_file_request(
            test_id,
            file_id,
            _content,
            api_version=api_version,
            headers=_headers,
            params=_params,
        )
        
        path_format_arguments = {
            "Endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }
        request.url = self._client.format_url(request.url, **path_format_arguments)

        request.method = "PUT"

        pipeline_response = self._client._pipeline.run( #type: ignore # pylint: disable=protected-access
            request,
            stream=False,
            **kwargs
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

__all__: List[str] = ["TestOperations"]
# Add all objects you want publicly available to users at this package level

def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
