# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-few-public-methods, too-many-instance-attributes

from azure.core.paging import Paged

from ._generated.models import Logging as GeneratedLogging
from ._generated.models import Metrics as GeneratedMetrics
from ._generated.models import RetentionPolicy as GeneratedRetentionPolicy
from ._generated.models import StaticWebsite as GeneratedStaticWebsite
from ._generated.models import CorsRule as GeneratedCorsRule
from ._generated.models import StorageServiceProperties
from ._generated.models import BlobProperties as GenBlobProps
from ._utils import decode_base64
from .common import BlockState, BlobType


def _get_enum_value(value):
    if value is None or value in ["None", ""]:
        return None
    try:
        return value.value
    except AttributeError:
        return value

class Logging(GeneratedLogging):
    """Azure Analytics Logging settings.

    All required parameters must be populated in order to send to Azure.

    :param version: Required. The version of Storage Analytics to configure.
    :type version: str
    :param delete: Required. Indicates whether all delete requests should be
     logged.
    :type delete: bool
    :param read: Required. Indicates whether all read requests should be
     logged.
    :type read: bool
    :param write: Required. Indicates whether all write requests should be
     logged.
    :type write: bool
    :param retention_policy: Required.
    :type retention_policy: ~blob.models.RetentionPolicy
    """

    def __init__(self, **kwargs):
        self.version = kwargs.get('version', u'1.0')
        self.delete = kwargs.get('delete', False)
        self.read = kwargs.get('read', False)
        self.write = kwargs.get('write', False)
        self.retention_policy = kwargs.get('retention_policy') or RetentionPolicy()


class Metrics(GeneratedMetrics):
    """a summary of request statistics grouped by API in hour or minute aggregates
    for blobs.

    All required parameters must be populated in order to send to Azure.

    :param version: The version of Storage Analytics to configure.
    :type version: str
    :param enabled: Required. Indicates whether metrics are enabled for the
     Blob service.
    :type enabled: bool
    :param include_ap_is: Indicates whether metrics should generate summary
     statistics for called API operations.
    :type include_ap_is: bool
    :param retention_policy:
    :type retention_policy: ~blob.models.RetentionPolicy
    """

    def __init__(self, **kwargs):
        self.version = kwargs.get('version', u'1.0')
        self.enabled = kwargs.get('enabled', False)
        self.include_apis = kwargs.get('include_apis')
        self.retention_policy = kwargs.get('retention_policy') or RetentionPolicy()


class RetentionPolicy(GeneratedRetentionPolicy):
    """the retention policy which determines how long the associated data should
    persist.

    All required parameters must be populated in order to send to Azure.

    :param enabled: Required. Indicates whether a retention policy is enabled
     for the storage service
    :type enabled: bool
    :param days: Indicates the number of days that metrics or logging or
     soft-deleted data should be retained. All data older than this value will
     be deleted
    :type days: int
    """

    def __init__(self, enabled=False, days=None):
        self.enabled = enabled
        self.days = days
        if self.enabled and (self.days is None):
            raise ValueError("If policy is enabled, 'days' must be specified.")


