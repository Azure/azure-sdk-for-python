# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import sys
from io import BytesIO
from typing import (  # pylint: disable=unused-import
    Union, Optional, Any, IO, Iterable, AnyStr, Dict, List, Tuple,
    TYPE_CHECKING
)
try:
    from urllib.parse import urlparse, quote, unquote, parse_qs
except ImportError:
    from urlparse import urlparse, parse_qs
    from urllib2 import quote, unquote

import six
from azure.core import Configuration

from .common import BlobType, LocationMode
from .lease import LeaseClient
from .models import BlobBlock
from .polling import CopyBlob, CopyStatusPoller
from ._shared_access_signature import BlobSharedAccessSignature
from ._encryption import _generate_blob_encryption_data, _encrypt_blob
from ._utils import (
    StorageAccountHostsMixin,
    create_client,
    create_configuration,
    create_pipeline,
    get_access_conditions,
    get_modification_conditions,
    get_sequence_conditions,
    return_response_headers,
    add_metadata_headers,
    process_storage_error,
    encode_base64,
    get_length,
    read_length,
    parse_connection_str,
    parse_query,
    is_credential_sastoken,
    validate_and_format_range_headers,
    parse_length_from_content_range
)
from ._deserialize import (
    deserialize_blob_properties,
    deserialize_metadata
)
from ._generated.models import (
    BlobHTTPHeaders,
    BlockLookupList,
    StorageErrorException,
    AppendPositionAccessConditions)
from ._download_chunking import StorageStreamDownloader
from ._upload_chunking import (
    _upload_blob_chunks,
    _upload_blob_substream_blocks,
    _PageBlobChunkUploader,
    _BlockBlobChunkUploader,
    _AppendBlobChunkUploader,
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
    )

_ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION = (
    'The require_encryption flag is set, but encryption is not supported'
    ' for this method.')


