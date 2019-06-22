# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from ..common._common_conversion import _to_str


class Container(object):
    '''
    Blob container class. 
    
    :ivar str name: 
        The name of the container.
    :ivar metadata: 
        A dict containing name-value pairs associated with the container as metadata.
        This var is set to None unless the include=metadata param was included 
        for the list containers operation. If this parameter was specified but the 
        container has no metadata, metadata will be set to an empty dictionary.
    :vartype metadata: dict(str, str)
    :ivar ContainerProperties properties:
        System properties for the container.
    '''

    def __init__(self, name=None, props=None, metadata=None):
        self.name = name
        self.properties = props or ContainerProperties()
        self.metadata = metadata


class ContainerProperties(object):
    '''
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
    '''

    def __init__(self):
        self.last_modified = None
        self.etag = None
        self.lease = LeaseProperties()
        self.public_access = None
        self.has_immutability_policy = None
        self.has_legal_hold = None


class Blob(object):
    '''
    Blob class.
    
    :ivar str name:
        Name of blob.
    :ivar str snapshot:
        A DateTime value that uniquely identifies the snapshot. The value of
        this header indicates the snapshot version, and may be used in
        subsequent requests to access the snapshot.
    :ivar content:
        Blob content.
    :vartype content: str or bytes
    :ivar BlobProperties properties:
        Stores all the system properties for the blob.
    :ivar metadata:
        Name-value pairs associated with the blob as metadata.
    :ivar bool deleted:
        Specify whether the blob was soft deleted.
        In other words, if the blob is being retained by the delete retention policy,
        this field would be True. The blob could be undeleted or it will be garbage collected after the specified
        time period.
    '''

    def __init__(self, name=None, snapshot=None, content=None, props=None, metadata=None, deleted=False):
        self.name = name
        self.snapshot = snapshot
        self.content = content
        self.properties = props or BlobProperties()
        self.metadata = metadata
        self.deleted = deleted


class BlobProperties(object):
    '''
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
    '''

    def __init__(self):
        self.blob_type = None
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


class ContentSettings(object):
    '''
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
    '''

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

    def _to_headers(self):
        return {
            'x-ms-blob-cache-control': _to_str(self.cache_control),
            'x-ms-blob-content-type': _to_str(self.content_type),
            'x-ms-blob-content-disposition': _to_str(self.content_disposition),
            'x-ms-blob-content-md5': _to_str(self.content_md5),
            'x-ms-blob-content-encoding': _to_str(self.content_encoding),
            'x-ms-blob-content-language': _to_str(self.content_language),
        }


class CopyProperties(object):
    '''
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
    '''

    def __init__(self):
        self.id = None
        self.source = None
        self.status = None
        self.progress = None
        self.completion_time = None
        self.status_description = None


class LeaseProperties(object):
    '''
    Blob Lease Properties.
    
    :ivar str status:
        The lease status of the blob.
        Possible values: locked|unlocked
    :ivar str state:
        Lease state of the blob.
        Possible values: available|leased|expired|breaking|broken
    :ivar str duration:
        When a blob is leased, specifies whether the lease is of infinite or fixed duration.
    '''

    def __init__(self):
        self.status = None
        self.state = None
        self.duration = None


class BlobPrefix(object):
    '''
    BlobPrefix objects may potentially returned in the blob list when 
    :func:`~azure.storage.blob.baseblobservice.BaseBlobService.list_blobs` is 
    used with a delimiter. Prefixes can be thought of as virtual blob directories.
    
    :ivar str name: The name of the blob prefix.
    '''

    def __init__(self):
        self.name = None


class BlobBlockState(object):
    '''Block blob block types.'''

    Committed = 'Committed'
    '''Committed blocks.'''

    Latest = 'Latest'
    '''Latest blocks.'''

    Uncommitted = 'Uncommitted'
    '''Uncommitted blocks.'''


