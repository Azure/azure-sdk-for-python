# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-few-public-methods, too-many-instance-attributes, super-init-not-called, too-many-lines

from enum import Enum
from typing import (
    Any, Callable, Dict, List, Literal, Optional, Union,
    TYPE_CHECKING
)
from urllib.parse import unquote
from typing_extensions import Self

from azure.core import CaseInsensitiveEnumMeta
from azure.core.exceptions import HttpResponseError
from azure.core.paging import PageIterator

from ._generated._utils.serialization import Deserializer
from ._generated.models import AccessPolicy as GenAccessPolicy
from ._generated.models import CorsRule as GeneratedCorsRule
from ._generated.models import DirectoryItem
from ._generated.models import Metrics as GeneratedMetrics
from ._generated.models import RetentionPolicy as GeneratedRetentionPolicy
from ._generated.models import ShareNfsSettings as GeneratedShareNfsSettings
from ._generated.models import ShareNfsSettingsEncryptionInTransit as GeneratedNfsEncryptionInTransit
from ._generated.models import ShareProtocolSettings as GeneratedShareProtocolSettings
from ._generated.models import ShareSmbSettings as GeneratedShareSmbSettings
from ._generated.models import ShareSmbSettingsEncryptionInTransit as GeneratedSmbEncryptionInTransit
from ._generated.models import SmbMultichannel as GeneratedSmbMultichannel
from ._generated.models import StorageServiceProperties as GeneratedStorageServiceProperties
from ._shared.models import DictMixin, get_enum_value
from ._shared.response_handlers import process_storage_error, return_context_and_deserialized

if TYPE_CHECKING:
    from datetime import datetime
    from ._generated.models import ShareRootSquash


def _wrap_item(item):
    if isinstance(item, DirectoryItem):
        return {'name': item.name, 'is_directory': True}
    return {'name': item.name, 'size': item.properties.content_length, 'is_directory': False}


class RetentionPolicy(GeneratedRetentionPolicy):
    """The retention policy which determines how long the associated data should
    persist.

    All required parameters must be populated in order to send to Azure.

    :param bool enabled:
        Indicates whether a retention policy is enabled for the storage service.
    :param Optional[int] days:
        Indicates the number of days that metrics or logging or soft-deleted data should be retained.
        All data older than this value will be deleted.
    """

    enabled: bool = False
    """Indicates whether a retention policy is enabled for the storage service."""
    days: Optional[int] = None
    """Indicates the number of days that metrics or logging or soft-deleted data should be retained.
        All data older than this value will be deleted."""

    def __init__(self, enabled: bool = False, days: Optional[int] = None) -> None:
        self.enabled = enabled
        self.days = days
        if self.enabled and (self.days is None):
            raise ValueError("If policy is enabled, 'days' must be specified.")

    @classmethod
    def _from_generated(cls, generated):
        if not generated:
            return cls()
        return cls(
            enabled=generated.enabled,
            days=generated.days,
        )


class Metrics(GeneratedMetrics):
    """A summary of request statistics grouped by API in hour or minute aggregates
    for files.

    All required parameters must be populated in order to send to Azure.

    :keyword str version:
        The version of Storage Analytics to configure. The default value is 1.0.
    :keyword bool enabled:
        Indicates whether metrics are enabled for the File service.
    :keyword bool include_apis:
        Indicates whether metrics should generate summary statistics for called API operations.
    :keyword ~azure.storage.fileshare.RetentionPolicy retention_policy:
        Determines how long the associated data should persist.
    """

    version: str = '1.0'
    """The version of Storage Analytics to configure."""
    enabled: bool = False
    """Indicates whether metrics are enabled for the File service."""
    include_apis: bool
    """Indicates whether metrics should generate summary statistics for called API operations."""
    retention_policy: RetentionPolicy = RetentionPolicy()
    """Determines how long the associated data should persist."""

    def __init__(self, **kwargs: Any) -> None:
        self.version = kwargs.get('version', '1.0')
        self.enabled = kwargs.get('enabled', False)
        self.include_apis = kwargs.get('include_apis')  # type: ignore [assignment]
        self.retention_policy = kwargs.get('retention_policy') or RetentionPolicy()

    @classmethod
    def _from_generated(cls, generated):
        if not generated:
            return cls()
        return cls(
            version=generated.version,
            enabled=generated.enabled,
            include_apis=generated.include_apis,
            retention_policy=RetentionPolicy._from_generated(generated.retention_policy)  # pylint: disable=protected-access
        )


class CorsRule(GeneratedCorsRule):
    """CORS is an HTTP feature that enables a web application running under one
    domain to access resources in another domain. Web browsers implement a
    security restriction known as same-origin policy that prevents a web page
    from calling APIs in a different domain; CORS provides a secure way to
    allow one domain (the origin domain) to call APIs in another domain.

    All required parameters must be populated in order to send to Azure.

    :param List[str] allowed_origins:
        A list of origin domains that will be allowed via CORS, or "*" to allow
        all domains. The list of must contain at least one entry. Limited to 64
        origin domains. Each allowed origin can have up to 256 characters.
    :param List[str] allowed_methods:
        A list of HTTP methods that are allowed to be executed by the origin.
        The list of must contain at least one entry. For Azure Storage,
        permitted methods are DELETE, GET, HEAD, MERGE, POST, OPTIONS or PUT.
    :keyword List[str] allowed_headers:
        Defaults to an empty list. A list of headers allowed to be part of
        the cross-origin request. Limited to 64 defined headers and 2 prefixed
        headers. Each header can be up to 256 characters.
    :keyword List[str] exposed_headers:
        Defaults to an empty list. A list of response headers to expose to CORS
        clients. Limited to 64 defined headers and two prefixed headers. Each
        header can be up to 256 characters.
    :keyword int max_age_in_seconds:
        The number of seconds that the client/browser should cache a
        preflight response.
    """

    allowed_origins: str
    """The comma-delimited string representation of the list of origin domains
        that will be allowed via CORS, or "*" to allow all domains."""
    allowed_methods: str
    """The comma-delimited string representation of the list of HTTP methods
        that are allowed to be executed by the origin."""
    allowed_headers: str
    """The comma-delimited string representation of the list of headers
        allowed to be a part of the cross-origin request."""
    exposed_headers: str
    """The comma-delimited string representation of the list of response
        headers to expose to CORS clients."""
    max_age_in_seconds: int
    """The number of seconds that the client/browser should cache a pre-flight response."""

    def __init__(self, allowed_origins: List[str], allowed_methods: List[str], **kwargs: Any) -> None:
        self.allowed_origins = ','.join(allowed_origins)
        self.allowed_methods = ','.join(allowed_methods)
        self.allowed_headers = ','.join(kwargs.get('allowed_headers', []))
        self.exposed_headers = ','.join(kwargs.get('exposed_headers', []))
        self.max_age_in_seconds = kwargs.get('max_age_in_seconds', 0)

    @staticmethod
    def _to_generated(rules: Optional[List["CorsRule"]]) -> Optional[List[GeneratedCorsRule]]:
        if rules is None:
            return rules

        generated_cors_list = []
        for cors_rule in rules:
            generated_cors = GeneratedCorsRule(
                allowed_origins=cors_rule.allowed_origins,
                allowed_methods=cors_rule.allowed_methods,
                allowed_headers=cors_rule.allowed_headers,
                exposed_headers=cors_rule.exposed_headers,
                max_age_in_seconds=cors_rule.max_age_in_seconds,
            )
            generated_cors_list.append(generated_cors)

        return generated_cors_list

    @classmethod
    def _from_generated(cls, generated):
        return cls(
            [generated.allowed_origins],
            [generated.allowed_methods],
            allowed_headers=[generated.allowed_headers],
            exposed_headers=[generated.exposed_headers],
            max_age_in_seconds=generated.max_age_in_seconds,
        )


