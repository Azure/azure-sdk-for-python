# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import (  # pylint: disable=unused-import
    Union, Optional, Any, IO, Iterable, AnyStr, Dict, List, Tuple,
    TYPE_CHECKING
)
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

from azure.core import Configuration

from .constants import MAX_SINGLE_PUT_SIZE, MAX_BLOCK_SIZE, MIN_LARGE_BLOCK_UPLOAD_THRESHOLD
from .common import BlobType
from ._utils import (
    create_client,
    create_configuration,
    create_pipeline,
    basic_error_map,
    get_access_conditions,
    get_modification_conditions,
    return_response_headers,
    add_metadata_headers
)
from ._generated.models import BlobHTTPHeaders

if TYPE_CHECKING:
    from datetime import datetime
    from .lease import Lease
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
        if parsed_url.path:
            path_container, _, path_blob = parsed_url.partition('/')

        try:
            self.container = container.name
        except AttributeError:
            self.container = container or path_container
        try:
            self.name = blob.name
        except AttributeError:
            self.name = blob or path_blob

        self.scheme = parsed_url.scheme
        self.account = parsed_url.hostname.split(".blob.core.")[0]
        self.url = "{}://{}/{}/{}".format(
            self.scheme,
            parsed_url.hostname,
            self.container,
            self.name
        )
        self.blob_type = blob_type
        self.snapshot = snapshot
        self.key_encryption_key = None

        self._pipeline = create_pipeline(credentials, configuration, **kwargs)
        self._client = create_client(self.url, self._pipeline)

    @staticmethod
    def create_configuration(**kwargs):
        # type: (**Any) -> Configuration
        return create_configuration(**kwargs)

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
        # TODO: Upload other blob types
        if self.blob_type != BlobType.BlockBlob:
            raise NotImplementedError("Other blob types not yet implemented.")
        # TODO Support encryption
        if self.key_encryption_key:
            raise NotImplementedError("Encrypted blobs not yet implmented.")
    
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
                blob_content_md5=bytearray(content_settings.content_md5),
                blob_content_encoding=content_settings.content_encoding,
                blob_content_language=content_settings.content_language,
                blob_content_disposition=content_settings.content_disposition
            )

        adjusted_count = length
        if (self.key_encryption_key is not None) and (adjusted_count is not None):
            adjusted_count += (16 - (length % 16))
        if validate_content:
            # TODO: Validate content
            # computed_md5 = _get_content_md5(request.body)
            # request.headers['Content-MD5'] = _to_str(computed_md5)
            raise NotImplementedError("Content validation not yet supported.")

        # Do single put if the size is smaller than MAX_SINGLE_PUT_SIZE
        if adjusted_count is not None and (adjusted_count < MAX_SINGLE_PUT_SIZE):
            return self._client.block_blob.upload(
                data,
                content_length=adjusted_count,
                timeout=timeout,
                blob_http_headers=blob_headers,
                lease_access_conditions=access_conditions,
                modified_access_conditions=mod_conditions,
                headers=headers,
                cls=return_response_headers,
                **kwargs)
        else:
            # TODO Port over multi-threaded upload chunking
            raise NotImplementedError("Chunked uploads not yet supported")

    def download_blob(
            self, offset=None,  # type: Any
            length=None,  # type: Optional[int]
            validate_content=False,  # type: bool
            lease=None,  # type: Union[Lease, str]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            timeout=None  # type: Optional[int]
        ):
        # type: (...) -> Iterable[bytes]
        """
        TODO: Fix type hints
        :returns: A iterable data generator (stream)
        """

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
        error_map = basic_error_map()
        access_conditions = get_access_conditions(lease)
        mod_conditions = get_modification_conditions(
            if_modified_since, if_unmodified_since, if_match, if_none_match)
        self._client.blob.delete(
            timeout=timeout,
            delete_snapshots=delete_snapshots,
            lease_access_conditions=access_conditions,
            modified_access_conditions=mod_conditions,
            error_map=error_map,
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
            timeout=None  # type: Optional[int]
        ):
        # type: (...) -> BlobProperties
        """
        :returns: BlobProperties
        """

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
            blob_content_md5=bytearray(content_settings.content_md5),
            blob_content_encoding=content_settings.content_encoding,
            blob_content_language=content_settings.content_language,
            blob_content_disposition=content_settings.content_disposition
        )
        return self._client.blob.set_http_headers(
            timeout=timeout,
            blob_http_headers=blob_headers,
            lease_access_conditions=access_conditions,
            modified_access_conditions=mod_conditions,
            cls=return_response_headers
        )

    def get_blob_metadata(
            self, lease=None,  # type: Optional[Union[Lease, str]]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            timeout=None  # type: Optional[int]
        ):
        # type: (...) -> Dict[str, str]
        """
        :returns: A dict of metadata
        """

    def set_blob_metadata(
            self, metadata=None,  # type: Optional[Dict[str, str]]
            lease=None,  # type: Optional[Union[Lease, str]]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            timeout=None  # type: Optional[int]
        ):
        # type: (...) -> Dict[str, Union[str, datetime]]
        """
        :returns: Blob-updated property dict (Etag and last modified)
        """

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
            premium_page_blob_tier=None  # type: Optional[Union[str, PremiumPageBlobTier]]
        ):
        # type: (...) -> Dict[str, Union[str, datetime]]
        """
        :returns: Blob-updated property dict (Etag and last modified).
        """

    def create_snapshot(
            self, metadata=None,  # type: Optional[Dict[str, str]]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            lease=None,  # type: Optional[Union[Lease, str]]
            timeout=None  # type: Optional[int]
        ):
        """
        TODO: Fix type hints - SnapshotProperties
        :returns: SnapshotProperties
        """

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
            timeout=None  # type: Optional[int]
        ):
        # type: (...) -> Lease
        """
        :returns: A Lease object.
        """

    def break_lease(
            self, lease_break_period=None,  # type: Optional[int]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            timeout=None  # type: Optional[int]
        ):
        # type: (...) -> int
        """
        :returns: Approximate time remaining in the lease period, in seconds.
        """

    def set_standard_blob_tier(self, standard_blob_tier, timeout=None):
        # type: (Union[str, StandardBlobTier], Optional[int]) -> None
        """
        :raises: InvalidOperation when blob client type is not BlockBlob.
        :returns: None
        """

    def stage_block(
            self, block_id,  # type: str
            data,  # type: Union[Iterable[AnyStr], IO[AnyStr]]
            validate_content=False,  # type: Optional[bool]
            lease=None,  # type: Optional[Union[Lease, str]]
            timeout=None  # type: Optional[int]
        ):
        # type: (...) -> None
        """
        :raises: InvalidOperation when blob client type is not BlockBlob.
        :returns: None
        """

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
            self, block_list_type=None,  # type: Optional[str]
            lease=None,  # type: Optional[Union[Lease, str]]
            timeout=None  # type: int
        ):
        # type: (...) -> Tuple[List[BlobBlock], List[BlobBlock]]
        """
        :raises: InvalidOperation when blob client type is not BlockBlob.
        :returns: A tuple of two sets - committed and uncommitted blocks
        """

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
            timeout=None  # type: Optional[int]
        ):
        # type: (...) -> Dict[str, Union[str, datetime]]
        """
        :raises: InvalidOperation when blob client type is not BlockBlob.
        :returns: Blob-updated property dict (Etag and last modified).
        """

    def set_premium_page_blob_tier(self, premium_page_blob_tier, timeout=None):
        # type: (Union[str, PremiumPageBlobTier], Optional[int]) -> None
        """
        :raises: InvalidOperation when blob client type is not PageBlob.
        :returns: None
        """

    def get_page_ranges(
            self, start_range=None, # type: Optional[int]
            end_range=None, # type: Optional[int]
            lease=None,  # type: Optional[Union[Lease, str]]
            previous_snapshot_diff=None,  # type: Optional[str]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            timeout=None # type: Optional[int]
        ):
        # type: (...) -> List[PageRange]
        """
        :raises: InvalidOperation when blob client type is not PageBlob.
        :returns: A list of page ranges.
        """

    def set_sequence_number(
            self, sequence_number_action,  # type: Union[str, SequenceNumberAction]
            sequence_number=None,  # type: Optional[str]
            lease=None,  # type: Optional[Union[Lease, str]]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            timeout=None # type: Optional[int]
        ):
        # type: (...) -> Dict[str, Union[str, datetime]]
        """
        :raises: InvalidOperation when blob client type is not PageBlob.
        :returns: Blob-updated property dict (Etag and last modified).
        """

    def resize_blob(
            self, content_length,  # type: int
            lease=None,  # type: Optional[Union[Lease, str]]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            timeout=None # type: Optional[int]
        ):
        # type: (...) -> Dict[str, Union[str, datetime]]
        """
        :raises: InvalidOperation when blob client type is not PageBlob.
        :returns: Blob-updated property dict (Etag and last modified).
        """

    def update_page(
            self, page,  # type: Union[Iterable[AnyStr], IO[AnyStr]]
            start_range,  # type: int
            end_range,  # type: int
            lease=None,  # type: Optional[Union[Lease, str]]
            validate_content=False,  # type: Optional[bool]
            if_sequence_number_lte=None, # type: Optional[int]
            if_sequence_number_lt=None, # type: Optional[int]
            if_sequence_number_eq=None, # type: Optional[int]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            timeout=None # type: Optional[int]
        ):
        # type: (...) -> Dict[str, Union[str, datetime]]
        """
        :raises: InvalidOperation when blob client type is not PageBlob.
        :returns: Blob-updated property dict (Etag and last modified).
        """

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
            timeout=None  # type: Optional[int]
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
