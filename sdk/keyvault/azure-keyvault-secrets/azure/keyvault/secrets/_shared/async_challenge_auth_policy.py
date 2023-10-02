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

import time
from typing import TYPE_CHECKING
from urllib.parse import urlparse

from azure.core.pipeline.policies import AsyncBearerTokenCredentialPolicy

from . import http_challenge_cache as ChallengeCache
from .challenge_auth_policy import _enforce_tls, _update_challenge

if TYPE_CHECKING:
    from typing import Optional
    from azure.core.credentials import AccessToken
    from azure.core.credentials_async import AsyncTokenCredential
    from azure.core.pipeline import PipelineRequest, PipelineResponse


class AsyncChallengeAuthPolicy(AsyncBearerTokenCredentialPolicy):
    """Policy for handling HTTP authentication challenges.

    :param credential: An object which can provide an access token for the vault, such as a credential from
        :mod:`azure.identity.aio`
    :type credential: :class:`~azure.core.credentials_async.AsyncTokenCredential`
    """

    def __init__(self, credential: "AsyncTokenCredential", *scopes: str, **kwargs) -> None:
        super().__init__(credential, *scopes, **kwargs)
        self._credential = credential
        self._token: "Optional[AccessToken]" = None
        self._verify_challenge_resource = kwargs.pop("verify_challenge_resource", True)

    async def on_request(self, request: "PipelineRequest") -> None:
        _enforce_tls(request)
        challenge = ChallengeCache.get_challenge_for_url(request.http_request.url)
        if challenge:
            # Note that if the vault has moved to a new tenant since our last request for it, this request will fail.
            if self._need_new_token():
                # azure-identity credentials require an AADv2 scope but the challenge may specify an AADv1 resource
                scope = challenge.get_scope() or challenge.get_resource() + "/.default"
                self._token = await self._credential.get_token(scope, tenant_id=challenge.tenant_id)

            # ignore mypy's warning -- although self._token is Optional, get_token raises when it fails to get a token
            request.http_request.headers["Authorization"] = f"Bearer {self._token.token}"  # type: ignore
            return

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
            # azure-identity credentials require an AADv2 scope but the challenge may specify an AADv1 resource
            scope = challenge.get_scope() or challenge.get_resource() + "/.default"
        except ValueError:
            return False

        if self._verify_challenge_resource:
            resource_domain = urlparse(scope).netloc
            if not resource_domain:
                raise ValueError(f"The challenge contains invalid scope '{scope}'.")

            request_domain = urlparse(request.http_request.url).netloc
            if not request_domain.lower().endswith(f".{resource_domain.lower()}"):
                raise ValueError(
                    f"The challenge resource '{resource_domain}' does not match the requested domain. Pass "
                    "`verify_challenge_resource=False` to your client's constructor to disable this verification. "
                    "See https://aka.ms/azsdk/blog/vault-uri for more information."
                )

        body = request.context.pop("key_vault_request_data", None)
        request.http_request.set_text_body(body)  # no-op when text is None

        # The tenant parsed from AD FS challenges is "adfs"; we don't actually need a tenant for AD FS authentication
        # For AD FS we skip cross-tenant authentication per https://github.com/Azure/azure-sdk-for-python/issues/28648
        if challenge.tenant_id and challenge.tenant_id.lower().endswith("adfs"):
            await self.authorize_request(request, scope)
        else:
            await self.authorize_request(request, scope, tenant_id=challenge.tenant_id)

        return True

    def _need_new_token(self) -> bool:
        return not self._token or self._token.expires_on - time.time() < 300
