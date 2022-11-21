# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from datetime import timedelta
from azure.communication.identity.aio import CommunicationIdentityClient
from azure.communication.identity import CommunicationTokenScope
from azure.communication.identity._shared.utils import parse_connection_str
from devtools_testutils import AzureRecordedTestCase, is_live
from devtools_testutils.aio import recorded_by_proxy_async
from _shared.communication_service_preparer import CommunicationPreparer
from _shared.utils import get_http_logging_policy
from _shared.fake_token_credential import FakeTokenCredential
from utils import is_token_expiration_within_allowed_deviation, generate_teams_user_aad_token, \
    skip_get_token_for_teams_user_test
from azure.identity.aio import DefaultAzureCredential
from acs_identity_decorator import acs_identity_decorator

class TestClientAsync(AzureRecordedTestCase):
    @CommunicationPreparer()
    @acs_identity_decorator
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
    @acs_identity_decorator
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
    @acs_identity_decorator
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
    @acs_identity_decorator
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
                await identity_client.create_user_and_token(scopes=None)

        assert ex is not None
        assert str(ex.value) == "'accessToken'"

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

        assert ex is not None
        assert str(ex.value) == "'NoneType' object has no attribute 'properties'"

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

        assert ex is not None
        assert str(ex.value) == 'No value for given attribute'

    @CommunicationPreparer()
    @recorded_by_proxy_async
    async def test_get_token_with_no_user(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )

        async with identity_client:
            with pytest.raises(Exception) as ex:
                await identity_client.get_token(user=None, scopes=[CommunicationTokenScope.CHAT])

        assert ex is not None
        assert str(ex.value) == "'NoneType' object has no attribute 'properties'"

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
                await identity_client.get_token(user, scopes=None)

        assert ex is not None
        assert str(ex.value.error.code) == 'ValidationError'

    @CommunicationPreparer()
    @acs_identity_decorator
    @recorded_by_proxy_async
    async def test_get_token_for_teams_user_from_managed_identity(self,
                                                                  communication_livetest_dynamic_connection_string):
        if skip_get_token_for_teams_user_test(self):
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
            aad_token, user_object_id = generate_teams_user_aad_token(self)
            token_response = await identity_client.get_token_for_teams_user(aad_token, self.m365_client_id,
                                                                            user_object_id)

        assert token_response.token is not None

    @CommunicationPreparer()
    @acs_identity_decorator
    @recorded_by_proxy_async
    async def test_get_token_for_teams_user_with_valid_params(self, communication_livetest_dynamic_connection_string):
        if skip_get_token_for_teams_user_test(self):
            return
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        async with identity_client:
            aad_token, user_object_id = generate_teams_user_aad_token(self)
            token_response = await identity_client.get_token_for_teams_user(aad_token, self.m365_client_id,
                                                                            user_object_id)

        assert token_response.token is not None

    @CommunicationPreparer()
    @acs_identity_decorator
    @recorded_by_proxy_async
    async def test_get_token_for_teams_user_with_invalid_token(self, communication_livetest_dynamic_connection_string):
        if skip_get_token_for_teams_user_test(self):
            return
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        async with identity_client:
            with pytest.raises(Exception) as ex:
                await identity_client.get_token_for_teams_user("invalid", self.m365_client_id, "")

        assert str(ex.value.status_code) == "401"
        assert ex.value.message is not None

    @CommunicationPreparer()
    @acs_identity_decorator
    @recorded_by_proxy_async
    async def test_get_token_for_teams_user_with_empty_token(self, communication_livetest_dynamic_connection_string):
        if skip_get_token_for_teams_user_test(self):
            return
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        async with identity_client:
            with pytest.raises(Exception) as ex:
                await identity_client.get_token_for_teams_user("", self.m365_client_id, "")

        assert str(ex.value.status_code) == "401"
        assert ex.value.message is not None

    @CommunicationPreparer()
    @acs_identity_decorator
    @recorded_by_proxy_async
    async def test_get_token_for_teams_user_with_expired_token(self, communication_livetest_dynamic_connection_string):
        if skip_get_token_for_teams_user_test(self):
            return
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        async with identity_client:
            with pytest.raises(Exception) as ex:
                _, user_object_id = generate_teams_user_aad_token(self)
                await identity_client.get_token_for_teams_user(self.expired_teams_token, self.m365_client_id,
                                                               user_object_id)

        assert str(ex.value.status_code) == "401"
        assert ex.value.message is not None

    @CommunicationPreparer()
    @acs_identity_decorator
    @recorded_by_proxy_async
    async def test_get_token_for_teams_user_with_empty_client_id(self,
                                                                 communication_livetest_dynamic_connection_string):
        if skip_get_token_for_teams_user_test(self):
            return
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        aad_token, user_object_id = generate_teams_user_aad_token(self)
        async with identity_client:
            with pytest.raises(Exception) as ex:
                await identity_client.get_token_for_teams_user(aad_token, "", user_object_id)

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    @CommunicationPreparer()
    @acs_identity_decorator
    @recorded_by_proxy_async
    async def test_get_token_for_teams_user_with_invalid_client_id(self,
                                                                   communication_livetest_dynamic_connection_string):
        if skip_get_token_for_teams_user_test(skip_get_token_for_teams_user_test):
            return
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        aad_token, user_object_id = generate_teams_user_aad_token(self)
        async with identity_client:
            with pytest.raises(Exception) as ex:
                await identity_client.get_token_for_teams_user(aad_token, "invalid", user_object_id)

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    @CommunicationPreparer()
    @acs_identity_decorator
    @recorded_by_proxy_async
    async def test_get_token_for_teams_user_with_wrong_client_id(self,
                                                                 communication_livetest_dynamic_connection_string):
        if skip_get_token_for_teams_user_test(self):
            return
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        aad_token, user_object_id = generate_teams_user_aad_token(self)
        async with identity_client:
            with pytest.raises(Exception) as ex:
                await identity_client.get_token_for_teams_user(aad_token, user_object_id, user_object_id)

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    @CommunicationPreparer()
    @acs_identity_decorator
    @recorded_by_proxy_async
    async def test_get_token_for_teams_user_with_invalid_user_object_id(self,
                                                                        communication_livetest_dynamic_connection_string):
        if skip_get_token_for_teams_user_test(self):
            return
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        aad_token, _ = generate_teams_user_aad_token(self)
        async with identity_client:
            with pytest.raises(Exception) as ex:
                await identity_client.get_token_for_teams_user(aad_token, self.m365_client_id, "invalid")

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    @CommunicationPreparer()
    @acs_identity_decorator
    @recorded_by_proxy_async
    async def test_get_token_for_teams_user_with_empty_user_object_id(self,
                                                                      communication_livetest_dynamic_connection_string):
        if skip_get_token_for_teams_user_test(self):
            return
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        aad_token, _ = generate_teams_user_aad_token(self)
        async with identity_client:
            with pytest.raises(Exception) as ex:
                await identity_client.get_token_for_teams_user(aad_token, self.m365_client_id, "")

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    @CommunicationPreparer()
    @acs_identity_decorator
    @recorded_by_proxy_async
    async def test_get_token_for_teams_user_with_wrong_user_object_id(self,
                                                                      communication_livetest_dynamic_connection_string):
        if skip_get_token_for_teams_user_test(self):
            return
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        aad_token, _ = generate_teams_user_aad_token(self)
        async with identity_client:
            with pytest.raises(Exception) as ex:
                await identity_client.get_token_for_teams_user(aad_token, self.m365_client_id, self.m365_client_id)

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None
