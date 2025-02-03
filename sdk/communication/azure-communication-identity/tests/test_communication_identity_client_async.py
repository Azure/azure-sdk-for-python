# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from datetime import timedelta
from azure.communication.identity import CommunicationTokenScope
from devtools_testutils import is_live, get_credential
from devtools_testutils.aio import recorded_by_proxy_async
from test_communication_identity_client import ArgumentPasser
from utils import is_token_expiration_within_allowed_deviation, token_scope_scenarios
from acs_identity_test_case import ACSIdentityTestCase
from azure.communication.identity.aio import CommunicationIdentityClient
from devtools_testutils.fake_credentials_async import AsyncFakeCredential
from _shared.utils import get_http_logging_policy


@pytest.mark.asyncio
class TestClientAsync(ACSIdentityTestCase):
    def setup_method(self):
        super().setUp()

    def create_client_from_connection_string(self):
        return CommunicationIdentityClient.from_connection_string(
            self.connection_str, http_logging_policy=get_http_logging_policy()
        )

    def create_client_from_token_credential(self):
        if not is_live():
            credential = AsyncFakeCredential()
        else:
            credential = get_credential(is_async=True)
        return CommunicationIdentityClient(self.endpoint, credential, http_logging_policy=get_http_logging_policy())

    @recorded_by_proxy_async
    async def test_create_user_from_token_credential(self):
        identity_client = self.create_client_from_token_credential()
        async with identity_client:
            user = await identity_client.create_user()

        assert user.properties.get("id") is not None

    @recorded_by_proxy_async
    async def test_create_user(self):
        identity_client = self.create_client_from_connection_string()
        async with identity_client:
            user = await identity_client.create_user()

        assert user.properties.get("id") is not None

    @pytest.mark.parametrize(
        "_, value",
        token_scope_scenarios,
    )
    @ArgumentPasser()
    @recorded_by_proxy_async
    async def test_create_user_and_token(self, _, scopes):
        identity_client = self.create_client_from_connection_string()
        async with identity_client:
            user, token_response = await identity_client.create_user_and_token(scopes=scopes)

        assert user.properties.get("id") is not None
        assert token_response.token is not None

    @recorded_by_proxy_async
    async def test_create_user_and_token_with_custom_minimum_validity(self):
        identity_client = self.create_client_from_connection_string()
        token_expires_in = timedelta(minutes=60)

        async with identity_client:
            user, token_response = await identity_client.create_user_and_token(
                scopes=[CommunicationTokenScope.CHAT], token_expires_in=token_expires_in
            )

        assert user.properties.get("id") is not None
        assert token_response.token is not None

        if is_live():
            assert is_token_expiration_within_allowed_deviation(token_expires_in, token_response.expires_on)

    @recorded_by_proxy_async
    async def test_create_user_and_token_with_custom_maximum_validity(self):
        identity_client = self.create_client_from_connection_string()
        token_expires_in = timedelta(minutes=1440)

        async with identity_client:
            user, token_response = await identity_client.create_user_and_token(
                scopes=[CommunicationTokenScope.CHAT], token_expires_in=token_expires_in
            )

        assert user.properties.get("id") is not None
        assert token_response.token is not None

        if is_live():
            assert is_token_expiration_within_allowed_deviation(token_expires_in, token_response.expires_on)

    @recorded_by_proxy_async
    async def test_create_user_and_token_with_custom_validity_under_minimum_allowed(
        self,
    ):
        identity_client = self.create_client_from_connection_string()
        token_expires_in = timedelta(minutes=59)

        async with identity_client:
            with pytest.raises(Exception) as ex:
                await identity_client.create_user_and_token(
                    scopes=[CommunicationTokenScope.CHAT],
                    token_expires_in=token_expires_in,
                )

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    @recorded_by_proxy_async
    async def test_create_user_and_token_with_custom_validity_over_maximum_allowed(
        self,
    ):
        identity_client = self.create_client_from_connection_string()
        token_expires_in = timedelta(minutes=1441)

        async with identity_client:
            with pytest.raises(Exception) as ex:
                await identity_client.create_user_and_token(
                    scopes=[CommunicationTokenScope.CHAT],
                    token_expires_in=token_expires_in,
                )

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    @pytest.mark.parametrize(
        "_, value",
        token_scope_scenarios,
    )
    @ArgumentPasser()
    @recorded_by_proxy_async
    async def test_get_token_from_token_credential(self, _, scopes):
        identity_client = self.create_client_from_token_credential()
        async with identity_client:
            user = await identity_client.create_user()
            token_response = await identity_client.get_token(user, scopes=scopes)

        assert user.properties.get("id") is not None
        assert token_response.token is not None

    @recorded_by_proxy_async
    async def test_get_token(self):
        identity_client = self.create_client_from_connection_string()
        async with identity_client:
            user = await identity_client.create_user()
            token_response = await identity_client.get_token(user, scopes=[CommunicationTokenScope.CHAT])

        assert user.properties.get("id") is not None
        assert token_response.token is not None

    @recorded_by_proxy_async
    async def test_get_token_with_custom_minimum_validity(self):
        identity_client = self.create_client_from_connection_string()
        token_expires_in = timedelta(minutes=60)

        async with identity_client:
            user = await identity_client.create_user()
            token_response = await identity_client.get_token(
                user,
                scopes=[CommunicationTokenScope.CHAT],
                token_expires_in=token_expires_in,
            )

        assert user.properties.get("id") is not None
        assert token_response.token is not None

        if is_live():
            assert is_token_expiration_within_allowed_deviation(token_expires_in, token_response.expires_on)

    @recorded_by_proxy_async
    async def test_get_token_with_custom_maximum_validity(self):
        identity_client = self.create_client_from_connection_string()
        token_expires_in = timedelta(minutes=1440)

        async with identity_client:
            user = await identity_client.create_user()
            token_response = await identity_client.get_token(
                user,
                scopes=[CommunicationTokenScope.CHAT],
                token_expires_in=token_expires_in,
            )

        assert user.properties.get("id") is not None
        assert token_response.token is not None

        if is_live():
            assert is_token_expiration_within_allowed_deviation(token_expires_in, token_response.expires_on)

    @recorded_by_proxy_async
    async def test_get_token_with_custom_validity_under_minimum_allowed(self):
        identity_client = self.create_client_from_connection_string()
        token_expires_in = timedelta(minutes=59)

        async with identity_client:
            with pytest.raises(Exception) as ex:
                user = await identity_client.create_user()
                await identity_client.get_token(
                    user,
                    scopes=[CommunicationTokenScope.CHAT],
                    token_expires_in=token_expires_in,
                )

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    @recorded_by_proxy_async
    async def test_get_token_with_custom_validity_over_maximum_allowed(self):
        identity_client = self.create_client_from_connection_string()
        token_expires_in = timedelta(minutes=1441)

        async with identity_client:
            with pytest.raises(Exception) as ex:
                user = await identity_client.create_user()
                await identity_client.get_token(
                    user,
                    scopes=[CommunicationTokenScope.CHAT],
                    token_expires_in=token_expires_in,
                )

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    @recorded_by_proxy_async
    async def test_revoke_tokens_from_token_credential(self):
        identity_client = self.create_client_from_token_credential()
        async with identity_client:
            user = await identity_client.create_user()
            token_response = await identity_client.get_token(user, scopes=[CommunicationTokenScope.CHAT])
            await identity_client.revoke_tokens(user)

        assert user.properties.get("id") is not None
        assert token_response.token is not None

    @recorded_by_proxy_async
    async def test_revoke_tokens(self):
        identity_client = self.create_client_from_connection_string()
        async with identity_client:
            user = await identity_client.create_user()
            token_response = await identity_client.get_token(user, scopes=[CommunicationTokenScope.CHAT])
            await identity_client.revoke_tokens(user)

        assert user.properties.get("id") is not None
        assert token_response.token is not None

    @recorded_by_proxy_async
    async def test_delete_user_from_token_credential(self):
        identity_client = self.create_client_from_token_credential()
        async with identity_client:
            user = await identity_client.create_user()
            await identity_client.delete_user(user)

        assert user.properties.get("id") is not None

    @recorded_by_proxy_async
    async def test_delete_user(self):
        identity_client = self.create_client_from_connection_string()
        async with identity_client:
            user = await identity_client.create_user()
            await identity_client.delete_user(user)

        assert user.properties.get("id") is not None

    @recorded_by_proxy_async
    async def test_create_user_and_token_with_no_scopes(self):
        identity_client = self.create_client_from_connection_string()
        async with identity_client:
            with pytest.raises(Exception) as ex:
                await identity_client.create_user_and_token(scopes=None)

        assert ex is not None and ex.value is not None

    @recorded_by_proxy_async
    async def test_delete_user_with_no_user(self):
        identity_client = self.create_client_from_connection_string()
        async with identity_client:
            with pytest.raises(Exception) as ex:
                await identity_client.delete_user(user=None)

        assert ex is not None and ex.value is not None

    @recorded_by_proxy_async
    async def test_revoke_tokens_with_no_user(self):
        identity_client = self.create_client_from_connection_string()
        async with identity_client:
            with pytest.raises(Exception) as ex:
                await identity_client.revoke_tokens(user=None)

        assert ex is not None and ex.value is not None

    @recorded_by_proxy_async
    async def test_get_token_with_no_user(self):
        identity_client = self.create_client_from_connection_string()
        async with identity_client:
            with pytest.raises(Exception) as ex:
                await identity_client.get_token(user=None, scopes=[CommunicationTokenScope.CHAT])

        assert ex is not None and ex.value is not None

    @recorded_by_proxy_async
    async def test_get_token_with_no_scopes(self):
        identity_client = self.create_client_from_connection_string()
        async with identity_client:
            with pytest.raises(Exception) as ex:
                user = await identity_client.create_user()
                await identity_client.get_token(user, scopes=None)

        assert ex is not None and ex.value is not None

    @recorded_by_proxy_async
    async def test_get_token_for_teams_user_from_token_credential(self):
        if self.skip_get_token_for_teams_user_test():
            return
        identity_client = self.create_client_from_token_credential()
        async with identity_client:
            aad_token, user_object_id = self.generate_teams_user_aad_token()
            token_response = await identity_client.get_token_for_teams_user(
                aad_token, self.m365_client_id, user_object_id
            )

        assert token_response.token is not None

    @recorded_by_proxy_async
    async def test_get_token_for_teams_user_with_valid_params(self):
        if self.skip_get_token_for_teams_user_test():
            return
        identity_client = self.create_client_from_connection_string()
        async with identity_client:
            aad_token, user_object_id = self.generate_teams_user_aad_token()
            token_response = await identity_client.get_token_for_teams_user(
                aad_token, self.m365_client_id, user_object_id
            )

        assert token_response.token is not None

    @recorded_by_proxy_async
    async def test_get_token_for_teams_user_with_invalid_token(self):
        if self.skip_get_token_for_teams_user_test():
            return
        identity_client = self.create_client_from_connection_string()
        async with identity_client:
            with pytest.raises(Exception) as ex:
                await identity_client.get_token_for_teams_user("invalid", self.m365_client_id, "")

        assert str(ex.value.status_code) == "401"
        assert ex.value.message is not None

    @recorded_by_proxy_async
    async def test_get_token_for_teams_user_with_empty_token(self):
        if self.skip_get_token_for_teams_user_test():
            return
        identity_client = self.create_client_from_connection_string()
        async with identity_client:
            with pytest.raises(Exception) as ex:
                await identity_client.get_token_for_teams_user("", self.m365_client_id, "")

        assert str(ex.value.status_code) == "401"
        assert ex.value.message is not None

    @recorded_by_proxy_async
    async def test_get_token_for_teams_user_with_expired_token(self):
        if self.skip_get_token_for_teams_user_test():
            return
        identity_client = self.create_client_from_connection_string()
        async with identity_client:
            with pytest.raises(Exception) as ex:
                _, user_object_id = self.generate_teams_user_aad_token()
                await identity_client.get_token_for_teams_user(
                    self.expired_teams_token, self.m365_client_id, user_object_id
                )

        assert str(ex.value.status_code) == "401"
        assert ex.value.message is not None

    @recorded_by_proxy_async
    async def test_get_token_for_teams_user_with_empty_client_id(self):
        if self.skip_get_token_for_teams_user_test():
            return
        identity_client = self.create_client_from_connection_string()
        aad_token, user_object_id = self.generate_teams_user_aad_token()
        async with identity_client:
            with pytest.raises(Exception) as ex:
                await identity_client.get_token_for_teams_user(aad_token, "", user_object_id)

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    @recorded_by_proxy_async
    async def test_get_token_for_teams_user_with_invalid_client_id(self):
        if self.skip_get_token_for_teams_user_test():
            return
        identity_client = self.create_client_from_connection_string()
        aad_token, user_object_id = self.generate_teams_user_aad_token()
        async with identity_client:
            with pytest.raises(Exception) as ex:
                await identity_client.get_token_for_teams_user(aad_token, "invalid", user_object_id)

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    @recorded_by_proxy_async
    async def test_get_token_for_teams_user_with_wrong_client_id(self):
        if self.skip_get_token_for_teams_user_test():
            return
        identity_client = self.create_client_from_connection_string()
        aad_token, user_object_id = self.generate_teams_user_aad_token()
        async with identity_client:
            with pytest.raises(Exception) as ex:
                await identity_client.get_token_for_teams_user(aad_token, user_object_id, user_object_id)

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    @recorded_by_proxy_async
    async def test_get_token_for_teams_user_with_invalid_user_object_id(self):
        if self.skip_get_token_for_teams_user_test():
            return
        identity_client = self.create_client_from_connection_string()
        aad_token, _ = self.generate_teams_user_aad_token()
        async with identity_client:
            with pytest.raises(Exception) as ex:
                await identity_client.get_token_for_teams_user(aad_token, self.m365_client_id, "invalid")

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    @recorded_by_proxy_async
    async def test_get_token_for_teams_user_with_empty_user_object_id(self):
        if self.skip_get_token_for_teams_user_test():
            return
        identity_client = self.create_client_from_connection_string()
        aad_token, _ = self.generate_teams_user_aad_token()
        async with identity_client:
            with pytest.raises(Exception) as ex:
                await identity_client.get_token_for_teams_user(aad_token, self.m365_client_id, "")

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    @recorded_by_proxy_async
    async def test_get_token_for_teams_user_with_wrong_user_object_id(self):
        if self.skip_get_token_for_teams_user_test():
            return
        identity_client = self.create_client_from_connection_string()
        aad_token, _ = self.generate_teams_user_aad_token()
        async with identity_client:
            with pytest.raises(Exception) as ex:
                await identity_client.get_token_for_teams_user(aad_token, self.m365_client_id, self.m365_client_id)

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None
