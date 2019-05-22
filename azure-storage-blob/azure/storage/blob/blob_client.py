# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from io import BytesIO
from typing import (  # pylint: disable=unused-import
    Union, Optional, Any, IO, Iterable, AnyStr, Dict, List, Tuple,
    TYPE_CHECKING
)
try:
    from urllib.parse import urlparse, quote, unquote
except ImportError:
    from urlparse import urlparse
    from urllib2 import quote, unquote

import six
from azure.core import Configuration, HttpResponseError

from .common import BlobType
from .lease import Lease
from .models import SnapshotProperties, BlobBlock
from ._utils import (
    create_client,
    create_configuration,
    create_pipeline,
    basic_error_map,
    get_access_conditions,
    get_modification_conditions,
    get_sequence_conditions,
    return_response_headers,
    add_metadata_headers,
    process_storage_error,
    encode_base64,
    get_length,
    parse_connection_str
)
from ._deserialize import (
    deserialize_blob_properties,
    deserialize_blob_stream,
    deserialize_metadata
)
from ._generated.models import (
    BlobHTTPHeaders,
    StorageErrorException,
    BlockLookupList)
from ._upload_chunking import (
    _upload_blob_chunks,
    _upload_blob_substream_blocks,
    _PageBlobChunkUploader,
    _BlockBlobChunkUploader,
    IterStreamer)

if TYPE_CHECKING:
    from datetime import datetime
    from .common import PremiumPageBlobTier, StandardBlobTier, SequenceNumberAction
    from azure.core.pipeline.policies import HTTPPolicy
    from .models import (  # pylint: disable=unused-import
        ContainerProperties,
        BlobProperties,
        BlobPermissions,
        ContentSettings,
        BlobBlock,
        PageRange,
    )