class SmbMultichannel(GeneratedSmbMultichannel):
    """Settings for Multichannel.

    :keyword bool enabled: If SMB Multichannel is enabled.
    """

    enabled: bool
    """If SMB Multichannel is enabled."""

    def __init__(self, *, enabled: bool, **kwargs: Any) -> None:
        self.enabled = enabled


class SmbEncryptionInTransit(GeneratedSmbEncryptionInTransit):
    """Settings for encryption in transit.

    :keyword bool required: If encryption in transit is required.
    """

    required: bool
    """If encryption in transit is enabled."""

    def __init__(self, *, required: bool, **kwargs: Any) -> None:
        self.required = required


class ShareSmbSettings(GeneratedShareSmbSettings):
    """Settings for the SMB protocol.

    :keyword SmbMultichannel multichannel: Sets the multichannel settings.
    :keyword SmbEncryptionInTransit encryption_in_transit: Sets the encryption in transit settings.
    """

    multichannel: Optional[SmbMultichannel]
    """Sets the multichannel settings."""
    encryption_in_transit: Optional[SmbEncryptionInTransit]
    """Sets the encryption in transit settings."""

    def __init__(
        self,
        *,
        multichannel: Optional[SmbMultichannel] = None,
        encryption_in_transit: Optional[SmbEncryptionInTransit] = None,
        **kwargs: Any
    ) -> None:
        self.multichannel = multichannel
        self.encryption_in_transit = encryption_in_transit
        if self.multichannel is None and self.encryption_in_transit is None:
            raise ValueError("The value 'multichannel' or 'encryption_in_transit' must be specified.")


class NfsEncryptionInTransit(GeneratedNfsEncryptionInTransit):
    """Settings for encryption in transit.

    :keyword bool required: If encryption in transit is required.
    """

    required: bool
    """If encryption in transit is enabled."""

    def __init__(self, *, required: bool, **kwargs: Any) -> None:
        self.required = required


class ShareNfsSettings(GeneratedShareNfsSettings):
    """Settings for the NFS protocol.

    :keyword NfsEncryptionInTransit encryption_in_transit: Sets the encryption in transit settings.
    """

    encryption_in_transit: NfsEncryptionInTransit
    """Sets the encryption in transit settings."""

    def __init__(self, *, encryption_in_transit: NfsEncryptionInTransit, **kwargs: Any) -> None:
        self.encryption_in_transit = encryption_in_transit


class ShareProtocolSettings(GeneratedShareProtocolSettings):
    """Protocol Settings class used by the set and get service properties methods in the share service.

    Contains protocol properties of the share service such as the SMB and NFS setting of the share service.

    :keyword ShareSmbSettings smb: Sets SMB settings.
    :keyword ShareNfsSettings nfs: Sets NFS settings.
    """

    smb: Optional[ShareSmbSettings]
    """Sets the SMB settings."""
    nfs: Optional[ShareNfsSettings]
    """Sets the NFS settings."""

    def __init__(
        self,
        *,
        smb: Optional[ShareSmbSettings] = None,
        nfs: Optional[ShareNfsSettings] = None,
        **kwargs: Any
    ) -> None:
        self.smb = smb
        self.nfs = nfs
        if self.smb is None and self.nfs is None:
            raise ValueError("The value 'smb' or 'nfs' must be specified.")

    @classmethod
    def _from_generated(cls, generated):
        return cls(smb=generated.smb, nfs=generated.nfs)


