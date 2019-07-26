# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-few-public-methods, too-many-instance-attributes
# pylint: disable=super-init-not-called, too-many-lines

from enum import Enum
from typing import List, Any, TYPE_CHECKING # pylint: disable=unused-import

from azure.core.paging import PageIterator, ItemPaged

from ._shared import decode_base64_to_text
from ._shared.response_handlers import return_context_and_deserialized, process_storage_error
from ._shared.models import DictMixin, get_enum_value
from ._generated.models import Logging as GeneratedLogging
from ._generated.models import Metrics as GeneratedMetrics
from ._generated.models import RetentionPolicy as GeneratedRetentionPolicy
from ._generated.models import StaticWebsite as GeneratedStaticWebsite
from ._generated.models import CorsRule as GeneratedCorsRule
from ._generated.models import AccessPolicy as GenAccessPolicy
from ._generated.models import StorageErrorException
from ._generated.models import BlobPrefix as GenBlobPrefix
from ._generated.models import BlobItem


class BlobType(str, Enum):

    BlockBlob = "BlockBlob"
    PageBlob = "PageBlob"
    AppendBlob = "AppendBlob"


class BlockState(str, Enum):
    """Block blob block types."""

    Committed = 'Committed'  #: Committed blocks.
    Latest = 'Latest'  #: Latest blocks.
    Uncommitted = 'Uncommitted'  #: Uncommitted blocks.


class StandardBlobTier(str, Enum):
    """
    Specifies the blob tier to set the blob to. This is only applicable for
    block blobs on standard storage accounts.
    """

    Archive = 'Archive'  #: Archive
    Cool = 'Cool'  #: Cool
    Hot = 'Hot'  #: Hot


class PremiumPageBlobTier(str, Enum):
    """
    Specifies the page blob tier to set the blob to. This is only applicable to page
    blobs on premium storage accounts. Please take a look at:
    https://docs.microsoft.com/en-us/azure/storage/storage-premium-storage#scalability-and-performance-targets
    for detailed information on the corresponding IOPS and throughtput per PageBlobTier.
    """

    P4 = 'P4'  #: P4 Tier
    P6 = 'P6'  #: P6 Tier
    P10 = 'P10'  #: P10 Tier
    P20 = 'P20'  #: P20 Tier
    P30 = 'P30'  #: P30 Tier
    P40 = 'P40'  #: P40 Tier
    P50 = 'P50'  #: P50 Tier
    P60 = 'P60'  #: P60 Tier


class SequenceNumberAction(str, Enum):
    """Sequence number actions."""

    Increment = 'increment'
    """
    Increments the value of the sequence number by 1. If specifying this option,
    do not include the x-ms-blob-sequence-number header.
    """

    Max = 'max'
    """
    Sets the sequence number to be the higher of the value included with the
    request and the value currently stored for the blob.
    """

    Update = 'update'
    """Sets the sequence number to the value included with the request."""


class PublicAccess(str, Enum):
    """
    Specifies whether data in the container may be accessed publicly and the level of access.
    """

    OFF = 'off'
    """
    Specifies that there is no public read access for both the container and blobs within the container.
    Clients cannot enumerate the containers within the storage account as well as the blobs within the container.
    """

    Blob = 'blob'
    """
    Specifies public read access for blobs. Blob data within this container can be read
    via anonymous request, but container data is not available. Clients cannot enumerate
    blobs within the container via anonymous request.
    """

    Container = 'container'
    """
    Specifies full public read access for container and blob data. Clients can enumerate
    blobs within the container via anonymous request, but cannot enumerate containers
    within the storage account.
    """


class Logging(GeneratedLogging):
    """Azure Analytics Logging settings.

    :param str version:
        The version of Storage Analytics to configure. The default value is 1.0.
    :param bool delete:
        Indicates whether all delete requests should be logged. The default value is `False`.
    :param bool read:
        Indicates whether all read requests should be logged. The default value is `False`.
    :param bool write:
        Indicates whether all write requests should be logged. The default value is `False`.
    :param retention_policy:
        Determines how long the associated data should persist. If not specified the retention
        policy will be disabled by default.
    :type retention_policy: ~azure.storage.blob.models.RetentionPolicy
    """

    def __init__(self, **kwargs):
        self.version = kwargs.get('version', u'1.0')
        self.delete = kwargs.get('delete', False)
        self.read = kwargs.get('read', False)
        self.write = kwargs.get('write', False)
        self.retention_policy = kwargs.get('retention_policy') or RetentionPolicy()


