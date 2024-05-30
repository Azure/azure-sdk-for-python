# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import sys
from typing import Any, Callable, Dict, IO, Iterable, List, Optional, Type, TypeVar, Union, cast, overload
from ._operations import DevCenterClientOperationsMixin as DevCenterClientOperationsMixinGenerated

from azure.core.pipeline import PipelineResponse
from azure.core.polling import LROPoller, NoPolling, PollingMethod
from azure.core.polling.base_polling import LROBasePolling
from azure.core.rest import HttpRequest, HttpResponse
from azure.core.tracing.decorator import distributed_trace

from .. import models as _models
from .._model_base import SdkJSONEncoder, _deserialize
from .._serialization import Serializer
from .._vendor import DevCenterClientMixinABC

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore  # pylint: disable=ungrouped-imports
JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object
T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, HttpResponse], T, Dict[str, Any]], Any]]

_SERIALIZER = Serializer()
_SERIALIZER.client_side_validation = False

class DevCenterClientOperationsMixin(DevCenterClientOperationsMixinGenerated):
    @distributed_trace
    def begin_delete_dev_box(
        self, project_name: str, user_id: str, dev_box_name: str, **kwargs: Any
    ) -> LROPoller[None]:
        # pylint: disable=line-too-long
        """Deletes a Dev Box.

        :param project_name: The DevCenter Project upon which to execute operations. Required.
        :type project_name: str
        :param user_id: The AAD object id of the user. If value is 'me', the identity is taken from the
         authentication context. Required.
        :type user_id: str
        :param dev_box_name: The name of a Dev Box. Required.
        :type dev_box_name: str
        :return: An instance of LROPoller that returns either None or the result of cls(response)
        :rtype: ~azure.core.polling.LROPoller[~azure.developer.devcenter.models.OperationDetails]
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 202
                response == {
                    "id": "str",  # Fully qualified ID for the operation status. Required.
                    "name": "str",  # The operation id name. Required.
                    "status": "str",  # Provisioning state of the resource. Required. Known
                      values are: "NotStarted", "Running", "Succeeded", "Failed", and "Canceled".
                    "endTime": "2020-02-20 00:00:00",  # Optional. The end time of the operation.
                    "error": {
                        "code": "str",  # One of a server-defined set of error codes.
                          Required.
                        "message": "str",  # A human-readable representation of the error.
                          Required.
                        "details": [
                            ...
                        ],
                        "innererror": {
                            "code": "str",  # Optional. One of a server-defined set of
                              error codes.
                            "innererror": ...
                        },
                        "target": "str"  # Optional. The target of the error.
                    },
                    "percentComplete": 0.0,  # Optional. Percent of the operation that is
                      complete.
                    "properties": {},  # Optional. Custom operation properties, populated only
                      for a successful operation.
                    "resourceId": "str",  # Optional. The id of the resource.
                    "startTime": "2020-02-20 00:00:00"  # Optional. The start time of the
                      operation.
                }
        """
        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[_models.OperationDetails] = kwargs.pop("cls", None)
        polling: Union[bool, PollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)
        if cont_token is None:
            raw_result = self._delete_dev_box_initial(
                project_name=project_name,
                user_id=user_id,
                dev_box_name=dev_box_name,
                cls=lambda x, y, z: x,
                headers=_headers,
                params=_params,
                **kwargs
            )
        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            response_headers = {}
            response = pipeline_response.http_response
            response_headers["Location"] = self._deserialize("str", response.headers.get("Location"))
            response_headers["Operation-Location"] = self._deserialize(
                "str", response.headers.get("Operation-Location")
            )

            deserialized = _deserialize(_models.OperationDetails, response.json())
            if cls:
                return cls(pipeline_response, deserialized, response_headers)  # type: ignore
            return deserialized

        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }

        if polling is True:
            polling_method: PollingMethod = cast(
                PollingMethod, LROBasePolling(lro_delay, path_format_arguments=path_format_arguments, **kwargs)
            )
        elif polling is False:
            polling_method = cast(PollingMethod, NoPolling())
        else:
            polling_method = polling
        if cont_token:
            return LROPoller.from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )
        return LROPoller(self._client, raw_result, get_long_running_output, polling_method)
    
    @distributed_trace
    def begin_delete_environment(
        self, project_name: str, user_id: str, environment_name: str, **kwargs: Any
    ) -> LROPoller[None]:
        # pylint: disable=line-too-long
        """Deletes an environment and all its associated resources.

        :param project_name: The DevCenter Project upon which to execute operations. Required.
        :type project_name: str
        :param user_id: The AAD object id of the user. If value is 'me', the identity is taken from the
         authentication context. Required.
        :type user_id: str
        :param environment_name: The name of the environment. Required.
        :type environment_name: str
        :return: An instance of LROPoller that returns either None or the result of cls(response)
        :rtype: ~azure.core.polling.LROPoller[~azure.developer.devcenter.models.OperationDetails]
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 202
                response == {
                    "id": "str",  # Fully qualified ID for the operation status. Required.
                    "name": "str",  # The operation id name. Required.
                    "status": "str",  # Provisioning state of the resource. Required. Known
                      values are: "NotStarted", "Running", "Succeeded", "Failed", and "Canceled".
                    "endTime": "2020-02-20 00:00:00",  # Optional. The end time of the operation.
                    "error": {
                        "code": "str",  # One of a server-defined set of error codes.
                          Required.
                        "message": "str",  # A human-readable representation of the error.
                          Required.
                        "details": [
                            ...
                        ],
                        "innererror": {
                            "code": "str",  # Optional. One of a server-defined set of
                              error codes.
                            "innererror": ...
                        },
                        "target": "str"  # Optional. The target of the error.
                    },
                    "percentComplete": 0.0,  # Optional. Percent of the operation that is
                      complete.
                    "properties": {},  # Optional. Custom operation properties, populated only
                      for a successful operation.
                    "resourceId": "str",  # Optional. The id of the resource.
                    "startTime": "2020-02-20 00:00:00"  # Optional. The start time of the
                      operation.
                }
        """
        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[_models.OperationDetails] = kwargs.pop("cls", None)
        polling: Union[bool, PollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)
        if cont_token is None:
            raw_result = self._delete_environment_initial(
                project_name=project_name,
                user_id=user_id,
                environment_name=environment_name,
                cls=lambda x, y, z: x,
                headers=_headers,
                params=_params,
                **kwargs
            )
        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            response_headers = {}
            response = pipeline_response.http_response
            response_headers["Location"] = self._deserialize("str", response.headers.get("Location"))
            response_headers["Operation-Location"] = self._deserialize(
                "str", response.headers.get("Operation-Location")
            )

            deserialized = _deserialize(_models.OperationDetails, response.json())
            if cls:
                return cls(pipeline_response, deserialized, response_headers)  # type: ignore
            return deserialized

        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }

        if polling is True:
            polling_method: PollingMethod = cast(
                PollingMethod, LROBasePolling(lro_delay, path_format_arguments=path_format_arguments, **kwargs)
            )
        elif polling is False:
            polling_method = cast(PollingMethod, NoPolling())
        else:
            polling_method = polling
        if cont_token:
            return LROPoller.from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )
        return LROPoller(
            self._client, raw_result, get_long_running_output, polling_method  # type: ignore
        )


__all__: List[str] = ["DevCenterClientOperationsMixin"]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
