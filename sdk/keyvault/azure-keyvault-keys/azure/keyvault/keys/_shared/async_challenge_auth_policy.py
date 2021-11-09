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
from typing import TYPE_CHECKING

from azure.core.pipeline.policies import AsyncBearerTokenCredentialPolicy

from . import http_challenge_cache as ChallengeCache
from .challenge_auth_policy import _enforce_tls, _update_challenge

if TYPE_CHECKING:
    from azure.core.pipeline import PipelineRequest, PipelineResponse
    from .http_challenge import HttpChallenge


class AsyncChallengeAuthPolicy(AsyncBearerTokenCredentialPolicy):
    """policy for handling HTTP authentication challenges"""

    async def on_request(self, request: "PipelineRequest") -> None:
        _enforce_tls(request)
        challenge = ChallengeCache.get_challenge_for_url(request.http_request.url)
        if challenge:
            # Note that if the vault has moved to a new tenant since our last request for it, this request will fail.
            await self._handle_challenge(request, challenge)
            response = await self.next.send(request)
            return await self._handle_response(request, response)

        # else: discover authentication information by eliciting a challenge from Key Vault. Remove any request data,
        # saving it for later. Key Vault will reject the request as unauthorized and respond with a challenge.
        # on_challenge will parse that challenge, reattach any body removed here, authorize the request, and tell
        # super to send it again.
        if request.http_request.body:
            request.context["key_vault_request_data"] = request.http_request.body
            request.http_request.set_json_body(None)
            request.http_request.headers["Content-Length"] = "0"


    async def on_challenge(self, request: "PipelineRequest", response: "PipelineResponse") -> bool:
        try:
            challenge = _update_challenge(request, response)
            scope = challenge.get_scope() or challenge.get_resource() + "/.default"
        except ValueError:
            return False

        self._scopes = (scope,)

        body = request.context.pop("key_vault_request_data", None)
        request.http_request.set_text_body(body)  # no-op when text is None
        await self.authorize_request(request, *self._scopes, tenant_id=challenge.tenant_id)

        return True

    async def _handle_challenge(self, request: "PipelineRequest", challenge: "HttpChallenge") -> None:
        """Authenticate according to challenge, add Authorization header to request"""

        scope = challenge.get_scope() or challenge.get_resource() + "/.default"
        await self.authorize_request(request, scope, tenant_id=challenge.tenant_id)

    async def _handle_response(self, request: "PipelineRequest", response: "PipelineResponse") -> "PipelineResponse":
        """Return a response and attempt to handle any authentication challenges"""

        if response.http_response.status_code == 401:
            # any cached token must be invalid
            self._token = None

            # cached challenge could be outdated; maybe this response has a new one?
            try:
                challenge = _update_challenge(request, response)
            except ValueError:
                # 401 with no legible challenge -> nothing more this policy can do
                return response

            await self._handle_challenge(request, challenge)
            response = await self.next.send(request)

        return response
