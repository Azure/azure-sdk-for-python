# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import json
import tempfile
import unittest
from io import open

from azure.common.client_factory import *

class TestCommon(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_client_from_auth_file(self):

        configuration = {
            "clientId": "a2ab11af-01aa-4759-8345-7803287dbd39",
            "clientSecret": "password",
            "subscriptionId": "15dbcfa8-4b93-4c9a-881c-6189d39f04d4",
            "tenantId": "c81da1d8-65ca-11e7-b1d1-ecb1d756380e",
            "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
            "resourceManagerEndpointUrl": "https://management.azure.com/",
            "activeDirectoryGraphResourceId": "https://graph.windows.net/",
            "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
            "galleryEndpointUrl": "https://gallery.azure.com/",
            "managementEndpointUrl": "https://management.core.windows.net/"
        }

        class FakeClient(object):
            def __init__(self, credentials, subscription_id, base_url):
                if credentials is None:
                    raise ValueError("Parameter 'credentials' must not be None.")
                if subscription_id is None:
                    raise ValueError("Parameter 'subscription_id' must not be None.")
                if not isinstance(subscription_id, str):
                    raise TypeError("Parameter 'subscription_id' must be str.")
                if not base_url:
                    base_url = 'https://management.azure.com'

                self.credentials = credentials
                self.subscription_id = subscription_id
                self.base_url = base_url

        class FakeSubscriptionClient(object):
            def __init__(self, credentials, base_url):
                if credentials is None:
                    raise ValueError("Parameter 'credentials' must not be None.")
                if not base_url:
                    base_url = 'https://management.azure.com'

                self.credentials = credentials
                self.base_url = base_url

        for encoding in ['utf-8', 'utf-8-sig', 'ascii']:

            temp_auth_file = tempfile.NamedTemporaryFile(delete=False)
            temp_auth_file.write(json.dumps(configuration).encode(encoding))
            temp_auth_file.close()

            client = get_client_from_auth_file(FakeClient, temp_auth_file.name)
            self.assertEqual('15dbcfa8-4b93-4c9a-881c-6189d39f04d4', client.subscription_id)
            self.assertEqual('https://management.azure.com/', client.base_url)
            self.assertTupleEqual(client.credentials._args, (
                'https://management.azure.com/', 
                'a2ab11af-01aa-4759-8345-7803287dbd39',
                'password'
            ))

            client = get_client_from_auth_file(FakeClient, temp_auth_file.name, subscription_id='fakesubid')
            self.assertEqual('fakesubid', client.subscription_id)
            self.assertEqual('https://management.azure.com/', client.base_url)
            self.assertTupleEqual(client.credentials._args, (
                'https://management.azure.com/',
                'a2ab11af-01aa-4759-8345-7803287dbd39',
                'password'
            ))

            credentials_instance = "Fake credentials class as a string"
            client = get_client_from_auth_file(FakeClient, temp_auth_file.name, credentials=credentials_instance)
            self.assertEqual('15dbcfa8-4b93-4c9a-881c-6189d39f04d4', client.subscription_id)
            self.assertEqual('https://management.azure.com/', client.base_url)
            self.assertEqual(credentials_instance, client.credentials)

            client = get_client_from_auth_file(FakeSubscriptionClient, temp_auth_file.name)
            self.assertEqual('https://management.azure.com/', client.base_url)
            self.assertTupleEqual(client.credentials._args, (
                'https://management.azure.com/',
                'a2ab11af-01aa-4759-8345-7803287dbd39',
                'password'
            ))

            os.unlink(temp_auth_file.name)
        

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
