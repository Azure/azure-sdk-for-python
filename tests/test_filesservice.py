# coding: utf-8
#-------------------------------------------------------------------------
# Copyright (c) 2015 SUSE Linux GmbH.  All rights reserved.
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
import base64
import datetime
import os
import random
import sys
import time
import unittest
if sys.version_info < (3,):
    from httplib import HTTPConnection
else:
    from http.client import HTTPConnection

from azure.files.filesservice import FilesService

from azure.storage.storageclient import (
    AZURE_STORAGE_ACCESS_KEY,
    AZURE_STORAGE_ACCOUNT,
    EMULATED,
    DEV_ACCOUNT_NAME,
    DEV_ACCOUNT_KEY,
    )

from util import (
    AzureTestCase,
    credentials,
    getUniqueName,
    set_service_options,
    )


#------------------------------------------------------------------------------


class FilesServiceTest(AzureTestCase):

    def setUp(self):
        self.fs = FilesService(
            credentials.getStorageServicesName(),
            credentials.getStorageServicesKey()
        )

        self.sharename = 'testshare'
        self.timeout = 1
        self.trycount = 60

        remote_storage_service_name = credentials.getRemoteStorageServicesName()
        remote_storage_service_key = credentials.getRemoteStorageServicesKey()
        if not remote_storage_service_key or not remote_storage_service_name:
            print("Remote Storage Account not configured. Add " \
                  "'remotestorageserviceskey' and 'remotestorageservicesname'" \
                  " to windowsazurecredentials.json to test functionality " \
                  "involving multiple storage accounts.")

    def tearDown(self):
        return super(FilesServiceTest, self).tearDown()

    def test_create_and_list_share(self):
        try_count = 0
        while try_count < self.trycount:
            try:
                created = self.fs.create_share(self.sharename)
                self.assertTrue(created)
                try_count = self.trycount
            except:
                time.sleep(self.timeout)
                try_count = try_count + 1
        share_name = None
        try_count = 0
        while try_count < self.trycount:
            try:
                for share in self.fs.list_shares():
                    if share.name == self.sharename:
                        share_name = share.name
                        try_count = self.trycount
                        break
            except:
                time.sleep(self.timeout)
                try_count = try_count + 1
        self.assertEqual(share_name, self.sharename)

    def test_delete_share(self):
        deleted = self.fs.delete_share(self.sharename)
        self.assertTrue(deleted)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
