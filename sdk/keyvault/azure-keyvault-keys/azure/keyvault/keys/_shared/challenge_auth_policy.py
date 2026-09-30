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
from typing import Any, cast, Optional, Tuple, Union
from urllib.parse import urlparse

from azure.core.credentials import (
    AccessToken,
    AccessTokenInfo,
    TokenCredential,
    TokenProvider,
    TokenRequestOptions,
    SupportsTokenInfo,
)
from azure.core.exceptions import ServiceRequestError
from azure.core.pipeline import PipelineRequest, PipelineResponse
from azure.core.pipeline.policies import BearerTokenCredentialPolicy
from azure.core.rest import HttpRequest, HttpResponse

from .http_challenge import HttpChallenge
from . import http_challenge_cache as ChallengeCache


# Key under which the original request is stashed on the per-request pipeline context during the challenge flow.
# Storing this per-request (rather than on the policy instance) prevents the body of one request from leaking into a
# subsequent request made by the same client.
_REQUEST_COPY_KEY = "key_vault_request_copy"
_CHALLENGE_INFO_KEY = "key_vault_challenge_info"
_ChallengeInfo = Tuple[str, str, Optional[str]]


def _enforce_tls(request: PipelineRequest) -> None:
    if not request.http_request.url.lower().startswith("https"):
        raise ServiceRequestError(
            "Bearer token authentication is not permitted for non-TLS protected (non-https) URLs."
        )


def _has_claims(challenge: str) -> bool:
    """Check if a challenge header contains claims.

    :param challenge: The challenge header to check.
    :type challenge: str

    :returns: True if the challenge contains claims; False otherwise.
    :rtype: bool
    """
    # Split the challenge into its scheme and parameters, then check if any parameter contains claims
    parameters = challenge.strip().partition(" ")[2]
    return any("claims=" in item for item in parameters.split(","))


def _update_challenge(request: PipelineRequest, challenger: PipelineResponse) -> HttpChallenge:
    """Parse challenge from a challenge response and return it.

    :param request: The pipeline request that prompted the challenge response.
    :type request: ~azure.core.pipeline.PipelineRequest
    :param challenger: The pipeline response containing the authentication challenge.
    :type challenger: ~azure.core.pipeline.PipelineResponse

    :returns: An HttpChallenge object representing the authentication challenge.
    :rtype: HttpChallenge
    """

    challenge_header = challenger.http_response.headers.get("WWW-Authenticate")
    # HttpChallenge expects a scheme followed by a space and parameters.
    if not challenge_header or " " not in challenge_header.strip():
        raise ValueError("Invalid challenge header")
    challenge = HttpChallenge(
        request.http_request.url,
        challenge_header,
        response_headers=challenger.http_response.headers,
    )
    return challenge


def _validate_challenge_resource(scope: str, request_url: str) -> None:
    """Verify the challenge resource and remove cached authentication information on failure.

    :param str scope: The scope derived from the challenge.
    :param str request_url: The URL being authenticated.
    """
    try:
        resource_domain = urlparse(scope).netloc
        if not resource_domain:
            raise ValueError(f"The challenge contains invalid scope '{scope}'.")

        # Compare authorities using the HTTPS request cache's default-port equivalence. The scope's scheme
        # doesn't affect the suffix check, just as it didn't before normalization was needed for cache hits.
        resource_key = ChallengeCache._get_cache_key("https://" + resource_domain)  # pylint:disable=protected-access
        request_domain = ChallengeCache._get_cache_key(request_url)  # pylint:disable=protected-access
        if not request_domain.lower().endswith(f".{resource_key.lower()}"):
            raise ValueError(
                f"The challenge resource '{resource_domain}' does not match the requested domain. Pass "
                "`verify_challenge_resource=False` to your client's constructor to disable this verification. "
                "See https://aka.ms/azsdk/blog/vault-uri for more information."
            )
    except ValueError:
        ChallengeCache.remove_challenge_for_url(request_url)
        raise


def _request_origin(url: str) -> str:
    # Use the same authority equivalence as the cache, but don't share authentication across schemes.
    authority = ChallengeCache._get_cache_key(url).lower()  # pylint:disable=protected-access
    return urlparse(url).scheme.lower() + "://" + authority


