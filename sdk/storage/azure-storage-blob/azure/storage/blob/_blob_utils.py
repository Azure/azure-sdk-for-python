# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=no-self-use

import sys
from io import BytesIO, SEEK_SET, UnsupportedOperation
from typing import Optional, Union, Any, TypeVar, TYPE_CHECKING # pylint: disable=unused-import

import six
from azure.core.exceptions import ResourceExistsError, ResourceModifiedError

from ._shared.utils import (
    process_storage_error,
    validate_and_format_range_headers,
    parse_length_from_content_range,
    return_response_headers)
from ._shared.models import StorageErrorCode, ModifiedAccessConditions
from ._shared.upload_chunking import (
    upload_blob_chunks,
    upload_blob_substream_blocks,
    BlockBlobChunkUploader,
    PageBlobChunkUploader,
    AppendBlobChunkUploader)
from ._shared.download_chunking import (
    process_content,
    process_range_and_offset,
    ParallelBlobChunkDownloader,
    SequentialBlobChunkDownloader
)
from ._shared.encryption import _generate_blob_encryption_data, _encrypt_blob
from ._generated.models import (
    StorageErrorException,
    BlockLookupList,
    AppendPositionAccessConditions,
    LeaseAccessConditions,
    SequenceNumberAccessConditions
)
from .models import BlobProperties, ContainerProperties

if TYPE_CHECKING:
    from datetime import datetime # pylint: disable=unused-import
    LeaseClient = TypeVar("LeaseClient")

_LARGE_BLOB_UPLOAD_MAX_READ_BUFFER_SIZE = 4 * 1024 * 1024
_ERROR_VALUE_SHOULD_BE_SEEKABLE_STREAM = '{0} should be a seekable file-like/io.IOBase type stream object.'


def _convert_mod_error(error):
    message = error.message.replace(
        "The condition specified using HTTP conditional header(s) is not met.",
        "The specified blob already exists.")
    message = message.replace("ConditionNotMet", "BlobAlreadyExists")
    overwrite_error = ResourceExistsError(
        message=message,
        response=error.response,
        error=error)
    overwrite_error.error_code = StorageErrorCode.blob_already_exists
    raise overwrite_error


def get_access_conditions(lease):
    # type: (Optional[Union[LeaseClient, str]]) -> Union[LeaseAccessConditions, None]
    try:
        lease_id = lease.id # type: ignore
    except AttributeError:
        lease_id = lease # type: ignore
    return LeaseAccessConditions(lease_id=lease_id) if lease_id else None


def get_sequence_conditions(
        if_sequence_number_lte=None, # type: Optional[int]
        if_sequence_number_lt=None, # type: Optional[int]
        if_sequence_number_eq=None, # type: Optional[int]
    ):
    # type: (...) -> Union[SequenceNumberAccessConditions, None]
    if any([if_sequence_number_lte, if_sequence_number_lt, if_sequence_number_eq]):
        return SequenceNumberAccessConditions(
            if_sequence_number_less_than_or_equal_to=if_sequence_number_lte,
            if_sequence_number_less_than=if_sequence_number_lt,
            if_sequence_number_equal_to=if_sequence_number_eq
        )
    return None


def get_modification_conditions(
        if_modified_since=None,  # type: Optional[datetime]
        if_unmodified_since=None,  # type: Optional[datetime]
        if_match=None,  # type: Optional[str]
        if_none_match=None  # type: Optional[str]
    ):
    # type: (...) -> Union[ModifiedAccessConditions, None]
    if any([if_modified_since, if_unmodified_since, if_match, if_none_match]):
        return ModifiedAccessConditions(
            if_modified_since=if_modified_since,
            if_unmodified_since=if_unmodified_since,
            if_match=if_match,
            if_none_match=if_none_match
        )
    return None