class BlobBlock(object):
    '''
    BlockBlob Block class.
    
    :ivar str id:
        Block id.
    :ivar str state:
        Block state.
        Possible valuse: committed|uncommitted
    :ivar int size:
        Block size in bytes.
    '''

    def __init__(self, id=None, state=BlobBlockState.Latest):
        self.id = id
        self.state = state

    def _set_size(self, size):
        self.size = size


class BlobBlockList(object):
    '''
    Blob Block List class.
   
    :ivar committed_blocks:
        List of committed blocks.
    :vartype committed_blocks: list(:class:`~azure.storage.blob.models.BlobBlock`)
    :ivar uncommitted_blocks:
        List of uncommitted blocks.
    :vartype uncommitted_blocks: list(:class:`~azure.storage.blob.models.BlobBlock`)
    '''

    def __init__(self):
        self.committed_blocks = list()
        self.uncommitted_blocks = list()


class PageRange(object):
    '''
    Page Range for page blob.
    
    :ivar int start:
        Start of page range in bytes.
    :ivar int end:
        End of page range in bytes.
    :ivar bool is_cleared:
        Indicates if a page range is cleared or not. Only applicable
        for get_page_range_diff API.
    '''

    def __init__(self, start=None, end=None, is_cleared=False):
        self.start = start
        self.end = end
        self.is_cleared = is_cleared


class ResourceProperties(object):
    '''
    Base response for a resource request.
    
    :ivar str etag:
        Opaque etag value that can be used to check if resource
        has been modified.
    :ivar datetime last_modified:
        Datetime for last time resource was modified.
    '''

    def __init__(self):
        self.last_modified = None
        self.etag = None


class AppendBlockProperties(ResourceProperties):
    '''
    Response for an append block request.
    
    :ivar int append_offset:
        Position to start next append.
    :ivar int committed_block_count:
        Number of committed append blocks.
    '''

    def __init__(self):
        super(ResourceProperties, self).__init__()
        self.append_offset = None
        self.committed_block_count = None


class PageBlobProperties(ResourceProperties):
    '''
    Response for a page request.
    
    :ivar int sequence_number:
        Identifer for page blobs to help handle concurrent writes.
    '''

    def __init__(self):
        super(ResourceProperties, self).__init__()
        self.sequence_number = None


class PublicAccess(object):
    '''
    Specifies whether data in the container may be accessed publicly and the level of access.
    '''

    OFF = 'off'
    '''
    Specifies that there is no public read access for both the container and blobs within the container.
    Clients cannot enumerate the containers within the storage account as well as the blobs within the container.
    '''

    Blob = 'blob'
    '''
    Specifies public read access for blobs. Blob data within this container can be read 
    via anonymous request, but container data is not available. Clients cannot enumerate 
    blobs within the container via anonymous request.
    '''

    Container = 'container'
    '''
    Specifies full public read access for container and blob data. Clients can enumerate 
    blobs within the container via anonymous request, but cannot enumerate containers 
    within the storage account.
    '''


class DeleteSnapshot(object):
    '''
    Required if the blob has associated snapshots. Specifies how to handle the snapshots.
    '''

    Include = 'include'
    '''
    Delete the base blob and all of its snapshots.
    '''

    Only = 'only'
    '''
    Delete only the blob's snapshots and not the blob itself.
    '''


class BlockListType(object):
    '''
    Specifies whether to return the list of committed blocks, the list of uncommitted 
    blocks, or both lists together.
    '''

    All = 'all'
    '''Both committed and uncommitted blocks.'''

    Committed = 'committed'
    '''Committed blocks.'''

    Uncommitted = 'uncommitted'
    '''Uncommitted blocks.'''


class SequenceNumberAction(object):
    '''Sequence number actions.'''

    Increment = 'increment'
    '''
    Increments the value of the sequence number by 1. If specifying this option, 
    do not include the x-ms-blob-sequence-number header.
    '''

    Max = 'max'
    '''
    Sets the sequence number to be the higher of the value included with the 
    request and the value currently stored for the blob.
    '''

    Update = 'update'
    '''Sets the sequence number to the value included with the request.'''


