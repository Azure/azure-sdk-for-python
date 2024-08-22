# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import warnings
from collections import namedtuple
from concurrent import futures
from io import BytesIO, IOBase, SEEK_CUR, SEEK_END, SEEK_SET, UnsupportedOperation
from itertools import islice
from math import ceil
from threading import Lock
from typing import Any, cast, Dict, Generator, IO, Iterable, Optional, Sized, Tuple, Union

from azure.core.tracing.common import with_current_context

from .import encode_base64, url_quote
from .request_handlers import get_length, read_length
from .response_handlers import return_response_headers
from .streams import IterStreamer, StructuredMessageEncodeStream, StructuredMessageProperties
from .validation import calculate_crc64, calculate_md5, ChecksumAlgorithm, combine_crc64, get_crc64_bytes


_LARGE_BLOB_UPLOAD_MAX_READ_BUFFER_SIZE = 4 * 1024 * 1024
_ERROR_VALUE_SHOULD_BE_SEEKABLE_STREAM = "{0} should be a seekable file-like/io.IOBase type stream object."


def prepare_upload_data(
    data: Union[bytes, str, IO[bytes], IO[str], Iterable[bytes], Iterable[str]],
    encoding: str,
    data_length: Optional[int],
    validate_content: Union[bool, str, None]
) -> Tuple[Union[bytes, IO[bytes]], int, int]:
    # Trim the incoming data per provided length
    if data_length is not None and isinstance(data, (str, bytes)) and data_length != len(data):
        data = data[:data_length]

    if isinstance(data, str):
        data = data.encode(encoding)
        data_length = len(data)

    # Attempt to determine length of data if it's not provided
    if data_length is None:
        data_length = get_length(data)
    # If we still can't get the length, read all the data into memory
    if data_length is None:
        warnings.warn("Unable to determine length for Iterable/IO, reading all data into memory.")
        data_length, data = read_length(data)

    structured_message = validate_content == ChecksumAlgorithm.CRC64
    md5 = validate_content in (True, ChecksumAlgorithm.MD5)
    if isinstance(data, bytes):
        if structured_message:
            data = BytesIO(data)
    elif hasattr(data, 'read'):
        # Block IO[str] with CRC64
        if structured_message:
            test = data.read(0)
            if not isinstance(test, bytes):
                raise TypeError("Only IO[bytes] is supported when using CRC64.")
    elif hasattr(data, '__iter__') and not isinstance(data, (list, tuple, set, dict)):
        data = IterStreamer(
            cast(Iterable[bytes], data),
            length=data_length,
            encoding='latin-1',  # Use latin-1 for backwards compatibility with Requests
            block_str=structured_message)
    else:
        raise TypeError(f"Unsupported data type: {type(data)}")

    # If MD5, read data out of IterStreamer because the pipeline
    # will require a seekable stream which IterStreamer is not.
    if isinstance(data, IterStreamer) and md5:
        data = data.read(data_length)

    content_length = data_length
    if structured_message:
        data = StructuredMessageEncodeStream(data, data_length, StructuredMessageProperties.CRC64)  # type: ignore
        content_length = len(cast(Sized, data))

    return data, data_length, content_length  # type: ignore


def _parallel_uploads(executor, uploader, pending, running):
    chunks = []
    while True:
        # Wait for some download to finish before adding a new one
        done, running = futures.wait(running, return_when=futures.FIRST_COMPLETED)
        chunks.extend([chunk.result() for chunk in done])
        try:
            for _ in range(0, len(done)):
                next_chunk = next(pending)
                running.add(executor.submit(with_current_context(uploader), next_chunk))
        except StopIteration:
            break

    # Wait for the remaining uploads to finish
    done, _running = futures.wait(running)
    chunks.extend([chunk.result() for chunk in done])
    return chunks