def upload_block_blob(  # pylint: disable=too-many-locals
        client,
        data,
        stream,
        length,
        overwrite,
        headers,
        blob_headers,
        access_conditions,
        mod_conditions,
        validate_content,
        timeout,
        max_connections,
        blob_settings,
        require_encryption,
        key_encryption_key,
        **kwargs):
    try:
        overwrite_mod_conditions = None
        if not overwrite:
            overwrite_mod_conditions = get_modification_conditions(if_none_match='*')
        adjusted_count = length
        if (key_encryption_key is not None) and (adjusted_count is not None):
            adjusted_count += (16 - (length % 16))

        # Do single put if the size is smaller than config.max_single_put_size
        if adjusted_count is not None and (adjusted_count < blob_settings.max_single_put_size):
            try:
                data = data.read(length)
                if not isinstance(data, six.binary_type):
                    raise TypeError('Blob data should be of type bytes.')
            except AttributeError:
                pass
            if key_encryption_key:
                encryption_data, data = _encrypt_blob(data, key_encryption_key)
                headers['x-ms-meta-encryptiondata'] = encryption_data
            return client.upload(
                data,
                content_length=adjusted_count,
                timeout=timeout,
                blob_http_headers=blob_headers,
                lease_access_conditions=access_conditions,
                modified_access_conditions=mod_conditions or overwrite_mod_conditions,
                headers=headers,
                cls=return_response_headers,
                validate_content=validate_content,
                data_stream_total=adjusted_count,
                upload_stream_current=0,
                **kwargs)

        cek, iv, encryption_data = None, None, None
        use_original_upload_path = blob_settings.use_byte_buffer or \
            validate_content or require_encryption or \
            blob_settings.max_block_size < blob_settings.min_large_block_upload_threshold or \
            hasattr(stream, 'seekable') and not stream.seekable() or \
            not hasattr(stream, 'seek') or not hasattr(stream, 'tell')

        if use_original_upload_path:
            if key_encryption_key:
                cek, iv, encryption_data = _generate_blob_encryption_data(key_encryption_key)
                headers['x-ms-meta-encryptiondata'] = encryption_data
            block_ids = upload_blob_chunks(
                blob_service=client,
                blob_size=length,
                block_size=blob_settings.max_block_size,
                stream=stream,
                max_connections=max_connections,
                validate_content=validate_content,
                access_conditions=access_conditions,
                uploader_class=BlockBlobChunkUploader,
                timeout=timeout,
                content_encryption_key=cek,
                initialization_vector=iv,
                **kwargs
            )
        else:
            block_ids = upload_blob_substream_blocks(
                blob_service=client,
                blob_size=length,
                block_size=blob_settings.max_block_size,
                stream=stream,
                max_connections=max_connections,
                validate_content=validate_content,
                access_conditions=access_conditions,
                uploader_class=BlockBlobChunkUploader,
                timeout=timeout,
                **kwargs
            )

        block_lookup = BlockLookupList(committed=[], uncommitted=[], latest=[])
        block_lookup.latest = block_ids
        return client.commit_block_list(
            block_lookup,
            blob_http_headers=blob_headers,
            lease_access_conditions=access_conditions,
            timeout=timeout,
            modified_access_conditions=mod_conditions or overwrite_mod_conditions,
            cls=return_response_headers,
            validate_content=validate_content,
            headers=headers,
            **kwargs)
    except StorageErrorException as error:
        try:
            process_storage_error(error)
        except ResourceModifiedError as mod_error:
            if overwrite_mod_conditions:
                _convert_mod_error(mod_error)
            raise


