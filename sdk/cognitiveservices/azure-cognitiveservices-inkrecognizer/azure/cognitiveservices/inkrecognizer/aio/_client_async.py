#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from azure.core import AsyncPipelineClient
from azure.core.pipeline.transport import HttpRequest, AioHttpTransport
from azure.core.pipeline.policies import (
    AsyncRedirectPolicy,
    AsyncRetryPolicy,
    AsyncBearerTokenCredentialPolicy
)
from azure.core.tracing.decorator_async import distributed_trace_async
from .._client import _InkRecognizerClientBase, _AzureConfiguration


class _AzureConfigurationAsync(_AzureConfiguration):
    def __init__(self, credential, **kwargs): # pylint:disable=super-init-not-called
        self._set_universal(**kwargs)
        # async-specific azure pipeline policies
        if isinstance(credential, str):
            self.headers_policy.add_header("Ocp-Apim-Subscription-Key", credential)
        else:
            scopes = kwargs.pop("scopes", [])
            self.authentication_policy = AsyncBearerTokenCredentialPolicy(credential, *scopes, **kwargs)
        self.retry_policy = kwargs.get("retry_policy", AsyncRetryPolicy(**kwargs))
        self.redirect_policy = kwargs.get("redirect_policy", AsyncRedirectPolicy(**kwargs))
        self.transport = kwargs.get("transport", AioHttpTransport())


class InkRecognizerClient(_InkRecognizerClientBase):
    """
    The InkRecognizerClient communicates with the service using default
    configuration settings or settings provided by the caller. Communication
    with the service is done in asynchronous manner.

    :param str url: target url of the Ink Recognizer service.

    :param ~azure.core.TokenCredential credential: An available Azure Active
    Directory credential for Ink Recognition Service.

    Key word arguments include Ink Recognizer specific arguments, azure service
    common arguments and azure pipline policies.

    Ink Recognizer specific arguments:

    :param ServiceVersion service_version: Version of Ink Recognizer Service.
    Default is ServiceVersion.Preview.

    :param ApplicationKind application_kind: Inform Ink Recognizer Service of
    contents of the application. This can facilitate faster processing as the
    service will skip some classification steps. Default is ApplicationKind.MIXED.

    :param InkPointUnit ink_point_unit: unit of the x and y axis values for each
    InkPoint. Default is InkPointUnit.MM.

    :param str language: Language (IETF BCP-47) of strokes, will be overwritten
    by stroke-specific language. Default is "en-US".

    :param float unit_multiple: multiplier for unit. Each value in InkPoint
    will be multiplied by this value on server side. Default 1.0.

    Azure service common arguments:

    :param ~azure.core.pipeline.transport.HttpTransport transport: transport
    strategy for the client. Default is AioHttpTransport.

    :param float timeout: Timeout in seconds.

    :param dict headers: Custom headers to include in the service request.

    :param str client_request_id: Caller specified identification of the request.

    :param callable response_hook: callable that is called with
    (headers, deserialized_response) if the http status is 200.

    :param list[str] scopes: let you specify the type of access needed during authentication.

    Azure pipeline policies:
    https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/docs/configuration.md
    """

    def __init__(self, url, credential, **kwargs):
        # type: (str, TokenCredential, Any) -> None
        super().__init__(url, credential, **kwargs)
        azure_config = _AzureConfigurationAsync(credential, **kwargs)
        self._pipeline_client = AsyncPipelineClient(
            base_url=url, config=azure_config, transport=azure_config.transport)

    async def __aenter__(self):
        await self._pipeline_client.__aenter__()
        return self

    async def __aexit__(self, *exc_details):
        await self._pipeline_client.__aexit__(*exc_details)

    async def _send_request(self, data, config):
        request = HttpRequest("PUT", self._generate_url(config), data=data)
        response = await self._pipeline_client._pipeline.run(  # pylint:disable=protected-access
            request, headers=config.headers, **config.kwargs)
        return response.http_response

    @distributed_trace_async
    async def recognize_ink(self, ink_stroke_list, **kwargs):
        # type: (Iterable[IInkStroke], Any) -> InkRecognitionRoot
        """
        Asynchronously sends data to the service and returns a tree structure
        containing all the recognition units from Ink Recognizer Service. This
        method is thread-safe.

        :param Iterable[IInkStroke] ink_stroke_list: an iterable that contanins
        stroke instances.

        Key word arguments include Ink Recognizer specific arguments, azure
        service common arguments and azure pipline policies.

        Ink Recognizer specific arguments:

        :param ServiceVersion service_version: Version of Ink Recognizer Service.
        Default is ServiceVersion.Preview.

        :param ApplicationKind application_kind: Inform Ink Recognizer Service of
        contents of the application. This can facilitate faster processing as the
        service will skip some classification steps. Default is ApplicationKind.MIXED.

        :param InkPointUnit ink_point_unit: unit of the x and y axis coordinates
        for each InkPoint. Default is InkPointUnit.MM.

        :param str language: Language (IETF BCP-47) of strokes, can be overwritten
        by stroke-specific language. Default is "en-US".

        :param float unit_multiple: multiplier for unit. Each value in InkPoint
        will be multiplied by this value on server side. Default is 1.0.

        Azure service common arguments:

        :param float timeout: Timeout in seconds.

        :param dict headers: Custom headers to include in the service request.

        :param str client_request_id: Caller-specified identifier for the request.

        :param callable response_hook: callable that is called with
        (headers, deserialized_response) if the http status is 200.

        Azure pipeline policies:
        https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/docs/configuration.md

        :rtype: InkRecognitionRoot

        **Exceptions:**

        :raise ServerResponseError: Unexpected Server response that can't be parsed by client.

        :raise ResourceNotFoundError: Indicates URL is invalid.

        :raise ClientAuthenticationError: Authentication issue.

        :raise HttpResponseError: Unclassified error.
        """

        config = self._generate_config(kwargs)
        request_data = self._pack_request(ink_stroke_list, config)
        response = await self._send_request(data=request_data, config=config)
        return self._parse_result(response, config)
            