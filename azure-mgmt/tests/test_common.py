
# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import unittest
import tempfile
from io import open

from azure.common.client_factory import *

class TestCommon(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_client_from_auth_file(self):

        configuration=b"""
# sample management library properties file
subscription=15dbcfa8-4b93-4c9a-881c-6189d39f04d4
client=a2ab11af-01aa-4759-8345-7803287dbd39
key=password
tenant=43413cc1-5886-4711-9804-8cfea3d1c3ee
managementURI=https://management.core.windows.net/
baseURL=https://management.azure.com/
authURL=https://login.windows.net/
graphURL=https://graph.windows.net/
"""

        class FakeClient(object):
            def __init__(self, credentials, subscription_id, base_url):
                self.credentials = credentials
                self.subscription_id = subscription_id
                self.base_url = base_url

        temp_auth_file = tempfile.NamedTemporaryFile(delete=False)
        temp_auth_file.write(configuration)
        temp_auth_file.close()

        client = get_client_from_auth_file(FakeClient, temp_auth_file.name)
        self.assertEquals('15dbcfa8-4b93-4c9a-881c-6189d39f04d4', client.subscription_id)
        self.assertEquals('https://management.azure.com/', client.base_url)
        self.assertTupleEqual(client.credentials._args, (
            'https://management.core.windows.net/', 
            'a2ab11af-01aa-4759-8345-7803287dbd39',
            'password'
        ))

        client = get_client_from_auth_file(FakeClient, temp_auth_file.name, subscription_id='fakesubid')
        self.assertEquals('fakesubid', client.subscription_id)
        self.assertEquals('https://management.azure.com/', client.base_url)
        self.assertTupleEqual(client.credentials._args, (
            'https://management.core.windows.net/', 
            'a2ab11af-01aa-4759-8345-7803287dbd39',
            'password'
        ))

        credentials_instance = "Fake credentials class as a string"
        client = get_client_from_auth_file(FakeClient, temp_auth_file.name, credentials=credentials_instance)
        self.assertEquals('15dbcfa8-4b93-4c9a-881c-6189d39f04d4', client.subscription_id)
        self.assertEquals('https://management.azure.com/', client.base_url)
        self.assertEquals(credentials_instance, client.credentials)

        os.unlink(temp_auth_file.name)
        

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
