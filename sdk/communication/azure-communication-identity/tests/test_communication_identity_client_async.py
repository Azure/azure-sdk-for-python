# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import pytest
from datetime import timedelta
from azure.core.credentials import AccessToken
from azure.communication.identity.aio import CommunicationIdentityClient
from azure.communication.identity import CommunicationTokenScope
from azure.communication.identity._shared.utils import parse_connection_str
from devtools_testutils import AzureRecordedTestCase, is_live
from devtools_testutils.aio import recorded_by_proxy_async
from _shared.communication_service_preparer import CommunicationPreparer
from _shared.utils import get_http_logging_policy
from utils import is_token_expiration_within_allowed_deviation
from azure.identity.aio import DefaultAzureCredential
from msal import PublicClientApplication


class FakeTokenCredential(object):
    def __init__(self):
        self.token = AccessToken("Fake Token", 0)

    async def get_token(self, *args):
        return self.token


class TestClientAsync(AzureRecordedTestCase):
    def setUp(self):
        self.communication_environment()             #TODO: TRY to remove this on pipelines

    @CommunicationPreparer()
    @recorded_by_proxy_async
    async def test_create_user_from_managed_identity(self, communication_livetest_dynamic_connection_string):
        endpoint, access_key = parse_connection_str(communication_livetest_dynamic_connection_string)
        if not is_live():
            credential = FakeTokenCredential()
        else:
            credential = DefaultAzureCredential()
        identity_client = CommunicationIdentityClient(
            endpoint,
            credential,
            http_logging_policy=get_http_logging_policy()
        )
        async with identity_client:
            user = await identity_client.create_user()

        assert user.properties.get('id') is not None

    @CommunicationPreparer()
    @recorded_by_proxy_async
    async def test_create_user(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        async with identity_client:
            user = await identity_client.create_user()

        assert user.properties.get('id') is not None

    @CommunicationPreparer()
    @recorded_by_proxy_async
    async def test_create_user_and_token(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        async with identity_client:
            user, token_response = await identity_client.create_user_and_token(scopes=[CommunicationTokenScope.CHAT])

        assert user.properties.get('id') is not None
        assert token_response.token is not None

    @CommunicationPreparer()
    @recorded_by_proxy_async
    async def test_create_user_and_token_with_custom_minimum_validity(self,
                                                                      communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )

        token_expires_in = timedelta(minutes=60)

        async with identity_client:
            user, token_response = await identity_client.create_user_and_token(scopes=[CommunicationTokenScope.CHAT],
                                                                               token_expires_in=token_expires_in)

        assert user.properties.get('id') is not None
        assert token_response.token is not None

        if is_live():
            assert is_token_expiration_within_allowed_deviation(token_expires_in, token_response.expires_on)

    @CommunicationPreparer()
    @recorded_by_proxy_async
    async def test_create_user_and_token_with_custom_maximum_validity(self,
                                                                      communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )

        token_expires_in = timedelta(minutes=1440)

        async with identity_client:
            user, token_response = await identity_client.create_user_and_token(scopes=[CommunicationTokenScope.CHAT],
                                                                               token_expires_in=token_expires_in)

        assert user.properties.get('id') is not None
        assert token_response.token is not None

        if is_live():
            assert is_token_expiration_within_allowed_deviation(token_expires_in, token_response.expires_on)

    @CommunicationPreparer()
    @recorded_by_proxy_async
    async def test_create_user_and_token_with_custom_validity_under_minimum_allowed(self,
                                                                                    communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )

        token_expires_in = timedelta(minutes=59)

        async with identity_client:
            with pytest.raises(Exception) as ex:
                await identity_client.create_user_and_token(scopes=[CommunicationTokenScope.CHAT],
                                                            token_expires_in=token_expires_in)

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    @CommunicationPreparer()
    @recorded_by_proxy_async
    async def test_create_user_and_token_with_custom_validity_over_maximum_allowed(self,
                                                                                   communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )

        token_expires_in = timedelta(minutes=1441)

        async with identity_client:
            with pytest.raises(Exception) as ex:
                await identity_client.create_user_and_token(scopes=[CommunicationTokenScope.CHAT],
                                                            token_expires_in=token_expires_in)

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    @CommunicationPreparer()
    @recorded_by_proxy_async
    async def test_get_token_from_managed_identity(self, communication_livetest_dynamic_connection_string):
        endpoint, access_key = parse_connection_str(communication_livetest_dynamic_connection_string)
        if not is_live():
            credential = FakeTokenCredential()
        else:
            credential = DefaultAzureCredential()
        identity_client = CommunicationIdentityClient(
            endpoint,
            credential,
            http_logging_policy=get_http_logging_policy()
        )
        async with identity_client:
            user = await identity_client.create_user()
            token_response = await identity_client.get_token(user, scopes=[CommunicationTokenScope.CHAT])

        assert user.properties.get('id') is not None
        assert token_response.token is not None

    @CommunicationPreparer()
    @recorded_by_proxy_async
    async def test_get_token(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        async with identity_client:
            user = await identity_client.create_user()
            token_response = await identity_client.get_token(user, scopes=[CommunicationTokenScope.CHAT])

        assert user.properties.get('id') is not None
        assert token_response.token is not None

    @CommunicationPreparer()
    @recorded_by_proxy_async
    async def test_get_token_with_custom_minimum_validity(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )

        token_expires_in = timedelta(minutes=60)

        async with identity_client:
            user = await identity_client.create_user()
            token_response = await identity_client.get_token(user, scopes=[CommunicationTokenScope.CHAT],
                                                             token_expires_in=token_expires_in)

        assert user.properties.get('id') is not None
        assert token_response.token is not None

        if is_live():
            assert is_token_expiration_within_allowed_deviation(token_expires_in, token_response.expires_on)

    @CommunicationPreparer()
    @recorded_by_proxy_async
    async def test_get_token_with_custom_maximum_validity(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )

        token_expires_in = timedelta(minutes=1440)

        async with identity_client:
            user = await identity_client.create_user()
            token_response = await identity_client.get_token(user, scopes=[CommunicationTokenScope.CHAT],
                                                             token_expires_in=token_expires_in)

        assert user.properties.get('id') is not None
        assert token_response.token is not None

        if is_live():
            assert is_token_expiration_within_allowed_deviation(token_expires_in, token_response.expires_on)

    @CommunicationPreparer()
    @recorded_by_proxy_async
    async def test_get_token_with_custom_validity_under_minimum_allowed(self,
                                                                        communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )

        token_expires_in = timedelta(minutes=59)

        async with identity_client:
            with pytest.raises(Exception) as ex:
                user = await identity_client.create_user()
                await identity_client.get_token(user, scopes=[CommunicationTokenScope.CHAT],
                                                token_expires_in=token_expires_in)

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    @CommunicationPreparer()
    @recorded_by_proxy_async
    async def test_get_token_with_custom_validity_over_maximum_allowed(self,
                                                                       communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )

        token_expires_in = timedelta(minutes=1441)

        async with identity_client:
            with pytest.raises(Exception) as ex:
                user = await identity_client.create_user()
                await identity_client.get_token(user, scopes=[CommunicationTokenScope.CHAT],
                                                token_expires_in=token_expires_in)

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    @CommunicationPreparer()
    @recorded_by_proxy_async
    async def test_revoke_tokens_from_managed_identity(self, communication_livetest_dynamic_connection_string):
        endpoint, access_key = parse_connection_str(communication_livetest_dynamic_connection_string)
        if not is_live():
            credential = FakeTokenCredential()
        else:
            credential = DefaultAzureCredential()
        identity_client = CommunicationIdentityClient(
            endpoint,
            credential,
            http_logging_policy=get_http_logging_policy()
        )
        async with identity_client:
            user = await identity_client.create_user()
            token_response = await identity_client.get_token(user, scopes=[CommunicationTokenScope.CHAT])
            await identity_client.revoke_tokens(user)

        assert user.properties.get('id') is not None
        assert token_response.token is not None

    @CommunicationPreparer()
    @recorded_by_proxy_async
    async def test_revoke_tokens(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        async with identity_client:
            user = await identity_client.create_user()
            token_response = await identity_client.get_token(user, scopes=[CommunicationTokenScope.CHAT])
            await identity_client.revoke_tokens(user)

        assert user.properties.get('id') is not None
        assert token_response.token is not None

    @CommunicationPreparer()
    @recorded_by_proxy_async
    async def test_delete_user_from_managed_identity(self, communication_livetest_dynamic_connection_string):
        endpoint, access_key = parse_connection_str(communication_livetest_dynamic_connection_string)
        if not is_live():
            credential = FakeTokenCredential()
        else:
            credential = DefaultAzureCredential()
        identity_client = CommunicationIdentityClient(
            endpoint,
            credential,
            http_logging_policy=get_http_logging_policy()
        )
        async with identity_client:
            user = await identity_client.create_user()
            await identity_client.delete_user(user)

        assert user.properties.get('id') is not None

    @CommunicationPreparer()
    @recorded_by_proxy_async
    async def test_delete_user(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        async with identity_client:
            user = await identity_client.create_user()
            await identity_client.delete_user(user)

        assert user.properties.get('id') is not None

    @CommunicationPreparer()
    @recorded_by_proxy_async
    async def test_create_user_and_token_with_no_scopes(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )

        async with identity_client:
            with pytest.raises(Exception) as ex:
                user, token_response = await identity_client.create_user_and_token(scopes=None)

    @CommunicationPreparer()
    @recorded_by_proxy_async
    async def test_delete_user_with_no_user(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )

        async with identity_client:
            with pytest.raises(Exception) as ex:
                await identity_client.delete_user(user=None)

    @CommunicationPreparer()
    @recorded_by_proxy_async
    async def test_revoke_tokens_with_no_user(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )

        async with identity_client:
            with pytest.raises(Exception) as ex:
                await identity_client.revoke_tokens(user=None)

    @CommunicationPreparer()
    @recorded_by_proxy_async
    async def test_get_token_with_no_user(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )

        async with identity_client:
            with pytest.raises(Exception) as ex:
                token_response = await identity_client.get_token(user=None, scopes=[CommunicationTokenScope.CHAT])

    @CommunicationPreparer()
    @recorded_by_proxy_async
    async def test_get_token_with_no_scopes(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )

        async with identity_client:
            with pytest.raises(Exception) as ex:
                user = await identity_client.create_user()
                token_response = await identity_client.get_token(user, scopes=None)

    @CommunicationPreparer()
    @recorded_by_proxy_async
    async def test_get_token_for_teams_user_from_managed_identity(self,
                                                                  communication_livetest_dynamic_connection_string):
        self.communication_environment()
        if self.skip_get_token_for_teams_user_test():
            return
        endpoint, access_key = parse_connection_str(communication_livetest_dynamic_connection_string)
        if not is_live():
            credential = FakeTokenCredential()
        else:
            credential = DefaultAzureCredential()
        identity_client = CommunicationIdentityClient(
            endpoint,
            credential,
            http_logging_policy=get_http_logging_policy()
        )
        async with identity_client:
            aad_token, user_object_id = self.generate_teams_user_aad_token()
            token_response = await identity_client.get_token_for_teams_user(aad_token, self.m365_client_id,
                                                                            user_object_id)

        assert token_response.token is not None

    @CommunicationPreparer()
    @recorded_by_proxy_async
    async def test_get_token_for_teams_user_with_valid_params(self, communication_livetest_dynamic_connection_string):
        self.communication_environment()
        if self.skip_get_token_for_teams_user_test():
            return
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        async with identity_client:
            aad_token, user_object_id = self.generate_teams_user_aad_token()
            token_response = await identity_client.get_token_for_teams_user(aad_token, self.m365_client_id,
                                                                            user_object_id)

        assert token_response.token is not None

    @CommunicationPreparer()
    @recorded_by_proxy_async
    async def test_get_token_for_teams_user_with_invalid_token(self, communication_livetest_dynamic_connection_string):
        self.communication_environment()
        if self.skip_get_token_for_teams_user_test():
            return
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        async with identity_client:
            with pytest.raises(Exception) as ex:
                token_response = await identity_client.get_token_for_teams_user("invalid", self.m365_client_id, "")

        assert str(ex.value.status_code) == "401"
        assert ex.value.message is not None

    @CommunicationPreparer()
    @recorded_by_proxy_async
    async def test_get_token_for_teams_user_with_empty_token(self, communication_livetest_dynamic_connection_string):
        self.communication_environment()
        if self.skip_get_token_for_teams_user_test():
            return
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        async with identity_client:
            with pytest.raises(Exception) as ex:
                token_response = await identity_client.get_token_for_teams_user("", self.m365_client_id, "")

        assert str(ex.value.status_code) == "401"
        assert ex.value.message is not None

    @CommunicationPreparer()
    @recorded_by_proxy_async
    async def test_get_token_for_teams_user_with_expired_token(self, communication_livetest_dynamic_connection_string):
        self.communication_environment()
        if self.skip_get_token_for_teams_user_test():
            return
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        async with identity_client:
            with pytest.raises(Exception) as ex:
                _, user_object_id = self.generate_teams_user_aad_token()
                token_response = await identity_client.get_token_for_teams_user(self.expired_teams_token,
                                                                                self.m365_client_id, user_object_id)

        assert str(ex.value.status_code) == "401"
        assert ex.value.message is not None

    @CommunicationPreparer()
    @recorded_by_proxy_async
    async def test_get_token_for_teams_user_with_empty_client_id(self,
                                                                 communication_livetest_dynamic_connection_string):
        self.communication_environment()
        if (self.skip_get_token_for_teams_user_test()):
            return
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        aad_token, user_object_id = self.generate_teams_user_aad_token()
        async with identity_client:
            with pytest.raises(Exception) as ex:
                token_response = await identity_client.get_token_for_teams_user(aad_token, "", user_object_id)
        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    @CommunicationPreparer()
    @recorded_by_proxy_async
    async def test_get_token_for_teams_user_with_invalid_client_id(self,
                                                                   communication_livetest_dynamic_connection_string):
        self.communication_environment()
        if (self.skip_get_token_for_teams_user_test()):
            return
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        aad_token, user_object_id = self.generate_teams_user_aad_token()
        async with identity_client:
            with pytest.raises(Exception) as ex:
                token_response = await identity_client.get_token_for_teams_user(aad_token, "invalid", user_object_id)
        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    @CommunicationPreparer()
    @recorded_by_proxy_async
    async def test_get_token_for_teams_user_with_wrong_client_id(self,
                                                                 communication_livetest_dynamic_connection_string):
        self.communication_environment()
        if (self.skip_get_token_for_teams_user_test()):
            return
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        aad_token, user_object_id = self.generate_teams_user_aad_token()
        async with identity_client:
            with pytest.raises(Exception) as ex:
                token_response = await identity_client.get_token_for_teams_user(aad_token, user_object_id,
                                                                                user_object_id)

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    @CommunicationPreparer()
    @recorded_by_proxy_async
    async def test_get_token_for_teams_user_with_invalid_user_object_id(self,
                                                                        communication_livetest_dynamic_connection_string):
        self.communication_environment()
        if (self.skip_get_token_for_teams_user_test()):
            return
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        aad_token, _ = self.generate_teams_user_aad_token()
        async with identity_client:
            with pytest.raises(Exception) as ex:
                token_response = await identity_client.get_token_for_teams_user(aad_token, self.m365_client_id,
                                                                                "invalid")

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    @CommunicationPreparer()
    @recorded_by_proxy_async
    async def test_get_token_for_teams_user_with_empty_user_object_id(self,
                                                                      communication_livetest_dynamic_connection_string):
        self.communication_environment()
        if (self.skip_get_token_for_teams_user_test()):
            return
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        aad_token, _ = self.generate_teams_user_aad_token()
        async with identity_client:
            with pytest.raises(Exception) as ex:
                token_response = await identity_client.get_token_for_teams_user(aad_token, self.m365_client_id, "")

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    @CommunicationPreparer()
    @recorded_by_proxy_async
    async def test_get_token_for_teams_user_with_wrong_user_object_id(self,
                                                                      communication_livetest_dynamic_connection_string):
        self.communication_environment()
        if (self.skip_get_token_for_teams_user_test()):
            return
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        aad_token, _ = self.generate_teams_user_aad_token()
        async with identity_client:
            with pytest.raises(Exception) as ex:
                token_response = await identity_client.get_token_for_teams_user(aad_token, self.m365_client_id,
                                                                                self.m365_client_id)

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None
    def communication_environment(self): #TODO:remove?
        if self.is_playback():
            self.connection_str = "endpoint=https://sanitized.communication.azure.com/;accesskey=fake==="
            self.m365_client_id = "sanitized"
            self.m365_aad_authority = "sanitized"
            self.m365_aad_tenant = "sanitized"
            self.msal_username = "sanitized"
            self.msal_password = "sanitized"
            self.expired_teams_token = "sanitized"
            self.skip_get_token_for_teams_user_tests = "true"
        else:
            self.connection_str = os.getenv('COMMUNICATION_LIVETEST_DYNAMIC_CONNECTION_STRING') or \
                                  os.getenv('COMMUNICATION_LIVETEST_STATIC_CONNECTION_STRING')
            self.connection_str = os.getenv('COMMUNICATION_LIVETEST_DYNAMIC_CONNECTION_STRING')
            self.m365_client_id = os.getenv('COMMUNICATION_M365_APP_ID')
            self.m365_aad_authority = os.getenv('COMMUNICATION_M365_AAD_AUTHORITY')
            self.m365_aad_tenant = os.getenv('COMMUNICATION_M365_AAD_TENANT')
            self.msal_username = os.getenv('COMMUNICATION_MSAL_USERNAME')
            self.msal_password = os.getenv('COMMUNICATION_MSAL_PASSWORD')
            self.expired_teams_token = os.getenv('COMMUNICATION_EXPIRED_TEAMS_TOKEN')
            endpoint, _ = parse_connection_str(self.connection_str)
            self._resource_name = endpoint.split(".")[0]
            self.skip_get_token_for_teams_user_tests = os.getenv('SKIP_INT_IDENTITY_EXCHANGE_TOKEN_TEST')

    def skip_get_token_for_teams_user_test(self):
        return str(self.skip_get_token_for_teams_user_tests).lower() == 'true'

    def generate_teams_user_aad_token(self):
        if self.is_playback():
            teams_user_aad_token = "sanitized"
            teams_user_oid = "sanitized"
        else:
            msal_app = PublicClientApplication(
                client_id=self.m365_client_id,
                authority="{}/{}".format(self.m365_aad_authority, self.m365_aad_tenant))
            scopes = [
                "https://auth.msft.communication.azure.com/Teams.ManageCalls",
                "https://auth.msft.communication.azure.com/Teams.ManageChats"
            ]
            result = msal_app.acquire_token_by_username_password(username=self.msal_username, password=self.msal_password, scopes=scopes)
            teams_user_aad_token = result["access_token"]
            teams_user_oid = result["id_token_claims"]["oid"]
        return teams_user_aad_token, teams_user_oid
