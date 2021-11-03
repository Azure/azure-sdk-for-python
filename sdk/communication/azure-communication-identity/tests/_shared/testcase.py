
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import re
import os
from devtools_testutils import AzureTestCase
from azure_devtools.scenario_tests import RecordingProcessor, ReplayableTest
from azure_devtools.scenario_tests.utilities import is_text_payload
from azure.communication.identity._shared.utils import parse_connection_str
from _shared.utils import generate_teams_user_aad_token
class ResponseReplacerProcessor(RecordingProcessor):
    def __init__(self, keys=None, replacement="sanitized"):
        self._keys = keys if keys else []
        self._replacement = replacement

    def process_response(self, response):
        def sanitize_dict(dictionary):
            for key in dictionary:
                value = dictionary[key]
                if isinstance(value, str):
                    dictionary[key] = re.sub(
                        r"("+'|'.join(self._keys)+r")",
                        self._replacement,
                        dictionary[key])
                elif isinstance(value, dict):
                    sanitize_dict(value)

        sanitize_dict(response)

        return response

class BodyReplacerProcessor(RecordingProcessor):
    """Sanitize the sensitive info inside request or response bodies"""

    def __init__(self, keys=None, replacement="sanitized"):
        self._replacement = replacement
        self._keys = keys if keys else []

    def process_request(self, request):
        if is_text_payload(request) and request.body:
            request.body = self._replace_keys(request.body.decode()).encode()

        return request

    def process_response(self, response):
        if is_text_payload(response) and response['body']['string']:
            response['body']['string'] = self._replace_keys(response['body']['string'])

        return response
    
    def _replace_keys(self, body):
        def _replace_recursively(dictionary):
            for key in dictionary:
                value = dictionary[key]
                if key in self._keys:
                    dictionary[key] = self._replacement
                elif isinstance(value, dict):
                    _replace_recursively(value)

        import json
        try:
            body = json.loads(body)
            _replace_recursively(body)

        except (KeyError, ValueError):
            return body

        return json.dumps(body)

class CommunicationTestCase(AzureTestCase):
    FILTER_HEADERS = ReplayableTest.FILTER_HEADERS + ['x-azure-ref', 'x-ms-content-sha256', 'location']

    def __init__(self, method_name, *args, **kwargs):
        super(CommunicationTestCase, self).__init__(method_name, *args, **kwargs)

    def setUp(self):
        super(CommunicationTestCase, self).setUp()
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
            teams_user_aad_token = generate_teams_user_aad_token(m365_app_id=self.m365_app_id, m365_aad_authority=self.m365_aad_authority, m365_aad_tenant=self.m365_aad_tenant, msal_username=self.msal_username, msal_password=self.msal_password, m365_scope=self.m365_scope)
        return teams_user_aad_token

    def skip_get_token_for_teams_user_test(self):
        return str(self.skip_get_token_for_teams_user_tests).lower() == 'true'