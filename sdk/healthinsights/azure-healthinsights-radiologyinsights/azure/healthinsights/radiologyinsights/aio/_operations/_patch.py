# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import Any, Callable, Dict, IO, List, Optional, TypeVar, Union, cast, overload, MutableMapping

__all__: List[str] = [
    "RadiologyInsightsClientOperationsMixin"
]  # Add all objects you want publicly available to users at this package level

from azure.core.pipeline import PipelineResponse
from azure.core.polling import AsyncLROPoller, AsyncNoPolling, AsyncPollingMethod
from azure.core.polling.async_base_polling import AsyncLROBasePolling
from azure.core.rest import AsyncHttpResponse, HttpRequest
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.utils import case_insensitive_dict

from ... import models as _models
from ..._model_base import _deserialize
from ._operations import RadiologyInsightsClientOperationsMixin as GeneratedRadiologyInsightsClientOperationsMixin

JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object
T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, AsyncHttpResponse], T, Dict[str, Any]], Any]]
class RadiologyInsightsClientOperationsMixin(GeneratedRadiologyInsightsClientOperationsMixin):

    @overload # type: ignore[override]
    async def begin_infer_radiology_insights(
        self,
        id: str,
        resource: _models.RadiologyInsightsJob,
        *,
        expand: Optional[List[str]] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> AsyncLROPoller[_models.RadiologyInsightsInferenceResult]:
        # pylint: disable=line-too-long
        """Create Radiology Insights inference result.

        Creates a Radiology Insights inference result with the given request body.

        :param id: The unique ID of the inference result. Required.
        :type id: str
        :param resource: The resource instance. Required.
        :type resource: ~azure.healthinsights.radiologyinsights.models.RadiologyInsightsJob
        :keyword expand: Expand the indicated resources into the response. Default value is None.
        :paramtype expand: list[str]
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body. Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller that returns RadiologyInsightsInferenceResult. The RadiologyInsightsInferenceResult is compatible with MutableMapping
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.healthinsights.radiologyinsights.models.RadiologyInsightsInferenceResult]
        :raises ~azure.core.exceptions.HttpResponseError:"""

    @overload  # type: ignore[override]
    async def begin_infer_radiology_insights(
        self,
        id: str,
        resource: JSON,
        *,
        expand: Optional[List[str]] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> AsyncLROPoller[_models.RadiologyInsightsInferenceResult]:
        # pylint: disable=line-too-long
        """Create Radiology Insights inference result.

        Creates a Radiology Insights inference result with the given request body.

        :param id: The unique ID of the inference result. Required.
        :type id: str
        :param resource: The resource instance. Required.
        :type resource: JSON
        :keyword expand: Expand the indicated resources into the response. Default value is None.
        :paramtype expand: list[str]
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body. Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller that returns RadiologyInsightsInferenceResult. The RadiologyInsightsInferenceResult is compatible with MutableMapping
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.healthinsights.radiologyinsights.models.RadiologyInsightsInferenceResult]
        :raises ~azure.core.exceptions.HttpResponseError:"""

    @overload  # type: ignore[override]
    async def begin_infer_radiology_insights(
        self,
        id: str,
        resource: IO[bytes],
        *,
        expand: Optional[List[str]] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> AsyncLROPoller[_models.RadiologyInsightsInferenceResult]:
        # pylint: disable=line-too-long
        """Create Radiology Insights inference result.

        Creates a Radiology Insights inference result with the given request body.

        :param id: The unique ID of the inference result. Required.
        :type id: str
        :param resource: The resource instance. Required.
        :type resource: IO[bytes]
        :keyword expand: Expand the indicated resources into the response. Default value is None.
        :paramtype expand: list[str]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body. Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller that returns RadiologyInsightsInferenceResult. The RadiologyInsightsInferenceResult is compatible with MutableMapping
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.healthinsights.radiologyinsights.models.RadiologyInsightsInferenceResult]
        :raises ~azure.core.exceptions.HttpResponseError:"""

    @distributed_trace_async  # type: ignore[override]
    async def begin_infer_radiology_insights(
        self,
        id: str,
        resource: Union[_models.RadiologyInsightsJob, JSON, IO[bytes]],
        *,
        expand: Optional[List[str]] = None,
        **kwargs: Any
    ) -> AsyncLROPoller[_models.RadiologyInsightsInferenceResult]:
        # pylint: disable=line-too-long
        """Create Radiology Insights inference result.

        Creates a Radiology Insights inference result with the given request body.

        :param id: The unique ID of the inference result. Required.
        :type id: str
        :param resource: The resource instance. Is one of the following types: RadiologyInsightsJob, JSON, IO[bytes] Required.
        :type resource: ~azure.healthinsights.radiologyinsights.models.RadiologyInsightsJob or JSON or IO[bytes]
        :keyword expand: Expand the indicated resources into the response. Default value is None.
        :paramtype expand: list[str]
        :return: An instance of AsyncLROPoller that returns RadiologyInsightsInferenceResult. The RadiologyInsightsInferenceResult is compatible with MutableMapping
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.healthinsights.radiologyinsights.models.RadiologyInsightsInferenceResult]
        :raises ~azure.core.exceptions.HttpResponseError:"""

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
