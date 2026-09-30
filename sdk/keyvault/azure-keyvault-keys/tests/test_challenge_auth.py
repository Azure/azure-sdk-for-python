# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Tests for the HTTP challenge authentication implementation. These tests aren't parallelizable, because
the challenge cache is global to the process.
"""

import base64
import functools
from itertools import product
import os
import time
from unittest.mock import Mock, patch
from urllib.parse import urlparse
from uuid import uuid4

from devtools_testutils import recorded_by_proxy

import pytest
from azure.core.credentials import AccessToken, AccessTokenInfo
from azure.core.exceptions import ServiceRequestError
from azure.core.pipeline import Pipeline, PipelineContext, PipelineRequest, PipelineResponse
from azure.core.pipeline.policies import RedirectPolicy, RetryPolicy, SansIOHTTPPolicy
from azure.core.rest import HttpRequest
from azure.keyvault.keys import KeyClient
from azure.keyvault.keys._shared import ChallengeAuthPolicy, HttpChallenge, HttpChallengeCache
from azure.keyvault.keys._shared.client_base import DEFAULT_VERSION

from _shared.helpers import Request, mock_response, validating_transport
from _shared.test_case import KeyVaultTestCase
from _test_case import KeysClientPreparer, get_decorator
from _keys_test_case import KeysTestCase

only_default_version = get_decorator(api_versions=[DEFAULT_VERSION])

TOKEN_TYPES = [AccessToken, AccessTokenInfo]


# These domains include the public/China/US Government cloud tables in eng/common/TestResources/clouds,
# Germany, Managed HSM, and arbitrary Azure Stack/custom domains supported by the suffix validator.
CACHE_RESOURCE_DOMAINS = [
    "vault.azure.net",
    "vault.azure.cn",
    "vault.usgovcloudapi.net",
    "vault.microsoftazure.de",
    "managedhsm.azure.net",
    "vault.stack.example",
    "vault.custom.example",
]
INVALID_CHALLENGE_HEADERS = [
    None,
    "",
    " ",
    "Bearer",
    "Bearer resource=https://vault.azure.net",
    'Bearer authorization="https://authority.net/tenant", resource=https://other.example',
    'Bearer authorization="https://authority.net/tenant", scope=invalid',
    'Bearer authorization="https://authority.net/tenant", scope=https://[invalid',
]


@pytest.mark.parametrize("token_type", TOKEN_TYPES)
@pytest.mark.parametrize("cached_token", [False, True])
@pytest.mark.parametrize(
    "request_port,resource",
    [
        ("", "https://other.example"),
        ("", "invalid"),
        ("", "https://vault.azure.net:8443"),
        (":8443", "https://vault.azure.net"),
        (":8443", "https://vault.azure.net:443"),
        (":443", "https://vault.azure.net:8443"),
    ],
)
def test_cached_challenge_resource_is_verified(token_type, cached_token, request_port, resource):
    url = get_random_url().replace(".vault.azure.net/", f".vault.azure.net{request_port}/")
    HttpChallengeCache.set_challenge_for_url(
        url, HttpChallenge(url, f'Bearer authorization="https://authority.net/tenant", resource={resource}')
    )
    credential = Mock(
        spec_set=["get_token", "get_token_info"],
        get_token=Mock(side_effect=AssertionError("unexpected token request")),
        get_token_info=Mock(side_effect=AssertionError("unexpected token request")),
    )
    policy = ChallengeAuthPolicy(credential)
    if cached_token:
        policy._token = token_type("cached-token", time.time() + 3600)
    transport = Mock(send=Mock(side_effect=AssertionError("unexpected transport call")))
    request = HttpRequest("POST", url, content=b"secret")

    with pytest.raises(ValueError):
        Pipeline(policies=[policy], transport=transport).run(request)

    assert "Authorization" not in request.headers
    credential.get_token.assert_not_called()
    credential.get_token_info.assert_not_called()
    transport.send.assert_not_called()
    assert HttpChallengeCache.get_challenge_for_url(url) is None

    follow_up = PipelineRequest(HttpRequest("POST", url, content=b"next secret"), PipelineContext(None))
    policy.on_request(follow_up)
    response = PipelineResponse(
        follow_up.http_request, Mock(status_code=401, headers={"WWW-Authenticate": "Bearer"}), follow_up.context
    )
    assert policy.on_challenge(follow_up, response) is False
    assert "Authorization" not in follow_up.http_request.headers
    assert not follow_up.http_request.body
    assert follow_up.http_request.headers["Content-Length"] == "0"
    credential.get_token.assert_not_called()
    credential.get_token_info.assert_not_called()


@pytest.mark.parametrize("cached_token", [False, True])
def test_opt_out_cache_is_not_trusted_by_strict_policy(cached_token):
    url = get_random_url()
    header = 'Bearer authorization="https://authority.net/tenant", resource=https://other.example'
    credential = Mock(spec_set=["get_token"], get_token=Mock(return_value=AccessToken("opt-out", time.time() + 3600)))
    transport = Mock(
        send=Mock(
            side_effect=[
                Mock(status_code=401, headers={"WWW-Authenticate": header}),
                Mock(status_code=200),
                Mock(status_code=200),
            ]
        )
    )
    pipeline = Pipeline(
        policies=[ChallengeAuthPolicy(credential, verify_challenge_resource=False)], transport=transport
    )
    pipeline.run(HttpRequest("GET", url))
    pipeline.run(HttpRequest("GET", url))
    assert transport.send.call_count == 3
    credential.get_token.assert_called_once()
    assert HttpChallengeCache.get_challenge_for_url(url)

    strict_credential = Mock(
        spec_set=["get_token"], get_token=Mock(side_effect=AssertionError("unexpected token request"))
    )
    strict_policy = ChallengeAuthPolicy(strict_credential)
    if cached_token:
        strict_policy._token = AccessToken("strict-token", time.time() + 3600)
    strict_transport = Mock(send=Mock(side_effect=AssertionError("unexpected transport call")))
    with pytest.raises(ValueError):
        Pipeline(policies=[strict_policy], transport=strict_transport).run(HttpRequest("GET", url))
    strict_credential.get_token.assert_not_called()
    strict_transport.send.assert_not_called()
    assert HttpChallengeCache.get_challenge_for_url(url) is None


@pytest.mark.parametrize("header", INVALID_CHALLENGE_HEADERS)
def test_rejected_response_clears_cached_challenge(header):
    url = get_random_url()
    credential = Mock(spec_set=["get_token"])
    policy = ChallengeAuthPolicy(credential)
    request = PipelineRequest(HttpRequest("POST", url, content=b"secret"), PipelineContext(None))
    policy.on_request(request)
    assert not request.http_request.body
    HttpChallengeCache.set_challenge_for_url(
        url, HttpChallenge(url, 'Bearer authorization="https://authority.net/tenant", resource=https://vault.azure.net')
    )
    response = PipelineResponse(
        request.http_request, Mock(status_code=401, headers={"WWW-Authenticate": header}), request.context
    )
    if header and "authorization=" in header:
        with pytest.raises(ValueError):
            policy.on_challenge(request, response)
    else:
        assert policy.on_challenge(request, response) is False
    assert HttpChallengeCache.get_challenge_for_url(url) is None
    assert "Authorization" not in request.http_request.headers
    assert not request.http_request.body
    credential.get_token.assert_not_called()

    def send(fresh_request):
        assert "Authorization" not in fresh_request.headers
        assert not fresh_request.body
        assert fresh_request.headers["Content-Length"] == "0"
        return Mock(status_code=401, headers={})

    fresh = Pipeline(policies=[ChallengeAuthPolicy(credential)], transport=Mock(send=send))
    assert fresh.run(HttpRequest("POST", url, content=b"new secret")).http_response.status_code == 401
    credential.get_token.assert_not_called()


@pytest.mark.parametrize("header", ["", " ", "Bearer", "Bearer resource=https://vault.azure.net"])
@pytest.mark.parametrize("consecutive", [False, True])
def test_malformed_challenge_flow_clears_cache(header, consecutive):
    url = get_random_url()
    HttpChallengeCache.set_challenge_for_url(
        url, HttpChallenge(url, 'Bearer authorization="https://authority.net/tenant", resource=https://vault.azure.net')
    )
    credential = Mock(spec_set=["get_token"])
    policy = ChallengeAuthPolicy(credential)
    request = PipelineRequest(HttpRequest("GET", url), PipelineContext(None))
    response = PipelineResponse(
        request.http_request, Mock(status_code=401, headers={"WWW-Authenticate": header}), request.context
    )
    assert policy.handle_challenge_flow(request, response, consecutive_challenge=consecutive) is response
    assert HttpChallengeCache.get_challenge_for_url(url) is None
    credential.get_token.assert_not_called()


def test_cae_invalid_inherited_scope_clears_cache():
    url = get_random_url()
    HttpChallengeCache.set_challenge_for_url(
        url,
        HttpChallenge(url, 'Bearer authorization="https://authority.net/tenant", scope=https://other.example/.default'),
    )
    credential = Mock(spec_set=["get_token"])
    request = PipelineRequest(HttpRequest("GET", url), PipelineContext(None))
    response = PipelineResponse(
        request.http_request,
        Mock(
            status_code=401,
            headers={"WWW-Authenticate": 'Bearer authorization="https://authority.net/", claims="e30="'},
        ),
        request.context,
    )
    with pytest.raises(ValueError):
        ChallengeAuthPolicy(credential).on_challenge(request, response)
    assert HttpChallengeCache.get_challenge_for_url(url) is None
    credential.get_token.assert_not_called()


@pytest.mark.parametrize("domain", CACHE_RESOURCE_DOMAINS)
@pytest.mark.parametrize("parameter", ["resource", "scope"])
@pytest.mark.parametrize(
    "request_port,resource_port", [("", ""), (":443", ""), ("", ":443"), (":443", ":443"), (":8443", ":8443")]
)
def test_valid_challenge_cache_reuse(domain, parameter, request_port, resource_port):
    host = f"{uuid4().hex}.{domain}"
    url = f"https://{host}{request_port}/first"
    alias_port = "" if request_port == ":443" else ":443" if not request_port else request_port
    alias = f"https://{host.upper()}{alias_port}/next"
    resource = f"https://{domain.upper()}{resource_port}"
    scope = resource + "/.default"
    header = f'Bearer authorization="https://authority.example/ADFS", {parameter}={scope if parameter == "scope" else resource}'
    credential = Mock(spec_set=["get_token"], get_token=Mock(return_value=AccessToken("token", time.time() + 3600)))
    requests = []

    def send(request):
        requests.append(request)
        if len(requests) == 1:
            assert "Authorization" not in request.headers
            assert not request.body
            return Mock(status_code=401, headers={"WWW-Authenticate": header})
        assert request.headers["Authorization"] == "Bearer token"
        assert request.body == b"body"
        return Mock(status_code=200)

    pipeline = Pipeline(policies=[ChallengeAuthPolicy(credential)], transport=Mock(send=send))
    pipeline.run(HttpRequest("POST", url, content=b"body"))
    pipeline.run(HttpRequest("POST", alias, content=b"body"))
    assert len(requests) == 3
    credential.get_token.assert_called_once_with(scope, claims=None, enable_cae=True)
    # A new policy must also use the cached challenge directly, without another unauthenticated request.
    Pipeline(policies=[ChallengeAuthPolicy(credential)], transport=Mock(send=send)).run(
        HttpRequest("POST", alias, content=b"body")
    )
    assert len(requests) == 4
    assert credential.get_token.call_count == 2
    assert credential.get_token.call_args.kwargs == {"enable_cae": True}
    assert HttpChallengeCache.get_challenge_for_url(alias) is HttpChallengeCache.get_challenge_for_url(url)


def test_cached_cae_scope_and_tenant_refresh():
    url = get_random_url()
    credential = Mock(spec_set=["get_token"], get_token=Mock(return_value=AccessToken("token", time.time() + 3600)))
    policy = ChallengeAuthPolicy(credential)
    request = PipelineRequest(HttpRequest("GET", url), PipelineContext(None))
    scope = "https://vault.azure.net/.default"
    for header, tenant, claims in [
        (f'Bearer authorization="https://authority.net/first", scope={scope}', "first", None),
        ('Bearer authorization="https://authority.net/", claims="e30="', "first", "{}"),
        (f'Bearer authorization="https://authority.net/second", scope={scope}', "second", None),
    ]:
        response = PipelineResponse(
            request.http_request, Mock(status_code=401, headers={"WWW-Authenticate": header}), request.context
        )
        assert policy.on_challenge(request, response)
        credential.get_token.assert_called_with(scope, claims=claims, tenant_id=tenant, enable_cae=True)
    policy._token = None
    policy.on_request(request)
    credential.get_token.assert_called_with(scope, tenant_id="second", enable_cae=True)


@pytest.mark.parametrize(
    "resource",
    [
        "http://vault.azure.net",
        "http://vault.azure.net:443",
        "spn://vault.azure.net",
        "//vault.azure.net",
        "https://vault.azure.net/scope",
    ],
)
def test_cached_resource_syntax_is_preserved(resource):
    url = get_random_url()
    HttpChallengeCache.set_challenge_for_url(
        url, HttpChallenge(url, f'Bearer authorization="https://authority.net/tenant", resource={resource}')
    )
    credential = Mock(spec_set=["get_token"], get_token=Mock(return_value=AccessToken("token", time.time() + 3600)))
    request = PipelineRequest(HttpRequest("GET", url), PipelineContext(None))
    ChallengeAuthPolicy(credential).on_request(request)
    credential.get_token.assert_called_once_with(resource + "/.default", tenant_id="tenant", enable_cae=True)
    assert request.http_request.headers["Authorization"] == "Bearer token"


def test_cache_removal_is_idempotent():
    url = get_random_url()
    alias = url.replace(".vault.azure.net", ".VAULT.AZURE.NET:443")
    HttpChallengeCache.remove_challenge_for_url(url)
    challenge = HttpChallenge(
        url, 'Bearer authorization="https://authority.net/tenant", resource=https://vault.azure.net'
    )
    HttpChallengeCache.set_challenge_for_url(url, challenge)
    HttpChallengeCache.remove_challenge_for_url(alias)
    HttpChallengeCache.remove_challenge_for_url(url)
    HttpChallengeCache.remove_challenge_for_url(alias)
    assert HttpChallengeCache.get_challenge_for_url(url) is None


class TestChallengeAuth(KeyVaultTestCase, KeysTestCase):
    @pytest.mark.parametrize("api_version,is_hsm", only_default_version)
    @KeysClientPreparer()
    @recorded_by_proxy
    def test_multitenant_authentication(self, client, is_hsm, **kwargs):
        if not self.is_live:
            pytest.skip("This test is incompatible with test proxy in playback")

        # we set up a client for this method to align with the async test, but we actually want to create a new client
        # this new client should use a credential with an initially fake tenant ID and still succeed with a real request
        original_tenant = os.environ.get("AZURE_TENANT_ID")
        os.environ["AZURE_TENANT_ID"] = str(uuid4())
        credential = self.get_credential(KeyClient, additionally_allowed_tenants="*")
        managed_hsm_url = kwargs.pop("managed_hsm_url", None)
        keyvault_url = kwargs.pop("vault_url", None)
        vault_url = managed_hsm_url if is_hsm else keyvault_url
        client = KeyClient(vault_url=vault_url, credential=credential)

        if self.is_live:
            time.sleep(2)  # to avoid throttling by the service
        key_name = self.get_resource_name("multitenant-key")
        key = client.create_rsa_key(key_name)
        assert key.id

        # try making another request with the credential's token revoked
        # the challenge policy should correctly request a new token for the correct tenant when a challenge is cached
        client._client._config.authentication_policy._token = None
        fetched_key = client.get_key(key_name)
        assert key.id == fetched_key.id

        # clear the fake tenant
        if original_tenant:
            os.environ["AZURE_TENANT_ID"] = original_tenant
        else:
            os.environ.pop("AZURE_TENANT_ID")


def empty_challenge_cache(fn):
    @functools.wraps(fn)
    def wrapper(**kwargs):
        HttpChallengeCache.clear()
        assert len(HttpChallengeCache._cache) == 0
        return fn(**kwargs)

    return wrapper


def get_random_url():
    """The challenge cache is keyed on URLs. Random URLs defend against tests interfering with each other."""

    return f"https://{uuid4()}.vault.azure.net/{uuid4()}".replace("-", "")


URL = f'authorization_uri="{get_random_url()}"'
CLIENT_ID = 'client_id="00000003-0000-0000-c000-000000000000"'
CAE_ERROR = 'error="insufficient_claims"'
CAE_DECODED_CLAIM = '{"access_token": {"foo": "bar"}}'
# Claim token is a string of the base64 encoding of the claim
CLAIM_TOKEN = base64.b64encode(CAE_DECODED_CLAIM.encode()).decode()
# Note that no resource or scope is necessarily provided in a CAE challenge
CLAIM_CHALLENGE = f'Bearer realm="", {URL}, {CLIENT_ID}, {CAE_ERROR}, claims="{CLAIM_TOKEN}"'
CAE_CHALLENGE_RESPONSE = Mock(status_code=401, headers={"WWW-Authenticate": CLAIM_CHALLENGE})

KV_CHALLENGE_TENANT = "tenant-id"
ENDPOINT = f"https://authority.net/{KV_CHALLENGE_TENANT}"
RESOURCE = "https://vault.azure.net"
KV_CHALLENGE_RESPONSE = Mock(
    status_code=401,
    headers={"WWW-Authenticate": f'Bearer authorization="{ENDPOINT}", resource={RESOURCE}'},
)


@empty_challenge_cache
@pytest.mark.parametrize("fresh_policy", [False, True])
def test_rejected_challenge_is_not_cached(fresh_policy):
    url = "https://example.net/keys/canary"
    challenge = Mock(
        status_code=401,
        headers={"WWW-Authenticate": 'Bearer authorization="https://authority.net/tenant", resource=https://vault.azure.net'},
    )

    class Requests:
        count = 0

    def send(request):
        Requests.count += 1
        assert "Authorization" not in request.headers
        assert not request.body
        assert request.headers["Content-Length"] == "0"
        return challenge

    credential = Mock(spec_set=["get_token"], get_token=Mock(side_effect=AssertionError("unexpected token request")))
    pipeline = Pipeline(policies=[ChallengeAuthPolicy(credential=credential)], transport=Mock(send=send))

    for _ in range(2):
        if fresh_policy:
            pipeline = Pipeline(policies=[ChallengeAuthPolicy(credential=credential)], transport=Mock(send=send))
        request = HttpRequest("POST", url)
        request.set_bytes_body(b"secret")
        with pytest.raises(ValueError):
            pipeline.run(request)

    assert Requests.count == 2
    assert not HttpChallengeCache.get_challenge_for_url(url)
    assert credential.get_token.call_count == 0


def add_url_port(url: str):
    """Like `get_random_url`, but includes a port number (comes after the domain, and before the path of the URL)."""

    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}:443{parsed.path}"


def test_enforces_tls():
    url = "http://not.secure"
    HttpChallengeCache.set_challenge_for_url(url, HttpChallenge(url, "Bearer authorization=_, resource=_"))

    credential = Mock()
    pipeline = Pipeline(transport=Mock(), policies=[ChallengeAuthPolicy(credential)])
    with pytest.raises(ServiceRequestError):
        pipeline.run(HttpRequest("GET", url))


def test_challenge_cache():
    url_a = get_random_url()
    challenge_a = HttpChallenge(url_a, "Bearer authorization=authority A, resource=resource A")

    url_b = get_random_url()
    challenge_b = HttpChallenge(url_b, "Bearer authorization=authority B, resource=resource B")

    for url, challenge in zip((url_a, url_b), (challenge_a, challenge_b)):
        HttpChallengeCache.set_challenge_for_url(url, challenge)
        assert HttpChallengeCache.get_challenge_for_url(url) == challenge
        assert HttpChallengeCache.get_challenge_for_url(url + "/some/path") == challenge
        assert HttpChallengeCache.get_challenge_for_url(url + "/some/path?with-query=string") == challenge
        assert HttpChallengeCache.get_challenge_for_url(add_url_port(url)) == challenge

        HttpChallengeCache.remove_challenge_for_url(url)
        assert not HttpChallengeCache.get_challenge_for_url(url)


def test_challenge_parsing():
    tenant = "tenant"
    authority = f"https://login.authority.net/{tenant}"
    resource = "https://challenge.resource"
    challenge = HttpChallenge("https://request.uri", challenge=f"Bearer authorization={authority}, resource={resource}")

    assert challenge.get_authorization_server() == authority
    assert challenge.get_resource() == resource
    assert challenge.tenant_id == tenant


@empty_challenge_cache
@pytest.mark.parametrize("token_type", TOKEN_TYPES)
def test_scope(token_type):
    """The policy's token requests should always be for an AADv2 scope"""

    expected_content = b"a duck"

    def test_with_challenge(challenge, expected_scope):
        expected_token = "expected_token"

        class Requests:
            count = 0

        def send(request):
            Requests.count += 1
            if Requests.count == 1:
                # first request should be unauthorized and have no content
                assert not request.body
                assert request.headers["Content-Length"] == "0"
                return challenge
            elif Requests.count == 2:
                # second request should be authorized according to challenge and have the expected content
                assert request.headers["Content-Length"]
                assert request.body == expected_content
                assert expected_token in request.headers["Authorization"]
                return Mock(status_code=200)
            raise ValueError("unexpected request")

        def get_token(*scopes, **_):
            assert len(scopes) == 1
            assert scopes[0] == expected_scope
            return token_type(expected_token, 0)

        if token_type == AccessToken:
            credential = Mock(spec_set=["get_token"], get_token=Mock(wraps=get_token))
        else:
            credential = Mock(spec_set=["get_token_info"], get_token_info=Mock(wraps=get_token))
        pipeline = Pipeline(policies=[ChallengeAuthPolicy(credential=credential)], transport=Mock(send=send))
        request = HttpRequest("POST", get_random_url())
        request.set_bytes_body(expected_content)
        pipeline.run(request)

        if hasattr(credential, "get_token"):
            assert credential.get_token.call_count == 1
        else:
            assert credential.get_token_info.call_count == 1

    endpoint = "https://authority.net/tenant"

    # an AADv1 resource becomes an AADv2 scope with the addition of '/.default'
    resource = "https://vault.azure.net"
    scope = resource + "/.default"

    challenge_with_resource = Mock(
        status_code=401,
        headers={"WWW-Authenticate": f'Bearer authorization="{endpoint}", resource={resource}'},
    )

    challenge_with_scope = Mock(
        status_code=401, headers={"WWW-Authenticate": f'Bearer authorization="{endpoint}", scope={scope}'}
    )

    test_with_challenge(challenge_with_resource, scope)
    test_with_challenge(challenge_with_scope, scope)


