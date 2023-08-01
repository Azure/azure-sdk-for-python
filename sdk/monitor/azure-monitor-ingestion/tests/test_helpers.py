# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import json
import random
import string
import zlib

import pytest

from azure.monitor.ingestion._helpers import (
    _create_gzip_requests,
    _split_chunks,
    MAX_CHUNK_SIZE_BYTES,
    GZIP_MAGIC_NUMBER
)


ALPHANUMERIC_CHARACTERS = string.ascii_letters + string.digits

random.seed(42) # For repeatibility


def _get_random_string(length: int):
    return ''.join(random.choice(ALPHANUMERIC_CHARACTERS) for _ in range(length))


class TestHelpers:

    @pytest.mark.parametrize("content", ["bar", "\uc548\ub155\ud558\uc138\uc694"])
    def test_split_chunks(self, content):
        obj = {"foo": content}
        logs = [obj] * 100

        entry_size = len(json.dumps(obj).encode("utf-8"))

        chunks = list(_split_chunks(logs, max_size_bytes=entry_size))
        assert len(chunks) == 100

        chunks = list(_split_chunks(logs, max_size_bytes=entry_size*2))
        assert len(chunks) == 50

        chunks = list(_split_chunks(logs, max_size_bytes=entry_size*100))
        assert len(chunks) == 1

    def test_split_chunks_larger_than_max(self):
        obj = {"foo": "some-long-string"}
        logs = [obj] * 3
        # If each entry in the log is greater than the max chunk size, then each entry should be its own chunk.
        chunks = list(_split_chunks(logs, max_size_bytes=10))
        assert len(chunks) == 3

    @pytest.mark.parametrize("num_entries", [100, 10000])
    def test_create_gzip_requests(self, num_entries):
        logs = [{_get_random_string(20): _get_random_string(500)} for _ in range(num_entries)]
        for compressed_bytes, raw_data in _create_gzip_requests(logs):
            assert len(compressed_bytes) < MAX_CHUNK_SIZE_BYTES
            assert compressed_bytes[:2] == GZIP_MAGIC_NUMBER
            assert zlib.decompress(compressed_bytes, 16+zlib.MAX_WBITS) == json.dumps(raw_data).encode("utf-8")
