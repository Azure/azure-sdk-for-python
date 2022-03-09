
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os

from azure.communication.identity._shared.utils import parse_connection_str
from _shared.testcase import CommunicationTestCase
from msal import PublicClientApplication

class CommunicationIdentityTestCase(CommunicationTestCase):
    
    def __init__(self, method_name, *args, **kwargs):
        super(CommunicationIdentityTestCase, self).__init__(method_name, *args, **kwargs)

    def setUp(self):
        super(CommunicationIdentityTestCase, self).setUp()
        if self.is_playback():
            self.connection_str = "endpoint=https://sanitized/;accesskey=fake==="
            self.m365_app_id = "sanitized"
            self.m365_aad_authority = "sanitized"
            self.m365_aad_tenant = "sanitized"
            self.m365_scope = "sanitized" 
            self.msal_username = "sanitized" 
            self.msal_password = "sanitized"
            self.expired_teams_token = "sanitized"
            self.skip_get_token_for_teams_user_tests = "false"
        else:
            self.connection_str = os.getenv('COMMUNICATION_LIVETEST_DYNAMIC_CONNECTION_STRING')
            self.m365_app_id = os.getenv('COMMUNICATION_M365_APP_ID') 
            self.m365_aad_authority = os.getenv('COMMUNICATION_M365_AAD_AUTHORITY') 
            self.m365_aad_tenant = os.getenv('COMMUNICATION_M365_AAD_TENANT')
            self.m365_scope = os.getenv('COMMUNICATION_M365_SCOPE') 
            self.msal_username = os.getenv('COMMUNICATION_MSAL_USERNAME') 
            self.msal_password = os.getenv('COMMUNICATION_MSAL_PASSWORD')
            self.expired_teams_token = os.getenv('COMMUNICATION_EXPIRED_TEAMS_TOKEN')  
            endpoint, _ = parse_connection_str(self.connection_str)
            self._resource_name = endpoint.split(".")[0]
            self.scrubber.register_name_pair(self._resource_name, "sanitized")
            self.skip_get_token_for_teams_user_tests = os.getenv('SKIP_INT_IDENTITY_EXCHANGE_TOKEN_TEST') 

    def generate_teams_user_aad_token(self):
        if self.is_playback():
            teams_user_aad_token = "sanitized"
        else:
            msal_app = PublicClientApplication(
                client_id=self.m365_app_id,
                authority="{}/{}".format(self.m365_aad_authority, self.m365_aad_tenant))
            result = msal_app.acquire_token_by_username_password(username=self.msal_username, password=self.msal_password, scopes=[self.m365_scope])
            teams_user_aad_token = result["access_token"]
        return teams_user_aad_token 

    def skip_get_token_for_teams_user_test(self):
        return str(self.skip_get_token_for_teams_user_tests).lower() == 'true'