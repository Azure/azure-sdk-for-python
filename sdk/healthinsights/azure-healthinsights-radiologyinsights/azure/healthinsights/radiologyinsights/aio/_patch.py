# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from copy import deepcopy
from typing import Any, Callable, Dict, IO, TYPE_CHECKING, List, Optional, TypeVar, Union, cast, overload, MutableMapping

from azure.core import AsyncPipelineClient
from azure.core.pipeline import PipelineResponse, policies
from azure.core.credentials import AzureKeyCredential
from azure.core.polling import AsyncLROPoller, AsyncPollingMethod, AsyncNoPolling
from azure.core.polling.async_base_polling import AsyncLROBasePolling
from azure.core.rest import AsyncHttpResponse, HttpRequest
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.utils import case_insensitive_dict

from ._operations._operations import RadiologyInsightsClientOperationsMixin as _RadiologyInsightsClientOperationsMixin  # pylint: disable=line-too-long
from ._configuration import RadiologyInsightsClientConfiguration
from .._serialization import Deserializer, Serializer

from .. import models as _models


JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object
T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, AsyncHttpResponse], T, Dict[str, Any]], Any]]

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from azure.core.credentials_async import AsyncTokenCredential

    class RadiologyInsightsClient(
        _RadiologyInsightsClientOperationsMixin
    ):  # pylint: disable=client-accepts-api-version-keyword
        """RadiologyInsightsClient.

        :param endpoint: Supported Cognitive Services endpoints (protocol and hostname, for example:
        https://westus2.api.cognitive.microsoft.com). Required.
        :type endpoint: str
        :param credential: Credential used to authenticate requests to the service. Is either a
        AzureKeyCredential type or a TokenCredential type. Required.
        :type credential: ~azure.core.credentials.AzureKeyCredential or
        ~azure.core.credentials_async.AsyncTokenCredential
        :keyword api_version: The API version to use for this operation. Default value is "2024-04-01".
        Note that overriding this default value may result in unsupported behavior.
        :paramtype api_version: str
        :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
        Retry-After header is present.
        """

        def __init__(
            self, endpoint: str, credential: Union[AzureKeyCredential, "AsyncTokenCredential"], **kwargs: Any
        ) -> None:
            _endpoint = "{endpoint}/health-insights"
            self._config = RadiologyInsightsClientConfiguration(endpoint=endpoint, credential=credential, **kwargs)
            _policies = kwargs.pop("policies", None)
            if _policies is None:
                _policies = [
                    policies.RequestIdPolicy(**kwargs),
                    self._config.headers_policy,
                    self._config.user_agent_policy,
                    self._config.proxy_policy,
                    policies.ContentDecodePolicy(**kwargs),
                    self._config.redirect_policy,
                    self._config.retry_policy,
                    self._config.authentication_policy,
                    self._config.custom_hook_policy,
                    self._config.logging_policy,
                    policies.DistributedTracingPolicy(**kwargs),
                    policies.SensitiveHeaderCleanupPolicy(**kwargs) if self._config.redirect_policy else None,
                    self._config.http_logging_policy,
                ]
            self._client: AsyncPipelineClient = AsyncPipelineClient(base_url=_endpoint, policies=_policies, **kwargs)

            self._serialize = Serializer()
            self._deserialize = Deserializer()
            self._serialize.client_side_validation = False

        @overload  # type: ignore[override]
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
                raw_result = self._infer_radiology_insights_initial(
                    id=id,
                    resource=resource,
                    expand=expand,
                    content_type=content_type,
                    cls=lambda x, y, z: x,
                    headers=_headers,
                    params=_params,
                    **kwargs
                )
                raw_result.http_response.read() # type: ignore
            kwargs.pop("error_map", None)

            def get_long_running_output(pipeline_response):
                response_headers = {}
                response = pipeline_response.http_response
                response_headers['x-ms-request-id']=self._deserialize('str', response.headers.get('x-ms-request-id'))
                response_headers['Operation-Location']=self._deserialize('str', response.headers.get('Operation-Location'))
                deserialized = self._deserialize(
                    _models.RadiologyInsightsInferenceResult,
                    response.json().get("result")
                )
                if cls:
                    return cls(pipeline_response, deserialized, response_headers) # type: ignore
                return deserialized

            path_format_arguments = {
                "endpoint": self._serialize.url("self._client._config.endpoint", self._config.endpoint, 'str', skip_quote=True),
            }

            if polling is True:
                polling_method: AsyncPollingMethod = cast(
                    AsyncPollingMethod, AsyncLROBasePolling(lro_delay, path_format_arguments=path_format_arguments, **kwargs)
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

__all__: List[str] = [
    "RadiologyInsightsClient"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """