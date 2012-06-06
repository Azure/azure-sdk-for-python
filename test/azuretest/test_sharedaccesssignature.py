#-------------------------------------------------------------------------
# Copyright 2011 Microsoft Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#--------------------------------------------------------------------------

from azure import WindowsAzureError, DEV_ACCOUNT_NAME, DEV_ACCOUNT_KEY
from azure.storage.sharedaccesssignature import (SharedAccessSignature, 
                                                 SharedAccessPolicy, 
                                                 Permission, 
                                                 WebResource)
from azure.storage import AccessPolicy

from azuretest.util import (credentials, 
                            getUniqueTestRunID,
                            STATUS_OK,
                            STATUS_CREATED,
                            STATUS_ACCEPTED,
                            DEFAULT_SLEEP_TIME,
                            DEFAULT_LEASE_TIME)

import unittest
import time

#------------------------------------------------------------------------------
SIGNED_START = 'st'
SIGNED_EXPIRY = 'se'
SIGNED_RESOURCE = 'sr'
SIGNED_PERMISSION = 'sp'
SIGNED_IDENTIFIER = 'si'
SIGNED_SIGNATURE = 'sig'
RESOURCE_BLOB = 'blob'
RESOURCE_CONTAINER = 'container'
SIGNED_RESOURCE_TYPE = 'resource'
SHARED_ACCESS_PERMISSION = 'permission'

#------------------------------------------------------------------------------
class SharedAccessSignatureTest(unittest.TestCase):

    def setUp(self):
        self.sas = SharedAccessSignature(account_name=DEV_ACCOUNT_NAME, 
                                         account_key=DEV_ACCOUNT_KEY)
    def tearDown(self):
        self.cleanup()
        return super(SharedAccessSignatureTest, self).tearDown()

    def cleanup(self):
        pass
        
    def test_generate_signature_container(self):
        access_policy = AccessPolicy()
        access_policy.start = '2011-10-11'
        access_policy.expiry = '2011-10-12'
        access_policy.permission = 'r'
        signed_identifier = 'YWJjZGVmZw=='
        shared_access_policy = SharedAccessPolicy(access_policy, 
                                                  signed_identifier)
        signature = self.sas._generate_signature('images', 
                                                 RESOURCE_CONTAINER, 
                                                 shared_access_policy)
        self.assertEqual(signature, 
                         'VdlALM4TYEYYNf94Bvt3dn48TsA01wk45ltwP3zeKp4=')

    def test_generate_signature_blob(self):
        access_policy = AccessPolicy()
        access_policy.start = '2011-10-11T11:03:40Z'
        access_policy.expiry = '2011-10-12T11:53:40Z'
        access_policy.permission = 'r'
        shared_access_policy = SharedAccessPolicy(access_policy)

        signature = self.sas._generate_signature('images/pic1.png', 
                                                 RESOURCE_BLOB, 
                                                 shared_access_policy)
        self.assertEqual(signature, 
                         '7NIEip+VOrQ5ZV80pORPK1MOsJc62wwCNcbMvE+lQ0s=')

    def test_blob_signed_query_string(self):
        access_policy = AccessPolicy()
        access_policy.start = '2011-10-11'
        access_policy.expiry = '2011-10-12'
        access_policy.permission = 'w'
        shared_access_policy = SharedAccessPolicy(access_policy)
        query_string = self.sas.generate_signed_query_string('images/pic1.png', 
                                                             RESOURCE_BLOB, 
                                                             shared_access_policy)
        self.assertEqual(query_string[SIGNED_START], '2011-10-11')
        self.assertEqual(query_string[SIGNED_EXPIRY], '2011-10-12')
        self.assertEqual(query_string[SIGNED_RESOURCE], RESOURCE_BLOB)
        self.assertEqual(query_string[SIGNED_PERMISSION], 'w')
        self.assertEqual(query_string[SIGNED_SIGNATURE], 
                         'k8uyTrn3pgLXuhwgZhxeAH6mZ/es9k2vqHPJEuIH4CE=')

    def test_container_signed_query_string(self):
        access_policy = AccessPolicy()
        access_policy.start = '2011-10-11'
        access_policy.expiry = '2011-10-12'
        access_policy.permission = 'r'
        signed_identifier = 'YWJjZGVmZw=='
        shared_access_policy = SharedAccessPolicy(access_policy, 
                                                  signed_identifier)
        query_string = self.sas.generate_signed_query_string('images', 
                                                             RESOURCE_CONTAINER, 
                                                             shared_access_policy)
        self.assertEqual(query_string[SIGNED_START], '2011-10-11')
        self.assertEqual(query_string[SIGNED_EXPIRY], '2011-10-12')
        self.assertEqual(query_string[SIGNED_RESOURCE], RESOURCE_CONTAINER)
        self.assertEqual(query_string[SIGNED_PERMISSION], 'r')
        self.assertEqual(query_string[SIGNED_IDENTIFIER], 'YWJjZGVmZw==')
        self.assertEqual(query_string[SIGNED_SIGNATURE], 
                         'VdlALM4TYEYYNf94Bvt3dn48TsA01wk45ltwP3zeKp4=')

    def test_sign_request(self):
        access_policy = AccessPolicy()
        access_policy.start = '2011-10-11'
        access_policy.expiry = '2011-10-12'
        access_policy.permission = 'r'
        shared_access_policy = SharedAccessPolicy(access_policy)
        query_string = self.sas.generate_signed_query_string('images/pic1.png', 
                                                             RESOURCE_BLOB, 
                                                             shared_access_policy)
        permission_set = []
        permission = Permission()
        permission.path = '/images/pic1.png'
        permission.query_string = query_string
        permission_set.append(permission)
        self.sas.permission_set = permission_set

        web_resource = WebResource()
        web_resource.properties[SIGNED_RESOURCE_TYPE] = RESOURCE_BLOB
        web_resource.properties[SHARED_ACCESS_PERMISSION] = 'r'
        web_resource.path = '/images/pic1.png?comp=metadata'
        web_resource.request_url = '/images/pic1.png?comp=metadata'

        web_resource = self.sas.sign_request(web_resource)

        self.assertEqual(web_resource.request_url, 
                         '/images/pic1.png?comp=metadata&' + 
                         self.sas._convert_query_string(query_string))

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
    