# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import base64
import os
import unittest
import asyncio

import pytest
from azure.core.pipeline.transport import AioHttpTransport
from multidict import CIMultiDict, CIMultiDictProxy
from azure.core.exceptions import HttpResponseError

from azure.storage.file.aio import (
    FileClient,
    FileServiceClient,
    FileProperties
)
from filetestcase import (
    FileTestCase,
    TestMode,
    record,
)

# ------------------------------------------------------------------------------
TEST_FILE_PREFIX = 'file'
FILE_PATH = 'file_output.temp.dat'


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


class StorageGetFileTest(FileTestCase):
    def setUp(self):
        super(StorageGetFileTest, self).setUp()

        # test chunking functionality by reducing the threshold
        # for chunking and the size of each chunk, otherwise
        # the tests would take too long to execute
        self.MAX_SINGLE_GET_SIZE = 32 * 1024
        self.MAX_CHUNK_GET_SIZE = 4 * 1024

        url = self.get_file_url()
        credential = self.get_shared_key_credential()

        self.fsc = FileServiceClient(
            url, credential=credential,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE,
            transport=AiohttpTestTransport())

        self.share_name = self.get_resource_name('utshare')
        self.directory_name = self.get_resource_name('utdir')
        self.byte_file = self.get_resource_name('bytefile')
        self.byte_data = self.get_random_bytes(64 * 1024 + 5)


    def tearDown(self):
        if not self.is_playback():
            loop = asyncio.get_event_loop()
            try:
                loop.run_until_complete(self.fsc.delete_share(self.share_name, delete_snapshots='include'))
            except:
                pass

        if os.path.isfile(FILE_PATH):
            try:
                os.remove(FILE_PATH)
            except:
                pass

        return super(StorageGetFileTest, self).tearDown()

    # --Helpers-----------------------------------------------------------------

    def _get_file_reference(self):
        return self.get_resource_name(TEST_FILE_PREFIX)

    async def _setup(self):
        if not self.is_playback():
            try:
                share = await self.fsc.create_share(self.share_name)
                await share.create_directory(self.directory_name)
            except:
                pass
            byte_file = self.directory_name + '/' + self.byte_file
            file_client = FileClient(
                self.get_file_url(),
                share=self.share_name,
                file_path=byte_file,
                credential=self.get_shared_key_credential()
            )
            try:
                await file_client.upload_file(self.byte_data)
            except:
                pass

    class NonSeekableFile(object):
        def __init__(self, wrapped_file):
            self.wrapped_file = wrapped_file

        def write(self, data):
            self.wrapped_file.write(data)

        def read(self, count):
            return self.wrapped_file.read(count)
    
        def seekable(self):
            return False

    # -- Get test cases for files ----------------------------------------------

    async def _test_unicode_get_file_unicode_data_async(self):
        # Arrange
        await self._setup()
        file_data = u'hello world啊齄丂狛狜'.encode('utf-8')
        file_name = self._get_file_reference()
        file_client = FileClient(
                self.get_file_url(),
                share=self.share_name,
                file_path=self.directory_name + '/' + file_name,
                credential=self.settings.STORAGE_ACCOUNT_KEY,
                max_single_get_size=self.MAX_SINGLE_GET_SIZE,
                max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)
        await file_client.upload_file(file_data)

        # Act
        file_content = await file_client.download_file()
        file_content = await file_content.content_as_bytes()

        # Assert
        self.assertEqual(file_content, file_data)

    @record
    def test_unicode_get_file_unicode_data_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_unicode_get_file_unicode_data_async())

    async def _test_unicode_get_file_binary_data_async(self):
        # Arrange
        await self._setup()
        base64_data = 'AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/wABAgMEBQYHCAkKCwwNDg8QERITFBUWFxgZGhscHR4fICEiIyQlJicoKSorLC0uLzAxMjM0NTY3ODk6Ozw9Pj9AQUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVpbXF1eX2BhYmNkZWZnaGlqa2xtbm9wcXJzdHV2d3h5ent8fX5/gIGCg4SFhoeIiYqLjI2Oj5CRkpOUlZaXmJmam5ydnp+goaKjpKWmp6ipqqusra6vsLGys7S1tre4ubq7vL2+v8DBwsPExcbHyMnKy8zNzs/Q0dLT1NXW19jZ2tvc3d7f4OHi4+Tl5ufo6err7O3u7/Dx8vP09fb3+Pn6+/z9/v8AAQIDBAUGBwgJCgsMDQ4PEBESExQVFhcYGRobHB0eHyAhIiMkJSYnKCkqKywtLi8wMTIzNDU2Nzg5Ojs8PT4/QEFCQ0RFRkdISUpLTE1OT1BRUlNUVVZXWFlaW1xdXl9gYWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXp7fH1+f4CBgoOEhYaHiImKi4yNjo+QkZKTlJWWl5iZmpucnZ6foKGio6SlpqeoqaqrrK2ur7CxsrO0tba3uLm6u7y9vr/AwcLDxMXGx8jJysvMzc7P0NHS09TV1tfY2drb3N3e3+Dh4uPk5ebn6Onq6+zt7u/w8fLz9PX29/j5+vv8/f7/AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/w=='
        binary_data = base64.b64decode(base64_data)

        file_name = self._get_file_reference()
        file_client = FileClient(
                self.get_file_url(),
                share=self.share_name,
                file_path=self.directory_name + '/' + file_name,
                credential=self.settings.STORAGE_ACCOUNT_KEY,
                max_single_get_size=self.MAX_SINGLE_GET_SIZE,
                max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)
        await file_client.upload_file(binary_data)

        # Act
        file_content = await file_client.download_file()
        file_content = await file_content.content_as_bytes()

        # Assert
        self.assertEqual(file_content, binary_data)

    @record
    def test_unicode_get_file_binary_data_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_unicode_get_file_binary_data_async())

    async def _test_get_file_no_content_async(self):
        # Arrange
        await self._setup()
        file_data = b''
        file_name = self._get_file_reference()
        file_client = FileClient(
                self.get_file_url(),
                share=self.share_name,
                file_path=self.directory_name + '/' + file_name,
                credential=self.settings.STORAGE_ACCOUNT_KEY,
                max_single_get_size=self.MAX_SINGLE_GET_SIZE,
                max_chunk_get_size=self.MAX_CHUNK_GET_SIZE,
                transport=AiohttpTestTransport())
        await file_client.upload_file(file_data)

        # Act
        file_output = await file_client.download_file()
        file_content = await file_output.content_as_bytes()

        # Assert
        self.assertEqual(file_data, file_content)
        self.assertEqual(0, file_output.properties.size)

    @record
    def test_get_file_no_content_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_file_no_content_async())

    async def _test_get_file_to_bytes_async(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        await self._setup()
        file_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=self.settings.STORAGE_ACCOUNT_KEY,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        file_output = await file_client.download_file()
        file_content = await file_output.content_as_bytes(max_concurrency=2)

        # Assert
        self.assertEqual(self.byte_data, file_content)

    @record
    def test_get_file_to_bytes_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_file_to_bytes_async())

    async def _test_get_file_to_bytes_with_progress_async(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        await self._setup()
        file_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=self.settings.STORAGE_ACCOUNT_KEY,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        progress = []
        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        # Act
        file_output = await file_client.download_file(raw_response_hook=callback)
        file_content = await file_output.content_as_bytes(max_concurrency=2)

        # Assert
        self.assertEqual(self.byte_data, file_content)
        self.assert_download_progress(
            len(self.byte_data),
            self.MAX_CHUNK_GET_SIZE,
            self.MAX_SINGLE_GET_SIZE,
            progress)

    @record
    def test_get_file_to_bytes_with_progress_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_file_to_bytes_with_progress_async())

    async def _test_get_file_to_bytes_non_parallel_async(self):
        # Arrange
        await self._setup()
        file_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=self.settings.STORAGE_ACCOUNT_KEY,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        progress = []
        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        # Act
        file_output = await file_client.download_file(raw_response_hook=callback)
        file_content = await file_output.content_as_bytes()

        # Assert
        self.assertEqual(self.byte_data, file_content)
        self.assert_download_progress(
            len(self.byte_data),
            self.MAX_CHUNK_GET_SIZE,
            self.MAX_SINGLE_GET_SIZE,
            progress)

    @record
    def test_get_file_to_bytes_non_parallel_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_file_to_bytes_non_parallel_async())

    async def _test_get_file_to_bytes_small_async(self):
        # Arrange
        await self._setup()
        file_data = self.get_random_bytes(1024)
        file_name = self._get_file_reference()
        file_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + file_name,
            credential=self.settings.STORAGE_ACCOUNT_KEY,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)
        await file_client.upload_file(file_data)

        progress = []
        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        # Act
        file_output = await file_client.download_file(raw_response_hook=callback)
        file_content = await file_output.content_as_bytes()

        # Assert
        self.assertEqual(file_data, file_content)
        self.assert_download_progress(
            len(file_data),
            self.MAX_CHUNK_GET_SIZE,
            self.MAX_SINGLE_GET_SIZE,
            progress)

    @record
    def test_get_file_to_bytes_small_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_file_to_bytes_small_async())

    async def _test_get_file_to_stream_async(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        await self._setup()
        file_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=self.settings.STORAGE_ACCOUNT_KEY,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        with open(FILE_PATH, 'wb') as stream:
            props = await file_client.download_file()
            props = await props.download_to_stream(stream, max_concurrency=2)

        # Assert
        self.assertIsInstance(props, FileProperties)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data, actual)

    @record
    def test_get_file_to_stream_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_file_to_stream_async())

    async def _test_get_file_with_iter_async(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        await self._setup()
        file_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=self.settings.STORAGE_ACCOUNT_KEY,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        with open(FILE_PATH, 'wb') as stream:
            download = await file_client.download_file()
            async for data in download:
                stream.write(data)
        # Assert
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data, actual)

    @record
    def test_get_file_with_iter_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_file_with_iter_async())

    async def _test_get_file_to_stream_with_progress_async(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        await self._setup()
        file_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=self.settings.STORAGE_ACCOUNT_KEY,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        progress = []
        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        # Act
        with open(FILE_PATH, 'wb') as stream:
            props = await file_client.download_file(raw_response_hook=callback)
            props = await props.download_to_stream(stream, max_concurrency=2)

        # Assert
        self.assertIsInstance(props, FileProperties)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data, actual)
        self.assert_download_progress(
            len(self.byte_data),
            self.MAX_CHUNK_GET_SIZE,
            self.MAX_SINGLE_GET_SIZE,
            progress)

    @record
    def test_get_file_to_stream_with_progress_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_file_to_stream_with_progress_async())

    async def _test_get_file_to_stream_non_parallel_async(self):
        # Arrange
        await self._setup()
        file_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=self.settings.STORAGE_ACCOUNT_KEY,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        progress = []
        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        # Act
        with open(FILE_PATH, 'wb') as stream:
            props = await file_client.download_file(raw_response_hook=callback)
            props = await props.download_to_stream(stream, max_concurrency=1)

        # Assert
        self.assertIsInstance(props, FileProperties)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data, actual)
        self.assert_download_progress(
            len(self.byte_data),
            self.MAX_CHUNK_GET_SIZE,
            self.MAX_SINGLE_GET_SIZE,
            progress)

    @record
    def test_get_file_to_stream_non_parallel_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_file_to_stream_non_parallel_async())

    async def _test_get_file_to_stream_small_async(self):
        # Arrange
        await self._setup()
        file_data = self.get_random_bytes(1024)
        file_name = self._get_file_reference()
        file_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + file_name,
            credential=self.settings.STORAGE_ACCOUNT_KEY,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)
        await file_client.upload_file(file_data)

        progress = []
        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        # Act
        with open(FILE_PATH, 'wb') as stream:
            props = await file_client.download_file(raw_response_hook=callback)
            props = await props.download_to_stream(stream, max_concurrency=1)

        # Assert
        self.assertIsInstance(props, FileProperties)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(file_data, actual)
        self.assert_download_progress(
            len(file_data),
            self.MAX_CHUNK_GET_SIZE,
            self.MAX_SINGLE_GET_SIZE,
            progress)

    @record
    def test_get_file_to_stream_small_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_file_to_stream_small_async())

    async def _test_get_file_to_stream_from_snapshot_async(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        await self._setup()
        # Create a snapshot of the share and delete the file
        share_client = self.fsc.get_share_client(self.share_name)
        share_snapshot = await share_client.create_snapshot()
        file_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=self.settings.STORAGE_ACCOUNT_KEY)
        await file_client.delete_file()

        snapshot_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            snapshot=share_snapshot,
            credential=self.settings.STORAGE_ACCOUNT_KEY,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        with open(FILE_PATH, 'wb') as stream:
            props = await snapshot_client.download_file()
            props = await props.download_to_stream(stream, max_concurrency=2)

        # Assert
        self.assertIsInstance(props, FileProperties)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data, actual)

    @record
    def test_get_file_to_stream_from_snapshot_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_file_to_stream_from_snapshot_async())

    async def _test_get_file_to_stream_with_progress_from_snapshot_async(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        await self._setup()
        # Create a snapshot of the share and delete the file
        share_client = self.fsc.get_share_client(self.share_name)
        share_snapshot = await share_client.create_snapshot()
        file_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=self.settings.STORAGE_ACCOUNT_KEY)
        await file_client.delete_file()

        snapshot_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            snapshot=share_snapshot,
            credential=self.settings.STORAGE_ACCOUNT_KEY,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        progress = []
        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        # Act
        with open(FILE_PATH, 'wb') as stream:
            props = await snapshot_client.download_file(raw_response_hook=callback)
            props = await props.download_to_stream(stream, max_concurrency=2)

        # Assert
        self.assertIsInstance(props, FileProperties)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data, actual)
        self.assert_download_progress(
            len(self.byte_data),
            self.MAX_CHUNK_GET_SIZE,
            self.MAX_SINGLE_GET_SIZE,
            progress)

    @record
    def test_get_file_to_stream_with_progress_from_snapshot_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_file_to_stream_with_progress_from_snapshot_async())

    async def _test_get_file_to_stream_non_parallel_from_snapshot_async(self):
        # Arrange
        await self._setup()
        # Create a snapshot of the share and delete the file
        share_client = self.fsc.get_share_client(self.share_name)
        share_snapshot = await share_client.create_snapshot()
        file_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=self.settings.STORAGE_ACCOUNT_KEY)
        await file_client.delete_file()

        snapshot_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            snapshot=share_snapshot,
            credential=self.settings.STORAGE_ACCOUNT_KEY,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        progress = []
        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        # Act
        with open(FILE_PATH, 'wb') as stream:
            props = await snapshot_client.download_file(raw_response_hook=callback)
            props = await props.download_to_stream(stream, max_concurrency=1)

        # Assert
        self.assertIsInstance(props, FileProperties)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data, actual)
        self.assert_download_progress(
            len(self.byte_data),
            self.MAX_CHUNK_GET_SIZE,
            self.MAX_SINGLE_GET_SIZE,
            progress)

    @record
    def test_get_file_to_stream_non_parallel_from_snapshot_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_file_to_stream_non_parallel_from_snapshot_async())

    async def _test_get_file_to_stream_small_from_snapshot_async(self):
        # Arrange
        await self._setup()
        file_data = self.get_random_bytes(1024)
        file_name = self._get_file_reference()
        file_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + file_name,
            credential=self.settings.STORAGE_ACCOUNT_KEY)
        await file_client.upload_file(file_data)

        # Create a snapshot of the share and delete the file
        share_client = self.fsc.get_share_client(self.share_name)
        share_snapshot = await share_client.create_snapshot()
        await file_client.delete_file()

        snapshot_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + file_name,
            snapshot=share_snapshot,
            credential=self.settings.STORAGE_ACCOUNT_KEY,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        progress = []
        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        # Act
        with open(FILE_PATH, 'wb') as stream:
            props = await snapshot_client.download_file(raw_response_hook=callback)
            props = await props.download_to_stream(stream, max_concurrency=1)

        # Assert
        self.assertIsInstance(props, FileProperties)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(file_data, actual)
        self.assert_download_progress(
            len(file_data),
            self.MAX_CHUNK_GET_SIZE,
            self.MAX_SINGLE_GET_SIZE,
            progress)

    @record
    def test_get_file_to_stream_small_from_snapshot_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_file_to_stream_small_from_snapshot_async())

    async def _test_ranged_get_file_to_path_async(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        await self._setup()
        file_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=self.settings.STORAGE_ACCOUNT_KEY,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        end_range = self.MAX_SINGLE_GET_SIZE + 1024
        with open(FILE_PATH, 'wb') as stream:
            props = await file_client.download_file(offset=1, length=end_range)
            props = await props.download_to_stream(stream, max_concurrency=2)

        # Assert
        self.assertIsInstance(props, FileProperties)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data[1:end_range + 1], actual)

    @record
    def test_ranged_get_file_to_path_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_ranged_get_file_to_path_async())

    async def _test_ranged_get_file_to_path_with_single_byte_async(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        await self._setup()
        file_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=self.settings.STORAGE_ACCOUNT_KEY,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        end_range = self.MAX_SINGLE_GET_SIZE + 1024
        with open(FILE_PATH, 'wb') as stream:
            props = await file_client.download_file(offset=0, length=0)
            props = await props.download_to_stream(stream)

        # Assert
        self.assertIsInstance(props, FileProperties)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(1, len(actual))
            self.assertEqual(self.byte_data[0], actual[0])

    @record
    def test_ranged_get_file_to_path_with_single_byte_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_ranged_get_file_to_path_with_single_byte_async())

    async def _test_ranged_get_file_to_bytes_with_zero_byte_async(self):
        # Arrange
        await self._setup()
        file_data = b''
        file_name = self._get_file_reference()
        file_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + file_name,
            credential=self.settings.STORAGE_ACCOUNT_KEY,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE,
            transport=AiohttpTestTransport())
        await file_client.upload_file(file_data)

        # Act
        # the get request should fail in this case since the blob is empty and yet there is a range specified
        with self.assertRaises(HttpResponseError):
            props = await file_client.download_file(offset=0, length=5)
            await props.content_as_bytes()

        with self.assertRaises(HttpResponseError):
            props = await file_client.download_file(offset=3, length=5)
            await props.content_as_bytes()

    @record
    def test_ranged_get_file_to_bytes_with_zero_byte_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_ranged_get_file_to_bytes_with_zero_byte_async())

    async def _test_ranged_get_file_to_path_with_progress_async(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        await self._setup()
        file_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=self.settings.STORAGE_ACCOUNT_KEY,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        progress = []
        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        # Act
        start_range = 3
        end_range = self.MAX_SINGLE_GET_SIZE + 1024
        with open(FILE_PATH, 'wb') as stream:
            props = await file_client.download_file(offset=start_range, length=end_range, raw_response_hook=callback)
            props = await props.download_to_stream(stream, max_concurrency=2)

        # Assert
        self.assertIsInstance(props, FileProperties)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data[start_range:end_range + 1], actual)
        self.assert_download_progress(
            end_range - start_range + 1,
            self.MAX_CHUNK_GET_SIZE,
            self.MAX_SINGLE_GET_SIZE,
            progress)

    @record
    def test_ranged_get_file_to_path_with_progress_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_ranged_get_file_to_path_with_progress_async())

    async def _test_ranged_get_file_to_path_small_async(self):
        # Arrange
        await self._setup()
        file_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=self.settings.STORAGE_ACCOUNT_KEY,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        with open(FILE_PATH, 'wb') as stream:
            props = await file_client.download_file(offset=1, length=4)
            props = await props.download_to_stream(stream, max_concurrency=1)

        # Assert
        self.assertIsInstance(props, FileProperties)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data[1:5], actual)

    @record
    def test_ranged_get_file_to_path_small_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_ranged_get_file_to_path_small_async())

    async def _test_ranged_get_file_to_path_non_parallel_async(self):
        # Arrange
        await self._setup()
        file_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=self.settings.STORAGE_ACCOUNT_KEY,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        with open(FILE_PATH, 'wb') as stream:
            props = await file_client.download_file(offset=1, length=3)
            props = await props.download_to_stream(stream, max_concurrency=1)

        # Assert
        self.assertIsInstance(props, FileProperties)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data[1:4], actual)

    @record
    def test_ranged_get_file_to_path_non_parallel_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_ranged_get_file_to_path_non_parallel_async())

    async def _test_ranged_get_file_to_path_invalid_range_parallel_async(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        await self._setup()
        file_size = self.MAX_SINGLE_GET_SIZE + 1
        file_data = self.get_random_bytes(file_size)
        file_name = self._get_file_reference()
        file_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + file_name,
            credential=self.settings.STORAGE_ACCOUNT_KEY,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)
        await file_client.upload_file(file_data)

        # Act
        end_range = 2 * self.MAX_SINGLE_GET_SIZE
        with open(FILE_PATH, 'wb') as stream:
            props = await file_client.download_file(offset=1, length=end_range)
            props = await props.download_to_stream(stream, max_concurrency=2)

        # Assert
        self.assertIsInstance(props, FileProperties)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(file_data[1:file_size], actual)

    @record
    def test_ranged_get_file_to_path_invalid_range_parallel_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_ranged_get_file_to_path_invalid_range_parallel_async())

    async def _test_ranged_get_file_to_path_invalid_range_non_parallel_async(self):

        # Arrange
        await self._setup()
        file_size = 1024
        file_data = self.get_random_bytes(file_size)
        file_name = self._get_file_reference()
        file_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + file_name,
            credential=self.settings.STORAGE_ACCOUNT_KEY,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)
        await file_client.upload_file(file_data)

        # Act
        end_range = 2 * self.MAX_SINGLE_GET_SIZE
        with open(FILE_PATH, 'wb') as stream:
            props = await file_client.download_file(offset=1, length=end_range)
            props = await props.download_to_stream(stream, max_concurrency=1)

        # Assert
        self.assertIsInstance(props, FileProperties)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(file_data[1:file_size], actual)

    @record
    def test_ranged_get_file_to_path_invalid_range_non_parallel_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_ranged_get_file_to_path_invalid_range_non_parallel_async())

    async def _test_get_file_to_text_async(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        await self._setup()
        text_file = self.get_resource_name('textfile')
        text_data = self.get_random_text_data(self.MAX_SINGLE_GET_SIZE + 1)
        file_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + text_file,
            credential=self.settings.STORAGE_ACCOUNT_KEY,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)
        await file_client.upload_file(text_data)

        # Act
        file_content = await file_client.download_file()
        file_content = await file_content.content_as_text(max_concurrency=2)

        # Assert
        self.assertEqual(text_data, file_content)

    @record
    def test_get_file_to_text_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_file_to_text_async())

    async def _test_get_file_to_text_with_progress_async(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        await self._setup()
        text_file = self.get_resource_name('textfile')
        text_data = self.get_random_text_data(self.MAX_SINGLE_GET_SIZE + 1)
        file_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + text_file,
            credential=self.settings.STORAGE_ACCOUNT_KEY,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)
        await file_client.upload_file(text_data)

        progress = []
        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        # Act
        file_content = await file_client.download_file(raw_response_hook=callback)
        file_content = await file_content.content_as_text(max_concurrency=2)

        # Assert
        self.assertEqual(text_data, file_content)
        self.assert_download_progress(
            len(text_data.encode('utf-8')),
            self.MAX_CHUNK_GET_SIZE,
            self.MAX_SINGLE_GET_SIZE,
            progress)

    @record
    def test_get_file_to_text_with_progress_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_file_to_text_with_progress_async())

    async def _test_get_file_to_text_non_parallel_async(self):
        # Arrange
        await self._setup()
        text_file = self._get_file_reference()
        text_data = self.get_random_text_data(self.MAX_SINGLE_GET_SIZE + 1)
        file_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + text_file,
            credential=self.settings.STORAGE_ACCOUNT_KEY,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)
        await file_client.upload_file(text_data)

        progress = []
        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        # Act
        file_content = await file_client.download_file(raw_response_hook=callback)
        file_content = await file_content.content_as_text(max_concurrency=1)

        # Assert
        self.assertEqual(text_data, file_content)
        self.assert_download_progress(
            len(text_data),
            self.MAX_CHUNK_GET_SIZE,
            self.MAX_SINGLE_GET_SIZE,
            progress)

    @record
    def test_get_file_to_text_non_parallel_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_file_to_text_non_parallel_async())

    async def _test_get_file_to_text_small_async(self):
        # Arrange
        await self._setup()
        file_data = self.get_random_text_data(1024)
        file_name = self._get_file_reference()
        file_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + file_name,
            credential=self.settings.STORAGE_ACCOUNT_KEY,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)
        await file_client.upload_file(file_data)

        progress = []
        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        # Act
        file_content = await file_client.download_file(raw_response_hook=callback)
        file_content = await file_content.content_as_text()

        # Assert
        self.assertEqual(file_data, file_content)
        self.assert_download_progress(
            len(file_data),
            self.MAX_CHUNK_GET_SIZE,
            self.MAX_SINGLE_GET_SIZE,
            progress)

    @record
    def test_get_file_to_text_small_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_file_to_text_small_async())

    async def _test_get_file_to_text_with_encoding_async(self):
        # Arrange
        await self._setup()
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-16')
        file_name = self._get_file_reference()
        file_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + file_name,
            credential=self.settings.STORAGE_ACCOUNT_KEY,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)
        await file_client.upload_file(data)

        # Act
        file_content = await file_client.download_file()
        file_content = await file_content.content_as_text(encoding='UTF-16')

        # Assert
        self.assertEqual(text, file_content)

    @record
    def test_get_file_to_text_with_encoding_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_file_to_text_with_encoding_async())

    async def _test_get_file_to_text_with_encoding_and_progress_async(self):
        # Arrange
        await self._setup()
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-16')
        file_name = self._get_file_reference()
        file_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + file_name,
            credential=self.settings.STORAGE_ACCOUNT_KEY,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)
        await file_client.upload_file(data)

        # Act
        progress = []
        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        file_content = await file_client.download_file(raw_response_hook=callback)
        file_content = await file_content.content_as_text(encoding='UTF-16')

        # Assert
        self.assertEqual(text, file_content)
        self.assert_download_progress(
            len(data),
            self.MAX_CHUNK_GET_SIZE,
            self.MAX_SINGLE_GET_SIZE,
            progress)

    @record
    def test_get_file_to_text_with_encoding_and_progress_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_file_to_text_with_encoding_and_progress_async())

    async def _test_get_file_non_seekable_async(self):
        # Arrange
        await self._setup()
        file_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=self.settings.STORAGE_ACCOUNT_KEY,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        with open(FILE_PATH, 'wb') as stream:
            non_seekable_stream = StorageGetFileTest.NonSeekableFile(stream)
            file_props = await file_client.download_file()
            file_props = await file_props.download_to_stream(non_seekable_stream, max_concurrency=1)

        # Assert
        self.assertIsInstance(file_props, FileProperties)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data, actual)

    @record
    def test_get_file_non_seekable_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_file_non_seekable_async())

    async def _test_get_file_non_seekable_parallel_async(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        await self._setup()
        file_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=self.settings.STORAGE_ACCOUNT_KEY,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        with open(FILE_PATH, 'wb') as stream:
            non_seekable_stream = StorageGetFileTest.NonSeekableFile(stream)

            with self.assertRaises(ValueError):
                data = await file_client.download_file()
                await data.download_to_stream(non_seekable_stream, max_concurrency=2)

                # Assert

    @record
    def test_get_file_non_seekable_parallel_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_file_non_seekable_parallel_async())

    async def _test_get_file_non_seekable_from_snapshot_async(self):
        # Arrange
        await self._setup()
        # Create a snapshot of the share and delete the file
        share_client = self.fsc.get_share_client(self.share_name)
        share_snapshot = await share_client.create_snapshot()
        file_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=self.settings.STORAGE_ACCOUNT_KEY)
        await file_client.delete_file()

        snapshot_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            snapshot=share_snapshot,
            credential=self.settings.STORAGE_ACCOUNT_KEY,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        with open(FILE_PATH, 'wb') as stream:
            non_seekable_stream = StorageGetFileTest.NonSeekableFile(stream)
            file_props = await snapshot_client.download_file()
            file_props = await file_props.download_to_stream(non_seekable_stream, max_concurrency=1)

        # Assert
        self.assertIsInstance(file_props, FileProperties)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data, actual)

    @record
    def test_get_file_non_seekable_from_snapshot_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_file_non_seekable_from_snapshot_async())

    async def _test_get_file_non_seekable_parallel_from_snapshot_async(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        await self._setup()
        # Create a snapshot of the share and delete the file
        share_client = self.fsc.get_share_client(self.share_name)
        share_snapshot = await share_client.create_snapshot()
        file_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=self.settings.STORAGE_ACCOUNT_KEY)
        await file_client.delete_file()

        snapshot_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            snapshot=share_snapshot,
            credential=self.settings.STORAGE_ACCOUNT_KEY,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        with open(FILE_PATH, 'wb') as stream:
            non_seekable_stream = StorageGetFileTest.NonSeekableFile(stream)

            with self.assertRaises(ValueError):
                data = await snapshot_client.download_file()
                await data.download_to_stream(non_seekable_stream, max_concurrency=2)

    @record
    def test_get_file_non_seekable_parallel_from_snapshot_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_file_non_seekable_parallel_from_snapshot_async())

    async def _test_get_file_exact_get_size_async(self):
        # Arrange
        await self._setup()
        file_name = self._get_file_reference()
        byte_data = self.get_random_bytes(self.MAX_SINGLE_GET_SIZE)
        file_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + file_name,
            credential=self.settings.STORAGE_ACCOUNT_KEY,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)
        await file_client.upload_file(byte_data)

        progress = []
        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        # Act
        file_content = await file_client.download_file(raw_response_hook=callback)
        file_bytes = await file_content.content_as_bytes()

        # Assert
        self.assertEqual(byte_data, file_bytes)
        self.assert_download_progress(
            len(byte_data),
            self.MAX_CHUNK_GET_SIZE,
            self.MAX_SINGLE_GET_SIZE,
            progress)

    @record
    def test_get_file_exact_get_size_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_file_exact_get_size_async())

    async def _test_get_file_exact_chunk_size_async(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        await self._setup()
        file_name = self._get_file_reference()
        byte_data = self.get_random_bytes(self.MAX_SINGLE_GET_SIZE + self.MAX_CHUNK_GET_SIZE)
        file_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + file_name,
            credential=self.settings.STORAGE_ACCOUNT_KEY,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)
        await file_client.upload_file(byte_data)

        progress = []
        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        # Act
        file_content = await file_client.download_file(raw_response_hook=callback)
        file_bytes = await file_content.content_as_bytes(max_concurrency=2)

        # Assert
        self.assertEqual(byte_data, file_bytes)
        self.assert_download_progress(
            len(byte_data),
            self.MAX_CHUNK_GET_SIZE,
            self.MAX_SINGLE_GET_SIZE,
            progress)

    @record
    def test_get_file_exact_chunk_size_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_file_exact_chunk_size_async())

    async def _test_get_file_with_md5_async(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        await self._setup()
        file_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=self.settings.STORAGE_ACCOUNT_KEY,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        file_content = await file_client.download_file(validate_content=True)
        file_bytes = await file_content.content_as_bytes()

        # Assert
        self.assertEqual(self.byte_data, file_bytes)

    @record
    def test_get_file_with_md5_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_file_with_md5_async())

    async def _test_get_file_range_with_md5_async(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        await self._setup()
        file_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=self.settings.STORAGE_ACCOUNT_KEY,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        file_content = await file_client.download_file(offset=0, length=1024, validate_content=True)

        # Assert
        self.assertIsNone(file_content.properties.content_settings.content_md5)

        # Arrange
        props = await file_client.get_file_properties()
        props.content_settings.content_md5 = b'MDAwMDAwMDA='
        await file_client.set_http_headers(props.content_settings)

        # Act
        file_content = await file_client.download_file(offset=0, length=1024, validate_content=True)

        # Assert
        self.assertEqual(b'MDAwMDAwMDA=', file_content.properties.content_settings.content_md5)

    @record
    def test_get_file_range_with_md5_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_file_range_with_md5_async())

    async def _test_get_file_server_encryption_async(self):

        #Arrange
        await self._setup()
        file_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=self.settings.STORAGE_ACCOUNT_KEY,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        file_content = await file_client.download_file(offset=0, length=1024, validate_content=True)
    
        # Assert
        if self.is_file_encryption_enabled():
            self.assertTrue(file_content.properties.server_encrypted)
        else:
            self.assertFalse(file_content.properties.server_encrypted)

    @record
    def test_get_file_server_encryption_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_file_server_encryption_async())

    async def _test_get_file_properties_server_encryption_async(self):

        # Arrange
        await self._setup()
        file_client = FileClient(
            self.get_file_url(),
            share=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=self.settings.STORAGE_ACCOUNT_KEY,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        props = await file_client.get_file_properties()

        # Assert
        if self.is_file_encryption_enabled():
            self.assertTrue(props.server_encrypted)
        else:
            self.assertFalse(props.server_encrypted)

    @record
    def test_get_file_properties_server_encryption_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_file_properties_server_encryption_async())

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
