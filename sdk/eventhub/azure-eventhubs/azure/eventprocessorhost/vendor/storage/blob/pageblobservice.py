# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import sys
from os import path

from ..common._common_conversion import (
    _int_to_str,
    _to_str,
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
)
from ..common._http import HTTPRequest
from ..common._serialization import (
    _get_data_bytes_only,
    _add_metadata_headers,
)
from ._deserialization import (
    _convert_xml_to_page_ranges,
    _parse_page_properties,
    _parse_base_properties,
)
from ._encryption import _generate_blob_encryption_data
from ._error import (
    _ERROR_PAGE_BLOB_SIZE_ALIGNMENT,
)
from ._serialization import (
    _get_path,
    _validate_and_format_range_headers,
)
from ._upload_chunking import (
    _PageBlobChunkUploader,
    _upload_blob_chunks,
)
from .baseblobservice import BaseBlobService
from .models import (
    _BlobTypes,
    ResourceProperties)

if sys.version_info >= (3,):
    from io import BytesIO
else:
    from cStringIO import StringIO as BytesIO

# Keep this value sync with _ERROR_PAGE_BLOB_SIZE_ALIGNMENT
_PAGE_ALIGNMENT = 512


class PageBlobService(BaseBlobService):
    '''
    Page blobs are a collection of 512-byte pages optimized for random read and
    write operations. To create a page blob, you initialize the page blob and
    specify the maximum size the page blob will grow. To add or update the
    contents of a page blob, you write a page or pages by specifying an offset
    and a range that align to 512-byte page boundaries. A write to a page blob
    can overwrite just one page, some pages, or up to 4 MB of the page blob.
    Writes to page blobs happen in-place and are immediately committed to the
    blob. The maximum size for a page blob is 8 TB.

    :ivar int MAX_PAGE_SIZE: 
        The size of the pages put by create_blob_from_* methods. Smaller pages 
        may be put if there is less data provided. The maximum page size the service 
        supports is 4MB. When using the create_blob_from_* methods, empty pages are skipped.
    '''

    MAX_PAGE_SIZE = 4 * 1024 * 1024

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
        self.blob_type = _BlobTypes.PageBlob
        super(PageBlobService, self).__init__(
            account_name, account_key, sas_token, is_emulated, protocol, endpoint_suffix,
            custom_domain, request_session, connection_string, socket_timeout, token_credential)

    def create_blob(
            self, container_name, blob_name, content_length, content_settings=None,
            sequence_number=None, metadata=None, lease_id=None, if_modified_since=None,
            if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None, premium_page_blob_tier=None):
        '''
        Creates a new Page Blob.

        See create_blob_from_* for high level functions that handle the
        creation and upload of large blobs with automatic chunking and
        progress notifications.

        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of blob to create or update.
        :param int content_length:
            Required. This header specifies the maximum size
            for the page blob, up to 1 TB. The page blob size must be aligned
            to a 512-byte boundary.
        :param ~azure.storage.blob.models.ContentSettings content_settings:
            ContentSettings object used to set properties on the blob.
        :param int sequence_number:
            The sequence number is a user-controlled value that you can use to
            track requests. The value of the sequence number must be between 0
            and 2^63 - 1.The default value is 0.
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
        :param PremiumPageBlobTier premium_page_blob_tier:
            A page blob tier value to set the blob to. The tier correlates to the size of the
            blob and number of allowed IOPS. This is only applicable to page blobs on
            premium storage accounts.
        :return: ETag and last modified properties for the new Page Blob
        :rtype: :class:`~azure.storage.blob.models.ResourceProperties`
        '''
        _validate_encryption_unsupported(self.require_encryption, self.key_encryption_key)

        return self._create_blob(
            container_name,
            blob_name,
            content_length,
            content_settings=content_settings,
            sequence_number=sequence_number,
            metadata=metadata,
            lease_id=lease_id,
            premium_page_blob_tier=premium_page_blob_tier,
            if_modified_since=if_modified_since,
            if_unmodified_since=if_unmodified_since,
            if_match=if_match,
            if_none_match=if_none_match,
            timeout=timeout
        )

    def incremental_copy_blob(self, container_name, blob_name, copy_source,
                              metadata=None, destination_if_modified_since=None, destination_if_unmodified_since=None,
                              destination_if_match=None, destination_if_none_match=None, destination_lease_id=None,
                              source_lease_id=None, timeout=None):
        '''
        Copies an incremental copy of a blob asynchronously. This operation returns a copy operation
        properties object, including a copy ID you can use to check or abort the
        copy operation. The Blob service copies blobs on a best-effort basis.

        The source blob for an incremental copy operation must be a page blob.
        Call get_blob_properties on the destination blob to check the status of the copy operation.
        The final blob will be committed when the copy completes.

        :param str container_name:
            Name of the destination container. The container must exist.
        :param str blob_name:
            Name of the destination blob. If the destination blob exists, it will
            be overwritten. Otherwise, it will be created.
        :param str copy_source:
            A URL of up to 2 KB in length that specifies an Azure page blob.
            The value should be URL-encoded as it would appear in a request URI.
            The copy source must be a snapshot and include a valid SAS token or be public.
            Example:
            https://myaccount.blob.core.windows.net/mycontainer/myblob?snapshot=<DateTime>&sastoken
        :param metadata:
            Name-value pairs associated with the blob as metadata. If no name-value
            pairs are specified, the operation will copy the metadata from the
            source blob or file to the destination blob. If one or more name-value
            pairs are specified, the destination blob is created with the specified
            metadata, and metadata is not copied from the source blob or file.
        :type metadata: dict(str, str).
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
            Specify this conditional header to copy the blob only if the destination blob
            has not been modified since the specified ate/time. If the destination blob
            has been modified, the Blob service returns status code 412 (Precondition Failed).
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
        :return: Copy operation properties such as status, source, and ID.
        :rtype: :class:`~azure.storage.blob.models.CopyProperties`
        '''
        return self._copy_blob(container_name, blob_name, copy_source,
                               metadata,
                               source_if_modified_since=None, source_if_unmodified_since=None,
                               source_if_match=None, source_if_none_match=None,
                               destination_if_modified_since=destination_if_modified_since,
                               destination_if_unmodified_since=destination_if_unmodified_since,
                               destination_if_match=destination_if_match,
                               destination_if_none_match=destination_if_none_match,
                               destination_lease_id=destination_lease_id,
                               source_lease_id=source_lease_id, timeout=timeout,
                               incremental_copy=True)

    def update_page(
            self, container_name, blob_name, page, start_range, end_range,
            validate_content=False, lease_id=None, if_sequence_number_lte=None,
            if_sequence_number_lt=None, if_sequence_number_eq=None,
            if_modified_since=None, if_unmodified_since=None,
            if_match=None, if_none_match=None, timeout=None):
        '''
        Updates a range of pages.

        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of existing blob.
        :param bytes page:
            Content of the page.
        :param int start_range:
            Start of byte range to use for writing to a section of the blob.
            Pages must be aligned with 512-byte boundaries, the start offset
            must be a modulus of 512 and the end offset must be a modulus of
            512-1. Examples of valid byte ranges are 0-511, 512-1023, etc.
        :param int end_range:
            End of byte range to use for writing to a section of the blob.
            Pages must be aligned with 512-byte boundaries, the start offset
            must be a modulus of 512 and the end offset must be a modulus of
            512-1. Examples of valid byte ranges are 0-511, 512-1023, etc.
        :param bool validate_content:
            If true, calculates an MD5 hash of the page content. The storage 
            service checks the hash of the content that has arrived
            with the hash that was sent. This is primarily valuable for detecting 
            bitflips on the wire if using http instead of https as https (the default) 
            will already validate. Note that this MD5 hash is not stored with the 
            blob.
        :param str lease_id:
            Required if the blob has an active lease.
        :param int if_sequence_number_lte:
            If the blob's sequence number is less than or equal to
            the specified value, the request proceeds; otherwise it fails.
        :param int if_sequence_number_lt:
            If the blob's sequence number is less than the specified
            value, the request proceeds; otherwise it fails.
        :param int if_sequence_number_eq:
            If the blob's sequence number is equal to the specified
            value, the request proceeds; otherwise it fails.
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
            An ETag value, or the wildcard character (*). Specify an ETag value for this conditional
            header to write the page only if the blob's ETag value matches the
            value specified. If the values do not match, the Blob service fails.
        :param str if_none_match:
            An ETag value, or the wildcard character (*). Specify an ETag value for this conditional
            header to write the page only if the blob's ETag value does not
            match the value specified. If the values are identical, the Blob
            service fails.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: ETag and last modified properties for the updated Page Blob
        :rtype: :class:`~azure.storage.blob.models.ResourceProperties`
        '''

        _validate_encryption_unsupported(self.require_encryption, self.key_encryption_key)

        return self._update_page(
            container_name,
            blob_name,
            page,
            start_range,
            end_range,
            validate_content=validate_content,
            lease_id=lease_id,
            if_sequence_number_lte=if_sequence_number_lte,
            if_sequence_number_lt=if_sequence_number_lt,
            if_sequence_number_eq=if_sequence_number_eq,
            if_modified_since=if_modified_since,
            if_unmodified_since=if_unmodified_since,
            if_match=if_match,
            if_none_match=if_none_match,
            timeout=timeout
        )

    def update_page_from_url(self, container_name, blob_name, start_range, end_range, copy_source_url,
                             source_range_start, source_content_md5=None, source_if_modified_since=None,
                             source_if_unmodified_since=None, source_if_match=None, source_if_none_match=None,
                             lease_id=None, if_sequence_number_lte=None, if_sequence_number_lt=None,
                             if_sequence_number_eq=None, if_modified_since=None, if_unmodified_since=None,
                             if_match=None, if_none_match=None, timeout=None):
        """
        Updates a range of pages to a page blob where the contents are read from a URL.

        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of blob.
        :param int start_range:
            Start of byte range to use for writing to a section of the blob.
            Pages must be aligned with 512-byte boundaries, the start offset
            must be a modulus of 512 and the end offset must be a modulus of
            512-1. Examples of valid byte ranges are 0-511, 512-1023, etc.
        :param int end_range:
            End of byte range to use for writing to a section of the blob.
            Pages must be aligned with 512-byte boundaries, the start offset
            must be a modulus of 512 and the end offset must be a modulus of
            512-1. Examples of valid byte ranges are 0-511, 512-1023, etc.
        :param str copy_source_url:
            The URL of the source data. It can point to any Azure Blob or File, that is either public or has a
            shared access signature attached.
        :param int source_range_start:
            This indicates the start of the range of bytes(inclusive) that has to be taken from the copy source.
            The service will read the same number of bytes as the destination range (end_range-start_range).
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
        :param str lease_id:
            Required if the blob has an active lease.
        :param int if_sequence_number_lte:
            If the blob's sequence number is less than or equal to
            the specified value, the request proceeds; otherwise it fails.
        :param int if_sequence_number_lt:
            If the blob's sequence number is less than the specified
            value, the request proceeds; otherwise it fails.
        :param int if_sequence_number_eq:
            If the blob's sequence number is equal to the specified
            value, the request proceeds; otherwise it fails.
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
            'comp': 'page',
            'timeout': _int_to_str(timeout),
        }
        request.headers = {
            'x-ms-page-write': 'update',
            'x-ms-copy-source': copy_source_url,
            'x-ms-source-content-md5': source_content_md5,
            'x-ms-source-if-Modified-Since': _datetime_to_utc_string(source_if_modified_since),
            'x-ms-source-if-Unmodified-Since': _datetime_to_utc_string(source_if_unmodified_since),
            'x-ms-source-if-Match': _to_str(source_if_match),
            'x-ms-source-if-None-Match': _to_str(source_if_none_match),
            'x-ms-lease-id': _to_str(lease_id),
            'x-ms-if-sequence-number-le': _to_str(if_sequence_number_lte),
            'x-ms-if-sequence-number-lt': _to_str(if_sequence_number_lt),
            'x-ms-if-sequence-number-eq': _to_str(if_sequence_number_eq),
            'If-Modified-Since': _datetime_to_utc_string(if_modified_since),
            'If-Unmodified-Since': _datetime_to_utc_string(if_unmodified_since),
            'If-Match': _to_str(if_match),
            'If-None-Match': _to_str(if_none_match)
        }
        _validate_and_format_range_headers(
            request,
            start_range,
            end_range,
            align_to_page=True)
        _validate_and_format_range_headers(
            request,
            source_range_start,
            source_range_start+(end_range-start_range),
            range_header_name="x-ms-source-range")

        return self._perform_request(request, _parse_page_properties)

    def clear_page(
            self, container_name, blob_name, start_range, end_range,
            lease_id=None, if_sequence_number_lte=None,
            if_sequence_number_lt=None, if_sequence_number_eq=None,
            if_modified_since=None, if_unmodified_since=None,
            if_match=None, if_none_match=None, timeout=None):
        '''
        Clears a range of pages.

        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of existing blob.
        :param int start_range:
            Start of byte range to use for writing to a section of the blob.
            Pages must be aligned with 512-byte boundaries, the start offset
            must be a modulus of 512 and the end offset must be a modulus of
            512-1. Examples of valid byte ranges are 0-511, 512-1023, etc.
        :param int end_range:
            End of byte range to use for writing to a section of the blob.
            Pages must be aligned with 512-byte boundaries, the start offset
            must be a modulus of 512 and the end offset must be a modulus of
            512-1. Examples of valid byte ranges are 0-511, 512-1023, etc.
        :param str lease_id:
            Required if the blob has an active lease.
        :param int if_sequence_number_lte:
            If the blob's sequence number is less than or equal to
            the specified value, the request proceeds; otherwise it fails.
        :param int if_sequence_number_lt:
            If the blob's sequence number is less than the specified
            value, the request proceeds; otherwise it fails.
        :param int if_sequence_number_eq:
            If the blob's sequence number is equal to the specified
            value, the request proceeds; otherwise it fails.
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
            An ETag value, or the wildcard character (*). Specify an ETag value for this conditional
            header to write the page only if the blob's ETag value matches the
            value specified. If the values do not match, the Blob service fails.
        :param str if_none_match:
            An ETag value, or the wildcard character (*). Specify an ETag value for this conditional
            header to write the page only if the blob's ETag value does not
            match the value specified. If the values are identical, the Blob
            service fails.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: ETag and last modified properties for the updated Page Blob
        :rtype: :class:`~azure.storage.blob.models.ResourceProperties`
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)

        request = HTTPRequest()
        request.method = 'PUT'
        request.host_locations = self._get_host_locations()
        request.path = _get_path(container_name, blob_name)
        request.query = {
            'comp': 'page',
            'timeout': _int_to_str(timeout),
        }
        request.headers = {
            'x-ms-page-write': 'clear',
            'x-ms-lease-id': _to_str(lease_id),
            'x-ms-if-sequence-number-le': _to_str(if_sequence_number_lte),
            'x-ms-if-sequence-number-lt': _to_str(if_sequence_number_lt),
            'x-ms-if-sequence-number-eq': _to_str(if_sequence_number_eq),
            'If-Modified-Since': _datetime_to_utc_string(if_modified_since),
            'If-Unmodified-Since': _datetime_to_utc_string(if_unmodified_since),
            'If-Match': _to_str(if_match),
            'If-None-Match': _to_str(if_none_match)
        }
        _validate_and_format_range_headers(
            request,
            start_range,
            end_range,
            align_to_page=True)

        return self._perform_request(request, _parse_page_properties)

    def get_page_ranges(
            self, container_name, blob_name, snapshot=None, start_range=None,
            end_range=None, lease_id=None, if_modified_since=None,
            if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None):
        '''
        Returns the list of valid page ranges for a Page Blob or snapshot
        of a page blob.

        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of existing blob.
        :param str snapshot:
            The snapshot parameter is an opaque DateTime value that,
            when present, specifies the blob snapshot to retrieve information
            from.
        :param int start_range:
            Start of byte range to use for getting valid page ranges.
            If no end_range is given, all bytes after the start_range will be searched.
            Pages must be aligned with 512-byte boundaries, the start offset
            must be a modulus of 512 and the end offset must be a modulus of
            512-1. Examples of valid byte ranges are 0-511, 512-, etc.
        :param int end_range:
            End of byte range to use for getting valid page ranges.
            If end_range is given, start_range must be provided.
            This range will return valid page ranges for from the offset start up to
            offset end.
            Pages must be aligned with 512-byte boundaries, the start offset
            must be a modulus of 512 and the end offset must be a modulus of
            512-1. Examples of valid byte ranges are 0-511, 512-, etc.
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
        :return: A list of valid Page Ranges for the Page Blob.
        :rtype: list(:class:`~azure.storage.blob.models.PageRange`)
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        request = HTTPRequest()
        request.method = 'GET'
        request.host_locations = self._get_host_locations(secondary=True)
        request.path = _get_path(container_name, blob_name)
        request.query = {
            'comp': 'pagelist',
            'snapshot': _to_str(snapshot),
            'timeout': _int_to_str(timeout),
        }
        request.headers = {
            'x-ms-lease-id': _to_str(lease_id),
            'If-Modified-Since': _datetime_to_utc_string(if_modified_since),
            'If-Unmodified-Since': _datetime_to_utc_string(if_unmodified_since),
            'If-Match': _to_str(if_match),
            'If-None-Match': _to_str(if_none_match),
        }
        if start_range is not None:
            _validate_and_format_range_headers(
                request,
                start_range,
                end_range,
                start_range_required=False,
                end_range_required=False,
                align_to_page=True)

        return self._perform_request(request, _convert_xml_to_page_ranges)

    def get_page_ranges_diff(
            self, container_name, blob_name, previous_snapshot, snapshot=None,
            start_range=None, end_range=None, lease_id=None, if_modified_since=None,
            if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None):
        '''
        The response will include only the pages that are different between either a
        recent snapshot or the current blob and a previous snapshot, including pages
        that were cleared.

        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of existing blob.
        :param str previous_snapshot:
            The snapshot parameter is an opaque DateTime value that
            specifies a previous blob snapshot to be compared
            against a more recent snapshot or the current blob.
        :param str snapshot:
            The snapshot parameter is an opaque DateTime value that
            specifies a more recent blob snapshot to be compared
            against a previous snapshot (previous_snapshot).
        :param int start_range:
            Start of byte range to use for getting different page ranges.
            If no end_range is given, all bytes after the start_range will be searched.
            Pages must be aligned with 512-byte boundaries, the start offset
            must be a modulus of 512 and the end offset must be a modulus of
            512-1. Examples of valid byte ranges are 0-511, 512-, etc.
        :param int end_range:
            End of byte range to use for getting different page ranges.
            If end_range is given, start_range must be provided.
            This range will return valid page ranges for from the offset start up to
            offset end.
            Pages must be aligned with 512-byte boundaries, the start offset
            must be a modulus of 512 and the end offset must be a modulus of
            512-1. Examples of valid byte ranges are 0-511, 512-, etc.
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
        :return: A list of different Page Ranges for the Page Blob.
        :rtype: list(:class:`~azure.storage.blob.models.PageRange`)
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        _validate_not_none('previous_snapshot', previous_snapshot)
        request = HTTPRequest()
        request.method = 'GET'
        request.host_locations = self._get_host_locations(secondary=True)
        request.path = _get_path(container_name, blob_name)
        request.query = {
            'comp': 'pagelist',
            'snapshot': _to_str(snapshot),
            'prevsnapshot': _to_str(previous_snapshot),
            'timeout': _int_to_str(timeout),
        }
        request.headers = {
            'x-ms-lease-id': _to_str(lease_id),
            'If-Modified-Since': _datetime_to_utc_string(if_modified_since),
            'If-Unmodified-Since': _datetime_to_utc_string(if_unmodified_since),
            'If-Match': _to_str(if_match),
            'If-None-Match': _to_str(if_none_match),
        }
        if start_range is not None:
            _validate_and_format_range_headers(
                request,
                start_range,
                end_range,
                start_range_required=False,
                end_range_required=False,
                align_to_page=True)

        return self._perform_request(request, _convert_xml_to_page_ranges)

    def set_sequence_number(
            self, container_name, blob_name, sequence_number_action, sequence_number=None,
            lease_id=None, if_modified_since=None, if_unmodified_since=None,
            if_match=None, if_none_match=None, timeout=None):

        '''
        Sets the blob sequence number.

        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of existing blob.
        :param str sequence_number_action:
            This property indicates how the service should modify the blob's sequence
            number. See :class:`~azure.storage.blob.models.SequenceNumberAction` for more information.
        :param str sequence_number:
            This property sets the blob's sequence number. The sequence number is a
            user-controlled property that you can use to track requests and manage
            concurrency issues.
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
        :return: ETag and last modified properties for the updated Page Blob
        :rtype: :class:`~azure.storage.blob.models.ResourceProperties`
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        _validate_not_none('sequence_number_action', sequence_number_action)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host_locations = self._get_host_locations()
        request.path = _get_path(container_name, blob_name)
        request.query = {
            'comp': 'properties',
            'timeout': _int_to_str(timeout),
        }
        request.headers = {
            'x-ms-blob-sequence-number': _to_str(sequence_number),
            'x-ms-sequence-number-action': _to_str(sequence_number_action),
            'x-ms-lease-id': _to_str(lease_id),
            'If-Modified-Since': _datetime_to_utc_string(if_modified_since),
            'If-Unmodified-Since': _datetime_to_utc_string(if_unmodified_since),
            'If-Match': _to_str(if_match),
            'If-None-Match': _to_str(if_none_match),
        }

        return self._perform_request(request, _parse_page_properties)

    def resize_blob(
            self, container_name, blob_name, content_length,
            lease_id=None, if_modified_since=None, if_unmodified_since=None,
            if_match=None, if_none_match=None, timeout=None):

        '''
        Resizes a page blob to the specified size. If the specified value is less
        than the current size of the blob, then all pages above the specified value
        are cleared.

        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of existing blob.
        :param int content_length:
            Size to resize blob to.
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
        :return: ETag and last modified properties for the updated Page Blob
        :rtype: :class:`~azure.storage.blob.models.ResourceProperties`
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        _validate_not_none('content_length', content_length)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host_locations = self._get_host_locations()
        request.path = _get_path(container_name, blob_name)
        request.query = {
            'comp': 'properties',
            'timeout': _int_to_str(timeout),
        }
        request.headers = {
            'x-ms-blob-content-length': _to_str(content_length),
            'x-ms-lease-id': _to_str(lease_id),
            'If-Modified-Since': _datetime_to_utc_string(if_modified_since),
            'If-Unmodified-Since': _datetime_to_utc_string(if_unmodified_since),
            'If-Match': _to_str(if_match),
            'If-None-Match': _to_str(if_none_match),
        }

        return self._perform_request(request, _parse_page_properties)

    # ----Convenience APIs-----------------------------------------------------

    def create_blob_from_path(
            self, container_name, blob_name, file_path, content_settings=None,
            metadata=None, validate_content=False, progress_callback=None, max_connections=2,
            lease_id=None, if_modified_since=None, if_unmodified_since=None,
            if_match=None, if_none_match=None, timeout=None, premium_page_blob_tier=None):
        '''
        Creates a new blob from a file path, or updates the content of an
        existing blob, with automatic chunking and progress notifications.
        Empty chunks are skipped, while non-emtpy ones(even if only partly filled) are uploaded.

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
            If true, calculates an MD5 hash for each page of the blob. The storage 
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
            Maximum number of parallel connections to use.
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
        :param premium_page_blob_tier:
            A page blob tier value to set the blob to. The tier correlates to the size of the
            blob and number of allowed IOPS. This is only applicable to page blobs on
            premium storage accounts.
        :return: ETag and last modified properties for the Page Blob
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
                progress_callback=progress_callback,
                max_connections=max_connections,
                lease_id=lease_id,
                if_modified_since=if_modified_since,
                if_unmodified_since=if_unmodified_since,
                if_match=if_match,
                if_none_match=if_none_match,
                timeout=timeout,
                premium_page_blob_tier=premium_page_blob_tier)

    def create_blob_from_stream(
            self, container_name, blob_name, stream, count, content_settings=None,
            metadata=None, validate_content=False, progress_callback=None,
            max_connections=2, lease_id=None, if_modified_since=None,
            if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None,
            premium_page_blob_tier=None):
        '''
        Creates a new blob from a file/stream, or updates the content of an
        existing blob, with automatic chunking and progress notifications.
        Empty chunks are skipped, while non-emtpy ones(even if only partly filled) are uploaded.

        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of blob to create or update.
        :param io.IOBase stream:
            Opened file/stream to upload as the blob content.
        :param int count:
            Number of bytes to read from the stream. This is required, a page
            blob cannot be created if the count is unknown.
        :param ~azure.storage.blob.models.ContentSettings content_settings:
            ContentSettings object used to set the blob properties.
        :param metadata:
            Name-value pairs associated with the blob as metadata.
        :type metadata: dict(str, str)
        :param bool validate_content:
            If true, calculates an MD5 hash for each page of the blob. The storage 
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
            Maximum number of parallel connections to use. Note that parallel upload 
            requires the stream to be seekable.
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
        :param premium_page_blob_tier:
            A page blob tier value to set the blob to. The tier correlates to the size of the
            blob and number of allowed IOPS. This is only applicable to page blobs on
            premium storage accounts.
        :return: ETag and last modified properties for the Page Blob
        :rtype: :class:`~azure.storage.blob.models.ResourceProperties`
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        _validate_not_none('stream', stream)
        _validate_not_none('count', count)
        _validate_encryption_required(self.require_encryption, self.key_encryption_key)

        if count < 0:
            raise ValueError(_ERROR_VALUE_NEGATIVE.format('count'))

        if count % _PAGE_ALIGNMENT != 0:
            raise ValueError(_ERROR_PAGE_BLOB_SIZE_ALIGNMENT.format(count))

        cek, iv, encryption_data = None, None, None
        if self.key_encryption_key is not None:
            cek, iv, encryption_data = _generate_blob_encryption_data(self.key_encryption_key)

        response = self._create_blob(
            container_name=container_name,
            blob_name=blob_name,
            content_length=count,
            content_settings=content_settings,
            metadata=metadata,
            lease_id=lease_id,
            premium_page_blob_tier=premium_page_blob_tier,
            if_modified_since=if_modified_since,
            if_unmodified_since=if_unmodified_since,
            if_match=if_match,
            if_none_match=if_none_match,
            timeout=timeout,
            encryption_data=encryption_data
        )

        if count == 0:
            return response

        # _upload_blob_chunks returns the block ids for block blobs so resource_properties
        # is passed as a parameter to get the last_modified and etag for page and append blobs.
        # this info is not needed for block_blobs since _put_block_list is called after which gets this info
        resource_properties = ResourceProperties()
        _upload_blob_chunks(
            blob_service=self,
            container_name=container_name,
            blob_name=blob_name,
            blob_size=count,
            block_size=self.MAX_PAGE_SIZE,
            stream=stream,
            max_connections=max_connections,
            progress_callback=progress_callback,
            validate_content=validate_content,
            lease_id=lease_id,
            uploader_class=_PageBlobChunkUploader,
            if_match=response.etag,
            timeout=timeout,
            content_encryption_key=cek,
            initialization_vector=iv,
            resource_properties=resource_properties
        )

        return resource_properties

    def create_blob_from_bytes(
            self, container_name, blob_name, blob, index=0, count=None,
            content_settings=None, metadata=None, validate_content=False,
            progress_callback=None, max_connections=2, lease_id=None,
            if_modified_since=None, if_unmodified_since=None, if_match=None,
            if_none_match=None, timeout=None, premium_page_blob_tier=None):
        '''
        Creates a new blob from an array of bytes, or updates the content
        of an existing blob, with automatic chunking and progress
        notifications. Empty chunks are skipped, while non-emtpy ones(even if only partly filled) are uploaded.

        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of blob to create or update.
        :param bytes blob:
            Content of blob as an array of bytes.
        :param int index:
            Start index in the byte array.
        :param int count:
            Number of bytes to upload. Set to None or negative value to upload
            all bytes starting from index.
        :param ~azure.storage.blob.models.ContentSettings content_settings:
            ContentSettings object used to set blob properties.
        :param metadata:
            Name-value pairs associated with the blob as metadata.
        :type metadata: dict(str, str)
        :param bool validate_content:
            If true, calculates an MD5 hash for each page of the blob. The storage 
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
            Maximum number of parallel connections to use.
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
        :param premium_page_blob_tier:
            A page blob tier value to set the blob to. The tier correlates to the size of the
            blob and number of allowed IOPS. This is only applicable to page blobs on
            premium storage accounts.
        :return: ETag and last modified properties for the Page Blob
        :rtype: :class:`~azure.storage.blob.models.ResourceProperties`
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        _validate_not_none('blob', blob)
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
            lease_id=lease_id,
            progress_callback=progress_callback,
            max_connections=max_connections,
            if_modified_since=if_modified_since,
            if_unmodified_since=if_unmodified_since,
            if_match=if_match,
            if_none_match=if_none_match,
            timeout=timeout,
            premium_page_blob_tier=premium_page_blob_tier)

    def set_premium_page_blob_tier(
            self, container_name, blob_name, premium_page_blob_tier,
            timeout=None):
        '''
        Sets the page blob tiers on the blob. This API is only supported for page blobs on premium accounts.

        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of blob to update.
        :param PremiumPageBlobTier premium_page_blob_tier:
            A page blob tier value to set the blob to. The tier correlates to the size of the
            blob and number of allowed IOPS. This is only applicable to page blobs on
            premium storage accounts.
        :param int timeout:
            The timeout parameter is expressed in seconds. This method may make
            multiple calls to the Azure service and the timeout will apply to
            each call individually.
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        _validate_not_none('premium_page_blob_tier', premium_page_blob_tier)

        request = HTTPRequest()
        request.method = 'PUT'
        request.host_locations = self._get_host_locations()
        request.path = _get_path(container_name, blob_name)
        request.query = {
            'comp': 'tier',
            'timeout': _int_to_str(timeout),
        }
        request.headers = {
            'x-ms-access-tier': _to_str(premium_page_blob_tier)
        }

        self._perform_request(request)

    def copy_blob(self, container_name, blob_name, copy_source,
                  metadata=None,
                  source_if_modified_since=None,
                  source_if_unmodified_since=None,
                  source_if_match=None, source_if_none_match=None,
                  destination_if_modified_since=None,
                  destination_if_unmodified_since=None,
                  destination_if_match=None,
                  destination_if_none_match=None,
                  destination_lease_id=None,
                  source_lease_id=None, timeout=None,
                  premium_page_blob_tier=None):
        '''
        Copies a blob asynchronously. This operation returns a copy operation
        properties object, including a copy ID you can use to check or abort the
        copy operation. The Blob service copies blobs on a best-effort basis.

        The source blob for a copy operation must be a page blob. If the destination
        blob already exists, it must be of the same blob type as the source blob.
        Any existing destination blob will be overwritten.
        The destination blob cannot be modified while a copy operation is in progress.

        When copying from a page blob, the Blob service creates a destination page
        blob of the source blob's length, initially containing all zeroes. Then
        the source page ranges are enumerated, and non-empty ranges are copied.

        If the tier on the source blob is larger than the tier being passed to this
        copy operation or if the size of the blob exceeds the tier being passed to
        this copy operation then the operation will fail.

        You can call get_blob_properties on the destination
        blob to check the status of the copy operation. The final blob will be
        committed when the copy completes.

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
        :type metadata: dict(str, str).
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
        :param PageBlobTier premium_page_blob_tier:
            A page blob tier value to set on the destination blob. The tier correlates to
            the size of the blob and number of allowed IOPS. This is only applicable to
            page blobs on premium storage accounts.
            If the tier on the source blob is larger than the tier being passed to this
            copy operation or if the size of the blob exceeds the tier being passed to
            this copy operation then the operation will fail.
        :return: Copy operation properties such as status, source, and ID.
        :rtype: :class:`~azure.storage.blob.models.CopyProperties`
        '''
        return self._copy_blob(container_name, blob_name, copy_source,
                               metadata, premium_page_blob_tier,
                               source_if_modified_since, source_if_unmodified_since,
                               source_if_match, source_if_none_match,
                               destination_if_modified_since,
                               destination_if_unmodified_since,
                               destination_if_match,
                               destination_if_none_match,
                               destination_lease_id,
                               source_lease_id, timeout,
                               False)

    # -----Helper methods-----------------------------------------------------

    def _create_blob(
            self, container_name, blob_name, content_length, content_settings=None,
            sequence_number=None, metadata=None, lease_id=None, premium_page_blob_tier=None, if_modified_since=None,
            if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None,
            encryption_data=None):
        '''
        See create_blob for more details. This helper method
        allows for encryption or other such special behavior because
        it is safely handled by the library. These behaviors are
        prohibited in the public version of this function.
        :param str encryption_data:
            The JSON formatted encryption metadata to upload as a part of the blob.
            This should only be passed internally from other methods and only applied
            when uploading entire blob contents immediately follows creation of the blob.
        '''

        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        _validate_not_none('content_length', content_length)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host_locations = self._get_host_locations()
        request.path = _get_path(container_name, blob_name)
        request.query = {'timeout': _int_to_str(timeout)}
        request.headers = {
            'x-ms-blob-type': _to_str(self.blob_type),
            'x-ms-blob-content-length': _to_str(content_length),
            'x-ms-lease-id': _to_str(lease_id),
            'x-ms-blob-sequence-number': _to_str(sequence_number),
            'x-ms-access-tier': _to_str(premium_page_blob_tier),
            'If-Modified-Since': _datetime_to_utc_string(if_modified_since),
            'If-Unmodified-Since': _datetime_to_utc_string(if_unmodified_since),
            'If-Match': _to_str(if_match),
            'If-None-Match': _to_str(if_none_match)
        }
        _add_metadata_headers(metadata, request)
        if content_settings is not None:
            request.headers.update(content_settings._to_headers())

        if encryption_data is not None:
            request.headers['x-ms-meta-encryptiondata'] = encryption_data

        return self._perform_request(request, _parse_base_properties)

    def _update_page(
            self, container_name, blob_name, page, start_range, end_range,
            validate_content=False, lease_id=None, if_sequence_number_lte=None,
            if_sequence_number_lt=None, if_sequence_number_eq=None,
            if_modified_since=None, if_unmodified_since=None,
            if_match=None, if_none_match=None, timeout=None):
        '''
        See update_page for more details. This helper method
        allows for encryption or other such special behavior because
        it is safely handled by the library. These behaviors are
        prohibited in the public version of this function.
        '''

        request = HTTPRequest()
        request.method = 'PUT'
        request.host_locations = self._get_host_locations()
        request.path = _get_path(container_name, blob_name)
        request.query = {
            'comp': 'page',
            'timeout': _int_to_str(timeout),
        }
        request.headers = {
            'x-ms-page-write': 'update',
            'x-ms-lease-id': _to_str(lease_id),
            'x-ms-if-sequence-number-le': _to_str(if_sequence_number_lte),
            'x-ms-if-sequence-number-lt': _to_str(if_sequence_number_lt),
            'x-ms-if-sequence-number-eq': _to_str(if_sequence_number_eq),
            'If-Modified-Since': _datetime_to_utc_string(if_modified_since),
            'If-Unmodified-Since': _datetime_to_utc_string(if_unmodified_since),
            'If-Match': _to_str(if_match),
            'If-None-Match': _to_str(if_none_match)
        }
        _validate_and_format_range_headers(
            request,
            start_range,
            end_range,
            align_to_page=True)
        request.body = _get_data_bytes_only('page', page)

        if validate_content:
            computed_md5 = _get_content_md5(request.body)
            request.headers['Content-MD5'] = _to_str(computed_md5)

        return self._perform_request(request, _parse_page_properties)
