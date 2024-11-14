# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import base64
import tempfile
from datetime import datetime, timedelta, timezone

import pytest
import requests
from azure.core import MatchConditions
from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError, ResourceExistsError, ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.storage.fileshare import (
    AccessPolicy,
    AccountSasPermissions,
    ContentSettings,
    FileSasPermissions,
    generate_account_sas,
    generate_file_sas,
    generate_share_sas,
    NTFSAttributes,
    ResourceTypes,
    ShareFileClient,
    ShareSasPermissions,
    ShareServiceClient,
    ShareDirectoryClient,
    StorageErrorCode
)

from devtools_testutils import recorded_by_proxy_async
from devtools_testutils.storage import AsyncStorageRecordedTestCase
from settings.testcase import FileSharePreparer
from test_helpers import ProgressTracker


TEST_INTENT = 'backup'
TEST_FILE_PREFIX = 'file'
TEST_DIRECTORY_PREFIX = 'directory'


class TestStorageFileNFSAsync(AsyncStorageRecordedTestCase):

    fsc: ShareServiceClient = None

    def _setup(self, storage_account_name):
        account_url = self.account_url(storage_account_name, "file")
        self.credential = self.get_credential(ShareServiceClient)

        # TODO: Create an async share client directly
        self.fsc = ShareServiceClient(account_url=account_url, credential=self.credential, token_intent=TEST_INTENT)
        self.share_name = self.get_resource_name('utshare')
        if self.is_live:
            try:
                self.fsc.create_share(self.share_name, protocols='NFS')
            except:
                pass

    def teardown_method(self):
        # TODO: Create a sync share client, then delete the async one here
        if self.fsc:
            try:
                self.fsc.delete_share()
            except:
                pass

    # --Helpers-----------------------------------------------------------------
    def _get_file_name(self, prefix=TEST_FILE_PREFIX):
        return self.get_resource_name(prefix)

    def _get_directory_name(self, prefix=TEST_DIRECTORY_PREFIX):
        return self.get_resource_name(prefix)

    # --Test cases for NFS ----------------------------------------------
    @FileSharePreparer()
    @recorded_by_proxy
    def test_create_hard_link(self, **kwargs):
        storage_account_name = kwargs.pop('storage_account_name')

        self._setup(storage_account_name)

        props = self.fsc.get_service_properties()
        assert props is not None