class ShareSasPermissions:
    """ShareSasPermissions class to be used to be used with
    generating shared access signature and access policy operations.

    :param bool read:
        Read the content, properties or metadata of any file in the share. Use any
        file in the share as the source of a copy operation.
    :param bool write:
        For any file in the share, create or write content, properties or metadata.
        Resize the file. Use the file as the destination of a copy operation within
        the same account.
        Note: You cannot grant permissions to read or write share properties or
        metadata with a service SAS. Use an account SAS instead.
    :param bool delete:
        Delete any file in the share.
        Note: You cannot grant permissions to delete a share with a service SAS. Use
        an account SAS instead.
    :param bool list:
        List files and directories in the share.
    :param bool create:
        Create a new file in the share, or copy a file to a new file in the share.
    """

    read: bool = False
    """The read permission for share SAS."""
    write: bool = False
    """The write permission for share SAS."""
    delete: bool = False
    """The delete permission for share SAS."""
    list: bool = False
    """The list permission for share SAS."""
    create: bool = False
    """The create permission for share SAS."""

    def __init__(
        self, read: bool = False,
        write: bool = False,
        delete: bool = False,
        list: bool = False,
        create: bool = False
    ) -> None:
        self.read = read
        self.create = create
        self.write = write
        self.delete = delete
        self.list = list
        self._str = (('r' if self.read else '') +
                     ('c' if self.create else '') +
                     ('w' if self.write else '') +
                     ('d' if self.delete else '') +
                     ('l' if self.list else ''))

    def __str__(self) -> str:
        return self._str

    @classmethod
    def from_string(cls, permission: str) -> Self:
        """Create a ShareSasPermissions from a string.

        To specify read, create, write, delete, or list permissions you need only to
        include the first letter of the word in the string. E.g. For read and
        write permissions, you would provide a string "rw".

        :param str permission: The string which dictates the read, create, write,
            delete, or list permissions
        :return: A ShareSasPermissions object
        :rtype: ~azure.storage.fileshare.ShareSasPermissions
        """
        p_read = 'r' in permission
        p_create = 'c' in permission
        p_write = 'w' in permission
        p_delete = 'd' in permission
        p_list = 'l' in permission

        parsed = cls(p_read, p_write, p_delete, p_list, p_create)

        return parsed


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
    :type permission: str or ~azure.storage.fileshare.FileSasPermissions or
        ~azure.storage.fileshare.ShareSasPermissions
    :param expiry:
        The time at which the shared access signature becomes invalid.
        Required unless an id is given referencing a stored access policy
        which contains this field. This field must be omitted if it has
        been specified in an associated stored access policy. Azure will always
        convert values to UTC. If a date is passed in without timezone info, it
        is assumed to be UTC.
    :type expiry: ~datetime.datetime or str
    :param start:
        The time at which the shared access signature becomes valid. If
        omitted, start time for this call is assumed to be the time when the
        storage service receives the request. The provided datetime will always
        be interpreted as UTC.
    :type start: ~datetime.datetime or str
    """

    permission: Optional[Union[ShareSasPermissions, str]]  # type: ignore [assignment]
    """The permissions associated with the shared access signature. The user is restricted to
        operations allowed by the permissions."""
    expiry: Optional[Union["datetime", str]]  # type: ignore [assignment]
    """The time at which the shared access signature becomes invalid."""
    start: Optional[Union["datetime", str]]  # type: ignore [assignment]
    """The time at which the shared access signature becomes valid."""

    def __init__(
        self, permission: Optional[Union[ShareSasPermissions, str]] = None,
        expiry: Optional[Union["datetime", str]] = None,
        start: Optional[Union["datetime", str]] = None
    ) -> None:
        self.start = start
        self.expiry = expiry
        self.permission = permission


class LeaseProperties(DictMixin):
    """File or Share Lease Properties."""

    status: str
    """The lease status of the file or share. Possible values: locked|unlocked"""
    state: str
    """Lease state of the file or share. Possible values: available|leased|expired|breaking|broken"""
    duration: Optional[str]
    """When a file or share is leased, specifies whether the lease is of infinite or fixed duration."""

    def __init__(self, **kwargs: Any) -> None:
        self.status = get_enum_value(kwargs.get('x-ms-lease-status'))
        self.state = get_enum_value(kwargs.get('x-ms-lease-state'))
        self.duration = get_enum_value(kwargs.get('x-ms-lease-duration'))

    @classmethod
    def _from_generated(cls, generated):
        lease = cls()
        lease.status = get_enum_value(generated.properties.lease_status)
        lease.state = get_enum_value(generated.properties.lease_state)
        lease.duration = get_enum_value(generated.properties.lease_duration)
        return lease


class ContentSettings(DictMixin):
    """Used to store the content settings of a file.

    :param Optional[str] content_type:
        The content type specified for the file. If no content type was
        specified, the default content type is application/octet-stream.
    :param Optional[str] content_encoding:
        If the content_encoding has previously been set
        for the file, that value is stored.
    :param Optional[str] content_language:
        If the content_language has previously been set
        for the file, that value is stored.
    :param Optional[str] content_disposition:
        content_disposition conveys additional information about how to
        process the response payload, and also can be used to attach
        additional metadata. If content_disposition has previously been set
        for the file, that value is stored.
    :param Optional[str] cache_control:
        If the cache_control has previously been set for
        the file, that value is stored.
    :param Optional[bytearray] content_md5:
        If the content_md5 has been set for the file, this response
        header is stored so that the client can check for message content
        integrity.
    """

    content_type: Optional[str] = None
    """The content type specified for the file."""
    content_encoding: Optional[str] = None
    """The content encoding specified for the file."""
    content_language: Optional[str] = None
    """The content language specified for the file."""
    content_disposition: Optional[str] = None
    """The content disposition specified for the file."""
    cache_control: Optional[str] = None
    """The cache control specified for the file."""
    content_md5: Optional[bytearray] = None
    """The content md5 specified for the file."""

    def __init__(
        self, content_type: Optional[str] = None,
        content_encoding: Optional[str] = None,
        content_language: Optional[str] = None,
        content_disposition: Optional[str] = None,
        cache_control: Optional[str] = None,
        content_md5: Optional[bytearray] = None,
        **kwargs: Any
    ) -> None:
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


class ShareProperties(DictMixin):
    """Share's properties class."""

    name: str
    """The name of the share."""
    last_modified: "datetime"
    """A datetime object representing the last time the share was modified."""
    etag: str
    """The ETag contains a value that you can use to perform operations conditionally."""
    quota: int
    """The allocated quota."""
    access_tier: str
    """The share's access tier.'"""
    next_allowed_quota_downgrade_time: Optional[str] = None
    """The share's next allowed quota downgrade time."""
    metadata: Dict[str, str]
    """Name-value pairs associate with the share as metadata."""
    snapshot: Optional[str] = None
    """Snapshot of the share."""
    deleted: Optional[bool] = None
    """Whether this share was deleted. 
        This is a service returned value, and the value will be set when list shared including deleted ones."""
    deleted_time: Optional["datetime"] = None
    """A datetime object representing the time at which the share was deleted.
        This is a service returned value, and the value will be set when list shared including deleted ones."""
    version: Optional[str] = None
    """To indicate the version of deleted share.
        This is a service returned value, and the value will be set when list shared including deleted ones."""
    remaining_retention_days: Optional[int] = None
    """The number of days that the share will be retained before being permanently deleted by the service.
        This is a service returned value, and the value will be set when list shared including deleted ones."""
    provisioned_egress_mbps: Optional[int] = None
    """Provisioned egress in megabits/second. Only applicable to premium file accounts."""
    provisioned_ingress_mbps: Optional[int] = None
    """Provisioned ingress in megabits/second. Only applicable to premium file accounts."""
    provisioned_iops: Optional[int] = None
    """Provisioned input/output operators per second (iops). Only applicable to premium file accounts."""
    provisioned_bandwidth: Optional[int] = None
    """Provisioned bandwidth in megabits/second. Only applicable to premium file accounts."""
    lease: LeaseProperties
    """Share lease properties."""
    protocols: Optional[List[str]] = None
    """Indicates the protocols enabled on the share. The protocol can be either SMB or NFS."""
    root_squash: Optional[Union["ShareRootSquash", str]] = None
    """Possible values include: 'NoRootSquash', 'RootSquash', 'AllSquash'."""
    enable_snapshot_virtual_directory_access: Optional[bool] = None
    """Specifies whether the snapshot virtual directory should be accessible at the root of the share
        mount point when NFS is enabled. if not specified, the default is True."""
    paid_bursting_enabled: Optional[int] = None
    """This property enables paid bursting."""
    paid_bursting_bandwidth_mibps: Optional[int] = None
    """The maximum throughput the file share can support in MiB/s."""
    paid_bursting_iops: Optional[int] = None
    """The maximum IOPS the file share can support."""
    next_provisioned_iops_downgrade: Optional["datetime"]
    """The share's next allowed provisioned throughput downgrade time."""
    next_provisioned_bandwidth_downgrade: Optional["datetime"]
    """The share's next allowed provisioned bandwidth downgrade time."""

    def __init__(self, **kwargs: Any) -> None:
        self.name = None  # type: ignore [assignment]
        self.last_modified = kwargs.get('Last-Modified')  # type: ignore [assignment]
        self.etag = kwargs.get('ETag')  # type: ignore [assignment]
        self.quota = kwargs.get('x-ms-share-quota')  # type: ignore [assignment]
        self.access_tier = kwargs.get('x-ms-access-tier')  # type: ignore [assignment]
        self.next_allowed_quota_downgrade_time = kwargs.get('x-ms-share-next-allowed-quota-downgrade-time')
        self.metadata = kwargs.get('metadata')  # type: ignore [assignment]
        self.snapshot = None
        self.deleted = None
        self.deleted_time = None
        self.version = None
        self.remaining_retention_days = None
        self.provisioned_egress_mbps = kwargs.get('x-ms-share-provisioned-egress-mbps')
        self.provisioned_ingress_mbps = kwargs.get('x-ms-share-provisioned-ingress-mbps')
        self.provisioned_iops = kwargs.get('x-ms-share-provisioned-iops')
        self.provisioned_bandwidth = kwargs.get('x-ms-share-provisioned-bandwidth-mibps')
        self.lease = LeaseProperties(**kwargs)
        enabled_protocols = kwargs.get("x-ms-enabled-protocols", None)
        if enabled_protocols is not None:
            self.protocols = [protocol.strip() for protocol in enabled_protocols.split(',')]
        else:
            self.protocols = None
        self.root_squash = kwargs.get('x-ms-root-squash', None)
        self.enable_snapshot_virtual_directory_access = \
            kwargs.get('x-ms-enable-snapshot-virtual-directory-access')
        self.paid_bursting_enabled = kwargs.get('x-ms-share-paid-bursting-enabled')
        self.paid_bursting_bandwidth_mibps = kwargs.get('x-ms-share-paid-bursting-max-bandwidth-mibps')
        self.paid_bursting_iops = kwargs.get('x-ms-share-paid-bursting-max-iops')
        self.included_burst_iops = kwargs.get('x-ms-share-included-burst-iops')
        self.max_burst_credits_for_iops = kwargs.get('x-ms-share-max-burst-credits-for-iops')
        self.next_provisioned_iops_downgrade = (  # pylint: disable=name-too-long
            kwargs.get('x-ms-share-next-allowed-provisioned-iops-downgrade-time'))
        self.next_provisioned_bandwidth_downgrade = (  # pylint: disable=name-too-long
            kwargs.get('x-ms-share-next-allowed-provisioned-bandwidth-downgrade-time'))

    @classmethod
    def _from_generated(cls, generated):
        props = cls()
        props.name = generated.name
        props.last_modified = generated.properties.last_modified
        props.etag = generated.properties.etag
        props.quota = generated.properties.quota
        props.access_tier = generated.properties.access_tier
        props.next_allowed_quota_downgrade_time = generated.properties.next_allowed_quota_downgrade_time
        props.metadata = generated.metadata
        props.snapshot = generated.snapshot
        props.deleted = generated.deleted
        props.deleted_time = generated.properties.deleted_time
        props.version = generated.version
        props.remaining_retention_days = generated.properties.remaining_retention_days
        props.provisioned_egress_mbps = generated.properties.provisioned_egress_m_bps
        props.provisioned_ingress_mbps = generated.properties.provisioned_ingress_m_bps
        props.provisioned_iops = generated.properties.provisioned_iops
        props.provisioned_bandwidth = generated.properties.provisioned_bandwidth_mi_bps
        props.lease = LeaseProperties._from_generated(generated)  # pylint: disable=protected-access
        props.protocols = [protocol.strip() for protocol in generated.properties.enabled_protocols.split(',')]\
            if generated.properties.enabled_protocols else None
        props.root_squash = generated.properties.root_squash
        props.enable_snapshot_virtual_directory_access = generated.properties.enable_snapshot_virtual_directory_access
        props.paid_bursting_enabled = generated.properties.paid_bursting_enabled
        props.paid_bursting_bandwidth_mibps = generated.properties.paid_bursting_max_bandwidth_mibps
        props.paid_bursting_iops = generated.properties.paid_bursting_max_iops
        props.included_burst_iops = generated.properties.included_burst_iops
        props.max_burst_credits_for_iops = generated.properties.max_burst_credits_for_iops
        props.next_provisioned_iops_downgrade = (  # pylint: disable=name-too-long
            generated.properties.next_allowed_provisioned_iops_downgrade_time)
        props.next_provisioned_bandwidth_downgrade = (  # pylint: disable=name-too-long
            generated.properties.next_allowed_provisioned_bandwidth_downgrade_time)
        return props


