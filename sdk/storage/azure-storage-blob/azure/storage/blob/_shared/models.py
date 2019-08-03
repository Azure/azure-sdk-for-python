# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from enum import Enum


def get_enum_value(value):
    if value is None or value in ["None", ""]:
        return None
    try:
        return value.value
    except AttributeError:
        return value


class StorageErrorCode(str, Enum):

    # Generic storage values
    account_already_exists = "AccountAlreadyExists"
    account_being_created = "AccountBeingCreated"
    account_is_disabled = "AccountIsDisabled"
    authentication_failed = "AuthenticationFailed"
    authorization_failure = "AuthorizationFailure"
    condition_headers_not_supported = "ConditionHeadersNotSupported"
    condition_not_met = "ConditionNotMet"
    empty_metadata_key = "EmptyMetadataKey"
    insufficient_account_permissions = "InsufficientAccountPermissions"
    internal_error = "InternalError"
    invalid_authentication_info = "InvalidAuthenticationInfo"
    invalid_header_value = "InvalidHeaderValue"
    invalid_http_verb = "InvalidHttpVerb"
    invalid_input = "InvalidInput"
    invalid_md5 = "InvalidMd5"
    invalid_metadata = "InvalidMetadata"
    invalid_query_parameter_value = "InvalidQueryParameterValue"
    invalid_range = "InvalidRange"
    invalid_resource_name = "InvalidResourceName"
    invalid_uri = "InvalidUri"
    invalid_xml_document = "InvalidXmlDocument"
    invalid_xml_node_value = "InvalidXmlNodeValue"
    md5_mismatch = "Md5Mismatch"
    metadata_too_large = "MetadataTooLarge"
    missing_content_length_header = "MissingContentLengthHeader"
    missing_required_query_parameter = "MissingRequiredQueryParameter"
    missing_required_header = "MissingRequiredHeader"
    missing_required_xml_node = "MissingRequiredXmlNode"
    multiple_condition_headers_not_supported = "MultipleConditionHeadersNotSupported"
    operation_timed_out = "OperationTimedOut"
    out_of_range_input = "OutOfRangeInput"
    out_of_range_query_parameter_value = "OutOfRangeQueryParameterValue"
    request_body_too_large = "RequestBodyTooLarge"
    resource_type_mismatch = "ResourceTypeMismatch"
    request_url_failed_to_parse = "RequestUrlFailedToParse"
    resource_already_exists = "ResourceAlreadyExists"
    resource_not_found = "ResourceNotFound"
    server_busy = "ServerBusy"
    unsupported_header = "UnsupportedHeader"
    unsupported_xml_node = "UnsupportedXmlNode"
    unsupported_query_parameter = "UnsupportedQueryParameter"
    unsupported_http_verb = "UnsupportedHttpVerb"

    # Blob values
    append_position_condition_not_met = "AppendPositionConditionNotMet"
    blob_already_exists = "BlobAlreadyExists"
    blob_not_found = "BlobNotFound"
    blob_overwritten = "BlobOverwritten"
    blob_tier_inadequate_for_content_length = "BlobTierInadequateForContentLength"
    block_count_exceeds_limit = "BlockCountExceedsLimit"
    block_list_too_long = "BlockListTooLong"
    cannot_change_to_lower_tier = "CannotChangeToLowerTier"
    cannot_verify_copy_source = "CannotVerifyCopySource"
    container_already_exists = "ContainerAlreadyExists"
    container_being_deleted = "ContainerBeingDeleted"
    container_disabled = "ContainerDisabled"
    container_not_found = "ContainerNotFound"
    content_length_larger_than_tier_limit = "ContentLengthLargerThanTierLimit"
    copy_across_accounts_not_supported = "CopyAcrossAccountsNotSupported"
    copy_id_mismatch = "CopyIdMismatch"
    feature_version_mismatch = "FeatureVersionMismatch"
    incremental_copy_blob_mismatch = "IncrementalCopyBlobMismatch"
    incremental_copy_of_eralier_version_snapshot_not_allowed = "IncrementalCopyOfEralierVersionSnapshotNotAllowed"
    incremental_copy_source_must_be_snapshot = "IncrementalCopySourceMustBeSnapshot"
    infinite_lease_duration_required = "InfiniteLeaseDurationRequired"
    invalid_blob_or_block = "InvalidBlobOrBlock"
    invalid_blob_tier = "InvalidBlobTier"
    invalid_blob_type = "InvalidBlobType"
    invalid_block_id = "InvalidBlockId"
    invalid_block_list = "InvalidBlockList"
    invalid_operation = "InvalidOperation"
    invalid_page_range = "InvalidPageRange"
    invalid_source_blob_type = "InvalidSourceBlobType"
    invalid_source_blob_url = "InvalidSourceBlobUrl"
    invalid_version_for_page_blob_operation = "InvalidVersionForPageBlobOperation"
    lease_already_present = "LeaseAlreadyPresent"
    lease_already_broken = "LeaseAlreadyBroken"
    lease_id_mismatch_with_blob_operation = "LeaseIdMismatchWithBlobOperation"
    lease_id_mismatch_with_container_operation = "LeaseIdMismatchWithContainerOperation"
    lease_id_mismatch_with_lease_operation = "LeaseIdMismatchWithLeaseOperation"
    lease_id_missing = "LeaseIdMissing"
    lease_is_breaking_and_cannot_be_acquired = "LeaseIsBreakingAndCannotBeAcquired"
    lease_is_breaking_and_cannot_be_changed = "LeaseIsBreakingAndCannotBeChanged"
    lease_is_broken_and_cannot_be_renewed = "LeaseIsBrokenAndCannotBeRenewed"
    lease_lost = "LeaseLost"
    lease_not_present_with_blob_operation = "LeaseNotPresentWithBlobOperation"
    lease_not_present_with_container_operation = "LeaseNotPresentWithContainerOperation"
    lease_not_present_with_lease_operation = "LeaseNotPresentWithLeaseOperation"
    max_blob_size_condition_not_met = "MaxBlobSizeConditionNotMet"
    no_pending_copy_operation = "NoPendingCopyOperation"
    operation_not_allowed_on_incremental_copy_blob = "OperationNotAllowedOnIncrementalCopyBlob"
    pending_copy_operation = "PendingCopyOperation"
    previous_snapshot_cannot_be_newer = "PreviousSnapshotCannotBeNewer"
    previous_snapshot_not_found = "PreviousSnapshotNotFound"
    previous_snapshot_operation_not_supported = "PreviousSnapshotOperationNotSupported"
    sequence_number_condition_not_met = "SequenceNumberConditionNotMet"
    sequence_number_increment_too_large = "SequenceNumberIncrementTooLarge"
    snapshot_count_exceeded = "SnapshotCountExceeded"
    snaphot_operation_rate_exceeded = "SnaphotOperationRateExceeded"
    snapshots_present = "SnapshotsPresent"
    source_condition_not_met = "SourceConditionNotMet"
    system_in_use = "SystemInUse"
    target_condition_not_met = "TargetConditionNotMet"
    unauthorized_blob_overwrite = "UnauthorizedBlobOverwrite"
    blob_being_rehydrated = "BlobBeingRehydrated"
    blob_archived = "BlobArchived"
    blob_not_archived = "BlobNotArchived"

    # Queue values
    invalid_marker = "InvalidMarker"
    message_not_found = "MessageNotFound"
    message_too_large = "MessageTooLarge"
    pop_receipt_mismatch = "PopReceiptMismatch"
    queue_already_exists = "QueueAlreadyExists"
    queue_being_deleted = "QueueBeingDeleted"
    queue_disabled = "QueueDisabled"
    queue_not_empty = "QueueNotEmpty"
    queue_not_found = "QueueNotFound"

    # File values
    cannot_delete_file_or_directory = "CannotDeleteFileOrDirectory"
    client_cache_flush_delay = "ClientCacheFlushDelay"
    delete_pending = "DeletePending"
    directory_not_empty = "DirectoryNotEmpty"
    file_lock_conflict = "FileLockConflict"
    invalid_file_or_directory_path_name = "InvalidFileOrDirectoryPathName"
    parent_not_found = "ParentNotFound"
    read_only_attribute = "ReadOnlyAttribute"
    share_already_exists = "ShareAlreadyExists"
    share_being_deleted = "ShareBeingDeleted"
    share_disabled = "ShareDisabled"
    share_not_found = "ShareNotFound"
    sharing_violation = "SharingViolation"
    share_snapshot_in_progress = "ShareSnapshotInProgress"
    share_snapshot_count_exceeded = "ShareSnapshotCountExceeded"
    share_snapshot_operation_not_supported = "ShareSnapshotOperationNotSupported"
    share_has_snapshots = "ShareHasSnapshots"
    container_quota_downgrade_not_allowed = "ContainerQuotaDowngradeNotAllowed"


