# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from typing import Any, Dict, Optional, Union
from urllib.parse import unquote

from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError
)
from azure.storage.fileshare import (
    ContentSettings,
    DirectoryProperties,
    FileProperties,
    ShareServiceClient
)
from azure.storage.fileshare.aio import ShareServiceClient as AsyncShareServiceClient
from azure.storage.fileshare.aio import ShareFileClient, ShareDirectoryClient

from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils.storage.aio import AsyncStorageRecordedTestCase
from settings.testcase import FileSharePreparer


TEST_INTENT = 'backup'
TEST_FILE_PREFIX = 'file'
TEST_DIRECTORY_PREFIX = 'directory'


class TestStorageFileNFSAsync(AsyncStorageRecordedTestCase):

    fsc: AsyncShareServiceClient = None

    async def _setup(self, storage_account_name: str):
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
        if self.fsc:
            try:
                fsc = ShareServiceClient(
                    account_url=self.account_url,
                    credential=self.get_credential(ShareServiceClient),
                    token_intent=TEST_INTENT
                )
                fsc.delete_share(self.share_name)
            except:
                pass

    # --Helpers----------------------------------------------------------
    def _get_file_name(self, prefix: str = TEST_FILE_PREFIX):
        return self.get_resource_name(prefix)

    def _get_directory_name(self, prefix: str = TEST_DIRECTORY_PREFIX):
        return self.get_resource_name(prefix)

    def _assert_props(
        self, props: Optional[Union[DirectoryProperties, FileProperties]],
        owner: str,
        group: str,
        file_mode: str,
        nfs_file_type: Optional[str] = None
    ) -> None:
        assert props is not None
        assert props.owner == owner
        assert props.group == group
        assert props.file_mode == file_mode
        assert props.file_attributes is None
        assert props.permission_key is None

        if nfs_file_type:
            assert props.nfs_file_type == nfs_file_type
        if isinstance(props, FileProperties):
            assert props.link_count == 1

    def _assert_copy(self, copy: Optional[Dict[str, Any]]) -> None:
        assert copy is not None
        assert copy['copy_status'] == 'success'
        assert copy['copy_id'] is not None

    # --Test cases for NFS ----------------------------------------------
    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_directory_and_set_directory_properties(self, **kwargs: Any):
        premium_storage_file_account_name = kwargs.pop("premium_storage_file_account_name")

        await self._setup(premium_storage_file_account_name)

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
        self._assert_props(props, create_owner, create_group, create_file_mode, 'Directory')

        await directory_client.set_http_headers(owner=set_owner, group=set_group, file_mode=set_file_mode)
        props = await directory_client.get_directory_properties()
        self._assert_props(props, set_owner, set_group, set_file_mode, 'Directory')

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_file_and_set_file_properties(self, **kwargs: Any):
        premium_storage_file_account_name = kwargs.pop("premium_storage_file_account_name")

        await self._setup(premium_storage_file_account_name)

        file_name = self._get_file_name()
        file_client = ShareFileClient(
            self.account_url,
            share_name=self.share_name,
            file_path=file_name,
            credential=self.credential,
            token_intent=TEST_INTENT
        )

        create_owner, create_group, create_file_mode = '345', '123', '7777'
        set_owner, set_group, set_file_mode = '0', '0', '0644'
        content_settings = ContentSettings(
            content_language='spanish',
            content_disposition='inline'
        )

        await file_client.create_file(1024, owner=create_owner, group=create_group, file_mode=create_file_mode)
        props = await file_client.get_file_properties()
        self._assert_props(props, create_owner, create_group, create_file_mode, 'Regular')

        await file_client.set_http_headers(
            content_settings=content_settings,
            owner=set_owner,
            group=set_group,
            file_mode=set_file_mode
        )
        props = await file_client.get_file_properties()
        self._assert_props(props, set_owner, set_group, set_file_mode, 'Regular')

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_download_and_copy_file(self, **kwargs: Any):
        premium_storage_file_account_name = kwargs.pop("premium_storage_file_account_name")

        await self._setup(premium_storage_file_account_name)

        default_owner, default_group, default_file_mode = '0', '0', '0664'
        source_owner, source_group, source_file_mode = '999', '888', '0111'
        override_owner, override_group, override_file_mode = '54321', '12345', '7777'
        data = b'abcdefghijklmnop' * 32

        share_client = self.fsc.get_share_client(self.share_name)

        file_name = self._get_file_name()
        file_client = share_client.get_file_client(file_name)
        await file_client.create_file(size=1024, owner=source_owner, group=source_group, file_mode=source_file_mode)

        await file_client.upload_range(data, offset=0, length=512)
        props = (await file_client.download_file()).properties
        self._assert_props(props, source_owner, source_group, source_file_mode)

        new_client_source_copy = ShareFileClient(
            self.account_url,
            share_name=self.share_name,
            file_path='newclientsourcecopy',
            credential=self.credential,
            token_intent=TEST_INTENT
        )
        copy = await new_client_source_copy.start_copy_from_url(
            file_client.url,
            file_mode_copy_mode='source',
            owner_copy_mode='source'
        )
        self._assert_copy(copy)
        props = await new_client_source_copy.get_file_properties()
        self._assert_props(props, source_owner, source_group, source_file_mode)

        new_client_default_copy = ShareFileClient(
            self.account_url,
            share_name=self.share_name,
            file_path='newclientdefaultcopy',
            credential=self.credential,
            token_intent=TEST_INTENT
        )
        copy = await new_client_default_copy.start_copy_from_url(file_client.url)
        self._assert_copy(copy)
        props = await new_client_default_copy.get_file_properties()
        self._assert_props(props, default_owner, default_group, default_file_mode)

        new_client_override_copy = ShareFileClient(
            self.account_url,
            share_name=self.share_name,
            file_path='newclientoverridecopy',
            credential=self.credential,
            token_intent=TEST_INTENT
        )
        copy = await new_client_override_copy.start_copy_from_url(
            file_client.url,
            owner=override_owner,
            group=override_group,
            file_mode=override_file_mode,
            file_mode_copy_mode='override',
            owner_copy_mode='override'
        )
        self._assert_copy(copy)
        props = await new_client_override_copy.get_file_properties()
        self._assert_props(props, override_owner, override_group, override_file_mode)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_hardlink(self, **kwargs: Any):
        premium_storage_file_account_name = kwargs.pop("premium_storage_file_account_name")

        await self._setup(premium_storage_file_account_name)

        share_client = self.fsc.get_share_client(self.share_name)
        directory_name = self._get_directory_name()
        directory_client = await share_client.create_directory(directory_name)
        source_file_name = self._get_file_name('file1')
        source_file_client = directory_client.get_file_client(source_file_name)
        await source_file_client.create_file(size=1024)
        hard_link_file_name = self._get_file_name('file2')
        hard_link_file_client = directory_client.get_file_client(hard_link_file_name)

        resp = await hard_link_file_client.create_hardlink(target=f"{directory_name}/{source_file_name}")

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
    async def test_create_hardlink_error(self, **kwargs: Any):
        premium_storage_file_account_name = kwargs.pop("premium_storage_file_account_name")

        await self._setup(premium_storage_file_account_name)

        share_client = self.fsc.get_share_client(self.share_name)
        directory_name = self._get_directory_name()
        directory_client = share_client.get_directory_client(directory_name)
        source_file_name = self._get_file_name('file1')
        source_file_client = directory_client.get_file_client(source_file_name)
        hard_link_file_name = self._get_file_name('file2')
        hard_link_file_client = directory_client.get_file_client(hard_link_file_name)

        with pytest.raises(ResourceNotFoundError) as e:
            await hard_link_file_client.create_hardlink(target=f"{directory_name}/{source_file_name}")

        assert 'ParentNotFound' in e.value.args[0]

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_and_get_symlink(self, **kwargs):
        premium_storage_file_account_name = kwargs.pop("premium_storage_file_account_name")

        await self._setup(premium_storage_file_account_name)

        share_client = self.fsc.get_share_client(self.share_name)
        directory_name = self._get_directory_name()
        directory_client = await share_client.create_directory(directory_name)
        source_file_name = self._get_file_name('file1')
        source_file_client = directory_client.get_file_client(source_file_name)
        await source_file_client.create_file(size=1024)
        symbolic_link_file_name = self._get_file_name('file2')
        symbolic_link_file_client = directory_client.get_file_client(symbolic_link_file_name)
        metadata = {"test1": "foo", "test2": "bar"}
        owner, group = "345", "123"
        target = f"{directory_name}/{source_file_name}"

        resp = await symbolic_link_file_client.create_symlink(
            target=target,
            metadata=metadata,
            owner=owner,
            group=group
        )
        assert resp is not None
        assert resp['file_file_type'] == 'SymLink'
        assert resp['owner'] == owner
        assert resp['group'] == group
        assert resp['file_creation_time'] is not None
        assert resp['file_last_write_time'] is not None
        assert resp['file_id'] is not None
        assert resp['file_parent_id'] is not None
        assert 'file_attributes' not in resp
        assert 'file_permission_key' not in resp

        resp = await symbolic_link_file_client.get_symlink()
        assert resp is not None
        assert resp['etag'] is not None
        assert resp['last_modified'] is not None
        assert unquote(resp['link_text']) == target

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_and_get_symlink_error(self, **kwargs):
        premium_storage_file_account_name = kwargs.pop("premium_storage_file_account_name")

        await self._setup(premium_storage_file_account_name)

        share_client = self.fsc.get_share_client(self.share_name)
        directory_name = self._get_directory_name()
        directory_client = share_client.get_directory_client(directory_name)
        source_file_name = self._get_file_name('file1')
        source_file_client = directory_client.get_file_client(source_file_name)
        symbolic_link_file_name = self._get_file_name('file2')
        symbolic_link_file_client = directory_client.get_file_client(symbolic_link_file_name)
        target = f"{directory_name}/{source_file_name}"

        with pytest.raises(ResourceNotFoundError) as e:
            await symbolic_link_file_client.create_symlink(target=target)
        assert 'ParentNotFound' in e.value.args[0]

        with pytest.raises(ResourceNotFoundError) as e:
            await symbolic_link_file_client.get_symlink()
        assert 'ParentNotFound' in e.value.args[0]
