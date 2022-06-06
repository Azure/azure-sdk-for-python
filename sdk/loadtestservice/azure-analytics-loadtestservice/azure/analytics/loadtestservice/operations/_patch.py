# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import IO, List
import sys
from msrest import Serializer
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError, ResourceExistsError, ResourceNotFoundError, map_error
from azure.core.pipeline import PipelineResponse
from azure.core.pipeline.transport import HttpResponse
from azure.core.rest import HttpRequest
from azure.core.utils import case_insensitive_dict
from azure.core.paging import ItemPaged
from .._vendor import _format_url_section
from ._operations import TestOperations as TestOperationsGenerated, JSON, ClsType

_SERIALIZER = Serializer()
_SERIALIZER.client_side_validation = False

def build_upload_test_file_request(
        test_id: str,
        file_id: str,
        file_content,
        **kwargs,
    ) -> HttpRequest:
        
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = case_insensitive_dict(kwargs.pop("params", {}) or {})
        api_version = kwargs.pop('api_version', _params.pop('api-version', "2022-06-01-preview"))  # type: str
        accept = _headers.pop('Accept', "application/json")

        # Construct URL
        _url = "/loadtests/{testId}/files/{fileId}"
        path_format_arguments = {
            "testId": _SERIALIZER.url("test_id", test_id, 'str', max_length=50, min_length=2, pattern=r'^[a-z0-9_-]*$'),
            "fileId": _SERIALIZER.url("file_id", file_id, 'str', max_length=50, min_length=2, pattern=r'^[a-z0-9_-]*$'),   
        }

        _url = _format_url_section(_url, **path_format_arguments)

        # Construct parameters
        _params['api-version'] = _SERIALIZER.query("api_version", api_version, 'str')

        # Construct headers
        _headers['Accept'] = _SERIALIZER.header("accept", accept, 'str')

        return HttpRequest(
            method="PUT",
            url=_url,
            files=file_content,
            params=_params,
            headers=_headers,
            **kwargs
        )
            
class TestOperations(TestOperationsGenerated):
    def __init__(self, *args, **kwargs):
        super(TestOperations, self).__init__(*args, **kwargs)
    
    def upload_test_file(
        self,
        test_id,
        file_id,
        file_content,
        **kwargs
    ) -> JSON:
        """
        """

        error_map = {
            401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError
        }
        error_map.update(kwargs.pop('error_map', {}) or {})

        _headers = kwargs.pop("headers", {}) or {}
        _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

        api_version = kwargs.pop('api_version', _params.pop('api-version', "2022-06-01-preview"))  # type: str
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
        request.url = self._client.format_url(request.url)
        request.method = "PUT"
           
        pipeline_response = self._client._pipeline.run( #type: ignore # pylint: disable=protected-access
            request,
            stream=False,
            **kwargs
        )
        response = pipeline_response.http_response
        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if response.status_code not in [202]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        return pipeline_response

__all__: List[str] = ["TestOperations"]  # Add all objects you want publicly available to users at this package level

def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