class Metrics(GeneratedMetrics):
    """A summary of request statistics grouped by API in hour or minute aggregates
    for blobs.

    :param str version:
        The version of Storage Analytics to configure. The default value is 1.0.
    :param bool enabled:
        Indicates whether metrics are enabled for the Blob service.
        The default value is `False`.
    :param bool include_apis:
        Indicates whether metrics should generate summary statistics for called API operations.
    :param retention_policy:
        Determines how long the associated data should persist. If not specified the retention
        policy will be disabled by default.
    :type retention_policy: ~azure.storage.blob.models.RetentionPolicy
    """

    def __init__(self, **kwargs):
        self.version = kwargs.get('version', u'1.0')
        self.enabled = kwargs.get('enabled', False)
        self.include_apis = kwargs.get('include_apis')
        self.retention_policy = kwargs.get('retention_policy') or RetentionPolicy()


class RetentionPolicy(GeneratedRetentionPolicy):
    """The retention policy which determines how long the associated data should
    persist.

    :param bool enabled:
        Indicates whether a retention policy is enabled for the storage service.
        The default value is False.
    :param int days:
        Indicates the number of days that metrics or logging or
        soft-deleted data should be retained. All data older than this value will
        be deleted. If enabled=True, the number of days must be specified.
    """

    def __init__(self, enabled=False, days=None):
        self.enabled = enabled
        self.days = days
        if self.enabled and (self.days is None):
            raise ValueError("If policy is enabled, 'days' must be specified.")


class StaticWebsite(GeneratedStaticWebsite):
    """The properties that enable an account to host a static website.

    :param bool enabled:
        Indicates whether this account is hosting a static website.
        The default value is `False`.
    :param str index_document:
        The default name of the index page under each directory.
    :param str error_document404_path:
        The absolute path of the custom 404 page.
    """

    def __init__(self, **kwargs):
        self.enabled = kwargs.get('enabled', False)
        if self.enabled:
            self.index_document = kwargs.get('index_document')
            self.error_document404_path = kwargs.get('error_document404_path')
        else:
            self.index_document = None
            self.error_document404_path = None


class CorsRule(GeneratedCorsRule):
    """CORS is an HTTP feature that enables a web application running under one
    domain to access resources in another domain. Web browsers implement a
    security restriction known as same-origin policy that prevents a web page
    from calling APIs in a different domain; CORS provides a secure way to
    allow one domain (the origin domain) to call APIs in another domain.

    :param list(str) allowed_origins:
        A list of origin domains that will be allowed via CORS, or "*" to allow
        all domains. The list of must contain at least one entry. Limited to 64
        origin domains. Each allowed origin can have up to 256 characters.
    :param list(str) allowed_methods:
        A list of HTTP methods that are allowed to be executed by the origin.
        The list of must contain at least one entry. For Azure Storage,
        permitted methods are DELETE, GET, HEAD, MERGE, POST, OPTIONS or PUT.
    :param list(str) allowed_headers:
        Defaults to an empty list. A list of headers allowed to be part of
        the cross-origin request. Limited to 64 defined headers and 2 prefixed
        headers. Each header can be up to 256 characters.
    :param list(str) exposed_headers:
        Defaults to an empty list. A list of response headers to expose to CORS
        clients. Limited to 64 defined headers and two prefixed headers. Each
        header can be up to 256 characters.
    :param int max_age_in_seconds:
        The number of seconds that the client/browser should cache a
        preflight response.
    """

    def __init__(self, allowed_origins, allowed_methods, **kwargs):
        self.allowed_origins = ','.join(allowed_origins)
        self.allowed_methods = ','.join(allowed_methods)
        self.allowed_headers = ','.join(kwargs.get('allowed_headers', []))
        self.exposed_headers = ','.join(kwargs.get('exposed_headers', []))
        self.max_age_in_seconds = kwargs.get('max_age_in_seconds', 0)


class ContainerProperties(DictMixin):
    """Blob container's properties class.

    :param datetime last_modified:
        A datetime object representing the last time the container was modified.
    :param str etag:
        The ETag contains a value that you can use to perform operations
        conditionally.
    :param ~azure.storage.blob.models.LeaseProperties lease:
        Stores all the lease information for the container.
    :param str public_access: Specifies whether data in the container may be accessed
        publicly and the level of access.
    :param bool has_immutability_policy:
        Represents whether the container has an immutability policy.
    :param bool has_legal_hold:
        Represents whether the container has a legal hold.
    :param dict metadata: A dict with name-value pairs to associate with the
        container as metadata.
    """

    def __init__(self, **kwargs):
        self.name = None
        self.last_modified = kwargs.get('Last-Modified')
        self.etag = kwargs.get('ETag')
        self.lease = LeaseProperties(**kwargs)
        self.public_access = kwargs.get('x-ms-blob-public-access')
        self.has_immutability_policy = kwargs.get('x-ms-has-immutability-policy')
        self.has_legal_hold = kwargs.get('x-ms-has-legal-hold')
        self.metadata = kwargs.get('metadata')

    @classmethod
    def _from_generated(cls, generated):
        props = cls()
        props.name = generated.name
        props.last_modified = generated.properties.last_modified
        props.etag = generated.properties.etag
        props.lease = LeaseProperties._from_generated(generated)  # pylint: disable=protected-access
        props.public_access = generated.properties.public_access
        props.has_immutability_policy = generated.properties.has_immutability_policy
        props.has_legal_hold = generated.properties.has_legal_hold
        props.metadata = generated.metadata
        return props