class SharePropertiesPaged(PageIterator):
    """An iterable of Share properties.

    :param Callable command: Function to retrieve the next page of items.
    :param Optional[str] prefix: Filters the results to return only shares whose names
        begin with the specified prefix.
    :param Optional[int] results_per_page: The maximum number of share names to retrieve per call.
    :param Optional[str] continuation_token: An opaque continuation token to retrieve the next page of results.
    """

    service_endpoint: Optional[str] = None
    """The service URL."""
    prefix: Optional[str] = None
    """A filename prefix being used to filter the list."""
    marker: Optional[str] = None
    """The continuation token of the current page of results."""
    results_per_page: Optional[int] = None
    """The maximum number of results to retrieve per API call."""
    location_mode: Optional[str] = None
    """The location mode being used to list results. The available
        options include "primary" and "secondary"."""
    current_page: List[ShareProperties]
    """The current page of listed results."""

    def __init__(
        self, command: Callable,
        prefix: Optional[str] = None,
        results_per_page: Optional[int] = None,
        continuation_token: Optional[str] = None
    ) -> None:
        super(SharePropertiesPaged, self).__init__(
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
                prefix=self.prefix,
                cls=return_context_and_deserialized,
                use_location=self.location_mode)
        except HttpResponseError as error:
            process_storage_error(error)

    def _extract_data_cb(self, get_next_return):
        self.location_mode, self._response = get_next_return
        self.service_endpoint = self._response.service_endpoint
        self.prefix = self._response.prefix
        self.marker = self._response.marker
        self.results_per_page = self._response.max_results
        self.current_page = [ShareProperties._from_generated(i) for i in self._response.share_items]  # pylint: disable=protected-access
        return self._response.next_marker or None, self.current_page


