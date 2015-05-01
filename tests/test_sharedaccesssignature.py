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
from azure.storage import AccessPolicy
from azure.storage.sharedaccesssignature import (
    SharedAccessPolicy,
    SharedAccessSignature,
    QueryStringConstants,
    ResourceType,
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

    def test_generate_signed_query_dict_container_with_access_policy(self):
        accss_plcy = AccessPolicy()
        accss_plcy.start = '2011-10-11'
        accss_plcy.expiry = '2011-10-12'
        accss_plcy.permission = 'r'

        query = self.sas._generate_signed_query_dict(
            'images',
            ResourceType.RESOURCE_CONTAINER,
            SharedAccessPolicy(accss_plcy),
        )

        self.assertEqual(query[QueryStringConstants.SIGNED_START], '2011-10-11')
        self.assertEqual(query[QueryStringConstants.SIGNED_EXPIRY], '2011-10-12')
        self.assertEqual(query[QueryStringConstants.SIGNED_RESOURCE], ResourceType.RESOURCE_CONTAINER)
        self.assertEqual(query[QueryStringConstants.SIGNED_PERMISSION], 'r')
        self.assertEqual(query[QueryStringConstants.SIGNED_SIGNATURE],
                         'CxLWN56cjXidpI9em7RDgSN2QIgLggTqrnzudH2XsOY=')

    def test_generate_signed_query_dict_container_with_signed_identifier(self):
        signed_identifier = 'YWJjZGVmZw=='

        query = self.sas._generate_signed_query_dict(
            'images',
            ResourceType.RESOURCE_CONTAINER,
            SharedAccessPolicy(signed_identifier=signed_identifier),
        )

        self.assertEqual(query[QueryStringConstants.SIGNED_RESOURCE], ResourceType.RESOURCE_CONTAINER)
        self.assertEqual(query[QueryStringConstants.SIGNED_IDENTIFIER], signed_identifier)
        self.assertEqual(query[QueryStringConstants.SIGNED_SIGNATURE],
                         'BbzpLHe+JxNAsW/v6LttP5x9DdGMvXsZpm2chKblr3s=')

    def test_generate_signed_query_dict_blob_with_access_policy_and_headers(self):
        accss_plcy = AccessPolicy()
        accss_plcy.start = '2011-10-11T11:03:40Z'
        accss_plcy.expiry = '2011-10-12T11:53:40Z'
        accss_plcy.permission = 'r'

        query = self.sas._generate_signed_query_dict(
            'images/pic1.png',
            ResourceType.RESOURCE_BLOB,
            SharedAccessPolicy(accss_plcy),
            content_disposition='file; attachment',
            content_type='binary',
        )

        self.assertEqual(query[QueryStringConstants.SIGNED_START], '2011-10-11T11:03:40Z')
        self.assertEqual(query[QueryStringConstants.SIGNED_EXPIRY], '2011-10-12T11:53:40Z')
        self.assertEqual(query[QueryStringConstants.SIGNED_RESOURCE], ResourceType.RESOURCE_BLOB)
        self.assertEqual(query[QueryStringConstants.SIGNED_PERMISSION], 'r')
        self.assertEqual(query[QueryStringConstants.SIGNED_CONTENT_DISPOSITION], 'file; attachment')
        self.assertEqual(query[QueryStringConstants.SIGNED_CONTENT_TYPE], 'binary')
        self.assertEqual(query[QueryStringConstants.SIGNED_SIGNATURE],
                         'uHckUC6T+BwUsc+DgrreyIS1k6au7uUd7LSSs/z+/+w=')


    def test_generate_signed_query_dict_blob_with_access_policy(self):
        accss_plcy = AccessPolicy()
        accss_plcy.start = '2011-10-11'
        accss_plcy.expiry = '2011-10-12'
        accss_plcy.permission = 'w'

        query = self.sas._generate_signed_query_dict(
            'images/pic1.png',
            ResourceType.RESOURCE_BLOB,
            SharedAccessPolicy(accss_plcy),
        )

        self.assertEqual(query[QueryStringConstants.SIGNED_START], '2011-10-11')
        self.assertEqual(query[QueryStringConstants.SIGNED_EXPIRY], '2011-10-12')
        self.assertEqual(query[QueryStringConstants.SIGNED_RESOURCE], ResourceType.RESOURCE_BLOB)
        self.assertEqual(query[QueryStringConstants.SIGNED_PERMISSION], 'w')
        self.assertEqual(query[QueryStringConstants.SIGNED_SIGNATURE],
                         'Fqt8tNcyUOp30qYRtSFNcImrRMcxlk6IF17O4l96KT8=')

    def test_generate_signed_query_dict_blob_with_signed_identifier(self):
        signed_identifier = 'YWJjZGVmZw=='

        query = self.sas._generate_signed_query_dict(
            'images',
            ResourceType.RESOURCE_CONTAINER,
            SharedAccessPolicy(signed_identifier=signed_identifier),
        )

        self.assertEqual(query[QueryStringConstants.SIGNED_RESOURCE], ResourceType.RESOURCE_CONTAINER)
        self.assertEqual(query[QueryStringConstants.SIGNED_IDENTIFIER], signed_identifier)
        self.assertEqual(query[QueryStringConstants.SIGNED_SIGNATURE],
                         'BbzpLHe+JxNAsW/v6LttP5x9DdGMvXsZpm2chKblr3s=')


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