class ContainerPropertiesPaged(PageIterator):
    """An Iterable of Container properties.

    :ivar str service_endpoint: The service URL.
    :ivar str prefix: A container name prefix being used to filter the list.
    :ivar str marker: The continuation token of the current page of results.
    :ivar int results_per_page: The maximum number of results retrieved per API call.
    :ivar str continuation_token: The continuation token to retrieve the next page of results.
    :ivar str location_mode: The location mode being used to list results. The available
        options include "primary" and "secondary".
    :ivar current_page: The current page of listed results.
    :vartype current_page: list(~azure.storage.blob.models.ContainerProperties)

    :param callable command: Function to retrieve the next page of items.
    :param str prefix: Filters the results to return only containers whose names
        begin with the specified prefix.
    :param int results_per_page: The maximum number of container names to retrieve per
        call.
    :param str continuation_token: An opaque continuation token.
    """
    def __init__(self, command, prefix=None, results_per_page=None, continuation_token=None):
        super(ContainerPropertiesPaged, self).__init__(
            get_next=self._get_next_cb,
            extract_data=self._extract_data_cb,
            continuation_token=continuation_token or ""
        )
        self._command = command
        self.service_endpoint = None
        self.prefix = prefix
        self.marker = None
        self.results_per_page = results_per_page
        self.location_mode = None
        self.current_page = []

    def _get_next_cb(self, continuation_token):
        try:
            return self._command(
                marker=continuation_token or None,
                maxresults=self.results_per_page,
                cls=return_context_and_deserialized,
                use_location=self.location_mode)
        except StorageErrorException as error:
            process_storage_error(error)

    def _extract_data_cb(self, get_next_return):
        self.location_mode, self._response = get_next_return
        self.service_endpoint = self._response.service_endpoint
        self.prefix = self._response.prefix
        self.marker = self._response.marker
        self.results_per_page = self._response.max_results
        self.current_page = [self._build_item(item) for item in self._response.container_items]

        return self._response.next_marker or None, self.current_page

    @staticmethod
    def _build_item(item):
        return ContainerProperties._from_generated(item)  # pylint: disable=protected-access


