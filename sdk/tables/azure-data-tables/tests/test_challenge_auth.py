# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from unittest.mock import Mock

from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError
from azure.core.pipeline import Pipeline
from azure.core.pipeline.transport import HttpRequest as PipelineTransportHttpRequest
from azure.data.tables import TableServiceClient
from azure.data.tables._authentication import BearerTokenChallengePolicy
import pytest

from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy, is_live
from devtools_testutils.sanitizers import add_general_regex_sanitizer
from preparers import tables_decorator
from _shared.testcase import TableTestCase

# Try to use azure.core.rest request if azure-core version supports it -- fall back to basic request
try:
    from azure.core.rest import HttpRequest as RestHttpRequest
    HTTP_REQUESTS = [PipelineTransportHttpRequest, RestHttpRequest]
except ModuleNotFoundError:
    HTTP_REQUESTS = [PipelineTransportHttpRequest]


class TestTableChallengeAuth(AzureRecordedTestCase, TableTestCase):
    @tables_decorator
    @recorded_by_proxy
    def test_challenge_auth_supported_version(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        """This test requires a client that uses an API version that supports 401 challenge responses.

        Recorded using an incorrect tenant for the credential provided to our client. To run this live, ensure that the
        service principal used for testing is enabled for multitenant authentication
        (https://docs.microsoft.com/azure/active-directory/develop/howto-convert-app-to-be-multi-tenant). Set the
        TABLES_TENANT_ID environment variable to a different, existing tenant than the one the storage account exists
        in, and set CHALLENGE_TABLES_TENANT_ID to the tenant that the storage account exists in.
        """

        if is_live():
            pytest.skip("Playback testing and live manual testing only")

        account_url = self.account_url(tables_storage_account_name, "table")
        client = TableServiceClient(
            credential=self.get_token_credential(), endpoint=account_url, api_version="2020-12-06"
        )
        stats = client.get_service_stats()
        self._assert_stats_default(stats)

    @tables_decorator
    @recorded_by_proxy
    def test_challenge_auth_unsupported_version(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        """This test requires a client that uses an API version that doesn't support 401 challenge responses.

        Recorded using an incorrect tenant for the credential provided to our client. To run this live, ensure that the
        service principal used for testing is enabled for multitenant authentication
        (https://docs.microsoft.com/azure/active-directory/develop/howto-convert-app-to-be-multi-tenant). Set the
        TABLES_TENANT_ID environment variable to a different, existing tenant than the one the storage account exists
        in, and set CHALLENGE_TABLES_TENANT_ID to the tenant that the storage account exists in.
        """

        if is_live():
            pytest.skip("Playback testing and live manual testing only")

        account_url = self.account_url(tables_storage_account_name, "table")
        client = TableServiceClient(
            credential=self.get_token_credential(), endpoint=account_url, api_version="2019-07-07"
        )

        # Our request fails because of the invalid token, prompting a 403 response
        with pytest.raises(ClientAuthenticationError) as e:
            client.get_service_stats()


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_challenge_policy_uses_scopes_and_tenant(http_request):
    """The policy's token requests should pass the parsed scope and tenant ID from the challenge, by default"""

    def test_with_challenge(challenge, expected_scope, challenge_tenant):
        bad_token = "bad_token"
        expected_token = "expected_token"

        class Requests:
            count = 0

        class TokenRequests:
            count = 0

        def send(request):
            Requests.count += 1
            if Requests.count == 1:
                # first request triggers a 401 response w/ auth challenge -- token is for incorrect scope/tenant
                assert bad_token in request.headers["Authorization"]
                return challenge
            elif Requests.count == 2:
                # second request should be authorized according to challenge and have the expected content
                assert expected_token in request.headers["Authorization"]
                return Mock(status_code=200)
            raise ValueError("unexpected request")

        def get_token(*scopes, **kwargs):
            assert len(scopes) == 1
            TokenRequests.count += 1
            if TokenRequests.count == 1:
                # first request uses the scope given to the policy, and no tenant ID
                assert scopes[0] != expected_scope
                assert kwargs.get("tenant_id") is None
                return AccessToken(bad_token, 0)
            elif TokenRequests.count == 2:
                # second request should use the scope and tenant ID specified in the auth challenge
                assert scopes[0] == expected_scope
                assert kwargs.get("tenant_id") == challenge_tenant
                return AccessToken(expected_token, 0)
            raise ValueError("unexpected token request")

        credential = Mock(get_token=Mock(wraps=get_token))
        policy = BearerTokenChallengePolicy(credential, "scope")
        pipeline = Pipeline(policies=[policy], transport=Mock(send=send))
        pipeline.run(http_request("GET", "https://localhost"))

    tenant = "tenant-id"
    endpoint = f"https://authority.net/{tenant}/oauth2/authorize"
    resource = "https://challenge.resource"
    scope = f"{resource}/.default"

    # this challenge separates the authorization server and resource with commas in the WWW-Authenticate header
    challenge_with_commas = Mock(
        status_code=401,
        headers={"WWW-Authenticate": f'Bearer authorization="{endpoint}", resource="{resource}"'},
    )
    test_with_challenge(challenge_with_commas, scope, tenant)

    # this challenge separates the authorization server and resource with only spaces in the WWW-Authenticate header
    challenge_without_commas = Mock(
        status_code=401,
        headers={"WWW-Authenticate": f'Bearer authorization={endpoint} resource={resource}'},
    )
    test_with_challenge(challenge_without_commas, scope, tenant)

    # this challenge gives an AADv2 scope, ending with "/.default", instead of an AADv1 resource
    challenge_with_scope = Mock(
        status_code=401,
        headers={"WWW-Authenticate": f'Bearer authorization={endpoint} scope={scope}'},
    )
    test_with_challenge(challenge_with_scope, scope, tenant)


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_challenge_policy_disable_tenant_discovery(http_request):
    """The policy's token requests should exclude the challenge's tenant if requested"""

    def test_with_challenge(challenge, expected_scope):
        bad_token = "bad_token"

        class Requests:
            count = 0

        class TokenRequests:
            count = 0

        def send(request):
            Requests.count += 1
            if Requests.count == 1:
                # first request triggers a 401 response w/ auth challenge
                assert bad_token in request.headers["Authorization"]
                return challenge
            elif Requests.count == 2:
                # second request should still be unauthorized because we didn't authenticate in the correct tenant
                assert bad_token in request.headers["Authorization"]
                return challenge
            raise ValueError("unexpected request")

        def get_token(*scopes, **kwargs):
            assert len(scopes) == 1
            TokenRequests.count += 1
            if TokenRequests.count == 1:
                # first request uses the scope given to the policy, and no tenant ID
                assert scopes[0] != expected_scope
                assert kwargs.get("tenant_id") is None
                return AccessToken(bad_token, 0)
            elif TokenRequests.count == 2:
                # second request should use the scope specified in the auth challenge, but not the tenant
                assert scopes[0] == expected_scope
                assert kwargs.get("tenant_id") is None
                return AccessToken(bad_token, 0)
            raise ValueError("unexpected token request")

        credential = Mock(get_token=Mock(wraps=get_token))
        policy = BearerTokenChallengePolicy(credential, "scope", discover_tenant=False)
        pipeline = Pipeline(policies=[policy], transport=Mock(send=send))
        pipeline.run(http_request("GET", "https://localhost"))

    tenant = "tenant-id"
    endpoint = f"https://authority.net/{tenant}/oauth2/authorize"
    resource = "https://challenge.resource"
    scope = f"{resource}/.default"

    # this challenge separates the authorization server and resource with commas in the WWW-Authenticate header
    challenge_with_commas = Mock(
        status_code=401,
        headers={"WWW-Authenticate": f'Bearer authorization="{endpoint}", resource="{resource}"'},
    )
    # the request should fail after the challenge because we don't use the correct tenant
    # after the second 4xx response, the policy should raise the authentication error
    test_with_challenge(challenge_with_commas, scope)


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_challenge_policy_disable_scopes_discovery(http_request):
    """The policy's token requests should exclude the challenge's scope if requested"""

    def test_with_challenge(challenge, expected_scope, challenge_tenant):
        bad_token = "bad_token"

        class Requests:
            count = 0

        class TokenRequests:
            count = 0

        def send(request):
            Requests.count += 1
            if Requests.count == 1:
                # first request triggers a 401 response w/ auth challenge
                assert bad_token in request.headers["Authorization"]
                return challenge
            elif Requests.count == 2:
                # second request should still be unauthorized because we didn't authenticate with the correct scope
                assert bad_token in request.headers["Authorization"]
                return challenge
            raise ValueError("unexpected request")

        def get_token(*scopes, **kwargs):
            assert len(scopes) == 1
            TokenRequests.count += 1
            if TokenRequests.count == 1:
                # first request uses the scope given to the policy, and no tenant ID
                assert scopes[0] != expected_scope
                assert kwargs.get("tenant_id") is None
                return AccessToken(bad_token, 0)
            elif TokenRequests.count == 2:
                # second request should use the tenant specified in the auth challenge, but not the scope
                assert scopes[0] != expected_scope
                assert kwargs.get("tenant_id") == challenge_tenant
                return AccessToken(bad_token, 0)
            raise ValueError("unexpected token request")

        credential = Mock(get_token=Mock(wraps=get_token))
        policy = BearerTokenChallengePolicy(credential, "scope", discover_scopes=False)
        pipeline = Pipeline(policies=[policy], transport=Mock(send=send))
        pipeline.run(http_request("GET", "https://localhost"))

    tenant = "tenant-id"
    endpoint = f"https://authority.net/{tenant}/oauth2/authorize"
    resource = "https://challenge.resource"
    scope = f"{resource}/.default"

    # this challenge separates the authorization server and resource with commas in the WWW-Authenticate header
    challenge_with_commas = Mock(
        status_code=401,
        headers={"WWW-Authenticate": f'Bearer authorization="{endpoint}", resource="{resource}"'},
    )
    # the request should fail after the challenge because we don't use the correct scope
    # after the second 4xx response, the policy should raise the authentication error
    test_with_challenge(challenge_with_commas, scope, tenant)


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_challenge_policy_disable_any_discovery(http_request):
    """The policy shouldn't respond to the challenge if it can't use the provided scope or tenant"""

    def test_with_challenge(challenge, expected_scope, challenge_tenant):
        bad_token = "bad_token"

        class Requests:
            count = 0

        class TokenRequests:
            count = 0

        def send(request):
            Requests.count += 1
            if Requests.count == 1:
                # first request triggers a 401 response w/ auth challenge
                assert bad_token in request.headers["Authorization"]
                return challenge
            raise ValueError("unexpected request")

        def get_token(*scopes, **kwargs):
            assert len(scopes) == 1
            TokenRequests.count += 1
            if TokenRequests.count == 1:
                # first request uses the scope given to the policy, and no tenant ID
                assert scopes[0] != expected_scope
                assert kwargs.get("tenant_id") is None
                return AccessToken(bad_token, 0)
            raise ValueError("unexpected token request")

        credential = Mock(get_token=Mock(wraps=get_token))
        policy = BearerTokenChallengePolicy(
            credential, "scope", discover_tenant=False, discover_scopes=False
        )
        pipeline = Pipeline(policies=[policy], transport=Mock(send=send))
        pipeline.run(http_request("GET", "https://localhost"))

    tenant = "tenant-id"
    endpoint = f"https://authority.net/{tenant}/oauth2/authorize"
    resource = "https://challenge.resource"
    scope = f"{resource}/.default"

    # this challenge separates the authorization server and resource with commas in the WWW-Authenticate header
    challenge_with_commas = Mock(
        status_code=401,
        headers={"WWW-Authenticate": f'Bearer authorization="{endpoint}", resource="{resource}"'},
    )
    # the policy should only send one request since we can't update our request per the challenge response
    test_with_challenge(challenge_with_commas, scope, tenant)


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_challenge_policy_no_scope_in_challenge(http_request):
    """The policy's token requests should use constructor scopes if none are in the challenge"""

    def test_with_challenge(challenge, expected_scope, challenge_tenant):
        bad_token = "bad_token"

        class Requests:
            count = 0

        class TokenRequests:
            count = 0

        def send(request):
            Requests.count += 1
            if Requests.count == 1:
                # first request triggers a 401 response w/ auth challenge
                assert bad_token in request.headers["Authorization"]
                return challenge
            elif Requests.count == 2:
                # second request should still be unauthorized because we didn't authenticate with the correct scope
                assert bad_token in request.headers["Authorization"]
                return challenge
            raise ValueError("unexpected request")

        def get_token(*scopes, **kwargs):
            assert len(scopes) == 1
            TokenRequests.count += 1
            if TokenRequests.count == 1:
                # first request uses the scope given to the policy, and no tenant ID
                assert scopes[0] != expected_scope
                assert kwargs.get("tenant_id") is None
                return AccessToken(bad_token, 0)
            elif TokenRequests.count == 2:
                # second request should use the tenant specified in the auth challenge, and same scope as before
                assert scopes[0] != expected_scope
                assert kwargs.get("tenant_id") == challenge_tenant
                return AccessToken(bad_token, 0)
            raise ValueError("unexpected token request")

        credential = Mock(get_token=Mock(wraps=get_token))
        policy = BearerTokenChallengePolicy(credential, "scope")
        pipeline = Pipeline(policies=[policy], transport=Mock(send=send))
        pipeline.run(http_request("GET", "https://localhost"))

    tenant = "tenant-id"
    endpoint = f"https://authority.net/{tenant}/oauth2/authorize"
    resource = "https://challenge.resource"
    scope = f"{resource}/.default"

    # this challenge has no `resource` or `scope` field
    challenge_with_commas = Mock(
        status_code=401,
        headers={"WWW-Authenticate": f'Bearer authorization="{endpoint}"'},
    )
    # the request should fail after the challenge because we don't use the correct scope
    # after the second 4xx response, the policy should raise the authentication error
    test_with_challenge(challenge_with_commas, scope, tenant)