@empty_challenge_cache
@pytest.mark.parametrize("token_type", TOKEN_TYPES)
def test_tenant(token_type):
    """The policy's token requests should pass the parsed tenant ID from the challenge"""

    expected_content = b"a duck"

    def test_with_challenge(challenge, expected_tenant):
        expected_token = "expected_token"

        class Requests:
            count = 0

        def send(request):
            Requests.count += 1
            if Requests.count == 1:
                # first request should be unauthorized and have no content
                assert not request.body
                assert request.headers["Content-Length"] == "0"
                return challenge
            elif Requests.count == 2:
                # second request should be authorized according to challenge and have the expected content
                assert request.headers["Content-Length"]
                assert request.body == expected_content
                assert expected_token in request.headers["Authorization"]
                return Mock(status_code=200)
            raise ValueError("unexpected request")

        def get_token(*_, options=None, **kwargs):
            options_bag = options if options else kwargs
            assert options_bag.get("tenant_id") == expected_tenant
            return token_type(expected_token, 0)

        if token_type == AccessToken:
            credential = Mock(spec_set=["get_token"], get_token=Mock(wraps=get_token))
        else:
            credential = Mock(spec_set=["get_token_info"], get_token_info=Mock(wraps=get_token))
        pipeline = Pipeline(policies=[ChallengeAuthPolicy(credential=credential)], transport=Mock(send=send))
        request = HttpRequest("POST", get_random_url())
        request.set_bytes_body(expected_content)
        pipeline.run(request)

        if hasattr(credential, "get_token"):
            assert credential.get_token.call_count == 1
        else:
            assert credential.get_token_info.call_count == 1

    tenant = "tenant-id"
    endpoint = f"https://authority.net/{tenant}"
    resource = "https://vault.azure.net"

    challenge = Mock(
        status_code=401,
        headers={"WWW-Authenticate": f'Bearer authorization="{endpoint}", resource={resource}'},
    )

    test_with_challenge(challenge, tenant)


