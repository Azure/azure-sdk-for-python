# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import sys
from os import path

from ..common._common_conversion import (
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
    _validate_encryption_unsupported,
    _ERROR_VALUE_NEGATIVE,
)
from ..common._http import HTTPRequest
from ..common._serialization import (
    _get_data_bytes_only,
    _add_metadata_headers,
)
from ._deserialization import (
    _parse_append_block,
    _parse_base_properties,
)
from ._serialization import (
    _get_path,
    _validate_and_format_range_headers,
)
from ._upload_chunking import (
    _AppendBlobChunkUploader,
    _upload_blob_chunks,
)
from .baseblobservice import BaseBlobService
from .models import (
    _BlobTypes,
    ResourceProperties
)

if sys.version_info >= (3,):
    from io import BytesIO
else:
    from cStringIO import StringIO as BytesIO


class AppendBlobService(BaseBlobService):
    '''
    An append blob is comprised of blocks and is optimized for append operations.
    When you modify an append blob, blocks are added to the end of the blob only,
    via the append_block operation. Updating or deleting of existing blocks is not
    supported. Unlike a block blob, an append blob does not expose its block IDs. 

    Each block in an append blob can be a different size, up to a maximum of 4 MB,
    and an append blob can include up to 50,000 blocks. The maximum size of an
    append blob is therefore slightly more than 195 GB (4 MB X 50,000 blocks).

    :ivar int MAX_BLOCK_SIZE: 
        The size of the blocks put by append_blob_from_* methods. Smaller blocks 
        may be put if there is less data provided. The maximum block size the service 
        supports is 4MB.
    '''
    MAX_BLOCK_SIZE = 4 * 1024 * 1024

    def __init__(self, account_name=None, account_key=None, sas_token=None, is_emulated=False,
                 protocol=DEFAULT_PROTOCOL, endpoint_suffix=SERVICE_HOST_BASE, custom_domain=None, request_session=None,
                 connection_string=None, socket_timeout=None, token_credential=None):
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
        self.blob_type = _BlobTypes.AppendBlob
        super(AppendBlobService, self).__init__(
            account_name, account_key, sas_token, is_emulated, protocol, endpoint_suffix,
            custom_domain, request_session, connection_string, socket_timeout, token_credential)

    def create_blob(self, container_name, blob_name, content_settings=None,
                    metadata=None, lease_id=None,
                    if_modified_since=None, if_unmodified_since=None,
                    if_match=None, if_none_match=None, timeout=None):
        '''
        Creates a blob or overrides an existing blob. Use if_none_match=* to
        prevent overriding an existing blob. 

        See create_blob_from_* for high level
        functions that handle the creation and upload of large blobs with
        automatic chunking and progress notifications.

        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of blob to create or update.
        :param ~azure.storage.blob.models.ContentSettings content_settings:
            ContentSettings object used to set blob properties.
        :param metadata:
            Name-value pairs associated with the blob as metadata.
        :type metadata: dict(str, str)
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
            An ETag value, or the wildcard character (*). Specify this header to
            perform the operation only if the resource's ETag matches the value specified.
        :param str if_none_match:
            An ETag value, or the wildcard character (*). Specify this header
            to perform the operation only if the resource's ETag does not match
            the value specified. Specify the wildcard character (*) to perform
            the operation only if the resource does not exist, and fail the
            operation if it does exist.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: ETag and last modified properties for the updated Append Blob
        :rtype: :class:`~azure.storage.blob.models.ResourceProperties`
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        _validate_encryption_unsupported(self.require_encryption, self.key_encryption_key)

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

        return self._perform_request(request, _parse_base_properties)

    def append_block(self, container_name, blob_name, block,
                     validate_content=False, maxsize_condition=None,
                     appendpos_condition=None,
                     lease_id=None, if_modified_since=None,
                     if_unmodified_since=None, if_match=None,
                     if_none_match=None, timeout=None):
        '''
        Commits a new block of data to the end of an existing append blob.
        
        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of existing blob.
        :param bytes block:
            Content of the block in bytes.
        :param bool validate_content:
            If true, calculates an MD5 hash of the block content. The storage 
            service checks the hash of the content that has arrived
            with the hash that was sent. This is primarily valuable for detecting 
            bitflips on the wire if using http instead of https as https (the default) 
            will already validate. Note that this MD5 hash is not stored with the 
            blob.
        :param int maxsize_condition:
            Optional conditional header. The max length in bytes permitted for
            the append blob. If the Append Block operation would cause the blob
            to exceed that limit or if the blob size is already greater than the
            value specified in this header, the request will fail with
            MaxBlobSizeConditionNotMet error (HTTP status code 412 - Precondition Failed).
        :param int appendpos_condition:
            Optional conditional header, used only for the Append Block operation.
            A number indicating the byte offset to compare. Append Block will
            succeed only if the append position is equal to this number. If it
            is not, the request will fail with the
            AppendPositionConditionNotMet error
            (HTTP status code 412 - Precondition Failed).
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
        :return:
            ETag, last modified, append offset, and committed block count 
            properties for the updated Append Blob
        :rtype: :class:`~azure.storage.blob.models.AppendBlockProperties`
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        _validate_not_none('block', block)
        _validate_encryption_unsupported(self.require_encryption, self.key_encryption_key)

        request = HTTPRequest()
        request.method = 'PUT'
        request.host_locations = self._get_host_locations()
        request.path = _get_path(container_name, blob_name)
        request.query = {
            'comp': 'appendblock',
            'timeout': _int_to_str(timeout),
        }
        request.headers = {
            'x-ms-blob-condition-maxsize': _to_str(maxsize_condition),
            'x-ms-blob-condition-appendpos': _to_str(appendpos_condition),
            'x-ms-lease-id': _to_str(lease_id),
            'If-Modified-Since': _datetime_to_utc_string(if_modified_since),
            'If-Unmodified-Since': _datetime_to_utc_string(if_unmodified_since),
            'If-Match': _to_str(if_match),
            'If-None-Match': _to_str(if_none_match)
        }
        request.body = _get_data_bytes_only('block', block)

        if validate_content:
            computed_md5 = _get_content_md5(request.body)
            request.headers['Content-MD5'] = _to_str(computed_md5)

        return self._perform_request(request, _parse_append_block)

    def append_block_from_url(self, container_name, blob_name, copy_source_url, source_range_start=None,
                              source_range_end=None, source_content_md5=None, source_if_modified_since=None,
                              source_if_unmodified_since=None, source_if_match=None,
                              source_if_none_match=None, maxsize_condition=None,
                              appendpos_condition=None, lease_id=None, if_modified_since=None,
                              if_unmodified_since=None, if_match=None,
                              if_none_match=None, timeout=None):
        """
        Creates a new block to be committed as part of a blob, where the contents are read from a source url.

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
        :param str source_content_md5:
            If given, the service will calculate the MD5 hash of the block content and compare against this value.
        :param datetime source_if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only
            if the source resource has been modified since the specified time.
        :param datetime source_if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the source resource has not been modified since the specified date/time.
        :param str source_if_match:
            An ETag value, or the wildcard character (*). Specify this header to perform
            the operation only if the source resource's ETag matches the value specified.
        :param str source_if_none_match:
            An ETag value, or the wildcard character (*). Specify this header
            to perform the operation only if the source resource's ETag does not match
            the value specified. Specify the wildcard character (*) to perform
            the operation only if the source resource does not exist, and fail the
            operation if it does exist.
        :param int maxsize_condition:
            Optional conditional header. The max length in bytes permitted for
            the append blob. If the Append Block operation would cause the blob
            to exceed that limit or if the blob size is already greater than the
            value specified in this header, the request will fail with
            MaxBlobSizeConditionNotMet error (HTTP status code 412 - Precondition Failed).
        :param int appendpos_condition:
            Optional conditional header, used only for the Append Block operation.
            A number indicating the byte offset to compare. Append Block will
            succeed only if the append position is equal to this number. If it
            is not, the request will fail with the
            AppendPositionConditionNotMet error
            (HTTP status code 412 - Precondition Failed).
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
        """
        _validate_encryption_unsupported(self.require_encryption, self.key_encryption_key)
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        _validate_not_none('copy_source_url', copy_source_url)

        request = HTTPRequest()
        request.method = 'PUT'
        request.host_locations = self._get_host_locations()
        request.path = _get_path(container_name, blob_name)
        request.query = {
            'comp': 'appendblock',
            'timeout': _int_to_str(timeout),
        }
        request.headers = {
            'x-ms-copy-source': copy_source_url,
            'x-ms-source-content-md5': source_content_md5,
            'x-ms-source-if-Modified-Since': _datetime_to_utc_string(source_if_modified_since),
            'x-ms-source-if-Unmodified-Since': _datetime_to_utc_string(source_if_unmodified_since),
            'x-ms-source-if-Match': _to_str(source_if_match),
            'x-ms-source-if-None-Match': _to_str(source_if_none_match),
            'x-ms-blob-condition-maxsize': _to_str(maxsize_condition),
            'x-ms-blob-condition-appendpos': _to_str(appendpos_condition),
            'x-ms-lease-id': _to_str(lease_id),
            'If-Modified-Since': _datetime_to_utc_string(if_modified_since),
            'If-Unmodified-Since': _datetime_to_utc_string(if_unmodified_since),
            'If-Match': _to_str(if_match),
            'If-None-Match': _to_str(if_none_match)
        }

        _validate_and_format_range_headers(request, source_range_start, source_range_end,
                                           start_range_required=False,
                                           end_range_required=False,
                                           range_header_name="x-ms-source-range")

        return self._perform_request(request, _parse_append_block)

    # ----Convenience APIs----------------------------------------------

    def append_blob_from_path(
            self, container_name, blob_name, file_path, validate_content=False,
            maxsize_condition=None, progress_callback=None, lease_id=None, timeout=None,
            if_modified_since=None, if_unmodified_since=None, if_match=None,
            if_none_match=None):
        '''
        Appends to the content of an existing blob from a file path, with automatic
        chunking and progress notifications.

        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of blob to create or update.
        :param str file_path:
            Path of the file to upload as the blob content.
        :param bool validate_content:
            If true, calculates an MD5 hash for each chunk of the blob. The storage 
            service checks the hash of the content that has arrived with the hash 
            that was sent. This is primarily valuable for detecting bitflips on 
            the wire if using http instead of https as https (the default) will 
            already validate. Note that this MD5 hash is not stored with the 
            blob.
        :param int maxsize_condition:
            Optional conditional header. The max length in bytes permitted for
            the append blob. If the Append Block operation would cause the blob
            to exceed that limit or if the blob size is already greater than the
            value specified in this header, the request will fail with
            MaxBlobSizeConditionNotMet error (HTTP status code 412 - Precondition Failed).
        :param progress_callback:
            Callback for progress with signature function(current, total) where
            current is the number of bytes transfered so far, and total is the
            size of the blob, or None if the total size is unknown.
        :type progress_callback: func(current, total)
        :param str lease_id:
            Required if the blob has an active lease.
        :param int timeout:
            The timeout parameter is expressed in seconds. This method may make 
            multiple calls to the Azure service and the timeout will apply to 
            each call individually.
        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetime will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetime will be converted to UTC.
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
        :return: ETag and last modified properties for the Append Blob
        :rtype: :class:`~azure.storage.blob.models.ResourceProperties`
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        _validate_not_none('file_path', file_path)
        _validate_encryption_unsupported(self.require_encryption, self.key_encryption_key)

        count = path.getsize(file_path)
        with open(file_path, 'rb') as stream:
            return self.append_blob_from_stream(
                container_name,
                blob_name,
                stream,
                count=count,
                validate_content=validate_content,
                maxsize_condition=maxsize_condition,
                progress_callback=progress_callback,
                lease_id=lease_id,
                timeout=timeout,
                if_modified_since=if_modified_since,
                if_unmodified_since=if_unmodified_since,
                if_match=if_match,
                if_none_match=if_none_match)

    def append_blob_from_bytes(
            self, container_name, blob_name, blob, index=0, count=None,
            validate_content=False, maxsize_condition=None, progress_callback=None,
            lease_id=None, timeout=None, if_modified_since=None, if_unmodified_since=None, if_match=None,
            if_none_match=None):
        '''
        Appends to the content of an existing blob from an array of bytes, with
        automatic chunking and progress notifications.

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
        :param bool validate_content:
            If true, calculates an MD5 hash for each chunk of the blob. The storage 
            service checks the hash of the content that has arrived with the hash 
            that was sent. This is primarily valuable for detecting bitflips on 
            the wire if using http instead of https as https (the default) will 
            already validate. Note that this MD5 hash is not stored with the 
            blob.
        :param int maxsize_condition:
            Optional conditional header. The max length in bytes permitted for
            the append blob. If the Append Block operation would cause the blob
            to exceed that limit or if the blob size is already greater than the
            value specified in this header, the request will fail with
            MaxBlobSizeConditionNotMet error (HTTP status code 412 - Precondition Failed).
        :param progress_callback:
            Callback for progress with signature function(current, total) where
            current is the number of bytes transfered so far, and total is the
            size of the blob, or None if the total size is unknown.
        :type progress_callback: func(current, total)
        :param str lease_id:
            Required if the blob has an active lease.
        :param int timeout:
            The timeout parameter is expressed in seconds. This method may make 
            multiple calls to the Azure service and the timeout will apply to 
            each call individually.
        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetime will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetime will be converted to UTC.
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
        :return: ETag and last modified properties for the Append Blob
        :rtype: :class:`~azure.storage.blob.models.ResourceProperties`
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        _validate_not_none('blob', blob)
        _validate_not_none('index', index)
        _validate_type_bytes('blob', blob)
        _validate_encryption_unsupported(self.require_encryption, self.key_encryption_key)

        if index < 0:
            raise IndexError(_ERROR_VALUE_NEGATIVE.format('index'))

        if count is None or count < 0:
            count = len(blob) - index

        stream = BytesIO(blob)
        stream.seek(index)

        return self.append_blob_from_stream(
            container_name,
            blob_name,
            stream,
            count=count,
            validate_content=validate_content,
            maxsize_condition=maxsize_condition,
            lease_id=lease_id,
            progress_callback=progress_callback,
            timeout=timeout,
            if_modified_since=if_modified_since,
            if_unmodified_since=if_unmodified_since,
            if_match=if_match,
            if_none_match=if_none_match)

    def append_blob_from_text(
            self, container_name, blob_name, text, encoding='utf-8',
            validate_content=False, maxsize_condition=None, progress_callback=None,
            lease_id=None, timeout=None, if_modified_since=None, if_unmodified_since=None, if_match=None,
            if_none_match=None):
        '''
        Appends to the content of an existing blob from str/unicode, with
        automatic chunking and progress notifications.

        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of blob to create or update.
        :param str text:
            Text to upload to the blob.
        :param str encoding:
            Python encoding to use to convert the text to bytes.
        :param bool validate_content:
            If true, calculates an MD5 hash for each chunk of the blob. The storage 
            service checks the hash of the content that has arrived with the hash 
            that was sent. This is primarily valuable for detecting bitflips on 
            the wire if using http instead of https as https (the default) will 
            already validate. Note that this MD5 hash is not stored with the 
            blob.
        :param int maxsize_condition:
            Optional conditional header. The max length in bytes permitted for
            the append blob. If the Append Block operation would cause the blob
            to exceed that limit or if the blob size is already greater than the
            value specified in this header, the request will fail with
            MaxBlobSizeConditionNotMet error (HTTP status code 412 - Precondition Failed).
        :param progress_callback:
            Callback for progress with signature function(current, total) where
            current is the number of bytes transfered so far, and total is the
            size of the blob, or None if the total size is unknown.
        :type progress_callback: func(current, total)
        :param str lease_id:
            Required if the blob has an active lease.
        :param int timeout:
            The timeout parameter is expressed in seconds. This method may make 
            multiple calls to the Azure service and the timeout will apply to 
            each call individually.
        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetime will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetime will be converted to UTC.
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
        :return: ETag and last modified properties for the Append Blob
        :rtype: :class:`~azure.storage.blob.models.ResourceProperties`
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        _validate_not_none('text', text)
        _validate_encryption_unsupported(self.require_encryption, self.key_encryption_key)

        if not isinstance(text, bytes):
            _validate_not_none('encoding', encoding)
            text = text.encode(encoding)

        return self.append_blob_from_bytes(
            container_name,
            blob_name,
            text,
            index=0,
            count=len(text),
            validate_content=validate_content,
            maxsize_condition=maxsize_condition,
            lease_id=lease_id,
            progress_callback=progress_callback,
            timeout=timeout,
            if_modified_since=if_modified_since,
            if_unmodified_since=if_unmodified_since,
            if_match=if_match,
            if_none_match=if_none_match)

    def append_blob_from_stream(
            self, container_name, blob_name, stream, count=None,
            validate_content=False, maxsize_condition=None, progress_callback=None,
            lease_id=None, timeout=None, if_modified_since=None, if_unmodified_since=None, if_match=None,
            if_none_match=None):
        '''
        Appends to the content of an existing blob from a file/stream, with
        automatic chunking and progress notifications.

        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of blob to create or update.
        :param io.IOBase stream:
            Opened stream to upload as the blob content.
        :param int count:
            Number of bytes to read from the stream. This is optional, but
            should be supplied for optimal performance.
        :param bool validate_content:
            If true, calculates an MD5 hash for each chunk of the blob. The storage 
            service checks the hash of the content that has arrived with the hash 
            that was sent. This is primarily valuable for detecting bitflips on 
            the wire if using http instead of https as https (the default) will 
            already validate. Note that this MD5 hash is not stored with the 
            blob.
        :param int maxsize_condition:
            Conditional header. The max length in bytes permitted for
            the append blob. If the Append Block operation would cause the blob
            to exceed that limit or if the blob size is already greater than the
            value specified in this header, the request will fail with
            MaxBlobSizeConditionNotMet error (HTTP status code 412 - Precondition Failed).
        :param progress_callback:
            Callback for progress with signature function(current, total) where
            current is the number of bytes transfered so far, and total is the
            size of the blob, or None if the total size is unknown.
        :type progress_callback: func(current, total)
        :param str lease_id:
            Required if the blob has an active lease.
        :param int timeout:
            The timeout parameter is expressed in seconds. This method may make 
            multiple calls to the Azure service and the timeout will apply to 
            each call individually.
        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetime will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetime will be converted to UTC.
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
        :return: ETag and last modified properties for the Append Blob
        :rtype: :class:`~azure.storage.blob.models.ResourceProperties`
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        _validate_not_none('stream', stream)
        _validate_encryption_unsupported(self.require_encryption, self.key_encryption_key)

        # _upload_blob_chunks returns the block ids for block blobs so resource_properties
        # is passed as a parameter to get the last_modified and etag for page and append blobs.
        # this info is not needed for block_blobs since _put_block_list is called after which gets this info
        resource_properties = ResourceProperties()
        _upload_blob_chunks(
            blob_service=self,
            container_name=container_name,
            blob_name=blob_name,
            blob_size=count,
            block_size=self.MAX_BLOCK_SIZE,
            stream=stream,
            max_connections=1,  # upload not easily parallelizable
            progress_callback=progress_callback,
            validate_content=validate_content,
            lease_id=lease_id,
            uploader_class=_AppendBlobChunkUploader,
            maxsize_condition=maxsize_condition,
            timeout=timeout,
            resource_properties=resource_properties,
            if_modified_since=if_modified_since,
            if_unmodified_since=if_unmodified_since,
            if_match=if_match,
            if_none_match=if_none_match
        )

        return resource_properties
