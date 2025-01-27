# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=docstring-keyword-should-match-keyword-only

import sys
import warnings
from typing import (
    Any, cast, Dict, Literal, Optional, Union,
    TYPE_CHECKING
)
from typing_extensions import Self

from azure.core.async_paging import AsyncItemPaged
from azure.core.exceptions import HttpResponseError
from azure.core.pipeline import AsyncPipeline
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async
from .._deserialize import deserialize_permission, deserialize_share_properties
from .._generated.aio import AzureFileStorage
from .._generated.models import (
    DeleteSnapshotsOptionType,
    ShareStats,
    SignedIdentifier
)
from .._models import ShareProtocols
from .._parser import _parse_snapshot
from .._share_client_helpers import (
    _create_permission_for_share_options,
    _format_url,
    _from_share_url,
    _parse_url
)
from .._shared.policies_async import ExponentialRetry
from .._shared.base_client import parse_query, StorageAccountHostsMixin
from .._shared.base_client_async import AsyncStorageAccountHostsMixin, AsyncTransportWrapper, parse_connection_str
from .._shared.request_handlers import add_metadata_headers, serialize_iso
from .._shared.response_handlers import (
    process_storage_error,
    return_headers_and_deserialized,
    return_response_headers
)
from .._serialize import get_access_conditions, get_api_version
from ..aio._lease_async import ShareLeaseClient
from ._directory_client_async import ShareDirectoryClient
from ._file_client_async import ShareFileClient

if TYPE_CHECKING:
    from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential
    from azure.core.credentials_async import AsyncTokenCredential
    from .._models import AccessPolicy, DirectoryProperties, FileProperties, ShareProperties


