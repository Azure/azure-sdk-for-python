# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import Any, Awaitable, Callable, Mapping, Union
from urllib.parse import urlsplit

from azure.core.exceptions import AzureError
from azure.core.pipeline import PipelineRequest, PipelineResponse
from azure.core.pipeline.policies import AsyncHTTPPolicy
from azure.core.pipeline.transport import AsyncHttpResponse as LegacyAsyncHttpResponse
from azure.core.rest import AsyncHttpResponse

from ._external_evaluation import (
    HTTPRequestType,
    PolicyTokenRequestContext,
    _acquisition_context,
    _denied,
    _eligible,
    _get_token,
    _missing_token_details,
    _replay_request,
)

AsyncHTTPResponseType = Union[LegacyAsyncHttpResponse, AsyncHttpResponse]


class AsyncExternalEvaluationPolicy(AsyncHTTPPolicy[HTTPRequestType, AsyncHTTPResponseType]):
    """Opt in to asynchronous, subscription-level ARM external evaluation.

    Install using ``per_call_policies`` before retry and authentication.
    The provider must use a separate async client without this policy, disable
    acquisition body logging, and return the complete acquisition response.
    Streaming bodies and automatic ChangeSafety integration are not supported.

    :param policy_token_provider: Async callback receiving an immutable operation
        context and returning the acquisition response.
    :type policy_token_provider: callable[
        [~azure.mgmt.core.policies.PolicyTokenRequestContext], Awaitable[Mapping[str, Any]]]
    """

    def __init__(
        self,
        policy_token_provider: Callable[[PolicyTokenRequestContext], Awaitable[Mapping[str, Any]]],
    ) -> None:
        if not callable(policy_token_provider):
            raise TypeError("policy_token_provider must be callable.")
        self._provider = policy_token_provider

    async def send(
        self, request: PipelineRequest[HTTPRequestType]
    ) -> PipelineResponse[HTTPRequestType, AsyncHTTPResponseType]:
        """Acquire and replay once without blocking synchronous acquisition.

        :param request: The pipeline request.
        :type request: ~azure.core.pipeline.PipelineRequest
        :return: The original response or the token-bound replay response.
        :rtype: ~azure.core.pipeline.PipelineResponse
        :raises ~azure.core.exceptions.HttpResponseError: If acquisition or evaluation fails.
        """
        initially_eligible = _eligible(request.http_request)
        original_origin = urlsplit(request.http_request.url).netloc.lower()
        response = await self.next.send(request)
        http_request = request.http_request
        if (
            not initially_eligible
            or not _eligible(http_request)
            or response.http_response.status_code != 403
            or urlsplit(http_request.url).netloc.lower() != original_origin
        ):
            return response
        if isinstance(response.http_response, AsyncHttpResponse):
            await response.http_response.read()
        else:
            load_body = getattr(response.http_response, "load_body", None)
            if load_body is not None:
                await load_body()
        hints = _missing_token_details(response.http_response.text())
        if not hints:
            return response
        context = _acquisition_context(http_request, response.http_response, hints)
        try:
            result = await self._provider(context)
        except AzureError as error:
            raise _denied(
                response.http_response,
                "Policy-token acquisition failed; see the chained exception.",
            ) from error
        token = _get_token(result, response.http_response)
        await response.http_response.__aexit__(None, None, None)
        request.http_request = _replay_request(http_request, context, token)
        request.context.options.update(permit_redirects=False, logging_enable=False)
        return await self.next.send(request)