def upload_data_chunks(
        service=None,
        uploader_class=None,
        total_size=None,
        chunk_size=None,
        max_concurrency=None,
        stream=None,
        progress_hook=None,
        **kwargs):

    parallel = max_concurrency > 1
    if parallel and 'modified_access_conditions' in kwargs:
        # Access conditions do not work with parallelism
        kwargs['modified_access_conditions'] = None

    uploader = uploader_class(
        service=service,
        total_size=total_size,
        chunk_size=chunk_size,
        stream=stream,
        parallel=parallel,
        progress_hook=progress_hook,
        **kwargs)

    if parallel:
        with futures.ThreadPoolExecutor(max_concurrency) as executor:
            upload_tasks = uploader.get_chunk_streams()
            running_futures = [
                executor.submit(with_current_context(uploader.process_chunk), u)
                for u in islice(upload_tasks, 0, max_concurrency)
            ]
            chunks = _parallel_uploads(executor, uploader.process_chunk, upload_tasks, running_futures)
    else:
        chunks = [uploader.process_chunk(result) for result in uploader.get_chunk_streams()]

    chunks.sort(key=lambda c: c.offset)
    # If there is a crc64, do overall crc check
    if chunks[0].crc64 is not None:
        combined = combine_crc64([(c.crc64, c.length) for c in chunks])
        if combined != uploader.overall_crc64:
            raise ValueError("Checksum mismatch detected during upload. Any data written may be invalid.")

    # If chunks have an id, return list of ids
    if chunks[0].id is not None:
        return [c.id for c in chunks]
    # Else, return the response headers for the last chunk that had a response. (Page Blobs can have empty responses)
    for c in reversed(chunks):
        if c.response_headers:
            return c.response_headers
    return {}


def upload_substream_blocks(
        service=None,
        uploader_class=None,
        total_size=None,
        chunk_size=None,
        max_concurrency=None,
        stream=None,
        progress_hook=None,
        **kwargs):
    parallel = max_concurrency > 1
    if parallel and 'modified_access_conditions' in kwargs:
        # Access conditions do not work with parallelism
        kwargs['modified_access_conditions'] = None
    uploader = uploader_class(
        service=service,
        total_size=total_size,
        chunk_size=chunk_size,
        stream=stream,
        parallel=parallel,
        progress_hook=progress_hook,
        **kwargs)

    if parallel:
        with futures.ThreadPoolExecutor(max_concurrency) as executor:
            upload_tasks = uploader.get_substream_blocks()
            running_futures = [
                executor.submit(with_current_context(uploader.process_substream_block), u)
                for u in islice(upload_tasks, 0, max_concurrency)
            ]
            range_ids = _parallel_uploads(executor, uploader.process_substream_block, upload_tasks, running_futures)
    else:
        range_ids = [uploader.process_substream_block(b) for b in uploader.get_substream_blocks()]
    if any(range_ids):
        return sorted(range_ids)
    return []


class ChunkInfo:
    offset: int
    length: int
    md5: Optional[bytes] = None
    crc64: Optional[int] = None
    id: Optional[str] = None
    """The id of the chunk. Only set if chunk needs to be committed."""
    response_headers: Dict[str, Any] = {}
    """The response headers from the upload chunk operation."""

    def __init__(self, offset: int, data: bytes, checksum_algorithm: Optional[Union[bool, str]]):
        self.offset = offset
        self.length = len(data)

        if checksum_algorithm == ChecksumAlgorithm.MD5:
            self.md5 = calculate_md5(data)
        if checksum_algorithm == ChecksumAlgorithm.CRC64:
            self.crc64 = calculate_crc64(data, 0)

    @property
    def crc64_bytes(self) -> Optional[bytes]:
        return get_crc64_bytes(self.crc64) if self.crc64 is not None else None


class _ChunkUploader(object):  # pylint: disable=too-many-instance-attributes

    def __init__(
            self, service,
            total_size,
            chunk_size,
            stream,
            parallel,
            encryptor=None,
            padder=None,
            progress_hook=None,
            validate_content=None,
            **kwargs):
        self.service = service
        self.total_size = total_size
        self.chunk_size = chunk_size
        self.stream = stream
        self.parallel = parallel
        self.validate_content = validate_content
        self.overall_crc64 = 0

        # Stream management
        self.stream_lock = Lock() if parallel else None

        # Progress feedback
        self.progress_total = 0
        self.progress_lock = Lock() if parallel else None
        self.progress_hook = progress_hook

        # Encryption
        self.encryptor = encryptor
        self.padder = padder
        self.etag = None
        self.last_modified = None
        self.request_options = kwargs
        # Legacy support for bool - Pass True through to pipeline
        self.request_options['validate_content'] = self.validate_content if self.validate_content is True else None

    def get_chunk_streams(self) -> Generator[Tuple[bytes, ChunkInfo], None, None]:
        index = 0
        while True:
            data = b""
            read_size = self.chunk_size

            # Buffer until we either reach the end of the stream or get a whole chunk.
            while True:
                if self.total_size:
                    read_size = min(self.chunk_size - len(data), self.total_size - (index + len(data)))
                temp = self.stream.read(read_size)
                if not isinstance(temp, bytes):
                    raise TypeError("Blob data should be of type bytes.")
                data += temp or b""

                # We have read an empty string and so are at the end
                # of the buffer or we have read a full chunk.
                if temp == b"" or len(data) == self.chunk_size:
                    break

            # Content validation and encryption cannot be enabled at the same time,
            # so this is safe to do here, before encryption
            if self.validate_content == ChecksumAlgorithm.CRC64:
                self.overall_crc64 = calculate_crc64(data, self.overall_crc64)

            if len(data) == self.chunk_size:
                if self.padder:
                    data = self.padder.update(data)
                if self.encryptor:
                    data = self.encryptor.update(data)
                yield data, ChunkInfo(index, data, self.validate_content)
            else:
                if self.padder:
                    data = self.padder.update(data) + self.padder.finalize()
                if self.encryptor:
                    data = self.encryptor.update(data) + self.encryptor.finalize()
                if data:
                    yield data, ChunkInfo(index, data, self.validate_content)
                break
            index += len(data)

    def process_chunk(self, chunk_data: Tuple[bytes, ChunkInfo]) -> ChunkInfo:
        chunk_info = self._upload_chunk(chunk_data[0], chunk_data[1])
        self._update_progress(chunk_info.length)
        return chunk_info

    def _update_progress(self, length):
        if self.progress_lock is not None:
            with self.progress_lock:
                self.progress_total += length
        else:
            self.progress_total += length

        if self.progress_hook:
            self.progress_hook(self.progress_total, self.total_size)

    def _upload_chunk(self, data: bytes, chunk_info: ChunkInfo) -> ChunkInfo:
        raise NotImplementedError("Must be implemented by child class.")

    def get_substream_blocks(self):
        assert self.chunk_size is not None
        lock = self.stream_lock
        blob_length = self.total_size

        if blob_length is None:
            blob_length = get_length(self.stream)
            if blob_length is None:
                raise ValueError("Unable to determine content length of upload data.")

        blocks = int(ceil(blob_length / (self.chunk_size * 1.0)))
        last_block_size = self.chunk_size if blob_length % self.chunk_size == 0 else blob_length % self.chunk_size

        for i in range(blocks):
            index = i * self.chunk_size
            length = last_block_size if i == blocks - 1 else self.chunk_size
            yield index, SubStream(self.stream, index, length, lock)

    def process_substream_block(self, block_data):
        return self._upload_substream_block_with_progress(block_data[0], block_data[1])

    def _upload_substream_block(self, index, block_stream):
        raise NotImplementedError("Must be implemented by child class.")

    def _upload_substream_block_with_progress(self, index, block_stream):
        range_id = self._upload_substream_block(index, block_stream)
        self._update_progress(len(block_stream))
        return range_id

    def set_response_properties(self, resp):
        self.etag = resp.etag
        self.last_modified = resp.last_modified


class BlockBlobChunkUploader(_ChunkUploader):

    def __init__(self, *args, **kwargs):
        kwargs.pop("modified_access_conditions", None)
        super(BlockBlobChunkUploader, self).__init__(*args, **kwargs)
        self.current_length = None

    def _upload_chunk(self, data: bytes, chunk_info: ChunkInfo) -> ChunkInfo:
        # TODO: This is incorrect, but works with recording.
        index = f'{chunk_info.offset:032d}'
        block_id = encode_base64(url_quote(encode_base64(index)))
        response_headers = self.service.stage_block(
            block_id,
            chunk_info.length,
            data,
            transactional_content_md5=chunk_info.md5,
            transactional_content_crc64=chunk_info.crc64_bytes,
            cls=return_response_headers,
            data_stream_total=self.total_size,
            upload_stream_current=self.progress_total,
            **self.request_options
        )
        chunk_info.id = block_id
        chunk_info.response_headers = response_headers
        return chunk_info

    def _upload_substream_block(self, index, block_stream):
        try:
            block_id = f'BlockId{(index//self.chunk_size):05}'
            self.service.stage_block(
                block_id,
                len(block_stream),
                block_stream,
                data_stream_total=self.total_size,
                upload_stream_current=self.progress_total,
                **self.request_options
            )
        finally:
            block_stream.close()
        return block_id