class _LeaseActions(object):
    '''Actions for a lease.'''

    Acquire = 'acquire'
    '''Acquire the lease.'''

    Break = 'break'
    '''Break the lease.'''

    Change = 'change'
    '''Change the lease ID.'''

    Release = 'release'
    '''Release the lease.'''

    Renew = 'renew'
    '''Renew the lease.'''


class _BlobTypes(object):
    '''Blob type options.'''

    AppendBlob = 'AppendBlob'
    '''Append blob type.'''

    BlockBlob = 'BlockBlob'
    '''Block blob type.'''

    PageBlob = 'PageBlob'
    '''Page blob type.'''


class Include(object):
    '''
    Specifies the datasets to include in the blob list response.

    :ivar ~azure.storage.blob.models.Include Include.COPY: 
        Specifies that metadata related to any current or previous Copy Blob operation 
        should be included in the response.
    :ivar ~azure.storage.blob.models.Include Include.METADATA: 
        Specifies that metadata be returned in the response.
    :ivar ~azure.storage.blob.models.Include Include.SNAPSHOTS: 
        Specifies that snapshots should be included in the enumeration.
    :ivar ~azure.storage.blob.models.Include Include.UNCOMMITTED_BLOBS: 
        Specifies that blobs for which blocks have been uploaded, but which have not 
        been committed using Put Block List, be included in the response.
    :ivar ~azure.storage.blob.models.Include Include.DELETED:
        Specifies that deleted blobs should be returned in the response.
    '''

    def __init__(self, snapshots=False, metadata=False, uncommitted_blobs=False,
                 copy=False, deleted=False, _str=None):
        '''
        :param bool snapshots:
             Specifies that snapshots should be included in the enumeration.
        :param bool metadata:
            Specifies that metadata be returned in the response.
        :param bool uncommitted_blobs:
            Specifies that blobs for which blocks have been uploaded, but which have 
            not been committed using Put Block List, be included in the response.
        :param bool copy: 
            Specifies that metadata related to any current or previous Copy Blob 
            operation should be included in the response.
        :param bool deleted:
            Specifies that deleted blobs should be returned in the response.
        :param str _str: 
            A string representing the includes.
        '''
        if not _str:
            _str = ''
        components = _str.split(',')
        self.snapshots = snapshots or ('snapshots' in components)
        self.metadata = metadata or ('metadata' in components)
        self.uncommitted_blobs = uncommitted_blobs or ('uncommittedblobs' in components)
        self.copy = copy or ('copy' in components)
        self.deleted = deleted or ('deleted' in components)

    def __or__(self, other):
        return Include(_str=str(self) + str(other))

    def __add__(self, other):
        return Include(_str=str(self) + str(other))

    def __str__(self):
        include = (('snapshots,' if self.snapshots else '') +
                   ('metadata,' if self.metadata else '') +
                   ('uncommittedblobs,' if self.uncommitted_blobs else '') +
                   ('copy,' if self.copy else '') +
                   ('deleted,' if self.deleted else ''))
        return include.rstrip(',')


Include.COPY = Include(copy=True)
Include.METADATA = Include(metadata=True)
Include.SNAPSHOTS = Include(snapshots=True)
Include.UNCOMMITTED_BLOBS = Include(uncommitted_blobs=True)
Include.DELETED = Include(deleted=True)


class BlobPermissions(object):
    '''
    BlobPermissions class to be used with 
    :func:`~azure.storage.blob.baseblobservice.BaseBlobService.generate_blob_shared_access_signature` API.

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
    '''

    def __init__(self, read=False, add=False, create=False, write=False,
                 delete=False, _str=None):
        '''    
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
        '''
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