class Handle(DictMixin):
    """A listed Azure Storage handle item.

    All required parameters must be populated in order to send to Azure.

    :keyword str client_name: Name of the client machine where the share is being mounted.
    :keyword str handle_id: XSMB service handle ID.
    :keyword str path: File or directory name including full path starting from share root.
    :keyword str file_id: FileId uniquely identifies the file or directory.
    :keyword str parent_id: ParentId uniquely identifies the parent directory of the object.
    :keyword str session_id: SMB session ID in context of which the file handle was opened.
    :keyword str client_ip: Client IP that opened the handle.
    :keyword ~datetime.datetime open_time: Time when the session that previously opened
        the handle has last been reconnected. (UTC)
    :keyword Optional[~datetime.datetime] last_reconnect_time: Time handle was last connected to. (UTC)
    :keyword access_rights: Access rights of the handle.
    :paramtype access_rights: List[Literal['Read', 'Write', 'Delete']]
    """

    client_name: str
    """Name of the client machine where the share is being mounted."""
    id: str
    """XSMB service handle ID."""
    path: str
    """File or directory name including full path starting from share root."""
    file_id: str
    """FileId uniquely identifies the file or directory."""
    parent_id: str
    """ParentId uniquely identifies the parent directory of the object."""
    session_id: str
    """SMB session ID in context of which the file handle was opened."""
    client_ip: str
    """Client IP that opened the handle."""
    open_time: "datetime"
    """Time when the session that previously opened the handle was last been reconnected. (UTC)"""
    last_reconnect_time: Optional["datetime"]
    """Time handle that was last connected to. (UTC)"""
    access_rights: List[Literal['Read', 'Write', 'Delete']]
    """Access rights of the handle."""

    def __init__(self, **kwargs: Any) -> None:
        self.client_name = kwargs.get('client_name')  # type: ignore [assignment]
        self.id = kwargs.get('handle_id')  # type: ignore [assignment]
        self.path = kwargs.get('path')  # type: ignore [assignment]
        self.file_id = kwargs.get('file_id')  # type: ignore [assignment]
        self.parent_id = kwargs.get('parent_id')  # type: ignore [assignment]
        self.session_id = kwargs.get('session_id')  # type: ignore [assignment]
        self.client_ip = kwargs.get('client_ip')  # type: ignore [assignment]
        self.open_time = kwargs.get('open_time')  # type: ignore [assignment]
        self.last_reconnect_time = kwargs.get('last_reconnect_time')
        self.access_rights = kwargs.get('access_right_list')  # type: ignore [assignment]

    @classmethod
    def _from_generated(cls, generated):
        handle = cls()
        handle.client_name = generated.client_name
        handle.id = generated.handle_id
        handle.path = unquote(generated.path.content) if generated.path.encoded else generated.path.content
        handle.file_id = generated.file_id
        handle.parent_id = generated.parent_id
        handle.session_id = generated.session_id
        handle.client_ip = generated.client_ip
        handle.open_time = generated.open_time
        handle.last_reconnect_time = generated.last_reconnect_time
        handle.access_rights = generated.access_right_list
        return handle


class HandlesPaged(PageIterator):
    """An iterable of Handles.

    :param Callable command: Function to retrieve the next page of items.
    :param Optional[int] results_per_page: The maximum number of share names to retrieve per call.
    :param Optional[str] continuation_token: An opaque continuation token to retrieve the next page of results.
    """

    marker: Optional[str] = None
    """The continuation token of the current page of results."""
    results_per_page: Optional[int] = None
    """The maximum number of results retrieved per API call."""
    location_mode: Optional[str] = None
    """The location mode being used to list results.
        The available options include "primary" and "secondary"."""
    current_page: List[Handle]
    """The current page of listed results."""

    def __init__(
        self, command: Callable,
        results_per_page: Optional[int] = None,
        continuation_token: Optional[str] = None
    ) -> None:
        super(HandlesPaged, self).__init__(
            get_next=self._get_next_cb,
            extract_data=self._extract_data_cb,
            continuation_token=continuation_token or ""
        )
        self._command = command
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
        except HttpResponseError as error:
            process_storage_error(error)

    def _extract_data_cb(self, get_next_return):
        self.location_mode, self._response = get_next_return
        self.current_page = [Handle._from_generated(h) for h in self._response.handle_list]  # pylint: disable=protected-access
        return self._response.next_marker or None, self.current_page


