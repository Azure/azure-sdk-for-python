# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any, Dict, Optional, Union
from urllib.parse import unquote

import pytest

from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils.storage.aio import AsyncStorageRecordedTestCase
from settings.testcase import FileSharePreparer

from azure.core.exceptions import HttpResponseError, ResourceExistsError, ResourceNotFoundError
from azure.core.pipeline.transport import (  # pylint: disable=no-name-in-module
    AioHttpTransportResponse,
    AsyncHttpTransport,
)
from azure.storage.fileshare import (
    ContentSettings,
    DirectoryProperties,
    FileProperties,
    ShareServiceClient,
)
from azure.storage.fileshare.aio import ShareDirectoryClient, ShareFileClient
from azure.storage.fileshare.aio import ShareServiceClient as AsyncShareServiceClient

from requests.structures import CaseInsensitiveDict

from test_helpers_async import MockAioHttpClientResponse
from test_nfs import LIST_FILES_AND_DIRECTORIES_NFS_XML

TEST_INTENT = "backup"
TEST_FILE_PREFIX = "file"
TEST_DIRECTORY_PREFIX = "directory"


class MockListTransport(AsyncHttpTransport):
    """A transport that returns a canned XML body for the list operation (an HTTP GET)."""

    def __init__(self, body: bytes) -> None:
        self._body = body

    async def send(self, request, **kwargs) -> AioHttpTransportResponse:
        rest_response = AioHttpTransportResponse(
            request=request,
            aiohttp_response=MockAioHttpClientResponse(
                request.url,
                self._body,
                CaseInsensitiveDict({"Content-Type": "application/xml", "Content-Length": str(len(self._body))}),
            ),
            decompress=False,
        )
        await rest_response.load_body()
        return rest_response

    async def open(self) -> None:
        pass

    async def close(self) -> None:
        pass

    async def __aenter__(self) -> "MockListTransport":
        return self

    async def __aexit__(self, *args: Any) -> None:
        pass


