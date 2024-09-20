# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Policy implementing Key Vault's challenge authentication protocol.

Normally the protocol is only used for the client's first service request, upon which:
1. The challenge authentication policy sends a copy of the request, without authorization or content.
2. Key Vault responds 401 with a header (the 'challenge') detailing how the client should authenticate such a request.
3. The policy authenticates according to the challenge and sends the original request with authorization.

The policy caches the challenge and thus knows how to authenticate future requests. However, authentication
requirements can change. For example, a vault may move to a new tenant. In such a case the policy will attempt the
protocol again.
"""

from copy import deepcopy
import time
from typing import Any, Awaitable, Callable, Optional, overload, TypeVar, Union
from urllib.parse import urlparse

from typing_extensions import ParamSpec

from azure.core.credentials import AccessToken
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.pipeline import PipelineRequest, PipelineResponse
from azure.core.pipeline.policies import AsyncBearerTokenCredentialPolicy
from azure.core.rest import AsyncHttpResponse, HttpRequest

from . import http_challenge_cache as ChallengeCache
from .challenge_auth_policy import _enforce_tls, _update_challenge


P = ParamSpec("P")
T = TypeVar("T")


@overload
async def await_result(func: Callable[P, Awaitable[T]], *args: P.args, **kwargs: P.kwargs) -> T: ...


@overload
async def await_result(func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T: ...


async def await_result(func: Callable[P, Union[T, Awaitable[T]]], *args: P.args, **kwargs: P.kwargs) -> T:
    """If func returns an awaitable, await it.

    :param func: The function to run.
    :type func: callable
    :param args: The positional arguments to pass to the function.
    :type args: list
    :rtype: any
    :return: The result of the function
    """
    result = func(*args, **kwargs)
    if isinstance(result, Awaitable):
        return await result
    return result


class AsyncChallengeAuthPolicy(AsyncBearerTokenCredentialPolicy):
    """Policy for handling HTTP authentication challenges.

    :param credential: An object which can provide an access token for the vault, such as a credential from
        :mod:`azure.identity.aio`
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential
    """

    def __init__(self, credential: AsyncTokenCredential, *scopes: str, **kwargs: Any) -> None:
        super().__init__(credential, *scopes, **kwargs)
        self._credential: AsyncTokenCredential = credential
        self._token: Optional[AccessToken] = None
        self._verify_challenge_resource = kwargs.pop("verify_challenge_resource", True)
        self._request_copy: Optional[HttpRequest] = None
        self._enable_cae = kwargs.pop("enable_cae", True)  # When True, `enable_cae=True` is always passed to get_token

    async def send(
        self, request: PipelineRequest[HttpRequest]
    ) -> PipelineResponse[HttpRequest, AsyncHttpResponse]:
        """Authorize request with a bearer token and send it to the next policy.

        We implement this method to account for the valid scenario where a Key Vault authentication challenge is
        immediately followed by a CAE claims challenge. The base class's implementation would return the second 401 to
        the caller, but we should handle that second challenge as well (and only return any third 401 response).

        :param request: The pipeline request object
        :type request: ~azure.core.pipeline.PipelineRequest
        :return: The pipeline response object
        :rtype: ~azure.core.pipeline.PipelineResponse
        """
        await await_result(self.on_request, request)
        response: PipelineResponse[HttpRequest, AsyncHttpResponse]
        try:
            response = await self.next.send(request)
        except Exception:  # pylint:disable=broad-except
            await await_result(self.on_exception, request)
            raise
        await await_result(self.on_response, request, response)

        if response.http_response.status_code == 401:
            return await self.handle_challenge_flow(request, response)
        return response

    async def handle_challenge_flow(
        self,
        request: PipelineRequest[HttpRequest],
        response: PipelineResponse[HttpRequest, AsyncHttpResponse],
        consecutive_challenge: bool = False,
    ) -> PipelineResponse[HttpRequest, AsyncHttpResponse]:
        """Handle the challenge flow of Key Vault and CAE authentication.

        :param request: The pipeline request object
        :type request: ~azure.core.pipeline.PipelineRequest
        :param response: The pipeline response object
        :type response: ~azure.core.pipeline.PipelineResponse
        :param bool consecutive_challenge: Whether the challenge is arriving immediately after another challenge.
            Consecutive challenges can only be valid if a Key Vault challenge is followed by a CAE claims challenge.
            True if the preceding challenge was a Key Vault challenge; False otherwise.

        :return: The pipeline response object
        :rtype: ~azure.core.pipeline.PipelineResponse
        """
        self._token = None  # any cached token is invalid
        if "WWW-Authenticate" in response.http_response.headers:
            request_authorized = await self.on_challenge(request, response)
            if request_authorized:
                # if we receive a challenge response, we retrieve a new token
                # which matches the new target. In this case, we don't want to remove
                # token from the request so clear the 'insecure_domain_change' tag
                request.context.options.pop("insecure_domain_change", False)
                try:
                    response = await self.next.send(request)
                except Exception:  # pylint:disable=broad-except
                    await await_result(self.on_exception, request)
                    raise

                # If consecutive_challenge == True, this could be a third consecutive 401
                if response.http_response.status_code == 401 and not consecutive_challenge:
                    # If the previous challenge wasn't from CAE, we can try this function one more time
                    challenge = ChallengeCache.get_challenge_for_url(request.http_request.url)
                    if challenge and not challenge.claims:
                        return await self.handle_challenge_flow(request, response, consecutive_challenge=True)
                await await_result(self.on_response, request, response)
        return response


    async def on_request(self, request: PipelineRequest) -> None:
        _enforce_tls(request)
        challenge = ChallengeCache.get_challenge_for_url(request.http_request.url)
        if challenge:
            # Note that if the vault has moved to a new tenant since our last request for it, this request will fail.
            if self._need_new_token():
                # azure-identity credentials require an AADv2 scope but the challenge may specify an AADv1 resource
                scope = challenge.get_scope() or challenge.get_resource() + "/.default"
                # Exclude tenant for AD FS authentication
                if challenge.tenant_id and challenge.tenant_id.lower().endswith("adfs"):
                    self._token = await self._credential.get_token(scope)
                else:
                    self._token = await self._credential.get_token(scope, tenant_id=challenge.tenant_id)

            # ignore mypy's warning -- although self._token is Optional, get_token raises when it fails to get a token
            request.http_request.headers["Authorization"] = f"Bearer {self._token.token}"  # type: ignore
            return

        # else: discover authentication information by eliciting a challenge from Key Vault. Remove any request data,
        # saving it for later. Key Vault will reject the request as unauthorized and respond with a challenge.
        # on_challenge will parse that challenge, use the original request including the body, authorize the
        # request, and tell super to send it again.
        if request.http_request.content:
            self._request_copy = request.http_request
            bodiless_request = HttpRequest(
                method=request.http_request.method,
                url=request.http_request.url,
                headers=deepcopy(request.http_request.headers),
            )
            bodiless_request.headers["Content-Length"] = "0"
            request.http_request = bodiless_request


    async def on_challenge(self, request: PipelineRequest, response: PipelineResponse) -> bool:
        try:
            # CAE challenges may not include a scope or tenant; cache from the previous challenge to use if necessary
            old_scope: Optional[str] = None
            old_tenant: Optional[str] = None
            cached_challenge = ChallengeCache.get_challenge_for_url(request.http_request.url)
            if cached_challenge:
                old_scope = cached_challenge.get_scope() or cached_challenge.get_resource() + "/.default"
                old_tenant = cached_challenge.tenant_id

            challenge = _update_challenge(request, response)
            # azure-identity credentials require an AADv2 scope but the challenge may specify an AADv1 resource
            scope = challenge.get_scope() or challenge.get_resource() + "/.default"
        except ValueError:
            return False

        if self._verify_challenge_resource:
            resource_domain = urlparse(scope).netloc
            if not resource_domain:
                # Use the old scope for CAE challenges. The parsing will succeed here since it did before
                if challenge.claims and old_scope:
                    resource_domain = urlparse(old_scope).netloc
                    challenge._parameters["scope"] = old_scope  # pylint:disable=protected-access
                    challenge.tenant_id = old_tenant
                else:
                    raise ValueError(f"The challenge contains invalid scope '{scope}'.")

            request_domain = urlparse(request.http_request.url).netloc
            if not request_domain.lower().endswith(f".{resource_domain.lower()}"):
                raise ValueError(
                    f"The challenge resource '{resource_domain}' does not match the requested domain. Pass "
                    "`verify_challenge_resource=False` to your client's constructor to disable this verification. "
                    "See https://aka.ms/azsdk/blog/vault-uri for more information."
                )

        # If we had created a request copy in on_request, use it now to send along the original body content
        if self._request_copy:
            request.http_request = self._request_copy

        # The tenant parsed from AD FS challenges is "adfs"; we don't actually need a tenant for AD FS authentication
        # For AD FS we skip cross-tenant authentication per https://github.com/Azure/azure-sdk-for-python/issues/28648
        if challenge.tenant_id and challenge.tenant_id.lower().endswith("adfs"):
            await self.authorize_request(request, scope, claims=challenge.claims)
        else:
            await self.authorize_request(
                request, scope, claims=challenge.claims, tenant_id=challenge.tenant_id
            )

        return True

    def _need_new_token(self) -> bool:
        return not self._token or self._token.expires_on - time.time() < 300
