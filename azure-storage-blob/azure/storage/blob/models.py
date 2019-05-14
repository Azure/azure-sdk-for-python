# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-few-public-methods, too-many-instance-attributes

from .common import BlockState, BlobType


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

    def __init__(self):
        self.name = None
        self.last_modified = None
        self.etag = None
        self.lease = LeaseProperties()
        self.public_access = None
        self.has_immutability_policy = None
        self.has_legal_hold = None
        self.metadata = None

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
        self.deleted_time = None
        self.remaining_retention_days = None
        self.creation_time = kwargs.get('x-ms-creation-time')
        self.archive_status = kwargs.get('x-ms-archive-status')


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
        self.source = kwargs.get('x-ms-copy-status')
        self.status = kwargs.get('x-ms-copy-source')
        self.progress = kwargs.get('x-ms-copy-progress')
        self.completion_time = kwargs.get('x-ms-copy-completion_time')
        self.status_description = kwargs.get('x-ms-copy-status-description')
        self.incremental_copy = kwargs.get('x-ms-incremental-copy')
        self.destination_snapshot = kwargs.get('x-ms-copy-destination-snapshot')


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
