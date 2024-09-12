# pylint: disable=protected-access
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import (
    Any,
    IO,
    Optional,
    Dict,
    Union,
    cast,
    overload,
    List,
    MutableMapping,
    TypeVar,
    Callable,
    TYPE_CHECKING,
)  # pylint: disable=line-too-long
from azure.core.credentials import AzureKeyCredential
from azure.core.rest import HttpRequest, HttpResponse
from azure.core.pipeline import PipelineResponse
from azure.core.polling import LROPoller, NoPolling, PollingMethod
from azure.core.polling.base_polling import LROBasePolling
from azure.core.tracing.decorator import distributed_trace
from azure.core.utils import case_insensitive_dict

from . import models as _models
from ._model_base import _deserialize
from ._client import RadiologyInsightsClient as _RadiologyInsightsClient


JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object
T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, HttpResponse], T, Dict[str, Any]], Any]]

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from azure.core.credentials import TokenCredential


class RadiologyInsightsClient:  # pylint: disable=client-accepts-api-version-keyword
    """RadiologyInsightsClient.

    :param endpoint: Supported Cognitive Services endpoints (protocol and hostname, for example:
     https://westus2.api.cognitive.microsoft.com). Required.
    :type endpoint: str
    :param credential: Credential used to authenticate requests to the service. Is either a
     AzureKeyCredential type or a TokenCredential type. Required.
    :type credential: ~azure.core.credentials.AzureKeyCredential or
     ~azure.core.credentials.TokenCredential
    :keyword api_version: The API version to use for this operation. Default value is "2024-04-01".
     Note that overriding this default value may result in unsupported behavior.
    :paramtype api_version: str
    :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
     Retry-After header is present.
    """

    def __init__(self, endpoint: str, credential: Union[AzureKeyCredential, "TokenCredential"], **kwargs: Any) -> None:
        self._client = _RadiologyInsightsClient(endpoint=endpoint, credential=credential, **kwargs)

    @overload
    def begin_infer_radiology_insights(
        self,
        id: str,
        resource: _models.RadiologyInsightsJob,
        *,
        expand: Optional[List[str]] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> LROPoller[_models.RadiologyInsightsInferenceResult]:
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
        :return: An instance of LROPoller that returns RadiologyInsightsInferenceResult. The RadiologyInsightsInferenceResult is compatible with MutableMapping
        :rtype: ~azure.core.polling.LROPoller[~azure.healthinsights.radiologyinsights.models.RadiologyInsightsResult]
        :raises ~azure.core.exceptions.HttpResponseError:"""

    @overload
    def begin_infer_radiology_insights(
        self,
        id: str,
        resource: JSON,
        *,
        expand: Optional[List[str]] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> LROPoller[_models.RadiologyInsightsInferenceResult]:
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
        :return: An instance of LROPoller that returns RadiologyInsightsInferenceResult. The RadiologyInsightsInferenceResult is compatible with MutableMapping
        :rtype: ~azure.core.polling.LROPoller[~azure.healthinsights.radiologyinsights.models.RadiologyInsightsInferenceResult]
        :raises ~azure.core.exceptions.HttpResponseError:"""

    @overload
    def begin_infer_radiology_insights(
        self,
        id: str,
        resource: IO[bytes],
        *,
        expand: Optional[List[str]] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> LROPoller[_models.RadiologyInsightsInferenceResult]:
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
        :return: An instance of LROPoller that returns RadiologyInsightsInferenceResult. The RadiologyInsightsInferenceResult is compatible with MutableMapping
        :rtype: ~azure.core.polling.LROPoller[~azure.healthinsights.radiologyinsights.models.RadiologyInsightsInferenceResult]
        :raises ~azure.core.exceptions.HttpResponseError:"""

    @distributed_trace
    def begin_infer_radiology_insights(
        self,
        id: str,
        resource: Union[_models.RadiologyInsightsJob, JSON, IO[bytes]],
        *,
        expand: Optional[List[str]] = None,
        **kwargs: Any
    ) -> LROPoller[_models.RadiologyInsightsInferenceResult]:
        # pylint: disable=line-too-long
        """Create Radiology Insights inference result.

        Creates a Radiology Insights inference result with the given request body.

        :param id: The unique ID of the inference result. Required.
        :type id: str
        :param resource: The resource instance. Is one of the following types: RadiologyInsightsJob, JSON, IO[bytes] Required.
        :type resource: ~azure.healthinsights.radiologyinsights.models.RadiologyInsightsJob or JSON or IO[bytes]
        :keyword expand: Expand the indicated resources into the response. Default value is None.
        :paramtype expand: list[str]
        :return: An instance of LROPoller that returns RadiologyInsightsInferenceResult. The RadiologyInsightsInferenceResult is compatible with MutableMapping
        :rtype: ~azure.core.polling.LROPoller[~azure.healthinsights.radiologyinsights.models.RadiologyInsightsInferenceResult]
        :raises ~azure.core.exceptions.HttpResponseError:"""

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[_models.RadiologyInsightsJob] = kwargs.pop("cls", None)
        polling: Union[bool, PollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop(
            "polling_interval", self._client._config.polling_interval  # pylint: disable=protected-access
        )
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)
        if cont_token is None:
            raw_result = self._client._infer_radiology_insights_initial(  # pylint: disable=protected-access
                id=id,
                resource=resource,
                expand=expand,
                content_type=content_type,
                cls=lambda x, y, z: x,
                headers=_headers,
                params=_params,
                **kwargs
            )
            raw_result.http_response.read()  # type: ignore
        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            response_headers = {}
            response = pipeline_response.http_response
            response_headers["x-ms-request-id"] = self._client._deserialize(  # pylint: disable=protected-access
                "str", response.headers.get("x-ms-request-id")
            )
            response_headers["Operation-Location"] = self._client._deserialize(  # pylint: disable=protected-access
                "str", response.headers.get("Operation-Location")
            )
            deserialized = _deserialize(_models.RadiologyInsightsInferenceResult, response.json().get("result"))
            if cls:
                return cls(pipeline_response, deserialized, response_headers)  # type: ignore
            return deserialized

        path_format_arguments = {
            "endpoint": self._client._serialize.url(  # pylint: disable=protected-access
                "self._client._config.endpoint", self._client._config.endpoint, "str", skip_quote=True
            ),
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
            return LROPoller[_models.RadiologyInsightsInferenceResult].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client._client,  # pylint: disable=protected-access
                deserialization_callback=get_long_running_output,
            )
        return LROPoller[_models.RadiologyInsightsInferenceResult](
            self._client._client, raw_result, get_long_running_output, polling_method  # type: ignore # pylint: disable=protected-access
        )

    def send_request(self, request: HttpRequest, *, stream: bool = False, **kwargs: Any) -> HttpResponse:
        """Runs the network request through the client's chained policies.

        >>> from azure.core.rest import HttpRequest
        >>> request = HttpRequest("GET", "https://www.example.org/")
        <HttpRequest [GET], url: 'https://www.example.org/'>
        >>> response = client.send_request(request)
        <HttpResponse: 200 OK>

        For more information on this code flow, see https://aka.ms/azsdk/dpcodegen/python/send_request

        :param request: The network request you want to make. Required.
        :type request: ~azure.core.rest.HttpRequest
        :keyword bool stream: Whether the response payload will be streamed. Defaults to False.
        :return: The response of your network call. Does not do error handling on your response.
        :rtype: ~azure.core.rest.HttpResponse
        """

        return self._client.send_request(request, stream=stream, **kwargs)  # type: ignore

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "RadiologyInsightsClient":
        self._client.__enter__()
        return self

    def __exit__(self, *exc_details: Any) -> None:
        self._client.__exit__(*exc_details)


__all__: List[str] = [
    "RadiologyInsightsClient"
]  # Add all objects you want publicly available to users at this package level # pylint: disable=line-too-long


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