class StaticWebsite(GeneratedStaticWebsite):
    """The properties that enable an account to host a static website.

    All required parameters must be populated in order to send to Azure.

    :param enabled: Required. Indicates whether this account is hosting a
     static website
    :type enabled: bool
    :param index_document: The default name of the index page under each
     directory
    :type index_document: str
    :param error_document404_path: The absolute path of the custom 404 page
    :type error_document404_path: str
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

    All required parameters must be populated in order to send to Azure.

    :param allowed_origins: 
        A list of origin domains that will be allowed via CORS, or "*" to allow 
        all domains. The list of must contain at least one entry. Limited to 64 
        origin domains. Each allowed origin can have up to 256 characters.
    :type allowed_origins: list(str)
    :param allowed_methods:
        A list of HTTP methods that are allowed to be executed by the origin. 
        The list of must contain at least one entry. For Azure Storage, 
        permitted methods are DELETE, GET, HEAD, MERGE, POST, OPTIONS or PUT.
    :type allowed_methods: list(str)
    :param int max_age_in_seconds:
        The number of seconds that the client/browser should cache a 
        preflight response.
    :param exposed_headers:
        Defaults to an empty list. A list of response headers to expose to CORS 
        clients. Limited to 64 defined headers and two prefixed headers. Each 
        header can be up to 256 characters.
    :type exposed_headers: list(str)
    :param allowed_headers:
        Defaults to an empty list. A list of headers allowed to be part of 
        the cross-origin request. Limited to 64 defined headers and 2 prefixed 
        headers. Each header can be up to 256 characters.
    :type allowed_headers: list(str)
    """

    def __init__(self, allowed_origins, allowed_methods, **kwargs):
        self.allowed_origins = ','.join(allowed_origins)
        self.allowed_methods = ','.join(allowed_methods)
        self.allowed_headers = ','.join(kwargs.get('allowed_headers', []))
        self.exposed_headers = ','.join(kwargs.get('exposed_headers', []))
        self.max_age_in_seconds = kwargs.get('max_age_in_seconds', 0)