@empty_challenge_cache
def test_challenge_cache_casing():
    """The challenge cache should update and retrieve challenges in a case-insensitive manner"""

    url = get_random_url()
    endpoint = f"https://authority.net/tenant-id"
    resource = "https://vault.azure.net"
    headers = {"WWW-Authenticate": f'Bearer authorization="{endpoint}", resource={resource}'}

    challenge = HttpChallenge(
        url,
        headers["WWW-Authenticate"],
        response_headers=headers,
    )

    # Store the challenge with original casing
    HttpChallengeCache.set_challenge_for_url(url, challenge)
    # Retrieve the challenge using a different casing
    retrieved_challenge = HttpChallengeCache.get_challenge_for_url(url.upper())
    assert retrieved_challenge == challenge
    # Remove the challenge and ensure it's no longer retrievable
    HttpChallengeCache.remove_challenge_for_url(url.upper())
    assert HttpChallengeCache.get_challenge_for_url(url) is None

    # Do the above, but with opposite casing
    HttpChallengeCache.set_challenge_for_url(url.upper(), challenge)
    retrieved_challenge = HttpChallengeCache.get_challenge_for_url(url)
    assert retrieved_challenge == challenge
    HttpChallengeCache.remove_challenge_for_url(url)
    assert HttpChallengeCache.get_challenge_for_url(url) is None


