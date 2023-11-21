# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from copy import deepcopy
from typing import Any, Union
from azure.core.credentials import AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.pipeline.policies import HttpLoggingPolicy
from azure.core.rest import AsyncHttpResponse, HttpRequest
from azure.core.tracing.decorator_async import distributed_trace_async
from .._form_base_client import _format_api_version, _SERIALIZER
from .._generated.aio._form_recognizer_client import (
    FormRecognizerClient as FormRecognizer,
)
from .._api_versions import validate_api_version
from .._helpers import (
    _get_deserialize,
    get_authentication_policy,
    POLLING_INTERVAL,
    QuotaExceededPolicy,
)
from .._user_agent import USER_AGENT


class FormRecognizerClientBaseAsync:
    def __init__(
        self, endpoint: str, credential: Union[AzureKeyCredential, AsyncTokenCredential], **kwargs: Any
    ) -> None:

        try:
            endpoint = endpoint.rstrip("/")
        except AttributeError:
            raise ValueError("Parameter 'endpoint' must be a string.")  # pylint: disable=raise-missing-from

        self._endpoint = endpoint
        self._credential = credential
        self._api_version = kwargs.pop("api_version", None)
        if not self._api_version:
            raise ValueError("'api_version' must be specified.")
        if self._api_version.startswith("v"):  # v2.0 released with this option
            self._api_version = self._api_version[1:]

        client_kind = kwargs.pop("client_kind")
        validate_api_version(self._api_version, client_kind)

        authentication_policy = get_authentication_policy(credential)
        polling_interval = kwargs.pop("polling_interval", POLLING_INTERVAL)

        http_logging_policy = HttpLoggingPolicy(**kwargs)
        http_logging_policy.allowed_header_names.update(
            {
                "Operation-Location",
                "Location",
                "x-envoy-upstream-service-time",
                "apim-request-id",
                "Strict-Transport-Security",
                "x-content-type-options",
                "ms-azure-ai-errorcode",
                "x-ms-cs-error-code",
                "x-ms-region",
            }
        )
        http_logging_policy.allowed_query_params.update(
            {
                "includeTextDetails",
                "locale",
                "language",
                "includeKeys",
                "op",
                "pages",
                "readingOrder",
                "stringIndexType",
                "api-version",
            }
        )

        self._client = FormRecognizer(
            endpoint=endpoint,
            credential=credential,  # type: ignore
            api_version=self._api_version,
            sdk_moniker=USER_AGENT,
            authentication_policy=kwargs.get("authentication_policy", authentication_policy),
            http_logging_policy=kwargs.get("http_logging_policy", http_logging_policy),
            per_retry_policies=kwargs.get("per_retry_policies", QuotaExceededPolicy()),
            polling_interval=polling_interval,
            **kwargs
        )
        self._deserialize = _get_deserialize(self._api_version)
        self._generated_models = self._client.models(self._api_version)

    @distributed_trace_async
    async def send_request(self, request: HttpRequest, *, stream: bool = False, **kwargs) -> AsyncHttpResponse:
        """Runs a network request using the client's existing pipeline.

        The request URL can be relative to the base URL. The service API version used for the request is the same as
        the client's unless otherwise specified. Overriding the client's configured API version in relative URL is
        supported on client with API version 2022-08-31 and later. Overriding in absolute URL supported on client with
        any API version. This method does not raise if the response is an error; to raise an exception, call
        `raise_for_status()` on the returned response object. For more information about how to send custom requests
        with this method, see https://aka.ms/azsdk/dpcodegen/python/send_request.

        :param request: The network request you want to make.
        :type request: ~azure.core.rest.HttpRequest
        :return: The response of your network call. Does not do error handling on your response.
        :rtype: ~azure.core.rest.AsyncHttpResponse
        """
        api_version = self._api_version
        if hasattr(api_version, "value"):
            api_version = api_version.value
        if self._api_version in ["2.0", "2.1"]:
            request_copy = deepcopy(request)
        else:
            request_copy = _format_api_version(request, api_version)
        path_format_arguments = {
            "endpoint": _SERIALIZER.url("endpoint", self._endpoint, "str", skip_quote=True),
        }
        request_copy.url = self._client._client.format_url(request_copy.url, **path_format_arguments)  # pylint:disable=protected-access
        return await self._client._client.send_request(request_copy, stream=stream, **kwargs)  # pylint:disable=protected-access
