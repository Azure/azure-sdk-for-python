# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=docstring-keyword-should-match-keyword-only

import sys
import functools
from typing import (
    Union, Optional, Any, Dict, List,
    TYPE_CHECKING
)
from typing_extensions import Self

from azure.core.exceptions import HttpResponseError
from azure.core.paging import ItemPaged
from azure.core.pipeline import Pipeline
from azure.core.tracing.decorator import distributed_trace
from ._generated import AzureFileStorage
from ._generated.models import KeyInfo, StorageServiceProperties
from ._models import (
    CorsRule,
    ShareProperties,
    SharePropertiesPaged,
    service_properties_deserialize,
)
from ._serialize import get_api_version
from ._share_client import ShareClient
from ._share_service_client_helpers import _parse_url
from ._shared.base_client import StorageAccountHostsMixin, TransportWrapper, parse_connection_str, parse_query
from ._shared.parser import _to_utc_datetime
from ._shared.response_handlers import parse_to_internal_user_delegation_key, process_storage_error

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

if TYPE_CHECKING:
    from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential, TokenCredential
    from datetime import datetime
    from ._models import Metrics, ShareProtocolSettings
    from ._shared.models import UserDelegationKey


class ShareServiceClient(StorageAccountHostsMixin):
    """A client to interact with the File Share Service at the account level.

    This client provides operations to retrieve and configure the account properties
    as well as list, create and delete shares within the account.
    For operations relating to a specific share, a client for that entity
    can also be retrieved using the :func:`get_share_client` function.

    For more optional configuration, please click
    `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
    #optional-configuration>`__.

    :param str account_url:
        The URL to the file share storage account. Any other entities included
        in the URL path (e.g. share or file) will be discarded. This URL can be optionally
        authenticated with a SAS token.
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
        ~azure.core.credentials.TokenCredential or
        str or dict[str, str] or None
    :keyword token_intent:
        Required when using `TokenCredential` for authentication and ignored for other forms of authentication.
        Specifies the intent for all requests when using `TokenCredential` authentication. Possible values are:

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

    .. admonition:: Example:

        .. literalinclude:: ../samples/file_samples_authentication.py
            :start-after: [START create_share_service_client]
            :end-before: [END create_share_service_client]
            :language: python
            :dedent: 8
            :caption: Create the share service client with url and credential.
    """
    def __init__(
        self, account_url: str,
        credential: Optional[Union[str, Dict[str, str], "AzureNamedKeyCredential", "AzureSasCredential", "TokenCredential"]] = None,  # pylint: disable=line-too-long
        *,
        token_intent: Optional[Literal['backup']] = None,
        **kwargs: Any
    ) -> None:
        if hasattr(credential, 'get_token') and not token_intent:
            raise ValueError("'token_intent' keyword is required when 'credential' is an TokenCredential.")
        parsed_url = _parse_url(account_url=account_url)
        _, sas_token = parse_query(parsed_url.query)
        if not sas_token and not credential:
            raise ValueError(
                'You need to provide either an account shared key or SAS token when creating a storage service.')

        self._query_str, credential = self._format_query_string(sas_token, credential)
        super(ShareServiceClient, self).__init__(
            parsed_url, service='file-share', credential=credential, **kwargs)
        self.allow_trailing_dot = kwargs.pop('allow_trailing_dot', None)
        self.allow_source_trailing_dot = kwargs.pop('allow_source_trailing_dot', None)
        self.file_request_intent = token_intent
        self._client = AzureFileStorage(url=self.url, base_url=self.url, pipeline=self._pipeline,
                                        allow_trailing_dot=self.allow_trailing_dot,
                                        allow_source_trailing_dot=self.allow_source_trailing_dot,
                                        file_request_intent=self.file_request_intent)
        self._client._config.version = get_api_version(kwargs)  # type: ignore [assignment]

    def __enter__(self) -> Self:
        self._client.__enter__()
        return self

    def __exit__(self, *args) -> None:
        self._client.__exit__(*args)

    def close(self) -> None:
        """This method is to close the sockets opened by the client.
        It need not be used when using with a context manager.

        :return: None
        :rtype: None
        """
        self._client.close()

    def _format_url(self, hostname: str) -> str:
        """Format the endpoint URL according to the current location mode hostname.

        :param str hostname:
            The hostname of the current location mode.
        :returns: A formatted endpoint URL including current location mode hostname.
        :rtype: str
        """
        return f"{self.scheme}://{hostname}/{self._query_str}"

    @classmethod
    def from_connection_string(
        cls, conn_str: str,
        credential: Optional[Union[str, Dict[str, str], "AzureNamedKeyCredential", "AzureSasCredential", "TokenCredential"]] = None,  # pylint: disable=line-too-long
        **kwargs: Any
    ) -> Self:
        """Create ShareServiceClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Storage account.
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
            ~azure.core.credentials.TokenCredential or
            str or dict[str, str] or None
        :returns: A File Share service client.
        :rtype: ~azure.storage.fileshare.ShareServiceClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_authentication.py
                :start-after: [START create_share_service_client_from_conn_string]
                :end-before: [END create_share_service_client_from_conn_string]
                :language: python
                :dedent: 8
                :caption: Create the share service client with connection string.
        """
        account_url, secondary, credential = parse_connection_str(conn_str, credential, 'file')
        if 'secondary_hostname' not in kwargs:
            kwargs['secondary_hostname'] = secondary
        return cls(account_url, credential=credential, **kwargs)

    @distributed_trace
    def get_user_delegation_key(
        self,
        *,
        expiry: "datetime",
        start: Optional["datetime"] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> "UserDelegationKey":
        """
        Obtain a user delegation key for the purpose of signing SAS tokens.

        A token credential must be present on the service object for this request to succeed.

        :keyword expiry:
            A DateTime value. Indicates when the key stops being valid.
        :paramtype expiry: ~datetime.datetime
        :keyword start:
            A DateTime value. Indicates when the key becomes valid.
        :paramtype start: Optional[~datetime.datetime]
        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-blob-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-blob
            #other-client--per-operation-configuration>`__.
        :return: The user delegation key.
        :rtype: ~azure.storage.fileshare.UserDelegationKey
        """
        key_info = KeyInfo(start=_to_utc_datetime(start), expiry=_to_utc_datetime(expiry))
        try:
            user_delegation_key = self._client.service.get_user_delegation_key(  # type: ignore
                key_info=key_info,
                timeout=timeout,
                **kwargs
            )
        except HttpResponseError as error:
            process_storage_error(error)
        return parse_to_internal_user_delegation_key(user_delegation_key)  # type: ignore

    @distributed_trace
    def get_service_properties(self, **kwargs: Any) -> Dict[str, Any]:
        """Gets the properties of a storage account's File Share service, including
        Azure Storage Analytics.

        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :returns: A dictionary containing file service properties such as
            analytics logging, hour/minute metrics, cors rules, etc.
        :rtype: Dict[str, Any]

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_service.py
                :start-after: [START get_service_properties]
                :end-before: [END get_service_properties]
                :language: python
                :dedent: 8
                :caption: Get file share service properties.
        """
        timeout = kwargs.pop('timeout', None)
        try:
            service_props = self._client.service.get_properties(timeout=timeout, **kwargs)
            return service_properties_deserialize(service_props)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace
    def set_service_properties(
        self, hour_metrics: Optional["Metrics"] = None,
        minute_metrics: Optional["Metrics"] = None,
        cors: Optional[List[CorsRule]] = None,
        protocol: Optional["ShareProtocolSettings"] = None,
        **kwargs: Any
    ) -> None:
        """Sets the properties of a storage account's File Share service, including
        Azure Storage Analytics. If an element (e.g. hour_metrics) is left as None, the
        existing settings on the service for that functionality are preserved.

        :param hour_metrics:
            The hour metrics settings provide a summary of request
            statistics grouped by API in hourly aggregates for files.
        :type hour_metrics: ~azure.storage.fileshare.Metrics
        :param minute_metrics:
            The minute metrics settings provide request statistics
            for each minute for files.
        :type minute_metrics: ~azure.storage.fileshare.Metrics
        :param cors:
            You can include up to five CorsRule elements in the
            list. If an empty list is specified, all CORS rules will be deleted,
            and CORS will be disabled for the service.
        :type cors: list[~azure.storage.fileshare.CorsRule]
        :param protocol:
            Sets protocol settings
        :type protocol: ~azure.storage.fileshare.ShareProtocolSettings
        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :rtype: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_service.py
                :start-after: [START set_service_properties]
                :end-before: [END set_service_properties]
                :language: python
                :dedent: 8
                :caption: Sets file share service properties.
        """
        timeout = kwargs.pop('timeout', None)
        props = StorageServiceProperties(
            hour_metrics=hour_metrics,
            minute_metrics=minute_metrics,
            cors=CorsRule._to_generated(cors),  # pylint: disable=protected-access
            protocol=protocol
        )
        try:
            self._client.service.set_properties(storage_service_properties=props, timeout=timeout, **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace
    def list_shares(
        self, name_starts_with: Optional[str] = None,
        include_metadata: Optional[bool] = False,
        include_snapshots: Optional[bool] = False,
        **kwargs: Any
    ) -> ItemPaged[ShareProperties]:
        """Returns auto-paging iterable of dict-like ShareProperties under the specified account.
        The generator will lazily follow the continuation tokens returned by
        the service and stop when all shares have been returned.

        :param str name_starts_with:
            Filters the results to return only shares whose names
            begin with the specified name_starts_with.
        :param bool include_metadata:
            Specifies that share metadata be returned in the response.
        :param bool include_snapshots:
            Specifies that share snapshot be returned in the response.
        :keyword bool include_deleted:
            Specifies that deleted shares be returned in the response.
            This is only for share soft delete enabled account.
        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :returns: An iterable (auto-paging) of ShareProperties.
        :rtype: ~azure.core.paging.ItemPaged[~azure.storage.fileshare.ShareProperties]

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_service.py
                :start-after: [START fsc_list_shares]
                :end-before: [END fsc_list_shares]
                :language: python
                :dedent: 12
                :caption: List shares in the file share service.
        """
        timeout = kwargs.pop('timeout', None)
        include = []
        include_deleted = kwargs.pop('include_deleted', None)
        if include_deleted:
            include.append("deleted")
        if include_metadata:
            include.append('metadata')
        if include_snapshots:
            include.append('snapshots')

        results_per_page = kwargs.pop('results_per_page', None)
        command = functools.partial(
            self._client.service.list_shares_segment,
            include=include,
            timeout=timeout,
            **kwargs)
        return ItemPaged(
            command, prefix=name_starts_with, results_per_page=results_per_page,
            page_iterator_class=SharePropertiesPaged)

    @distributed_trace
    def create_share(self, share_name: str, **kwargs: Any) -> ShareClient:
        """Creates a new share under the specified account. If the share
        with the same name already exists, the operation fails. Returns a client with
        which to interact with the newly created share.

        :param str share_name: The name of the share to create.
        :keyword dict[str, str] metadata:
            A dict with name_value pairs to associate with the
            share as metadata. Example:{'Category':'test'}
        :keyword int quota:
            Quota in bytes.
        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :keyword int provisioned_iops: The provisioned IOPS of the share, stored on the share object.
        :keyword int provisioned_bandwidth_mibps: The provisioned throughput of the share, stored on the share object.
        :return: A ShareClient for the newly created Share.
        :rtype: ~azure.storage.fileshare.ShareClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_service.py
                :start-after: [START fsc_create_shares]
                :end-before: [END fsc_create_shares]
                :language: python
                :dedent: 8
                :caption: Create a share in the file share service.
        """
        metadata = kwargs.pop('metadata', None)
        quota = kwargs.pop('quota', None)
        timeout = kwargs.pop('timeout', None)
        provisioned_iops = kwargs.pop('provisioned_iops', None)
        provisioned_bandwidth_mibps = kwargs.pop('provisioned_bandwidth_mibps', None)
        share = self.get_share_client(share_name)
        kwargs.setdefault('merge_span', True)
        share.create_share(
            metadata=metadata,
            quota=quota,
            timeout=timeout,
            provisioned_iops=provisioned_iops,
            provisioned_bandwidth_mibps=provisioned_bandwidth_mibps,
            **kwargs
        )
        return share

    @distributed_trace
    def delete_share(
        self, share_name: Union[ShareProperties, str],
        delete_snapshots: Optional[bool] = False,
        **kwargs: Any
    ) -> None:
        """Marks the specified share for deletion. The share is
        later deleted during garbage collection.

        :param share_name:
            The share to delete. This can either be the name of the share,
            or an instance of ShareProperties.
        :type share_name: str or ~azure.storage.fileshare.ShareProperties
        :param bool delete_snapshots:
            Indicates if snapshots are to be deleted.
        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :rtype: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_service.py
                :start-after: [START fsc_delete_shares]
                :end-before: [END fsc_delete_shares]
                :language: python
                :dedent: 12
                :caption: Delete a share in the file share service.
        """
        timeout = kwargs.pop('timeout', None)
        share = self.get_share_client(share_name)
        kwargs.setdefault('merge_span', True)
        share.delete_share(
            delete_snapshots=delete_snapshots, timeout=timeout, **kwargs)

    @distributed_trace
    def undelete_share(self, deleted_share_name: str, deleted_share_version: str, **kwargs: Any) -> ShareClient:
        """Restores soft-deleted share.

        Operation will only be successful if used within the specified number of days
        set in the delete retention policy.

        .. versionadded:: 12.2.0

            This operation was introduced in API version '2019-12-12'.

        :param str deleted_share_name:
            Specifies the name of the deleted share to restore.
        :param str deleted_share_version:
            Specifies the version of the deleted share to restore.
        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :return: A ShareClient for the undeleted Share.
        :rtype: ~azure.storage.fileshare.ShareClient
        """
        share = self.get_share_client(deleted_share_name)

        try:
            share._client.share.restore(deleted_share_name=deleted_share_name,  # pylint: disable=protected-access
                                        deleted_share_version=deleted_share_version,
                                        timeout=kwargs.pop('timeout', None), **kwargs)
            return share
        except HttpResponseError as error:
            process_storage_error(error)

    def get_share_client(
        self, share: Union[ShareProperties, str],
        snapshot: Optional[Union[Dict[str, Any], str]] = None
    ) -> ShareClient:
        """Get a client to interact with the specified share.
        The share need not already exist.

        :param share:
            The share. This can either be the name of the share,
            or an instance of ShareProperties.
        :type share: str or ~azure.storage.fileshare.ShareProperties
        :param str snapshot:
            An optional share snapshot on which to operate. This can be the snapshot ID string
            or the response returned from :func:`create_snapshot`.
        :returns: A ShareClient.
        :rtype: ~azure.storage.fileshare.ShareClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_service.py
                :start-after: [START get_share_client]
                :end-before: [END get_share_client]
                :language: python
                :dedent: 8
                :caption: Gets the share client.
        """
        if isinstance(share, ShareProperties):
            share_name = share.name
        else:
            share_name = share

        _pipeline = Pipeline(
            transport=TransportWrapper(self._pipeline._transport), # pylint: disable=protected-access
            policies=self._pipeline._impl_policies # pylint: disable=protected-access
        )
        return ShareClient(
            self.url, share_name=share_name, snapshot=snapshot, credential=self.credential,
            api_version=self.api_version, _hosts=self._hosts,
            _configuration=self._config, _pipeline=_pipeline, _location_mode=self._location_mode,
            allow_trailing_dot=self.allow_trailing_dot, allow_source_trailing_dot=self.allow_source_trailing_dot,
            token_intent=self.file_request_intent)