@empty_challenge_cache
@pytest.mark.parametrize("token_type", TOKEN_TYPES)
def test_adfs(token_type):
    """The policy should handle AD FS challenges as a special case and omit the tenant ID from token requests"""

    expected_content = b"a duck"

    def test_with_challenge(challenge, expected_tenant):
        expected_token = "expected_token"

        class Requests:
            count = 0

        def send(request):
            Requests.count += 1
            if Requests.count == 1:
                # first request should be unauthorized and have no content
                assert not request.body
                assert request.headers["Content-Length"] == "0"
                return challenge
            elif Requests.count in (2, 3):
                # second request should be authorized according to challenge and have the expected content
                assert request.headers["Content-Length"]
                assert request.body == expected_content
                assert expected_token in request.headers["Authorization"]
                return Mock(status_code=200)
            raise ValueError("unexpected request")

        def get_token(*_, **kwargs):
            # we shouldn't provide a tenant ID during AD FS authentication
            assert "tenant_id" not in kwargs
            return token_type(expected_token, 0)

        if token_type == AccessToken:
            credential = Mock(spec_set=["get_token"], get_token=Mock(wraps=get_token))
        else:
            credential = Mock(spec_set=["get_token_info"], get_token_info=Mock(wraps=get_token))
        policy = ChallengeAuthPolicy(credential=credential)
        pipeline = Pipeline(policies=[policy], transport=Mock(send=send))
        request = HttpRequest("POST", get_random_url())
        request.set_bytes_body(expected_content)
        pipeline.run(request)
        if hasattr(credential, "get_token"):
            assert credential.get_token.call_count == 1
        else:
            assert credential.get_token_info.call_count == 1

        # Regression test: https://github.com/Azure/azure-sdk-for-python/issues/33621
        policy._token = None
        pipeline.run(request)

    tenant = "tenant-id"
    # AD FS challenges have an unusual authority format; see https://github.com/Azure/azure-sdk-for-python/issues/28648
    endpoint = f"https://adfs.redmond.azurestack.corp.microsoft.com/adfs/{tenant}"
    resource = "https://vault.azure.net"

    challenge = Mock(
        status_code=401,
        headers={"WWW-Authenticate": f'Bearer authorization="{endpoint}", resource={resource}'},
    )

    test_with_challenge(challenge, tenant)


@pytest.mark.parametrize("token_type", TOKEN_TYPES)
def test_policy_updates_cache(token_type):
    """
    It's possible for the challenge returned for a request to change, e.g. when a vault is moved to a new tenant.
    When the policy receives a 401, it should update the cached challenge for the requested URL, if one exists.
    """

    url = get_random_url()
    first_scope = "https://vault.azure.net/first-scope"
    first_token = "first-scope-token"
    second_scope = "https://vault.azure.net/second-scope"
    second_token = "second-scope-token"
    challenge_fmt = 'Bearer authorization="https://login.authority.net/tenant", resource='

    # mocking a tenant change:
    # 1. first request -> respond with challenge
    # 2. second request should be authorized according to the challenge
    # 3. third request should match the second (using a cached access token)
    # 4. fourth request should also match the second -> respond with a new challenge
    # 5. fifth request should be authorized according to the new challenge
    # 6. sixth request should match the fifth
    transport = validating_transport(
        requests=(
            Request(url),
            Request(url, required_headers={"Authorization": f"Bearer {first_token}"}),
            Request(url, required_headers={"Authorization": f"Bearer {first_token}"}),
            Request(url, required_headers={"Authorization": f"Bearer {first_token}"}),
            Request(url, required_headers={"Authorization": f"Bearer {second_token}"}),
            Request(url, required_headers={"Authorization": f"Bearer {second_token}"}),
        ),
        responses=(
            mock_response(status_code=401, headers={"WWW-Authenticate": challenge_fmt + first_scope}),
            mock_response(status_code=200),
            mock_response(status_code=200),
            mock_response(status_code=401, headers={"WWW-Authenticate": challenge_fmt + second_scope}),
            mock_response(status_code=200),
            mock_response(status_code=200),
        ),
    )

    token = token_type(first_token, time.time() + 3600)

    def get_token(*_, **__):
        return token

    if token_type == AccessToken:
        credential = Mock(spec_set=["get_token"], get_token=Mock(wraps=get_token))
    else:
        credential = Mock(spec_set=["get_token_info"], get_token_info=Mock(wraps=get_token))
    pipeline = Pipeline(policies=[ChallengeAuthPolicy(credential=credential)], transport=transport)

    # policy should complete and cache the first challenge and access token
    for _ in range(2):
        pipeline.run(HttpRequest("GET", url))
        if hasattr(credential, "get_token"):
            assert credential.get_token.call_count == 1
        else:
            assert credential.get_token_info.call_count == 1

    # The next request will receive a new challenge. The policy should handle it and update caches.
    token = token_type(second_token, time.time() + 3600)
    for _ in range(2):
        pipeline.run(HttpRequest("GET", url))
        if hasattr(credential, "get_token"):
            assert credential.get_token.call_count == 2
        else:
            assert credential.get_token_info.call_count == 2


