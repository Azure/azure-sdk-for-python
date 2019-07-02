# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import sys
from io import BytesIO

from .models import ShareProperties, DirectoryProperties, FileProperties
from ._generated.models import StorageErrorException
from ._shared.utils import process_storage_error, parse_length_from_content_range
from ._shared.upload_chunking import upload_file_chunks
from ._shared.download_chunking import (
    validate_and_format_range_headers,
    process_range_and_offset,
    process_content,
    ParallelFileChunkDownloader,
    SequentialFileChunkDownloader)


def deserialize_metadata(response, obj, headers):  # pylint: disable=unused-argument
    raw_metadata = {k: v for k, v in response.headers.items() if k.startswith("x-ms-meta-")}
    return {k[10:]: v for k, v in raw_metadata.items()}


def deserialize_share_properties(response, obj, headers):
    metadata = deserialize_metadata(response, obj, headers)
    share_properties = ShareProperties(
        metadata=metadata,
        **headers
    )
    return share_properties


def deserialize_directory_properties(response, obj, headers):
    metadata = deserialize_metadata(response, obj, headers)
    directory_properties = DirectoryProperties(
        metadata=metadata,
        **headers
    )
    return directory_properties


def deserialize_file_properties(response, obj, headers):
    metadata = deserialize_metadata(response, obj, headers)
    file_properties = FileProperties(
        metadata=metadata,
        **headers
    )
    if 'Content-Range' in headers:
        if 'x-ms-content-md5' in headers:
            file_properties.content_settings.content_md5 = headers['x-ms-content-md5']
        else:
            file_properties.content_settings.content_md5 = None
    return file_properties


def deserialize_file_stream(response, obj, headers):
    file_properties = deserialize_file_properties(response, obj, headers)
    obj.properties = file_properties
    return response.location_mode, obj


def upload_file_helper(
        client,
        stream,
        size,
        metadata,
        content_settings,
        validate_content,
        timeout,
        max_connections,
        file_settings,
        **kwargs):
    try:
        if size is None or size < 0:
            raise ValueError("A content size must be specified for a File.")
        response = client.create_file(
            size,
            content_settings=content_settings,
            metadata=metadata,
            timeout=timeout,
            **kwargs
        )
        if size == 0:
            return response

        return upload_file_chunks(
            file_service=client,
            file_size=size,
            block_size=file_settings.max_range_size,
            stream=stream,
            max_connections=max_connections,
            validate_content=validate_content,
            timeout=timeout,
            **kwargs)
    except StorageErrorException as error:
        process_storage_error(error)