class BlobProperties(DictMixin):
    """
    Blob Properties.

    :ivar str name:
        The name of the blob.
    :ivar container:
        The container in which the blob resides.
    :ivar str snapshot:
        Datetime value that uniquely identifies the blob snapshot.
    :ivar ~azure.blob.storage.models.BlobType blob_type:
        String indicating this blob's type.
    :ivar dict metadata:
        Name-value pairs associated with the blob as metadata.
    :ivar datetime last_modified:
        A datetime object representing the last time the blob was modified.
    :ivar str etag:
        The ETag contains a value that you can use to perform operations
        conditionally.
    :ivar int size:
        The size of the content returned. If the entire blob was requested,
        the length of blob in bytes. If a subset of the blob was requested, the
        length of the returned subset.
    :ivar str content_range:
        Indicates the range of bytes returned in the event that the client
        requested a subset of the blob.
    :ivar int append_blob_committed_block_count:
        (For Append Blobs) Number of committed blocks in the blob.
    :ivar int page_blob_sequence_number:
        (For Page Blobs) Sequence number for page blob used for coordinating
        concurrent writes.
    :ivar bool server_encrypted:
        Set to true if the blob is encrypted on the server.
    :ivar ~azure.storage.blob.models.CopyProperties copy:
        Stores all the copy properties for the blob.
    :ivar ~azure.storage.blob.models.ContentSettings content_settings:
        Stores all the content settings for the blob.
    :ivar ~azure.storage.blob.models.LeaseProperties lease:
        Stores all the lease information for the blob.
    :ivar ~azure.storage.blob.models.StandardBlobTier blob_tier:
        Indicates the access tier of the blob. The hot tier is optimized
        for storing data that is accessed frequently. The cool storage tier
        is optimized for storing data that is infrequently accessed and stored
        for at least a month. The archive tier is optimized for storing
        data that is rarely accessed and stored for at least six months
        with flexible latency requirements.
    :ivar datetime blob_tier_change_time:
        Indicates when the access tier was last changed.
    :ivar bool blob_tier_inferred:
        Indicates whether the access tier was inferred by the service.
        If false, it indicates that the tier was set explicitly.
    :ivar bool deleted:
        Whether this blob was deleted.
    :ivar datetime deleted_time:
        A datetime object representing the time at which the blob was deleted.
    :ivar int remaining_retention_days:
        The number of days that the blob will be retained before being permanently deleted by the service.
    :ivar datetime creation_time:
        Indicates when the blob was created, in UTC.
    :ivar str archive_status:
        Archive status of blob.
    """

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.container = None
        self.snapshot = kwargs.get('x-ms-snapshot')
        self.blob_type = BlobType(kwargs['x-ms-blob-type']) if kwargs.get('x-ms-blob-type') else None
        self.metadata = kwargs.get('metadata')
        self.last_modified = kwargs.get('Last-Modified')
        self.etag = kwargs.get('ETag')
        self.size = kwargs.get('Content-Length')
        self.content_range = kwargs.get('Content-Range')
        self.append_blob_committed_block_count = kwargs.get('x-ms-blob-committed-block-count')
        self.page_blob_sequence_number = kwargs.get('x-ms-blob-sequence-number')
        self.server_encrypted = kwargs.get('x-ms-server-encrypted')
        self.copy = CopyProperties(**kwargs)
        self.content_settings = ContentSettings(**kwargs)
        self.lease = LeaseProperties(**kwargs)
        self.blob_tier = kwargs.get('x-ms-access-tier')
        self.blob_tier_change_time = kwargs.get('x-ms-access-tier-change-time')
        self.blob_tier_inferred = kwargs.get('x-ms-access-tier-inferred')
        self.deleted = False
        self.deleted_time = None
        self.remaining_retention_days = None
        self.creation_time = kwargs.get('x-ms-creation-time')
        self.archive_status = kwargs.get('x-ms-archive-status')

    @classmethod
    def _from_generated(cls, generated):
        blob = BlobProperties()
        blob.name = generated.name
        blob_type = get_enum_value(generated.properties.blob_type)
        blob.blob_type = BlobType(blob_type) if blob_type else None
        blob.etag = generated.properties.etag
        blob.deleted = generated.deleted
        blob.snapshot = generated.snapshot
        blob.metadata = generated.metadata
        blob.lease = LeaseProperties._from_generated(generated)  # pylint: disable=protected-access
        blob.copy = CopyProperties._from_generated(generated)  # pylint: disable=protected-access
        blob.last_modified = generated.properties.last_modified
        blob.creation_time = generated.properties.creation_time
        blob.content_settings = ContentSettings._from_generated(generated)  # pylint: disable=protected-access
        blob.size = generated.properties.content_length
        blob.page_blob_sequence_number = generated.properties.blob_sequence_number
        blob.server_encrypted = generated.properties.server_encrypted
        blob.deleted_time = generated.properties.deleted_time
        blob.remaining_retention_days = generated.properties.remaining_retention_days
        blob.blob_tier = generated.properties.access_tier
        blob.blob_tier_inferred = generated.properties.access_tier_inferred
        blob.archive_status = generated.properties.archive_status
        blob.blob_tier_change_time = generated.properties.access_tier_change_time
        return blob


