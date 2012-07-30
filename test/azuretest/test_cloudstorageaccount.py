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

from azure.storage import *
from azuretest.util import *

import unittest

#------------------------------------------------------------------------------
class CloudStorageAccountTest(AzureTestCase):

    def setUp(self):
        self.account = CloudStorageAccount(account_name=credentials.getStorageServicesName(), 
                                           account_key=credentials.getStorageServicesKey())

    #--Test cases --------------------------------------------------------
    def test_create_blob_service(self):
        # Arrange

        # Act
        service = self.account.create_blob_service()

        # Assert
        self.assertIsNotNone(service)
        self.assertIsInstance(service, BlobService)
        self.assertEqual(service.account_name, credentials.getStorageServicesName())
        self.assertEqual(service.account_key, credentials.getStorageServicesKey())

    def test_create_blob_service_empty_credentials(self):
        # Arrange

        # Act
        bad_account = CloudStorageAccount('', '')
        with self.assertRaises(WindowsAzureError):
            service = bad_account.create_blob_service()

        # Assert

    def test_create_table_service(self):
        # Arrange

        # Act
        service = self.account.create_table_service()

        # Assert
        self.assertIsNotNone(service)
        self.assertIsInstance(service, TableService)
        self.assertEqual(service.account_name, credentials.getStorageServicesName())
        self.assertEqual(service.account_key, credentials.getStorageServicesKey())

    def test_create_queue_service(self):
        # Arrange

        # Act
        service = self.account.create_queue_service()

        # Assert
        self.assertIsNotNone(service)
        self.assertIsInstance(service, QueueService)
        self.assertEqual(service.account_name, credentials.getStorageServicesName())
        self.assertEqual(service.account_key, credentials.getStorageServicesKey())

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
