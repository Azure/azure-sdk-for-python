# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from io import (
    BytesIO
)
from os import (
    path,
)

from ..common._common_conversion import (
    _encode_base64,
    _to_str,
    _int_to_str,
    _datetime_to_utc_string,
    _get_content_md5,
)
from ..common._constants import (
    SERVICE_HOST_BASE,
    DEFAULT_PROTOCOL,
)
from ..common._error import (
    _validate_not_none,
    _validate_type_bytes,
    _validate_encryption_required,
    _validate_encryption_unsupported,
    _ERROR_VALUE_NEGATIVE,
    _ERROR_VALUE_SHOULD_BE_STREAM
)
from ..common._http import HTTPRequest
from ..common._serialization import (
    _get_request_body,
    _get_data_bytes_only,
    _get_data_bytes_or_stream_only,
    _add_metadata_headers,
)
from ..common._serialization import (
    _len_plus
)
from ._deserialization import (
    _convert_xml_to_block_list,
    _parse_base_properties,
)
from ._encryption import (
    _encrypt_blob,
    _generate_blob_encryption_data,
)
from ._serialization import (
    _convert_block_list_to_xml,
    _get_path,
    _validate_and_format_range_headers,
)
from ._upload_chunking import (
    _BlockBlobChunkUploader,
    _upload_blob_chunks,
    _upload_blob_substream_blocks,
)
from .baseblobservice import BaseBlobService
from .models import (
    _BlobTypes,
)