class BlobPropertiesPaged(PageIterator):
    """An Iterable of Blob properties.

    :ivar str service_endpoint: The service URL.
    :ivar str prefix: A blob name prefix being used to filter the list.
    :ivar str marker: The continuation token of the current page of results.
    :ivar int results_per_page: The maximum number of results retrieved per API call.
    :ivar str continuation_token: The continuation token to retrieve the next page of results.
    :ivar str location_mode: The location mode being used to list results. The available
        options include "primary" and "secondary".
    :ivar current_page: The current page of listed results.
    :vartype current_page: list(~azure.storage.blob.models.BlobProperties)
    :ivar str container: The container that the blobs are listed from.
    :ivar str delimiter: A delimiting character used for hierarchy listing.

    :param callable command: Function to retrieve the next page of items.
    :param str prefix: Filters the results to return only blobs whose names
        begin with the specified prefix.
    :param int results_per_page: The maximum number of blobs to retrieve per
        call.
    :param str continuation_token: An opaque continuation token.
    :param str delimiter:
        Used to capture blobs whose names begin with the same substring up to
        the appearance of the delimiter character. The delimiter may be a single
        character or a string.
    :param location_mode: Specifies the location the request should be sent to.
        This mode only applies for RA-GRS accounts which allow secondary read access.
        Options include 'primary' or 'secondary'.
    """
    def __init__(
            self, command,
            container=None,
            prefix=None,
            results_per_page=None,
            continuation_token=None,
            delimiter=None,
            location_mode=None):
        super(BlobPropertiesPaged, self).__init__(
            get_next=self._get_next_cb,
            extract_data=self._extract_data_cb,
            continuation_token=continuation_token or ""
        )
        self._command = command
        self.service_endpoint = None
        self.prefix = prefix
        self.marker = None
        self.results_per_page = results_per_page
        self.container = container
        self.delimiter = delimiter
        self.current_page = None
        self.location_mode = location_mode

    def _get_next_cb(self, continuation_token):
        try:
            return self._command(
                prefix=self.prefix,
                marker=continuation_token or None,
                maxresults=self.results_per_page,
                cls=return_context_and_deserialized,
                use_location=self.location_mode)
        except StorageErrorException as error:
            process_storage_error(error)

    def _extract_data_cb(self, get_next_return):
        self.location_mode, self._response = get_next_return
        self.service_endpoint = self._response.service_endpoint
        self.prefix = self._response.prefix
        self.marker = self._response.marker
        self.results_per_page = self._response.max_results
        self.container = self._response.container_name
        self.current_page = [self._build_item(item) for item in self._response.segment.blob_items]
        self.delimiter = self._response.delimiter

        return self._response.next_marker or None, self.current_page

    def _build_item(self, item):
        if isinstance(item, BlobProperties):
            return item
        if isinstance(item, BlobItem):
            blob = BlobProperties._from_generated(item)  # pylint: disable=protected-access
            blob.container = self.container
            return blob
        return item


class BlobPrefix(ItemPaged, DictMixin):
    """An Iterable of Blob properties.

    Returned from walk_blobs when a delimiter is used.
    Can be thought of as a virtual blob directory.

    :ivar str name: The prefix, or "directory name" of the blob.
    :ivar str service_endpoint: The service URL.
    :ivar str prefix: A blob name prefix being used to filter the list.
    :ivar str marker: The continuation token of the current page of results.
    :ivar int results_per_page: The maximum number of results retrieved per API call.
    :ivar str next_marker: The continuation token to retrieve the next page of results.
    :ivar str location_mode: The location mode being used to list results. The available
        options include "primary" and "secondary".
    :ivar current_page: The current page of listed results.
    :vartype current_page: list(~azure.storage.blob.models.BlobProperties)
    :ivar str container: The container that the blobs are listed from.
    :ivar str delimiter: A delimiting character used for hierarchy listing.

    :param callable command: Function to retrieve the next page of items.
    :param str prefix: Filters the results to return only blobs whose names
        begin with the specified prefix.
    :param int results_per_page: The maximum number of blobs to retrieve per
        call.
    :param str marker: An opaque continuation token.
    :param str delimiter:
        Used to capture blobs whose names begin with the same substring up to
        the appearance of the delimiter character. The delimiter may be a single
        character or a string.
    :param location_mode: Specifies the location the request should be sent to.
        This mode only applies for RA-GRS accounts which allow secondary read access.
        Options include 'primary' or 'secondary'.
    """
    def __init__(self, *args, **kwargs):
        super(BlobPrefix, self).__init__(*args, page_iterator_class=BlobPrefixPaged, **kwargs)
        self.name = kwargs.get('prefix')
        self.prefix = kwargs.get('prefix')
        self.results_per_page = kwargs.get('results_per_page')
        self.container = kwargs.get('container')
        self.delimiter = kwargs.get('delimiter')
        self.location_mode = kwargs.get('location_mode')

class BlobPrefixPaged(BlobPropertiesPaged):
    def __init__(self, *args, **kwargs):
        super(BlobPrefixPaged, self).__init__(*args, **kwargs)
        self.name = self.prefix

    def _extract_data_cb(self, get_next_return):
        continuation_token, _ = super(BlobPrefixPaged, self)._extract_data_cb(get_next_return)
        self.current_page = self._response.segment.blob_prefixes + self._response.segment.blob_items
        self.current_page = [self._build_item(item) for item in self.current_page]

        return continuation_token, self.current_page

    def _build_item(self, item):
        item = super(BlobPrefixPaged, self)._build_item(item)
        if isinstance(item, GenBlobPrefix):
            return BlobPrefix(
                self._command,
                container=self.container,
                prefix=item.name,
                results_per_page=self.results_per_page,
                location_mode=self.location_mode)
        return item

