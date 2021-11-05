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

    def __init__(self, *args, **kwargs):
        # type: (*Any, **Any) -> None
        self._last_tenant_id = None  # type: Optional[str]
        super(ChallengeAuthPolicy, self).__init__(*args, **kwargs)

    def on_request(self, request):
        # type: (PipelineRequest) -> None
        challenge = ChallengeCache.get_challenge_for_url(request.http_request.url)
        if challenge:
            if self._last_tenant_id == challenge.tenant_id:
                # Super can handle this. Its cached token, if any, probably isn't from a different tenant, and
                # it knows the scope to request for a new token. Note that if the vault has moved to a new
                # tenant since our last request for it, this request will fail.
                super(ChallengeAuthPolicy, self).on_request(request)
            else:
                # acquire a new token because this vault is in a different tenant
                self.authorize_request(request, *self._scopes, tenant_id=challenge.tenant_id)
            return

        # else: discover authentication information by eliciting a challenge from Key Vault. Remove any request data,
        # saving it for later. Key Vault will reject the request as unauthorized and respond with a challenge.
        # on_challenge will parse that challenge, reattach any body removed here, authorize the request, and tell
        # super to send it again.
        _enforce_tls(request)
        if request.http_request.body:
            request.context["key_vault_request_data"] = request.http_request.body
            request.http_request.set_json_body(None)
            request.http_request.headers["Content-Length"] = "0"

    def on_challenge(self, request, response):
        # type: (PipelineRequest, PipelineResponse) -> bool
        try:
            challenge = _update_challenge(request, response)
            scope = challenge.get_scope() or challenge.get_resource() + "/.default"
        except ValueError:
            return False

        self._scopes = (scope,)

        body = request.context.pop("key_vault_request_data", None)
        request.http_request.set_text_body(body)  # no-op when text is None

        self._last_tenant_id = challenge.tenant_id
        self.authorize_request(request, *self._scopes, tenant_id=challenge.tenant_id)

        return True
