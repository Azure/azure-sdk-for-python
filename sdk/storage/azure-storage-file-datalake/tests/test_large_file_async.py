# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import asyncio
import platform
import re
import unittest
from io import BytesIO
from os import urandom

import pytest
from azure.core.exceptions import ResourceExistsError
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.storage.blob._shared.base_client import _format_shared_key_credential
from azure.storage.filedatalake.aio import DataLakeServiceClient

from devtools_testutils.storage.aio import AsyncStorageRecordedTestCase
from settings.testcase import DataLakePreparer

# ------------------------------------------------------------------------------
TEST_DIRECTORY_PREFIX = 'directory'
TEST_FILE_PREFIX = 'file'
FILE_PATH = 'file_output.temp.dat'
LARGEST_BLOCK_SIZE = 4000 * 1024 * 1024
# ------------------------------------------------------------------------------


class TestLargeFileAsync(AsyncStorageRecordedTestCase):
    async def _setUp(self, account_name, account_key):
        url = self.account_url(account_name, 'dfs')
        self.payload_dropping_policy = PayloadDroppingPolicy()
        credential_policy = _format_shared_key_credential(account_name, account_key)
        self.dsc = DataLakeServiceClient(url,
                                         credential=account_key,
                                         _additional_pipeline_policies=[self.payload_dropping_policy, credential_policy])

        self.config = self.dsc._config

        self.file_system_name = self.get_resource_name('filesystem')

        if not self.is_playback():
            file_system = self.dsc.get_file_system_client(self.file_system_name)
            try:
                await file_system.create_file_system(timeout=5)

            except ResourceExistsError:
                pass

    def tearDown(self):
        if not self.is_playback():
            try:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(self.dsc.delete_file_system(self.file_system_name))
                loop.run_until_complete(self.dsc.__aexit__())
            except:
                pass

        return super(TestLargeFileAsync, self).tearDown()

    # --Helpers-----------------------------------------------------------------
    def _get_directory_reference(self, prefix=TEST_DIRECTORY_PREFIX):
        directory_name = self.get_resource_name(prefix)
        return directory_name

    # --Helpers-----------------------------------------------------------------
    @pytest.mark.live_test_only
    @DataLakePreparer()
    async def test_append_large_stream_without_network(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()

        # Create a directory to put the file under that
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()

        file_client = directory_client.get_file_client('filename')
        await file_client.create_file()

        data = LargeStream(LARGEST_BLOCK_SIZE)

        # Act
        response = await file_client.append_data(data, 0, LARGEST_BLOCK_SIZE)

        assert response is not None
        assert self.payload_dropping_policy.append_counter == 1
        assert self.payload_dropping_policy.append_sizes[0] == LARGEST_BLOCK_SIZE

    @pytest.mark.skipif(platform.python_implementation() == "PyPy", reason="Test failing on Pypy3 Linux, skip to investigate")
    @pytest.mark.live_test_only
    @DataLakePreparer()
    async def test_upload_large_stream_without_network(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self.get_resource_name(TEST_DIRECTORY_PREFIX)

        # Create a directory to put the file under that
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()

        file_client = directory_client.get_file_client('filename')
        await file_client.create_file()

        length = 2*LARGEST_BLOCK_SIZE
        data = LargeStream(length)

        # Act
        response = await file_client.upload_data(data, length, overwrite=True, chunk_size=LARGEST_BLOCK_SIZE)

        assert response is not None
        assert self.payload_dropping_policy.append_counter == 2
        assert self.payload_dropping_policy.append_sizes[0] == LARGEST_BLOCK_SIZE
        assert self.payload_dropping_policy.append_sizes[1] == LARGEST_BLOCK_SIZE


class LargeStream(BytesIO):
    def __init__(self, length, initial_buffer_length=1024 * 1024):
        self._base_data = urandom(initial_buffer_length)
        self._base_data_length = initial_buffer_length
        self._position = 0
        self._remaining = length
        self._closed = False

    def read(self, size=None):
        if self._remaining == 0:
            return b""

        if size is None:
            e = self._base_data_length
        else:
            e = size
        e = min(e, self._remaining)
        if e > self._base_data_length:
            self._base_data = urandom(e)
            self._base_data_length = e
        self._remaining = self._remaining - e
        return self._base_data[:e]

    def remaining(self):
        return self._remaining

    def close(self):
        self._closed = True


class PayloadDroppingPolicy(SansIOHTTPPolicy):
    def __init__(self):
        self.append_counter = 0
        self.append_sizes = []
        self.dummy_body = "dummy_body"

    def on_request(self, request):  # type: (PipelineRequest) -> Union[None, Awaitable[None]]
        if _is_append_request(request):
            if request.http_request.body:
                position = self.append_counter*len(self.dummy_body)
                request.http_request.url = re.sub(r'position=\d+', "position=" + str(position), request.http_request.url)
                self.append_sizes.append(_get_body_length(request))
                replacement = self.dummy_body
                request.http_request.body = replacement
                request.http_request.headers["Content-Length"] = str(len(replacement))
                self.append_counter = self.append_counter + 1
        elif _is_flush_request(request):
            position = self.append_counter * len(self.dummy_body)
            request.http_request.url = re.sub(r'position=\d+', "position=" + str(position), request.http_request.url)


def _is_append_request(request):
    query = request.http_request.query
    return query and "action" in query and query["action"] == "append"


def _is_flush_request(request):
    query = request.http_request.query
    return query and "action" in query and query["action"] == "flush"


def _get_body_length(request):
    body = request.http_request.body
    length = 0
    if hasattr(body, "read"):
        chunk = body.read(10*1024*1024)
        while chunk:
            length = length + len(chunk)
            chunk = body.read(10 * 1024 * 1024)
    else:
        length = len(body)
    return length


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
