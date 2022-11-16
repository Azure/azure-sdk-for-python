# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import pytest
from datetime import timedelta
from azure.communication.identity import CommunicationIdentityClient
from azure.communication.identity import CommunicationTokenScope
from azure.core.credentials import AccessToken
from devtools_testutils import AzureRecordedTestCase, is_live, recorded_by_proxy
from _shared.communication_service_preparer import CommunicationPreparer
from _shared.utils import get_http_logging_policy
from utils import is_token_expiration_within_allowed_deviation
from azure.identity import DefaultAzureCredential
from azure.communication.identity._shared.utils import parse_connection_str
from msal import PublicClientApplication
from acs_identity_decorator import acs_identity_decorator


class ArgumentPasser:
    def __call__(self, fn):
        def _wrapper(test_class, _, value, **kwargs):
            fn(test_class, _, value, **kwargs)
        return _wrapper


class FakeTokenCredential(object):
    def __init__(self):
        self.token = AccessToken("Fake Token", 0)

    def get_token(self, *args):
        return self.token


class TestClient(AzureRecordedTestCase):
    @CommunicationPreparer()
    @recorded_by_proxy
    def test_create_user_from_managed_identity(self, communication_livetest_dynamic_connection_string):
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
        user = identity_client.create_user()

        assert user.properties.get('id') is not None

    @CommunicationPreparer()
    @recorded_by_proxy
    def test_create_user(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        user = identity_client.create_user()

        assert user.properties.get('id') is not None

    @CommunicationPreparer()
    @recorded_by_proxy
    def test_create_user_and_token(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        user, token_response = identity_client.create_user_and_token(scopes=[CommunicationTokenScope.CHAT])

        assert user.properties.get('id') is not None
        assert token_response.token is not None

    @CommunicationPreparer()
    @pytest.mark.parametrize("_, value", [("min_valid_hours", 1), ("max_valid_hours", 24)])
    @ArgumentPasser()
    @acs_identity_decorator
    @recorded_by_proxy
    def test_create_user_and_token_with_valid_custom_expirations_new(self, _, valid_hours):
        identity_client = CommunicationIdentityClient.from_connection_string(
            self.connection_str,
            http_logging_policy=get_http_logging_policy()
        )

        token_expires_in = timedelta(hours=valid_hours)
        user, token_response = identity_client.create_user_and_token(scopes=[CommunicationTokenScope.CHAT],
                                                                     token_expires_in=token_expires_in)
        assert user.properties.get('id') is not None
        assert token_response.token is not None

        if is_live():
            assert is_token_expiration_within_allowed_deviation(token_expires_in, token_response.expires_on)

    @CommunicationPreparer()
    @pytest.mark.parametrize("_, value", [("min_invalid_mins", 59), ("max_invalid_mins", 1441)])
    @ArgumentPasser()
    @acs_identity_decorator
    @recorded_by_proxy
    def test_create_user_and_token_with_invalid_custom_expirations(self, _, time):
        identity_client = CommunicationIdentityClient.from_connection_string(
            self.connection_str,
            http_logging_policy=get_http_logging_policy()
        )

        token_expires_in = timedelta(minutes=time)

        with pytest.raises(Exception) as ex:
            identity_client.create_user_and_token(scopes=[CommunicationTokenScope.CHAT], token_expires_in=token_expires_in)

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    @CommunicationPreparer()
    @recorded_by_proxy
    def test_get_token_from_managed_identity(self, communication_livetest_dynamic_connection_string):
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
        user = identity_client.create_user()

        token_response = identity_client.get_token(user, scopes=[CommunicationTokenScope.CHAT])

        assert user.properties.get('id') is not None
        assert token_response.token is not None

    @CommunicationPreparer()
    @recorded_by_proxy
    def test_get_token(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        user = identity_client.create_user()

        token_response = identity_client.get_token(user, scopes=[CommunicationTokenScope.CHAT])

        assert user.properties.get('id') is not None
        assert token_response.token is not None

    @CommunicationPreparer()
    @pytest.mark.parametrize("_, value", [("min_valid_hours", 1), ("max_valid_hours", 24)])
    @ArgumentPasser()
    @acs_identity_decorator
    @recorded_by_proxy
    def test_get_token_with_valid_custom_expirations(self, _, value):
        identity_client = CommunicationIdentityClient.from_connection_string(
            self.connection_str,
            http_logging_policy=get_http_logging_policy()
        )
        user = identity_client.create_user()

        token_expires_in = timedelta(hours=value)
        token_response = identity_client.get_token(user, scopes=[CommunicationTokenScope.CHAT],
                                                   token_expires_in=token_expires_in)

        assert user.properties.get('id') is not None
        assert token_response.token is not None
        if is_live():
            assert is_token_expiration_within_allowed_deviation(token_expires_in, token_response.expires_on)

    @CommunicationPreparer()
    @pytest.mark.parametrize("_, value", [("min_invalid_mins", 59), ("max_invalid_mins", 1441)])
    @ArgumentPasser()
    @acs_identity_decorator
    @recorded_by_proxy
    def test_get_token_with_invalid_custom_expirations(self, _, value):
        identity_client = CommunicationIdentityClient.from_connection_string(
            self.connection_str,
            http_logging_policy=get_http_logging_policy()
        )
        user = identity_client.create_user()

        token_expires_in = timedelta(minutes=value)

        with pytest.raises(Exception) as ex:
            identity_client.get_token(user, scopes=[CommunicationTokenScope.CHAT], token_expires_in=token_expires_in)

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    @CommunicationPreparer()
    @recorded_by_proxy
    def test_revoke_tokens_from_managed_identity(self, communication_livetest_dynamic_connection_string):
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
        user = identity_client.create_user()

        token_response = identity_client.get_token(user, scopes=[CommunicationTokenScope.CHAT])
        identity_client.revoke_tokens(user)

        assert user.properties.get('id') is not None
        assert token_response.token is not None

    @CommunicationPreparer()
    @recorded_by_proxy
    def test_revoke_tokens(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        user = identity_client.create_user()

        token_response = identity_client.get_token(user, scopes=[CommunicationTokenScope.CHAT])
        identity_client.revoke_tokens(user)

        assert user.properties.get('id') is not None
        assert token_response.token is not None

    @CommunicationPreparer()
    @recorded_by_proxy
    def test_delete_user_from_managed_identity(self, communication_livetest_dynamic_connection_string):
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
        user = identity_client.create_user()

        identity_client.delete_user(user)

        assert user.properties.get('id') is not None

    @CommunicationPreparer()
    @recorded_by_proxy
    def test_delete_user(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        user = identity_client.create_user()

        identity_client.delete_user(user)

        assert user.properties.get('id') is not None

    @CommunicationPreparer()
    @recorded_by_proxy
    def test_create_user_and_token_with_no_scopes(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )

        with pytest.raises(Exception) as ex:
            identity_client.create_user_and_token(scopes=None)

        assert ex is not None

    @CommunicationPreparer()
    @recorded_by_proxy
    def test_delete_user_with_no_user(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )

        with pytest.raises(Exception) as ex:
            identity_client.delete_user(user=None)

        assert ex is not None

    @CommunicationPreparer()
    @recorded_by_proxy
    def test_revoke_tokens_with_no_user(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )

        with pytest.raises(Exception) as ex:
            identity_client.revoke_tokens(user=None)

        assert ex is not None

    @CommunicationPreparer()
    @recorded_by_proxy
    def test_get_token_with_no_user(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )

        with pytest.raises(Exception) as ex:
            identity_client.get_token(user=None, scopes=[CommunicationTokenScope.CHAT])

        assert ex is not None

    @CommunicationPreparer()
    @recorded_by_proxy
    def test_get_token_with_no_scopes(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        user = identity_client.create_user()

        with pytest.raises(Exception) as ex:
            identity_client.get_token(user, scopes=None)

        assert ex is not None

    @CommunicationPreparer()
    @acs_identity_decorator
    @recorded_by_proxy
    def test_get_token_for_teams_user_from_managed_identity(self, communication_livetest_dynamic_connection_string):
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
        aad_token, user_object_id = self.generate_teams_user_aad_token()
        token_response = identity_client.get_token_for_teams_user(aad_token, self.m365_client_id, user_object_id)
        assert token_response.token is not None

    @CommunicationPreparer()
    @acs_identity_decorator
    @recorded_by_proxy
    def test_get_token_for_teams_user_with_valid_params(self, communication_livetest_dynamic_connection_string):
        if self.skip_get_token_for_teams_user_test():
            return
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        aad_token, user_object_id = self.generate_teams_user_aad_token()
        token_response = identity_client.get_token_for_teams_user(aad_token, self.m365_client_id, user_object_id)
        assert token_response.token is not None

    @CommunicationPreparer()
    @pytest.mark.parametrize("_, value", [("empty_token", ""), ("invalid_token", "invalid")])
    @ArgumentPasser()
    @acs_identity_decorator
    @recorded_by_proxy
    def test_get_token_for_teams_user_with_invalid_token(self, _, value):
        if self.skip_get_token_for_teams_user_test():
            return
        identity_client = CommunicationIdentityClient.from_connection_string(
            self.connection_str,
            http_logging_policy=get_http_logging_policy()
        )
        with pytest.raises(Exception) as ex:
            identity_client.get_token_for_teams_user(value, self.m365_client_id, "")
        assert str(ex.value.status_code) == "401"
        assert ex.value.message is not None

    @CommunicationPreparer()
    @acs_identity_decorator
    @recorded_by_proxy
    def test_get_token_for_teams_user_with_expired_token(self, communication_livetest_dynamic_connection_string):
        if self.skip_get_token_for_teams_user_test():
            return
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        _, user_object_id = self.generate_teams_user_aad_token()
        with pytest.raises(Exception) as ex:
            identity_client.get_token_for_teams_user(self.expired_teams_token, self.m365_client_id,
                                                                      user_object_id)
        assert str(ex.value.status_code) == "401"
        assert ex.value.message is not None

    @CommunicationPreparer()
    @pytest.mark.parametrize("_, value", [("empty_client_id", ""), ("invalid_client_id", "invalid")])
    @ArgumentPasser()
    @acs_identity_decorator
    @recorded_by_proxy
    def test_get_token_for_teams_user_with_invalid_client_id(self, _, value):
        if self.skip_get_token_for_teams_user_test():
            return
        identity_client = CommunicationIdentityClient.from_connection_string(
            self.connection_str,
            http_logging_policy=get_http_logging_policy()
        )
        aad_token, user_object_id = self.generate_teams_user_aad_token()
        with pytest.raises(Exception) as ex:
            identity_client.get_token_for_teams_user(aad_token, value, user_object_id)
        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    @CommunicationPreparer()
    @acs_identity_decorator
    @recorded_by_proxy
    def test_get_token_for_teams_user_with_wrong_client_id(self, communication_livetest_dynamic_connection_string):
        if self.skip_get_token_for_teams_user_test():
            return
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        aad_token, user_object_id = self.generate_teams_user_aad_token()
        with pytest.raises(Exception) as ex:
            identity_client.get_token_for_teams_user(aad_token, user_object_id, user_object_id)
        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    @CommunicationPreparer()
    @pytest.mark.parametrize("_, value", [("empty_user_object_id", ""), ("invalid_user_object_id", "invalid")])
    @ArgumentPasser()
    @acs_identity_decorator
    @recorded_by_proxy
    def test_get_token_for_teams_user_with_invalid_user_object_id(self, _, value):
        if self.skip_get_token_for_teams_user_test():
            return
        identity_client = CommunicationIdentityClient.from_connection_string(
            self.connection_str,
            http_logging_policy=get_http_logging_policy()
        )
        aad_token, _ = self.generate_teams_user_aad_token()
        with pytest.raises(Exception) as ex:
            identity_client.get_token_for_teams_user(aad_token, self.m365_client_id, value)
        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    @CommunicationPreparer()
    @acs_identity_decorator
    @recorded_by_proxy
    def test_get_token_for_teams_user_with_wrong_user_object_id(self):
        if self.skip_get_token_for_teams_user_test():
            return
        identity_client = CommunicationIdentityClient.from_connection_string(
            self.connection_str,
            http_logging_policy=get_http_logging_policy()
        )
        aad_token, _ = self.generate_teams_user_aad_token()
        with pytest.raises(Exception) as ex:
            identity_client.get_token_for_teams_user(aad_token, self.m365_client_id, self.m365_client_id)
        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

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

    def skip_get_token_for_teams_user_test(self):
        return str(self.skip_get_token_for_teams_user_tests).lower() == 'true'
