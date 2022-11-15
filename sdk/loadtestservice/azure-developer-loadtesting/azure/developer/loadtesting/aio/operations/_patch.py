# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, IO, Optional, Union, cast, overload, List, MutableMapping, Coroutine, BinaryIO, Awaitable
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    map_error,
)
from azure.core.tracing.decorator import distributed_trace
from azure.core.utils import case_insensitive_dict

from ._operations import AppComponentOperations as AppComponentOperationsGenerated
from ._operations import TestOperations as TestOperationsGenerated, JSON, ClsType
from ...operations._patch import build_upload_test_file_request


class TestOperations(TestOperationsGenerated):
    """
    for performing the operations on test
    """

    def __init__(self, *args, **kwargs):
        super(TestOperations, self).__init__(*args, **kwargs)

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


class AppComponentOperations:
    def __init__(self, *args, **kwargs):
        self.__app_component_operations_generated = AppComponentOperationsGenerated(*args, **kwargs)

    async def get_app_components(
        self,
        *,
        test_run_id: Optional[str] = None,
        test_id: Optional[str] = None,
        name: Optional[str] = None,
        **kwargs: Any,
    ) -> MutableMapping[str, Any]:
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
            return await self.__app_component_operations_generated.get_app_component_by_name(name=name, **kwargs)
        else:
            return await self.__app_component_operations_generated.get_app_component(
                test_run_id=test_run_id, test_id=test_id, **kwargs
            )

    @overload
    async def create_or_update_app_components(
        self, name: str, body: JSON, *, content_type: str = "application/merge-patch+json", **kwargs: Any
    ) -> JSON:
        """Associate an App Component (Azure resource) to a test or test run.

        Associate an App Component (Azure resource) to a test or test run.

        :param name: Unique name of the App Component, must be a valid URL character ^[a-z0-9_-]*$.
         Required.
        :type name: str
        :param body: App Component model. Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/merge-patch+json".
        :paramtype content_type: str
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                body = {
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

                # response body for status code(s): 200, 201
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

    @overload
    async def create_or_update_app_components(
        self, name: str, body: IO, *, content_type: str = "application/merge-patch+json", **kwargs: Any
    ) -> JSON:
        """Associate an App Component (Azure resource) to a test or test run.

        Associate an App Component (Azure resource) to a test or test run.

        :param name: Unique name of the App Component, must be a valid URL character ^[a-z0-9_-]*$.
         Required.
        :type name: str
        :param body: App Component model. Required.
        :type body: IO
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/merge-patch+json".
        :paramtype content_type: str
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200, 201
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

    @distributed_trace
    async def create_or_update_app_components(
        self, name: str, body: Union[JSON, IO], **kwargs: Any
    ) -> MutableMapping[str, Any]:
        """Associate an App Component (Azure resource) to a test or test run.

        Associate an App Component (Azure resource) to a test or test run.

        :param name: Unique name of the App Component, must be a valid URL character ^[a-z0-9_-]*$.
         Required.
        :type name: str
        :param body: App Component model. Is either a model type or a IO type. Required.
        :type body: JSON or IO
        :keyword content_type: Body Parameter content-type. Known values are:
         'application/merge-patch+json'. Default value is None.
        :paramtype content_type: str
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200, 201
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
        return await self.__app_component_operations_generated.create_or_update_app_components(name, body, **kwargs)

    @distributed_trace
    async def delete_app_components(  # pylint: disable=inconsistent-return-statements
        self, name: str, **kwargs: Any
    ) -> None:
        """Delete an App Component.

        Delete an App Component.

        :param name: Unique name of the App Component, must be a valid URL character ^[a-z0-9_-]*$.
        Required.
        :type name: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        return await self.__app_component_operations_generated.delete_app_components(name, **kwargs)


__all__: List[str] = ["TestOperations", "AppComponentOperations"]


# Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