@empty_challenge_cache
@pytest.mark.parametrize("token_type", TOKEN_TYPES)
def test_token_expiration(token_type):
    """policy should not use a cached token which has expired"""

    url = get_random_url()

    expires_on = time.time() + 3600
    first_token = "*"
    second_token = "**"
    resource = "https://vault.azure.net"

    token = token_type(first_token, expires_on)

    def get_token(*_, **__):
        return token

    if token_type == AccessToken:
        credential = Mock(spec_set=["get_token"], get_token=Mock(wraps=get_token))
    else:
        credential = Mock(spec_set=["get_token_info"], get_token_info=Mock(wraps=get_token))
    transport = validating_transport(
        requests=[
            Request(),
            Request(required_headers={"Authorization": "Bearer " + first_token}),
            Request(required_headers={"Authorization": "Bearer " + first_token}),
            Request(required_headers={"Authorization": "Bearer " + second_token}),
        ],
        responses=[
            mock_response(
                status_code=401, headers={"WWW-Authenticate": f'Bearer authorization="{url}", resource={resource}'}
            )
        ]
        + [mock_response()] * 3,
    )
    pipeline = Pipeline(policies=[ChallengeAuthPolicy(credential=credential)], transport=transport)

    for _ in range(2):
        pipeline.run(HttpRequest("GET", url))
        if hasattr(credential, "get_token"):
            assert credential.get_token.call_count == 1
        else:
            assert credential.get_token_info.call_count == 1

    token = token_type(second_token, time.time() + 3600)
    with patch("time.time", lambda: expires_on):
        pipeline.run(HttpRequest("GET", url))
    if hasattr(credential, "get_token"):
        assert credential.get_token.call_count == 2
    else:
        assert credential.get_token_info.call_count == 2


@empty_challenge_cache
@pytest.mark.parametrize("token_type", TOKEN_TYPES)
def test_preserves_options_and_headers(token_type):
    """After a challenge, the policy should send the original request with its options and headers preserved"""

    url = get_random_url()
    token = "**"
    resource = "https://vault.azure.net"

    def get_token(*_, **__):
        return token_type(token, 0)

    if token_type == AccessToken:
        credential = Mock(spec_set=["get_token"], get_token=Mock(wraps=get_token))
    else:
        credential = Mock(spec_set=["get_token_info"], get_token_info=Mock(wraps=get_token))

    transport = validating_transport(
        requests=[Request()] * 2 + [Request(required_headers={"Authorization": "Bearer " + token})],
        responses=[
            mock_response(
                status_code=401, headers={"WWW-Authenticate": f'Bearer authorization="{url}", resource={resource}'}
            )
        ]
        + [mock_response()] * 2,
    )

    key = "foo"
    value = "bar"

    def add(request):
        # add the expected option and header
        request.context.options[key] = value
        request.http_request.headers[key] = value

    adder = Mock(spec_set=SansIOHTTPPolicy, on_request=Mock(wraps=add), on_exception=lambda _: False)

    def verify(request):
        # authorized (non-challenge) requests should have the expected option and header
        if request.http_request.headers.get("Authorization"):
            assert request.context.options.get(key) == value, "request option wasn't preserved across challenge"
            assert request.http_request.headers.get(key) == value, "headers wasn't preserved across challenge"

    verifier = Mock(spec=SansIOHTTPPolicy, on_request=Mock(wraps=verify))

    challenge_policy = ChallengeAuthPolicy(credential=credential)
    policies = [adder, challenge_policy, verifier]
    pipeline = Pipeline(policies=policies, transport=transport)

    pipeline.run(HttpRequest("GET", url))

    # ensure the mock sans I/O policies were called
    assert adder.on_request.called, "mock policy wasn't invoked"
    assert verifier.on_request.called, "mock policy wasn't invoked"


@empty_challenge_cache
@pytest.mark.parametrize("verify_challenge_resource,token_type", product([True, False], TOKEN_TYPES))
def test_verify_challenge_resource_matches(verify_challenge_resource, token_type):
    """The auth policy should raise if the challenge resource doesn't match the request URL unless check is disabled"""

    url = get_random_url()
    url_with_port = add_url_port(url)
    token = "**"
    resource = "https://myvault.azure.net"  # Doesn't match a "".vault.azure.net" resource because of the "my" prefix

    def get_token(*_, **__):
        return token_type(token, 0)

    if token_type == AccessToken:
        credential = Mock(spec_set=["get_token"], get_token=Mock(wraps=get_token))
    else:
        credential = Mock(spec_set=["get_token_info"], get_token_info=Mock(wraps=get_token))

    transport = validating_transport(
        requests=[Request(), Request(required_headers={"Authorization": f"Bearer {token}"})],
        responses=[
            mock_response(
                status_code=401, headers={"WWW-Authenticate": f'Bearer authorization="{url}", resource={resource}'}
            ),
            mock_response(status_code=200, json_payload={"key": {"kid": f"{url}/key-name"}}),
        ],
    )
    transport_2 = validating_transport(
        requests=[Request(), Request(required_headers={"Authorization": f"Bearer {token}"})],
        responses=[
            mock_response(
                status_code=401, headers={"WWW-Authenticate": f'Bearer authorization="{url}", resource={resource}'}
            ),
            mock_response(status_code=200, json_payload={"key": {"kid": f"{url}/key-name"}}),
        ],
    )

    client = KeyClient(url, credential, transport=transport, verify_challenge_resource=verify_challenge_resource)
    client_with_port = KeyClient(
        url_with_port, credential, transport=transport_2, verify_challenge_resource=verify_challenge_resource
    )

    if verify_challenge_resource:
        with pytest.raises(ValueError) as e:
            client.get_key("key-name")
        assert f"The challenge resource 'myvault.azure.net' does not match the requested domain" in str(e.value)
        with pytest.raises(ValueError) as e:
            client_with_port.get_key("key-name")
        assert f"The challenge resource 'myvault.azure.net' does not match the requested domain" in str(e.value)
    else:
        key = client.get_key("key-name")
        assert key.name == "key-name"
        key = client_with_port.get_key("key-name")
        assert key.name == "key-name"


@empty_challenge_cache
@pytest.mark.parametrize("verify_challenge_resource,token_type", product([True, False], TOKEN_TYPES))
def test_verify_challenge_resource_valid(verify_challenge_resource, token_type):
    """The auth policy should raise if the challenge resource isn't a valid URL unless check is disabled"""

    url = get_random_url()
    token = "**"
    resource = "bad-resource"

    def get_token(*_, **__):
        return token_type(token, 0)

    if token_type == AccessToken:
        credential = Mock(spec_set=["get_token"], get_token=Mock(wraps=get_token))
    else:
        credential = Mock(spec_set=["get_token_info"], get_token_info=Mock(wraps=get_token))

    transport = validating_transport(
        requests=[Request(), Request(required_headers={"Authorization": f"Bearer {token}"})],
        responses=[
            mock_response(
                status_code=401, headers={"WWW-Authenticate": f'Bearer authorization="{url}", resource={resource}'}
            ),
            mock_response(status_code=200, json_payload={"key": {"kid": f"{url}/key-name"}}),
        ],
    )

    client = KeyClient(url, credential, transport=transport, verify_challenge_resource=verify_challenge_resource)

    if verify_challenge_resource:
        with pytest.raises(ValueError) as e:
            client.get_key("key-name")
        assert "The challenge contains invalid scope" in str(e.value)
    else:
        key = client.get_key("key-name")
        assert key.name == "key-name"