class ContainerPermissions(object):
    '''
    ContainerPermissions class to be used with :func:`~azure.storage.blob.baseblobservice.BaseBlobService.generate_container_shared_access_signature`
    API and for the AccessPolicies used with :func:`~azure.storage.blob.baseblobservice.BaseBlobService.set_container_acl`. 

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
    '''

    def __init__(self, read=False, add=False, create=False, write=False, delete=False, list=False,
                 _str=None):
        '''
        :param bool read:
            Read the content, properties, metadata or block list of any blob in the 
            container. Use any blob in the container as the source of a copy operation.
        :param bool add:
            Add a block to any append blob in the container.
        :param bool create:
            Write a new blob to the container, snapshot any blob in the container, or copy a blob to
            a new blob in the container. Note: You cannot grant permissions to create a container
            with a container SAS. Use an account SAS to create a container instead.
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
        '''
        if not _str:
            _str = ''
        self.read = read or ('r' in _str)
        self.add = add or ('a' in _str)
        self.create = create or ('c' in _str)
        self.write = write or ('w' in _str)
        self.delete = delete or ('d' in _str)
        self.list = list or ('l' in _str)

    def __or__(self, other):
        return ContainerPermissions(_str=str(self) + str(other))

    def __add__(self, other):
        return ContainerPermissions(_str=str(self) + str(other))

    def __str__(self):
        return (('r' if self.read else '') +
                ('a' if self.add else '') +
                ('c' if self.create else '') +
                ('w' if self.write else '') +
                ('d' if self.delete else '') +
                ('l' if self.list else ''))


ContainerPermissions.DELETE = ContainerPermissions(delete=True)
ContainerPermissions.LIST = ContainerPermissions(list=True)
ContainerPermissions.READ = ContainerPermissions(read=True)
ContainerPermissions.WRITE = ContainerPermissions(write=True)
ContainerPermissions.ADD = ContainerPermissions(add=True)
ContainerPermissions.CREATE = ContainerPermissions(create=True)


class PremiumPageBlobTier(object):
    '''
    Specifies the page blob tier to set the blob to. This is only applicable to page
    blobs on premium storage accounts.
    Please take a look at https://docs.microsoft.com/en-us/azure/storage/storage-premium-storage#scalability-and-performance-targets
    for detailed information on the corresponding IOPS and throughtput per PageBlobTier.
    '''

    P4 = 'P4'
    ''' P4 Tier '''

    P6 = 'P6'
    ''' P6 Tier '''

    P10 = 'P10'
    ''' P10 Tier '''

    P20 = 'P20'
    ''' P20 Tier '''

    P30 = 'P30'
    ''' P30 Tier '''

    P40 = 'P40'
    ''' P40 Tier '''

    P50 = 'P50'
    ''' P50 Tier '''

    P60 = 'P60'
    ''' P60 Tier '''


class StandardBlobTier(object):
    '''
    Specifies the blob tier to set the blob to. This is only applicable for block blobs on standard storage accounts.
    '''

    Archive = 'Archive'
    ''' Archive '''

    Cool = 'Cool'
    ''' Cool '''

    Hot = 'Hot'
    ''' Hot '''


class AccountInformation(object):
    """
    Holds information related to the storage account.

    :ivar str sku_name:
        Name of the storage SKU, also known as account type.
        Example: Standard_LRS, Standard_ZRS, Standard_GRS, Standard_RAGRS, Premium_LRS, Premium_ZRS
    :ivar str account_kind:
        Describes the flavour of the storage account, also known as account kind.
        Example: Storage, StorageV2, BlobStorage
    """
    def __init__(self):
        self.sku_name = None
        self.account_kind = None


class UserDelegationKey(object):
    """
    Represents a user delegation key, provided to the user by Azure Storage
    based on their Azure Active Directory access token.

    The fields are saved as simple strings since the user does not have to interact with this object;
    to generate an identify SAS, the user can simply pass it to the right API.

    :ivar str signed_oid:
        Object ID of this token.
    :ivar str signed_tid:
        Tenant ID of the tenant that issued this token.
    :ivar str signed_start:
        The datetime this token becomes valid.
    :ivar str signed_expiry:
        The datetime this token expires.
    :ivar str signed_service:
        What service this key is valid for.
    :ivar str signed_version:
        The version identifier of the REST service that created this token.
    :ivar str value:
        The user delegation key.
    """
    def __init__(self):
        self.signed_oid = None
        self.signed_tid = None
        self.signed_start = None
        self.signed_expiry = None
        self.signed_service = None
        self.signed_version = None
        self.value = None
