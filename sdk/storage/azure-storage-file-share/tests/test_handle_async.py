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
from filetestcase import (
    FileTestCase,
    record,
    TestMode,
)

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


class StorageHandleTest(FileTestCase):
    def setUp(self):
        super(StorageHandleTest, self).setUp()
        file_url = self.get_file_url()
        credentials = self.get_shared_key_credential()
        self.fsc = ShareServiceClient(account_url=file_url, credential=credentials, transport=AiohttpTestTransport())
        self.test_shares = []

    def tearDown(self):
        if not self.is_playback():
            loop = asyncio.get_event_loop()
            for share in self.test_shares:
                loop.run_until_complete(self.fsc.delete_share(share.share_name, delete_snapshots=True))
        return super(StorageHandleTest, self).tearDown()

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

    async def _test_close_single_handle_async(self):
        # don't run live, since the test set up was highly manual
        # only run when recording, or playing back in CI
        if not TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
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

    @record
    def test_close_single_handle_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_close_single_handle_async())

    async def _test_close_all_handle_async(self):
        # don't run live, since the test set up was highly manual
        # only run when recording, or playing back in CI
        if not TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
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

    @record
    def test_close_all_handle_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_close_all_handle_async())


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