class DictMixin(object):

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    def __repr__(self):
        return str(self)

    def __len__(self):
        return len(self.keys())

    def __delitem__(self, key):
        self.__dict__[key] = None

    def __eq__(self, other):
        """Compare objects by comparing all attributes."""
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        """Compare objects by comparing all attributes."""
        return not self.__eq__(other)

    def __str__(self):
        return str({k: v for k, v in self.__dict__.items() if not k.startswith('_')})

    def has_key(self, k):
        return k in self.__dict__

    def update(self, *args, **kwargs):
        return self.__dict__.update(*args, **kwargs)

    def keys(self):
        return [k for k in self.__dict__ if not k.startswith('_')]

    def values(self):
        return [v for k, v in self.__dict__.items() if not k.startswith('_')]

    def items(self):
        return [(k, v) for k, v in self.__dict__.items() if not k.startswith('_')]

    def get(self, key, default=None):
        if key in self.__dict__:
            return self.__dict__[key]
        return default


class LocationMode(object):
    """
    Specifies the location the request should be sent to. This mode only applies
    for RA-GRS accounts which allow secondary read access. All other account types
    must use PRIMARY.
    """

    PRIMARY = 'primary'  #: Requests should be sent to the primary location.
    SECONDARY = 'secondary'  #: Requests should be sent to the secondary location, if possible.