class ContainerProperties(object):
    """
    Blob container's properties class.

    :ivar datetime last_modified:
        A datetime object representing the last time the container was modified.
    :ivar str etag:
        The ETag contains a value that you can use to perform operations
        conditionally.
    :ivar LeaseProperties lease:
        Stores all the lease information for the container.
    :ivar bool has_immutability_policy:
        Represents whether the container has an immutability policy.
    :ivar bool has_legal_hold:
        Represents whether the container has a legal hold.
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
        props.lease = LeaseProperties._from_generated(generated)
        props.public_access = generated.properties.public_access
        props.has_immutability_policy = generated.properties.has_immutability_policy
        props.has_legal_hold = generated.properties.has_legal_hold
        props.metadata = generated.metadata
        return props


class ContainerPropertiesPaged(Paged):

    def __init__(self, command, prefix=None, results_per_page=None, **kwargs):
        super(ContainerPropertiesPaged, self).__init__(command, None, **kwargs)
        self.service_endpoint = None
        self.prefix = prefix
        self.current_marker = None
        self.results_per_page = results_per_page
        self.next_marker = kwargs.get('marker', "")

    def _advance_page(self):
        # type: () -> List[Model]
        """Force moving the cursor to the next azure call.

        This method is for advanced usage, iterator protocol is prefered.

        :raises: StopIteration if no further page
        :return: The current page list
        :rtype: list
        """
        if self.next_marker is None:
            raise StopIteration("End of paging")
        self._current_page_iter_index = 0
        self._response = self._get_next(
            prefix=self.prefix,
            marker=self.next_marker or None,
            maxresults=self.results_per_page)

        self.service_endpoint = self._response.service_endpoint
        self.prefix = self._response.prefix
        self.current_marker = self._response.marker
        self.results_per_page = self._response.max_results
        self.current_page = self._response.container_items
        self.next_marker = self._response.next_marker or None
        return self.current_page

    def __next__(self):
        item = super(ContainerPropertiesPaged, self).__next__()
        if isinstance(item, ContainerProperties):
            return item
        return ContainerProperties._from_generated(item)


class SnapshotProperties(object):

    def __init__(self, **kwargs):
        self.name = None
        self.container = None
        self.snapshot = kwargs.get('x-ms-snapshot')
        self.blob_type = None
        self.last_modified = kwargs.get('Last-Modified')
        self.etag = kwargs.get('ETag')


class BlobProperties(object):
    """
    Blob Properties

    :ivar str blob_type:
        String indicating this blob's type.
    :ivar datetime last_modified:
        A datetime object representing the last time the blob was modified.
    :ivar str etag:
        The ETag contains a value that you can use to perform operations
        conditionally.
    :ivar int content_length:
        The length of the content returned. If the entire blob was requested,
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
    :ivar StandardBlobTier blob_tier:
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
    :ivar datetime deleted_time:
        A datetime object representing the time at which the blob was deleted.
    :ivar int remaining_retention_days:
        The number of days that the blob will be retained before being permanently deleted by the service.
    :ivar datetime creation_time:
        Indicates when the blob was created, in UTC.
    """

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.container = None
        self.snapshot = kwargs.get('x-ms-snapshot')
        self.blob_type = BlobType(kwargs['x-ms-blob-type']) if kwargs.get('x-ms-blob-type') else None
        self.metadata = kwargs.get('metadata')
        self.last_modified = kwargs.get('Last-Modified')
        self.etag = kwargs.get('ETag')
        self.content_length = kwargs.get('Content-Length')
        self.content_range = kwargs.get('Accept-Ranges')
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
        blob.blob_type = BlobType(_get_enum_value(generated.properties.blob_type))
        blob.etag = generated.properties.etag
        blob.deleted = generated.deleted
        blob.snapshot = generated.snapshot
        blob.metadata = generated.metadata
        blob.lease = LeaseProperties._from_generated(generated)
        blob.copy = CopyProperties._from_generated(generated)
        blob.last_modified = generated.properties.last_modified
        blob.creation_time = generated.properties.creation_time
        blob.content_settings = ContentSettings._from_generated(generated)
        blob.content_length = generated.properties.content_length
        blob.page_blob_sequence_number = generated.properties.blob_sequence_number
        blob.server_encrypted = generated.properties.server_encrypted
        blob.deleted_time = generated.properties.deleted_time
        blob.remaining_retention_days = generated.properties.remaining_retention_days
        blob.blob_tier = generated.properties.access_tier
        blob.blob_tier_inferred = generated.properties.access_tier_inferred
        blob.archive_status = generated.properties.archive_status
        blob.blob_tier_change_time = generated.properties.access_tier_change_time
        return blob



class BlobPropertiesPaged(Paged):

    def __init__(self, command, container=None, prefix=None, results_per_page=None, **kwargs):
        super(BlobPropertiesPaged, self).__init__(command, None, **kwargs)
        self.service_endpoint = None
        self.prefix = prefix
        self.current_marker = None
        self.results_per_page = results_per_page
        self.next_marker = kwargs.get('marker', "")
        self.container_name = container
        self.delimiter = None
        self.segment = None

    def _advance_page(self):
        # type: () -> List[Model]
        """Force moving the cursor to the next azure call.

        This method is for advanced usage, iterator protocol is prefered.

        :raises: StopIteration if no further page
        :return: The current page list
        :rtype: list
        """
        if self.next_marker is None:
            raise StopIteration("End of paging")
        self._current_page_iter_index = 0
        self._response = self._get_next(
            prefix=self.prefix,
            marker=self.next_marker or None,
            maxresults=self.results_per_page)

        self.service_endpoint = self._response.service_endpoint
        self.prefix = self._response.prefix
        self.current_marker = self._response.marker
        self.results_per_page = self._response.max_results
        self.current_page = self._response.segment.blob_items
        self.next_marker = self._response.next_marker or None
        self.container_name = self._response.container_name
        self.delimiter = self._response.delimiter
        return self.current_page

    def __next__(self):
        item = super(BlobPropertiesPaged, self).__next__()
        if isinstance(item, BlobProperties):
            return item
        return BlobProperties._from_generated(item)
    

class LeaseProperties(object):
    """
    Blob Lease Properties.

    :ivar str status:
        The lease status of the blob.
        Possible values: locked|unlocked
    :ivar str state:
        Lease state of the blob.
        Possible values: available|leased|expired|breaking|broken
    :ivar str duration:
        When a blob is leased, specifies whether the lease is of infinite or fixed duration.
    """

    def __init__(self, **kwargs):
        self.status = kwargs.get('x-ms-lease-status')
        self.state = kwargs.get('x-ms-lease-state')
        self.duration = kwargs.get('x-ms-lease-duration')

    @classmethod
    def _from_generated(cls, generated):
        lease = cls()
        lease.status = _get_enum_value(generated.properties.lease_status)
        lease.state = _get_enum_value(generated.properties.lease_state)
        lease.duration = _get_enum_value(generated.properties.lease_duration)
        return lease


class ContentSettings(object):
    """
    Used to store the content settings of a blob.

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
        settings.content_type = generated.properties.content_type
        settings.content_encoding = generated.properties.content_encoding
        settings.content_language = generated.properties.content_language
        settings.content_md5 = generated.properties.content_md5
        settings.content_disposition = generated.properties.content_disposition
        settings.cache_control = generated.properties.cache_control
        return settings


