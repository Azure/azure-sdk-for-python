# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List

__all__: List[str] = [
    "RadiologyInsightsClientOperationsMixin"
]  # Add all objects you want publicly available to users at this package level

from io import IOBase
import json
import sys
import logging
from typing import Any, Callable, Dict, IO, List, Optional, Type, TypeVar, Union, cast, overload

from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
    map_error,
)
from azure.core.pipeline import PipelineResponse
from azure.core.polling import AsyncLROPoller, AsyncNoPolling, AsyncPollingMethod
from azure.core.polling.async_base_polling import AsyncLROBasePolling
from azure.core.rest import AsyncHttpResponse, HttpRequest
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.utils import case_insensitive_dict

from ... import models as _models
from ..._model_base import SdkJSONEncoder, _deserialize
from ._operations import RadiologyInsightsClientOperationsMixin as GeneratedRadiologyInsightsClientOperationsMixin

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore  # pylint: disable=ungrouped-imports
JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object
T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, AsyncHttpResponse], T, Dict[str, Any]], Any]]

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
class RadiologyInsightsClientOperationsMixin(GeneratedRadiologyInsightsClientOperationsMixin):

    @overload
    async def begin_infer_radiology_insights(
        self,
        id: str,
        resource: _models.RadiologyInsightsJob,
        *,
        expand: Optional[List[str]] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> AsyncLROPoller[_models.RadiologyInsightsInferenceResult]:...
        

    @overload
    async def begin_infer_radiology_insights(
        self,
        id: str,
        resource: JSON,
        *,
        expand: Optional[List[str]] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> AsyncLROPoller[_models.RadiologyInsightsInferenceResult]:...
        

    @overload
    async def begin_infer_radiology_insights(
        self,
        id: str,
        resource: IO[bytes],
        *,
        expand: Optional[List[str]] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> AsyncLROPoller[_models.RadiologyInsightsInferenceResult]:...
        


    @distributed_trace_async
    async def begin_infer_radiology_insights(
        self,
        id: str,
        resource: Union[_models.RadiologyInsightsJob, JSON, IO[bytes]],
        *,
        expand: Optional[List[str]] = None,
        **kwargs: Any
    ) -> AsyncLROPoller[_models.RadiologyInsightsInferenceResult]:
        
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[_models.RadiologyInsightsJob] = kwargs.pop("cls", None)
        polling: Union[bool, AsyncPollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)
        if cont_token is None:
            raw_result = await self._infer_radiology_insights_initial(
                id=id,
                resource=resource,
                expand=expand,
                content_type=content_type,
                cls=lambda x, y, z: x,
                headers=_headers,
                params=_params,
                **kwargs
            )# type: ignore
            await raw_result.http_response.read()
            logger.debug(f"Raw result: {raw_result}")
        kwargs.pop('error_map', None)

        def get_long_running_output(pipeline_response):
            response_headers = {}
            response = pipeline_response.http_response
            response_headers["x-ms-request-id"] = self._deserialize("str", response.headers.get("x-ms-request-id"))
            response_headers["Operation-Location"] = self._deserialize(
                "str", response.headers.get("Operation-Location")
            )

            deserialized = _deserialize(_models.RadiologyInsightsInferenceResult, response.json().get("result"))
            if cls:
                return cls(pipeline_response, deserialized, response_headers) # type: ignore
            return deserialized


        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, 'str', skip_quote=True),
        }

        if polling is True:
            polling_method: AsyncPollingMethod = cast(
                AsyncPollingMethod,
                AsyncLROBasePolling(lro_delay, path_format_arguments=path_format_arguments, **kwargs),
            )
        elif polling is False:
            polling_method = cast(AsyncPollingMethod, AsyncNoPolling())
        else:
            polling_method = polling
        if cont_token:
            return AsyncLROPoller[_models.RadiologyInsightsInferenceResult].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output
            )
        return AsyncLROPoller[_models.RadiologyInsightsInferenceResult](
            self._client, raw_result, get_long_running_output, polling_method  # type: ignore
            )

def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """

