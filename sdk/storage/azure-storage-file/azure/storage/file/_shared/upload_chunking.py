# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=no-self-use

from io import (BytesIO, IOBase, SEEK_CUR, SEEK_END, SEEK_SET, UnsupportedOperation)
from threading import Lock

from math import ceil

import six

from .models import ModifiedAccessConditions
from .utils import (
    encode_base64,
    url_quote,
    get_length,
    return_response_headers)
from .encryption import _get_blob_encryptor_and_padder


_LARGE_BLOB_UPLOAD_MAX_READ_BUFFER_SIZE = 4 * 1024 * 1024
_ERROR_VALUE_SHOULD_BE_SEEKABLE_STREAM = '{0} should be a seekable file-like/io.IOBase type stream object.'


def upload_file_chunks(file_service, file_size, block_size, stream, max_connections,
                       validate_content, timeout, **kwargs):
    uploader = FileChunkUploader(
        file_service,
        file_size,
        block_size,
        stream,
        max_connections > 1,
        validate_content,
        timeout,
        **kwargs
    )
    if max_connections > 1:
        import concurrent.futures
        executor = concurrent.futures.ThreadPoolExecutor(max_connections)
        range_ids = list(executor.map(uploader.process_chunk, uploader.get_chunk_offsets()))
    else:
        if file_size is not None:
            range_ids = [uploader.process_chunk(start) for start in uploader.get_chunk_offsets()]
        else:
            range_ids = uploader.process_all_unknown_size()
    return range_ids


def upload_blob_chunks(blob_service, blob_size, block_size, stream, max_connections, validate_content,  # pylint: disable=too-many-locals
                       access_conditions, uploader_class, append_conditions=None, modified_access_conditions=None,
                       timeout=None, content_encryption_key=None, initialization_vector=None, **kwargs):

    encryptor, padder = _get_blob_encryptor_and_padder(
        content_encryption_key,
        initialization_vector,
        uploader_class is not PageBlobChunkUploader)

    uploader = uploader_class(
        blob_service,
        blob_size,
        block_size,
        stream,
        max_connections > 1,
        validate_content,
        access_conditions,
        append_conditions,
        timeout,
        encryptor,
        padder,
        **kwargs
    )

    # Access conditions do not work with parallelism
    if max_connections > 1:
        uploader.modified_access_conditions = None
    else:
        uploader.modified_access_conditions = modified_access_conditions

    if max_connections > 1:
        import concurrent.futures
        from threading import BoundedSemaphore

        # Ensures we bound the chunking so we only buffer and submit 'max_connections'
        # amount of work items to the executor. This is necessary as the executor queue will keep
        # accepting submitted work items, which results in buffering all the blocks if
        # the max_connections + 1 ensures the next chunk is already buffered and ready for when
        # the worker thread is available.
        chunk_throttler = BoundedSemaphore(max_connections + 1)

        executor = concurrent.futures.ThreadPoolExecutor(max_connections)
        futures = []
        running_futures = []

        # Check for exceptions and fail fast.
        for chunk in uploader.get_chunk_streams():
            for f in running_futures:
                if f.done():
                    if f.exception():
                        raise f.exception()
                    running_futures.remove(f)

            chunk_throttler.acquire()
            future = executor.submit(uploader.process_chunk, chunk)

            # Calls callback upon completion (even if the callback was added after the Future task is done).
            future.add_done_callback(lambda x: chunk_throttler.release())
            futures.append(future)
            running_futures.append(future)

        # result() will wait until completion and also raise any exceptions that may have been set.
        range_ids = [f.result() for f in futures]
    else:
        range_ids = [uploader.process_chunk(result) for result in uploader.get_chunk_streams()]

    if any(range_ids):
        return range_ids
    return uploader.response_headers


def upload_blob_substream_blocks(blob_service, blob_size, block_size, stream, max_connections,
                                 validate_content, access_conditions, uploader_class,
                                 append_conditions=None, modified_access_conditions=None, timeout=None, **kwargs):

    uploader = uploader_class(
        blob_service,
        blob_size,
        block_size,
        stream,
        max_connections > 1,
        validate_content,
        access_conditions,
        append_conditions,
        timeout,
        None,
        None,
        **kwargs
    )
    # ETag matching does not work with parallelism as a ranged upload may start
    # before the previous finishes and provides an etag
    if max_connections > 1:
        uploader.modified_access_conditions = None
    else:
        uploader.modified_access_conditions = modified_access_conditions

    if max_connections > 1:
        import concurrent.futures
        executor = concurrent.futures.ThreadPoolExecutor(max_connections)
        range_ids = list(executor.map(uploader.process_substream_block, uploader.get_substream_blocks()))
    else:
        range_ids = [uploader.process_substream_block(result) for result in uploader.get_substream_blocks()]

    return range_ids


class _BlobChunkUploader(object):  # pylint: disable=too-many-instance-attributes

    def __init__(self, blob_service, blob_size, chunk_size, stream, parallel, validate_content,
                 access_conditions, append_conditions, timeout, encryptor, padder, **kwargs):
        self.blob_service = blob_service
        self.blob_size = blob_size
        self.chunk_size = chunk_size
        self.stream = stream
        self.parallel = parallel
        self.stream_start = stream.tell() if parallel else None
        self.stream_lock = Lock() if parallel else None
        self.progress_total = 0
        self.progress_lock = Lock() if parallel else None
        self.validate_content = validate_content
        self.lease_access_conditions = access_conditions
        self.modified_access_conditions = None
        self.append_conditions = append_conditions
        self.timeout = timeout
        self.encryptor = encryptor
        self.padder = padder
        self.response_headers = None
        self.etag = None
        self.last_modified = None
        self.request_options = kwargs

    def get_chunk_streams(self):
        index = 0
        while True:
            data = b''
            read_size = self.chunk_size

            # Buffer until we either reach the end of the stream or get a whole chunk.
            while True:
                if self.blob_size:
                    read_size = min(self.chunk_size - len(data), self.blob_size - (index + len(data)))
                temp = self.stream.read(read_size)
                if not isinstance(temp, six.binary_type):
                    raise TypeError('Blob data should be of type bytes.')
                data += temp or b""

                # We have read an empty string and so are at the end
                # of the buffer or we have read a full chunk.
                if temp == b'' or len(data) == self.chunk_size:
                    break

            if len(data) == self.chunk_size:
                if self.padder:
                    data = self.padder.update(data)
                if self.encryptor:
                    data = self.encryptor.update(data)
                yield index, data
            else:
                if self.padder:
                    data = self.padder.update(data) + self.padder.finalize()
                if self.encryptor:
                    data = self.encryptor.update(data) + self.encryptor.finalize()
                if data:
                    yield index, data
                break
            index += len(data)

    def process_chunk(self, chunk_data):
        chunk_bytes = chunk_data[1]
        chunk_offset = chunk_data[0]
        return self._upload_chunk_with_progress(chunk_offset, chunk_bytes)

    def _update_progress(self, length):
        if self.progress_lock is not None:
            with self.progress_lock:
                self.progress_total += length
        else:
            self.progress_total += length

    def _upload_chunk(self, chunk_offset, chunk_data):
        raise NotImplementedError("Must be implemented by child class.")

    def _upload_chunk_with_progress(self, chunk_offset, chunk_data):
        range_id = self._upload_chunk(chunk_offset, chunk_data)
        self._update_progress(len(chunk_data))
        return range_id

    def get_substream_blocks(self):
        assert self.chunk_size is not None
        lock = self.stream_lock
        blob_length = self.blob_size

        if blob_length is None:
            blob_length = get_length(self.stream)
            if blob_length is None:
                raise ValueError("Unable to determine content length of upload data.")

        blocks = int(ceil(blob_length / (self.chunk_size * 1.0)))
        last_block_size = self.chunk_size if blob_length % self.chunk_size == 0 else blob_length % self.chunk_size

        for i in range(blocks):
            yield ('BlockId{}'.format("%05d" % i),
                   _SubStream(self.stream, i * self.chunk_size, last_block_size if i == blocks - 1 else self.chunk_size,
                              lock))

    def process_substream_block(self, block_data):
        return self._upload_substream_block_with_progress(block_data[0], block_data[1])

    def _upload_substream_block(self, block_id, block_stream):
        raise NotImplementedError("Must be implemented by child class.")

    def _upload_substream_block_with_progress(self, block_id, block_stream):
        range_id = self._upload_substream_block(block_id, block_stream)
        return range_id

    def set_response_properties(self, resp):
        self.etag = resp.etag
        self.last_modified = resp.last_modified


class BlockBlobChunkUploader(_BlobChunkUploader):

    def _upload_chunk(self, chunk_offset, chunk_data):
        # TODO: This is incorrect, but works with recording.
        block_id = encode_base64(url_quote(encode_base64('{0:032d}'.format(chunk_offset))))
        self.blob_service.stage_block(
            block_id,
            len(chunk_data),
            chunk_data,
            timeout=self.timeout,
            lease_access_conditions=self.lease_access_conditions,
            validate_content=self.validate_content,
            data_stream_total=self.blob_size,
            upload_stream_current=self.progress_total,
            **self.request_options)
        return block_id

    def _upload_substream_block(self, block_id, block_stream):
        try:
            self.blob_service.stage_block(
                block_id,
                len(block_stream),
                block_stream,
                validate_content=self.validate_content,
                lease_access_conditions=self.lease_access_conditions,
                timeout=self.timeout,
                data_stream_total=self.blob_size,
                upload_stream_current=self.progress_total,
                **self.request_options)
        finally:
            block_stream.close()
        return block_id


class PageBlobChunkUploader(_BlobChunkUploader):  # pylint: disable=abstract-method

    def _is_chunk_empty(self, chunk_data):
        # read until non-zero byte is encountered
        # if reached the end without returning, then chunk_data is all 0's
        for each_byte in chunk_data:
            if each_byte not in [0, b'\x00']:
                return False
        return True

    def _upload_chunk(self, chunk_offset, chunk_data):
        # avoid uploading the empty pages
        if not self._is_chunk_empty(chunk_data):
            chunk_end = chunk_offset + len(chunk_data) - 1
            content_range = 'bytes={0}-{1}'.format(chunk_offset, chunk_end)
            computed_md5 = None
            self.response_headers = self.blob_service.upload_pages(
                chunk_data,
                content_length=len(chunk_data),
                transactional_content_md5=computed_md5,
                timeout=self.timeout,
                range=content_range,
                lease_access_conditions=self.lease_access_conditions,
                modified_access_conditions=self.modified_access_conditions,
                validate_content=self.validate_content,
                cls=return_response_headers,
                data_stream_total=self.blob_size,
                upload_stream_current=self.progress_total,
                **self.request_options)

            if not self.parallel:
                self.modified_access_conditions = ModifiedAccessConditions(
                    if_match=self.response_headers['etag'])


class AppendBlobChunkUploader(_BlobChunkUploader):  # pylint: disable=abstract-method

    def __init__(self, *args, **kwargs):
        super(AppendBlobChunkUploader, self).__init__(*args, **kwargs)
        self.current_length = None

    def _upload_chunk(self, chunk_offset, chunk_data):
        if self.current_length is None:
            self.response_headers = self.blob_service.append_block(
                chunk_data,
                content_length=len(chunk_data),
                timeout=self.timeout,
                lease_access_conditions=self.lease_access_conditions,
                modified_access_conditions=self.modified_access_conditions,
                validate_content=self.validate_content,
                append_position_access_conditions=self.append_conditions,
                cls=return_response_headers,
                data_stream_total=self.blob_size,
                upload_stream_current=self.progress_total,
                **self.request_options
            )
            self.current_length = int(self.response_headers['blob_append_offset'])
        else:
            self.append_conditions.append_position = self.current_length + chunk_offset
            self.response_headers = self.blob_service.append_block(
                chunk_data,
                content_length=len(chunk_data),
                timeout=self.timeout,
                lease_access_conditions=self.lease_access_conditions,
                modified_access_conditions=self.modified_access_conditions,
                validate_content=self.validate_content,
                append_position_access_conditions=self.append_conditions,
                cls=return_response_headers,
                data_stream_total=self.blob_size,
                upload_stream_current=self.progress_total,
                **self.request_options
            )


class FileChunkUploader(object):  # pylint: disable=too-many-instance-attributes

    def __init__(self, file_service, file_size, chunk_size, stream, parallel,
                 validate_content, timeout, **kwargs):
        self.file_service = file_service
        self.file_size = file_size
        self.chunk_size = chunk_size
        self.stream = stream
        self.parallel = parallel
        self.stream_start = stream.tell() if parallel else None
        self.stream_lock = Lock() if parallel else None
        self.progress_total = 0
        self.progress_lock = Lock() if parallel else None
        self.validate_content = validate_content
        self.timeout = timeout
        self.request_options = kwargs

    def get_chunk_offsets(self):
        index = 0
        if self.file_size is None:
            # we don't know the size of the stream, so we have no
            # choice but to seek
            while True:
                data = self._read_from_stream(index, 1)
                if not data:
                    break
                yield index
                index += self.chunk_size
        else:
            while index < self.file_size:
                yield index
                index += self.chunk_size

    def process_chunk(self, chunk_offset):
        size = self.chunk_size
        if self.file_size is not None:
            size = min(size, self.file_size - chunk_offset)
        chunk_data = self._read_from_stream(chunk_offset, size)
        return self._upload_chunk_with_progress(chunk_offset, chunk_data)

    def process_all_unknown_size(self):
        assert self.stream_lock is None
        range_ids = []
        index = 0
        while True:
            data = self._read_from_stream(None, self.chunk_size)
            if data:
                index += len(data)
                range_id = self._upload_chunk_with_progress(index, data)
                range_ids.append(range_id)
            else:
                break

        return range_ids

    def _read_from_stream(self, offset, count):
        if self.stream_lock is not None:
            with self.stream_lock:
                self.stream.seek(self.stream_start + offset)
                data = self.stream.read(count)
        else:
            data = self.stream.read(count)
        return data

    def _update_progress(self, length):
        if self.progress_lock is not None:
            with self.progress_lock:
                self.progress_total += length
        else:
            self.progress_total += length

    def _upload_chunk_with_progress(self, chunk_start, chunk_data):
        chunk_end = chunk_start + len(chunk_data) - 1
        self.file_service.upload_range(
            chunk_data,
            chunk_start,
            chunk_end,
            validate_content=self.validate_content,
            timeout=self.timeout,
            data_stream_total=self.file_size,
            upload_stream_current=self.progress_total,
            **self.request_options
        )
        range_id = 'bytes={0}-{1}'.format(chunk_start, chunk_end)
        self._update_progress(len(chunk_data))
        return range_id


class _SubStream(IOBase):
    def __init__(self, wrapped_stream, stream_begin_index, length, lockObj):
        # Python 2.7: file-like objects created with open() typically support seek(), but are not
        # derivations of io.IOBase and thus do not implement seekable().
        # Python > 3.0: file-like objects created with open() are derived from io.IOBase.
        try:
            # only the main thread runs this, so there's no need grabbing the lock
            wrapped_stream.seek(0, SEEK_CUR)
        except:
            raise ValueError("Wrapped stream must support seek().")

        self._lock = lockObj
        self._wrapped_stream = wrapped_stream
        self._position = 0
        self._stream_begin_index = stream_begin_index
        self._length = length
        self._buffer = BytesIO()

        # we must avoid buffering more than necessary, and also not use up too much memory
        # so the max buffer size is capped at 4MB
        self._max_buffer_size = length if length < _LARGE_BLOB_UPLOAD_MAX_READ_BUFFER_SIZE \
            else _LARGE_BLOB_UPLOAD_MAX_READ_BUFFER_SIZE
        self._current_buffer_start = 0
        self._current_buffer_size = 0
        super(_SubStream, self).__init__()

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

    def read(self, n):
        if self.closed:
            raise ValueError("Stream is closed.")

        # adjust if out of bounds
        if n + self._position >= self._length:
            n = self._length - self._position

        # return fast
        if n == 0 or self._buffer.closed:
            return b''

        # attempt first read from the read buffer and update position
        read_buffer = self._buffer.read(n)
        bytes_read = len(read_buffer)
        bytes_remaining = n - bytes_read
        self._position += bytes_read

        # repopulate the read buffer from the underlying stream to fulfill the request
        # ensure the seek and read operations are done atomically (only if a lock is provided)
        if bytes_remaining > 0:
            with self._buffer:
                # either read in the max buffer size specified on the class
                # or read in just enough data for the current block/sub stream
                current_max_buffer_size = min(self._max_buffer_size, self._length - self._position)

                # lock is only defined if max_connections > 1 (parallel uploads)
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
            offset = - offset
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


class IterStreamer(object):
    """
    File-like streaming iterator.
    """
    def __init__(self, generator, encoding='UTF-8'):
        self.generator = generator
        self.iterator = iter(generator)
        self.leftover = b''
        self.encoding = encoding

    def __len__(self):
        return self.generator.__len__()

    def __iter__(self):
        return self.iterator

    def seekable(self):
        return False

    def next(self):
        return next(self.iterator)

    def tell(self, *args, **kwargs):
        raise UnsupportedOperation("Data generator does not support tell.")

    def seek(self, *args, **kwargs):
        raise UnsupportedOperation("Data generator is unseekable.")

    def read(self, size):
        data = self.leftover
        count = len(self.leftover)
        try:
            while count < size:
                chunk = self.next()
                if isinstance(chunk, six.text_type):
                    chunk = chunk.encode(self.encoding)
                data += chunk
                count += len(chunk)
        except StopIteration:
            pass

        if count > size:
            self.leftover = data[size:]

        return data[:size]