@empty_challenge_cache
@pytest.mark.parametrize("token_type", TOKEN_TYPES)
def test_cae(token_type):
    """The policy should handle claims in a challenge response after having successfully authenticated prior."""

    expected_content = b"a duck"

    def test_with_challenge(claims_challenge, expected_claim):
        first_token = "first_token"
        expected_token = "expected_token"

        class Requests:
            count = 0

        def send(request):
            Requests.count += 1
            if Requests.count == 1:
                # first request should be unauthorized and have no content; triggers a KV challenge response
                assert not request.body
                assert "Authorization" not in request.headers
                assert request.headers["Content-Length"] == "0"
                return KV_CHALLENGE_RESPONSE
            elif Requests.count == 2:
                # second request should be authorized according to challenge and have the expected content
                assert request.headers["Content-Length"]
                assert request.body == expected_content
                assert first_token in request.headers["Authorization"]
                return Mock(status_code=200)
            elif Requests.count == 3:
                # third request will trigger a CAE challenge response in this test scenario
                assert request.headers["Content-Length"]
                assert request.body == expected_content
                assert first_token in request.headers["Authorization"]
                return claims_challenge
            elif Requests.count == 4:
                # fourth request should include the required claims and correctly use content from the first challenge
                assert request.headers["Content-Length"]
                assert request.body == expected_content
                assert expected_token in request.headers["Authorization"]
                return Mock(status_code=200)
            elif Requests.count == 5:
                # fifth request should be a regular request with the expected token
                assert request.headers["Content-Length"]
                assert request.body == expected_content
                assert expected_token in request.headers["Authorization"]
                return KV_CHALLENGE_RESPONSE
            elif Requests.count == 6:
                # sixth request should respond to the KV challenge WITHOUT including claims
                # we return another challenge to confirm that the policy will return consecutive 401s to the user
                assert request.headers["Content-Length"]
                assert request.body == expected_content
                assert first_token in request.headers["Authorization"]
                return KV_CHALLENGE_RESPONSE
            raise ValueError("unexpected request")

        def get_token(*scopes, options=None, **kwargs):
            options_bag = options if options else kwargs
            assert options_bag.get("enable_cae") == True
            assert options_bag.get("tenant_id") == KV_CHALLENGE_TENANT
            assert scopes[0] == RESOURCE + "/.default"
            # Response to KV challenge
            if Requests.count == 1:
                assert options_bag.get("claims") == None
                return AccessToken(first_token, time.time() + 3600)
            # Response to CAE challenge
            elif Requests.count == 3:
                assert options_bag.get("claims") == expected_claim
                return AccessToken(expected_token, time.time() + 3600)
            # Response to second KV challenge
            elif Requests.count == 5:
                assert options_bag.get("claims") == None
                return AccessToken(first_token, time.time() + 3600)
            elif Requests.count == 6:
                raise ValueError("unexpected token request")

        if token_type == AccessToken:
            credential = Mock(spec_set=["get_token"], get_token=Mock(wraps=get_token))
        else:
            credential = Mock(spec_set=["get_token_info"], get_token_info=Mock(wraps=get_token))
        pipeline = Pipeline(policies=[ChallengeAuthPolicy(credential=credential)], transport=Mock(send=send))
        request = HttpRequest("POST", get_random_url())
        request.set_bytes_body(expected_content)
        pipeline.run(request)  # Send the request once to trigger a regular auth challenge
        pipeline.run(request)  # Send the request again to trigger a CAE challenge
        pipeline.run(request)  # Send the request once to trigger another regular auth challenge

        # token requests made for the CAE challenge and first two KV challenges, but not the final KV challenge
        if hasattr(credential, "get_token"):
            assert credential.get_token.call_count == 3
        else:
            assert credential.get_token_info.call_count == 3

    test_with_challenge(CAE_CHALLENGE_RESPONSE, CAE_DECODED_CLAIM)


@empty_challenge_cache
@pytest.mark.parametrize("token_type", TOKEN_TYPES)
def test_cae_consecutive_challenges(token_type):
    """The policy should correctly handle consecutive challenges in cases where the flow is valid or invalid."""

    expected_content = b"a duck"

    def test_with_challenge(claims_challenge, expected_claim):
        first_token = "first_token"
        expected_token = "expected_token"

        class Requests:
            count = 0

        def send(request):
            Requests.count += 1
            if Requests.count == 1:
                # first request should be unauthorized and have no content; triggers a KV challenge response
                assert not request.body
                assert "Authorization" not in request.headers
                assert request.headers["Content-Length"] == "0"
                return KV_CHALLENGE_RESPONSE
            elif Requests.count == 2:
                # second request will trigger a CAE challenge response in this test scenario
                assert request.headers["Content-Length"]
                assert request.body == expected_content
                assert first_token in request.headers["Authorization"]
                return claims_challenge
            elif Requests.count == 3:
                # third request should include the required claims and correctly use content from the first challenge
                # we return another CAE challenge to verify that the policy will return consecutive CAE 401s to the user
                assert request.headers["Content-Length"]
                assert request.body == expected_content
                assert expected_token in request.headers["Authorization"]
                return claims_challenge
            raise ValueError("unexpected request")

        def get_token(*scopes, options=None, **kwargs):
            options_bag = options if options else kwargs
            assert options_bag.get("enable_cae") == True
            assert options_bag.get("tenant_id") == KV_CHALLENGE_TENANT
            assert scopes[0] == RESOURCE + "/.default"
            # Response to KV challenge
            if Requests.count == 1:
                assert options_bag.get("claims") == None
                return token_type(first_token, time.time() + 3600)
            # Response to first CAE challenge
            elif Requests.count == 2:
                assert options_bag.get("claims") == expected_claim
                return token_type(expected_token, time.time() + 3600)

        if token_type == AccessToken:
            credential = Mock(spec_set=["get_token"], get_token=Mock(wraps=get_token))
        else:
            credential = Mock(spec_set=["get_token_info"], get_token_info=Mock(wraps=get_token))
        pipeline = Pipeline(policies=[ChallengeAuthPolicy(credential=credential)], transport=Mock(send=send))
        request = HttpRequest("POST", get_random_url())
        request.set_bytes_body(expected_content)
        pipeline.run(request)

        # token requests made for the KV challenge and first CAE challenge, but not the second CAE challenge
        if hasattr(credential, "get_token"):
            assert credential.get_token.call_count == 2
        else:
            assert credential.get_token_info.call_count == 2

    test_with_challenge(CAE_CHALLENGE_RESPONSE, CAE_DECODED_CLAIM)