class LeaseProperties(DictMixin):
    """Blob Lease Properties.

    :param str status:
        The lease status of the blob. Possible values: locked|unlocked
    :param str state:
        Lease state of the blob. Possible values: available|leased|expired|breaking|broken
    :param str duration:
        When a blob is leased, specifies whether the lease is of infinite or fixed duration.
    """

    def __init__(self, **kwargs):
        self.status = kwargs.get('x-ms-lease-status')
        self.state = kwargs.get('x-ms-lease-state')
        self.duration = kwargs.get('x-ms-lease-duration')

    @classmethod
    def _from_generated(cls, generated):
        lease = cls()
        lease.status = get_enum_value(generated.properties.lease_status)
        lease.state = get_enum_value(generated.properties.lease_state)
        lease.duration = get_enum_value(generated.properties.lease_duration)
        return lease


class ContentSettings(DictMixin):
    """The content settings of a blob.

    :ivar str content_type:
        The content type specified for the blob. If no content type was
        specified, the default content type is application/octet-stream.
    :ivar str content_encoding:
        If the content_encoding has previously been set
        for the blob, that value is stored.
    :ivar str content_language:
        If the content_language has previously been set
        for the blob, that value is stored.
    :ivar str content_disposition:
        content_disposition conveys additional information about how to
        process the response payload, and also can be used to attach
        additional metadata. If content_disposition has previously been set
        for the blob, that value is stored.
    :ivar str cache_control:
        If the cache_control has previously been set for
        the blob, that value is stored.
    :ivar str content_md5:
        If the content_md5 has been set for the blob, this response
        header is stored so that the client can check for message content
        integrity.
    """

    def __init__(
            self, content_type=None, content_encoding=None,
            content_language=None, content_disposition=None,
            cache_control=None, content_md5=None, **kwargs):

        self.content_type = content_type or kwargs.get('Content-Type')
        self.content_encoding = content_encoding or kwargs.get('Content-Encoding')
        self.content_language = content_language or kwargs.get('Content-Language')
        self.content_md5 = content_md5 or kwargs.get('Content-MD5')
        self.content_disposition = content_disposition or kwargs.get('Content-Disposition')
        self.cache_control = cache_control or kwargs.get('Cache-Control')

    @classmethod
    def _from_generated(cls, generated):
        settings = cls()
        settings.content_type = generated.properties.content_type or None
        settings.content_encoding = generated.properties.content_encoding or None
        settings.content_language = generated.properties.content_language or None
        settings.content_md5 = generated.properties.content_md5 or None
        settings.content_disposition = generated.properties.content_disposition or None
        settings.cache_control = generated.properties.cache_control or None
        return settings


class CopyProperties(DictMixin):
    """Blob Copy Properties.

    These properties will be `None` if this blob has never been the destination
    in a Copy Blob operation, or if this blob has been modified after a concluded
    Copy Blob operation, for example, using Set Blob Properties, Upload Blob, or Commit Block List.

    :param str id:
        String identifier for the last attempted Copy Blob operation where this blob
        was the destination blob.
    :param str source:
        URL up to 2 KB in length that specifies the source blob used in the last attempted
        Copy Blob operation where this blob was the destination blob.
    :param str status:
        State of the copy operation identified by Copy ID, with these values:
            success:
                Copy completed successfully.
            pending:
                Copy is in progress. Check copy_status_description if intermittent,
                non-fatal errors impede copy progress but don't cause failure.
            aborted:
                Copy was ended by Abort Copy Blob.
            failed:
                Copy failed. See copy_status_description for failure details.
    :param str progress:
        Contains the number of bytes copied and the total bytes in the source in the last
        attempted Copy Blob operation where this blob was the destination blob. Can show
        between 0 and Content-Length bytes copied.
    :param datetime completion_time:
        Conclusion time of the last attempted Copy Blob operation where this blob was the
        destination blob. This value can specify the time of a completed, aborted, or
        failed copy attempt.
    :param str status_description:
        Only appears when x-ms-copy-status is failed or pending. Describes cause of fatal
        or non-fatal copy operation failure.
    :param bool incremental_copy:
        Copies the snapshot of the source page blob to a destination page blob.
        The snapshot is copied such that only the differential changes between
        the previously copied snapshot are transferred to the destination
    :param datetime destination_snapshot:
        Included if the blob is incremental copy blob or incremental copy snapshot,
        if x-ms-copy-status is success. Snapshot time of the last successful
        incremental copy snapshot for this blob.
    """

    def __init__(self, **kwargs):
        self.id = kwargs.get('x-ms-copy-id')
        self.source = kwargs.get('x-ms-copy-source')
        self.status = kwargs.get('x-ms-copy-status')
        self.progress = kwargs.get('x-ms-copy-progress')
        self.completion_time = kwargs.get('x-ms-copy-completion_time')
        self.status_description = kwargs.get('x-ms-copy-status-description')
        self.incremental_copy = kwargs.get('x-ms-incremental-copy')
        self.destination_snapshot = kwargs.get('x-ms-copy-destination-snapshot')

    @classmethod
    def _from_generated(cls, generated):
        copy = cls()
        copy.id = generated.properties.copy_id or None
        copy.status = get_enum_value(generated.properties.copy_status) or None
        copy.source = generated.properties.copy_source or None
        copy.progress = generated.properties.copy_progress or None
        copy.completion_time = generated.properties.copy_completion_time or None
        copy.status_description = generated.properties.copy_status_description or None
        copy.incremental_copy = generated.properties.incremental_copy or None
        copy.destination_snapshot = generated.properties.destination_snapshot or None
        return copy