class NTFSAttributes:
    """Valid set of attributes to set for file or directory.

    To set attribute for directory, 'Directory' should always be enabled except setting 'None' for directory.
    """

    read_only: bool = False
    """Enable/disable 'ReadOnly' attribute for DIRECTORY or FILE."""
    hidden: bool = False
    """Enable/disable 'Hidden' attribute for DIRECTORY or FILE."""
    system: bool = False
    """Enable/disable 'System' attribute for DIRECTORY or FILE."""
    none: bool = False
    """Enable/disable 'None' attribute for DIRECTORY or FILE to clear all attributes of FILE/DIRECTORY."""
    directory: bool = False
    """Enable/disable 'Directory' attribute for DIRECTORY."""
    archive: bool = False
    """Enable/disable 'Archive' attribute for DIRECTORY."""
    temporary: bool = False
    """Enable/disable 'Temporary' attribute for DIRECTORY."""
    offline: bool = False
    """Enable/disable 'Offline' attribute for DIRECTORY."""
    not_content_indexed: bool = False
    """Enable/disable 'NotContentIndexed' attribute for DIRECTORY."""
    no_scrub_data: bool = False
    """Enable/disable 'NoScrubData' attribute for DIRECTORY."""

    def __init__(
        self, read_only: bool = False,
        hidden: bool = False,
        system: bool = False,
        none: bool = False,
        directory: bool = False,
        archive: bool = False,
        temporary: bool = False,
        offline: bool = False,
        not_content_indexed: bool = False,
        no_scrub_data: bool = False
    ) -> None:
        self.read_only = read_only
        self.hidden = hidden
        self.system = system
        self.none = none
        self.directory = directory
        self.archive = archive
        self.temporary = temporary
        self.offline = offline
        self.not_content_indexed = not_content_indexed
        self.no_scrub_data = no_scrub_data
        self._str = (('ReadOnly|' if self.read_only else '') +
                               ('Hidden|' if self.hidden else '') +
                               ('System|' if self.system else '') +
                               ('None|' if self.none else '') +
                               ('Directory|' if self.directory else '') +
                               ('Archive|' if self.archive else '') +
                               ('Temporary|' if self.temporary else '') +
                               ('Offline|' if self.offline else '') +
                               ('NotContentIndexed|' if self.not_content_indexed else '') +
                               ('NoScrubData|' if self.no_scrub_data else ''))

    def __str__(self):
        concatenated_params = self._str
        return concatenated_params.strip('|')

    @classmethod
    def from_string(cls, string: str) -> Self:
        """Create a NTFSAttributes from a string.

        To specify permissions you can pass in a string with the
        desired permissions, e.g. "ReadOnly|Hidden|System"

        :param str string: The string which dictates the permissions.
        :return: A NTFSAttributes object
        :rtype: ~azure.storage.fileshare.NTFSAttributes
        """
        read_only = "ReadOnly" in string
        hidden = "Hidden" in string
        system = "System" in string
        none = "None" in string
        directory = "Directory" in string
        archive = "Archive" in string
        temporary = "Temporary" in string
        offline = "Offline" in string
        not_content_indexed = "NotContentIndexed" in string
        no_scrub_data = "NoScrubData" in string

        parsed = cls(read_only, hidden, system, none, directory, archive, temporary, offline, not_content_indexed,
                     no_scrub_data)
        parsed._str = string
        return parsed


class DirectoryProperties(DictMixin):
    """Directory's properties class."""

    name: str
    """The name of the directory."""
    last_modified: "datetime"
    """A datetime object representing the last time the directory was modified."""
    etag: str
    """The ETag contains a value that you can use to perform operations conditionally."""
    server_encrypted: bool
    """Whether encryption is enabled."""
    metadata: Dict[str, str]
    """Name_value pairs to associate with the directory as metadata."""
    change_time: Optional[Union[str, "datetime"]] = None
    """Change time for the file."""
    creation_time: Optional[Union[str, "datetime"]] = None
    """Creation time for the file."""
    last_write_time: Optional[Union[str, "datetime"]] = None
    """Last write time for the file."""
    last_access_time: Optional["datetime"] = None
    """Last access time for the file."""
    file_attributes: Union[str, NTFSAttributes]
    """The file system attributes for files and directories."""
    permission_key: str
    """Key of the permission to be set for the directory/file."""
    file_id: str
    """FileId uniquely identifies the file or directory."""
    parent_id: str
    """ParentId uniquely identifies the parent directory of the object."""
    is_directory: bool = True
    """Whether input is a directory."""
    owner: Optional[str] = None
    """NFS only. The owner of the directory."""
    group: Optional[str] = None
    """NFS only. The owning group of the directory."""
    file_mode: Optional[str] = None
    """NFS only. The file mode of the directory."""
    nfs_file_type: Optional[Literal['Directory']] = None
    """NFS only. The type of the directory."""

    def __init__(self, **kwargs: Any) -> None:
        self.name = None  # type: ignore [assignment]
        self.last_modified = kwargs.get('Last-Modified')  # type: ignore [assignment]
        self.etag = kwargs.get('ETag')  # type: ignore [assignment]
        self.server_encrypted = kwargs.get('x-ms-server-encrypted')  # type: ignore [assignment]
        self.metadata = kwargs.get('metadata')  # type: ignore [assignment]
        self.change_time = Deserializer.deserialize_iso(kwargs.get('x-ms-file-change-time')) if (
                kwargs.get('x-ms-file-change-time') is not None) else None
        self.creation_time = Deserializer.deserialize_iso(kwargs.get('x-ms-file-creation-time')) if (
                kwargs.get('x-ms-file-creation-time') is not None) else None
        self.last_write_time = Deserializer.deserialize_iso(kwargs.get('x-ms-file-last-write-time')) if (
                kwargs.get('x-ms-file-last-write-time') is not None) else None
        self.last_access_time = None
        self.file_attributes = kwargs.get('x-ms-file-attributes')  # type: ignore [assignment]
        self.permission_key = kwargs.get('x-ms-file-permission-key')  # type: ignore [assignment]
        self.file_id = kwargs.get('x-ms-file-id')  # type: ignore [assignment]
        self.parent_id = kwargs.get('x-ms-file-parent-id')  # type: ignore [assignment]
        self.is_directory = True
        self.owner = kwargs.get('x-ms-owner')
        self.group = kwargs.get('x-ms-group')
        self.file_mode = kwargs.get('x-ms-mode')
        self.nfs_file_type = kwargs.get('x-ms-file-file-type')

    @classmethod
    def _from_generated(cls, generated):
        props = cls()
        props.name = unquote(generated.name.content) if generated.name.encoded else generated.name.content
        props.file_id = generated.file_id
        props.file_attributes = generated.attributes
        props.last_modified = generated.properties.last_modified
        props.creation_time = generated.properties.creation_time
        props.last_access_time = generated.properties.last_access_time
        props.last_write_time = generated.properties.last_write_time
        props.change_time = generated.properties.change_time
        props.etag = generated.properties.etag
        props.permission_key = generated.permission_key
        return props