@empty_challenge_cache
@pytest.mark.parametrize("token_type", TOKEN_TYPES)
def test_cae_token_expiry(token_type):
    """The policy should avoid sending claims more than once when a token expires."""

    expected_content = b"a duck"

    def test_with_challenge(claims_challenge, expected_claim):
        first_token = "first_token"
        second_token = "second_token"
        third_token = "third_token"

        class Requests:
            count = 0

        def send(request):
            Requests.count += 1
            if Requests.count == 1:
                # first request should be unauthorized and have no content; triggers a KV challenge response
                assert not request.body
                assert "Authorization" not in request.headers
                assert request.headers["Content-Length"] == "0"
                return KV_CHALLENGE_RESPONSE
            elif Requests.count == 2:
                # second request will trigger a CAE challenge response in this test scenario
                assert request.headers["Content-Length"]
                assert request.body == expected_content
                assert first_token in request.headers["Authorization"]
                return claims_challenge
            elif Requests.count == 3:
                # third request should include the required claims and correctly use content from the first challenge
                assert request.headers["Content-Length"]
                assert request.body == expected_content
                assert second_token in request.headers["Authorization"]
                return Mock(status_code=200)
            elif Requests.count == 4:
                # fourth request should not include claims, but otherwise use content from the first challenge
                assert request.headers["Content-Length"]
                assert request.body == expected_content
                assert third_token in request.headers["Authorization"]
                return Mock(status_code=200)
            raise ValueError("unexpected request")

        def get_token(*scopes, options=None, **kwargs):
            options_bag = options if options else kwargs
            assert options_bag.get("enable_cae") == True
            assert options_bag.get("tenant_id") == KV_CHALLENGE_TENANT
            assert scopes[0] == RESOURCE + "/.default"
            # Response to KV challenge
            if Requests.count == 1:
                assert options_bag.get("claims") == None
                return token_type(first_token, time.time() + 3600)
            # Response to first CAE challenge
            elif Requests.count == 2:
                assert options_bag.get("claims") == expected_claim
                return token_type(second_token, 0)  # Return a token that expires immediately to trigger a refresh
            # Token refresh before making the final request
            elif Requests.count == 3:
                assert options_bag.get("claims") == None
                return token_type(third_token, time.time() + 3600)

        if token_type == AccessToken:
            credential = Mock(spec_set=["get_token"], get_token=Mock(wraps=get_token))
        else:
            credential = Mock(spec_set=["get_token_info"], get_token_info=Mock(wraps=get_token))
        pipeline = Pipeline(policies=[ChallengeAuthPolicy(credential=credential)], transport=Mock(send=send))
        request = HttpRequest("POST", get_random_url())
        request.set_bytes_body(expected_content)
        pipeline.run(request)
        pipeline.run(request)  # Send the request again to trigger a token refresh upon expiry

        # token requests made for the KV and CAE challenges, as well as for the token refresh
        if hasattr(credential, "get_token"):
            assert credential.get_token.call_count == 3
        else:
            assert credential.get_token_info.call_count == 3

    test_with_challenge(CAE_CHALLENGE_RESPONSE, CAE_DECODED_CLAIM)


@empty_challenge_cache
@pytest.mark.parametrize("token_type", TOKEN_TYPES)
def test_request_body_not_reused_across_requests(token_type):
    """A request's body must not leak into a later request made by the same client.

    Regression test for the replay bug: the original request used to be stashed on the policy instance and was
    never cleared, so a subsequent bodiless request (e.g. a polling GET) that triggered its own challenge would
    have the earlier request's body (and method/URL) replayed onto it. The copy is now stored per-request on the
    pipeline context, so it cannot leak across requests. See
    https://github.com/Azure/azure-sdk-for-python/pull/47742.
    """

    expected_token = "expected_token"
    first_content = b"a duck"
    first_url = get_random_url()
    second_url = get_random_url()
    challenge = Mock(
        status_code=401,
        headers={"WWW-Authenticate": 'Bearer authorization="https://authority.net/tenant", resource=https://vault.azure.net'},
    )

    class Requests:
        count = 0

    def send(request):
        Requests.count += 1
        if Requests.count == 1:
            # first request (POST with body): the body is stripped to elicit a challenge
            assert not request.body
            assert request.headers["Content-Length"] == "0"
            return challenge
        elif Requests.count == 2:
            # first request is retried with its original body and authorization
            assert request.body == first_content
            assert expected_token in request.headers["Authorization"]
            return Mock(status_code=200)
        elif Requests.count == 3:
            # second request (bodiless GET): elicits its own challenge and must have no body
            assert not request.body
            return challenge
        elif Requests.count == 4:
            # second request is retried: it must remain a bodiless GET, i.e. the first request's body and
            # method/URL must NOT be replayed onto it
            assert not request.body
            assert request.method == "GET"
            assert request.url == second_url
            assert expected_token in request.headers["Authorization"]
            return Mock(status_code=200)
        raise ValueError("unexpected request")

    def get_token(*_, **__):
        return token_type(expected_token, time.time() + 3600)

    if token_type == AccessToken:
        credential = Mock(spec_set=["get_token"], get_token=Mock(wraps=get_token))
    else:
        credential = Mock(spec_set=["get_token_info"], get_token_info=Mock(wraps=get_token))

    # a single policy instance handles both requests; the fix prevents state from one request leaking into the next
    policy = ChallengeAuthPolicy(credential=credential)
    pipeline = Pipeline(policies=[policy], transport=Mock(send=send))

    first_request = HttpRequest("POST", first_url)
    first_request.set_bytes_body(first_content)
    pipeline.run(first_request)

    pipeline.run(HttpRequest("GET", second_url))


@pytest.mark.parametrize("method,body", [("PUT", b"payload"), ("HEAD", None), ("HEAD", b"payload")])
@pytest.mark.parametrize("warm_cache", [False, True])
@pytest.mark.parametrize("refill_cache", [False, True])
def test_retry_cache_eviction_preserves_request(method, body, warm_cache, refill_cache):
    url = get_random_url()
    header = 'Bearer authorization="https://authority.net/tenant", resource=https://vault.azure.net'
    if warm_cache:
        HttpChallengeCache.set_challenge_for_url(url, HttpChallenge(url, header))
    credential = Mock(spec_set=["get_token"], get_token=Mock(return_value=AccessToken("token", time.time() + 3600)))
    policy = ChallengeAuthPolicy(credential)
    other_credential = Mock(
        spec_set=["get_token"], get_token=Mock(return_value=AccessToken("other", time.time() + 3600))
    )
    other = Pipeline(
        policies=[ChallengeAuthPolicy(other_credential)],
        transport=Mock(send=Mock(return_value=Mock(status_code=401, headers={"WWW-Authenticate": "Bearer invalid=1"}))),
    )
    stages = (
        [(True, 503, "evict"), (False, 503, "refill"), (True, 200, None)]
        if refill_cache
        else [
            (True, 503, "evict"),
            (False, 503, None),
            (False, 401, None),
            (True, 503, "evict"),
            (False, 401, None),
            (True, 200, None),
        ]
    )
    if not warm_cache:
        stages.insert(0, (False, 401, None))

    def send(request):
        if not stages:
            assert (request.method, request.url, request.body) == ("GET", url + "/next", None)
            return Mock(status_code=200, headers={})
        authenticated, status, action = stages.pop(0)
        assert (request.method, request.url) == (method, url)
        if authenticated:
            assert request.headers["Authorization"] == "Bearer token"
            assert request.body == body
        else:
            assert "Authorization" not in request.headers
            assert not request.body
            if body:
                assert request.headers["Content-Length"] == "0"
        if action == "evict":
            assert other.run(HttpRequest("GET", url + "/other")).http_response.status_code == 401
            assert HttpChallengeCache.get_challenge_for_url(url) is None
        elif action == "refill":
            HttpChallengeCache.set_challenge_for_url(url, HttpChallenge(url, header))
        return Mock(status_code=status, headers={"WWW-Authenticate": header} if status == 401 else {})

    pipeline = Pipeline(
        policies=[RetryPolicy(retry_total=5, retry_status=5, retry_backoff_factor=0), policy],
        transport=Mock(send=send),
    )
    assert pipeline.run(HttpRequest(method, url, content=body)).http_response.status_code == 200
    assert not stages
    assert pipeline.run(HttpRequest("GET", url + "/next")).http_response.status_code == 200


