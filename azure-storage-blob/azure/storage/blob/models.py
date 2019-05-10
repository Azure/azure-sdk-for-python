# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-few-public-methods, too-many-instance-attributes

from .common import BlockState


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

    def __init__(self):
        self.name = None
        self.container = None
        self.snapshot = None
        self.blob_type = None
        self.metadata = None
        self.last_modified = None
        self.etag = None
        self.content_length = None
        self.content_range = None
        self.append_blob_committed_block_count = None
        self.page_blob_sequence_number = None
        self.server_encrypted = None
        self.copy = CopyProperties()
        self.content_settings = ContentSettings()
        self.lease = LeaseProperties()
        self.blob_tier = None
        self.blob_tier_change_time = None
        self.blob_tier_inferred = False
        self.deleted_time = None
        self.remaining_retention_days = None
        self.creation_time = None


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

    def __init__(self):
        self.status = None
        self.state = None
        self.duration = None


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
            cache_control=None, content_md5=None):
        self.content_type = content_type
        self.content_encoding = content_encoding
        self.content_language = content_language
        self.content_disposition = content_disposition
        self.cache_control = cache_control
        self.content_md5 = content_md5


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

    def __init__(self):
        self.id = None
        self.source = None
        self.status = None
        self.progress = None
        self.completion_time = None
        self.status_description = None


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