class DirectoryPropertiesPaged(PageIterator):
    """An iterable for the contents of a directory.

    This iterable will yield dicts for the contents of the directory. The dicts
    will have the keys 'name' (str) and 'is_directory' (bool).
    Items that are files (is_directory=False) will have an additional 'content_length' key.

    :param Callable command: Function to retrieve the next page of items.
    :param Optional[str] prefix: Filters the results to return only directories whose names
        begin with the specified prefix.
    :param Optional[int] results_per_page: The maximum number of share names to retrieve per call.
    :param Optional[str] continuation_token: An opaque continuation token.
    """

    service_endpoint: Optional[str] = None
    """The service URL."""
    prefix: Optional[str] = None
    """A file name prefix being used to filter the list."""
    marker: Optional[str] = None
    """The continuation token of the current page of results."""
    results_per_page: Optional[int] = None
    """The maximum number of results retrieved per API call."""
    continuation_token: Optional[str] = None
    """The continuation token to retrieve the next page of results."""
    location_mode: Optional[str] = None
    """The location mode being used to list results. The available options include "primary" and "secondary"."""
    current_page: List[Dict[str, Any]]
    """The current page of listed results."""

    def __init__(
        self, command: Callable,
        prefix: Optional[str] = None,
        results_per_page: Optional[int] = None,
        continuation_token: Optional[str] = None
    ) -> None:
        super(DirectoryPropertiesPaged, self).__init__(
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
                prefix=self.prefix,
                maxresults=self.results_per_page,
                cls=return_context_and_deserialized,
                use_location=self.location_mode)
        except HttpResponseError as error:
            process_storage_error(error)

    def _extract_data_cb(self, get_next_return):
        self.location_mode, self._response = get_next_return
        self.service_endpoint = self._response.service_endpoint
        self.marker = self._response.marker
        self.results_per_page = self._response.max_results
        self.current_page = [DirectoryProperties._from_generated(i) for i in self._response.segment.directory_items] # pylint: disable = protected-access
        self.current_page.extend([FileProperties._from_generated(i) for i in self._response.segment.file_items]) # pylint: disable = protected-access
        return self._response.next_marker or None, self.current_page


class CopyProperties(DictMixin):
    """File Copy Properties.

    These properties will be `None` if this file has never been the destination in a Copy
    File operation, or if this file has been modified after a concluded Copy File operation.
    """

    id: str
    """String identifier for the last attempted Copy File operation where this file
        was the destination file. This header does not appear if this file has never
        been the destination in a Copy File operation, or if this file has been
        modified after a concluded Copy File operation."""
    source: Optional[str] = None
    """URL up to 2 KB in length that specifies the source file used in the last attempted
        Copy File operation where this file was the destination file."""
    status: Optional[str] = None
    """State of the copy operation identified by Copy ID, with these values:
            success:
                Copy completed successfully.
            pending:
                Copy is in progress. Check copy_status_description if intermittent,
                non-fatal errors impede copy progress but don't cause failure.
            aborted:
                Copy was ended by Abort Copy File.
            failed:
                Copy failed. See copy_status_description for failure details."""
    progress: Optional[str] = None
    """Contains the number of bytes copied and the total bytes in the source in the last
        attempted Copy File operation where this file was the destination file. Can show
        between 0 and Content-Length bytes copied."""
    status_description: Optional[str] = None
    """Only appears when x-ms-copy-status is failed or pending. Describes cause of fatal
        or non-fatal copy operation failure."""
    incremental_copy: Optional[bool] = None
    """Copies the snapshot of the source file to a destination file.
        The snapshot is copied such that only the differential changes between
        the previously copied snapshot are transferred to the destination."""
    destination_snapshot: Optional["datetime"] = None
    """Included if the file is incremental copy or incremental copy snapshot,
        if x-ms-copy-status is success. Snapshot time of the last successful
        incremental copy snapshot for this file."""
    datetime: Optional["datetime"] = None
    """Conclusion time of the last attempted Copy File operation where this file was the
        destination file. This value can specify the time of a completed, aborted, or
        failed copy attempt."""

    def __init__(self, **kwargs: Any) -> None:
        self.id = kwargs.get('x-ms-copy-id')  # type: ignore [assignment]
        self.source = kwargs.get('x-ms-copy-source')
        self.status = get_enum_value(kwargs.get('x-ms-copy-status'))
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