class CopyProperties(object):
    """
    Blob Copy Properties.

    :ivar str id:
        String identifier for the last attempted Copy Blob operation where this blob
        was the destination blob. This header does not appear if this blob has never
        been the destination in a Copy Blob operation, or if this blob has been
        modified after a concluded Copy Blob operation using Set Blob Properties,
        Put Blob, or Put Block List.
    :ivar str source:
        URL up to 2 KB in length that specifies the source blob used in the last attempted
        Copy Blob operation where this blob was the destination blob. This header does not
        appear if this blob has never been the destination in a Copy Blob operation, or if
        this blob has been modified after a concluded Copy Blob operation using
        Set Blob Properties, Put Blob, or Put Block List.
    :ivar str status:
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
    :ivar str progress:
        Contains the number of bytes copied and the total bytes in the source in the last
        attempted Copy Blob operation where this blob was the destination blob. Can show
        between 0 and Content-Length bytes copied.
    :ivar datetime completion_time:
        Conclusion time of the last attempted Copy Blob operation where this blob was the
        destination blob. This value can specify the time of a completed, aborted, or
        failed copy attempt.
    :ivar str status_description:
        only appears when x-ms-copy-status is failed or pending. Describes cause of fatal
        or non-fatal copy operation failure.
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
        copy.id = generated.properties.copy_id
        copy.status = _get_enum_value(generated.properties.copy_status)
        copy.source = generated.properties.copy_source
        copy.progress = generated.properties.copy_progress
        copy.completion_time = generated.properties.copy_completion_time
        copy.status_description = generated.properties.copy_status_description
        copy.incremental_copy = generated.properties.incremental_copy
        copy.destination_snapshot = generated.properties.destination_snapshot
        return copy


class BlobBlock(object):
    """
    BlockBlob Block class.

    :ivar str id:
        Block id.
    :ivar str state:
        Block state.
        Possible valuse: committed|uncommitted
    :ivar int size:
        Block size in bytes.
    """

    def __init__(self, block_id=None, state=BlockState.Latest):
        self.id = block_id
        self.state = state
        self.size = None

    def _set_size(self, size):
        self.size = size

    @classmethod
    def _from_generated(cls, generated):
        block = cls()
        block.id = decode_base64(generated.name)
        block.size = generated.size
        return block


class PageRange(object):
    """
    Page Range for page blob.

    :ivar int start:
        Start of page range in bytes.
    :ivar int end:
        End of page range in bytes.
    :ivar bool is_cleared:
        Indicates if a page range is cleared or not. Only applicable
        for get_page_range_diff API.
    """

    def __init__(self, start=None, end=None, is_cleared=False):
        self.start = start
        self.end = end
        self.is_cleared = is_cleared


class ResourceTypes(object):
    """
    Specifies the resource types that are accessible with the account SAS.

    :ivar ResourceTypes ResourceTypes.CONTAINER:
        Access to container-level APIs (e.g., Create/Delete Container,
        Create/Delete Queue, Create/Delete Share,
        List Blobs/Files and Directories)
    :ivar ResourceTypes ResourceTypes.OBJECT:
        Access to object-level APIs for blobs, queue messages, and
        files(e.g. Put Blob, Query Entity, Get Messages, Create File, etc.)
    :ivar ResourceTypes ResourceTypes.SERVICE:
        Access to service-level APIs (e.g., Get/Set Service Properties,
        Get Service Stats, List Containers/Queues/Shares)
    """

    SERVICE = None  # type: ResourceTypes
    CONTAINER = None  # type: ResourceTypes
    OBJECT = None  # type: ResourceTypes

    def __init__(self, service=False, container=False, object=False, _str=None):  # pylint: disable=redefined-builtin
        """
        :param bool service:
            Access to service-level APIs (e.g., Get/Set Service Properties,
            Get Service Stats, List Containers/Queues/Shares)
        :param bool container:
            Access to container-level APIs (e.g., Create/Delete Container,
            Create/Delete Queue, Create/Delete Share,
            List Blobs/Files and Directories)
        :param bool object:
            Access to object-level APIs for blobs, queue messages, and
            files(e.g. Put Blob, Query Entity, Get Messages, Create File, etc.)
        :param str _str:
            A string representing the resource types.
        """
        if not _str:
            _str = ''
        self.service = service or ('s' in _str)
        self.container = container or ('c' in _str)
        self.object = object or ('o' in _str)

    def __or__(self, other):
        return ResourceTypes(_str=str(self) + str(other))

    def __add__(self, other):
        return ResourceTypes(_str=str(self) + str(other))

    def __str__(self):
        return (('s' if self.service else '') +
                ('c' if self.container else '') +
                ('o' if self.object else ''))


ResourceTypes.SERVICE = ResourceTypes(service=True)
ResourceTypes.CONTAINER = ResourceTypes(container=True)
ResourceTypes.OBJECT = ResourceTypes(object=True)


class AccountPermissions(object):
    """
    :class:`~ResourceTypes` class to be used with generate_shared_access_signature
    method and for the AccessPolicies used with set_*_acl. There are two types of
    SAS which may be used to grant resource access. One is to grant access to a
    specific resource (resource-specific). Another is to grant access to the
    entire service for a specific account and allow certain operations based on
    perms found here.

    :ivar AccountPermissions AccountPermissions.ADD:
        Valid for the following Object resource types only: queue messages and append blobs.
    :ivar AccountPermissions AccountPermissions.CREATE:
        Valid for the following Object resource types only: blobs and files. Users
        can create new blobs or files, but may not overwrite existing blobs or files.
    :ivar AccountPermissions AccountPermissions.DELETE:
        Valid for Container and Object resource types, except for queue messages.
    :ivar AccountPermissions AccountPermissions.LIST:
        Valid for Service and Container resource types only.
    :ivar AccountPermissions AccountPermissions.PROCESS:
        Valid for the following Object resource type only: queue messages.
    :ivar AccountPermissions AccountPermissions.READ:
        Valid for all signed resources types (Service, Container, and Object).
        Permits read permissions to the specified resource type.
    :ivar AccountPermissions AccountPermissions.UPDATE:
        Valid for the following Object resource types only: queue messages.
    :ivar AccountPermissions AccountPermissions.WRITE:
        Valid for all signed resources types (Service, Container, and Object).
        Permits write permissions to the specified resource type.
    """

    READ = None  # type: AccountPermissions
    WRITE = None  # type: AccountPermissions
    DELETE = None  # type: AccountPermissions
    LIST = None  # type: AccountPermissions
    ADD = None  # type: AccountPermissions
    CREATE = None  # type: AccountPermissions
    UPDATE = None  # type: AccountPermissions
    PROCESS = None  # type: AccountPermissions

    def __init__(self, read=False, write=False, delete=False, list=False,  # pylint: disable=redefined-builtin
                 add=False, create=False, update=False, process=False, _str=None):
        """
        :param bool read:
            Valid for all signed resources types (Service, Container, and Object).
            Permits read permissions to the specified resource type.
        :param bool write:
            Valid for all signed resources types (Service, Container, and Object).
            Permits write permissions to the specified resource type.
        :param bool delete:
            Valid for Container and Object resource types, except for queue messages.
        :param bool list:
            Valid for Service and Container resource types only.
        :param bool add:
            Valid for the following Object resource types only: queue messages, and append blobs.
        :param bool create:
            Valid for the following Object resource types only: blobs and files.
            Users can create new blobs or files, but may not overwrite existing
            blobs or files.
        :param bool update:
            Valid for the following Object resource types only: queue messages.
        :param bool process:
            Valid for the following Object resource type only: queue messages.
        :param str _str:
            A string representing the permissions.
        """
        if not _str:
            _str = ''
        self.read = read or ('r' in _str)
        self.write = write or ('w' in _str)
        self.delete = delete or ('d' in _str)
        self.list = list or ('l' in _str)
        self.add = add or ('a' in _str)
        self.create = create or ('c' in _str)
        self.update = update or ('u' in _str)
        self.process = process or ('p' in _str)

    def __or__(self, other):
        return AccountPermissions(_str=str(self) + str(other))

    def __add__(self, other):
        return AccountPermissions(_str=str(self) + str(other))

    def __str__(self):
        return (('r' if self.read else '') +
                ('w' if self.write else '') +
                ('d' if self.delete else '') +
                ('l' if self.list else '') +
                ('a' if self.add else '') +
                ('c' if self.create else '') +
                ('u' if self.update else '') +
                ('p' if self.process else ''))


AccountPermissions.READ = AccountPermissions(read=True)
AccountPermissions.WRITE = AccountPermissions(write=True)
AccountPermissions.DELETE = AccountPermissions(delete=True)
AccountPermissions.LIST = AccountPermissions(list=True)
AccountPermissions.ADD = AccountPermissions(add=True)
AccountPermissions.CREATE = AccountPermissions(create=True)
AccountPermissions.UPDATE = AccountPermissions(update=True)
AccountPermissions.PROCESS = AccountPermissions(process=True)


class ContainerPermissions(object):
    """
    ContainerPermissions class to be used with
    :func:`~azure.storage.blob.container_client.ContainerClient.generate_shared_access_signature` API and
    for the AccessPolicies used with
    :func:`~azure.storage.blob.container_client.ContainerClient.set_container_acl`.

    :ivar ContainerPermissions ContainerPermissions.DELETE:
        Delete any blob in the container. Note: You cannot grant permissions to
        delete a container with a container SAS. Use an account SAS instead.
    :ivar ContainerPermissions ContainerPermissions.LIST:
        List blobs in the container.
    :ivar ContainerPermissions ContainerPermissions.READ:
        Read the content, properties, metadata or block list of any blob in the
        container. Use any blob in the container as the source of a copy operation.
    :ivar ContainerPermissions ContainerPermissions.WRITE:
        For any blob in the container, create or write content, properties,
        metadata, or block list. Snapshot or lease the blob. Resize the blob
        (page blob only). Use the blob as the destination of a copy operation
        within the same account. Note: You cannot grant permissions to read or
        write container properties or metadata, nor to lease a container, with
        a container SAS. Use an account SAS instead.
    """

    DELETE = None  # type: ContainerPermissions
    LIST = None  # type: ContainerPermissions
    READ = None  # type: ContainerPermissions
    WRITE = None  # type: ContainerPermissions

    def __init__(self, read=False, write=False, delete=False, list=False, _str=None):  # pylint: disable=redefined-builtin
        """
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
    """
    BlobPermissions class to be used with
    :func:`~azure.storage.blob.blob_client.BlobClient.generate_shared_access_signature` API.

    :ivar BlobPermissions BlobPermissions.ADD:
        Add a block to an append blob.
    :ivar BlobPermissions BlobPermissions.CREATE:
        Write a new blob, snapshot a blob, or copy a blob to a new blob.
    :ivar BlobPermissions BlobPermissions.DELETE:
        Delete the blob.
    :ivar BlobPermissions BlobPermissions.READ:
        Read the content, properties, metadata and block list. Use the blob as the source of a copy operation.
    :ivar BlobPermissions BlobPermissions.WRITE:
        Create or write content, properties, metadata, or block list. Snapshot or lease
        the blob. Resize the blob (page blob only). Use the blob as the destination of a
        copy operation within the same account.
    """
    ADD = None  # type: BlobPermissions
    CREATE = None  # type: BlobPermissions
    DELETE = None  # type: BlobPermissions
    READ = None  # type: BlobPermissions
    WRITE = None  # type: BlobPermissions


    def __init__(self, read=False, add=False, create=False, write=False,
                 delete=False, _str=None):
        """
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