class TestStorageFileNFSAsync(AsyncStorageRecordedTestCase):

    fsc: AsyncShareServiceClient = None

    async def _setup(self, storage_account_name: str, storage_account_key: Optional[str] = None) -> None:
        self.account_url = self.account_url(storage_account_name, "file")
        self.credential = getattr(storage_account_key, "secret", None) or self.get_credential(
            AsyncShareServiceClient, is_async=True
        )
        self.fsc = AsyncShareServiceClient(
            account_url=self.account_url, credential=self.credential, token_intent=TEST_INTENT
        )
        self.share_name = self.get_resource_name("utshare")

        async with AsyncShareServiceClient(
            account_url=self.account_url, credential=self.credential, token_intent=TEST_INTENT
        ) as fsc:
            if self.is_live:
                try:
                    await fsc.create_share(self.share_name, protocols="NFS")
                except ResourceExistsError:
                    pass

    def teardown_method(self):
        if self.is_live and self.fsc:
            try:
                fsc = ShareServiceClient(
                    account_url=self.account_url,
                    credential=self.get_credential(ShareServiceClient),
                    token_intent=TEST_INTENT,
                )
                fsc.delete_share(self.share_name)
            except HttpResponseError:
                pass

    # --Helpers----------------------------------------------------------
    def _get_file_name(self, prefix: str = TEST_FILE_PREFIX):
        return self.get_resource_name(prefix)

    def _get_directory_name(self, prefix: str = TEST_DIRECTORY_PREFIX):
        return self.get_resource_name(prefix)

    def _assert_props(
        self,
        props: Optional[Union[DirectoryProperties, FileProperties]],
        owner: str,
        group: str,
        file_mode: str,
        nfs_file_type: Optional[str] = None,
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
        assert copy["copy_status"] == "success"
        assert copy["copy_id"] is not None

    # --Test cases for NFS ----------------------------------------------
    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_directory_and_set_directory_properties(self, **kwargs: Any):
        premium_storage_file_account_name = kwargs.pop("premium_storage_file_account_name")

        await self._setup(premium_storage_file_account_name)

        create_owner, create_group, create_file_mode = "345", "123", "7777"
        set_owner, set_group, set_file_mode = "0", "0", "0755"

        share_client = self.fsc.get_share_client(self.share_name)
        directory_client = ShareDirectoryClient(
            self.account_url, share_client.share_name, "dir1", credential=self.credential, token_intent=TEST_INTENT
        )

        await directory_client.create_directory(owner=create_owner, group=create_group, file_mode=create_file_mode)
        props = await directory_client.get_directory_properties()
        self._assert_props(props, create_owner, create_group, create_file_mode, "Directory")

        await directory_client.set_http_headers(owner=set_owner, group=set_group, file_mode=set_file_mode)
        props = await directory_client.get_directory_properties()
        self._assert_props(props, set_owner, set_group, set_file_mode, "Directory")

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
            token_intent=TEST_INTENT,
        )

        create_owner, create_group, create_file_mode = "345", "123", "7777"
        set_owner, set_group, set_file_mode = "0", "0", "0644"
        content_settings = ContentSettings(content_language="spanish", content_disposition="inline")

        await file_client.create_file(1024, owner=create_owner, group=create_group, file_mode=create_file_mode)
        props = await file_client.get_file_properties()
        self._assert_props(props, create_owner, create_group, create_file_mode, "Regular")

        await file_client.set_http_headers(
            content_settings=content_settings, owner=set_owner, group=set_group, file_mode=set_file_mode
        )
        props = await file_client.get_file_properties()
        self._assert_props(props, set_owner, set_group, set_file_mode, "Regular")

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_download_and_copy_file(self, **kwargs: Any):
        premium_storage_file_account_name = kwargs.pop("premium_storage_file_account_name")

        await self._setup(premium_storage_file_account_name)

        default_owner, default_group, default_file_mode = "0", "0", "0664"
        source_owner, source_group, source_file_mode = "999", "888", "0111"
        override_owner, override_group, override_file_mode = "54321", "12345", "7777"
        data = b"abcdefghijklmnop" * 32

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
            file_path="newclientsourcecopy",
            credential=self.credential,
            token_intent=TEST_INTENT,
        )
        copy = await new_client_source_copy.start_copy_from_url(
            file_client.url, file_mode_copy_mode="source", owner_copy_mode="source"
        )
        self._assert_copy(copy)
        props = await new_client_source_copy.get_file_properties()
        self._assert_props(props, source_owner, source_group, source_file_mode)

        new_client_default_copy = ShareFileClient(
            self.account_url,
            share_name=self.share_name,
            file_path="newclientdefaultcopy",
            credential=self.credential,
            token_intent=TEST_INTENT,
        )
        copy = await new_client_default_copy.start_copy_from_url(file_client.url)
        self._assert_copy(copy)
        props = await new_client_default_copy.get_file_properties()
        self._assert_props(props, default_owner, default_group, default_file_mode)

        new_client_override_copy = ShareFileClient(
            self.account_url,
            share_name=self.share_name,
            file_path="newclientoverridecopy",
            credential=self.credential,
            token_intent=TEST_INTENT,
        )
        copy = await new_client_override_copy.start_copy_from_url(
            file_client.url,
            owner=override_owner,
            group=override_group,
            file_mode=override_file_mode,
            file_mode_copy_mode="override",
            owner_copy_mode="override",
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
        source_file_name = self._get_file_name("file1")
        source_file_client = directory_client.get_file_client(source_file_name)
        await source_file_client.create_file(size=1024)
        hard_link_file_name = self._get_file_name("file2")
        hard_link_file_client = directory_client.get_file_client(hard_link_file_name)

        resp = await hard_link_file_client.create_hardlink(target=f"{directory_name}/{source_file_name}")

        assert resp is not None
        assert resp["file_file_type"] == "Regular"
        assert resp["owner"] == "0"
        assert resp["group"] == "0"
        assert resp["mode"] == "0664"
        assert resp["link_count"] == 2

        assert resp["file_creation_time"] is not None
        assert resp["file_last_write_time"] is not None
        assert resp["file_change_time"] is not None
        assert resp["file_id"] is not None
        assert resp["file_parent_id"] is not None

        assert "file_attributes" not in resp
        assert "file_response_key" not in resp

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_hardlink_error(self, **kwargs: Any):
        premium_storage_file_account_name = kwargs.pop("premium_storage_file_account_name")

        await self._setup(premium_storage_file_account_name)

        share_client = self.fsc.get_share_client(self.share_name)
        directory_name = self._get_directory_name()
        directory_client = share_client.get_directory_client(directory_name)
        source_file_name = self._get_file_name("file1")
        hard_link_file_name = self._get_file_name("file2")
        hard_link_file_client = directory_client.get_file_client(hard_link_file_name)

        with pytest.raises(ResourceNotFoundError) as e:
            await hard_link_file_client.create_hardlink(target=f"{directory_name}/{source_file_name}")

        assert "ParentNotFound" in e.value.args[0]

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_and_get_symlink(self, **kwargs):
        premium_storage_file_account_name = kwargs.pop("premium_storage_file_account_name")

        await self._setup(premium_storage_file_account_name)

        share_client = self.fsc.get_share_client(self.share_name)
        directory_name = self._get_directory_name()
        directory_client = await share_client.create_directory(directory_name)
        source_file_name = self._get_file_name("file1")
        source_file_client = directory_client.get_file_client(source_file_name)
        await source_file_client.create_file(size=1024)
        symbolic_link_file_name = self._get_file_name("file2")
        symbolic_link_file_client = directory_client.get_file_client(symbolic_link_file_name)
        metadata = {"test1": "foo", "test2": "bar"}
        owner, group = "345", "123"
        target = f"{directory_name}/{source_file_name}"

        resp = await symbolic_link_file_client.create_symlink(
            target=target, metadata=metadata, owner=owner, group=group
        )
        assert resp is not None
        assert resp["file_file_type"] == "SymLink"
        assert resp["owner"] == owner
        assert resp["group"] == group
        assert resp["file_creation_time"] is not None
        assert resp["file_last_write_time"] is not None
        assert resp["file_id"] is not None
        assert resp["file_parent_id"] is not None
        assert "file_attributes" not in resp
        assert "file_permission_key" not in resp

        resp = await symbolic_link_file_client.get_symlink()
        assert resp is not None
        assert resp["etag"] is not None
        assert resp["last_modified"] is not None
        assert unquote(resp["link_text"]) == target

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_and_get_symlink_error(self, **kwargs):
        premium_storage_file_account_name = kwargs.pop("premium_storage_file_account_name")

        await self._setup(premium_storage_file_account_name)

        share_client = self.fsc.get_share_client(self.share_name)
        directory_name = self._get_directory_name()
        directory_client = share_client.get_directory_client(directory_name)
        source_file_name = self._get_file_name("file1")
        symbolic_link_file_name = self._get_file_name("file2")
        symbolic_link_file_client = directory_client.get_file_client(symbolic_link_file_name)
        target = f"{directory_name}/{source_file_name}"

        with pytest.raises(ResourceNotFoundError) as e:
            await symbolic_link_file_client.create_symlink(target=target)
        assert "ParentNotFound" in e.value.args[0]

        with pytest.raises(ResourceNotFoundError) as e:
            await symbolic_link_file_client.get_symlink()
        assert "ParentNotFound" in e.value.args[0]

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_list_directories_and_files(self, **kwargs: Any):
        premium_storage_file_account_name = kwargs.pop("premium_storage_file_account_name")
        premium_storage_file_account_key = kwargs.pop("premium_storage_file_account_key")

        await self._setup(premium_storage_file_account_name, premium_storage_file_account_key)

        share_client = self.fsc.get_share_client(self.share_name)
        directory_name = self._get_directory_name()
        owner, group, file_mode = "345", "123", "0644"
        directory_client = await share_client.create_directory(
            directory_name, owner=owner, group=group, file_mode="0755"
        )

        file_name = self._get_file_name("file1")
        file_client = directory_client.get_file_client(file_name)
        await file_client.create_file(size=1024, owner=owner, group=group, file_mode="0644")

        symlink_name = self._get_file_name("file2")
        symlink_client = directory_client.get_file_client(symlink_name)
        target = f"{directory_name}/{file_name}"
        await symlink_client.create_symlink(target=target, owner=owner, group=group)

        subdir_name = self._get_directory_name("subdir")
        await directory_client.create_subdirectory(subdir_name, owner=owner, group=group, file_mode="0755")

        # Act
        items = []
        async for item in directory_client.list_directories_and_files(
            include=["Timestamps", "Etag", "Permissions", "LinkCount", "NfsAttributes"],
            include_extended_info=True,
        ):
            items.append(item)
        items_by_name = {item.name: item for item in items}

        # Assert: file
        file_props = items_by_name[file_name]
        assert isinstance(file_props, FileProperties)
        assert file_props.owner == owner
        assert file_props.group == group
        assert file_props.file_mode == file_mode
        assert file_props.nfs_file_type == "Regular"
        assert file_props.link_count == 1
        assert file_props.file_attributes is None
        assert file_props.permission_key is None
        assert file_props.etag is not None

        # Assert: symbolic link
        symlink_props = items_by_name[symlink_name]
        assert isinstance(symlink_props, FileProperties)
        assert symlink_props.owner == owner
        assert symlink_props.group == group
        assert symlink_props.nfs_file_type == "SymLink"
        assert symlink_props.link_count == 1

        # Assert: directory
        dir_props = items_by_name[subdir_name]
        assert isinstance(dir_props, DirectoryProperties)
        assert dir_props.owner == owner
        assert dir_props.group == group
        assert dir_props.file_mode == "0755"
        assert dir_props.nfs_file_type == "Directory"
        assert dir_props.link_count is not None
        assert dir_props.file_attributes is None
        assert dir_props.permission_key is None

        assert len(items) == 3

    @FileSharePreparer()
    async def test_list_directories_and_files_special_types_mock(self):
        directory_client = ShareDirectoryClient(
            "https://fakeaccount.file.core.windows.net",
            share_name="share",
            directory_path="",
            credential="ZmFrZWtleWZha2VrZXlmYWtla2V5",
            transport=MockListTransport(LIST_FILES_AND_DIRECTORIES_NFS_XML),
        )

        items = []
        async for item in directory_client.list_directories_and_files():
            items.append(item)
        items_by_name = {item.name: item for item in items}
        assert len(items) == 7

        directory = items_by_name["subdir"]
        assert isinstance(directory, DirectoryProperties)
        assert directory.is_directory is True
        assert directory.owner == "0"
        assert directory.group == "0"
        assert directory.file_mode == "0755"
        assert directory.link_count == 2
        assert directory.nfs_file_type == "Directory"

        regular = items_by_name["regular.txt"]
        assert isinstance(regular, FileProperties)
        assert regular.is_directory is False
        assert regular.size == 80
        assert regular.owner == "1000"
        assert regular.group == "1000"
        assert regular.file_mode == "0644"
        assert regular.link_count == 2
        assert regular.nfs_file_type == "Regular"

        symlink = items_by_name["symlink.txt"]
        assert isinstance(symlink, FileProperties)
        assert symlink.nfs_file_type == "SymLink"
        assert symlink.file_mode == "0777"
        assert symlink.link_count == 1
        assert symlink.link_text == "/mnt/s2/dir2/regular.txt"

        block_device = items_by_name["block_device"]
        assert isinstance(block_device, FileProperties)
        assert block_device.nfs_file_type == "BlockDevice"
        assert block_device.owner == "0"
        assert block_device.group == "0"
        assert block_device.file_mode == "0640"
        assert block_device.link_count == 1
        assert block_device.device_major == 8
        assert block_device.device_minor == 0

        char_device = items_by_name["char_device"]
        assert isinstance(char_device, FileProperties)
        assert char_device.nfs_file_type == "CharacterDevice"
        assert char_device.file_mode == "0644"
        assert char_device.device_major == 1
        assert char_device.device_minor == 7

        fifo = items_by_name["fifo_pipe"]
        assert isinstance(fifo, FileProperties)
        assert fifo.nfs_file_type == "Fifo"
        assert fifo.owner == "1000"
        assert fifo.group == "1000"
        assert fifo.file_mode == "0644"
        assert fifo.link_count == 1

        socket = items_by_name["unix_socket"]
        assert isinstance(socket, FileProperties)
        assert socket.nfs_file_type == "Socket"
        assert socket.file_mode == "0755"
        assert socket.link_count == 1