class BlockBlobService(BaseBlobService):
    '''
    Block blobs let you upload large blobs efficiently. Block blobs are comprised
    of blocks, each of which is identified by a block ID. You create or modify a
    block blob by writing a set of blocks and committing them by their block IDs.
    Each block can be a different size, up to a maximum of 100 MB, and a block blob
    can include up to 50,000 blocks. The maximum size of a block blob is therefore
    approximately 4.75 TB (100 MB X 50,000 blocks). If you are writing a block
    blob that is no more than 64 MB in size, you can upload it in its entirety with
    a single write operation; see create_blob_from_bytes.

    :ivar int MAX_SINGLE_PUT_SIZE:
        The largest size upload supported in a single put call. This is used by
        the create_blob_from_* methods if the content length is known and is less
        than this value.
    :ivar int MAX_BLOCK_SIZE:
        The size of the blocks put by create_blob_from_* methods if the content
        length is unknown or is larger than MAX_SINGLE_PUT_SIZE. Smaller blocks
        may be put. The maximum block size the service supports is 100MB.
    :ivar int MIN_LARGE_BLOCK_UPLOAD_THRESHOLD:
        The minimum block size at which the the memory-optimized, block upload
        algorithm is considered. This algorithm is only applicable to the create_blob_from_file and
        create_blob_from_stream methods and will prevent the full buffering of blocks.
        In addition to the block size, ContentMD5 validation and Encryption must be disabled as
        these options require the blocks to be buffered.
    '''

    MAX_SINGLE_PUT_SIZE = 64 * 1024 * 1024
    MAX_BLOCK_SIZE = 4 * 1024 * 1024
    MIN_LARGE_BLOCK_UPLOAD_THRESHOLD = 4 * 1024 * 1024 + 1

    def __init__(self, account_name=None, account_key=None, sas_token=None, is_emulated=False,
                 protocol=DEFAULT_PROTOCOL, endpoint_suffix=SERVICE_HOST_BASE, custom_domain=None,
                 request_session=None, connection_string=None, socket_timeout=None, token_credential=None):
        '''
        :param str account_name:
            The storage account name. This is used to authenticate requests
            signed with an account key and to construct the storage endpoint. It
            is required unless a connection string is given, or if a custom
            domain is used with anonymous authentication.
        :param str account_key:
            The storage account key. This is used for shared key authentication.
            If neither account key or sas token is specified, anonymous access
            will be used.
        :param str sas_token:
             A shared access signature token to use to authenticate requests
             instead of the account key. If account key and sas token are both
             specified, account key will be used to sign. If neither are
             specified, anonymous access will be used.
        :param bool is_emulated:
            Whether to use the emulator. Defaults to False. If specified, will
            override all other parameters besides connection string and request
            session.
        :param str protocol:
            The protocol to use for requests. Defaults to https.
        :param str endpoint_suffix:
            The host base component of the url, minus the account name. Defaults
            to Azure (core.windows.net). Override this to use the China cloud
            (core.chinacloudapi.cn).
        :param str custom_domain:
            The custom domain to use. This can be set in the Azure Portal. For
            example, 'www.mydomain.com'.
        :param requests.Session request_session:
            The session object to use for http requests.
        :param str connection_string:
            If specified, this will override all other parameters besides
            request session. See
            http://azure.microsoft.com/en-us/documentation/articles/storage-configure-connection-string/
            for the connection string format.
        :param int socket_timeout:
            If specified, this will override the default socket timeout. The timeout specified is in seconds.
            See DEFAULT_SOCKET_TIMEOUT in _constants.py for the default value.
        :param token_credential:
            A token credential used to authenticate HTTPS requests. The token value
            should be updated before its expiration.
        :type `~azure.storage.common.TokenCredential`
        '''
        self.blob_type = _BlobTypes.BlockBlob
        super(BlockBlobService, self).__init__(
            account_name, account_key, sas_token, is_emulated, protocol, endpoint_suffix,
            custom_domain, request_session, connection_string, socket_timeout, token_credential)

    def put_block(self, container_name, blob_name, block, block_id,
                  validate_content=False, lease_id=None, timeout=None):
        '''
        Creates a new block to be committed as part of a blob.

        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of blob.
        :param block: Content of the block.
        :type block: io.IOBase or bytes
            Content of the block.
        :param str block_id:
            A valid Base64 string value that identifies the block. Prior to
            encoding, the string must be less than or equal to 64 bytes in size.
            For a given blob, the length of the value specified for the blockid
            parameter must be the same size for each block. Note that the Base64
            string must be URL-encoded.
        :param bool validate_content:
            If true, calculates an MD5 hash of the block content. The storage
            service checks the hash of the content that has arrived
            with the hash that was sent. This is primarily valuable for detecting
            bitflips on the wire if using http instead of https as https (the default)
            will already validate. Note that this MD5 hash is not stored with the
            blob.
        :param str lease_id:
            Required if the blob has an active lease.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        '''
        _validate_encryption_unsupported(self.require_encryption, self.key_encryption_key)

        self._put_block(
            container_name,
            blob_name,
            block,
            block_id,
            validate_content=validate_content,
            lease_id=lease_id,
            timeout=timeout
        )

    def put_block_list(
            self, container_name, blob_name, block_list, content_settings=None,
            metadata=None, validate_content=False, lease_id=None, if_modified_since=None,
            if_unmodified_since=None, if_match=None, if_none_match=None,
            timeout=None):
        '''
        Writes a blob by specifying the list of block IDs that make up the blob.
        In order to be written as part of a blob, a block must have been
        successfully written to the server in a prior Put Block operation.

        You can call Put Block List to update a blob by uploading only those
        blocks that have changed, then committing the new and existing blocks
        together. You can do this by specifying whether to commit a block from
        the committed block list or from the uncommitted block list, or to commit
        the most recently uploaded version of the block, whichever list it may
        belong to.

        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of existing blob.
        :param block_list:
            A list of :class:`~azure.storeage.blob.models.BlobBlock` containing the block ids and block state.
        :type block_list: list(:class:`~azure.storage.blob.models.BlobBlock`)
        :param ~azure.storage.blob.models.ContentSettings content_settings:
            ContentSettings object used to set properties on the blob.
        :param metadata:
            Name-value pairs associated with the blob as metadata.
        :type metadata: dict(str, str)
        :param bool validate_content:
            If true, calculates an MD5 hash of the block list content. The storage
            service checks the hash of the block list content that has arrived
            with the hash that was sent. This is primarily valuable for detecting
            bitflips on the wire if using http instead of https as https (the default)
            will already validate. Note that this check is associated with
            the block list content, and not with the content of the blob itself.
        :param str lease_id:
            Required if the blob has an active lease.
        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :param str if_match:
            An ETag value, or the wildcard character (*). Specify this header to perform
            the operation only if the resource's ETag matches the value specified.
        :param str if_none_match:
            An ETag value, or the wildcard character (*). Specify this header
            to perform the operation only if the resource's ETag does not match
            the value specified. Specify the wildcard character (*) to perform
            the operation only if the resource does not exist, and fail the
            operation if it does exist.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: ETag and last modified properties for the updated Block Blob
        :rtype: :class:`~azure.storage.blob.models.ResourceProperties`
        '''

        _validate_encryption_unsupported(self.require_encryption, self.key_encryption_key)

        return self._put_block_list(
            container_name,
            blob_name,
            block_list,
            content_settings=content_settings,
            metadata=metadata,
            validate_content=validate_content,
            lease_id=lease_id,
            if_modified_since=if_modified_since,
            if_unmodified_since=if_unmodified_since,
            if_match=if_match,
            if_none_match=if_none_match,
            timeout=timeout
        )

    def get_block_list(self, container_name, blob_name, snapshot=None,
                       block_list_type=None, lease_id=None, timeout=None):
        '''
        Retrieves the list of blocks that have been uploaded as part of a
        block blob. There are two block lists maintained for a blob:
            Committed Block List:
                The list of blocks that have been successfully committed to a
                given blob with Put Block List.
            Uncommitted Block List:
                The list of blocks that have been uploaded for a blob using
                Put Block, but that have not yet been committed. These blocks
                are stored in Azure in association with a blob, but do not yet
                form part of the blob.

        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of existing blob.
        :param str snapshot:
            Datetime to determine the time to retrieve the blocks.
        :param str block_list_type:
            Specifies whether to return the list of committed blocks, the list
            of uncommitted blocks, or both lists together. Valid values are:
            committed, uncommitted, or all.
        :param str lease_id:
            Required if the blob has an active lease.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: list committed and/or uncommitted blocks for Block Blob
        :rtype: :class:`~azure.storage.blob.models.BlobBlockList`
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        request = HTTPRequest()
        request.method = 'GET'
        request.host_locations = self._get_host_locations(secondary=True)
        request.path = _get_path(container_name, blob_name)
        request.query = {
            'comp': 'blocklist',
            'snapshot': _to_str(snapshot),
            'blocklisttype': _to_str(block_list_type),
            'timeout': _int_to_str(timeout),
        }
        request.headers = {'x-ms-lease-id': _to_str(lease_id)}

        return self._perform_request(request, _convert_xml_to_block_list)

    def put_block_from_url(self, container_name, blob_name, copy_source_url, block_id,
                           source_range_start=None, source_range_end=None,
                           source_content_md5=None, lease_id=None, timeout=None):
        """
        Creates a new block to be committed as part of a blob.

        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of blob.
        :param str copy_source_url:
            The URL of the source data. It can point to any Azure Blob or File, that is either public or has a
            shared access signature attached.
        :param int source_range_start:
            This indicates the start of the range of bytes(inclusive) that has to be taken from the copy source.
        :param int source_range_end:
            This indicates the end of the range of bytes(inclusive) that has to be taken from the copy source.
        :param str block_id:
            A valid Base64 string value that identifies the block. Prior to
            encoding, the string must be less than or equal to 64 bytes in size.
            For a given blob, the length of the value specified for the blockid
            parameter must be the same size for each block. Note that the Base64
            string must be URL-encoded.
        :param str source_content_md5:
            If given, the service will calculate the MD5 hash of the block content and compare against this value.
        :param str lease_id:
            Required if the blob has an active lease.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        """
        _validate_encryption_unsupported(self.require_encryption, self.key_encryption_key)
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        _validate_not_none('copy_source_url', copy_source_url)
        _validate_not_none('block_id', block_id)

        request = HTTPRequest()
        request.method = 'PUT'
        request.host_locations = self._get_host_locations()
        request.path = _get_path(container_name, blob_name)
        request.query = {
            'comp': 'block',
            'blockid': _encode_base64(_to_str(block_id)),
            'timeout': _int_to_str(timeout),
        }
        request.headers = {
            'x-ms-lease-id': _to_str(lease_id),
            'x-ms-copy-source': copy_source_url,
            'x-ms-source-content-md5': source_content_md5,
        }
        _validate_and_format_range_headers(
            request,
            source_range_start,
            source_range_end,
            start_range_required=False,
            end_range_required=False,
            range_header_name="x-ms-source-range"
        )

        self._perform_request(request)

    # ----Convenience APIs-----------------------------------------------------

    def create_blob_from_path(
            self, container_name, blob_name, file_path, content_settings=None,
            metadata=None, validate_content=False, progress_callback=None,
            max_connections=2, lease_id=None, if_modified_since=None,
            if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None):
        '''
        Creates a new blob from a file path, or updates the content of an
        existing blob, with automatic chunking and progress notifications.

        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of blob to create or update.
        :param str file_path:
            Path of the file to upload as the blob content.
        :param ~azure.storage.blob.models.ContentSettings content_settings:
            ContentSettings object used to set blob properties.
        :param metadata:
            Name-value pairs associated with the blob as metadata.
        :type metadata: dict(str, str)
        :param bool validate_content:
            If true, calculates an MD5 hash for each chunk of the blob. The storage
            service checks the hash of the content that has arrived with the hash
            that was sent. This is primarily valuable for detecting bitflips on
            the wire if using http instead of https as https (the default) will
            already validate. Note that this MD5 hash is not stored with the
            blob. Also note that if enabled, the memory-efficient upload algorithm
            will not be used, because computing the MD5 hash requires buffering
            entire blocks, and doing so defeats the purpose of the memory-efficient algorithm.
        :param progress_callback:
            Callback for progress with signature function(current, total) where
            current is the number of bytes transfered so far, and total is the
            size of the blob, or None if the total size is unknown.
        :type progress_callback: func(current, total)
        :param int max_connections:
            Maximum number of parallel connections to use when the blob size exceeds
            64MB.
        :param str lease_id:
            Required if the blob has an active lease.
        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :param str if_match:
            An ETag value, or the wildcard character (*). Specify this header to perform
            the operation only if the resource's ETag matches the value specified.
        :param str if_none_match:
            An ETag value, or the wildcard character (*). Specify this header
            to perform the operation only if the resource's ETag does not match
            the value specified. Specify the wildcard character (*) to perform
            the operation only if the resource does not exist, and fail the
            operation if it does exist.
        :param int timeout:
            The timeout parameter is expressed in seconds. This method may make
            multiple calls to the Azure service and the timeout will apply to
            each call individually.
        :return: ETag and last modified properties for the Block Blob
        :rtype: :class:`~azure.storage.blob.models.ResourceProperties`
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        _validate_not_none('file_path', file_path)

        count = path.getsize(file_path)
        with open(file_path, 'rb') as stream:
            return self.create_blob_from_stream(
                container_name=container_name,
                blob_name=blob_name,
                stream=stream,
                count=count,
                content_settings=content_settings,
                metadata=metadata,
                validate_content=validate_content,
                lease_id=lease_id,
                progress_callback=progress_callback,
                max_connections=max_connections,
                if_modified_since=if_modified_since,
                if_unmodified_since=if_unmodified_since,
                if_match=if_match,
                if_none_match=if_none_match,
                timeout=timeout)

    def create_blob_from_stream(
            self, container_name, blob_name, stream, count=None,
            content_settings=None, metadata=None, validate_content=False,
            progress_callback=None, max_connections=2, lease_id=None,
            if_modified_since=None, if_unmodified_since=None, if_match=None,
            if_none_match=None, timeout=None, use_byte_buffer=False):
        '''
        Creates a new blob from a file/stream, or updates the content of
        an existing blob, with automatic chunking and progress
        notifications.

        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of blob to create or update.
        :param io.IOBase stream:
            Opened file/stream to upload as the blob content.
        :param int count:
            Number of bytes to read from the stream. This is optional, but
            should be supplied for optimal performance.
        :param ~azure.storage.blob.models.ContentSettings content_settings:
            ContentSettings object used to set blob properties.
        :param metadata:
            Name-value pairs associated with the blob as metadata.
        :type metadata: dict(str, str)
        :param bool validate_content:
            If true, calculates an MD5 hash for each chunk of the blob. The storage
            service checks the hash of the content that has arrived with the hash
            that was sent. This is primarily valuable for detecting bitflips on
            the wire if using http instead of https as https (the default) will
            already validate. Note that this MD5 hash is not stored with the
            blob. Also note that if enabled, the memory-efficient upload algorithm
            will not be used, because computing the MD5 hash requires buffering
            entire blocks, and doing so defeats the purpose of the memory-efficient algorithm.
        :param progress_callback:
            Callback for progress with signature function(current, total) where
            current is the number of bytes transfered so far, and total is the
            size of the blob, or None if the total size is unknown.
        :type progress_callback: func(current, total)
        :param int max_connections:
            Maximum number of parallel connections to use when the blob size exceeds
            64MB. Note that parallel upload requires the stream to be seekable.
        :param str lease_id:
            Required if the blob has an active lease.
        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :param str if_match:
            An ETag value, or the wildcard character (*). Specify this header to perform
            the operation only if the resource's ETag matches the value specified.
        :param str if_none_match:
            An ETag value, or the wildcard character (*). Specify this header
            to perform the operation only if the resource's ETag does not match
            the value specified. Specify the wildcard character (*) to perform
            the operation only if the resource does not exist, and fail the
            operation if it does exist.
        :param int timeout:
            The timeout parameter is expressed in seconds. This method may make
            multiple calls to the Azure service and the timeout will apply to
            each call individually.
        :param bool use_byte_buffer:
            If True, this will force usage of the original full block buffering upload path.
            By default, this value is False and will employ a memory-efficient,
            streaming upload algorithm under the following conditions:
            The provided stream is seekable, 'require_encryption' is False, and
            MAX_BLOCK_SIZE >= MIN_LARGE_BLOCK_UPLOAD_THRESHOLD.
            One should consider the drawbacks of using this approach. In order to achieve
            memory-efficiency, a IOBase stream or file-like object is segmented into logical blocks
            using a SubStream wrapper. In order to read the correct data, each SubStream must acquire
            a lock so that it can safely seek to the right position on the shared, underlying stream.
            If max_connections > 1, the concurrency will result in a considerable amount of seeking on
            the underlying stream. For the most common inputs such as a file-like stream object, seeking
            is an inexpensive operation and this is not much of a concern. However, for other variants of streams
            this may not be the case. The trade-off for memory-efficiency must be weighed against the cost of seeking
            with your input stream.
            The SubStream class will attempt to buffer up to 4 MB internally to reduce the amount of
            seek and read calls to the underlying stream. This is particularly beneficial when uploading larger blocks.
        :return: ETag and last modified properties for the Block Blob
        :rtype: :class:`~azure.storage.blob.models.ResourceProperties`
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        _validate_not_none('stream', stream)
        _validate_encryption_required(self.require_encryption, self.key_encryption_key)

        # Adjust count to include padding if we are expected to encrypt.
        adjusted_count = count
        if (self.key_encryption_key is not None) and (adjusted_count is not None):
            adjusted_count += (16 - (count % 16))

        # Do single put if the size is smaller than MAX_SINGLE_PUT_SIZE
        if adjusted_count is not None and (adjusted_count < self.MAX_SINGLE_PUT_SIZE):
            if progress_callback:
                progress_callback(0, count)

            data = stream.read(count)
            resp = self._put_blob(
                container_name=container_name,
                blob_name=blob_name,
                blob=data,
                content_settings=content_settings,
                metadata=metadata,
                validate_content=validate_content,
                lease_id=lease_id,
                if_modified_since=if_modified_since,
                if_unmodified_since=if_unmodified_since,
                if_match=if_match,
                if_none_match=if_none_match,
                timeout=timeout)

            if progress_callback:
                progress_callback(count, count)

            return resp
        else:  # Size is larger than MAX_SINGLE_PUT_SIZE, must upload with multiple put_block calls
            cek, iv, encryption_data = None, None, None

            use_original_upload_path = use_byte_buffer or validate_content or self.require_encryption or \
                                       self.MAX_BLOCK_SIZE < self.MIN_LARGE_BLOCK_UPLOAD_THRESHOLD or \
                                       hasattr(stream, 'seekable') and not stream.seekable() or \
                                       not hasattr(stream, 'seek') or not hasattr(stream, 'tell')

            if use_original_upload_path:
                if self.key_encryption_key:
                    cek, iv, encryption_data = _generate_blob_encryption_data(self.key_encryption_key)

                block_ids = _upload_blob_chunks(
                    blob_service=self,
                    container_name=container_name,
                    blob_name=blob_name,
                    blob_size=count,
                    block_size=self.MAX_BLOCK_SIZE,
                    stream=stream,
                    max_connections=max_connections,
                    progress_callback=progress_callback,
                    validate_content=validate_content,
                    lease_id=lease_id,
                    uploader_class=_BlockBlobChunkUploader,
                    timeout=timeout,
                    content_encryption_key=cek,
                    initialization_vector=iv
                )
            else:
                block_ids = _upload_blob_substream_blocks(
                    blob_service=self,
                    container_name=container_name,
                    blob_name=blob_name,
                    blob_size=count,
                    block_size=self.MAX_BLOCK_SIZE,
                    stream=stream,
                    max_connections=max_connections,
                    progress_callback=progress_callback,
                    validate_content=validate_content,
                    lease_id=lease_id,
                    uploader_class=_BlockBlobChunkUploader,
                    timeout=timeout,
                )

            return self._put_block_list(
                container_name=container_name,
                blob_name=blob_name,
                block_list=block_ids,
                content_settings=content_settings,
                metadata=metadata,
                validate_content=validate_content,
                lease_id=lease_id,
                if_modified_since=if_modified_since,
                if_unmodified_since=if_unmodified_since,
                if_match=if_match,
                if_none_match=if_none_match,
                timeout=timeout,
                encryption_data=encryption_data
            )

    def create_blob_from_bytes(
            self, container_name, blob_name, blob, index=0, count=None,
            content_settings=None, metadata=None, validate_content=False,
            progress_callback=None, max_connections=2, lease_id=None,
            if_modified_since=None, if_unmodified_since=None, if_match=None,
            if_none_match=None, timeout=None):
        '''
        Creates a new blob from an array of bytes, or updates the content
        of an existing blob, with automatic chunking and progress
        notifications.

        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of blob to create or update.
        :param bytes blob:
            Content of blob as an array of bytes.
        :param int index:
            Start index in the array of bytes.
        :param int count:
            Number of bytes to upload. Set to None or negative value to upload
            all bytes starting from index.
        :param ~azure.storage.blob.models.ContentSettings content_settings:
            ContentSettings object used to set blob properties.
        :param metadata:
            Name-value pairs associated with the blob as metadata.
        :type metadata: dict(str, str)
        :param bool validate_content:
            If true, calculates an MD5 hash for each chunk of the blob. The storage
            service checks the hash of the content that has arrived with the hash
            that was sent. This is primarily valuable for detecting bitflips on
            the wire if using http instead of https as https (the default) will
            already validate. Note that this MD5 hash is not stored with the
            blob.
        :param progress_callback:
            Callback for progress with signature function(current, total) where
            current is the number of bytes transfered so far, and total is the
            size of the blob, or None if the total size is unknown.
        :type progress_callback: func(current, total)
        :param int max_connections:
            Maximum number of parallel connections to use when the blob size exceeds
            64MB.
        :param str lease_id:
            Required if the blob has an active lease.
        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :param str if_match:
            An ETag value, or the wildcard character (*). Specify this header to perform
            the operation only if the resource's ETag matches the value specified.
        :param str if_none_match:
            An ETag value, or the wildcard character (*). Specify this header
            to perform the operation only if the resource's ETag does not match
            the value specified. Specify the wildcard character (*) to perform
            the operation only if the resource does not exist, and fail the
            operation if it does exist.
        :param int timeout:
            The timeout parameter is expressed in seconds. This method may make
            multiple calls to the Azure service and the timeout will apply to
            each call individually.
        :return: ETag and last modified properties for the Block Blob
        :rtype: :class:`~azure.storage.blob.models.ResourceProperties`
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        _validate_not_none('blob', blob)
        _validate_not_none('index', index)
        _validate_type_bytes('blob', blob)

        if index < 0:
            raise IndexError(_ERROR_VALUE_NEGATIVE.format('index'))

        if count is None or count < 0:
            count = len(blob) - index

        stream = BytesIO(blob)
        stream.seek(index)

        return self.create_blob_from_stream(
            container_name=container_name,
            blob_name=blob_name,
            stream=stream,
            count=count,
            content_settings=content_settings,
            metadata=metadata,
            validate_content=validate_content,
            progress_callback=progress_callback,
            max_connections=max_connections,
            lease_id=lease_id,
            if_modified_since=if_modified_since,
            if_unmodified_since=if_unmodified_since,
            if_match=if_match,
            if_none_match=if_none_match,
            timeout=timeout,
            use_byte_buffer=True
        )

    def create_blob_from_text(
            self, container_name, blob_name, text, encoding='utf-8',
            content_settings=None, metadata=None, validate_content=False,
            progress_callback=None, max_connections=2, lease_id=None,
            if_modified_since=None, if_unmodified_since=None, if_match=None,
            if_none_match=None, timeout=None):
        '''
        Creates a new blob from str/unicode, or updates the content of an
        existing blob, with automatic chunking and progress notifications.

        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of blob to create or update.
        :param str text:
            Text to upload to the blob.
        :param str encoding:
            Python encoding to use to convert the text to bytes.
        :param ~azure.storage.blob.models.ContentSettings content_settings:
            ContentSettings object used to set blob properties.
        :param metadata:
            Name-value pairs associated with the blob as metadata.
        :type metadata: dict(str, str)
        :param bool validate_content:
            If true, calculates an MD5 hash for each chunk of the blob. The storage
            service checks the hash of the content that has arrived with the hash
            that was sent. This is primarily valuable for detecting bitflips on
            the wire if using http instead of https as https (the default) will
            already validate. Note that this MD5 hash is not stored with the
            blob.
        :param progress_callback:
            Callback for progress with signature function(current, total) where
            current is the number of bytes transfered so far, and total is the
            size of the blob, or None if the total size is unknown.
        :type progress_callback: func(current, total)
        :param int max_connections:
            Maximum number of parallel connections to use when the blob size exceeds
            64MB.
        :param str lease_id:
            Required if the blob has an active lease.
        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :param str if_match:
            An ETag value, or the wildcard character (*). Specify this header to perform
            the operation only if the resource's ETag matches the value specified.
        :param str if_none_match:
            An ETag value, or the wildcard character (*). Specify this header
            to perform the operation only if the resource's ETag does not match
            the value specified. Specify the wildcard character (*) to perform
            the operation only if the resource does not exist, and fail the
            operation if it does exist.
        :param int timeout:
            The timeout parameter is expressed in seconds. This method may make
            multiple calls to the Azure service and the timeout will apply to
            each call individually.
        :return: ETag and last modified properties for the Block Blob
        :rtype: :class:`~azure.storage.blob.models.ResourceProperties`
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        _validate_not_none('text', text)

        if not isinstance(text, bytes):
            _validate_not_none('encoding', encoding)
            text = text.encode(encoding)

        return self.create_blob_from_bytes(
            container_name=container_name,
            blob_name=blob_name,
            blob=text,
            index=0,
            count=len(text),
            content_settings=content_settings,
            metadata=metadata,
            validate_content=validate_content,
            lease_id=lease_id,
            progress_callback=progress_callback,
            max_connections=max_connections,
            if_modified_since=if_modified_since,
            if_unmodified_since=if_unmodified_since,
            if_match=if_match,
            if_none_match=if_none_match,
            timeout=timeout)

    def set_standard_blob_tier(
            self, container_name, blob_name, standard_blob_tier, timeout=None):
        '''
        Sets the block blob tiers on the blob. This API is only supported for block blobs on standard storage accounts.

        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of blob to update.
        :param StandardBlobTier standard_blob_tier:
            A standard blob tier value to set the blob to. For this version of the library,
            this is only applicable to block blobs on standard storage accounts.
        :param int timeout:
            The timeout parameter is expressed in seconds. This method may make
            multiple calls to the Azure service and the timeout will apply to
            each call individually.
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        _validate_not_none('standard_blob_tier', standard_blob_tier)

        request = HTTPRequest()
        request.method = 'PUT'
        request.host_locations = self._get_host_locations()
        request.path = _get_path(container_name, blob_name)
        request.query = {
            'comp': 'tier',
            'timeout': _int_to_str(timeout),
        }
        request.headers = {
            'x-ms-access-tier': _to_str(standard_blob_tier)
        }

        self._perform_request(request)

    def copy_blob(self, container_name, blob_name, copy_source,
                  metadata=None, source_if_modified_since=None,
                  source_if_unmodified_since=None, source_if_match=None,
                  source_if_none_match=None, destination_if_modified_since=None,
                  destination_if_unmodified_since=None, destination_if_match=None,
                  destination_if_none_match=None, destination_lease_id=None,
                  source_lease_id=None, timeout=None, requires_sync=None):

        '''
        Copies a blob. This operation returns a copy operation
        properties object. The copy operation may be configured to either be an
        asynchronous, best-effort operation, or a synchronous operation.

        The source must be a block blob if requires_sync is true. Any existing
        destination blob will be overwritten. The destination blob cannot be
        modified while a copy operation is in progress.

        When copying from a block blob, all committed blocks and their block IDs are
        copied. Uncommitted blocks are not copied. At the end of the copy operation,
        the destination blob will have the same committed block count as the source.

        You can call get_blob_properties on the destination blob to check the status
        of the copy operation. The final blob will be committed when the copy completes.

        :param str container_name:
        Name of the destination container. The container must exist.
        :param str blob_name:
        Name of the destination blob. If the destination blob exists, it will
        be overwritten. Otherwise, it will be created.
        :param str copy_source:
        A URL of up to 2 KB in length that specifies an Azure file or blob.
        The value should be URL-encoded as it would appear in a request URI.
        If the source is in another account, the source must either be public
        or must be authenticated via a shared access signature. If the source
        is public, no authentication is required.
        Examples:
        https://myaccount.blob.core.windows.net/mycontainer/myblob
        https://myaccount.blob.core.windows.net/mycontainer/myblob?snapshot=<DateTime>
        https://otheraccount.blob.core.windows.net/mycontainer/myblob?sastoken
        :param metadata:
        Name-value pairs associated with the blob as metadata. If no name-value
        pairs are specified, the operation will copy the metadata from the
        source blob or file to the destination blob. If one or more name-value
        pairs are specified, the destination blob is created with the specified
        metadata, and metadata is not copied from the source blob or file.
        :type metadata: dict(str, str)
        :param datetime source_if_modified_since:
        A DateTime value. Azure expects the date value passed in to be UTC.
        If timezone is included, any non-UTC datetimes will be converted to UTC.
        If a date is passed in without timezone info, it is assumed to be UTC.
        Specify this conditional header to copy the blob only if the source
        blob has been modified since the specified date/time.
        :param datetime source_if_unmodified_since:
        A DateTime value. Azure expects the date value passed in to be UTC.
        If timezone is included, any non-UTC datetimes will be converted to UTC.
        If a date is passed in without timezone info, it is assumed to be UTC.
        Specify this conditional header to copy the blob only if the source blob
        has not been modified since the specified date/time.
        :param ETag source_if_match:
        An ETag value, or the wildcard character (*). Specify this conditional
        header to copy the source blob only if its ETag matches the value
        specified. If the ETag values do not match, the Blob service returns
        status code 412 (Precondition Failed). This header cannot be specified
        if the source is an Azure File.
        :param ETag source_if_none_match:
        An ETag value, or the wildcard character (*). Specify this conditional
        header to copy the blob only if its ETag does not match the value
        specified. If the values are identical, the Blob service returns status
        code 412 (Precondition Failed). This header cannot be specified if the
        source is an Azure File.
        :param datetime destination_if_modified_since:
        A DateTime value. Azure expects the date value passed in to be UTC.
        If timezone is included, any non-UTC datetimes will be converted to UTC.
        If a date is passed in without timezone info, it is assumed to be UTC.
        Specify this conditional header to copy the blob only
        if the destination blob has been modified since the specified date/time.
        If the destination blob has not been modified, the Blob service returns
        status code 412 (Precondition Failed).
        :param datetime destination_if_unmodified_since:
        A DateTime value. Azure expects the date value passed in to be UTC.
        If timezone is included, any non-UTC datetimes will be converted to UTC.
        If a date is passed in without timezone info, it is assumed to be UTC.
        Specify this conditional header to copy the blob only
        if the destination blob has not been modified since the specified
        date/time. If the destination blob has been modified, the Blob service
        returns status code 412 (Precondition Failed).
        :param ETag destination_if_match:
        An ETag value, or the wildcard character (*). Specify an ETag value for
        this conditional header to copy the blob only if the specified ETag value
        matches the ETag value for an existing destination blob. If the ETag for
        the destination blob does not match the ETag specified for If-Match, the
        Blob service returns status code 412 (Precondition Failed).
        :param ETag destination_if_none_match:
        An ETag value, or the wildcard character (*). Specify an ETag value for
        this conditional header to copy the blob only if the specified ETag value
        does not match the ETag value for the destination blob. Specify the wildcard
        character (*) to perform the operation only if the destination blob does not
        exist. If the specified condition isn't met, the Blob service returns status
        code 412 (Precondition Failed).
        :param str destination_lease_id:
        The lease ID specified for this header must match the lease ID of the
        destination blob. If the request does not include the lease ID or it is not
        valid, the operation fails with status code 412 (Precondition Failed).
        :param str source_lease_id:
        Specify this to perform the Copy Blob operation only if
        the lease ID given matches the active lease ID of the source blob.
        :param int timeout:
        The timeout parameter is expressed in seconds.
        :param bool requires_sync:
        Enforces that the service will not return a response until the copy is complete.
        :return: Copy operation properties such as status, source, and ID.
        :rtype: :class:`~azure.storage.blob.models.CopyProperties`
        '''

        return self._copy_blob(container_name, blob_name, copy_source,
                               metadata,
                               premium_page_blob_tier=None,
                               source_if_modified_since=source_if_modified_since,
                               source_if_unmodified_since=source_if_unmodified_since,
                               source_if_match=source_if_match,
                               source_if_none_match=source_if_none_match,
                               destination_if_modified_since=destination_if_modified_since,
                               destination_if_unmodified_since=destination_if_unmodified_since,
                               destination_if_match=destination_if_match,
                               destination_if_none_match=destination_if_none_match,
                               destination_lease_id=destination_lease_id,
                               source_lease_id=source_lease_id, timeout=timeout,
                               incremental_copy=False,
                               requires_sync=requires_sync)

    # -----Helper methods------------------------------------
    def _put_blob(self, container_name, blob_name, blob, content_settings=None,
                  metadata=None, validate_content=False, lease_id=None, if_modified_since=None,
                  if_unmodified_since=None, if_match=None, if_none_match=None,
                  timeout=None):
        '''
        Creates a blob or updates an existing blob.

        See create_blob_from_* for high level
        functions that handle the creation and upload of large blobs with
        automatic chunking and progress notifications.

        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of blob to create or update.
        :param bytes blob:
            Content of blob as bytes (size < 64MB). For larger size, you
            must call put_block and put_block_list to set content of blob.
        :param ~azure.storage.blob.models.ContentSettings content_settings:
            ContentSettings object used to set properties on the blob.
        :param metadata:
            Name-value pairs associated with the blob as metadata.
        :param bool validate_content:
            If true, calculates an MD5 hash of the blob content. The storage
            service checks the hash of the content that has arrived
            with the hash that was sent. This is primarily valuable for detecting
            bitflips on the wire if using http instead of https as https (the default)
            will already validate. Note that this MD5 hash is not stored with the
            blob.
        :param str lease_id:
            Required if the blob has an active lease.
        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :param str if_match:
            An ETag value, or the wildcard character (*). Specify this header to perform
            the operation only if the resource's ETag matches the value specified.
        :param str if_none_match:
            An ETag value, or the wildcard character (*). Specify this header
            to perform the operation only if the resource's ETag does not match
            the value specified. Specify the wildcard character (*) to perform
            the operation only if the resource does not exist, and fail the
            operation if it does exist.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: ETag and last modified properties for the new Block Blob
        :rtype: :class:`~azure.storage.blob.models.ResourceProperties`
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        _validate_encryption_required(self.require_encryption, self.key_encryption_key)

        request = HTTPRequest()
        request.method = 'PUT'
        request.host_locations = self._get_host_locations()
        request.path = _get_path(container_name, blob_name)
        request.query = {'timeout': _int_to_str(timeout)}
        request.headers = {
            'x-ms-blob-type': _to_str(self.blob_type),
            'x-ms-lease-id': _to_str(lease_id),
            'If-Modified-Since': _datetime_to_utc_string(if_modified_since),
            'If-Unmodified-Since': _datetime_to_utc_string(if_unmodified_since),
            'If-Match': _to_str(if_match),
            'If-None-Match': _to_str(if_none_match)
        }
        _add_metadata_headers(metadata, request)
        if content_settings is not None:
            request.headers.update(content_settings._to_headers())
        blob = _get_data_bytes_only('blob', blob)
        if self.key_encryption_key:
            encryption_data, blob = _encrypt_blob(blob, self.key_encryption_key)
            request.headers['x-ms-meta-encryptiondata'] = encryption_data
        request.body = blob

        if validate_content:
            computed_md5 = _get_content_md5(request.body)
            request.headers['Content-MD5'] = _to_str(computed_md5)

        return self._perform_request(request, _parse_base_properties)

    def _put_block(self, container_name, blob_name, block, block_id,
                   validate_content=False, lease_id=None, timeout=None):
        '''
        See put_block for more details. This helper method
        allows for encryption or other such special behavior because
        it is safely handled by the library. These behaviors are
        prohibited in the public version of this function.
        '''

        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        _validate_not_none('block', block)
        _validate_not_none('block_id', block_id)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host_locations = self._get_host_locations()
        request.path = _get_path(container_name, blob_name)
        request.query = {
            'comp': 'block',
            'blockid': _encode_base64(_to_str(block_id)),
            'timeout': _int_to_str(timeout),
        }
        request.headers = {
            'x-ms-lease-id': _to_str(lease_id)
        }
        request.body = _get_data_bytes_or_stream_only('block', block)
        if hasattr(request.body, 'read'):
            if _len_plus(request.body) is None:
                try:
                    data = b''
                    for chunk in iter(lambda: request.body.read(4096), b""):
                        data += chunk
                    request.body = data
                except AttributeError:
                    raise ValueError(_ERROR_VALUE_SHOULD_BE_STREAM.format('request.body'))

        if validate_content:
            computed_md5 = _get_content_md5(request.body)
            request.headers['Content-MD5'] = _to_str(computed_md5)

        self._perform_request(request)

    def _put_block_list(
            self, container_name, blob_name, block_list, content_settings=None,
            metadata=None, validate_content=False, lease_id=None, if_modified_since=None,
            if_unmodified_since=None, if_match=None, if_none_match=None,
            timeout=None, encryption_data=None):
        '''
        See put_block_list for more details. This helper method
        allows for encryption or other such special behavior because
        it is safely handled by the library. These behaviors are
        prohibited in the public version of this function.
        :param str encryption_data:
            A JSON formatted string containing the encryption metadata generated for this 
            blob if it was encrypted all at once upon upload. This should only be passed
            in by internal methods.
        '''

        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        _validate_not_none('block_list', block_list)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host_locations = self._get_host_locations()
        request.path = _get_path(container_name, blob_name)
        request.query = {
            'comp': 'blocklist',
            'timeout': _int_to_str(timeout),
        }
        request.headers = {
            'x-ms-lease-id': _to_str(lease_id),
            'If-Modified-Since': _datetime_to_utc_string(if_modified_since),
            'If-Unmodified-Since': _datetime_to_utc_string(if_unmodified_since),
            'If-Match': _to_str(if_match),
            'If-None-Match': _to_str(if_none_match),
        }
        _add_metadata_headers(metadata, request)
        if content_settings is not None:
            request.headers.update(content_settings._to_headers())
        request.body = _get_request_body(
            _convert_block_list_to_xml(block_list))

        if validate_content:
            computed_md5 = _get_content_md5(request.body)
            request.headers['Content-MD5'] = _to_str(computed_md5)

        if encryption_data is not None:
            request.headers['x-ms-meta-encryptiondata'] = encryption_data

        return self._perform_request(request, _parse_base_properties)