@pytest.mark.parametrize("initial", ["cached", "fresh", "refresh", "refresh-tenantless"])
@pytest.mark.parametrize("cache_change", ["evict", "replace-valid", "replace-invalid"])
@pytest.mark.parametrize(
    "new_tenant,new_scope",
    [
        (None, None),
        ("new-tenant", None),
        (None, "https://vault.azure.net/new-scope"),
        ("new-tenant", "https://vault.azure.net/new-scope"),
    ],
)
def test_cae_request_snapshot_survives_cache_changes(initial, cache_change, new_tenant, new_scope):
    url = get_random_url()
    old_scope = "https://vault.azure.net/.default"
    if initial != "fresh":
        HttpChallengeCache.set_challenge_for_url(
            url, HttpChallenge(url, f'Bearer authorization="https://authority.net/old-tenant", scope={old_scope}')
        )
    active_scope = "https://vault.azure.net/refreshed-scope" if initial.startswith("refresh") else old_scope
    active_tenant = (
        None if initial == "refresh-tenantless" else "refreshed-tenant" if initial == "refresh" else "old-tenant"
    )
    full_header = f'Bearer authorization="https://authority.net/{active_tenant or ""}", scope={active_scope}'
    claims_header = f'Bearer authorization="https://authority.net/{new_tenant or ""}", claims="e30="'
    if new_scope:
        claims_header += f", scope={new_scope}"
    credential = Mock(spec_set=["get_token"], get_token=Mock(return_value=AccessToken("token", time.time() + 3600)))
    other_credential = Mock(
        spec_set=["get_token"], get_token=Mock(return_value=AccessToken("other", time.time() + 3600))
    )
    other = Pipeline(
        policies=[ChallengeAuthPolicy(other_credential)],
        transport=Mock(send=Mock(return_value=Mock(status_code=401, headers={"WWW-Authenticate": "Bearer invalid=1"}))),
    )
    full_challenge_pending = initial != "cached"
    claims_pending = True

    def send(request):
        nonlocal full_challenge_pending, claims_pending
        if full_challenge_pending:
            full_challenge_pending = False
            assert bool(request.headers.get("Authorization")) == initial.startswith("refresh")
            return Mock(status_code=401, headers={"WWW-Authenticate": full_header})
        assert request.headers["Authorization"] == "Bearer token"
        assert request.body == b"payload"
        if claims_pending:
            claims_pending = False
            assert other.run(HttpRequest("GET", url + "/other")).http_response.status_code == 401
            assert HttpChallengeCache.get_challenge_for_url(url) is None
            if cache_change != "evict":
                replacement = "https://other.example/.default" if cache_change == "replace-invalid" else old_scope
                HttpChallengeCache.set_challenge_for_url(
                    url,
                    HttpChallenge(
                        url, f'Bearer authorization="https://authority.net/other-tenant", scope={replacement}'
                    ),
                )
            return Mock(status_code=401, headers={"WWW-Authenticate": claims_header})
        return Mock(status_code=200, headers={})

    pipeline = Pipeline(
        policies=[RetryPolicy(retry_backoff_factor=0), ChallengeAuthPolicy(credential)], transport=Mock(send=send)
    )
    assert pipeline.run(HttpRequest("PUT", url, content=b"payload")).http_response.status_code == 200
    # Preserve CAE precedence: both accepted values override replacements supplied in the claims challenge.
    credential.get_token.assert_called_with(active_scope, tenant_id=active_tenant, claims="{}", enable_cae=True)
    cached = HttpChallengeCache.get_challenge_for_url(url)
    assert cached.get_scope() == active_scope
    assert cached.tenant_id == active_tenant


@pytest.mark.parametrize(
    "target", ["same-path", "same-case", "default-port", "other-host", "other-port", "other-scheme"]
)
def test_cae_request_snapshot_is_origin_bound(target):
    url = get_random_url()
    parsed = urlparse(url)
    targets = {
        "same-path": url + "/redirected",
        "same-case": f"https://{parsed.netloc.upper()}{parsed.path}",
        "default-port": f"https://{parsed.netloc.upper()}:443{parsed.path}",
        "other-host": get_random_url(),
        "other-port": f"https://{parsed.netloc}:8443{parsed.path}",
        "other-scheme": url.replace("https://", "http://", 1),
    }
    redirect_url = targets[target]
    scope = "https://vault.azure.net/.default"
    HttpChallengeCache.set_challenge_for_url(
        url, HttpChallenge(url, f'Bearer authorization="https://authority.net/tenant", scope={scope}')
    )
    credential = Mock(spec_set=["get_token"], get_token=Mock(return_value=AccessToken("token", time.time() + 3600)))
    requests = []

    def send(request):
        requests.append(request.url)
        if len(requests) == 1:
            if target != "other-scheme":
                HttpChallengeCache.remove_challenge_for_url(url)
            return Mock(status_code=307, headers={"location": redirect_url})
        assert request.url == redirect_url
        if len(requests) == 2:
            return Mock(
                status_code=401,
                headers={"WWW-Authenticate": 'Bearer authorization="https://authority.net/", claims="e30="'},
            )
        return Mock(status_code=200, headers={})

    pipeline = Pipeline(
        policies=[RetryPolicy(), ChallengeAuthPolicy(credential), RedirectPolicy()], transport=Mock(send=send)
    )
    if target.startswith("other"):
        with pytest.raises(ValueError):
            pipeline.run(HttpRequest("GET", url))
        assert credential.get_token.call_count == 1
    else:
        assert pipeline.run(HttpRequest("GET", url)).http_response.status_code == 200
        credential.get_token.assert_called_with(scope, tenant_id="tenant", claims="{}", enable_cae=True)
        assert credential.get_token.call_count == 2


def test_cae_does_not_inherit_tenant_from_invalid_cache():
    url = get_random_url()
    HttpChallengeCache.set_challenge_for_url(
        url,
        HttpChallenge(url, 'Bearer authorization="https://authority.net/untrusted", resource=https://other.example'),
    )
    credential = Mock(spec_set=["get_token"])
    request = PipelineRequest(HttpRequest("GET", url), PipelineContext(None))
    response = PipelineResponse(
        request.http_request,
        Mock(
            status_code=401,
            headers={
                "WWW-Authenticate": 'Bearer authorization="https://authority.net/", scope=https://vault.azure.net/.default, claims="e30="'
            },
        ),
        request.context,
    )
    with pytest.raises(ValueError):
        ChallengeAuthPolicy(credential).on_challenge(request, response)
    credential.get_token.assert_not_called()
    assert HttpChallengeCache.get_challenge_for_url(url) is None


@pytest.mark.parametrize("redirect_status", [303, 307])
def test_discovery_replay_preserves_redirect_target(redirect_status):
    url = get_random_url()
    redirect_url = get_random_url()
    header = 'Bearer authorization="https://authority.net/tenant", resource=https://vault.azure.net'
    HttpChallengeCache.set_challenge_for_url(url, HttpChallenge(url, header))
    credential = Mock(spec_set=["get_token"], get_token=Mock(return_value=AccessToken("token", time.time() + 3600)))
    other = Pipeline(
        policies=[ChallengeAuthPolicy(credential)],
        transport=Mock(send=Mock(return_value=Mock(status_code=401, headers={"WWW-Authenticate": "Bearer invalid=1"}))),
    )
    requests = []

    def send(request):
        requests.append(request.url)
        if len(requests) == 1:
            assert (request.method, request.url, request.body) == ("PUT", url, b"payload")
            assert request.headers["Authorization"] == "Bearer token"
            assert other.run(HttpRequest("GET", url + "/other")).http_response.status_code == 401
            assert HttpChallengeCache.get_challenge_for_url(url) is None
            return Mock(status_code=503, headers={})
        if len(requests) == 2:
            assert (request.method, request.url) == ("PUT", url)
            assert "Authorization" not in request.headers
            assert not request.body
            return Mock(status_code=redirect_status, headers={"location": redirect_url})
        assert request.url == redirect_url
        assert request.method == ("GET" if redirect_status == 303 else "PUT")
        if len(requests) == 3:
            assert "Authorization" not in request.headers
            assert not request.body
            return Mock(
                status_code=401,
                headers={
                    "WWW-Authenticate": 'Bearer authorization="https://authority.net/tenant", resource=https://vault.azure.net'
                },
            )
        assert request.headers["Authorization"] == "Bearer token"
        assert request.body == (None if redirect_status == 303 else b"payload")
        return Mock(status_code=200, headers={})

    pipeline = Pipeline(
        policies=[
            RetryPolicy(retry_total=1, retry_backoff_factor=0),
            ChallengeAuthPolicy(credential),
            RedirectPolicy(),
        ],
        transport=Mock(send=send),
    )
    assert pipeline.run(HttpRequest("PUT", url, content=b"payload")).http_response.status_code == 200
    assert len(requests) == 4
