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

from azure.common import (
    WindowsAzureError,
    WindowsAzureConflictError,
    WindowsAzureMissingResourceError
)
from azure.storage import (
    DEV_ACCOUNT_NAME,
    DEV_ACCOUNT_KEY,
    AccessPolicy,
    Logging,
    HourMetrics,
    MinuteMetrics,
    SharedAccessPolicy,
    SignedIdentifier,
    SignedIdentifiers,
    StorageServiceProperties
)
from azure.storage.files import (
    FILES_SERVICE_HOST_BASE,
    FilesService
)
from azure.storage.storageclient import (
    AZURE_STORAGE_ACCESS_KEY,
    AZURE_STORAGE_ACCOUNT,
    EMULATED,
)
from testutils.common_recordingtestcase import (
    TestMode,
    record,
)
from tests.storage_testcase import StorageTestCase

#------------------------------------------------------------------------------


class FilesServiceTest(StorageTestCase):

    def setUp(self):
        super(FilesServiceTest, self).setUp()

        if self.settings.REMOTE_STORAGE_ACCOUNT_NAME and self.settings.REMOTE_STORAGE_ACCOUNT_KEY:
            self.fs = self._create_storage_service(
                FilesService,
                self.settings,
                self.settings.REMOTE_STORAGE_ACCOUNT_NAME,
                self.settings.REMOTE_STORAGE_ACCOUNT_KEY,
            )
        else:
            print("REMOTE_STORAGE_ACCOUNT_NAME and REMOTE_STORAGE_ACCOUNT_KEY not set in test settings file.")

        self.sharename = 'testshare'
        self.timeout = 1
        self.trycount = 60

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