class ShareClient(AsyncStorageAccountHostsMixin, StorageAccountHostsMixin):  # type: ignore [misc]
    """A client to interact with a specific share, although that share may not yet exist.

    For operations relating to a specific directory or file in this share, the clients for
    those entities can also be retrieved using the :func:`get_directory_client` and :func:`get_file_client` functions.

    :param str account_url:
        The URI to the storage account. In order to create a client given the full URI to the share,
        use the :func:`from_share_url` classmethod.
    :param share_name:
        The name of the share with which to interact.
    :type share_name: str
    :param str snapshot:
        An optional share snapshot on which to operate. This can be the snapshot ID string
        or the response returned from :func:`create_snapshot`.
    :param credential:
        The credentials with which to authenticate. This is optional if the
        account URL already has a SAS token. The value can be a SAS token string,
        an instance of a AzureSasCredential or AzureNamedKeyCredential from azure.core.credentials,
        an account shared access key, or an instance of a TokenCredentials class from azure.identity.
        If the resource URI already contains a SAS token, this will be ignored in favor of an explicit credential
        - except in the case of AzureSasCredential, where the conflicting SAS tokens will raise a ValueError.
        If using an instance of AzureNamedKeyCredential, "name" should be the storage account name, and "key"
        should be the storage account key.
    :type credential:
        ~azure.core.credentials.AzureNamedKeyCredential or
        ~azure.core.credentials.AzureSasCredential or
        ~azure.core.credentials_async.AsyncTokenCredential or
        str or dict[str, str] or None
    :keyword token_intent:
        Required when using `AsyncTokenCredential` for authentication and ignored for other forms of authentication.
        Specifies the intent for all requests when using `AsyncTokenCredential` authentication. Possible values are:

        backup - Specifies requests are intended for backup/admin type operations, meaning that all file/directory
                 ACLs are bypassed and full permissions are granted. User must also have required RBAC permission.

    :paramtype token_intent: Literal['backup']
    :keyword bool allow_trailing_dot: If true, the trailing dot will not be trimmed from the target URI.
    :keyword bool allow_source_trailing_dot: If true, the trailing dot will not be trimmed from the source URI.
    :keyword str api_version:
        The Storage API version to use for requests. Default value is the most recent service version that is
        compatible with the current SDK. Setting to an older version may result in reduced feature compatibility.

        .. versionadded:: 12.1.0

    :keyword str secondary_hostname:
        The hostname of the secondary endpoint.
    :keyword int max_range_size: The maximum range size used for a file upload. Defaults to 4*1024*1024.
    """
    def __init__(
        self, account_url: str,
        share_name: str,
        snapshot: Optional[Union[str, Dict[str, Any]]] = None,
        credential: Optional[Union[str, Dict[str, str], "AzureNamedKeyCredential", "AzureSasCredential", "AsyncTokenCredential"]] = None,  # pylint: disable=line-too-long
        *,
        token_intent: Optional[Literal['backup']] = None,
        **kwargs: Any
    ) -> None:
        kwargs['retry_policy'] = kwargs.get('retry_policy') or ExponentialRetry(**kwargs)
        loop = kwargs.pop('loop', None)
        if loop and sys.version_info >= (3, 8):
            warnings.warn("The 'loop' parameter was deprecated from asyncio's high-level"
            "APIs in Python 3.8 and is no longer supported.", DeprecationWarning)
        if hasattr(credential, 'get_token') and not token_intent:
            raise ValueError("'token_intent' keyword is required when 'credential' is an AsyncTokenCredential.")
        parsed_url = _parse_url(account_url, share_name)
        path_snapshot, sas_token = parse_query(parsed_url.query)
        if not sas_token and not credential:
            raise ValueError(
                'You need to provide either an account shared key or SAS token when creating a storage service.')
        self.snapshot = _parse_snapshot(snapshot, path_snapshot)
        self.share_name = share_name
        self._query_str, credential = self._format_query_string(
            sas_token=sas_token, credential=credential, share_snapshot=self.snapshot)
        super(ShareClient, self).__init__(
            parsed_url=parsed_url, service='file-share', credential=credential, **kwargs)
        self.allow_trailing_dot = kwargs.pop('allow_trailing_dot', None)
        self.allow_source_trailing_dot = kwargs.pop('allow_source_trailing_dot', None)
        self.file_request_intent = token_intent
        self._client = AzureFileStorage(url=self.url, base_url=self.url, pipeline=self._pipeline,
                                        allow_trailing_dot=self.allow_trailing_dot,
                                        allow_source_trailing_dot=self.allow_source_trailing_dot,
                                        file_request_intent=self.file_request_intent)
        self._client._config.version = get_api_version(kwargs)  # type: ignore [assignment]

    @classmethod
    def from_share_url(
        cls, share_url: str,
        snapshot: Optional[Union[str, Dict[str, Any]]] = None,
        credential: Optional[Union[str, Dict[str, str], "AzureNamedKeyCredential", "AzureSasCredential", "AsyncTokenCredential"]] = None,  # pylint: disable=line-too-long
        **kwargs: Any
    ) -> Self:
        """
        :param str share_url: The full URI to the share.
        :param snapshot:
            An optional share snapshot on which to operate. This can be the snapshot ID string
            or the response returned from :func:`create_snapshot`.
        :type snapshot: Optional[Union[str, dict[str, Any]]]
        :param credential:
            The credentials with which to authenticate. This is optional if the
            account URL already has a SAS token. The value can be a SAS token string,
            an instance of a AzureSasCredential or AzureNamedKeyCredential from azure.core.credentials,
            an account shared access key, or an instance of a AsyncTokenCredentials class from azure.identity.
            If the resource URI already contains a SAS token, this will be ignored in favor of an explicit credential
            - except in the case of AzureSasCredential, where the conflicting SAS tokens will raise a ValueError.
            If using an instance of AzureNamedKeyCredential, "name" should be the storage account name, and "key"
            should be the storage account key.
        :type credential:
            ~azure.core.credentials.AzureNamedKeyCredential or
            ~azure.core.credentials.AzureSasCredential or
            ~azure.core.credentials_async.AsyncTokenCredential or
            str or dict[str, str] or None
        :returns: A share client.
        :rtype: ~azure.storage.fileshare.aio.ShareClient
        """
        account_url, share_name, path_snapshot = _from_share_url(share_url, snapshot)
        return cls(account_url, share_name, path_snapshot, credential, **kwargs)

    def _format_url(self, hostname: str) -> str:
        """Format the endpoint URL according to the current location mode hostname.

        :param str hostname:
            The hostname of the current location mode.
        :returns: A formatted endpoint URL including current location mode hostname.
        :rtype: str
        """
        return _format_url(self.scheme, hostname, self.share_name, self._query_str)

    @classmethod
    def from_connection_string(
        cls, conn_str: str,
        share_name: str,
        snapshot: Optional[Union[str, Dict[str, Any]]] = None,
        credential: Optional[Union[str, Dict[str, str], "AzureNamedKeyCredential", "AzureSasCredential", "AsyncTokenCredential"]] = None,  # pylint: disable=line-too-long
        **kwargs: Any
    ) -> Self:
        """Create ShareClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Storage account.
        :param str share_name: The name of the share.
        :param snapshot:
            The optional share snapshot on which to operate. This can be the snapshot ID string
            or the response returned from :func:`create_snapshot`.
        :type snapshot: Optional[Union[str, dict[str, Any]]]
        :param credential:
            The credentials with which to authenticate. This is optional if the
            account URL already has a SAS token. The value can be a SAS token string,
            an instance of a AzureSasCredential or AzureNamedKeyCredential from azure.core.credentials,
            an account shared access key, or an instance of a AsyncTokenCredentials class from azure.identity.
            If the resource URI already contains a SAS token, this will be ignored in favor of an explicit credential
            - except in the case of AzureSasCredential, where the conflicting SAS tokens will raise a ValueError.
            If using an instance of AzureNamedKeyCredential, "name" should be the storage account name, and "key"
            should be the storage account key.
        :type credential:
            ~azure.core.credentials.AzureNamedKeyCredential or
            ~azure.core.credentials.AzureSasCredential or
            ~azure.core.credentials_async.AsyncTokenCredential or
            str or dict[str, str] or None
        :returns: A share client.
        :rtype: ~azure.storage.fileshare.aio.ShareClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_share_async.py
                :start-after: [START create_share_client_from_conn_string]
                :end-before: [END create_share_client_from_conn_string]
                :language: python
                :dedent: 8
                :caption: Gets the share client from connection string.
        """
        account_url, secondary, credential = parse_connection_str(conn_str, credential, 'file')
        if 'secondary_hostname' not in kwargs:
            kwargs['secondary_hostname'] = secondary
        return cls(
            account_url, share_name=share_name, snapshot=snapshot, credential=credential, **kwargs)

    def get_directory_client(self, directory_path: Optional[str] = None) -> ShareDirectoryClient:
        """Get a client to interact with the specified directory.
        The directory need not already exist.

        :param str directory_path:
            Path to the specified directory.
        :returns: A Directory Client.
        :rtype: ~azure.storage.fileshare.aio.ShareDirectoryClient
        """
        _pipeline = AsyncPipeline(
            transport=AsyncTransportWrapper(self._pipeline._transport),  # pylint: disable=protected-access
            policies=self._pipeline._impl_policies  # type: ignore [arg-type] # pylint: disable=protected-access
        )

        return ShareDirectoryClient(
            self.url, share_name=self.share_name, directory_path=directory_path or "", snapshot=self.snapshot,
            credential=self.credential, api_version=self.api_version, _hosts=self._hosts, _configuration=self._config,
            _pipeline=_pipeline, _location_mode=self._location_mode, allow_trailing_dot=self.allow_trailing_dot,
            allow_source_trailing_dot=self.allow_source_trailing_dot, token_intent=self.file_request_intent)

    def get_file_client(self, file_path: str) -> ShareFileClient:
        """Get a client to interact with the specified file.
        The file need not already exist.

        :param str file_path:
            Path to the specified file.
        :returns: A File Client.
        :rtype: ~azure.storage.fileshare.aio.ShareFileClient
        """
        _pipeline = AsyncPipeline(
            transport=AsyncTransportWrapper(self._pipeline._transport),  # pylint: disable=protected-access
            policies=self._pipeline._impl_policies  # type: ignore [arg-type] # pylint: disable=protected-access
        )

        return ShareFileClient(
            self.url, share_name=self.share_name, file_path=file_path, snapshot=self.snapshot,
            credential=self.credential, api_version=self.api_version, _hosts=self._hosts, _configuration=self._config,
            _pipeline=_pipeline, _location_mode=self._location_mode, allow_trailing_dot=self.allow_trailing_dot,
            allow_source_trailing_dot=self.allow_source_trailing_dot, token_intent=self.file_request_intent)

    @distributed_trace_async
    async def acquire_lease(self, **kwargs: Any) -> ShareLeaseClient:
        """Requests a new lease.

        If the share does not have an active lease, the Share
        Service creates a lease on the share and returns a new lease.

        .. versionadded:: 12.5.0

        :keyword int lease_duration:
            Specifies the duration of the lease, in seconds, or negative one
            (-1) for a lease that never expires. A non-infinite lease can be
            between 15 and 60 seconds. A lease duration cannot be changed
            using renew or change. Default is -1 (infinite lease).
        :keyword str lease_id:
            Proposed lease ID, in a GUID string format. The Share Service
            returns 400 (Invalid request) if the proposed lease ID is not
            in the correct format.
        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :returns: A ShareLeaseClient object.
        :rtype: ~azure.storage.fileshare.ShareLeaseClient
        """
        kwargs['lease_duration'] = kwargs.pop('lease_duration', -1)
        lease_id = kwargs.pop('lease_id', None)
        lease = ShareLeaseClient(self, lease_id=lease_id)
        await lease.acquire(**kwargs)
        return lease

    @distributed_trace_async
    async def create_share(self, **kwargs: Any) -> Dict[str, Any]:
        """Creates a new Share under the account. If a share with the
        same name already exists, the operation fails.

        :keyword metadata:
            Name-value pairs associated with the share as metadata.
        :paramtype metadata: Optional[dict[str, str]]
        :keyword int quota:
            The quota to be allotted.
        :keyword access_tier:
            Specifies the access tier of the share.
            Possible values: 'TransactionOptimized', 'Hot', 'Cool', 'Premium'
        :paramtype access_tier: str or ~azure.storage.fileshare.models.ShareAccessTier

            .. versionadded:: 12.4.0

        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :keyword protocols:
            Protocols to enable on the share. Only one protocol can be enabled on the share.
        :paramtype protocols: str or ~azure.storage.fileshare.ShareProtocols
        :keyword root_squash:
            Root squash to set on the share.
            Only valid for NFS shares. Possible values include: 'NoRootSquash', 'RootSquash', 'AllSquash'.
        :paramtype root_squash: str or ~azure.storage.fileshare.ShareRootSquash
        :keyword bool paid_bursting_enabled: This property enables paid bursting.
        :keyword int paid_bursting_bandwidth_mibps: The maximum throughput the file share can support in MiB/s.
        :keyword int paid_bursting_iops: The maximum IOPS the file share can support.
        :keyword int provisioned_iops: The provisioned IOPS of the share, stored on the share object.
        :keyword int provisioned_bandwidth_mibps: The provisioned throughput of the share, stored on the share object.
        :returns: Share-updated property dict (Etag and last modified).
        :rtype: dict[str, Any]

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_share_async.py
                :start-after: [START create_share]
                :end-before: [END create_share]
                :language: python
                :dedent: 12
                :caption: Creates a file share.
        """
        metadata = kwargs.pop('metadata', None)
        quota = kwargs.pop('quota', None)
        access_tier = kwargs.pop('access_tier', None)
        timeout = kwargs.pop('timeout', None)
        root_squash = kwargs.pop('root_squash', None)
        protocols = kwargs.pop('protocols', None)
        paid_bursting_bandwidth_mibps = kwargs.pop('paid_bursting_bandwidth_mibps', None)
        paid_bursting_iops = kwargs.pop('paid_bursting_iops', None)
        share_provisioned_iops = kwargs.pop('provisioned_iops', None)
        share_provisioned_bandwidth_mibps = kwargs.pop('provisioned_bandwidth_mibps', None)
        if protocols and protocols not in ['NFS', 'SMB', ShareProtocols.SMB, ShareProtocols.NFS]:
            raise ValueError("The enabled protocol must be set to either SMB or NFS.")
        if root_squash and protocols not in ['NFS', ShareProtocols.NFS]:
            raise ValueError("The 'root_squash' keyword can only be used on NFS enabled shares.")
        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata))

        try:
            return cast(Dict[str, Any], await self._client.share.create(
                timeout=timeout,
                metadata=metadata,
                quota=quota,
                access_tier=access_tier,
                root_squash=root_squash,
                enabled_protocols=protocols,
                paid_bursting_max_bandwidth_mibps=paid_bursting_bandwidth_mibps,
                paid_bursting_max_iops=paid_bursting_iops,
                share_provisioned_iops=share_provisioned_iops,
                share_provisioned_bandwidth_mibps=share_provisioned_bandwidth_mibps,
                cls=return_response_headers,
                headers=headers,
                **kwargs))
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def create_snapshot(self, **kwargs: Any) -> Dict[str, Any]:
        """Creates a snapshot of the share.

        A snapshot is a read-only version of a share that's taken at a point in time.
        It can be read, copied, or deleted, but not modified. Snapshots provide a way
        to back up a share as it appears at a moment in time.

        A snapshot of a share has the same name as the base share from which the snapshot
        is taken, with a DateTime value appended to indicate the time at which the
        snapshot was taken.

        :keyword metadata:
            Name-value pairs associated with the share as metadata.
        :paramtype metadata: Optional[dict[str, str]]
        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :returns: Share-updated property dict (Snapshot ID, Etag, and last modified).
        :rtype: dict[str, Any]

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_share_async.py
                :start-after: [START create_share_snapshot]
                :end-before: [END create_share_snapshot]
                :language: python
                :dedent: 16
                :caption: Creates a snapshot of the file share.
        """
        metadata = kwargs.pop('metadata', None)
        timeout = kwargs.pop('timeout', None)
        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata))
        try:
            return cast(Dict[str, Any], await self._client.share.create_snapshot(
                timeout=timeout,
                cls=return_response_headers,
                headers=headers,
                **kwargs))
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def delete_share(
        self, delete_snapshots: Optional[Union[bool, Literal['include', 'include-leased']]] = False,
        **kwargs: Any
    ) -> None:
        """Marks the specified share for deletion. The share is
        later deleted during garbage collection.

        :param delete_snapshots:
            Indicates if snapshots are to be deleted. If "True" or enum "include", snapshots will
            be deleted (but not include leased). To include leased snapshots, specify the "include-leased"
            enum.
        :type delete_snapshots:
            Optional[Union[bool, Literal['include', 'include-leased']]]
        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :keyword lease:
            Required if the share has an active lease. Value can be a ShareLeaseClient object
            or the lease ID as a string.

            .. versionadded:: 12.5.0

            This keyword argument was introduced in API version '2020-08-04'.

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_share_async.py
                :start-after: [START delete_share]
                :end-before: [END delete_share]
                :language: python
                :dedent: 16
                :caption: Deletes the share and any snapshots.
        """
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        timeout = kwargs.pop('timeout', None)
        delete_include = None
        if isinstance(delete_snapshots, bool) and delete_snapshots:
            delete_include = DeleteSnapshotsOptionType.INCLUDE
        else:
            if delete_snapshots == 'include':
                delete_include = DeleteSnapshotsOptionType.INCLUDE
            elif delete_snapshots == 'include-leased':
                delete_include = DeleteSnapshotsOptionType.INCLUDE_LEASED
        try:
            await self._client.share.delete(
                timeout=timeout,
                sharesnapshot=self.snapshot,
                delete_snapshots=delete_include,
                lease_access_conditions=access_conditions,
                **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def get_share_properties(self, **kwargs: Any) -> "ShareProperties":
        """Returns all user-defined metadata and system properties for the
        specified share. The data returned does not include the shares's
        list of files or directories.

        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :keyword lease:
            Required if the share has an active lease. Value can be a ShareLeaseClient object
            or the lease ID as a string.

            .. versionadded:: 12.5.0

            This keyword argument was introduced in API version '2020-08-04'.

        :returns: The share properties.
        :rtype: ~azure.storage.fileshare.ShareProperties

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_hello_world_async.py
                :start-after: [START get_share_properties]
                :end-before: [END get_share_properties]
                :language: python
                :dedent: 16
                :caption: Gets the share properties.
        """
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        timeout = kwargs.pop('timeout', None)
        try:
            props = cast("ShareProperties", await self._client.share.get_properties(
                timeout=timeout,
                sharesnapshot=self.snapshot,
                cls=deserialize_share_properties,
                lease_access_conditions=access_conditions,
                **kwargs))
        except HttpResponseError as error:
            process_storage_error(error)
        props.name = self.share_name
        props.snapshot = self.snapshot
        return props

    @distributed_trace_async
    async def set_share_quota(self, quota: int, **kwargs: Any) -> Dict[str, Any]:
        """Sets the quota for the share.

        :param int quota:
            Specifies the maximum size of the share, in gigabytes.
            Must be greater than 0, and less than or equal to 5TB.
        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :keyword lease:
            Required if the share has an active lease. Value can be a ShareLeaseClient object
            or the lease ID as a string.

            .. versionadded:: 12.5.0

            This keyword argument was introduced in API version '2020-08-04'.

        :returns: Share-updated property dict (Etag and last modified).
        :rtype: dict[str, Any]

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_share_async.py
                :start-after: [START set_share_quota]
                :end-before: [END set_share_quota]
                :language: python
                :dedent: 16
                :caption: Sets the share quota.
        """
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        timeout = kwargs.pop('timeout', None)
        try:
            return cast(Dict[str, Any], await self._client.share.set_properties(
                timeout=timeout,
                quota=quota,
                access_tier=None,
                cls=return_response_headers,
                lease_access_conditions=access_conditions,
                **kwargs))
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def set_share_properties(self, **kwargs: Any) -> Dict[str, Any]:
        """Sets the share properties.

        .. versionadded:: 12.3.0

        :keyword access_tier:
            Specifies the access tier of the share.
            Possible values: 'TransactionOptimized', 'Hot', 'Cool', 'Premium'
        :paramtype access_tier: str or ~azure.storage.fileshare.models.ShareAccessTier
        :keyword int quota:
            Specifies the maximum size of the share, in gigabytes.
            Must be greater than 0, and less than or equal to 5TB.
        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :keyword root_squash:
            Root squash to set on the share.
            Only valid for NFS shares. Possible values include: 'NoRootSquash', 'RootSquash', 'AllSquash'
        :paramtype root_squash: str or ~azure.storage.fileshare.ShareRootSquash
        :keyword lease:
            Required if the share has an active lease. Value can be a ShareLeaseClient object
            or the lease ID as a string.
        :keyword bool paid_bursting_enabled: This property enables paid bursting.
        :keyword int paid_bursting_bandwidth_mibps: The maximum throughput the file share can support in MiB/s.
        :keyword int paid_bursting_iops: The maximum IOPS the file share can support.
        :keyword int provisioned_iops: The provisioned IOPS of the share, stored on the share object.
        :keyword int provisioned_bandwidth_mibps: The provisioned throughput of the share, stored on the share object.
        :returns: Share-updated property dict (Etag and last modified).
        :rtype: dict[str, Any]

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_share_async.py
                :start-after: [START set_share_properties]
                :end-before: [END set_share_properties]
                :language: python
                :dedent: 16
                :caption: Sets the share properties.
        """
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        timeout = kwargs.pop('timeout', None)
        access_tier = kwargs.pop('access_tier', None)
        quota = kwargs.pop('quota', None)
        root_squash = kwargs.pop('root_squash', None)
        paid_bursting_bandwidth_mibps = kwargs.pop('paid_bursting_bandwidth_mibps', None)
        paid_bursting_iops = kwargs.pop('paid_bursting_iops', None)
        share_provisioned_iops = kwargs.pop('provisioned_iops', None)
        share_provisioned_bandwidth_mibps = kwargs.pop('provisioned_bandwidth_mibps', None)
        if all(parameter is None for parameter in [access_tier, quota, root_squash]):
            raise ValueError("set_share_properties should be called with at least one parameter.")
        try:
            return cast(Dict[str, Any], await self._client.share.set_properties(
                timeout=timeout,
                quota=quota,
                access_tier=access_tier,
                root_squash=root_squash,
                lease_access_conditions=access_conditions,
                paid_bursting_max_bandwidth_mibps=paid_bursting_bandwidth_mibps,
                paid_bursting_max_iops=paid_bursting_iops,
                share_provisioned_iops=share_provisioned_iops,
                share_provisioned_bandwidth_mibps=share_provisioned_bandwidth_mibps,
                cls=return_response_headers,
                **kwargs))
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def set_share_metadata(self, metadata: Dict[str, str], **kwargs: Any) -> Dict[str, Any]:
        """Sets the metadata for the share.

        Each call to this operation replaces all existing metadata
        attached to the share. To remove all metadata from the share,
        call this operation with no metadata dict.

        :param metadata:
            Name-value pairs associated with the share as metadata.
        :type metadata: dict[str, str]
        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :keyword lease:
            Required if the share has an active lease. Value can be a ShareLeaseClient object
            or the lease ID as a string.

            .. versionadded:: 12.5.0

            This keyword argument was introduced in API version '2020-08-04'.

        :returns: Share-updated property dict (Etag and last modified).
        :rtype: dict[str, Any]

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_share_async.py
                :start-after: [START set_share_metadata]
                :end-before: [END set_share_metadata]
                :language: python
                :dedent: 16
                :caption: Sets the share metadata.
        """
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        timeout = kwargs.pop('timeout', None)
        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata))
        try:
            return cast(Dict[str, Any], await self._client.share.set_metadata(
                timeout=timeout,
                cls=return_response_headers,
                headers=headers,
                lease_access_conditions=access_conditions,
                **kwargs))
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def get_share_access_policy(self, **kwargs: Any) -> Dict[str, Any]:
        """Gets the permissions for the share. The permissions
        indicate whether files in a share may be accessed publicly.

        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :keyword lease:
            Required if the share has an active lease. Value can be a ShareLeaseClient object
            or the lease ID as a string.

            .. versionadded:: 12.5.0

            This keyword argument was introduced in API version '2020-08-04'.

        :returns: Access policy information in a dict.
        :rtype: dict[str, Any]
        """
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        timeout = kwargs.pop('timeout', None)
        try:
            response, identifiers = await self._client.share.get_access_policy(
                timeout=timeout,
                cls=return_headers_and_deserialized,
                lease_access_conditions=access_conditions,
                **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)
        return {
            'public_access': response.get('share_public_access'),
            'signed_identifiers': identifiers or []
        }

    @distributed_trace_async
    async def set_share_access_policy(
        self, signed_identifiers: Dict[str, "AccessPolicy"],
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Sets the permissions for the share, or stored access
        policies that may be used with Shared Access Signatures. The permissions
        indicate whether files in a share may be accessed publicly.

        :param signed_identifiers:
            A dictionary of access policies to associate with the share. The
            dictionary may contain up to 5 elements. An empty dictionary
            will clear the access policies set on the service.
        :type signed_identifiers: dict[str, ~azure.storage.fileshare.AccessPolicy]
        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :keyword lease:
            Required if the share has an active lease. Value can be a ShareLeaseClient object
            or the lease ID as a string.

            .. versionadded:: 12.5.0

            This keyword argument was introduced in API version '2020-08-04'.

        :returns: Share-updated property dict (Etag and last modified).
        :rtype: dict[str, Any]
        """
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        timeout = kwargs.pop('timeout', None)
        if len(signed_identifiers) > 5:
            raise ValueError(
                'Too many access policies provided. The server does not support setting '
                'more than 5 access policies on a single resource.')
        identifiers = []
        for key, value in signed_identifiers.items():
            if value:
                value.start = serialize_iso(value.start)
                value.expiry = serialize_iso(value.expiry)
            identifiers.append(SignedIdentifier(id=key, access_policy=value))
        try:
            return cast(Dict[str, Any], await self._client.share.set_access_policy(
                share_acl=identifiers or None,
                timeout=timeout,
                cls=return_response_headers,
                lease_access_conditions=access_conditions,
                **kwargs))
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def get_share_stats(self, **kwargs: Any) -> int:
        """Gets the approximate size of the data stored on the share in bytes.

        Note that this value may not include all recently created
        or recently re-sized files.

        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :keyword lease:
            Required if the share has an active lease. Value can be a ShareLeaseClient object
            or the lease ID as a string.

            .. versionadded:: 12.5.0

            This keyword argument was introduced in API version '2020-08-04'.

        :return: The approximate size of the data (in bytes) stored on the share.
        :rtype: int
        """
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        timeout = kwargs.pop('timeout', None)
        try:
            stats = cast(ShareStats, await self._client.share.get_statistics(
                timeout=timeout,
                lease_access_conditions=access_conditions,
                **kwargs))
            return stats.share_usage_bytes
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace
    def list_directories_and_files(
        self, directory_name: Optional[str] = None,
        name_starts_with: Optional[str] = None,
        marker: Optional[str] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[Union["DirectoryProperties", "FileProperties"]]:
        """Lists the directories and files under the share.

        :param str directory_name:
            Name of a directory.
        :param str name_starts_with:
            Filters the results to return only directories whose names
            begin with the specified prefix.
        :param str marker:
            An opaque continuation token. This value can be retrieved from the
            next_marker field of a previous generator object. If specified,
            this generator will begin returning results from this point.
        :keyword List[str] include:
            Include this parameter to specify one or more datasets to include in the response.
            Possible str values are "timestamps", "Etag", "Attributes", "PermissionKey".

            .. versionadded:: 12.6.0

            This keyword argument was introduced in API version '2020-10-02'.

        :keyword bool include_extended_info:
            If this is set to true, file id will be returned in listed results.

            .. versionadded:: 12.6.0

            This keyword argument was introduced in API version '2020-10-02'.

        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :returns: An auto-paging iterable of dict-like DirectoryProperties and FileProperties
        :rtype: ~azure.core.paging.ItemPaged[Union[DirectoryProperties, FileProperties]]

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_share_async.py
                :start-after: [START share_list_files_in_dir]
                :end-before: [END share_list_files_in_dir]
                :language: python
                :dedent: 16
                :caption: List directories and files in the share.
        """
        timeout = kwargs.pop('timeout', None)
        directory = self.get_directory_client(directory_name)
        return directory.list_directories_and_files(
            name_starts_with=name_starts_with, marker=marker, timeout=timeout, **kwargs)

    @distributed_trace_async
    async def create_permission_for_share(self, file_permission: str, **kwargs: Any) -> Optional[str]:
        """Create a permission (a security descriptor) at the share level.

        This 'permission' can be used for the files/directories in the share.
        If a 'permission' already exists, it shall return the key of it, else
        creates a new permission at the share level and return its key.

        :param str file_permission:
            File permission, a Portable SDDL
        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :keyword file_permission_format:
            Specifies the format in which the permission is returned. If not specified, SDDL will be the default.
        :paramtype file_permission_format: Literal['sddl', 'binary']
        :returns: A file permission key
        :rtype: str or None
        """
        timeout = kwargs.pop('timeout', None)
        options = _create_permission_for_share_options(file_permission, timeout=timeout, **kwargs)
        try:
            return cast(Optional[str], await self._client.share.create_permission(**options))
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def get_permission_for_share(self, permission_key: str, **kwargs: Any) -> str:
        """Get a permission (a security descriptor) for a given key.

        This 'permission' can be used for the files/directories in the share.

        :param str permission_key:
            Key of the file permission to retrieve
        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :keyword file_permission_format:
            Specifies the format in which the permission is returned. If not specified, SDDL will be the default.
        :paramtype file_permission_format: Literal['sddl', 'binary']
        :returns: A file permission (a portable SDDL)
        :rtype: str
        """
        timeout = kwargs.pop('timeout', None)
        try:
            return cast(str, await self._client.share.get_permission(
                file_permission_key=permission_key,
                cls=deserialize_permission,
                timeout=timeout,
                **kwargs))
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def create_directory(self, directory_name: str, **kwargs: Any) -> ShareDirectoryClient:
        """Creates a directory in the share and returns a client to interact
        with the directory.

        :param str directory_name:
            The name of the directory.
        :keyword metadata:
            Name-value pairs associated with the directory as metadata.
        :paramtype metadata: Optional[dict[str, str]]
        :keyword str owner:
            NFS only. The owner of the directory.
        :keyword str group:
            NFS only. The owning group of the directory.
        :keyword str file_mode:
            NFS only. The file mode of the directory.
        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :returns: ShareDirectoryClient
        :rtype: ~azure.storage.fileshare.aio.ShareDirectoryClient
        """
        directory = self.get_directory_client(directory_name)
        kwargs.setdefault('merge_span', True)
        await directory.create_directory(**kwargs)
        return directory

    @distributed_trace_async
    async def delete_directory(self, directory_name: str, **kwargs: Any) -> None:
        """Marks the directory for deletion. The directory is
        later deleted during garbage collection.

        :param str directory_name:
            The name of the directory.
        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :rtype: None
        """
        directory = self.get_directory_client(directory_name)
        await directory.delete_directory(**kwargs)