def upload_page_blob(
        client,
        stream,
        length,
        overwrite,
        headers,
        blob_headers,
        access_conditions,
        mod_conditions,
        validate_content,
        premium_page_blob_tier,
        timeout,
        max_connections,
        blob_settings,
        cek,
        iv,
        encryption_data,
        **kwargs):
    try:
        overwrite_mod_conditions = None
        if not overwrite:
            overwrite_mod_conditions = get_modification_conditions(if_none_match='*')
        if length is None or length < 0:
            raise ValueError("A content length must be specified for a Page Blob.")
        if length % 512 != 0:
            raise ValueError("Invalid page blob size: {0}. "
                             "The size must be aligned to a 512-byte boundary.".format(length))
        if premium_page_blob_tier:
            try:
                headers['x-ms-access-tier'] = premium_page_blob_tier.value
            except AttributeError:
                headers['x-ms-access-tier'] = premium_page_blob_tier
        if encryption_data is not None:
            headers['x-ms-meta-encryptiondata'] = encryption_data
        response = client.create(
            content_length=0,
            blob_content_length=length,
            blob_sequence_number=None,
            blob_http_headers=blob_headers,
            timeout=timeout,
            lease_access_conditions=access_conditions,
            modified_access_conditions=mod_conditions or overwrite_mod_conditions,
            cls=return_response_headers,
            headers=headers,
            **kwargs)
        if length == 0:
            return response

        mod_conditions = get_modification_conditions(if_match=response['etag'])
        return upload_blob_chunks(
            blob_service=client,
            blob_size=length,
            block_size=blob_settings.max_page_size,
            stream=stream,
            max_connections=max_connections,
            validate_content=validate_content,
            access_conditions=access_conditions,
            uploader_class=PageBlobChunkUploader,
            modified_access_conditions=mod_conditions,
            timeout=timeout,
            content_encryption_key=cek,
            initialization_vector=iv,
            **kwargs)
    except StorageErrorException as error:
        try:
            process_storage_error(error)
        except ResourceModifiedError as mod_error:
            if overwrite_mod_conditions:
                _convert_mod_error(mod_error)
            raise


def _create_append_blob(
        client,
        blob_headers,
        timeout,
        access_conditions,
        mod_conditions,
        headers,
        **kwargs):
    created = client.create(
        content_length=0,
        blob_http_headers=blob_headers,
        timeout=timeout,
        lease_access_conditions=access_conditions,
        modified_access_conditions=mod_conditions,
        cls=return_response_headers,
        headers=headers,
        **kwargs)
    get_modification_conditions(if_match=created['etag'])  # TODO: Not working...


def upload_append_blob(
        client,
        stream,
        length,
        overwrite,
        headers,
        blob_headers,
        access_conditions,
        mod_conditions,
        maxsize_condition,
        validate_content,
        timeout,
        max_connections,
        blob_settings,
        **kwargs
    ):
    try:
        if length == 0:
            return {}
        append_conditions = AppendPositionAccessConditions(
            max_size=maxsize_condition,
            append_position=None)
        try:
            if overwrite:
                _create_append_blob(
                    client,
                    blob_headers,
                    timeout,
                    access_conditions,
                    mod_conditions,
                    headers,
                    **kwargs)
            return upload_blob_chunks(
                blob_service=client,
                blob_size=length,
                block_size=blob_settings.max_block_size,
                stream=stream,
                append_conditions=append_conditions,
                max_connections=max_connections,
                validate_content=validate_content,
                access_conditions=access_conditions,
                uploader_class=AppendBlobChunkUploader,
                modified_access_conditions=mod_conditions,
                timeout=timeout,
                **kwargs)
        except StorageErrorException as error:
            if error.response.status_code != 404:
                raise
            # rewind the request body if it is a stream
            if hasattr(stream, 'read'):
                try:
                    # attempt to rewind the body to the initial position
                    stream.seek(0, SEEK_SET)
                except UnsupportedOperation:
                    # if body is not seekable, then retry would not work
                    raise error
            _create_append_blob(
                client,
                blob_headers,
                timeout,
                access_conditions,
                mod_conditions,
                headers,
                **kwargs)
            return upload_blob_chunks(
                blob_service=client,
                blob_size=length,
                block_size=blob_settings.max_block_size,
                stream=stream,
                append_conditions=append_conditions,
                max_connections=max_connections,
                validate_content=validate_content,
                access_conditions=access_conditions,
                uploader_class=AppendBlobChunkUploader,
                modified_access_conditions=mod_conditions,
                timeout=timeout,
                **kwargs)
    except StorageErrorException as error:
        process_storage_error(error)


