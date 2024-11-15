# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError, ResourceExistsError, ResourceNotFoundError
from azure.storage.fileshare import ShareServiceClient
from azure.storage.fileshare.aio import ShareServiceClient as AsyncShareServiceClient

from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils.storage.aio import AsyncStorageRecordedTestCase
from settings.testcase import FileSharePreparer


TEST_INTENT = 'backup'
TEST_FILE_PREFIX = 'file'
TEST_DIRECTORY_PREFIX = 'directory'


class TestStorageFileNFSAsync(AsyncStorageRecordedTestCase):

    fsc: ShareServiceClient = None

    async def _setup(self, storage_account_name):
        self.account_url = self.account_url(storage_account_name, "file")
        self.credential = self.get_credential(ShareServiceClient)
        self.fsc = ShareServiceClient(
            account_url=self.account_url,
            credential=self.credential,
            token_intent=TEST_INTENT
        )
        self.share_name = self.get_resource_name('utshare')

        async with AsyncShareServiceClient(
            account_url=self.account_url,
            credential=self.get_credential(ShareServiceClient, is_async=True),
            token_intent=TEST_INTENT
        ) as fsc:
            if self.is_live:
                try:
                    await fsc.create_share(self.share_name, protocols='NFS')
                except:
                    pass

    def teardown_method(self):
        if self.fsc:
            try:
                self.fsc.delete_share(self.share_name)
            except:
                pass

    # --Helpers-----------------------------------------------------------------
    def _get_file_name(self, prefix=TEST_FILE_PREFIX):
        return self.get_resource_name(prefix)

    def _get_directory_name(self, prefix=TEST_DIRECTORY_PREFIX):
        return self.get_resource_name(prefix)

    # --Test cases for NFS ----------------------------------------------
    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_hard_link_playground(self, **kwargs):
        storage_account_name = kwargs.pop('storage_account_name')

        await self._setup(storage_account_name)

        props = self.fsc.get_service_properties()
        assert props is not None
