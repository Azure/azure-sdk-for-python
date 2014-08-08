#-------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
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
import unittest

from azure import (
    DEV_ACCOUNT_NAME,
    DEV_ACCOUNT_KEY,
    )
from azure.storage import AccessPolicy, X_MS_VERSION
from azure.storage.sharedaccesssignature import (
    Permission,
    SharedAccessPolicy,
    SharedAccessSignature,
    WebResource,
    RESOURCE_BLOB,
    RESOURCE_CONTAINER,
    SHARED_ACCESS_PERMISSION,
    SIGNED_EXPIRY,
    SIGNED_IDENTIFIER,
    SIGNED_PERMISSION,
    SIGNED_RESOURCE,
    SIGNED_RESOURCE_TYPE,
    SIGNED_SIGNATURE,
    SIGNED_START,
    )
from util import (
    AzureTestCase,
    credentials,
    getUniqueName,
    )

#------------------------------------------------------------------------------


class SharedAccessSignatureTest(AzureTestCase):

    def setUp(self):
        self.sas = SharedAccessSignature(account_name=DEV_ACCOUNT_NAME,
                                         account_key=DEV_ACCOUNT_KEY)

    def tearDown(self):
        return super(SharedAccessSignatureTest, self).tearDown()

    def test_generate_signature_container(self):
        accss_plcy = AccessPolicy()
        accss_plcy.start = '2011-10-11'
        accss_plcy.expiry = '2011-10-12'
        accss_plcy.permission = 'r'
        signed_identifier = 'YWJjZGVmZw=='
        sap = SharedAccessPolicy(accss_plcy, signed_identifier)
        signature = self.sas._generate_signature('images',
                                                 sap,
                                                 X_MS_VERSION)
        self.assertEqual(signature,
                         '1AWckmWSNrNCjh9krPXoD4exAgZWQQr38gG6z/ymkhQ=')

    def test_generate_signature_blob(self):
        accss_plcy = AccessPolicy()
        accss_plcy.start = '2011-10-11T11:03:40Z'
        accss_plcy.expiry = '2011-10-12T11:53:40Z'
        accss_plcy.permission = 'r'
        sap = SharedAccessPolicy(accss_plcy)

        signature = self.sas._generate_signature('images/pic1.png',
                                                 sap,
                                                 X_MS_VERSION)
        self.assertEqual(signature,
                         'ju4tX0G79vPxMOkBb7UfNVEgrj9+ZnSMutpUemVYHLY=')

    def test_blob_signed_query_string(self):
        accss_plcy = AccessPolicy()
        accss_plcy.start = '2011-10-11'
        accss_plcy.expiry = '2011-10-12'
        accss_plcy.permission = 'w'
        sap = SharedAccessPolicy(accss_plcy)
        qry_str = self.sas.generate_signed_query_string('images/pic1.png',
                                                        RESOURCE_BLOB,
                                                        sap)
        self.assertEqual(qry_str[SIGNED_START], '2011-10-11')
        self.assertEqual(qry_str[SIGNED_EXPIRY], '2011-10-12')
        self.assertEqual(qry_str[SIGNED_RESOURCE], RESOURCE_BLOB)
        self.assertEqual(qry_str[SIGNED_PERMISSION], 'w')
        self.assertEqual(qry_str[SIGNED_SIGNATURE],
                         '8I8E8TImfR2TIAcMDq8rF+IhhYyvowXpxSfF1kxnWLQ=')

    def test_container_signed_query_string(self):
        accss_plcy = AccessPolicy()
        accss_plcy.start = '2011-10-11'
        accss_plcy.expiry = '2011-10-12'
        accss_plcy.permission = 'r'
        signed_identifier = 'YWJjZGVmZw=='
        sap = SharedAccessPolicy(accss_plcy, signed_identifier)
        qry_str = self.sas.generate_signed_query_string('images',
                                                        RESOURCE_CONTAINER,
                                                        sap)
        self.assertEqual(qry_str[SIGNED_START], '2011-10-11')
        self.assertEqual(qry_str[SIGNED_EXPIRY], '2011-10-12')
        self.assertEqual(qry_str[SIGNED_RESOURCE], RESOURCE_CONTAINER)
        self.assertEqual(qry_str[SIGNED_PERMISSION], 'r')
        self.assertEqual(qry_str[SIGNED_IDENTIFIER], 'YWJjZGVmZw==')
        self.assertEqual(qry_str[SIGNED_SIGNATURE],
                         '1AWckmWSNrNCjh9krPXoD4exAgZWQQr38gG6z/ymkhQ=')

    def test_sign_request(self):
        accss_plcy = AccessPolicy()
        accss_plcy.start = '2011-10-11'
        accss_plcy.expiry = '2011-10-12'
        accss_plcy.permission = 'r'
        sap = SharedAccessPolicy(accss_plcy)
        qry_str = self.sas.generate_signed_query_string('images/pic1.png',
                                                        RESOURCE_BLOB,
                                                        sap)

        permission = Permission()
        permission.path = '/images/pic1.png'
        permission.query_string = qry_str
        self.sas.permission_set = [permission]

        web_rsrc = WebResource()
        web_rsrc.properties[SIGNED_RESOURCE_TYPE] = RESOURCE_BLOB
        web_rsrc.properties[SHARED_ACCESS_PERMISSION] = 'r'
        web_rsrc.path = '/images/pic1.png?comp=metadata'
        web_rsrc.request_url = '/images/pic1.png?comp=metadata'

        web_rsrc = self.sas.sign_request(web_rsrc)

        self.assertEqual(web_rsrc.request_url,
                         '/images/pic1.png?comp=metadata&' +
                         self.sas._convert_query_string(qry_str))

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