def _get_challenge_info(
    request_url: str, previous: Optional[_ChallengeInfo], verify_resource: bool
) -> Tuple[Optional[str], Optional[str]]:
    if previous and previous[0] == _request_origin(request_url):
        scope, tenant = previous[1:]
    else:
        cached = ChallengeCache.get_challenge_for_url(request_url)
        if not cached or _request_origin(cached.source_uri) != _request_origin(request_url):
            return None, None
        scope = cached.get_scope() or cached.get_resource() + "/.default"
        tenant = cached.tenant_id
    if verify_resource:
        _validate_challenge_resource(scope, request_url)
    return scope, tenant


def _restore_request(request: PipelineRequest) -> None:
    request_copy = request.context.pop(_REQUEST_COPY_KEY, None)
    if request_copy and request_copy.method == request.http_request.method:
        # A redirect may change the destination or method while discovery is in progress.
        request_copy.url = request.http_request.url
        request.http_request = request_copy


class ChallengeAuthPolicy(BearerTokenCredentialPolicy):
    """Policy for handling HTTP authentication challenges.

    :param credential: An object which can provide an access token for the vault, such as a credential from
        :mod:`azure.identity`
    :type credential: ~azure.core.credentials.TokenProvider
    :param str scopes: Lets you specify the type of access needed.
    """

    def __init__(self, credential: TokenProvider, *scopes: str, **kwargs: Any) -> None:
        # Pass `enable_cae` so `enable_cae=True` is always passed through self.authorize_request
        super(ChallengeAuthPolicy, self).__init__(credential, *scopes, enable_cae=True, **kwargs)
        self._credential: TokenProvider = credential
        self._token: Optional[Union["AccessToken", "AccessTokenInfo"]] = None
        self._verify_challenge_resource = kwargs.pop("verify_challenge_resource", True)

    def send(self, request: PipelineRequest[HttpRequest]) -> PipelineResponse[HttpRequest, HttpResponse]:
        """Authorize request with a bearer token and send it to the next policy.

        We implement this method to account for the valid scenario where a Key Vault authentication challenge is
        immediately followed by a CAE claims challenge. The base class's implementation would return the second 401 to
        the caller, but we should handle that second challenge as well (and only return any third 401 response).

        :param request: The pipeline request object
        :type request: ~azure.core.pipeline.PipelineRequest

        :return: The pipeline response object
        :rtype: ~azure.core.pipeline.PipelineResponse
        """
        self.on_request(request)
        try:
            response = self.next.send(request)
        except Exception:  # pylint:disable=broad-except
            self.on_exception(request)
            raise

        self.on_response(request, response)
        if response.http_response.status_code == 401:
            return self.handle_challenge_flow(request, response)
        return response

    def handle_challenge_flow(
        self,
        request: PipelineRequest[HttpRequest],
        response: PipelineResponse[HttpRequest, HttpResponse],
        consecutive_challenge: bool = False,
    ) -> PipelineResponse[HttpRequest, HttpResponse]:
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
            # If the previous challenge was a KV challenge and this one is too, return the 401
            claims_challenge = _has_claims(response.http_response.headers["WWW-Authenticate"])
            if consecutive_challenge and not claims_challenge:
                ChallengeCache.remove_challenge_for_url(request.http_request.url)
                return response

            request_authorized = self.on_challenge(request, response)
            if request_authorized:
                # if we receive a challenge response, we retrieve a new token
                # which matches the new target. In this case, we don't want to remove
                # token from the request so clear the 'insecure_domain_change' tag
                request.context.options.pop("insecure_domain_change", False)
                try:
                    response = self.next.send(request)
                except Exception:  # pylint:disable=broad-except
                    self.on_exception(request)
                    raise

                # If consecutive_challenge == True, this could be a third consecutive 401
                if response.http_response.status_code == 401 and not consecutive_challenge:
                    # If the previous challenge wasn't from CAE, we can try this function one more time
                    if not claims_challenge:
                        return self.handle_challenge_flow(request, response, consecutive_challenge=True)
                self.on_response(request, response)
        return response

    def on_request(self, request: PipelineRequest) -> None:
        _enforce_tls(request)
        request.context.pop(_CHALLENGE_INFO_KEY, None)
        challenge = ChallengeCache.get_challenge_for_url(request.http_request.url)
        if challenge:
            # A shared cache entry may have been stored by a client that disabled resource verification.
            scope = challenge.get_scope() or challenge.get_resource() + "/.default"
            if self._verify_challenge_resource:
                _validate_challenge_resource(scope, request.http_request.url)
            request.context[_CHALLENGE_INFO_KEY] = (
                _request_origin(request.http_request.url),
                scope,
                challenge.tenant_id,
            )
            # Note that if the vault has moved to a new tenant since our last request for it, this request will fail.
            if self._need_new_token:
                self._request_kv_token(scope, challenge)

            _restore_request(request)
            bearer_token = cast(Union["AccessToken", "AccessTokenInfo"], self._token).token
            request.http_request.headers["Authorization"] = f"Bearer {bearer_token}"
            return

        # else: discover authentication information by eliciting a challenge from Key Vault. Remove any request data,
        # saving it for later. Key Vault will reject the request as unauthorized and respond with a challenge.
        # on_challenge will parse that challenge, use the original request including the body, authorize the
        # request, and tell super to send it again.
        # The original request is stashed on the request's context (per-request), so it cannot leak into a later
        # request made by the same client. A restored request must be stripped again if the cache is evicted on retry.
        request.http_request.headers.pop("Authorization", None)
        if request.http_request.content:
            request.context[_REQUEST_COPY_KEY] = request.http_request
            bodiless_request = HttpRequest(
                method=request.http_request.method,
                url=request.http_request.url,
                headers=deepcopy(request.http_request.headers),
            )
            bodiless_request.headers["Content-Length"] = "0"
            request.http_request = bodiless_request

    def on_challenge(self, request: PipelineRequest, response: PipelineResponse) -> bool:
        previous_challenge = request.context.pop(_CHALLENGE_INFO_KEY, None)
        try:
            challenge = _update_challenge(request, response)
        except ValueError:
            ChallengeCache.remove_challenge_for_url(request.http_request.url)
            return False

        if challenge.claims:
            # Another request may have evicted or replaced the cache while this request was in flight.
            old_scope, old_tenant = _get_challenge_info(
                request.http_request.url, previous_challenge, self._verify_challenge_resource
            )
            if old_scope:
                challenge._parameters["scope"] = old_scope  # pylint:disable=protected-access
                challenge.tenant_id = old_tenant
        # azure-identity credentials require an AADv2 scope but the challenge may specify an AADv1 resource
        scope = challenge.get_scope() or challenge.get_resource() + "/.default"
        if self._verify_challenge_resource:
            _validate_challenge_resource(scope, request.http_request.url)

        ChallengeCache.set_challenge_for_url(request.http_request.url, challenge)
        request.context[_CHALLENGE_INFO_KEY] = (_request_origin(request.http_request.url), scope, challenge.tenant_id)

        # If we stashed the original request in on_request, use it now to send along the original body content
        _restore_request(request)

        # The tenant parsed from AD FS challenges is "adfs"; we don't actually need a tenant for AD FS authentication
        # For AD FS we skip cross-tenant authentication per https://github.com/Azure/azure-sdk-for-python/issues/28648
        if challenge.tenant_id and challenge.tenant_id.lower().endswith("adfs"):
            self.authorize_request(request, scope, claims=challenge.claims)
        else:
            self.authorize_request(request, scope, claims=challenge.claims, tenant_id=challenge.tenant_id)

        return True

    @property
    def _need_new_token(self) -> bool:
        now = time.time()
        refresh_on = getattr(self._token, "refresh_on", None)
        return not self._token or (refresh_on and refresh_on <= now) or self._token.expires_on - now < 300

    def _request_kv_token(self, scope: str, challenge: HttpChallenge) -> None:
        """Implementation of BearerTokenCredentialPolicy's _request_token method, but specific to Key Vault.

        :param str scope: The scope for which to request a token.
        :param challenge: The challenge for the request being made.
        :type challenge: HttpChallenge
        """
        # Exclude tenant for AD FS authentication
        exclude_tenant = challenge.tenant_id and challenge.tenant_id.lower().endswith("adfs")
        # The SupportsTokenInfo protocol needs TokenRequestOptions for token requests instead of kwargs
        if hasattr(self._credential, "get_token_info"):
            options: TokenRequestOptions = {"enable_cae": True}
            if challenge.tenant_id and not exclude_tenant:
                options["tenant_id"] = challenge.tenant_id
            self._token = cast(SupportsTokenInfo, self._credential).get_token_info(scope, options=options)
        else:
            if exclude_tenant:
                self._token = self._credential.get_token(scope, enable_cae=True)
            else:
                self._token = cast(TokenCredential, self._credential).get_token(
                    scope, tenant_id=challenge.tenant_id, enable_cae=True
                )
