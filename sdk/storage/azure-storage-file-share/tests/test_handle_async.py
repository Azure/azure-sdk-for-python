# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import asyncio
import pytest

from azure.core.pipeline.transport import AioHttpTransport
from multidict import CIMultiDict, CIMultiDictProxy


from azure.storage.fileshare.aio import (
    ShareServiceClient,
)
from _shared.testcase import (
    LogCaptured,
    GlobalStorageAccountPreparer,
    GlobalResourceGroupPreparer
)
from _shared.asynctestcase import AsyncStorageTestCase

# ------------------------------------------------------------------------------
TEST_SHARE_NAME = 'test'
TEST_SHARE_PREFIX = 'share'


# ------------------------------------------------------------------------------
class AiohttpTestTransport(AioHttpTransport):
    """Workaround to vcrpy bug: https://github.com/kevin1024/vcrpy/pull/461
    """
    async def send(self, request, **config):
        response = await super(AiohttpTestTransport, self).send(request, **config)
        if not isinstance(response.headers, CIMultiDictProxy):
            response.headers = CIMultiDictProxy(CIMultiDict(response.internal_response.headers))
            response.content_type = response.headers.get("content-type")
        return response


class StorageHandleTest(AsyncStorageTestCase):
    def _setup(self, storage_account, storage_account_key):
        file_url = self.account_url(storage_account, "file")
        credentials = storage_account_key
        self.fsc = ShareServiceClient(account_url=file_url, credential=credentials, transport=AiohttpTestTransport())
        self.test_shares = []

    # --Helpers-----------------------------------------------------------------

    def _validate_handles(self, handles):
        # Assert
        self.assertIsNotNone(handles)
        self.assertGreaterEqual(len(handles), 1)
        self.assertIsNotNone(handles[0])

        # verify basic fields
        # path may or may not be present
        # last_connect_time_string has been missing in the test
        self.assertIsNotNone(handles[0].id)
        self.assertIsNotNone(handles[0].file_id)
        self.assertIsNotNone(handles[0].parent_id)
        self.assertIsNotNone(handles[0].session_id)
        self.assertIsNotNone(handles[0].client_ip)
        self.assertIsNotNone(handles[0].open_time)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_close_single_handle_async(self, resource_group, location, storage_account, storage_account_key):
        pytest.skip("investigate later")
        # don't run live, since the test set up was highly manual
        # only run when recording, or playing back in CI
        if self.is_live:
            pytest.skip("Cannot run in live without manual setup")

        self._setup(storage_account, storage_account_key)
        share = self.fsc.get_share_client(TEST_SHARE_NAME)
        root = share.get_directory_client()
        handles = []
        async for handle in root.list_handles(recursive=True):
            handles.append(handle)
        self._validate_handles(handles)

        # Act
        with self.assertRaises(ValueError):
            await root.close_handle('*')

        handles_info = await root.close_handle(handles[0])

        # Assert 1 handle has been closed
        self.assertEqual(1, handles_info['closed_handles_count'])
        self.assertEqual(handles_info['failed_handles_count'], 0)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_close_all_handle_async(self, resource_group, location, storage_account, storage_account_key):
        pytest.skip("investigate later")
        # don't run live, since the test set up was highly manual
        # only run when recording, or playing back in CI
        if self.is_live:
            pytest.skip("Cannot run in live without manual setup")

        self._setup(storage_account, storage_account_key)
        share = self.fsc.get_share_client(TEST_SHARE_NAME)
        root = share.get_directory_client()
        handles = []
        async for handle in root.list_handles(recursive=True):
            handles.append(handle)
        self._validate_handles(handles)

        # Act
        handles_info = await root.close_all_handles(recursive=True)

        # Assert at least 1 handle has been closed
        self.assertTrue(handles_info['closed_handles_count'] > 1)
        self.assertEqual(handles_info['failed_handles_count'], 0)

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
