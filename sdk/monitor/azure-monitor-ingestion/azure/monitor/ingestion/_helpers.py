# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json
import logging
import sys
from typing import Any, Generator, List, Tuple
import zlib

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore  # pylint: disable=ungrouped-imports


_LOGGER = logging.getLogger(__name__)
JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object

MAX_CHUNK_SIZE_BYTES = 1024 * 1024 # 1 MiB
CHAR_SIZE_BYTES = 4
GZIP_MAGIC_NUMBER = b"\x1f\x8b"


def _split_chunks(logs: List[JSON]) -> Generator[List[JSON], None, None]:
    chunk_size = 0
    curr_chunk = []
    for log in logs:
        # each char is 4 bytes
        size = len(json.dumps(log)) * CHAR_SIZE_BYTES
        if chunk_size + size <= MAX_CHUNK_SIZE_BYTES:
            curr_chunk.append(log)
            chunk_size += size
        else:
            _LOGGER.debug('Yielding chunk with size: %d', chunk_size)
            yield curr_chunk
            curr_chunk = [log]
            chunk_size = size
    if len(curr_chunk) > 0:
        _LOGGER.debug('Yielding chunk with size: %d', chunk_size)
        yield curr_chunk


def _create_gzip_requests(logs: List[JSON]) -> Generator[Tuple[bytes, List[JSON]], None, None]:
    for chunk in _split_chunks(logs):
        zlib_mode = 16 + zlib.MAX_WBITS  # for gzip encoding
        _compress = zlib.compressobj(wbits=zlib_mode)
        data = _compress.compress(bytes(json.dumps(chunk), encoding="utf-8"))
        data += _compress.flush()
        _LOGGER.debug('Yielding gzip compressed data, Length: %d', len(data))
        yield data, chunk