class BlobClient(StorageAccountHostsMixin):  # pylint: disable=too-many-public-methods

    def __init__(
            self, blob_url,  # type: str
            container=None,  # type: Optional[Union[str, ContainerProperties]]
            blob=None,  # type: Optional[Union[str, BlobProperties]]
            snapshot=None,  # type: Optional[Union[str, Dict[str, Any]]]
            credential=None,  # type: Optional[Any]
            configuration=None,  # type: Optional[Configuration]
            **kwargs  # type: Any
        ):
        # type: (...) -> None
        """Creates a new BlobClient. This client represents interaction with a specific
        blob, although that blob may not yet exist.

        :param str url: The full URI to the blob. This can also be a URL to the storage account
         or container, in which case the blob and/or container must also be specified.
        :param container: The container for the blob. If specified, this value will override
         a container value specified in the blob URL.
        :type container: str or ~azure.storage.blob.models.ContainerProperties
        :param blob: The blob with which to interact. If specified, this value will override
         a blob value specified in the blob URL.
        :type blob: str or ~azure.storage.blob.models.BlobProperties
        :param credential:
        :param configuration: A optional pipeline configuration.
         This can be retrieved with :func:`BlobClient.create_configuration()`
        """
        try:
            if not blob_url.lower().startswith('http'):
                blob_url = "https://" + blob_url
        except AttributeError:
            raise ValueError("Blob URL must be a string.")
        parsed_url = urlparse(blob_url.rstrip('/'))
        if not parsed_url.path and not (container and blob):
            raise ValueError("Please specify a container and blob name.")
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(blob_url))

        path_container = ""
        path_blob = ""
        path_snapshot = None
        if parsed_url.path:
            path_container, _, path_blob = parsed_url.path.lstrip('/').partition('/')
        path_snapshot, sas_token = parse_query(parsed_url.query)

        try:
            self.container_name = container.name
        except AttributeError:
            self.container_name = container or unquote(path_container)
        try:
            self.snapshot = snapshot.snapshot
        except AttributeError:
            try:
                self.snapshot = snapshot['snapshot']
            except TypeError:
                self.snapshot = snapshot or path_snapshot
        try:
            self.blob_name = blob.name
            if not snapshot:
                self.snapshot = blob.snapshot
        except AttributeError:
            self.blob_name = blob or unquote(path_blob)
        self._query_str, credential = self._format_query_string(sas_token, credential, self.snapshot)
        super(BlobClient, self).__init__(parsed_url, credential, configuration, **kwargs)

    def _format_url(self, hostname):
        container_name = self.container_name
        if isinstance(container_name, six.text_type):
            container_name = container_name.encode('UTF-8')
        return "{}://{}/{}/{}{}".format(
            self.scheme,
            hostname,
            quote(container_name),
            quote(self.blob_name, safe='~'),
            self._query_str)

    @classmethod
    def from_connection_string(
            cls, conn_str,  # type: str
            container,  # type: Union[str, ContainerProperties]
            blob,  # type: Union[str, BlobProperties]
            snapshot=None,  # type: Optional[str]
            credential=None,  # type: Optional[Any]
            configuration=None,  # type: Optional[Configuration]
            **kwargs  # type: Any
        ):
        """
        Create BlobClient from a Connection String.
        """
        account_url, secondary, credential = parse_connection_str(conn_str, credential)
        if 'secondary_hostname' not in kwargs:
            kwargs['secondary_hostname'] = secondary
        return cls(
            account_url, container=container, blob=blob, snapshot=snapshot,
            credential=credential, configuration=configuration, **kwargs)

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
        if not hasattr(self.credential, 'account_key') or not self.credential.account_key:
            raise ValueError("No account SAS key available.")
        sas = BlobSharedAccessSignature(self.credential.account_name, self.credential.account_key)
        return sas.generate_blob(
            self.container_name,
            self.blob_name,
            permission,
            expiry,
            start=start,
            policy_id=policy_id,
            ip=ip,
            protocol=protocol,
            cache_control=cache_control,
            content_disposition=content_disposition,
            content_encoding=content_encoding,
            content_language=content_language,
            content_type=content_type,
        )

    def get_account_information(self, timeout=None):
        # type: (Optional[int]) -> Dict[str, str]
        """
        :returns: A dict of account information (SKU and account type).
        """
        try:
            return self._client.blob.get_account_info(cls=return_response_headers)
        except StorageErrorException as error:
            process_storage_error(error)

    def upload_blob(
            self, data,  # type: Union[Iterable[AnyStr], IO[AnyStr]]
            blob_type=BlobType.BlockBlob,  # type: Union[str, BlobType]
            length=None,  # type: Optional[int]
            metadata=None,  # type: Optional[Dict[str, str]]
            content_settings=None,  # type: Optional[ContentSettings]
            validate_content=False,  # type: Optional[bool]
            lease=None,  # type: Optional[Union[LeaseClient, str]]
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
        :param ~azure.storage.blob.common.BlobType blob_type: The type of the blob. This can be
         either BlockBlob, PageBlob or AppendBlob. The default value is BlockBlob.
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
            stream = IterStreamer(data, encoding=encoding)
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
        try:
            if blob_type == BlobType.BlockBlob:
                adjusted_count = length
                if (self.key_encryption_key is not None) and (adjusted_count is not None):
                    adjusted_count += (16 - (length % 16))

                # Do single put if the size is smaller than config.max_single_put_size
                if adjusted_count is not None and (adjusted_count < self._config.blob_settings.max_single_put_size):
                    try:
                        data = data.read(length)
                        if not isinstance(data, six.binary_type):
                            raise TypeError('blob data should be of type bytes.')
                    except AttributeError:
                        pass
                    if self.key_encryption_key:
                        encryption_data, data = _encrypt_blob(data, self.key_encryption_key)
                        headers['x-ms-meta-encryptiondata'] = encryption_data
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
                        data_stream_total=adjusted_count,
                        upload_stream_current=0,
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
                            headers['x-ms-meta-encryptiondata'] = encryption_data
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

            elif blob_type == BlobType.PageBlob:
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
                    **kwargs)
                if length == 0:
                    return response

                mod_conditions = get_modification_conditions(if_match=response['etag'])
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
            elif blob_type == BlobType.AppendBlob:
                if self.require_encryption or (self.key_encryption_key is not None):
                    raise ValueError(_ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)
                if length == 0:
                    return {}
                append_conditions = AppendPositionAccessConditions(
                    max_size=maxsize_condition,
                    append_condition=None)
                return _upload_blob_chunks(
                    blob_service=self._client.append_blob,
                    blob_size=length,
                    block_size=self._config.blob_settings.max_block_size,
                    stream=stream,
                    append_conditions=append_conditions,
                    max_connections=max_connections,
                    validate_content=validate_content,
                    access_conditions=access_conditions,
                    uploader_class=_AppendBlobChunkUploader,
                    modified_access_conditions=mod_conditions,
                    timeout=timeout,
                    **kwargs
                )
        except StorageErrorException as error:
            process_storage_error(error)

    def download_blob(
            self, offset=None,  # type: Optional[int]
            length=None,  # type: Optional[int]
            validate_content=False,  # type: bool
            lease=None,  # type: Union[LeaseClient, str]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            timeout=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> Iterable[bytes]
        """
        :returns: A iterable data generator (stream)
        """
        if self.require_encryption and not self.key_encryption_key:
            raise ValueError("Encryption required but no key was provided.")
        if length is not None and offset is None:
            raise ValueError("Offset value must not be None is length is set.")

        access_conditions = get_access_conditions(lease)
        mod_conditions = get_modification_conditions(
            if_modified_since, if_unmodified_since, if_match, if_none_match)

        return StorageStreamDownloader(
            name=self.blob_name,
            container=self.container_name,
            service=self._client.blob,
            config=self._config.blob_settings,
            offset=offset,
            length=length,
            validate_content=validate_content,
            access_conditions=access_conditions,
            mod_conditions=mod_conditions,
            timeout=timeout,
            require_encryption=self.require_encryption,
            key_encryption_key=self.key_encryption_key,
            key_resolver_function=self.key_resolver_function,
            **kwargs)

    def delete_blob(
            self, lease=None,  # type: Optional[Union[str, LeaseClient]]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            timeout=None,  # type: Optional[int]
            **kwargs
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
            Required if the blob has an active lease. Value can be a LeaseClient object
            or the lease ID as a string.
        :type lease: ~azure.storage.blob.lease.LeaseClient or str
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
        if not self.snapshot:
            kwargs['delete_snapshots'] = "include"
        try:
            self._client.blob.delete(
                timeout=timeout,
                snapshot=self.snapshot,
                lease_access_conditions=access_conditions,
                modified_access_conditions=mod_conditions,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    def delete_blob_snapshots(
            self, lease=None,  # type: Optional[Union[str, LeaseClient]]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            timeout=None,  # type: Optional[int]
            **kwargs
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
            Required if the blob has an active lease. Value can be a LeaseClient object
            or the lease ID as a string.
        :type lease: ~azure.storage.blob.lease.LeaseClient or str
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
        if self.snapshot:
            raise ValueError("This operation cannot be performed on a snapshot.")
        try:
            self._client.blob.delete(
                timeout=timeout,
                delete_snapshots="only",
                lease_access_conditions=access_conditions,
                modified_access_conditions=mod_conditions,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    def undelete_blob(self, timeout=None, **kwargs):
        # type: (Optional[int]) -> None
        """
        :returns: None
        """
        try:
            self._client.blob.undelete(timeout=timeout, **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    def get_blob_properties(
            self, lease=None,  # type: Optional[Union[LeaseClient, str]]
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
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)
        blob_props.name = self.blob_name
        blob_props.container = self.container_name
        return blob_props

    def set_http_headers(
            self, content_settings=None,  # type: Optional[ContentSettings]
            lease=None,  # type: Optional[Union[LeaseClient, str]]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            timeout=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> None
        """
        Sets system properties on the blob. If one property is set for the
        content_settings, all properties will be overriden.

        :param ~azure.storage.blob.models.ContentSettings content_settings:
            ContentSettings object used to set blob properties.
        :param lease:
            Required if the blob has an active lease. Value can be a LeaseClient object
            or the lease ID as a string.
        :type lease: ~azure.storage.blob.lease.LeaseClient or str
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
        try:
            return self._client.blob.set_http_headers(
                timeout=timeout,
                blob_http_headers=blob_headers,
                lease_access_conditions=access_conditions,
                modified_access_conditions=mod_conditions,
                cls=return_response_headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    def set_blob_metadata(
            self, metadata=None,  # type: Optional[Dict[str, str]]
            lease=None,  # type: Optional[Union[LeaseClient, str]]
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
        try:
            return self._client.blob.set_metadata(
                timeout=timeout,
                lease_access_conditions=access_conditions,
                modified_access_conditions=mod_conditions,
                cls=return_response_headers,
                headers=headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    def create_page_blob(
            self, size,  # type: int
            content_settings=None,  # type: Optional[ContentSettings]
            sequence_number=None,  # type: Optional[int]
            metadata=None, # type: Optional[Dict[str, str]]
            lease=None,  # type: Optional[Union[LeaseClient, str]]
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
        Creates a new Page or Append Blob depending on the current blob type
        of the client.

        :param int size:
            This header specifies the maximum size
            for the page blob, up to 1 TB. The page blob size must be aligned
            to a 512-byte boundary.
        :param ~azure.storage.blob.models.ContentSettings content_settings:
            ContentSettings object used to set properties on the blob.
        :param int sequence_number:
            Only for Page blobs. The sequence number is a user-controlled value that you can use to
            track requests. The value of the sequence number must be between 0
            and 2^63 - 1.The default value is 0.
        :param metadata:
            Name-value pairs associated with the blob as metadata.
        :type metadata: dict(str, str)
        :param ~azure.storage.blob.lease.LeaseClient lease:
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
        :param ~azure.storage.blob.common.PremiumPageBlobTier premium_page_blob_tier:
            A page blob tier value to set the blob to. The tier correlates to the size of the
            blob and number of allowed IOPS. This is only applicable to page blobs on
            premium storage accounts.
        :returns: Blob-updated property dict (Etag and last modified).
        :rtype: dict(str, Any)
        """
        if self.require_encryption or (self.key_encryption_key is not None):
            raise ValueError(_ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)
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
        try:
            if premium_page_blob_tier:
                try:
                    headers['x-ms-access-tier'] = premium_page_blob_tier.value
                except AttributeError:
                    headers['x-ms-access-tier'] = premium_page_blob_tier
            return self._client.page_blob.create(
                content_length=0,
                blob_content_length=size,
                blob_sequence_number=sequence_number,
                blob_http_headers=blob_headers,
                timeout=timeout,
                lease_access_conditions=access_conditions,
                modified_access_conditions=mod_conditions,
                cls=return_response_headers,
                headers=headers,
                **kwargs
            )
        except StorageErrorException as error:
            process_storage_error(error)

    def create_append_blob(
            self, content_settings=None,  # type: Optional[ContentSettings]
            metadata=None, # type: Optional[Dict[str, str]]
            lease=None,  # type: Optional[Union[LeaseClient, str]]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            timeout=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> Dict[str, Union[str, datetime]]
        """
        Creates a new Append Blob.

        :param ~azure.storage.blob.models.ContentSettings content_settings:
            ContentSettings object used to set properties on the blob.
        :param metadata:
            Name-value pairs associated with the blob as metadata.
        :type metadata: dict(str, str)
        :param ~azure.storage.blob.lease.LeaseClient lease:
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
        :returns: Blob-updated property dict (Etag and last modified).
        :rtype: dict(str, Any)
        """
        if self.require_encryption or (self.key_encryption_key is not None):
            raise ValueError(_ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)
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
        try:
            return self._client.append_blob.create(
                content_length=0,
                blob_http_headers=blob_headers,
                timeout=timeout,
                lease_access_conditions=access_conditions,
                modified_access_conditions=mod_conditions,
                cls=return_response_headers,
                headers=headers,
                **kwargs
            )
        except StorageErrorException as error:
            process_storage_error(error)

    def create_snapshot(
            self, metadata=None,  # type: Optional[Dict[str, str]]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            lease=None,  # type: Optional[Union[LeaseClient, str]]
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
        try:
            return self._client.blob.create_snapshot(
                timeout=timeout,
                lease_access_conditions=access_conditions,
                modified_access_conditions=mod_conditions,
                cls=return_response_headers,
                headers=headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    def copy_blob_from_url(
            self, source_url,  # type: str
            metadata=None,  # type: Optional[Dict[str, str]]
            source_if_modified_since=None,  # type: Optional[datetime]
            source_if_unmodified_since=None,  # type: Optional[datetime]
            source_if_match=None,  # type: Optional[str]
            source_if_none_match=None,  # type: Optional[str]
            destination_if_modified_since=None,  # type: Optional[datetime]
            destination_if_unmodified_since=None,  # type: Optional[datetime]
            destination_if_match=None,  # type: Optional[str]
            destination_if_none_match=None,  # type: Optional[str]
            destination_lease=None,  # type: Optional[Union[LeaseClient, str]]
            source_lease=None,  # type: Optional[Union[LeaseClient, str]]
            timeout=None,  # type: Optional[int]
            incremental_copy=False, # type bool,
            premium_page_blob_tier=None,
            requires_sync=False,  # type: Optional[bool]
            polling=True,  # type: bool
            **kwargs
        ):
        # type: (...) -> Any
        """
        Copies a blob asynchronously. This operation returns a copy operation 
        object that can be used to wait on the completion of the operation,
        as well as check status or abort the copy operation.
        The Blob service copies blobs on a best-effort basis.

        The source blob for a copy operation may be a block blob, an append blob, 
        or a page blob. If the destination blob already exists, it must be of the 
        same blob type as the source blob. Any existing destination blob will be 
        overwritten. The destination blob cannot be modified while a copy operation 
        is in progress.

        When copying from a page blob, the Blob service creates a destination page 
        blob of the source blob's length, initially containing all zeroes. Then 
        the source page ranges are enumerated, and non-empty ranges are copied. 

        For a block blob or an append blob, the Blob service creates a committed 
        blob of zero length before returning from this operation. When copying 
        from a block blob, all committed blocks and their block IDs are copied. 
        Uncommitted blocks are not copied. At the end of the copy operation, the 
        destination blob will have the same committed block count as the source.

        When copying from an append blob, all committed blocks are copied. At the 
        end of the copy operation, the destination blob will have the same committed 
        block count as the source.

        For all blob types, you can call status() on the returned polling object 
        to check the status of the copy operation, or wait() to block until the
        operation is complete. The final blob will be committed when the copy completes.

        :param str source_url:
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
        :param str source_if_match:
            An ETag value, or the wildcard character (*). Specify this conditional
            header to copy the source blob only if its ETag matches the value
            specified. If the ETag values do not match, the Blob service returns
            status code 412 (Precondition Failed). This header cannot be specified
            if the source is an Azure File.
        :param str source_if_none_match:
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
        :returns: A pollable object to check copy operation status (and abort).
        :rtype: :class:`~azure.storage.blob.polling.CopyStatusPoller`
        """
        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata))
        if source_lease:
            try:
                headers['x-ms-source-lease-id'] = source_lease.id
            except AttributeError:
                headers['x-ms-source-lease-id'] = source_lease
        if premium_page_blob_tier:
            headers['x-ms-access-tier'] = premium_page_blob_tier.value
        if requires_sync:
            headers['x-ms-requires-sync'] = str(requires_sync)

        dest_access_conditions = get_access_conditions(destination_lease)
        dest_mod_conditions = get_modification_conditions(
            destination_if_modified_since,
            destination_if_unmodified_since,
            destination_if_match,
            destination_if_none_match)
        try:
            if incremental_copy:
                start_copy = self._client.page_blob.copy_incremental(
                    source_url,
                    timeout=None,
                    modified_access_conditions=dest_mod_conditions,
                    headers=headers,
                    cls=return_response_headers,
                    **kwargs)
            else:
                source_mod_conditions = get_modification_conditions(
                    source_if_modified_since,
                    source_if_unmodified_since,
                    source_if_match,
                    source_if_none_match)
                start_copy = self._client.blob.start_copy_from_url(
                    source_url,
                    timeout=timeout,
                    source_modified_access_conditions=source_mod_conditions,
                    modified_access_conditions=dest_mod_conditions,
                    lease_access_conditions=dest_access_conditions,
                    headers=headers,
                    cls=return_response_headers,
                    **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

        poller = CopyStatusPoller(
            self, start_copy,
            polling=polling,
            configuration=self._config,
            lease_access_conditions=destination_lease,
            timeout=timeout)
        return poller

    def acquire_lease(
            self, lease_duration=-1,  # type: int
            lease_id=None,  # type: Optional[str]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            timeout=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> LeaseClient
        """
        :returns: A LeaseClient object.
        """
        lease = LeaseClient(self, lease_id=lease_id)
        lease.acquire(
            lease_duration=lease_duration,
            if_modified_since=if_modified_since,
            if_unmodified_since=if_unmodified_since,
            if_match=if_match,
            if_none_match=if_none_match,
            timeout=timeout,
            **kwargs)
        return lease

    def set_standard_blob_tier(self, standard_blob_tier, timeout=None, lease=None):
        # type: (Union[str, StandardBlobTier], Optional[int], Optional[Union[LeaseClient, str]]) -> None
        """
        :raises: TypeError when blob client type is not BlockBlob.
        :returns: None
        """
        access_conditions = get_access_conditions(lease)
        if standard_blob_tier is None:
            raise ValueError("A StandardBlobTier must be specified")
        try:
            self._client.blob.set_tier(
                tier=standard_blob_tier,
                timeout=timeout,
                lease_access_conditions=access_conditions)
        except StorageErrorException as error:
            process_storage_error(error)

    def stage_block(
            self, block_id,  # type: str
            data,  # type: Union[Iterable[AnyStr], IO[AnyStr]]
            length=None,  # type: Optional[int]
            validate_content=False,  # type: Optional[bool]
            lease=None,  # type: Optional[Union[LeaseClient, str]]
            encoding='UTF-8',  # type: str
            timeout=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> None
        """
        :raises: TypeError when blob client type is not BlockBlob.
        :returns: None
        """
        if self.require_encryption or (self.key_encryption_key is not None):
            raise ValueError(_ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)
        block_id = encode_base64(str(block_id))
        if isinstance(data, six.text_type):
            data = data.encode(encoding)
        access_conditions = get_access_conditions(lease)
        if length is None:
            length = get_length(data)
            if length is None:
                length, data = read_length(data)
        if isinstance(data, bytes):
            data = data[:length]
        try:
            self._client.block_blob.stage_block(
                block_id,
                length,
                data,
                transactional_content_md5=None,
                timeout=timeout,
                lease_access_conditions=access_conditions,
                validate_content=validate_content,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    def stage_block_from_url(
            self, block_id,  # type: str
            source_url,  # type: str
            source_offset=None,  # type: Optional[int]
            source_length=None,  # type: Optional[int]
            source_content_md5=None,  # type: Optional[Union[bytes, bytearray]]
            lease=None,  # type: Optional[Union[LeaseClient, str]]
            timeout=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> None
        """
        :returns: None
        """
        if source_length is not None and source_offset is None:
            raise ValueError("Source offset value must not be None is length is set.")
        block_id = encode_base64(str(block_id))
        access_conditions = get_access_conditions(lease)
        range_header = None
        if source_offset is not None:
            range_header, _ = validate_and_format_range_headers(source_offset, source_length)
        try:
            self._client.block_blob.stage_block_from_url(
                block_id,
                content_length=0,
                source_url=source_url,
                source_range=range_header,
                source_content_md5=bytearray(source_content_md5) if source_content_md5 else None,
                timeout=timeout,
                lease_access_conditions=access_conditions,
                cls=return_response_headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    def get_block_list(
            self, block_list_type="committed",  # type: Optional[str]
            lease=None,  # type: Optional[Union[LeaseClient, str]]
            timeout=None,  # type: int
            **kwargs
        ):
        # type: (...) -> Tuple[List[BlobBlock], List[BlobBlock]]
        """
        The Get Block List operation retrieves the list of blocks that have
        been uploaded as part of a block blob.

        :param str list_type:
            Specifies whether to return the list of committed
            blocks, the list of uncommitted blocks, or both lists together.
            Possible values include: 'committed', 'uncommitted', 'all'
        :param str lease:
            Required if the blob has an active lease.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: A tuple of two sets - committed and uncommitted blocks
        """
        access_conditions = get_access_conditions(lease)
        try:
            blocks= self._client.block_blob.get_block_list(
                list_type=block_list_type,
                snapshot=self.snapshot,
                timeout=timeout,
                lease_access_conditions=access_conditions,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)
        committed = []
        uncommitted = []
        if blocks.committed_blocks:
            committed = [BlobBlock._from_generated(b) for b in blocks.committed_blocks]
        if blocks.uncommitted_blocks:
            uncommitted = [BlobBlock._from_generated(b) for b in blocks.uncommitted_blocks]
        return committed, uncommitted

    def commit_block_list(
            self, block_list,  # type: List[BlobBlock]
            lease=None,  # type: Optional[Union[LeaseClient, str]]
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
        The Commit Block List operation writes a blob by specifying the list of
        block IDs that make up the blob.

        :param list block_list:
            List of Bloclblobs.
        :param str lease:
            Required if the blob has an active lease.
        :param ~azure.storage.blob.models.ContentSettings content_settings:
            ContentSettings object used to set blob properties.
        :param metadata:
            Name-value pairs associated with the blob as metadata.
        :param bool validate_content:
            If true, calculates an MD5 hash of the page content. The storage 
            service checks the hash of the content that has arrived
            with the hash that was sent. This is primarily valuable for detecting 
            bitflips on the wire if using http instead of https as https (the default) 
            will already validate. Note that this MD5 hash is not stored with the 
            blob.
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
        :returns: Blob-updated property dict (Etag and last modified).
        """
        if self.require_encryption or (self.key_encryption_key is not None):
            raise ValueError(_ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)
        block_lookup = BlockLookupList(committed=[], uncommitted=[], latest=[])
        for block in block_list:
            try:
                if block.state.value == 'committed':
                    block_lookup.committed.append(encode_base64(str(block.id)))
                elif block.state.value == 'uncommitted':
                    block_lookup.uncommitted.append(encode_base64(str(block.id)))
                else:
                    block_lookup.latest.append(encode_base64(str(block.id)))
            except AttributeError:
                block_lookup.latest.append(encode_base64(str(block)))
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
        try:
            return self._client.block_blob.commit_block_list(
                block_lookup,
                blob_http_headers=blob_headers,
                lease_access_conditions=access_conditions,
                timeout=timeout,
                modified_access_conditions=mod_conditions,
                cls=return_response_headers,
                validate_content=validate_content,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    def set_premium_page_blob_tier(self, premium_page_blob_tier, timeout=None, lease=None, **kwargs):
        # type: (Union[str, PremiumPageBlobTier], Optional[int], Optional[Union[LeaseClient, str]]) -> None
        """
        Sets the page blob tiers on the blob. This API is only supported for page blobs on premium accounts.

        :param PremiumPageBlobTier premium_page_blob_tier:
            A page blob tier value to set the blob to. The tier correlates to the size of the
            blob and number of allowed IOPS. This is only applicable to page blobs on
            premium storage accounts.
        :param int timeout:
            The timeout parameter is expressed in seconds. This method may make
            multiple calls to the Azure service and the timeout will apply to
            each call individually.
        :param str lease:
            Required if the blob has an active lease.
        :returns: None
        """
        access_conditions = get_access_conditions(lease)
        if premium_page_blob_tier is None:
            raise ValueError("A PremiumPageBlobTiermust be specified")
        try:
            self._client.blob.set_tier(
                tier=premium_page_blob_tier,
                timeout=timeout,
                lease_access_conditions=access_conditions,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    def get_page_ranges(
            self, start_range=None, # type: Optional[int]
            end_range=None, # type: Optional[int]
            lease=None,  # type: Optional[Union[LeaseClient, str]]
            previous_snapshot_diff=None,  # type: Optional[Union[str, Dict[str, Any]]]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            timeout=None, # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> List[dict[str, int]]
        """
        Returns the list of valid page ranges for a Page Blob or snapshot
        of a page blob.

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
        :param str lease:
            Required if the blob has an active lease.
        :param str previous_snapshot_diff:
            The snapshot diff parameter that contains an opaque DateTime value that
            specifies a previous blob snapshot to be compared
            against a more recent snapshot or the current blob.
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
        try:
            if previous_snapshot_diff:
                try:
                    prev_snapshot = previous_snapshot_diff.snapshot
                except AttributeError:
                    try:
                        prev_snapshot = previous_snapshot_diff['snapshot']
                    except TypeError:
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
        except StorageErrorException as error:
            process_storage_error(error)
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
            lease=None,  # type: Optional[Union[LeaseClient, str]]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            timeout=None, # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> Dict[str, Union[str, datetime]]
        """
        Sets the blob sequence number.

        :param str sequence_number_action:
            This property indicates how the service should modify the blob's sequence
            number. See :class:`~azure.storage.blob.models.SequenceNumberAction` for more information.
        :param str sequence_number:
            This property sets the blob's sequence number. The sequence number is a
            user-controlled property that you can use to track requests and manage
            concurrency issues.
        :param str lease:
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
        :returns: Blob-updated property dict (Etag and last modified).
        """
        access_conditions = get_access_conditions(lease)
        mod_conditions = get_modification_conditions(
            if_modified_since, if_unmodified_since, if_match, if_none_match)
        if sequence_number_action is None:
            raise ValueError("A sequence number action must be specified")
        try:
            return self._client.page_blob.update_sequence_number(
                sequence_number_action=sequence_number_action,
                timeout=timeout,
                blob_sequence_number=sequence_number,
                lease_access_conditions=access_conditions,
                modified_access_conditions=mod_conditions,
                cls=return_response_headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    def resize_blob(
            self, size,  # type: int
            lease=None,  # type: Optional[Union[LeaseClient, str]]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            timeout=None, # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> Dict[str, Union[str, datetime]]
        """
        Resizes a page blob to the specified size. If the specified value is less
        than the current size of the blob, then all pages above the specified value
        are cleared.

        :param int size:
            Size to resize blob to.
        :param str lease:
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
        :returns: Blob-updated property dict (Etag and last modified).
        """
        access_conditions = get_access_conditions(lease)
        mod_conditions = get_modification_conditions(
            if_modified_since, if_unmodified_since, if_match, if_none_match)
        if size is None:
            raise ValueError("A content length must be specified for a Page Blob.")
        try:
            return self._client.page_blob.resize(
                blob_content_length=size,
                timeout=timeout,
                lease_access_conditions=access_conditions,
                modified_access_conditions=mod_conditions,
                cls=return_response_headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    def upload_page(
            self, page,  # type: bytes
            start_range,  # type: int
            end_range,  # type: int
            length=None,  # type: Optional[int]
            lease=None,  # type: Optional[Union[LeaseClient, str]]
            validate_content=False,  # type: Optional[bool]
            if_sequence_number_lte=None, # type: Optional[int]
            if_sequence_number_lt=None, # type: Optional[int]
            if_sequence_number_eq=None, # type: Optional[int]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            encoding='UTF-8',  # type: str
            timeout=None, # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> Dict[str, Union[str, datetime]]
        """
        The Upload Pages operation writes a range of pages to a page blob.

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
        :param int length:
            Length of the page
        :param lease:
            Required if the blob has an active lease.
        :param bool validate_content:
            If true, calculates an MD5 hash of the page content. The storage 
            service checks the hash of the content that has arrived
            with the hash that was sent. This is primarily valuable for detecting 
            bitflips on the wire if using http instead of https as https (the default) 
            will already validate. Note that this MD5 hash is not stored with the 
            blob.
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
        :returns: Blob-updated property dict (Etag and last modified).
        """
        if isinstance(page, six.text_type):
            page = page.encode(encoding)
        if self.require_encryption or (self.key_encryption_key is not None):
            raise ValueError(_ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)

        if length is None:
            length = get_length(page)
            if length is None:
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
        try:
            return self._client.page_blob.upload_pages(
                page[:length],
                content_length=length,
                transactional_content_md5=None,
                timeout=timeout,
                range=content_range,
                lease_access_conditions=access_conditions,
                sequence_number_access_conditions=seq_conditions,
                modified_access_conditions=mod_conditions,
                validate_content=validate_content,
                cls=return_response_headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    def clear_page(
            self, start_range,  # type: int
            end_range,  # type: int
            lease=None,  # type: Optional[Union[LeaseClient, str]]
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
        :returns: Blob-updated property dict (Etag and last modified).
        """
        if self.require_encryption or (self.key_encryption_key is not None):
            raise ValueError(_ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)
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
        try:
            return self._client.page_blob.clear_pages(
                content_length=0,
                timeout=timeout,
                range=content_range,
                lease_access_conditions=access_conditions,
                sequence_number_access_conditions=seq_conditions,
                modified_access_conditions=mod_conditions,
                cls=return_response_headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    def append_block(
            self, data,  # type: Union[Iterable[AnyStr], IO[AnyStr]]
            length=None,  # type: Optional[int]
            validate_content=False,  # type: Optional[bool]
            maxsize_condition=None,  # type: Optional[int]
            appendpos_condition=None,  # type: Optional[int]
            lease=None, # type: Optional[Union[LeaseClient, str]]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[datetime]
            encoding='UTF-8',  # type: str
            timeout=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> Dict[str, Union[str, datetime, int]]
        """
        :returns: Blob-updated property dict (Etag, last modified, append offset, committed block count).
        """
        if self.require_encryption or (self.key_encryption_key is not None):
            raise ValueError(_ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)

        if isinstance(data, six.text_type):
            data = data.encode(encoding)
        if length is None:
            length = get_length(data)
            if length is None:
                length, data = read_length(data)
        if length == 0:
            return {}
        if isinstance(data, bytes):
            data = data[:length]

        append_conditions = None
        if maxsize_condition or appendpos_condition:
            append_conditions = AppendPositionAccessConditions(
                max_size=maxsize_condition,
                append_condition=appendpos_condition
            )
        access_conditions = get_access_conditions(lease)
        mod_conditions = get_modification_conditions(
            if_modified_since, if_unmodified_since, if_match, if_none_match)
        try:
            return self._client.append_blob.append_block(
                data,
                content_length=length,
                timeout=None,
                transactional_content_md5=None,
                lease_access_conditions=access_conditions,
                append_position_access_conditions=append_conditions,
                modified_access_conditions=mod_conditions,
                cls=return_response_headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)
