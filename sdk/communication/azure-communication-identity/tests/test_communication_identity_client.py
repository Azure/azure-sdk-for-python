# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from datetime import timedelta
from azure.communication.identity import CommunicationTokenScope
from devtools_testutils import is_live, recorded_by_proxy, get_credential
from utils import is_token_expiration_within_allowed_deviation, token_scope_scenarios
from acs_identity_test_case import ACSIdentityTestCase
from azure.communication.identity import CommunicationIdentityClient
from devtools_testutils.fake_credentials import FakeTokenCredential
from _shared.utils import get_http_logging_policy


class ArgumentPasser:
    def __call__(self, fn):
        def _wrapper(test_class, _, value, **kwargs):
            fn(test_class, _, value, **kwargs)

        return _wrapper


class TestClient(ACSIdentityTestCase):
    def setup_method(self):
        super().setUp()

    def create_client_from_connection_string(self):
        return CommunicationIdentityClient.from_connection_string(
            self.connection_str, http_logging_policy=get_http_logging_policy()
        )

    def create_client_from_token_credential(self):
        if not is_live():
            credential = FakeTokenCredential()
        else:
            credential = get_credential()
        return CommunicationIdentityClient(self.endpoint, credential, http_logging_policy=get_http_logging_policy())

    @recorded_by_proxy
    def test_create_user_from_token_credential(self):
        identity_client = self.create_client_from_token_credential()
        user = identity_client.create_user()

        assert user.properties.get("id") is not None

    @recorded_by_proxy
    def test_create_user(self):
        identity_client = self.create_client_from_connection_string()
        user = identity_client.create_user()
        assert user.properties.get("id") is not None

    @pytest.mark.parametrize(
        "_, value",
        token_scope_scenarios,
    )
    @ArgumentPasser()
    @recorded_by_proxy
    def test_create_user_and_token(self, _, scopes):
        identity_client = self.create_client_from_connection_string()
        user, token_response = identity_client.create_user_and_token(scopes=scopes)

        assert user.properties.get("id") is not None
        assert token_response.token is not None

    @pytest.mark.parametrize("_, value", [("min_valid_hours", 1), ("max_valid_hours", 24)])
    @ArgumentPasser()
    @recorded_by_proxy
    def test_create_user_and_token_with_valid_custom_expirations_new(self, _, valid_hours):
        identity_client = self.create_client_from_connection_string()
        token_expires_in = timedelta(hours=valid_hours)
        user, token_response = identity_client.create_user_and_token(
            scopes=[CommunicationTokenScope.CHAT], token_expires_in=token_expires_in
        )
        assert user.properties.get("id") is not None
        assert token_response.token is not None

        if is_live():
            assert is_token_expiration_within_allowed_deviation(token_expires_in, token_response.expires_on)

    @pytest.mark.parametrize("_, value", [("min_invalid_mins", 59), ("max_invalid_mins", 1441)])
    @ArgumentPasser()
    @recorded_by_proxy
    def test_create_user_and_token_with_invalid_custom_expirations(self, _, invalid_mins):
        identity_client = self.create_client_from_connection_string()
        token_expires_in = timedelta(minutes=invalid_mins)

        with pytest.raises(Exception) as ex:
            identity_client.create_user_and_token(
                scopes=[CommunicationTokenScope.CHAT], token_expires_in=token_expires_in
            )

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    @pytest.mark.parametrize(
        "_, value",
        token_scope_scenarios,
    )
    @ArgumentPasser()
    @recorded_by_proxy
    def test_get_token_from_token_credential(self, _, scopes):
        identity_client = self.create_client_from_token_credential()
        user = identity_client.create_user()

        token_response = identity_client.get_token(user, scopes=scopes)

        assert user.properties.get("id") is not None
        assert token_response.token is not None

    @recorded_by_proxy
    def test_get_token(self):
        identity_client = self.create_client_from_connection_string()
        user = identity_client.create_user()

        token_response = identity_client.get_token(user, scopes=[CommunicationTokenScope.CHAT])

        assert user.properties.get("id") is not None
        assert token_response.token is not None

    @pytest.mark.parametrize("_, value", [("min_valid_hours", 1), ("max_valid_hours", 24)])
    @ArgumentPasser()
    @recorded_by_proxy
    def test_get_token_with_valid_custom_expirations(self, _, valid_hours):
        identity_client = self.create_client_from_connection_string()
        user = identity_client.create_user()

        token_expires_in = timedelta(hours=valid_hours)
        token_response = identity_client.get_token(
            user,
            scopes=[CommunicationTokenScope.CHAT],
            token_expires_in=token_expires_in,
        )

        assert user.properties.get("id") is not None
        assert token_response.token is not None
        if is_live():
            assert is_token_expiration_within_allowed_deviation(token_expires_in, token_response.expires_on)

    @pytest.mark.parametrize("_, value", [("min_invalid_mins", 59), ("max_invalid_mins", 1441)])
    @ArgumentPasser()
    @recorded_by_proxy
    def test_get_token_with_invalid_custom_expirations(self, _, invalid_mins):
        identity_client = self.create_client_from_connection_string()
        user = identity_client.create_user()

        token_expires_in = timedelta(minutes=invalid_mins)

        with pytest.raises(Exception) as ex:
            identity_client.get_token(
                user,
                scopes=[CommunicationTokenScope.CHAT],
                token_expires_in=token_expires_in,
            )

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    @recorded_by_proxy
    def test_revoke_tokens_from_token_credential(self):
        identity_client = self.create_client_from_token_credential()
        user = identity_client.create_user()

        token_response = identity_client.get_token(user, scopes=[CommunicationTokenScope.CHAT])
        identity_client.revoke_tokens(user)

        assert user.properties.get("id") is not None
        assert token_response.token is not None

    @recorded_by_proxy
    def test_revoke_tokens(self):
        identity_client = self.create_client_from_connection_string()
        user = identity_client.create_user()

        token_response = identity_client.get_token(user, scopes=[CommunicationTokenScope.CHAT])
        identity_client.revoke_tokens(user)

        assert user.properties.get("id") is not None
        assert token_response.token is not None

    @recorded_by_proxy
    def test_delete_user_from_token_credential(self):
        identity_client = self.create_client_from_token_credential()
        user = identity_client.create_user()

        identity_client.delete_user(user)

        assert user.properties.get("id") is not None

    @recorded_by_proxy
    def test_delete_user(self):
        identity_client = self.create_client_from_connection_string()
        user = identity_client.create_user()

        identity_client.delete_user(user)

        assert user.properties.get("id") is not None

    @recorded_by_proxy
    def test_create_user_and_token_with_no_scopes(self):
        identity_client = self.create_client_from_connection_string()
        with pytest.raises(Exception) as ex:
            identity_client.create_user_and_token(scopes=None)

        assert ex is not None and ex.value is not None

    @recorded_by_proxy
    def test_delete_user_with_no_user(self):
        identity_client = self.create_client_from_connection_string()
        with pytest.raises(Exception) as ex:
            identity_client.delete_user(user=None)

        assert ex is not None and ex.value is not None

    @recorded_by_proxy
    def test_revoke_tokens_with_no_user(self):
        identity_client = self.create_client_from_connection_string()
        with pytest.raises(Exception) as ex:
            identity_client.revoke_tokens(user=None)

        assert ex is not None and ex.value is not None

    @recorded_by_proxy
    def test_get_token_with_no_user(self):
        identity_client = self.create_client_from_connection_string()
        with pytest.raises(Exception) as ex:
            identity_client.get_token(user=None, scopes=[CommunicationTokenScope.CHAT])

        assert ex is not None and ex.value is not None

    @recorded_by_proxy
    def test_get_token_with_no_scopes(self):
        identity_client = self.create_client_from_connection_string()
        user = identity_client.create_user()

        with pytest.raises(Exception) as ex:
            identity_client.get_token(user, scopes=None)

        assert ex is not None and ex.value is not None

    @recorded_by_proxy
    def test_get_token_for_teams_user_from_token_credential(self):
        if self.skip_get_token_for_teams_user_test():
            return
        identity_client = self.create_client_from_token_credential()
        aad_token, user_object_id = self.generate_teams_user_aad_token()
        token_response = identity_client.get_token_for_teams_user(aad_token, self.m365_client_id, user_object_id)
        assert token_response.token is not None

    @recorded_by_proxy
    def test_get_token_for_teams_user_with_valid_params(self):
        if self.skip_get_token_for_teams_user_test():
            return
        identity_client = self.create_client_from_connection_string()
        aad_token, user_object_id = self.generate_teams_user_aad_token()
        token_response = identity_client.get_token_for_teams_user(aad_token, self.m365_client_id, user_object_id)
        assert token_response.token is not None

    @pytest.mark.parametrize("_, value", [("empty_token", ""), ("invalid_token", "invalid")])
    @ArgumentPasser()
    @recorded_by_proxy
    def test_get_token_for_teams_user_with_invalid_token(self, _, invalid_token):
        if self.skip_get_token_for_teams_user_test():
            return
        identity_client = self.create_client_from_connection_string()
        with pytest.raises(Exception) as ex:
            identity_client.get_token_for_teams_user(invalid_token, self.m365_client_id, "")
        assert str(ex.value.status_code) == "401"
        assert ex.value.message is not None

    @recorded_by_proxy
    def test_get_token_for_teams_user_with_expired_token(self):
        if self.skip_get_token_for_teams_user_test():
            return
        identity_client = self.create_client_from_connection_string()
        _, user_object_id = self.generate_teams_user_aad_token()
        with pytest.raises(Exception) as ex:
            identity_client.get_token_for_teams_user(self.expired_teams_token, self.m365_client_id, user_object_id)
        assert str(ex.value.status_code) == "401"
        assert ex.value.message is not None

    @pytest.mark.parametrize("_, value", [("empty_client_id", ""), ("invalid_client_id", "invalid")])
    @ArgumentPasser()
    @recorded_by_proxy
    def test_get_token_for_teams_user_with_invalid_client_id(self, _, invalid_client):
        if self.skip_get_token_for_teams_user_test():
            return
        identity_client = self.create_client_from_connection_string()
        aad_token, user_object_id = self.generate_teams_user_aad_token()
        with pytest.raises(Exception) as ex:
            identity_client.get_token_for_teams_user(aad_token, invalid_client, user_object_id)
        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    @recorded_by_proxy
    def test_get_token_for_teams_user_with_wrong_client_id(self):
        if self.skip_get_token_for_teams_user_test():
            return
        identity_client = self.create_client_from_connection_string()
        aad_token, user_object_id = self.generate_teams_user_aad_token()
        with pytest.raises(Exception) as ex:
            identity_client.get_token_for_teams_user(aad_token, user_object_id, user_object_id)
        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    @pytest.mark.parametrize(
        "_, value",
        [("empty_user_object_id", ""), ("invalid_user_object_id", "invalid")],
    )
    @ArgumentPasser()
    @recorded_by_proxy
    def test_get_token_for_teams_user_with_invalid_user_object_id(self, _, invalid_user_object):
        if self.skip_get_token_for_teams_user_test():
            return
        identity_client = self.create_client_from_connection_string()
        aad_token, _ = self.generate_teams_user_aad_token()
        with pytest.raises(Exception) as ex:
            identity_client.get_token_for_teams_user(aad_token, self.m365_client_id, invalid_user_object)
        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    @recorded_by_proxy
    def test_get_token_for_teams_user_with_wrong_user_object_id(self):
        if self.skip_get_token_for_teams_user_test():
            return
        identity_client = self.create_client_from_connection_string()
        aad_token, _ = self.generate_teams_user_aad_token()
        with pytest.raises(Exception) as ex:
            identity_client.get_token_for_teams_user(aad_token, self.m365_client_id, self.m365_client_id)
        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None