class StorageStreamDownloader(object):  # pylint: disable=too-many-instance-attributes
    """A streaming object to download a file.

    The stream downloader can iterated, or download to open file or stream
    over multiple threads.
    """

    def __init__(
            self, share, file_name, file_path, service, config, offset,
            length, validate_content, timeout, **kwargs):
        self.service = service

        self.config = config
        self.offset = offset
        self.length = length
        self.timeout = timeout
        self.validate_content = validate_content
        self.request_options = kwargs
        self.location_mode = None
        self._download_complete = False

        # The service only provides transactional MD5s for chunks under 4MB.
        # If validate_content is on, get only self.MAX_CHUNK_GET_SIZE for the first
        # chunk so a transactional MD5 can be retrieved.
        self.first_get_size = self.config.max_single_get_size if not self.validate_content \
            else self.config.max_chunk_get_size
        initial_request_start = self.offset if self.offset is not None else 0
        if self.length is not None and self.length - self.offset < self.first_get_size:
            initial_request_end = self.length
        else:
            initial_request_end = initial_request_start + self.first_get_size - 1

        self.initial_range, self.initial_offset = process_range_and_offset(
            initial_request_start,
            initial_request_end,
            self.length,
            None, None)

        self.download_size = None
        self.file_size = None
        self.file = self._initial_request()
        self.properties = self.file.properties
        self.properties.name = file_name
        self.properties.share = share
        self.properties.path = file_path

        # Set the content length to the download size instead of the size of
        # the last range
        self.properties.size = self.download_size

        # Overwrite the content range to the user requested range
        self.properties.content_range = 'bytes {0}-{1}/{2}'.format(self.offset, self.length, self.file_size)

        # Overwrite the content MD5 as it is the MD5 for the last range instead
        # of the stored MD5
        # TODO: Set to the stored MD5 when the service returns this
        self.properties.content_md5 = None

    def __len__(self):
        return self.download_size

    def __iter__(self):
        if self.download_size == 0:
            content = b""
        else:
            content = process_content(
                self.file,
                self.initial_offset[0],
                self.initial_offset[1],
                False, None, None)

        if content is not None:
            yield content
        if self._download_complete:
            return

        end_file = self.file_size
        if self.length is not None:
            # Use the length unless it is over the end of the file
            end_file = min(self.file_size, self.length + 1)

        downloader = SequentialFileChunkDownloader(
            file_service=self.service,
            download_size=self.download_size,
            chunk_size=self.config.max_chunk_get_size,
            progress=self.first_get_size,
            start_range=self.initial_range[1] + 1,  # start where the first download ended
            end_range=end_file,
            stream=None,
            validate_content=self.validate_content,
            timeout=self.timeout,
            use_location=self.location_mode,
            cls=deserialize_file_stream,
            **self.request_options)

        for chunk in downloader.get_chunk_offsets():
            yield downloader.yield_chunk(chunk)

    def _initial_request(self):
        range_header, range_validation = validate_and_format_range_headers(
            self.initial_range[0],
            self.initial_range[1],
            start_range_required=False,
            end_range_required=False,
            check_content_md5=self.validate_content)

        try:
            location_mode, file_stream = self.service.download(
                timeout=self.timeout,
                range=range_header,
                range_get_content_md5=range_validation,
                validate_content=self.validate_content,
                cls=deserialize_file_stream,
                data_stream_total=None,
                download_stream_current=0,
                **self.request_options)

            # Check the location we read from to ensure we use the same one
            # for subsequent requests.
            self.location_mode = location_mode

            # Parse the total file size and adjust the download size if ranges
            # were specified
            self.file_size = parse_length_from_content_range(file_stream.properties.content_range)
            if self.length is not None:
                # Use the length unless it is over the end of the file
                self.download_size = min(self.file_size, self.length - self.offset + 1)
            elif self.offset is not None:
                self.download_size = self.file_size - self.offset
            else:
                self.download_size = self.file_size

        except StorageErrorException as error:
            if self.offset is None and error.response.status_code == 416:
                # Get range will fail on an empty file. If the user did not
                # request a range, do a regular get request in order to get
                # any properties.
                try:
                    _, file_stream = self.service.download(
                        timeout=self.timeout,
                        validate_content=self.validate_content,
                        cls=deserialize_file_stream,
                        data_stream_total=0,
                        download_stream_current=0,
                        **self.request_options)
                except StorageErrorException as error:
                    process_storage_error(error)

                # Set the download size to empty
                self.download_size = 0
                self.file_size = 0
            else:
                process_storage_error(error)

        # If the file is small, the download is complete at this point.
        # If file size is large, download the rest of the file in chunks.
        if file_stream.properties.size == self.download_size:
            self._download_complete = True

        return file_stream

    def content_as_bytes(self, max_connections=1):
        """Download the contents of this file.

        This operation is blocking until all data is downloaded.

        :param int max_connections:
            The number of parallel connections with which to download.
        :rtype: bytes
        """
        stream = BytesIO()
        self.download_to_stream(stream, max_connections=max_connections)
        return stream.getvalue()

    def content_as_text(self, max_connections=1, encoding='UTF-8'):
        """Download the contents of this file, and decode as text.

        This operation is blocking until all data is downloaded.

        :param int max_connections:
            The number of parallel connections with which to download.
        :rtype: str
        """
        content = self.content_as_bytes(max_connections=max_connections)
        return content.decode(encoding)

    def download_to_stream(self, stream, max_connections=1):
        """Download the contents of this file to a stream.

        :param stream:
            The stream to download to. This can be an open file-handle,
            or any writable stream. The stream must be seekable if the download
            uses more than one parallel connection.
        :returns: The properties of the downloaded file.
        :rtype: ~azure.storage.file.models.FileProperties
        """
        # the stream must be seekable if parallel download is required
        if max_connections > 1:
            error_message = "Target stream handle must be seekable."
            if sys.version_info >= (3,) and not stream.seekable():
                raise ValueError(error_message)

            try:
                stream.seek(stream.tell())
            except (NotImplementedError, AttributeError):
                raise ValueError(error_message)

        if self.download_size == 0:
            content = b""
        else:
            content = process_content(
                self.file,
                self.initial_offset[0],
                self.initial_offset[1],
                False, None, None)
        # Write the content to the user stream
        # Clear file content since output has been written to user stream
        if content is not None:
            stream.write(content)
        if self._download_complete:
            return self.properties

        end_file = self.file_size
        if self.length is not None:
            # Use the length unless it is over the end of the file
            end_file = min(self.file_size, self.length + 1)

        downloader_class = ParallelFileChunkDownloader if max_connections > 1 else SequentialFileChunkDownloader
        downloader = downloader_class(
            file_service=self.service,
            download_size=self.download_size,
            chunk_size=self.config.max_chunk_get_size,
            progress=self.first_get_size,
            start_range=self.initial_range[1] + 1,  # start where the first download ended
            end_range=end_file,
            stream=stream,
            validate_content=self.validate_content,
            timeout=self.timeout,
            use_location=self.location_mode,
            cls=deserialize_file_stream,
            **self.request_options)

        if max_connections > 1:
            import concurrent.futures
            executor = concurrent.futures.ThreadPoolExecutor(max_connections)
            list(executor.map(downloader.process_chunk, downloader.get_chunk_offsets()))
        else:
            for chunk in downloader.get_chunk_offsets():
                downloader.process_chunk(chunk)

        return self.properties
