# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from io import BytesIO

import pytest
from azure.storage.fileshare.aio import ShareClient, ShareServiceClient

from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils.storage.aio import AsyncStorageRecordedTestCase, GenericTestProxyParametrize1
from settings.testcase import FileSharePreparer
from test_content_validation import assert_content_md5, assert_structured_message


class TestStorageContentValidationAsync(AsyncStorageRecordedTestCase):
    ssc: ShareServiceClient = None
    share_client: ShareClient = None

    async def _setup(self, account_name, account_key):
        credential = {"account_name": account_name, "account_key": account_key}
        self.ssc = ShareServiceClient(self.account_url(account_name, "file"), credential=credential, logging_enable=True)
        self.share_client = self.ssc.get_share_client(self.get_resource_name('utshare'))
        await self.share_client.create_share()

    async def _teardown(self):
        if self.share_client:
            try:
                await self.share_client.delete_share()
            except:
                pass

    def _get_file_reference(self):
        return self.get_resource_name('file')

    @FileSharePreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy_async
    async def test_upload_file(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        file = self.share_client.get_file_client(self._get_file_reference())
        data = b'abc' * 512
        assert_method = assert_structured_message if a == 'crc64' else assert_content_md5

        # Act
        await file.upload_file(data, validate_content=a, raw_request_hook=assert_method)

        # Assert
        content = await file.download_file()
        assert await content.readall() == data
        await self._teardown()

    @FileSharePreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy_async
    async def test_upload_file_chunks(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        self.share_client._config.max_range_size = 1024
        file = self.share_client.get_file_client(self._get_file_reference())
        data = b'abcde' * 512
        assert_method = assert_structured_message if a == 'crc64' else assert_content_md5

        # Act
        await file.upload_file(data, validate_content=a, raw_request_hook=assert_method)

        # Assert
        content = await file.download_file()
        assert await content.readall() == data
        await self._teardown()

    @FileSharePreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy_async
    async def test_upload_range(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        file = self.share_client.get_file_client(self._get_file_reference())
        data1 = b'abcde' * 512
        data2 = '你好世界' * 10
        encoded = data2.encode('utf-8')
        assert_method = assert_structured_message if a == 'crc64' else assert_content_md5

        # Act
        await file.create_file(len(data1) + len(encoded))
        await file.upload_range(data1, 0, len(data1), validate_content=a, raw_request_hook=assert_method)
        await file.upload_range(data2, len(data1), len(encoded), encoding='utf-8', validate_content=a, raw_request_hook=assert_method)

        # Assert
        content = await file.download_file()
        assert await content.readall() == data1 + encoded
        await self._teardown()

    @FileSharePreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy_async
    async def test_upload_range_data_types(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        file = self.share_client.get_file_client(self._get_file_reference())
        assert_method = assert_structured_message if a == 'crc64' else assert_content_md5

        data = b'abcd' * 1030  # 4 KiB + 24
        byte_io = BytesIO(data)

        def generator():
            for i in range(0, len(data), 500):
                yield data[i: i + 500]

        data_list = [byte_io, generator()]

        # Act
        offset = 0
        await file.create_file(len(data) * len(data_list))
        for j in data_list:
            await file.upload_range(j, offset, len(data), validate_content=a, raw_request_hook=assert_method)
            offset += len(data)

        # Assert
        content = await file.download_file()
        assert await content.readall() == data * len(data_list)
        await self._teardown()
