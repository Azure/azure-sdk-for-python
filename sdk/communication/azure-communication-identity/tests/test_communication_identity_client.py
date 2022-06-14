# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import datetime
from azure.communication.identity import CommunicationIdentityClient
from azure.communication.identity import CommunicationTokenScope
from azure.core.credentials import AccessToken
from _shared.helper import URIIdentityReplacer, URIMsalUsernameReplacer
from _shared.testcase import BodyReplacerProcessor
from testcase import CommunicationIdentityTestCase
from _shared.communication_service_preparer import CommunicationPreparer
from _shared.utils import get_http_logging_policy
from azure.identity import DefaultAzureCredential
from azure.communication.identity._shared.utils import parse_connection_str
from parameterized import parameterized
class FakeTokenCredential(object):
    def __init__(self):
        self.token = AccessToken("Fake Token", 0)

    def get_token(self, *args):
        return self.token

class CommunicationIdentityClientTest(CommunicationIdentityTestCase):
    def setUp(self):
        super(CommunicationIdentityClientTest, self).setUp()
        self.recording_processors.extend([
            BodyReplacerProcessor(keys=["id", "token", "appId", "userId", "domain_name"]),
            URIIdentityReplacer(),
            URIMsalUsernameReplacer()])
    
    @CommunicationPreparer()
    def test_create_user_from_managed_identity(self, communication_livetest_dynamic_connection_string):
        endpoint, access_key = parse_connection_str(communication_livetest_dynamic_connection_string)
        from devtools_testutils import is_live
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
    def test_create_user(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        user = identity_client.create_user()

    @CommunicationPreparer()
    def test_create_user_and_token(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        user, token_response = identity_client.create_user_and_token(scopes=[CommunicationTokenScope.CHAT])

        assert user.properties.get('id') is not None
        assert token_response.token is not None

    @CommunicationPreparer()
    def test_get_token_from_managed_identity(self, communication_livetest_dynamic_connection_string):
        endpoint, access_key = parse_connection_str(communication_livetest_dynamic_connection_string)
        from devtools_testutils import is_live
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
    def test_revoke_tokens_from_managed_identity(self, communication_livetest_dynamic_connection_string):
        endpoint, access_key = parse_connection_str(communication_livetest_dynamic_connection_string)
        from devtools_testutils import is_live
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
    def test_delete_user_from_managed_identity(self, communication_livetest_dynamic_connection_string):
        endpoint, access_key = parse_connection_str(communication_livetest_dynamic_connection_string)
        from devtools_testutils import is_live
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
    def test_delete_user(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        user = identity_client.create_user()

        identity_client.delete_user(user)

        assert user.properties.get('id') is not None

    @CommunicationPreparer()
    def test_create_user_and_token_with_no_scopes(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )

        with pytest.raises(Exception) as ex:
            user, token_response = identity_client.create_user_and_token(scopes=None)

    @CommunicationPreparer()
    def test_delete_user_with_no_user(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )

        with pytest.raises(Exception) as ex:
            identity_client.delete_user(user=None)

    @CommunicationPreparer()
    def test_revoke_tokens_with_no_user(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        
        with pytest.raises(Exception) as ex:
            identity_client.revoke_tokens(user=None)
    
    @CommunicationPreparer()
    def test_get_token_with_no_user(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )

        with pytest.raises(Exception) as ex:
            token_response = identity_client.get_token(user=None, scopes=[CommunicationTokenScope.CHAT])
    
    @CommunicationPreparer()
    def test_get_token_with_no_scopes(self, communication_livetest_dynamic_connection_string):
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        user = identity_client.create_user()

        with pytest.raises(Exception) as ex:
            token_response = identity_client.get_token(user, scopes=None)

    
    @CommunicationPreparer()
    def test_get_token_for_teams_user_from_managed_identity(self, communication_livetest_dynamic_connection_string):
        if(self.skip_get_token_for_teams_user_test()):
            return
        endpoint, access_key = parse_connection_str(communication_livetest_dynamic_connection_string)
        from devtools_testutils import is_live
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
    def test_get_token_for_teams_user_with_valid_params(self, communication_livetest_dynamic_connection_string):
        if(self.skip_get_token_for_teams_user_test()):
            return
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        aad_token, user_object_id = self.generate_teams_user_aad_token() 
        token_response = identity_client.get_token_for_teams_user(aad_token, self.m365_client_id, user_object_id)
        assert token_response.token is not None

    @parameterized.expand(
        [
            ("empty_token", ""),
            ("invalid_token", "invalid")
        ]
    )
    def test_get_token_for_teams_user_with_invalid_token(self, _, invalid_token):
        if(self.skip_get_token_for_teams_user_test()):
            return
        identity_client = CommunicationIdentityClient.from_connection_string(
            self.connection_str,
            http_logging_policy=get_http_logging_policy()
        )
        with pytest.raises(Exception) as ex:
            token_response = identity_client.get_token_for_teams_user(invalid_token, self.m365_client_id, "")
        assert str(ex.value.status_code) == "401"
        assert ex.value.message is not None

    @CommunicationPreparer()
    def test_get_token_for_teams_user_with_expired_token(self, communication_livetest_dynamic_connection_string):
        if(self.skip_get_token_for_teams_user_test()):
            return
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        _, user_object_id = self.generate_teams_user_aad_token()
        with pytest.raises(Exception) as ex:
            token_response = identity_client.get_token_for_teams_user(self.expired_teams_token, self.m365_client_id, user_object_id)
        assert str(ex.value.status_code) == "401"
        assert ex.value.message is not None
    
    @parameterized.expand(
        [
            ("empty_client_id", ""),
            ("invalid_client_id", "invalid")
        ]
    )    
    def test_get_token_for_teams_user_with_invalid_client_id(self, _, invalid_client_id):
        if(self.skip_get_token_for_teams_user_test()):
            return
        identity_client = CommunicationIdentityClient.from_connection_string(
            self.connection_str,
            http_logging_policy=get_http_logging_policy()
        )
        aad_token, user_object_id = self.generate_teams_user_aad_token()
        with pytest.raises(Exception) as ex:
            token_response = identity_client.get_token_for_teams_user(aad_token, invalid_client_id, user_object_id)
        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None
    
    @CommunicationPreparer()
    def test_get_token_for_teams_user_with_wrong_client_id(self, communication_livetest_dynamic_connection_string):
        if(self.skip_get_token_for_teams_user_test()):
            return
        identity_client = CommunicationIdentityClient.from_connection_string(
            communication_livetest_dynamic_connection_string,
            http_logging_policy=get_http_logging_policy()
        )
        aad_token, user_object_id = self.generate_teams_user_aad_token()
        with pytest.raises(Exception) as ex:
            token_response = identity_client.get_token_for_teams_user(aad_token, user_object_id, user_object_id)
        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None
        
    @parameterized.expand(
        [
            ("empty_user_object_id", ""),
            ("invalid_user_object_id", "invalid"),
        ]
    )    
    def test_get_token_for_teams_user_with_invalid_user_object_id(self, _, invalid_user_object_id):
        if(self.skip_get_token_for_teams_user_test()):
            return
        identity_client = CommunicationIdentityClient.from_connection_string(
            self.connection_str,
            http_logging_policy=get_http_logging_policy()
        )
        aad_token, _ = self.generate_teams_user_aad_token()
        with pytest.raises(Exception) as ex:
            token_response = identity_client.get_token_for_teams_user(aad_token, self.m365_client_id, invalid_user_object_id)
        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None
           
    def test_get_token_for_teams_user_with_wrong_user_object_id(self):
        if(self.skip_get_token_for_teams_user_test()):
            return
        identity_client = CommunicationIdentityClient.from_connection_string(
            self.connection_str,
            http_logging_policy=get_http_logging_policy()
        )
        aad_token, _ = self.generate_teams_user_aad_token()
        with pytest.raises(Exception) as ex:
            token_response = identity_client.get_token_for_teams_user(aad_token, self.m365_client_id, self.m365_client_id)
        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None