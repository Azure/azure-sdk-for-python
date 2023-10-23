# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Callable, Coroutine, Any

from azure.core.credentials_async import AsyncTokenCredential
from azure.core.pipeline.policies import AsyncBearerTokenCredentialPolicy
from azure.core.pipeline import PipelineRequest, PipelineContext
from azure.core.rest import HttpRequest


def _make_request() -> PipelineRequest[HttpRequest]:
    return PipelineRequest(HttpRequest("CredentialWrapper", "https://fakeurl"), PipelineContext(None))


def get_bearer_token_provider(credential: AsyncTokenCredential, *scopes: str) -> Callable[[], Coroutine[Any, Any, str]]:
    """Returns a callable that provides a bearer token.

    It can be used for instance to write code like:

    .. code-block:: python

        from azure.identity.aio import DefaultAzureCredential, get_bearer_token_provider

        credential = DefaultAzureCredential()
        bearer_token_provider = get_bearer_token_provider(credential, "https://storage.azure.com/.default")


        # Usage
        request.headers["Authorization"] = "Bearer " + await bearer_token_provider()

    :param credential: The credential used to authenticate the request.
    :type credential: ~azure.core.credentials.TokenCredential
    :param str scopes: The scopes required for the bearer token.
    :rtype: coroutine
    :return: A coroutine that returns a bearer token.
    """

    async def wrapper() -> str:
        policy = AsyncBearerTokenCredentialPolicy(credential, *scopes)
        request = _make_request()
        await policy.on_request(request)
        return request.http_request.headers["Authorization"][len("Bearer ") :]

    return wrapper