class BlobBlock(DictMixin):
    """BlockBlob Block class.

    :param str block_id:
        Block id.
    :param str state:
        Block state. Possible values: committed|uncommitted
    :ivar int size:
        Block size in bytes.
    """

    def __init__(self, block_id=None, state=BlockState.Latest):
        self.id = block_id
        self.state = state
        self.size = None

    @classmethod
    def _from_generated(cls, generated):
        block = cls()
        block.id = decode_base64_to_text(generated.name)
        block.size = generated.size
        return block


class PageRange(DictMixin):
    """Page Range for page blob.

    :ivar int start:
        Start of page range in bytes.
    :ivar int end:
        End of page range in bytes.
    """

    def __init__(self, start=None, end=None):
        self.start = start
        self.end = end


class AccessPolicy(GenAccessPolicy):
    """Access Policy class used by the set and get acl methods in each service.

    A stored access policy can specify the start time, expiry time, and
    permissions for the Shared Access Signatures with which it's associated.
    Depending on how you want to control access to your resource, you can
    specify all of these parameters within the stored access policy, and omit
    them from the URL for the Shared Access Signature. Doing so permits you to
    modify the associated signature's behavior at any time, as well as to revoke
    it. Or you can specify one or more of the access policy parameters within
    the stored access policy, and the others on the URL. Finally, you can
    specify all of the parameters on the URL. In this case, you can use the
    stored access policy to revoke the signature, but not to modify its behavior.

    Together the Shared Access Signature and the stored access policy must
    include all fields required to authenticate the signature. If any required
    fields are missing, the request will fail. Likewise, if a field is specified
    both in the Shared Access Signature URL and in the stored access policy, the
    request will fail with status code 400 (Bad Request).

    :param permission:
        The permissions associated with the shared access signature. The
        user is restricted to operations allowed by the permissions.
        Required unless an id is given referencing a stored access policy
        which contains this field. This field must be omitted if it has been
        specified in an associated stored access policy.
    :type permission: str or ~azure.storage.blob.models.ContainerPermissions
    :param expiry:
        The time at which the shared access signature becomes invalid.
        Required unless an id is given referencing a stored access policy
        which contains this field. This field must be omitted if it has
        been specified in an associated stored access policy. Azure will always
        convert values to UTC. If a date is passed in without timezone info, it
        is assumed to be UTC.
    :type expiry: datetime or str
    :param start:
        The time at which the shared access signature becomes valid. If
        omitted, start time for this call is assumed to be the time when the
        storage service receives the request. Azure will always convert values
        to UTC. If a date is passed in without timezone info, it is assumed to
        be UTC.
    :type start: datetime or str
    """
    def __init__(self, permission=None, expiry=None, start=None):
        self.start = start
        self.expiry = expiry
        self.permission = permission