class PageBlobChunkUploader(_ChunkUploader):  # pylint: disable=abstract-method

    def _is_chunk_empty(self, chunk_data):
        # read until non-zero byte is encountered
        # if reached the end without returning, then chunk_data is all 0's
        return not any(bytearray(chunk_data))

    def _upload_chunk(self, data: bytes, chunk_info: ChunkInfo) -> ChunkInfo:
        # avoid uploading the empty pages
        response_headers = {}
        if not self._is_chunk_empty(data):
            chunk_end = chunk_info.offset + chunk_info.length - 1
            content_range = f"bytes={chunk_info.offset}-{chunk_end}"
            response_headers = self.service.upload_pages(
                body=data,
                content_length=chunk_info.length,
                range=content_range,
                transactional_content_md5=chunk_info.md5,
                transactional_content_crc64=chunk_info.crc64_bytes,
                cls=return_response_headers,
                data_stream_total=self.total_size,
                upload_stream_current=self.progress_total,
                **self.request_options
            )

            if not self.parallel and self.request_options.get('modified_access_conditions'):
                self.request_options['modified_access_conditions'].if_match = response_headers['etag']
        chunk_info.response_headers = response_headers
        return chunk_info

    def _upload_substream_block(self, index, block_stream):
        pass


class AppendBlobChunkUploader(_ChunkUploader):  # pylint: disable=abstract-method

    def __init__(self, *args, **kwargs):
        super(AppendBlobChunkUploader, self).__init__(*args, **kwargs)
        self.current_length = None

    def _upload_chunk(self, data: bytes, chunk_info: ChunkInfo) -> ChunkInfo:
        if self.current_length is None:
            response_headers = self.service.append_block(
                body=data,
                content_length=chunk_info.length,
                transactional_content_md5=chunk_info.md5,
                transactional_content_crc64=chunk_info.crc64_bytes,
                cls=return_response_headers,
                data_stream_total=self.total_size,
                upload_stream_current=self.progress_total,
                **self.request_options
            )
            self.current_length = int(response_headers["blob_append_offset"])
        else:
            self.request_options['append_position_access_conditions'].append_position = \
                self.current_length + chunk_info.offset
            response_headers = self.service.append_block(
                body=data,
                content_length=chunk_info.length,
                transactional_content_md5=chunk_info.md5,
                transactional_content_crc64=chunk_info.crc64_bytes,
                cls=return_response_headers,
                data_stream_total=self.total_size,
                upload_stream_current=self.progress_total,
                **self.request_options
            )
        chunk_info.response_headers = response_headers
        return chunk_info

    def _upload_substream_block(self, index, block_stream):
        pass


class DataLakeFileChunkUploader(_ChunkUploader):  # pylint: disable=abstract-method

    def _upload_chunk(self, data: bytes, chunk_info: ChunkInfo) -> ChunkInfo:
        # Use a namedtuple here to avoid having a Datalake import in shared code
        PathHeaders = namedtuple('PathHeaders', ['transactional_content_hash'])
        path_headers = PathHeaders(chunk_info.md5) if chunk_info.md5 is not None else None

        response_headers = self.service.append_data(
            body=data,
            position=chunk_info.offset,
            content_length=chunk_info.length,
            path_http_headers=path_headers,  # type: ignore
            transactional_content_crc64=chunk_info.crc64_bytes,
            cls=return_response_headers,
            data_stream_total=self.total_size,
            upload_stream_current=self.progress_total,
            **self.request_options
        )

        if not self.parallel and self.request_options.get('modified_access_conditions'):
            self.request_options['modified_access_conditions'].if_match = response_headers['etag']
        chunk_info.response_headers = response_headers
        return chunk_info

    def _upload_substream_block(self, index, block_stream):
        try:
            self.service.append_data(
                body=block_stream,
                position=index,
                content_length=len(block_stream),
                cls=return_response_headers,
                data_stream_total=self.total_size,
                upload_stream_current=self.progress_total,
                **self.request_options
            )
        finally:
            block_stream.close()


class FileChunkUploader(_ChunkUploader):  # pylint: disable=abstract-method

    def _upload_chunk(self, data: bytes, chunk_info: ChunkInfo) -> ChunkInfo:
        # Files is unique in self.service here is a ShareFileClient rather than a generated client
        # Pass through any value of validate_content to let upload_range use it
        self.request_options['validate_content'] = self.validate_content
        response_headers = self.service.upload_range(
            data,
            chunk_info.offset,
            chunk_info.length,
            data_stream_total=self.total_size,
            upload_stream_current=self.progress_total,
            **self.request_options
        )
        chunk_info.response_headers = response_headers
        return chunk_info

    # TODO: Implement this method.
    def _upload_substream_block(self, index, block_stream):
        pass


