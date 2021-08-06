# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import abc
import base64
import json
import time
from uuid import uuid4

import six
from msal import TokenCache

from azure.core.pipeline.policies import ContentDecodePolicy
from azure.core.pipeline.transport import HttpRequest
from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError
from . import get_default_authority, normalize_authority
from .._internal import resolve_tenant

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

try:
    ABC = abc.ABC
except AttributeError:  # Python 2.7, abc exists, but not ABC
    ABC = abc.ABCMeta("ABC", (object,), {"__slots__": ()})  # type: ignore

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any, Iterable, List, Optional, Union
    from azure.core.pipeline import AsyncPipeline, Pipeline, PipelineResponse
    from azure.core.pipeline.policies import AsyncHTTPPolicy, HTTPPolicy, SansIOHTTPPolicy
    from azure.core.pipeline.transport import AsyncHttpTransport, HttpTransport
    from .._internal import AadClientCertificate

    PipelineType = Union[AsyncPipeline, Pipeline]
    PolicyType = Union[AsyncHTTPPolicy, HTTPPolicy, SansIOHTTPPolicy]
    TransportType = Union[AsyncHttpTransport, HttpTransport]


class AadClientBase(ABC):
    _POST = ["POST"]

    def __init__(
        self, tenant_id, client_id, authority=None, cache=None, allow_multitenant_authentication=False, **kwargs
    ):
        # type: (str, str, Optional[str], Optional[TokenCache], bool, **Any) -> None
        self._authority = normalize_authority(authority) if authority else get_default_authority()

        self._tenant_id = tenant_id
        self._allow_multitenant = allow_multitenant_authentication

        self._cache = cache or TokenCache()
        self._client_id = client_id
        self._pipeline = self._build_pipeline(**kwargs)

    def get_cached_access_token(self, scopes, **kwargs):
        # type: (Iterable[str], **Any) -> Optional[AccessToken]
        tenant = resolve_tenant(self._tenant_id, self._allow_multitenant, **kwargs)
        tokens = self._cache.find(
            TokenCache.CredentialType.ACCESS_TOKEN,
            target=list(scopes),
            query={"client_id": self._client_id, "realm": tenant},
        )
        for token in tokens:
            expires_on = int(token["expires_on"])
            if expires_on > int(time.time()):
                return AccessToken(token["secret"], expires_on)
        return None

    def get_cached_refresh_tokens(self, scopes):
        # type: (Iterable[str]) -> List[dict]
        """Assumes all cached refresh tokens belong to the same user"""
        return self._cache.find(TokenCache.CredentialType.REFRESH_TOKEN, target=list(scopes))

    @abc.abstractmethod
    def obtain_token_by_authorization_code(self, scopes, code, redirect_uri, client_secret=None, **kwargs):
        pass

    @abc.abstractmethod
    def obtain_token_by_jwt_assertion(self, scopes, assertion, **kwargs):
        pass

    @abc.abstractmethod
    def obtain_token_by_client_certificate(self, scopes, certificate, **kwargs):
        pass

    @abc.abstractmethod
    def obtain_token_by_client_secret(self, scopes, secret, **kwargs):
        pass

    @abc.abstractmethod
    def obtain_token_by_refresh_token(self, scopes, refresh_token, **kwargs):
        pass

    @abc.abstractmethod
    def _build_pipeline(self, **kwargs):
        pass

    def _process_response(self, response, request_time):
        # type: (PipelineResponse, int) -> AccessToken
        content = response.context.get(
            ContentDecodePolicy.CONTEXT_NAME
        ) or ContentDecodePolicy.deserialize_from_http_generics(response.http_response)

        if response.http_request.body.get("grant_type") == "refresh_token":
            if content.get("error") == "invalid_grant":
                # the request's refresh token is invalid -> evict it from the cache
                cache_entries = self._cache.find(
                    TokenCache.CredentialType.REFRESH_TOKEN,
                    query={"secret": response.http_request.body["refresh_token"]},
                )
                for invalid_token in cache_entries:
                    self._cache.remove_rt(invalid_token)
            if "refresh_token" in content:
                # AAD returned a new refresh token -> update the cache entry
                cache_entries = self._cache.find(
                    TokenCache.CredentialType.REFRESH_TOKEN,
                    query={"secret": response.http_request.body["refresh_token"]},
                )
                # If the old token is in multiple cache entries, the cache is in a state we don't
                # expect or know how to reason about, so we update nothing.
                if len(cache_entries) == 1:
                    self._cache.update_rt(cache_entries[0], content["refresh_token"])
                    del content["refresh_token"]  # prevent caching a redundant entry

        _raise_for_error(response, content)

        if "expires_on" in content:
            expires_on = int(content["expires_on"])
        elif "expires_in" in content:
            expires_on = request_time + int(content["expires_in"])
        else:
            _scrub_secrets(content)
            raise ClientAuthenticationError(
                message="Unexpected response from Azure Active Directory: {}".format(content)
            )

        token = AccessToken(content["access_token"], expires_on)

        # caching is the final step because 'add' mutates 'content'
        self._cache.add(
            event={
                "client_id": self._client_id,
                "response": content,
                "scope": response.http_request.body["scope"].split(),
                "token_endpoint": response.http_request.url,
            },
            now=request_time,
        )

        return token

    def _get_auth_code_request(self, scopes, code, redirect_uri, client_secret=None, **kwargs):
        # type: (Iterable[str], str, str, Optional[str], **Any) -> HttpRequest
        data = {
            "client_id": self._client_id,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
            "scope": " ".join(scopes),
        }
        if client_secret:
            data["client_secret"] = client_secret

        request = self._post(data, **kwargs)
        return request

    def _get_jwt_assertion_request(self, scopes, assertion, **kwargs):
        # type: (Iterable[str], str, **Any) -> HttpRequest
        data = {
            "client_assertion": assertion,
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_id": self._client_id,
            "grant_type": "client_credentials",
            "scope": " ".join(scopes),
        }

        request = self._post(data, **kwargs)
        return request

    def _get_client_certificate_request(self, scopes, certificate, **kwargs):
        # type: (Iterable[str], AadClientCertificate, **Any) -> HttpRequest
        now = int(time.time())
        header = six.ensure_binary(
            json.dumps({"typ": "JWT", "alg": "RS256", "x5t": certificate.thumbprint}), encoding="utf-8"
        )
        payload = six.ensure_binary(
            json.dumps(
                {
                    "jti": str(uuid4()),
                    "aud": self._get_token_url(**kwargs),
                    "iss": self._client_id,
                    "sub": self._client_id,
                    "nbf": now,
                    "exp": now + (60 * 30),
                }
            ),
            encoding="utf-8",
        )
        jws = base64.urlsafe_b64encode(header) + b"." + base64.urlsafe_b64encode(payload)
        signature = certificate.sign(jws)
        jwt_bytes = jws + b"." + base64.urlsafe_b64encode(signature)
        assertion = jwt_bytes.decode("utf-8")

        return self._get_jwt_assertion_request(scopes, assertion, **kwargs)

    def _get_client_secret_request(self, scopes, secret, **kwargs):
        # type: (Iterable[str], str, **Any) -> HttpRequest
        data = {
            "client_id": self._client_id,
            "client_secret": secret,
            "grant_type": "client_credentials",
            "scope": " ".join(scopes),
        }
        request = self._post(data, **kwargs)
        return request

    def _get_refresh_token_request(self, scopes, refresh_token, **kwargs):
        # type: (Iterable[str], str, **Any) -> HttpRequest
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "scope": " ".join(scopes),
            "client_id": self._client_id,
            "client_info": 1,  # request AAD include home_account_id in its response
        }
        request = self._post(data, **kwargs)
        return request

    def _get_token_url(self, **kwargs):
        # type: (**Any) -> str
        tenant = resolve_tenant(self._tenant_id, self._allow_multitenant, **kwargs)
        return "/".join((self._authority, tenant, "oauth2/v2.0/token"))

    def _post(self, data, **kwargs):
        # type: (dict, **Any) -> HttpRequest
        url = self._get_token_url(**kwargs)
        return HttpRequest("POST", url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})


def _scrub_secrets(response):
    # type: (dict) -> None
    for secret in ("access_token", "refresh_token"):
        if secret in response:
            response[secret] = "***"


def _raise_for_error(response, content):
    # type: (PipelineResponse, dict) -> None
    if "error" not in content:
        return

    _scrub_secrets(content)
    if "error_description" in content:
        message = "Azure Active Directory error '({}) {}'".format(content["error"], content["error_description"])
    else:
        message = "Azure Active Directory error '{}'".format(content)
    raise ClientAuthenticationError(message=message, response=response.http_response)