class ContainerPermissions(object):
    """ContainerPermissions class to be used with
    :func:`~azure.storage.blob.container_client.ContainerClient.generate_shared_access_signature` API and
    for the AccessPolicies used with
    :func:`~azure.storage.blob.container_client.ContainerClient.set_container_access_policy`.

    :cvar ContainerPermissions ContainerPermissions.DELETE:
        Delete any blob in the container. Note: You cannot grant permissions to
        delete a container with a container SAS. Use an account SAS instead.
    :cvar ContainerPermissions ContainerPermissions.LIST:
        List blobs in the container.
    :cvar ContainerPermissions ContainerPermissions.READ:
        Read the content, properties, metadata or block list of any blob in the
        container. Use any blob in the container as the source of a copy operation.
    :cvar ContainerPermissions ContainerPermissions.WRITE:
        For any blob in the container, create or write content, properties,
        metadata, or block list. Snapshot or lease the blob. Resize the blob
        (page blob only). Use the blob as the destination of a copy operation
        within the same account. Note: You cannot grant permissions to read or
        write container properties or metadata, nor to lease a container, with
        a container SAS. Use an account SAS instead.
    :param bool read:
        Read the content, properties, metadata or block list of any blob in the
        container. Use any blob in the container as the source of a copy operation.
    :param bool write:
        For any blob in the container, create or write content, properties,
        metadata, or block list. Snapshot or lease the blob. Resize the blob
        (page blob only). Use the blob as the destination of a copy operation
        within the same account. Note: You cannot grant permissions to read or
        write container properties or metadata, nor to lease a container, with
        a container SAS. Use an account SAS instead.
    :param bool delete:
        Delete any blob in the container. Note: You cannot grant permissions to
        delete a container with a container SAS. Use an account SAS instead.
    :param bool list:
        List blobs in the container.
    :param str _str:
        A string representing the permissions.
    """

    DELETE = None  # type: ContainerPermissions
    LIST = None  # type: ContainerPermissions
    READ = None  # type: ContainerPermissions
    WRITE = None  # type: ContainerPermissions

    def __init__(self, read=False, write=False, delete=False, list=False, _str=None):  # pylint: disable=redefined-builtin
        if not _str:
            _str = ''
        self.read = read or ('r' in _str)
        self.write = write or ('w' in _str)
        self.delete = delete or ('d' in _str)
        self.list = list or ('l' in _str)

    def __or__(self, other):
        return ContainerPermissions(_str=str(self) + str(other))

    def __add__(self, other):
        return ContainerPermissions(_str=str(self) + str(other))

    def __str__(self):
        return (('r' if self.read else '') +
                ('w' if self.write else '') +
                ('d' if self.delete else '') +
                ('l' if self.list else ''))


ContainerPermissions.DELETE = ContainerPermissions(delete=True)
ContainerPermissions.LIST = ContainerPermissions(list=True)
ContainerPermissions.READ = ContainerPermissions(read=True)
ContainerPermissions.WRITE = ContainerPermissions(write=True)


class BlobPermissions(object):
    """BlobPermissions class to be used with
    :func:`~azure.storage.blob.blob_client.BlobClient.generate_shared_access_signature` API.

    :cvar BlobPermissions BlobPermissions.ADD:
        Add a block to an append blob.
    :cvar BlobPermissions BlobPermissions.CREATE:
        Write a new blob, snapshot a blob, or copy a blob to a new blob.
    :cvar BlobPermissions BlobPermissions.DELETE:
        Delete the blob.
    :cvar BlobPermissions BlobPermissions.READ:
        Read the content, properties, metadata and block list. Use the blob as the source of a copy operation.
    :cvar BlobPermissions BlobPermissions.WRITE:
        Create or write content, properties, metadata, or block list. Snapshot or lease
        the blob. Resize the blob (page blob only). Use the blob as the destination of a
        copy operation within the same account.
    :param bool read:
        Read the content, properties, metadata and block list. Use the blob as
        the source of a copy operation.
    :param bool add:
        Add a block to an append blob.
    :param bool create:
        Write a new blob, snapshot a blob, or copy a blob to a new blob.
    :param bool write:
        Create or write content, properties, metadata, or block list. Snapshot
        or lease the blob. Resize the blob (page blob only). Use the blob as the
        destination of a copy operation within the same account.
    :param bool delete:
        Delete the blob.
    :param str _str:
        A string representing the permissions.
    """
    ADD = None  # type: BlobPermissions
    CREATE = None  # type: BlobPermissions
    DELETE = None  # type: BlobPermissions
    READ = None  # type: BlobPermissions
    WRITE = None  # type: BlobPermissions


    def __init__(self, read=False, add=False, create=False, write=False,
                 delete=False, _str=None):
        if not _str:
            _str = ''
        self.read = read or ('r' in _str)
        self.add = add or ('a' in _str)
        self.create = create or ('c' in _str)
        self.write = write or ('w' in _str)
        self.delete = delete or ('d' in _str)

    def __or__(self, other):
        return BlobPermissions(_str=str(self) + str(other))

    def __add__(self, other):
        return BlobPermissions(_str=str(self) + str(other))

    def __str__(self):
        return (('r' if self.read else '') +
                ('a' if self.add else '') +
                ('c' if self.create else '') +
                ('w' if self.write else '') +
                ('d' if self.delete else ''))


BlobPermissions.ADD = BlobPermissions(add=True)
BlobPermissions.CREATE = BlobPermissions(create=True)
BlobPermissions.DELETE = BlobPermissions(delete=True)
BlobPermissions.READ = BlobPermissions(read=True)
BlobPermissions.WRITE = BlobPermissions(write=True)