class ResourceTypes(object):
    """
    Specifies the resource types that are accessible with the account SAS.

    :cvar ResourceTypes ResourceTypes.CONTAINER:
        Access to container-level APIs (e.g., Create/Delete Container,
        Create/Delete Queue, Create/Delete Share,
        List Blobs/Files and Directories)
    :cvar ResourceTypes ResourceTypes.OBJECT:
        Access to object-level APIs for blobs, queue messages, and
        files(e.g. Put Blob, Query Entity, Get Messages, Create File, etc.)
    :cvar ResourceTypes ResourceTypes.SERVICE:
        Access to service-level APIs (e.g., Get/Set Service Properties,
        Get Service Stats, List Containers/Queues/Shares)
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

    SERVICE = None  # type: ResourceTypes
    CONTAINER = None  # type: ResourceTypes
    OBJECT = None  # type: ResourceTypes

    def __init__(self, service=False, container=False, object=False, _str=None):  # pylint: disable=redefined-builtin
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

    :cvar AccountPermissions AccountPermissions.ADD:
        Valid for the following Object resource types only: queue messages and append blobs.
    :cvar AccountPermissions AccountPermissions.CREATE:
        Valid for the following Object resource types only: blobs and files. Users
        can create new blobs or files, but may not overwrite existing blobs or files.
    :cvar AccountPermissions AccountPermissions.DELETE:
        Valid for Container and Object resource types, except for queue messages.
    :cvar AccountPermissions AccountPermissions.LIST:
        Valid for Service and Container resource types only.
    :cvar AccountPermissions AccountPermissions.PROCESS:
        Valid for the following Object resource type only: queue messages.
    :cvar AccountPermissions AccountPermissions.READ:
        Valid for all signed resources types (Service, Container, and Object).
        Permits read permissions to the specified resource type.
    :cvar AccountPermissions AccountPermissions.UPDATE:
        Valid for the following Object resource types only: queue messages.
    :cvar AccountPermissions AccountPermissions.WRITE:
        Valid for all signed resources types (Service, Container, and Object).
        Permits write permissions to the specified resource type.
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


class Services(object):
    """Specifies the services accessible with the account SAS.

    :cvar Services Services.BLOB: The blob service.
    :cvar Services Services.FILE: The file service
    :cvar Services Services.QUEUE: The queue service.
    :param bool blob:
        Access for the `~azure.storage.blob.blob_service_client.BlobServiceClient`
    :param bool queue:
        Access for the `~azure.storage.queue.queue_service_client.QueueServiceClient`
    :param bool file:
        Access for the `~azure.storage.file.file_service_client.FileServiceClient`
    :param str _str:
        A string representing the services.
    """

    BLOB = None # type: Services
    QUEUE = None # type: Services
    FILE = None # type: Services

    def __init__(self, blob=False, queue=False, file=False, _str=None):
        if not _str:
            _str = ''
        self.blob = blob or ('b' in _str)
        self.queue = queue or ('q' in _str)
        self.file = file or ('f' in _str)

    def __or__(self, other):
        return Services(_str=str(self) + str(other))

    def __add__(self, other):
        return Services(_str=str(self) + str(other))

    def __str__(self):
        return (('b' if self.blob else '') +
                ('q' if self.queue else '') +
                ('f' if self.file else ''))


Services.BLOB = Services(blob=True)
Services.QUEUE = Services(queue=True)
Services.FILE = Services(file=True)
