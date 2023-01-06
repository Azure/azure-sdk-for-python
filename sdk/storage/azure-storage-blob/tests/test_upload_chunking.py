# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import unittest
from io import BytesIO, SEEK_SET
from threading import Lock

from azure.storage.blob._shared.uploads import SubStream


class StorageBlobUploadChunkingTest(unittest.TestCase):

    # this is a white box test that's designed to make sure _Substream behaves properly
    # when the buffer needs to be swapped out at least once
    def test_sub_stream_with_length_larger_than_buffer(self, **kwargs):
        data = os.urandom(12 * 1024 * 1024)

        # assuming the max size of the buffer is 4MB, this test needs to be updated if that has changed
        # the block size is 6MB for this test
        expected_data = data[0: 6 * 1024 * 1024]
        wrapped_stream = BytesIO(data)  # simulate stream given by user
        lockObj = Lock()  # simulate multi-threaded environment
        substream = SubStream(wrapped_stream, stream_begin_index=0, length=6 * 1024 * 1024, lockObj=lockObj)

        try:
            # substream should start with position at 0
            assert substream.tell() == 0

            # reading a chunk that is smaller than the buffer
            data_chunk_1 = substream.read(2 * 1024 * 1024)
            assert len(data_chunk_1) == 2 * 1024 * 1024

            # reading a chunk that is bigger than the data remaining in buffer, force a buffer swap
            data_chunk_2 = substream.read(4 * 1024 * 1024)
            assert len(data_chunk_2) == 4 * 1024 * 1024

            # assert data is consistent
            assert data_chunk_1 + data_chunk_2 == expected_data
            assert 6 * 1024 * 1024 == substream.tell()

            # attempt to read more than what the sub stream contains should return nothing
            empty_data = substream.read(1 * 1024 * 1024)
            assert 0 == len(empty_data)
            assert 6 * 1024 * 1024 == substream.tell()

            # test seek outside of current buffer, which is at the moment the last 2MB of data
            substream.seek(0, SEEK_SET)
            data_chunk_1 = substream.read(4 * 1024 * 1024)
            data_chunk_2 = substream.read(2 * 1024 * 1024)

            # assert data is consistent
            assert data_chunk_1 + data_chunk_2 == expected_data

            # test seek inside of buffer, which is at the moment the last 2MB of data
            substream.seek(4 * 1024 * 1024, SEEK_SET)
            data_chunk_2 = substream.read(2 * 1024 * 1024)

            # assert data is consistent
            assert data_chunk_1 + data_chunk_2 == expected_data

        finally:
            wrapped_stream.close()
            substream.close()

    # this is a white box test that's designed to make sure _Substream behaves properly
    # when block size is smaller than 4MB, thus there's no need for buffer swap
    def test_sub_stream_with_length_equal_to_buffer(self, **kwargs):
        data = os.urandom(6 * 1024 * 1024)

        # assuming the max size of the buffer is 4MB, this test needs to be updated if that has changed
        # the block size is 2MB for this test
        expected_data = data[0: 2 * 1024 * 1024]
        wrapped_stream = BytesIO(expected_data)  # simulate stream given by user
        lockObj = Lock()  # simulate multi-threaded environment
        substream = SubStream(wrapped_stream, stream_begin_index=0, length=2 * 1024 * 1024, lockObj=lockObj)

        try:
            # substream should start with position at 0
            assert substream.tell() == 0

            # reading a chunk that is smaller than the buffer
            data_chunk_1 = substream.read(1 * 1024 * 1024)
            assert len(data_chunk_1) == 1 * 1024 * 1024

            # reading a chunk that is bigger than the buffer, should not read anything beyond
            data_chunk_2 = substream.read(4 * 1024 * 1024)
            assert len(data_chunk_2) == 1 * 1024 * 1024

            # assert data is consistent
            assert data_chunk_1 + data_chunk_2 == expected_data

            # test seek
            substream.seek(1 * 1024 * 1024, SEEK_SET)
            data_chunk_2 = substream.read(1 * 1024 * 1024)

            # assert data is consistent
            assert data_chunk_1 + data_chunk_2 == expected_data

        finally:
            wrapped_stream.close()
            substream.close()
