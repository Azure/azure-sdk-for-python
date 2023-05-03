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

MAX_CHUNK_SIZE_BYTES = 1024 * 1024  # 1 MiB
GZIP_MAGIC_NUMBER = b"\x1f\x8b"
ENCODING = "utf-8"
LOW_SPACE_THRESHOLD = 1024
ZLIB_WINDOW_BITS = 16 + zlib.MAX_WBITS  # For gzip header

# Characters used to create the JSON array.
CHAR_OPEN = '['.encode(ENCODING)
CHAR_CLOSE = ']'.encode(ENCODING)
CHAR_SEP = ','.encode(ENCODING)
SEP_SIZE = len(CHAR_SEP)


def _create_gzip_chunks(
    logs: List[JSON], max_size_bytes: int = MAX_CHUNK_SIZE_BYTES
) -> Generator[Tuple[bytes, List[JSON]], None, None]:
    """Create gzip-compressed chunks of data to be uploaded to the ingestion service.

    This iterates through each log entry, then progressively compresses and flushes the data up to the
    maximum chunk size specified by `max_size_bytes`. Once the maximum chunk size is reached, the compressed
    data is yielded and the process is repeated until all the logs are compressed and yielded.
    """

    # Initialize tracking variables.
    compressor = zlib.compressobj(wbits=ZLIB_WINDOW_BITS)
    compressed_logs = bytes()
    curr_chunk: List[JSON] = []
    curr_uncompressed_size = 0
    remaining_space = max_size_bytes

    # Account for the opening bracket.
    compressed_logs += compressor.compress(CHAR_OPEN)
    curr_uncompressed_size += len(CHAR_OPEN)

    add_separator = False

    for log in logs:
        # In order to get the accurate size of the compressed data, we need to perform a zlib flush.
        # We try to flush the compressed data only when the size of the uncompressed data reaches the
        # value specified by `remaining_space`. The `remaining_space` is initialized to the maximum
        # chunk size specified by `max_size_bytes` and is decremented by the size of the compressed data.
        # For example, if the `remaining_space` is 1 MiB and the compressed data is 500 KiB, then the
        # `remaining_space` is decremented by 500 KiB. This means that the `remaining_space` is now 500 KiB.
        # Once the `remaining_space` is less than the low space threshold, we yield the compressed data, and
        # the process is then repeated. This yields better compression and speed compared to flushing
        # after each log entry being added.
        if curr_uncompressed_size >= remaining_space:
            compressed_logs += compressor.flush(zlib.Z_FULL_FLUSH)
            remaining_space = max_size_bytes - len(compressed_logs)
            curr_uncompressed_size = 0

            # If remaining space is less than the low space threshold, yield the compressed data.
            if remaining_space <= LOW_SPACE_THRESHOLD:

                # Account for the closing bracket.
                compressed_logs += compressor.compress(CHAR_CLOSE)
                # Finalize the compression.
                compressed_logs += compressor.flush(zlib.Z_FINISH)

                _LOGGER.debug('Yielding gzip compressed data, Length: %d', len(compressed_logs))
                yield compressed_logs, curr_chunk

                # Re-initialize tracking variables.
                compressor = zlib.compressobj(wbits=ZLIB_WINDOW_BITS)
                compressed_logs = bytes()
                remaining_space = max_size_bytes
                curr_chunk = []
                add_separator = False

                compressed_logs += compressor.compress(CHAR_OPEN)
                curr_uncompressed_size += len(CHAR_OPEN)

        # Account for separator (comma) between entries.
        if add_separator:
            compressed_logs += compressor.compress(CHAR_SEP)
            curr_uncompressed_size += SEP_SIZE

        # Encode the log and add it to the compressed data. Remove spaces after separators
        # when log is serialized to JSON.
        encoded_log = json.dumps(log, separators=(',', ':')).encode(ENCODING)
        curr_uncompressed_size += len(encoded_log)
        compressed_logs += compressor.compress(encoded_log)
        curr_chunk.append(log)
        add_separator = True

    # If there are any logs left in the chunk, yield the compressed data.
    if curr_chunk:
        compressed_logs += compressor.compress(CHAR_CLOSE)
        compressed_logs += compressor.flush(zlib.Z_FINISH)
        _LOGGER.debug('Yielding gzip compressed data, Length: %d', len(compressed_logs))
        yield compressed_logs, curr_chunk


def _split_chunks(logs: List[JSON], max_size_bytes: int = MAX_CHUNK_SIZE_BYTES) -> Generator[List[JSON], None, None]:
    chunk_size = 0
    curr_chunk = []
    for log in logs:
        size = len(json.dumps(log).encode("utf-8"))
        if chunk_size + size <= max_size_bytes:
            curr_chunk.append(log)
            chunk_size += size
        else:
            if curr_chunk:
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