class FileProperties(DictMixin):
    """File's properties class."""

    name: str
    """The name of the file."""
    path: Optional[str] = None
    """The path of the file."""
    share: Optional[str] = None
    """The name of the share."""
    snapshot: Optional[str] = None
    """File snapshot."""
    content_length: int
    """Size of file in bytes."""
    metadata: Dict[str, str]
    """Name-value pairs to associate with the file as metadata."""
    file_type: str
    """String indicating the type of file."""
    last_modified: "datetime"
    """A datetime object representing the last time the file was modified."""
    etag: str
    """The ETag contains a value that can be used to perform operations conditionally."""
    size: int
    """Size of the file in bytes."""
    content_range: Optional[str] = None
    """Indicates the range of bytes returned in the event that the client
        requested a subset of the file."""
    server_encrypted: bool
    """Whether encryption is enabled."""
    copy: CopyProperties
    """The copy properties."""
    content_settings: ContentSettings
    """The content settings for the file."""
    lease: LeaseProperties
    """File lease properties."""
    change_time: Optional[Union[str, "datetime"]] = None
    """Change time for the file."""
    creation_time: Optional[Union[str, "datetime"]] = None
    """Creation time for the file."""
    last_write_time: Optional[Union[str, "datetime"]] = None
    """Last write time for the file."""
    last_access_time: Optional["datetime"] = None
    """Last access time for the file."""
    file_attributes: Union[str, NTFSAttributes]
    """The file system attributes for files and directories."""
    permission_key: str
    """Key of the permission to be set for the directory/file."""
    file_id: str
    """FileId uniquely identifies the file or directory."""
    parent_id: Optional[str] = None
    """ParentId uniquely identifies the parent directory of the object."""
    is_directory: bool = False
    """Whether input is a directory."""
    owner: Optional[str] = None
    """NFS only. The owner of the file."""
    group: Optional[str] = None
    """NFS only. The owning group of the file."""
    file_mode: Optional[str] = None
    """NFS only. The file mode of the file."""
    link_count: Optional[int] = None
    """NFS only. The number of hard links of the file."""
    nfs_file_type: Optional[Literal['Regular']] = None
    """NFS only. The type of the file."""

    def __init__(self, **kwargs: Any) -> None:
        self.name = kwargs.get('name')  # type: ignore [assignment]
        self.path = None
        self.share = None
        self.snapshot = None
        self.content_length = kwargs.get('Content-Length')  # type: ignore [assignment]
        self.metadata = kwargs.get('metadata')  # type: ignore [assignment]
        self.file_type = kwargs.get('x-ms-type')  # type: ignore [assignment]
        self.last_modified = kwargs.get('Last-Modified')  # type: ignore [assignment]
        self.etag = kwargs.get('ETag')  # type: ignore [assignment]
        self.size = kwargs.get('Content-Length')  # type: ignore [assignment]
        self.content_range = kwargs.get('Content-Range')
        self.server_encrypted = kwargs.get('x-ms-server-encrypted')  # type: ignore [assignment]
        self.copy = CopyProperties(**kwargs)
        self.content_settings = ContentSettings(**kwargs)
        self.lease = LeaseProperties(**kwargs)
        self.change_time = Deserializer.deserialize_iso(kwargs.get('x-ms-file-change-time')) if (
            kwargs.get('x-ms-file-change-time') is not None) else None
        self.creation_time = Deserializer.deserialize_iso(kwargs.get('x-ms-file-creation-time')) if (
            kwargs.get('x-ms-file-creation-time') is not None) else None
        self.last_write_time = Deserializer.deserialize_iso(kwargs.get('x-ms-file-last-write-time')) if (
            kwargs.get('x-ms-file-last-write-time') is not None) else None
        self.last_access_time = None
        self.file_attributes = kwargs.get('x-ms-file-attributes')  # type: ignore [assignment]
        self.permission_key = kwargs.get('x-ms-file-permission-key')  # type: ignore [assignment]
        self.file_id = kwargs.get('x-ms-file-id')  # type: ignore [assignment]
        self.parent_id = kwargs.get('x-ms-file-parent-id')
        self.is_directory = False
        self.owner = kwargs.get('x-ms-owner')
        self.group = kwargs.get('x-ms-group')
        self.file_mode = kwargs.get('x-ms-mode')
        self.link_count = kwargs.get('x-ms-link-count')
        self.nfs_file_type = kwargs.get('x-ms-file-file-type')

    @classmethod
    def _from_generated(cls, generated):
        props = cls()
        props.name = unquote(generated.name.content) if generated.name.encoded else generated.name.content
        props.file_id = generated.file_id
        props.etag = generated.properties.etag
        props.file_attributes = generated.attributes
        props.last_modified = generated.properties.last_modified
        props.creation_time = generated.properties.creation_time
        props.last_access_time = generated.properties.last_access_time
        props.last_write_time = generated.properties.last_write_time
        props.change_time = generated.properties.change_time
        props.size = generated.properties.content_length
        props.permission_key = generated.permission_key
        return props


class ShareProtocols(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Enabled protocols on the share"""
    SMB = "SMB"
    NFS = "NFS"


class FileSasPermissions:
    """FileSasPermissions class to be used with
    generating shared access signature operations.

    :param bool read:
        Read the content, properties, metadata. Use the file as the source of a copy operation.
    :param bool create:
        Create a new file or copy a file to a new file.
    :param bool write:
        Create or write content, properties, metadata. Resize the file. Use the file
        as the destination of a copy operation within the same account.
    :param bool delete:
        Delete the file.
    """

    read: bool = False
    """Read the content, properties, metadata. Use the file as the source of a copy operation."""
    create: bool = False
    """Create a new file or copy a file to a new file."""
    write: bool = False
    """Create or write content, properties, metadata. Resize the file. Use the file
        as the destination of a copy operation within the same account."""
    delete: bool = False
    """Delete the file."""

    def __init__(
        self, read: bool = False,
        create: bool = False,
        write: bool = False,
        delete: bool = False
    ) -> None:
        self.read = read
        self.create = create
        self.write = write
        self.delete = delete
        self._str = (('r' if self.read else '') +
                     ('c' if self.create else '') +
                     ('w' if self.write else '') +
                     ('d' if self.delete else ''))

    def __str__(self):
        return self._str

    @classmethod
    def from_string(cls, permission: str) -> Self:
        """Create a FileSasPermissions from a string.

        To specify read, create, write, or delete permissions you need only to
        include the first letter of the word in the string. E.g. For read and
        create permissions, you would provide a string "rc".

        :param str permission: The string which dictates the read, create,
            write, or delete permissions
        :return: A FileSasPermissions object
        :rtype: ~azure.storage.fileshare.FileSasPermissions
        """
        p_read = 'r' in permission
        p_create = 'c' in permission
        p_write = 'w' in permission
        p_delete = 'd' in permission

        parsed = cls(p_read, p_create, p_write, p_delete)

        return parsed


def service_properties_deserialize(generated: GeneratedStorageServiceProperties) -> Dict[str, Any]:
    return {
        'hour_metrics': Metrics._from_generated(generated.hour_metrics),  # pylint: disable=protected-access
        'minute_metrics': Metrics._from_generated(generated.minute_metrics),  # pylint: disable=protected-access
        'cors': [CorsRule._from_generated(cors) for cors in generated.cors],  # type: ignore [union-attr] # pylint: disable=protected-access
        'protocol': ShareProtocolSettings._from_generated(generated.protocol),  # pylint: disable=protected-access
    }
