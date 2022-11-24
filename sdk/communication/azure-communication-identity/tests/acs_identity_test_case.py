# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
from devtools_testutils import AzureRecordedTestCase, is_live
from azure.communication.identity._shared.utils import parse_connection_str

class ACSIdentityTestCase(AzureRecordedTestCase):
    def setUp(self):
        if is_live():
            self.connection_str = os.getenv('COMMUNICATION_LIVETEST_DYNAMIC_CONNECTION_STRING')
            self.m365_client_id = os.getenv('COMMUNICATION_M365_APP_ID')
            self.m365_aad_authority = os.getenv('COMMUNICATION_M365_AAD_AUTHORITY')
            self.m365_aad_tenant = os.getenv('COMMUNICATION_M365_AAD_TENANT')
            self.msal_username = os.getenv('COMMUNICATION_MSAL_USERNAME')
            self.msal_password = os.getenv('COMMUNICATION_MSAL_PASSWORD')
            self.expired_teams_token = os.getenv('COMMUNICATION_EXPIRED_TEAMS_TOKEN')
            self.endpoint, _ = parse_connection_str(self.connection_str)
            self._resource_name = self.endpoint.split(".")[0]
            self.skip_get_token_for_teams_user_tests = os.getenv('SKIP_INT_IDENTITY_EXCHANGE_TOKEN_TEST')
        else:
            self.connection_str = "endpoint=https://sanitized.communication.azure.com/;accesskey=fake==="
            self.endpoint, _ = parse_connection_str(self.connection_str)
            self.m365_client_id = "sanitized"
            self.m365_aad_authority = "sanitized"
            self.m365_aad_tenant = "sanitized"
            self.msal_username = "sanitized"
            self.msal_password = "sanitized"
            self.expired_teams_token = "sanitized"
            self.skip_get_token_for_teams_user_tests = "true"