class SubStream(IOBase):

    def __init__(self, wrapped_stream, stream_begin_index, length, lockObj):
        # Python 2.7: file-like objects created with open() typically support seek(), but are not
        # derivations of io.IOBase and thus do not implement seekable().
        # Python > 3.0: file-like objects created with open() are derived from io.IOBase.
        try:
            # only the main thread runs this, so there's no need grabbing the lock
            wrapped_stream.seek(0, SEEK_CUR)
        except Exception as exc:
            raise ValueError("Wrapped stream must support seek().") from exc

        self._lock = lockObj
        self._wrapped_stream = wrapped_stream
        self._position = 0
        self._stream_begin_index = stream_begin_index
        self._length = length
        self._buffer = BytesIO()

        # we must avoid buffering more than necessary, and also not use up too much memory
        # so the max buffer size is capped at 4MB
        self._max_buffer_size = (
            length if length < _LARGE_BLOB_UPLOAD_MAX_READ_BUFFER_SIZE else _LARGE_BLOB_UPLOAD_MAX_READ_BUFFER_SIZE
        )
        self._current_buffer_start = 0
        self._current_buffer_size = 0
        super(SubStream, self).__init__()

    def __len__(self):
        return self._length

    def close(self):
        if self._buffer:
            self._buffer.close()
        self._wrapped_stream = None
        IOBase.close(self)

    def fileno(self):
        return self._wrapped_stream.fileno()

    def flush(self):
        pass

    def read(self, size=None):
        if self.closed:  # pylint: disable=using-constant-test
            raise ValueError("Stream is closed.")

        if size is None:
            size = self._length - self._position

        # adjust if out of bounds
        if size + self._position >= self._length:
            size = self._length - self._position

        # return fast
        if size == 0 or self._buffer.closed:
            return b""

        # attempt first read from the read buffer and update position
        read_buffer = self._buffer.read(size)
        bytes_read = len(read_buffer)
        bytes_remaining = size - bytes_read
        self._position += bytes_read

        # repopulate the read buffer from the underlying stream to fulfill the request
        # ensure the seek and read operations are done atomically (only if a lock is provided)
        if bytes_remaining > 0:
            with self._buffer:
                # either read in the max buffer size specified on the class
                # or read in just enough data for the current block/sub stream
                current_max_buffer_size = min(self._max_buffer_size, self._length - self._position)

                # lock is only defined if max_concurrency > 1 (parallel uploads)
                if self._lock:
                    with self._lock:
                        # reposition the underlying stream to match the start of the data to read
                        absolute_position = self._stream_begin_index + self._position
                        self._wrapped_stream.seek(absolute_position, SEEK_SET)
                        # If we can't seek to the right location, our read will be corrupted so fail fast.
                        if self._wrapped_stream.tell() != absolute_position:
                            raise IOError("Stream failed to seek to the desired location.")
                        buffer_from_stream = self._wrapped_stream.read(current_max_buffer_size)
                else:
                    absolute_position = self._stream_begin_index + self._position
                    # It's possible that there's connection problem during data transfer,
                    # so when we retry we don't want to read from current position of wrapped stream,
                    # instead we should seek to where we want to read from.
                    if self._wrapped_stream.tell() != absolute_position:
                        self._wrapped_stream.seek(absolute_position, SEEK_SET)

                    buffer_from_stream = self._wrapped_stream.read(current_max_buffer_size)

            if buffer_from_stream:
                # update the buffer with new data from the wrapped stream
                # we need to note down the start position and size of the buffer, in case seek is performed later
                self._buffer = BytesIO(buffer_from_stream)
                self._current_buffer_start = self._position
                self._current_buffer_size = len(buffer_from_stream)

                # read the remaining bytes from the new buffer and update position
                second_read_buffer = self._buffer.read(bytes_remaining)
                read_buffer += second_read_buffer
                self._position += len(second_read_buffer)

        return read_buffer

    def readable(self):
        return True

    def readinto(self, b):
        raise UnsupportedOperation

    def seek(self, offset, whence=0):
        if whence is SEEK_SET:
            start_index = 0
        elif whence is SEEK_CUR:
            start_index = self._position
        elif whence is SEEK_END:
            start_index = self._length
            offset = -offset
        else:
            raise ValueError("Invalid argument for the 'whence' parameter.")

        pos = start_index + offset

        if pos > self._length:
            pos = self._length
        elif pos < 0:
            pos = 0

        # check if buffer is still valid
        # if not, drop buffer
        if pos < self._current_buffer_start or pos >= self._current_buffer_start + self._current_buffer_size:
            self._buffer.close()
            self._buffer = BytesIO()
        else:  # if yes seek to correct position
            delta = pos - self._current_buffer_start
            self._buffer.seek(delta, SEEK_SET)

        self._position = pos
        return pos

    def seekable(self):
        return True

    def tell(self):
        return self._position

    def write(self):
        raise UnsupportedOperation

    def writelines(self):
        raise UnsupportedOperation

    def writeable(self):
        return False
