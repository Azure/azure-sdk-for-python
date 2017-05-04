#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import json
import os.path
import re
import time

import azure.mgmt.resource
from azure.mgmt.keyvault import KeyVaultManagementClient
from azure.mgmt.keyvault.models import \
    (VaultCreateOrUpdateParameters, VaultProperties, Sku, AccessPolicyEntry, Permissions)
from azure.keyvault import KeyVaultClient, KeyVaultAuthentication, KeyVaultAuthBase, HttpBearerChallenge

from azure.common.exceptions import (
    CloudError
)
from testutils.common_recordingtestcase import (
    RecordingTestCase,
    TestMode,
)
import tests.mgmt_settings_fake as fake_settings

should_log = os.getenv('SDK_TESTS_LOG', '0')
if should_log.lower() == 'true' or should_log == '1':
    import logging
    logger = logging.getLogger('msrest')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())

class HttpStatusCode(object):
    OK = 200
    Created = 201
    Accepted = 202
    NoContent = 204
    NotFound = 404
    Unauthorized = 401

class AzureKeyVaultTestCase(RecordingTestCase):

    def setUp(self):
        self.working_folder = os.path.dirname(__file__)

        super(AzureKeyVaultTestCase, self).setUp()

        def mock_key_vault_auth_base(self, request):
            challenge = HttpBearerChallenge(request.url, 'Bearer authorization=fake-url,resource=https://vault.azure.net')
            self.set_authorization_header(request, challenge)
            return request

        self.fake_settings = fake_settings
        if TestMode.is_playback(self.test_mode):
            self.settings = self.fake_settings
            KeyVaultAuthBase.__call__ = mock_key_vault_auth_base
        else:
            import tests.mgmt_settings_real as real_settings
            self.settings = real_settings

        self.client = self.create_keyvault_client()

    def tearDown(self):
        return super(AzureKeyVaultTestCase, self).tearDown()

    def create_keyvault_client(self):

        def _auth_callback(server, resource, scope):
            if TestMode.is_playback(self.test_mode):
                return ('Bearer', 'fake-token')
            credentials = self.settings.get_credentials()
            credentials.resource = resource
            credentials.set_token()
            return credentials.scheme, credentials.__dict__['token']['access_token']
        return KeyVaultClient(KeyVaultAuthentication(_auth_callback))

    def _scrub_sensitive_request_info(self, request):
        request = super(AzureKeyVaultTestCase, self)._scrub_sensitive_request_info(request)
        # prevents URI mismatch between Python 2 and 3 if request URI has extra / chars
        request.uri = re.sub('//', '/', request.uri)
        request.uri = re.sub('/', '//', request.uri, count=1)
        # do not record token requests
        if '/oauth2/token' in request.uri:
            request = None
        return request

    def _scrub_sensitive_response_info(self, response):
        from pprint import pprint
        response = super(AzureKeyVaultTestCase, self)._scrub_sensitive_response_info(response)
        # ignore any 401 responses during playback
        if response['status']['code'] == 401:
            response = None
        return response

    def _scrub(self, val):
        val = super(AzureKeyVaultTestCase, self)._scrub(val)
        real_to_fake_dict = {
            self.settings.SUBSCRIPTION_ID: self.fake_settings.SUBSCRIPTION_ID,
            self.settings.AD_DOMAIN:  self.fake_settings.AD_DOMAIN
        }
        val = self._scrub_using_dict(val, real_to_fake_dict)
        return val