def deserialize_metadata(response, _, headers):  # pylint: disable=unused-argument
    raw_metadata = {k: v for k, v in response.headers.items() if k.startswith("x-ms-meta-")}
    return {k[10:]: v for k, v in raw_metadata.items()}


def deserialize_blob_properties(response, obj, headers):
    metadata = deserialize_metadata(response, obj, headers)
    blob_properties = BlobProperties(
        metadata=metadata,
        **headers
    )
    if 'Content-Range' in headers:
        if 'x-ms-blob-content-md5' in headers:
            blob_properties.content_settings.content_md5 = headers['x-ms-blob-content-md5']
        else:
            blob_properties.content_settings.content_md5 = None
    return blob_properties


def deserialize_blob_stream(response, obj, headers):
    blob_properties = deserialize_blob_properties(response, obj, headers)
    obj.properties = blob_properties
    return response.location_mode, obj


def deserialize_container_properties(response, obj, headers):
    metadata = deserialize_metadata(response, obj, headers)
    container_properties = ContainerProperties(
        metadata=metadata,
        **headers
    )
    return container_properties


class StorageStreamDownloader(object):  # pylint: disable=too-many-instance-attributes
    """A streaming object to download a blob.

    The stream downloader can iterated, or download to open file or stream
    over multiple threads.
    """

    def __init__(
            self, name, container, service, config, offset, length, validate_content,
            access_conditions, mod_conditions, timeout,
            require_encryption, key_encryption_key, key_resolver_function, **kwargs
    ):
        self.service = service
        self.config = config
        self.offset = offset
        self.length = length
        self.timeout = timeout
        self.validate_content = validate_content
        self.access_conditions = access_conditions
        self.mod_conditions = mod_conditions
        self.require_encryption = require_encryption
        self.key_encryption_key = key_encryption_key
        self.key_resolver_function = key_resolver_function
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
            self.key_encryption_key,
            self.key_resolver_function)

        self.download_size = None
        self.blob_size = None
        self.blob = self._initial_request()
        self.properties = self.blob.properties
        self.properties.name = name
        self.properties.container = container
        # Set the content length to the download size instead of the size of
        # the last range
        self.properties.size = self.download_size

        # Overwrite the content range to the user requested range
        self.properties.content_range = 'bytes {0}-{1}/{2}'.format(self.offset, self.length, self.blob_size)

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
                self.blob,
                self.initial_offset[0],
                self.initial_offset[1],
                self.require_encryption,
                self.key_encryption_key,
                self.key_resolver_function)

        if content is not None:
            yield content
        if self._download_complete:
            return

        end_blob = self.blob_size
        if self.length is not None:
            # Use the length unless it is over the end of the blob
            end_blob = min(self.blob_size, self.length + 1)

        downloader = SequentialBlobChunkDownloader(
            blob_service=self.service,
            download_size=self.download_size,
            chunk_size=self.config.max_chunk_get_size,
            progress=self.first_get_size,
            start_range=self.initial_range[1] + 1,  # start where the first download ended
            end_range=end_blob,
            stream=None,
            validate_content=self.validate_content,
            access_conditions=self.access_conditions,
            mod_conditions=self.mod_conditions,
            timeout=self.timeout,
            require_encryption=self.require_encryption,
            key_encryption_key=self.key_encryption_key,
            key_resolver_function=self.key_resolver_function,
            use_location=self.location_mode,
            cls=deserialize_blob_stream,
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
            location_mode, blob = self.service.download(
                timeout=self.timeout,
                range=range_header,
                range_get_content_md5=range_validation,
                lease_access_conditions=self.access_conditions,
                modified_access_conditions=self.mod_conditions,
                validate_content=self.validate_content,
                cls=deserialize_blob_stream,
                data_stream_total=None,
                download_stream_current=0,
                **self.request_options)

            # Check the location we read from to ensure we use the same one
            # for subsequent requests.
            self.location_mode = location_mode

            # Parse the total blob size and adjust the download size if ranges
            # were specified
            self.blob_size = parse_length_from_content_range(blob.properties.content_range)
            if self.length is not None:
                # Use the length unless it is over the end of the blob
                self.download_size = min(self.blob_size, self.length - self.offset + 1)
            elif self.offset is not None:
                self.download_size = self.blob_size - self.offset
            else:
                self.download_size = self.blob_size

        except StorageErrorException as error:
            if self.offset is None and error.response.status_code == 416:
                # Get range will fail on an empty blob. If the user did not
                # request a range, do a regular get request in order to get
                # any properties.
                try:
                    _, blob = self.service.download(
                        timeout=self.timeout,
                        lease_access_conditions=self.access_conditions,
                        modified_access_conditions=self.mod_conditions,
                        validate_content=self.validate_content,
                        cls=deserialize_blob_stream,
                        data_stream_total=0,
                        download_stream_current=0,
                        **self.request_options)
                except StorageErrorException as error:
                    process_storage_error(error)

                # Set the download size to empty
                self.download_size = 0
                self.blob_size = 0
            else:
                process_storage_error(error)

        # If the blob is small, the download is complete at this point.
        # If blob size is large, download the rest of the blob in chunks.
        if blob.properties.size != self.download_size:
            # Lock on the etag. This can be overriden by the user by specifying '*'
            if not self.mod_conditions:
                self.mod_conditions = ModifiedAccessConditions()
            if not self.mod_conditions.if_match:
                self.mod_conditions.if_match = blob.properties.etag
        else:
            self._download_complete = True

        return blob


    def content_as_bytes(self, max_connections=1):
        """Download the contents of this blob.

        This operation is blocking until all data is downloaded.

        :param int max_connections:
            The number of parallel connections with which to download.
        :rtype: bytes
        """
        stream = BytesIO()
        self.download_to_stream(stream, max_connections=max_connections)
        return stream.getvalue()

    def content_as_text(self, max_connections=1, encoding='UTF-8'):
        """Download the contents of this blob, and decode as text.

        This operation is blocking until all data is downloaded.

        :param int max_connections:
            The number of parallel connections with which to download.
        :rtype: str
        """
        content = self.content_as_bytes(max_connections=max_connections)
        return content.decode(encoding)

    def download_to_stream(self, stream, max_connections=1):
        """Download the contents of this blob to a stream.

        :param stream:
            The stream to download to. This can be an open file-handle,
            or any writable stream. The stream must be seekable if the download
            uses more than one parallel connection.
        :returns: The properties of the downloaded blob.
        :rtype: ~azure.storage.blob.models.BlobProperties
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
                self.blob,
                self.initial_offset[0],
                self.initial_offset[1],
                self.require_encryption,
                self.key_encryption_key,
                self.key_resolver_function)
        # Write the content to the user stream
        # Clear blob content since output has been written to user stream
        if content is not None:
            stream.write(content)
        if self._download_complete:
            return self.properties

        end_blob = self.blob_size
        if self.length is not None:
            # Use the length unless it is over the end of the blob
            end_blob = min(self.blob_size, self.length + 1)

        downloader_class = ParallelBlobChunkDownloader if max_connections > 1 else SequentialBlobChunkDownloader
        downloader = downloader_class(
            blob_service=self.service,
            download_size=self.download_size,
            chunk_size=self.config.max_chunk_get_size,
            progress=self.first_get_size,
            start_range=self.initial_range[1] + 1,  # start where the first download ended
            end_range=end_blob,
            stream=stream,
            validate_content=self.validate_content,
            access_conditions=self.access_conditions,
            mod_conditions=self.mod_conditions,
            timeout=self.timeout,
            require_encryption=self.require_encryption,
            key_encryption_key=self.key_encryption_key,
            key_resolver_function=self.key_resolver_function,
            use_location=self.location_mode,
            cls=deserialize_blob_stream,
            **self.request_options)

        if max_connections > 1:
            import concurrent.futures
            executor = concurrent.futures.ThreadPoolExecutor(max_connections)
            list(executor.map(downloader.process_chunk, downloader.get_chunk_offsets()))
        else:
            for chunk in downloader.get_chunk_offsets():
                downloader.process_chunk(chunk)

        return self.properties
