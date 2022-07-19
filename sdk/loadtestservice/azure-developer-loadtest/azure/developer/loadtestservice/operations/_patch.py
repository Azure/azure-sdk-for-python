# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import List, cast, Optional, Any
from .._serialization import Serializer
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    map_error,
)
from azure.core.rest import HttpRequest
from azure.core.utils import case_insensitive_dict
from .._vendor import _format_url_section
from ._operations import TestOperations as TestOperationsGenerated, JSON, ClsType
from ._operations import AppComponentOperations as AppComponentOperationsGenerated

_SERIALIZER = Serializer()
_SERIALIZER.client_side_validation = False

def build_upload_test_file_request(
    test_id: str,
    file_id: str,
    file_content,
    **kwargs,
) -> HttpRequest:
    """
    Core logic for uploading a file
    """
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
    _params = case_insensitive_dict(kwargs.pop("params", {}) or {})
    api_version = kwargs.pop("api_version", _params.pop("api-version", "2022-06-01-preview"))
    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/loadtests/{testId}/files/{fileId}"
    path_format_arguments = {
        "testId": _SERIALIZER.url("test_id", test_id, "str", max_length=50, min_length=2, pattern=r"^[a-z0-9_-]*$"),
        "fileId": _SERIALIZER.url("file_id", file_id, "str", max_length=50, min_length=2, pattern=r"^[a-z0-9_-]*$"),
    }

    _url = _format_url_section(_url, **path_format_arguments)

    # Construct parameters
    _params["api-version"] = _SERIALIZER.query("api_version", api_version, "str")

    # Construct headers
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="PUT", url=_url, files=file_content, params=_params, headers=_headers, **kwargs)


class TestOperations(TestOperationsGenerated):
    """
    for performing the operations on test
    """

    def __init__(self, *args, **kwargs):
        super(TestOperations, self).__init__(*args, **kwargs)

    def upload_test_file(self, test_id: str, file_id: str, file_content: JSON, **kwargs) -> JSON:
        """
        Uploading a test file
        """

        error_map = {401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError}
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = kwargs.pop("headers", {}) or {}
        _params = case_insensitive_dict(kwargs.pop("params", {}) or {})
        api_version = kwargs.pop("api_version", _params.pop("api-version", "2022-06-01-preview"))
        cls = kwargs.pop("cls", None)  # type: ClsType[JSON]

        _content = file_content

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
        request.url = self._client.format_url(request.url, **path_format_arguments)  # type: ignore

        request.method = "PUT"

        pipeline_response = self._client._pipeline.run(  # type: ignore # pylint: disable=protected-access
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


class AppComponentOperations(AppComponentOperationsGenerated):

    __excludes__ = ["get_by_name", "get_app_component"]

    def get_app_components(
        self,
        *,
        test_run_id: Optional[str] = None,
        test_id: Optional[str] = None,
        name: Optional[str] = None,
        **kwargs: Any,
    ) -> JSON:
        """Get App Components for a test or a test run by its name.

        Get App Components for a test or a test run by its name.

        :keyword test_run_id: [Required, if testId is not provided] Test run Id. Default value is None.
        :paramtype test_run_id: st
        :keyword test_id: Unique name for load test, must be a valid URL character ^[a-z0-9_-]*$.
         Default value is None.
        :paramtype test_id: str
        :keyword name: Unique name of the App Component, must be a valid URL character ^[a-z0-9_-]*$.
         Default value is None.
        :paramtype name: str
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response == {
                    "name": "str",  # Optional. AppComponent name.
                    "resourceId": "str",  # Optional. Azure Load Testing resource Id.
                    "testId": "str",  # Optional. [Required, if testRunId is not given] Load test
                      unique identifier.
                    "testRunId": "str",  # Optional. [Required if testId is not given] Load test
                      run unique identifier.
                    "value": {
                        "str": {
                            "displayName": "str",  # Optional. Azure resource display
                              name.
                            "kind": "str",  # Optional. Kind of Azure resource type.
                            "resourceGroup": "str",  # Optional. Resource group name of
                              the Azure resource.
                            "resourceId": "str",  # Fully qualified resource Id e.g
                              subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.LoadTestService/loadtests/{resName}.
                              Required.
                            "resourceName": "str",  # Azure resource name. Required.
                            "resourceType": "str",  # Azure resource type. Required.
                            "subscriptionId": "str"  # Optional. Subscription Id of the
                              Azure resource.
                        }
                    }
                }
        """

        if name is not None:
            return super().get_by_name(name=name, **kwargs)

        else:
            return super().get_app_component(test_run_id=test_run_id, test_id=test_id, **kwargs)


__all__: List[str] = ["TestOperations", "AppComponentOperations"]
# Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
