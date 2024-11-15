# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError, ResourceExistsError, ResourceNotFoundError
from azure.storage.fileshare import ShareServiceClient
from azure.storage.fileshare.aio import ShareServiceClient as AsyncShareServiceClient
from azure.storage.fileshare.aio import ShareDirectoryClient

from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils.storage.aio import AsyncStorageRecordedTestCase
from settings.testcase import FileSharePreparer


TEST_INTENT = 'backup'
TEST_FILE_PREFIX = 'file'
TEST_DIRECTORY_PREFIX = 'directory'


class TestStorageFileNFSAsync(AsyncStorageRecordedTestCase):

    fsc: ShareServiceClient = None

    async def _setup(self, storage_account_name):
        self.account_url = self.account_url(storage_account_name, 'file')
        self.credential = self.get_credential(AsyncShareServiceClient, is_async=True)
        self.fsc = AsyncShareServiceClient(
            account_url=self.account_url,
            credential=self.credential,
            token_intent=TEST_INTENT
        )
        self.share_name = self.get_resource_name('utshare')

        async with AsyncShareServiceClient(
            account_url=self.account_url,
            credential=self.credential,
            token_intent=TEST_INTENT
        ) as fsc:
            if self.is_live:
                try:
                    await fsc.create_share(self.share_name, protocols='NFS')
                except:
                    pass

    def teardown_method(self):
        fsc = ShareServiceClient(
            account_url=self.account_url,
            credential=self.get_credential(ShareServiceClient),
            token_intent=TEST_INTENT
        )
        if fsc:
            try:
                fsc.delete_share(self.share_name)
            except:
                pass

    # --Helpers----------------------------------------------------------
    def _get_file_name(self, prefix=TEST_FILE_PREFIX):
        return self.get_resource_name(prefix)

    def _get_directory_name(self, prefix=TEST_DIRECTORY_PREFIX):
        return self.get_resource_name(prefix)

    # --Test cases for NFS ----------------------------------------------
    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_directory_and_set_directory_properties(self, **kwargs):
        storage_account_name = kwargs.pop('storage_account_name')

        await self._setup(storage_account_name)

        create_owner, create_group, create_file_mode = '345', '123', '7777'
        set_owner, set_group, set_file_mode = '0', '0', '0755'

        share_client = self.fsc.get_share_client(self.share_name)
        directory_client = ShareDirectoryClient(
            self.account_url,
            share_client.share_name, 'dir1',
            credential=self.credential,
            token_intent=TEST_INTENT
        )

        await directory_client.create_directory(owner=create_owner, group=create_group, file_mode=create_file_mode)
        props = await directory_client.get_directory_properties()

        assert props is not None
        assert props.owner == create_owner
        assert props.group == create_group
        assert props.file_mode == create_file_mode
        assert props.nfs_file_type == 'Directory'
        assert props.file_attributes is None
        assert props.permission_key is None

        await directory_client.set_http_headers(owner=set_owner, group=set_group, file_mode=set_file_mode)
        props = await directory_client.get_directory_properties()

        assert props is not None
        assert props.owner == set_owner
        assert props.group == set_group
        assert props.file_mode == set_file_mode
        assert props.nfs_file_type == 'Directory'
        assert props.file_attributes is None
        assert props.permission_key is None

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_hard_link(self, **kwargs):
        storage_account_name = kwargs.pop('storage_account_name')

        await self._setup(storage_account_name)

        share_client = self.fsc.get_share_client(self.share_name)
        directory_name = self._get_directory_name()
        directory_client = await share_client.create_directory(directory_name)
        source_file_name = self._get_file_name('file1')
        source_file_client = directory_client.get_file_client(source_file_name)
        await source_file_client.create_file(size=1024)
        hard_link_file_name = self._get_file_name('file2')
        hard_link_file_client = directory_client.get_file_client(hard_link_file_name)

        resp = await hard_link_file_client.create_hard_link(target_file=f"{directory_name}/{source_file_name}")

        assert resp is not None
        assert resp['file_file_type'] == 'Regular'
        assert resp['owner'] == '0'
        assert resp['group'] == '0'
        assert resp['mode'] == '0664'
        assert resp['link_count'] == 2

        assert resp['file_creation_time'] is not None
        assert resp['file_last_write_time'] is not None
        assert resp['file_change_time'] is not None
        assert resp['file_id'] is not None
        assert resp['file_parent_id'] is not None

        assert 'file_attributes' not in resp
        assert 'file_response_key' not in resp

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_hard_link_error_1(self, **kwargs):
        storage_account_name = kwargs.pop('storage_account_name')

        await self._setup(storage_account_name)

        share_client = self.fsc.get_share_client(self.share_name)
        directory_name = self._get_directory_name()
        directory_client = await share_client.create_directory(directory_name)
        source_file_name = self._get_file_name()
        source_file_client = directory_client.get_file_client(source_file_name)
        hard_link_file_name = self._get_file_name()
        hard_link_file_client = directory_client.get_file_client(hard_link_file_name)

        with pytest.raises(ResourceNotFoundError) as e:
            await hard_link_file_client.create_hard_link(target_file=source_file_client.url)

        assert 'ParentNotFound' in e.value.args[0]
