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

from azure.core.exceptions import ServiceRequestError
from azure.core.pipeline import PipelineRequest
from azure.core.pipeline.policies import BearerTokenCredentialPolicy

from .http_challenge import HttpChallenge
from . import http_challenge_cache as ChallengeCache

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    from typing import Any, Optional
    from azure.core.credentials import AccessToken, TokenCredential
    from azure.core.pipeline import PipelineResponse


def _enforce_tls(request):
    # type: (PipelineRequest) -> None
    if not request.http_request.url.lower().startswith("https"):
        raise ServiceRequestError(
            "Bearer token authentication is not permitted for non-TLS protected (non-https) URLs."
        )


def _update_challenge(request, challenger):
    # type: (PipelineRequest, PipelineResponse) -> HttpChallenge
    """parse challenge from challenger, cache it, return it"""

    challenge = HttpChallenge(
        request.http_request.url,
        challenger.http_response.headers.get("WWW-Authenticate"),
        response_headers=challenger.http_response.headers,
    )
    ChallengeCache.set_challenge_for_url(request.http_request.url, challenge)
    return challenge


class ChallengeAuthPolicy(BearerTokenCredentialPolicy):
    """policy for handling HTTP authentication challenges"""

    def __init__(self, credential, *scopes, **kwargs):
        # type: (TokenCredential, *str, **Any) -> None
        super(ChallengeAuthPolicy, self).__init__(credential, *scopes, **kwargs)
        self._credential = credential
        self._token = None  # type: Optional[AccessToken]

    def on_request(self, request):
        # type: (PipelineRequest) -> None
        _enforce_tls(request)
        challenge = ChallengeCache.get_challenge_for_url(request.http_request.url)
        if challenge:
            # Note that if the vault has moved to a new tenant since our last request for it, this request will fail.
            if self._need_new_token:
                # azure-identity credentials require an AADv2 scope but the challenge may specify an AADv1 resource
                scope = challenge.get_scope() or challenge.get_resource() + "/.default"
                self._token = self._credential.get_token(scope, tenant_id=challenge.tenant_id)

            # ignore mypy's warning -- although self._token is Optional, get_token raises when it fails to get a token
            request.http_request.headers["Authorization"] = "Bearer {}".format(self._token.token)  # type: ignore
            return

        # else: discover authentication information by eliciting a challenge from Key Vault. Remove any request data,
        # saving it for later. Key Vault will reject the request as unauthorized and respond with a challenge.
        # on_challenge will parse that challenge, reattach any body removed here, authorize the request, and tell
        # super to send it again.
        if request.http_request.body:
            request.context["key_vault_request_data"] = request.http_request.body
            request.http_request.set_json_body(None)
            request.http_request.headers["Content-Length"] = "0"

    def on_challenge(self, request, response):
        # type: (PipelineRequest, PipelineResponse) -> bool
        try:
            challenge = _update_challenge(request, response)
            # azure-identity credentials require an AADv2 scope but the challenge may specify an AADv1 resource
            scope = challenge.get_scope() or challenge.get_resource() + "/.default"
        except ValueError:
            return False

        body = request.context.pop("key_vault_request_data", None)
        request.http_request.set_text_body(body)  # no-op when text is None
        self.authorize_request(request, scope, tenant_id=challenge.tenant_id)

        return True

    @property
    def _need_new_token(self):
        # type: () -> bool
        return not self._token or self._token.expires_on - time.time() < 300