class BlobClient(object):  # pylint: disable=too-many-public-methods

    def __init__(
            self, url,  # type: str
            container=None,  # type: Optional[Union[str, ContainerProperties]]
            blob=None,  # type: Optional[Union[str, BlobProperties]]
            snapshot=None,  # type: Optional[str]
            blob_type=BlobType.BlockBlob,  # type: Union[str, BlobType]
            credentials=None,  # type: Optional[HTTPPolicy]
            configuration=None,  # type: Optional[Configuration]
            **kwargs  # type: Any
        ):
        # type: (...) -> None
        parsed_url = urlparse(url)

        if not parsed_url.path and not (container and blob):
            raise ValueError("Please specify a container and blob name.")
        path_container = ""
        path_blob = ""
        path_snapshot = None
        if parsed_url.path:
            path_container, _, path_blob = parsed_url.path.partition('/')
        if parsed_url.query:
            query = parsed_url.query.lower().split('&')
            q_snapshot = [q for q in query if q.startswith('snapshot=')]
            if q_snapshot:
                path_snapshot = q_snapshot[0].split('=')[1]

        try:
            self.container = container.name
        except AttributeError:
            self.container = container or unquote(path_container)
        try:
            self.snapshot = snapshot.snapshot
        except AttributeError:
            self.snapshot = snapshot or path_snapshot
        try:
            self.name = blob.name
            self.blob_type = blob.blob_type
            if not snapshot:
                self.snapshot = blob.snapshot
        except AttributeError:
            self.name = blob or unquote(path_blob)
            self.blob_type = blob_type

        self.scheme = parsed_url.scheme
        self.account = parsed_url.hostname.split(".blob.core.")[0]
        self.url = "{}://{}/{}/{}".format(
            self.scheme,
            parsed_url.hostname,
            quote(self.container),
            self.name.replace(' ', '%20').replace('?', '%3F')  # TODO: Confirm why recordings don't urlencode chars
        )
        self.require_encryption = False
        self.key_encryption_key = None
        self.key_resolver_function = None

        self._config, self._pipeline = create_pipeline(configuration, credentials, **kwargs)
        self._client = create_client(self.url, self._pipeline)

    @staticmethod
    def create_configuration(**kwargs):
        # type: (**Any) -> Configuration
        return create_configuration(**kwargs)

    @classmethod
    def from_connection_string(
            cls, conn_str,  # type: str
            container,  # type: Union[str, ContainerProperties]
            blob,  # type: Union[str, BlobProperties]
            snapshot=None,  # type: Optional[str]
            blob_type=BlobType.BlockBlob,  # type: Union[str, BlobType]
            credentials=None,  # type: Optional[HTTPPolicy]
            configuration=None,  # type: Optional[Configuration]
            **kwargs  # type: Any
        ):
        """
        Create BlobClient from a Connection String.
        """
        account_url, creds = parse_connection_str(conn_str, credentials)
        return cls(
            account_url, container=container, blob=blob,
            snapshot=snapshot, blob_type=blob_type,
            credentials=creds, configuration=configuration, **kwargs)

    def make_url(self, protocol=None, sas_token=None):
        # type: (Optional[str], Optional[str]) -> str
        """
        Creates the url to access this blob.

        :param str protocol:
            Protocol to use: 'http' or 'https'. If not specified, uses the
            protocol specified in the URL when the client was created..
        :param str sas_token:
            Shared access signature token created with
            generate_shared_access_signature.
        :return: blob access URL.
        :rtype: str
        """
        parsed_url = urlparse(self.url)
        new_scheme = protocol or parsed_url.scheme
        query = []
        if self.snapshot:
            query.append("snapshot={}".format(self.snapshot))
        if sas_token:
            query.append(sas_token)
        new_url = "{}://{}{}".format(
            new_scheme,
            parsed_url.netloc,
            parsed_url.path)
        if query:
            new_url += "?{}".format('&'.join(query))
        return new_url

    def generate_shared_access_signature(
            self, permission=None,  # type: Optional[Union[BlobPermissions, str]]
            expiry=None,  # type: Optional[Union[datetime, str]]
            start=None,  # type: Optional[Union[datetime, str]]
            policy_id=None,  # type: Optional[str]
            ip=None,  # type: Optional[str]
            protocol=None,  # type: Optional[str]
            cache_control=None,  # type: Optional[str]
            content_disposition=None,  # type: Optional[str]
            content_encoding=None,  # type: Optional[str]
            content_language=None,  # type: Optional[str]
            content_type=None  # type: Optional[str]
        ):
        # type: (...) -> str
        """
        Generates a shared access signature for the blob.

        :param BlobPermissions permission:
            The permissions associated with the shared access signature. The
            user is restricted to operations allowed by the permissions.
            Permissions must be ordered read, write, delete, list.
            Required unless an id is given referencing a stored access policy
            which contains this field. This field must be omitted if it has been
            specified in an associated stored access policy.
        :param expiry:
            The time at which the shared access signature becomes invalid.
            Required unless an id is given referencing a stored access policy
            which contains this field. This field must be omitted if it has
            been specified in an associated stored access policy. Azure will always
            convert values to UTC. If a date is passed in without timezone info, it
            is assumed to be UTC.
        :type expiry: datetime or str
        :param start:
            The time at which the shared access signature becomes valid. I
            omitted, start time for this call is assumed to be the time when the
            storage service receives the request. Azure will always convert values
            to UTC. If a date is passed in without timezone info, it is assumed to
            be UTC.
        :type start: datetime or str
        :param str policy_id:
            A unique value up to 64 characters in length that correlates to a
            stored access policy. To create a stored access policy, use :func:`~set_container_acl`.
        :param str ip:
            Specifies an IP address or a range of IP addresses from which to accept requests.
            If the IP address from which the request originates does not match the IP address
            or address range specified on the SAS token, the request is not authenticated.
            For example, specifying sip=168.1.5.65 or sip=168.1.5.60-168.1.5.70 on the SAS
            restricts the request to those IP addresses.
        :param str protocol:
            Specifies the protocol permitted for a request made. The default value
            is https,http. See :class:`~azure.storage.common.models.Protocol` for possible values.
        :param str cache_control:
            Response header value for Cache-Control when resource is accessed
            using this shared access signature.
        :param str content_disposition:
            Response header value for Content-Disposition when resource is accessed
            using this shared access signature.
        :param str content_encoding:
            Response header value for Content-Encoding when resource is accessed
            using this shared access signature.
        :param str content_language:
            Response header value for Content-Language when resource is accessed
            using this shared access signature.
        :param str content_type:
            Response header value for Content-Type when resource is accessed
            using this shared access signature.
        :return: A Shared Access Signature (sas) token.
        :rtype: str
        """

    def get_account_information(self, timeout=None):
        # type: (Optional[int]) -> Dict[str, str]
        """
        :returns: A dict of account information (SKU and account type).
        """
        response = self._client.service.get_account_info(cls=return_response_headers)
        return {
            'SKU': response.get('x-ms-sku-name'),
            'AccountType': response.get('x-ms-account-kind')
        }

    def upload_blob(
            self, data,  # type: Union[Iterable[AnyStr], IO[AnyStr]]
            length=None,  # type: Optional[int]
            metadata=None,  # type: Optional[Dict[str, str]]
            content_settings=None,  # type: Optional[ContentSettings]
            validate_content=False,  # type: Optional[bool]
            lease=None,  # type: Optional[Union[Lease, str]]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            timeout=None,  # type: Optional[int]
            premium_page_blob_tier=None,  # type: Optional[Union[str, PremiumPageBlobTier]]
            maxsize_condition=None,  # type: Optional[int]
            max_connections=1,  # type: int
            encoding='UTF-8', # type: str
            **kwargs
        ):
        # type: (...) -> Dict[str, Union[str, datetime]]
        """
        Creates a new blob from a data source with automatic chunking.

        :param int length:
            Number of bytes to read from the stream. This is optional, but
            should be supplied for optimal performance.
        :param metadata:
            Name-value pairs associated with the blob as metadata.
        :type metadata: dict(str, str)
        :param ~azure.storage.blob.models.ContentSettings content_settings:
            ContentSettings object used to set blob properties.
        :param bool validate_content:
            If true, calculates an MD5 hash for each chunk of the blob. The storage
            service checks the hash of the content that has arrived with the hash
            that was sent. This is primarily valuable for detecting bitflips on
            the wire if using http instead of https as https (the default) will
            already validate. Note that this MD5 hash is not stored with the
            blob. Also note that if enabled, the memory-efficient upload algorithm
            will not be used, because computing the MD5 hash requires buffering
            entire blocks, and doing so defeats the purpose of the memory-efficient algorithm.
        :param int max_connections:
            Maximum number of parallel connections to use when the blob size exceeds
            64MB.
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
        :param int maxsize_condition:
            Optional conditional header. The max length in bytes permitted for
            the append blob. If the Append Block operation would cause the blob
            to exceed that limit or if the blob size is already greater than the
            value specified in this header, the request will fail with
            MaxBlobSizeConditionNotMet error (HTTP status code 412 - Precondition Failed).
        :returns: Blob-updated property dict (Etag and last modified)
        :rtype: dict[str, Any]
        """
        if self.require_encryption and not self.key_encryption_key:
            raise ValueError("Encryption required but no key was provided.")

        cek, iv, encryption_data = None, None, None
        if self.key_encryption_key is not None:
            cek, iv, encryption_data = _generate_blob_encryption_data(self.key_encryption_key)

        if isinstance(data, six.text_type):
            data = data.encode(encoding)
        if length is None:
            length = get_length(data)
        if isinstance(data, bytes):
            data = data[:length]

        if isinstance(data, bytes):
            stream = BytesIO(data)
        elif hasattr(data, 'read'):
            stream = data
        elif hasattr(data, '__iter__'):
            stream = IterStreamer(data)
        else:
            raise TypeError("Unsupported data type: {}".format(type(data)))

        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata))
        blob_headers = None
        access_conditions = get_access_conditions(lease)
        mod_conditions = get_modification_conditions(
            if_modified_since, if_unmodified_since, if_match, if_none_match)
        if content_settings:
            blob_headers = BlobHTTPHeaders(
                blob_cache_control=content_settings.cache_control,
                blob_content_type=content_settings.content_type,
                blob_content_md5=bytearray(content_settings.content_md5) if content_settings.content_md5 else None,
                blob_content_encoding=content_settings.content_encoding,
                blob_content_language=content_settings.content_language,
                blob_content_disposition=content_settings.content_disposition
            )

        if self.blob_type == BlobType.BlockBlob:
            adjusted_count = length
            if (self.key_encryption_key is not None) and (adjusted_count is not None):
                adjusted_count += (16 - (length % 16))

            # Do single put if the size is smaller than config.max_single_put_size
            if adjusted_count is not None and (adjusted_count < self._config.blob_settings.max_single_put_size):
                return self._client.block_blob.upload(
                    data,
                    content_length=adjusted_count,
                    timeout=timeout,
                    blob_http_headers=blob_headers,
                    lease_access_conditions=access_conditions,
                    modified_access_conditions=mod_conditions,
                    headers=headers,
                    cls=return_response_headers,
                    validate_content=validate_content,
                    **kwargs)
            else:
                cek, iv, encryption_data = None, None, None

                blob_settings = self._config.blob_settings
                use_original_upload_path = blob_settings.use_byte_buffer or \
                    validate_content or self.require_encryption or \
                    blob_settings.max_block_size < blob_settings.min_large_block_upload_threshold or \
                    hasattr(stream, 'seekable') and not stream.seekable() or \
                    not hasattr(stream, 'seek') or not hasattr(stream, 'tell')

                if use_original_upload_path:
                    if self.key_encryption_key:
                        cek, iv, encryption_data = _generate_blob_encryption_data(self.key_encryption_key)
                    block_ids = _upload_blob_chunks(
                        blob_service=self._client.block_blob,
                        blob_size=length,
                        block_size=blob_settings.max_block_size,
                        stream=stream,
                        max_connections=max_connections,
                        validate_content=validate_content,
                        access_conditions=access_conditions,
                        uploader_class=_BlockBlobChunkUploader,
                        timeout=timeout,
                        content_encryption_key=cek,
                        initialization_vector=iv,
                        **kwargs
                    )
                else:
                    block_ids = _upload_blob_substream_blocks(
                        blob_service=self._client.block_blob,
                        blob_size=length,
                        block_size=blob_settings.max_block_size,
                        stream=stream,
                        max_connections=max_connections,
                        validate_content=validate_content,
                        access_conditions=access_conditions,
                        uploader_class=_BlockBlobChunkUploader,
                        timeout=timeout,
                        **kwargs
                    )

                block_lookup = BlockLookupList(committed=[], uncommitted=[], latest=[])
                block_lookup.latest = [b.id for b in block_ids]
                return self._client.block_blob.commit_block_list(
                    block_lookup,
                    blob_http_headers=blob_headers,
                    lease_access_conditions=access_conditions,
                    timeout=timeout,
                    modified_access_conditions=mod_conditions,
                    cls=return_response_headers,
                    validate_content=validate_content,
                    headers=headers,
                    **kwargs)

        elif self.blob_type == BlobType.PageBlob:
            if length is None or length < 0:
                raise ValueError("A content length must be specified for a Page Blob.")
            if length % 512 != 0:
                raise ValueError("Invalid page blob size: {0}. "
                                 "The size must be aligned to a 512-byte boundary.".format(count))
            if premium_page_blob_tier:
                try:
                    headers['x-ms-access-tier'] = premium_page_blob_tier.value
                except AttributeError:
                    headers['x-ms-access-tier'] = premium_page_blob_tier
            if encryption_data is not None:
                headers['x-ms-meta-encryptiondata'] = encryption_data
            response = self._client.page_blob.create(
                content_length=0,
                blob_content_length=length,
                blob_sequence_number=None,
                blob_http_headers=blob_headers,
                timeout=timeout,
                lease_access_conditions=access_conditions,
                modified_access_conditions=mod_conditions,
                cls=return_response_headers,
                headers=headers,
                error_map=basic_error_map(),
                **kwargs)
            if length == 0:
                return response

            mod_conditions = get_modification_conditions(if_match=response['ETag'])
            return _upload_blob_chunks(
                blob_service=self._client.page_blob,
                blob_size=length,
                block_size=self._config.blob_settings.max_page_size,
                stream=stream,
                max_connections=max_connections,
                validate_content=validate_content,
                access_conditions=access_conditions,
                uploader_class=_PageBlobChunkUploader,
                modified_access_conditions=mod_conditions,
                timeout=timeout,
                content_encryption_key=cek,
                initialization_vector=iv,
                **kwargs
            )
        # TODO: Upload other blob types
        else:
            raise NotImplementedError("Other blob types not yet implemented.")

    def download_blob(
            self, offset=None,  # type: Optional[int]
            length=None,  # type: Optional[int]
            validate_content=False,  # type: bool
            lease=None,  # type: Union[Lease, str]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            timeout=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> Iterable[bytes]
        """
        TODO: Full download chunking needed.
        :returns: A iterable data generator (stream)
        """
        access_conditions = get_access_conditions(lease)
        mod_conditions = get_modification_conditions(
            if_modified_since, if_unmodified_since, if_match, if_none_match)

        # The service only provides transactional MD5s for chunks under 4MB.
        # If validate_content is on, get only max_chunk_get_size for the first
        # chunk so a transactional MD5 can be retrieved.
        first_get_size = self._config.blob_settings.max_single_get_size \
            if not validate_content else self._config.blob_settings.max_chunk_get_size

        range_header = None
        #if length or offset:
        initial_request_start = offset if offset is not None else 0

        if length is not None and length - offset < first_get_size:
            initial_request_end = length
        else:
            initial_request_end = initial_request_start + first_get_size - 1
        range_header = 'bytes={0}-{1}'.format(initial_request_start, initial_request_end)

        try:
            stream = self._client.blob.download(
                timeout=timeout,
                snapshot=self.snapshot,
                range=range_header,
                lease_access_conditions=access_conditions,
                modified_access_conditions=mod_conditions,
                error_map=basic_error_map(),
                validate_content=validate_content,
                cls=deserialize_blob_stream,
                **kwargs)
        except StorageErrorException as error:
            if error.response.status_code == 416:
                stream = self._client.blob.download(
                    timeout=timeout,
                    snapshot=self.snapshot,
                    range=None,
                    lease_access_conditions=access_conditions,
                    modified_access_conditions=mod_conditions,
                    error_map=basic_error_map(),
                    cls=deserialize_blob_stream,
                    **kwargs)
            else:
                process_storage_error(error)
        stream.properties.name = self.name
        stream.properties.container = self.container
        return stream

    def delete_blob(
            self, lease=None,  # type: Optional[Union[str, Lease]]
            delete_snapshots=None,  # type: Optional[str]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            timeout=None,  # type: Optional[int]
            **kwargs,
        ):
        # type: (...) -> None
        """
        Marks the specified blob or snapshot for deletion.
        The blob is later deleted during garbage collection.

        Note that in order to delete a blob, you must delete all of its
        snapshots. You can delete both at the same time with the Delete
        Blob operation.

        If a delete retention policy is enabled for the service, then this operation soft deletes the blob or snapshot
        and retains the blob or snapshot for specified number of days.
        After specified number of days, blob's data is removed from the service during garbage collection.
        Soft deleted blob or snapshot is accessible through List Blobs API specifying include=Include.Deleted option.
        Soft-deleted blob or snapshot can be restored using Undelete API.

        :param lease:
            Required if the blob has an active lease. Value can be a Lease object
            or the lease ID as a string.
        :type lease: ~azure.storage.blob.lease.Lease or str
        :param str delete_snapshots:
            Required if the blob has associated snapshots. Values include:
             - "only": Deletes only the blobs snapshots.
             - "include": Deletes the blob along with all snapshots.
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
        :rtype: None
        """
        access_conditions = get_access_conditions(lease)
        mod_conditions = get_modification_conditions(
            if_modified_since, if_unmodified_since, if_match, if_none_match)
        self._client.blob.delete(
            timeout=timeout,
            snapshot=self.snapshot,
            delete_snapshots=delete_snapshots,
            lease_access_conditions=access_conditions,
            modified_access_conditions=mod_conditions,
            error_map=basic_error_map(),
            **kwargs)

    def undelete_blob(self, timeout=None):
        # type: (Optional[int]) -> None
        """
        :returns: None
        """
        self._client.blob.undelete(timeout=timeout)

    def get_blob_properties(
            self, lease=None,  # type: Optional[Union[Lease, str]]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            timeout=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> BlobProperties
        """
        :returns: BlobProperties
        """
        access_conditions = get_access_conditions(lease)
        mod_conditions = get_modification_conditions(
            if_modified_since, if_unmodified_since, if_match, if_none_match)
        try:
            blob_props = self._client.blob.get_properties(
                timeout=timeout,
                snapshot=self.snapshot,
                lease_access_conditions=access_conditions,
                modified_access_conditions=mod_conditions,
                cls=deserialize_blob_properties,
                error_map=basic_error_map(),
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)
        blob_props.name = self.name
        blob_props.container = self.container
        return blob_props

    def set_blob_properties(
            self, content_settings=None,  # type: Optional[ContentSettings]
            lease=None,  # type: Optional[Union[Lease, str]]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            timeout=None  # type: Optional[int]
        ):
        # type: (...) -> None
        """
        Sets system properties on the blob. If one property is set for the
        content_settings, all properties will be overriden.

        :param ~azure.storage.blob.models.ContentSettings content_settings:
            ContentSettings object used to set blob properties.
        :param lease:
            Required if the blob has an active lease. Value can be a Lease object
            or the lease ID as a string.
        :type lease: ~azure.storage.blob.lease.Lease or str
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
        :returns: Blob-updated property dict (Etag and last modified)
        :rtype: Dict[str, Any]
        """
        access_conditions = get_access_conditions(lease)
        mod_conditions = get_modification_conditions(
            if_modified_since, if_unmodified_since, if_match, if_none_match)
        blob_headers = BlobHTTPHeaders(
            blob_cache_control=content_settings.cache_control,
            blob_content_type=content_settings.content_type,
            blob_content_md5=bytearray(content_settings.content_md5) if content_settings.content_md5 else None,
            blob_content_encoding=content_settings.content_encoding,
            blob_content_language=content_settings.content_language,
            blob_content_disposition=content_settings.content_disposition
        )
        return self._client.blob.set_http_headers(
            timeout=timeout,
            blob_http_headers=blob_headers,
            lease_access_conditions=access_conditions,
            modified_access_conditions=mod_conditions,
            cls=return_response_headers,
            error_map=basic_error_map()
        )

    def get_blob_metadata(
            self, lease=None,  # type: Optional[Union[Lease, str]]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            timeout=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> Dict[str, str]
        """
        :returns: A dict of metadata
        """
        access_conditions = get_access_conditions(lease)
        mod_conditions = get_modification_conditions(
            if_modified_since, if_unmodified_since, if_match, if_none_match)
        try:
            return self._client.blob.get_properties(
                comp='metadata',
                snapshot=self.snapshot,
                timeout=timeout,
                lease_access_conditions=access_conditions,
                modified_access_conditions=mod_conditions,
                cls=deserialize_metadata,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    def set_blob_metadata(
            self, metadata=None,  # type: Optional[Dict[str, str]]
            lease=None,  # type: Optional[Union[Lease, str]]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            timeout=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> Dict[str, Union[str, datetime]]
        """
        :returns: Blob-updated property dict (Etag and last modified)
        """
        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata))
        access_conditions = get_access_conditions(lease)
        mod_conditions = get_modification_conditions(
            if_modified_since, if_unmodified_since, if_match, if_none_match)
        return self._client.blob.set_metadata(
            timeout=timeout,
            lease_access_conditions=access_conditions,
            modified_access_conditions=mod_conditions,
            cls=return_response_headers,
            headers=headers,
            error_map=basic_error_map(),
            **kwargs
        )

    def create_blob(
            self, content_length=None,  # type: Optional[int]
            content_settings=None,  # type: Optional[ContentSettings]
            sequence_number=None,  # type: Optional[int]
            metadata=None, # type: Optional[Dict[str, str]]
            lease=None,  # type: Optional[Union[Lease, str]]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            timeout=None,  # type: Optional[int]
            premium_page_blob_tier=None,  # type: Optional[Union[str, PremiumPageBlobTier]]
            **kwargs
        ):
        # type: (...) -> Dict[str, Union[str, datetime]]
        """
        :returns: Blob-updated property dict (Etag and last modified).
        """
        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata))
        access_conditions = get_access_conditions(lease)
        mod_conditions = get_modification_conditions(
            if_modified_since, if_unmodified_since, if_match, if_none_match)
        blob_headers = None
        if content_settings:
            blob_headers = BlobHTTPHeaders(
                blob_cache_control=content_settings.cache_control,
                blob_content_type=content_settings.content_type,
                blob_content_md5=bytearray(content_settings.content_md5) if content_settings.content_md5 else None,
                blob_content_encoding=content_settings.content_encoding,
                blob_content_language=content_settings.content_language,
                blob_content_disposition=content_settings.content_disposition
            )
        if self.blob_type == BlobType.PageBlob:
            if content_length is None:
                raise ValueError("A content length must be specified for a Page Blob.")
            if premium_page_blob_tier:
                try:
                    headers['x-ms-access-tier'] = premium_page_blob_tier.value
                except AttributeError:
                    headers['x-ms-access-tier'] = premium_page_blob_tier
            return self._client.page_blob.create(
                content_length=0,
                blob_content_length=content_length,
                blob_sequence_number=sequence_number,
                blob_http_headers=blob_headers,
                timeout=timeout,
                lease_access_conditions=access_conditions,
                modified_access_conditions=mod_conditions,
                cls=return_response_headers,
                headers=headers,
                error_map=basic_error_map(),
                **kwargs
            )
        elif self.blob_type == BlobType.AppendBlob:
            if content_length or premium_page_blob_tier or sequence_number:
                raise ValueError("The following options cannot be used with Append Blobs: {}".format(
                    "\n".join("content_length", "premium_page_blob_tier", "sequence_number")))
            return self._client.append_blob.create(
                content_length=0,
                blob_http_headers=blob_headers,
                timeout=timeout,
                lease_access_conditions=access_conditions,
                modified_access_conditions=mod_conditions,
                cls=return_response_headers,
                headers=headers,
                error_map=basic_error_map(),
                **kwargs
            )
        else:
            raise TypeError("Create operation not supported by BlobClients of type BlockBlob.")

    def create_snapshot(
            self, metadata=None,  # type: Optional[Dict[str, str]]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            lease=None,  # type: Optional[Union[Lease, str]]
            timeout=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> SnapshotProperties
        """
        :returns: SnapshotProperties
        """
        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata))
        access_conditions = get_access_conditions(lease)
        mod_conditions = get_modification_conditions(
            if_modified_since, if_unmodified_since, if_match, if_none_match)
        properties = self._client.blob.create_snapshot(
            timeout=timeout,
            lease_access_conditions=access_conditions,
            modified_access_conditions=mod_conditions,
            cls=return_response_headers,
            headers=headers,
            **kwargs)
        snapshot = SnapshotProperties(**properties)
        snapshot.name = self.name
        snapshot.container = self.container
        snapshot.blob_type = self.blob_type
        return snapshot

    def copy_blob_from_source(
            self, copy_source,  # type: Any
            metadata=None,  # type: Optional[Dict[str, str]]
            source_if_modified_since=None,  # type: Optional[datetime]
            source_if_unmodified_since=None,  # type: Optional[datetime]
            source_if_match=None,  # type: Optional[str]
            source_if_none_match=None,  # type: Optional[str]
            destination_if_modified_since=None,  # type: Optional[datetime]
            destination_if_unmodified_since=None,  # type: Optional[datetime]
            destination_if_match=None,  # type: Optional[str]
            destination_if_none_match=None,  # type: Optional[str]
            destination_lease=None,  # type: Optional[Union[Lease, str]]
            source_lease=None,  # type: Optional[Union[Lease, str]]
            timeout=None,  # type: Optional[int]
            premium_page_blob_tier=None,
            requires_sync=None  # type: Optional[bool]
        ):
        # type: (...) -> Any
        """
        TODO: Fix type hints
        :returns: A pollable object to check copy operation status (and abort).
        """

    def acquire_lease(
            self, lease_duration=-1,  # type: int
            proposed_lease_id=None,  # type: Optional[str]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            timeout=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> Lease
        """
        :returns: A Lease object.
        """
        mod_conditions = get_modification_conditions(
            if_modified_since, if_unmodified_since, if_match, if_none_match)
        response = self._client.blob.acquire_lease(
            timeout=timeout,
            duration=lease_duration,
            proposed_lease_id=proposed_lease_id,
            modified_access_conditions=mod_conditions,
            cls=return_response_headers,
            **kwargs)
        return Lease(self._client.blob, **response)

    def break_lease(
            self, lease_break_period=None,  # type: Optional[int]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            timeout=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> int
        """
        :returns: Approximate time remaining in the lease period, in seconds.
        """
        mod_conditions = get_modification_conditions(
            if_modified_since, if_unmodified_since, if_match, if_none_match)
        response = self._client.blob.break_lease(
            timeout=timeout,
            break_period=lease_break_period,
            modified_access_conditions=mod_conditions,
            cls=return_response_headers,
            **kwargs)
        return response.get('x-ms-lease-time')

    def set_standard_blob_tier(self, standard_blob_tier, timeout=None, lease=None):
        # type: (Union[str, StandardBlobTier], Optional[int], Optional[Union[Lease, str]]) -> None
        """
        :raises: InvalidOperation when blob client type is not BlockBlob.
        :returns: None
        """
        access_conditions = get_access_conditions(lease)
        if standard_blob_tier is None:
            raise ValueError("A StandardBlobTier must be specified")
        self._client.blob.set_tier(
            tier=standard_blob_tier,
            timeout=timeout,
            lease_access_conditions=access_conditions
        )

    def stage_block(
            self, block_id,  # type: str
            data,  # type: Union[Iterable[AnyStr], IO[AnyStr]]
            length=None,  # type: Optional[int]
            validate_content=False,  # type: Optional[bool]
            lease=None,  # type: Optional[Union[Lease, str]]
            timeout=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> None
        """
        :raises: InvalidOperation when blob client type is not BlockBlob.
        :returns: None
        """
        block_id = encode_base64(str(block_id))
        access_conditions = get_access_conditions(lease)
        if not length:
            try:
                length = len(data)
            except TypeError:
                raise ValueError("Please specify content length.")
        self._client.block_blob.stage_block(
            block_id,
            length,
            data,
            transactional_content_md5=None,
            timeout=timeout,
            lease_access_conditions=access_conditions,
            validate_content=validate_content,
            **kwargs)

    def stage_block_from_url(
            self, block_id,  # type: str
            copy_source_url,  # type: str
            source_range_start,  # type: int
            source_range_end,  # type: int
            source_content_md5=None,  #type: Optional[str]
            lease=None,  # type: Optional[Union[Lease, str]]
            timeout=None # type: int
        ):
        # type: (...) -> None
        """
        :raises: InvalidOperation when blob client type is not BlockBlob.
        :returns: None
        """

    def get_block_list(
            self, block_list_type="committed",  # type: Optional[str]
            lease=None,  # type: Optional[Union[Lease, str]]
            timeout=None,  # type: int
            **kwargs
        ):
        # type: (...) -> Tuple[List[BlobBlock], List[BlobBlock]]
        """
        :raises: InvalidOperation when blob client type is not BlockBlob.
        :returns: A tuple of two sets - committed and uncommitted blocks
        """
        access_conditions = get_access_conditions(lease)
        blocks= self._client.block_blob.get_block_list(
            list_type=block_list_type,
            snapshot=self.snapshot,
            timeout=timeout,
            lease_access_conditions=access_conditions,
            **kwargs
        )
        committed = []
        uncommitted = []
        if blocks.committed_blocks:
            committed = [BlobBlock._from_generated(b) for b in blocks.committed_blocks]
        if blocks.uncommitted_blocks:
            uncommitted = [BlobBlock._from_generated(b) for b in blocks.uncommitted_blocks]
        return committed, uncommitted

    def commit_block_list(
            self, block_list,  # type: List[BlobBlock]
            lease=None,  # type: Optional[Union[Lease, str]]
            content_settings=None,  # type: Optional[ContentSettings]
            metadata=None,  # type: Optional[Dict[str, str]]
            validate_content=False,  # type: Optional[bool]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            timeout=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> Dict[str, Union[str, datetime]]
        """
        :raises: InvalidOperation when blob client type is not BlockBlob.
        :returns: Blob-updated property dict (Etag and last modified).
        """
        block_lookup = BlockLookupList(committed=[], uncommitted=[], latest=[])
        for block in block_list:
            if block.state.value == 'committed':
                block_lookup.committed.append(encode_base64(str(block.id)))
            elif block.state.value == 'uncommitted':
                block_lookup.uncommitted.append(encode_base64(str(block.id)))
            else:
                block_lookup.latest.append(encode_base64(str(block.id)))
        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata))
        blob_headers = None
        access_conditions = get_access_conditions(lease)
        mod_conditions = get_modification_conditions(
            if_modified_since, if_unmodified_since, if_match, if_none_match)
        if content_settings:
            blob_headers = BlobHTTPHeaders(
                blob_cache_control=content_settings.cache_control,
                blob_content_type=content_settings.content_type,
                blob_content_md5=bytearray(content_settings.content_md5) if content_settings.content_md5 else None,
                blob_content_encoding=content_settings.content_encoding,
                blob_content_language=content_settings.content_language,
                blob_content_disposition=content_settings.content_disposition
            )
        return self._client.block_blob.commit_block_list(
            block_lookup,
            blob_http_headers=blob_headers,
            lease_access_conditions=access_conditions,
            timeout=timeout,
            modified_access_conditions=mod_conditions,
            cls=return_response_headers,
            validate_content=validate_content,
            **kwargs)

    def set_premium_page_blob_tier(self, premium_page_blob_tier, timeout=None, lease=None, **kwargs):
        # type: (Union[str, PremiumPageBlobTier], Optional[int], Optional[Union[Lease, str]]) -> None
        """
        :raises: InvalidOperation when blob client type is not PageBlob.
        :returns: None
        """
        access_conditions = get_access_conditions(lease)
        if premium_page_blob_tier is None:
            raise ValueError("A PremiumPageBlobTiermust be specified")
        self._client.blob.set_tier(
            tier=premium_page_blob_tier,
            timeout=timeout,
            lease_access_conditions=access_conditions,
            **kwargs
        )

    def get_page_ranges(
            self, start_range=None, # type: Optional[int]
            end_range=None, # type: Optional[int]
            lease=None,  # type: Optional[Union[Lease, str]]
            previous_snapshot_diff=None,  # type: Optional[str]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            timeout=None, # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> List[PageRange]
        """
        :raises: InvalidOperation when blob client type is not PageBlob.
        :returns: A list of page ranges.
        """
        access_conditions = get_access_conditions(lease)
        mod_conditions = get_modification_conditions(
            if_modified_since, if_unmodified_since, if_match, if_none_match)
        page_range = None
        if start_range is not None and end_range is None:
            page_range = str(start_range)
        elif start_range is not None and end_range is not None:
            page_range = str(end_range - start_range + 1)
        if previous_snapshot_diff:
            try:
                prev_snapshot = previous_snapshot_diff.snapshot
            except AttributeError:
                prev_snapshot = previous_snapshot_diff
            ranges = self._client.page_blob.get_page_ranges_diff(
                snapshot=self.snapshot,
                prevsnapshot=prev_snapshot,
                lease_access_conditions=access_conditions,
                modified_access_conditions=mod_conditions,
                timeout=timeout,
                range=page_range,
                **kwargs
            )
        else:
            ranges = self._client.page_blob.get_page_ranges(
                snapshot=self.snapshot,
                lease_access_conditions=access_conditions,
                modified_access_conditions=mod_conditions,
                timeout=timeout,
                range=page_range,
                **kwargs
            )
        page_range = []
        clear_range = []
        if ranges.page_range:
            page_range = [{'start': b.start, 'end': b.end} for b in ranges.page_range]
        if ranges.clear_range:
            clear_range = [{'start': b.start, 'end': b.end} for b in ranges.clear_range]
        return page_range, clear_range

    def set_sequence_number(
            self, sequence_number_action,  # type: Union[str, SequenceNumberAction]
            sequence_number=None,  # type: Optional[str]
            lease=None,  # type: Optional[Union[Lease, str]]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            timeout=None, # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> Dict[str, Union[str, datetime]]
        """
        :raises: InvalidOperation when blob client type is not PageBlob.
        :returns: Blob-updated property dict (Etag and last modified).
        """
        access_conditions = get_access_conditions(lease)
        mod_conditions = get_modification_conditions(
            if_modified_since, if_unmodified_since, if_match, if_none_match)
        if sequence_number_action is None:
            raise ValueError("A sequence number action must be specified")
        return self._client.page_blob.update_sequence_number(
            sequence_number_action=sequence_number_action,
            timeout=timeout,
            blob_sequence_number=sequence_number,
            lease_access_conditions=access_conditions,
            modified_access_conditions=mod_conditions,
            cls=return_response_headers,
            **kwargs
        )

    def resize_blob(
            self, content_length,  # type: int
            lease=None,  # type: Optional[Union[Lease, str]]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            timeout=None, # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> Dict[str, Union[str, datetime]]
        """
        :raises: InvalidOperation when blob client type is not PageBlob.
        :returns: Blob-updated property dict (Etag and last modified).
        """
        access_conditions = get_access_conditions(lease)
        mod_conditions = get_modification_conditions(
            if_modified_since, if_unmodified_since, if_match, if_none_match)
        if content_length is None:
            raise ValueError("A content length must be specified for a Page Blob.")
        return self._client.page_blob.resize(
            blob_content_length=content_length,
            timeout=timeout,
            lease_access_conditions=access_conditions,
            modified_access_conditions=mod_conditions,
            cls=return_response_headers,
            **kwargs
        )

    def upload_page(
            self, page,  # type: bytes
            start_range,  # type: int
            end_range,  # type: int
            length=None,  # type: Optional[int]
            lease=None,  # type: Optional[Union[Lease, str]]
            validate_content=False,  # type: Optional[bool]
            if_sequence_number_lte=None, # type: Optional[int]
            if_sequence_number_lt=None, # type: Optional[int]
            if_sequence_number_eq=None, # type: Optional[int]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            timeout=None, # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> Dict[str, Union[str, datetime]]
        """
        :raises: InvalidOperation when blob client type is not PageBlob.
        :returns: Blob-updated property dict (Etag and last modified).
        """
        if self.require_encryption and not self.key_encryption_key:
            raise ValueError("Encryption required but no key was provided.")
        cek, iv, encryption_data = None, None, None
        if self.key_encryption_key is not None:
            cek, iv, encryption_data = _generate_blob_encryption_data(self.key_encryption_key)
        headers = kwargs.pop('headers', {})
        if encryption_data is not None:
                headers['x-ms-meta-encryptiondata'] = encryption_data
        if not length:
            try:
                length = len(page)
            except TypeError:
                raise ValueError("Please specifiy content length.")
        if start_range is None or start_range % 512 != 0:
            raise ValueError("start_range must be an integer that aligns with 512 page size")
        if end_range is None or end_range % 512 != 511:
            raise ValueError("end_range must be an integer that aligns with 512 page size")
        content_range = 'bytes={0}-{1}'.format(start_range, end_range)
        access_conditions = get_access_conditions(lease)
        seq_conditions = get_sequence_conditions(
            if_sequence_number_lte=if_sequence_number_lte,
            if_sequence_number_lt=if_sequence_number_lt,
            if_sequence_number_eq=if_sequence_number_eq
        )
        mod_conditions = get_modification_conditions(
            if_modified_since, if_unmodified_since, if_match, if_none_match)
        return self._client.page_blob.upload_pages(
            page,
            content_length=length,
            transactional_content_md5=None,
            timeout=timeout,
            range=content_range,
            lease_access_conditions=access_conditions,
            sequence_number_access_conditions=seq_conditions,
            modified_access_conditions=mod_conditions,
            validate_content=validate_content,
            cls=return_response_headers,
            **kwargs
        )

    def clear_page(
            self, start_range,  # type: int
            end_range,  # type: int
            lease=None,  # type: Optional[Union[Lease, str]]
            if_sequence_number_lte=None, # type: Optional[int]
            if_sequence_number_lt=None, # type: Optional[int]
            if_sequence_number_eq=None, # type: Optional[int]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            timeout=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> Dict[str, Union[str, datetime]]
        """
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
        :raises: InvalidOperation when blob client type is not PageBlob.
        :returns: Blob-updated property dict (Etag and last modified).
        """
        access_conditions = get_access_conditions(lease)
        seq_conditions = get_sequence_conditions(
            if_sequence_number_lte=if_sequence_number_lte,
            if_sequence_number_lt=if_sequence_number_lt,
            if_sequence_number_eq=if_sequence_number_eq
        )
        mod_conditions = get_modification_conditions(
            if_modified_since, if_unmodified_since, if_match, if_none_match)
        if start_range is None or start_range % 512 != 0:
            raise ValueError("start_range must be an integer that aligns with 512 page size")
        if end_range is None or end_range % 512 != 511:
            raise ValueError("end_range must be an integer that aligns with 512 page size")
        content_range = 'bytes={0}-{1}'.format(start_range, end_range)
        return self._client.page_blob.clear_pages(
            content_length=0,
            timeout=timeout,
            range=content_range,
            lease_access_conditions=access_conditions,
            sequence_number_access_conditions=seq_conditions,
            modified_access_conditions=mod_conditions,
            cls=return_response_headers,
            **kwargs
        )

    def incremental_copy(
            self, copy_source,  # type: str
            metadata=None,  # type: Optional[Dict[str, str]]
            destination_if_modified_since=None,  # type: Optional[datetime]
            destination_if_unmodified_since=None,  # type: Optional[datetime]                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
            destination_if_match=None,  # type: Optional[str]
            destination_if_none_match=None,  # type: Optional[str]
            destination_lease=None,  # type: Optional[Union[str, Lease]]
            source_lease=None,  # type: Optional[Union[str, Lease]]
            timeout=None  # type: Optional[int]
        ):
        # type: (...) -> Any
        """
        Copies an incremental copy of a blob asynchronously.

        The Blob service copies blobs on a best-effort basis.
        The source blob for an incremental copy operation must be a page blob.
        Call get_blob_properties on the destination blob to check the status of the copy operation.
        The final blob will be committed when the copy completes.

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
        :param str destination_if_match:
            An ETag value, or the wildcard character (*). Specify an ETag value for
            this conditional header to copy the blob only if the specified ETag value
            matches the ETag value for an existing destination blob. If the ETag for
            the destination blob does not match the ETag specified for If-Match, the
            Blob service returns status code 412 (Precondition Failed).
        :param str destination_if_none_match:
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
        :raises: InvalidOperation when blob client type is not PageBlob.
        :returns: A pollable object to check copy operation status (and abort).
        """

    def append_block(
            self, data,  # type: Union[Iterable[AnyStr], IO[AnyStr]]
            validate_content=False,  # type: Optional[bool]
            maxsize_condition=None,  # type: Optional[int]
            appendpos_condition=None,  # type: Optional[int]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[datetime]
            timeout=None  # type: Optional[int]
        ):
        # type: (...) -> Dict[str, Union[str, datetime, int]]
        """
        :raises: InvalidOperation when blob client type is not AppendBlob.
        :returns: Blob-updated property dict (Etag, last modified, append offset, committed block count).
        """
