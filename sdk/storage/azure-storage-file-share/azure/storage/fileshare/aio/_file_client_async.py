# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-many-lines, too-many-public-methods, docstring-keyword-should-match-keyword-only

import functools
import sys
import time
import warnings
from datetime import datetime
from io import BytesIO
from typing import (
    Any, AnyStr, AsyncGenerator, AsyncIterable, Callable, cast,
    Dict, IO, Iterable, List, Optional, Tuple, Union,
    TYPE_CHECKING
)
from typing_extensions import Self

from azure.core.async_paging import AsyncItemPaged
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async
from .._deserialize import deserialize_file_properties, deserialize_file_stream, get_file_ranges_result
from .._file_client_helpers import (
    _format_url,
    _from_file_url,
    _get_ranges_options,
    _parse_url,
    _upload_range_from_url_options
)
from .._generated.aio import AzureFileStorage
from .._generated.models import FileHTTPHeaders
from .._parser import _datetime_to_str, _get_file_permission, _parse_snapshot
from .._serialize import (
    get_access_conditions,
    get_api_version,
    get_dest_access_conditions,
    get_rename_smb_properties,
    get_smb_properties,
    get_source_access_conditions
)
from .._shared.base_client import StorageAccountHostsMixin, parse_query
from .._shared.base_client_async import AsyncStorageAccountHostsMixin, parse_connection_str
from .._shared.policies_async import ExponentialRetry
from .._shared.request_handlers import add_metadata_headers, get_length
from .._shared.response_handlers import process_storage_error, return_response_headers
from .._shared.uploads_async import AsyncIterStreamer, FileChunkUploader, IterStreamer, upload_data_chunks
from ._download_async import StorageStreamDownloader
from ._lease_async import ShareLeaseClient
from ._models import FileProperties, Handle, HandlesPaged

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

if TYPE_CHECKING:
    from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential
    from azure.core.credentials_async import AsyncTokenCredential
    from .._models import ContentSettings, NTFSAttributes
    from .._shared.base_client import StorageConfiguration


async def _upload_file_helper(
    client: "ShareFileClient",
    stream: Any,
    size: Optional[int],
    metadata: Optional[Dict[str, str]],
    content_settings: Optional["ContentSettings"],
    validate_content: bool,
    timeout: Optional[int],
    max_concurrency: int,
    file_settings: "StorageConfiguration",
    file_attributes: Optional[Union[str, "NTFSAttributes"]] = None,
    file_creation_time: Optional[Union[str, datetime]] = None,
    file_last_write_time: Optional[Union[str, datetime]] = None,
    file_permission: Optional[str] = None,
    file_permission_key: Optional[str] = None,
    progress_hook: Optional[Callable[[int, Optional[int]], None]] = None,
    **kwargs: Any
) -> Dict[str, Any]:
    try:
        if size is None or size < 0:
            raise ValueError("A content size must be specified for a File.")
        response = await client.create_file(
            size, content_settings=content_settings, metadata=metadata,
            file_attributes=file_attributes,
            file_creation_time=file_creation_time,
            file_last_write_time=file_last_write_time,
            file_permission=file_permission,
            permission_key=file_permission_key,
            timeout=timeout,
            **kwargs
        )
        if size == 0:
            return response

        responses = await upload_data_chunks(
            service=client,
            uploader_class=FileChunkUploader,
            total_size=size,
            chunk_size=file_settings.max_range_size,
            stream=stream,
            max_concurrency=max_concurrency,
            validate_content=validate_content,
            progress_hook=progress_hook,
            timeout=timeout,
            **kwargs
        )
        return cast(Dict[str, Any], sorted(responses, key=lambda r: r.get('last_modified'))[-1])
    except HttpResponseError as error:
        process_storage_error(error)


class ShareFileClient(AsyncStorageAccountHostsMixin, StorageAccountHostsMixin):  # type: ignore [misc]
    """A client to interact with a specific file, although that file may not yet exist.

    :param str account_url:
        The URI to the storage account. In order to create a client given the full URI to the
        file, use the :func:`from_file_url` classmethod.
    :param share_name:
        The name of the share for the file.
    :type share_name: str
    :param str file_path:
        The file path to the file with which to interact. If specified, this value will override
        a file value specified in the file URL.
    :param str snapshot:
        An optional file snapshot on which to operate. This can be the snapshot ID string
        or the response returned from :func:`ShareClient.create_snapshot`.
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
    :keyword str audience: The audience to use when requesting tokens for Azure Active Directory
        authentication. Only has an effect when credential is of type AsyncTokenCredential. The value could be
        https://storage.azure.com/ (default) or https://<account>.blob.core.windows.net.
    """
    def __init__(
        self, account_url: str,
        share_name: str,
        file_path: str,
        snapshot: Optional[Union[str, Dict[str, Any]]] = None,
        credential: Optional[Union[str, Dict[str, str], "AzureNamedKeyCredential", "AzureSasCredential", "AsyncTokenCredential"]] = None,  # pylint: disable=line-too-long
        *,
        token_intent: Optional[Literal['backup']] = None,
        **kwargs: Any
    ) -> None:
        kwargs["retry_policy"] = kwargs.get("retry_policy") or ExponentialRetry(**kwargs)
        loop = kwargs.pop('loop', None)
        if loop and sys.version_info >= (3, 8):
            warnings.warn("The 'loop' parameter was deprecated from asyncio's high-level"
                          "APIs in Python 3.8 and is no longer supported.", DeprecationWarning)
        if hasattr(credential, 'get_token') and not token_intent:
            raise ValueError("'token_intent' keyword is required when 'credential' is an AsyncTokenCredential.")
        parsed_url = _parse_url(account_url, share_name, file_path)
        path_snapshot, sas_token = parse_query(parsed_url.query)
        if not sas_token and not credential:
            raise ValueError(
                'You need to provide either an account shared key or SAS token when creating a storage service.')
        self.snapshot = _parse_snapshot(snapshot, path_snapshot)
        self.share_name = share_name
        self.file_path = file_path.split('/')
        self.file_name = self.file_path[-1]
        self.directory_path = "/".join(self.file_path[:-1])

        self._query_str, credential = self._format_query_string(
            sas_token, credential, share_snapshot=self.snapshot)
        super(ShareFileClient, self).__init__(
            parsed_url, service='file-share', credential=credential, **kwargs)
        self.allow_trailing_dot = kwargs.pop('allow_trailing_dot', None)
        self.allow_source_trailing_dot = kwargs.pop('allow_source_trailing_dot', None)
        self.file_request_intent = token_intent
        self._client = AzureFileStorage(url=self.url, base_url=self.url, pipeline=self._pipeline,
                                        allow_trailing_dot=self.allow_trailing_dot,
                                        allow_source_trailing_dot=self.allow_source_trailing_dot,
                                        file_request_intent=self.file_request_intent)
        self._client._config.version = get_api_version(kwargs)  # type: ignore [assignment]

    async def __aenter__(self) -> Self:
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args) -> None:
        await self._client.__aexit__(*args)

    async def close(self) -> None:
        """This method is to close the sockets opened by the client.
        It need not be used when using with a context manager.

        :return: None
        :rtype: None
        """
        await self._client.close()

    @classmethod
    def from_file_url(
        cls, file_url: str,
        snapshot: Optional[Union[str, Dict[str, Any]]] = None,
        credential: Optional[Union[str, Dict[str, str], "AzureNamedKeyCredential", "AzureSasCredential", "AsyncTokenCredential"]] = None,  # pylint: disable=line-too-long
        **kwargs: Any
    ) -> Self:
        """A client to interact with a specific file, although that file may not yet exist.

        :param str file_url: The full URI to the file.
        :param str snapshot:
            An optional file snapshot on which to operate. This can be the snapshot ID string
            or the response returned from :func:`ShareClient.create_snapshot`.
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
        :keyword str audience: The audience to use when requesting tokens for Azure Active Directory
            authentication. Only has an effect when credential is of type AsyncTokenCredential. The value could be
            https://storage.azure.com/ (default) or https://<account>.file.core.windows.net.
        :returns: A File client.
        :rtype: ~azure.storage.fileshare.ShareFileClient
        """
        account_url, share_name, file_path, snapshot = _from_file_url(file_url, snapshot)
        return cls(account_url, share_name, file_path, snapshot, credential, **kwargs)

    def _format_url(self, hostname: str):
        return _format_url(self.scheme, hostname, self.share_name, self.file_path, self._query_str)

    @classmethod
    def from_connection_string(
        cls, conn_str: str,
        share_name: str,
        file_path: str,
        snapshot: Optional[Union[str, Dict[str, Any]]] = None,
        credential: Optional[Union[str, Dict[str, str], "AzureNamedKeyCredential", "AzureSasCredential", "AsyncTokenCredential"]] = None,  # pylint: disable=line-too-long
        **kwargs: Any
    ) -> Self:
        """Create ShareFileClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Storage account.
        :param share_name: The name of the share.
        :type share_name: str
        :param str file_path:
            The file path.
        :param str snapshot:
            An optional file snapshot on which to operate. This can be the snapshot ID string
            or the response returned from :func:`ShareClient.create_snapshot`.
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
        :keyword str audience: The audience to use when requesting tokens for Azure Active Directory
            authentication. Only has an effect when credential is of type AsyncTokenCredential. The value could be
            https://storage.azure.com/ (default) or https://<account>.file.core.windows.net.
        :returns: A File client.
        :rtype: ~azure.storage.fileshare.ShareFileClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_hello_world_async.py
                :start-after: [START create_file_client]
                :end-before: [END create_file_client]
                :language: python
                :dedent: 12
                :caption: Creates the file client with connection string.
        """
        account_url, secondary, credential = parse_connection_str(conn_str, credential, 'file')
        if 'secondary_hostname' not in kwargs:
            kwargs['secondary_hostname'] = secondary
        return cls(
            account_url, share_name=share_name, file_path=file_path, snapshot=snapshot, credential=credential, **kwargs)

    @distributed_trace_async
    async def acquire_lease(self, lease_id: Optional[str] = None, **kwargs: Any) -> ShareLeaseClient:
        """Requests a new lease.

        If the file does not have an active lease, the File
        Service creates a lease on the blob and returns a new lease.

        :param str lease_id:
            Proposed lease ID, in a GUID string format. The File Service
            returns 400 (Invalid request) if the proposed lease ID is not
            in the correct format.
        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :returns: A ShareLeaseClient object.
        :rtype: ~azure.storage.fileshare.aio.ShareLeaseClient
        """
        kwargs['lease_duration'] = -1
        lease = ShareLeaseClient(self, lease_id=lease_id)
        await lease.acquire(**kwargs)
        return lease

    @distributed_trace_async
    async def exists(self, **kwargs: Any) -> bool:
        """
        Returns True if the file exists and returns False otherwise.

        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :returns: True if the file exists, False otherwise.
        :rtype: bool
        """
        try:
            await self._client.file.get_properties(**kwargs)
            return True
        except HttpResponseError as error:
            try:
                process_storage_error(error)
            except ResourceNotFoundError:
                return False

    @distributed_trace_async
    async def create_file(
        self, size: int,
        file_attributes: Optional[Union[str, "NTFSAttributes"]] = None,
        file_creation_time: Optional[Union[str, datetime]] = None,
        file_last_write_time: Optional[Union[str, datetime]] = None,
        file_permission: Optional[str] = None,
        permission_key: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Creates a new file.

        Note that it only initializes the file with no content.

        :param int size: Specifies the maximum size for the file,
            up to 1 TB.
        :param file_attributes:
            The file system attributes for files and directories.
            If not set, the default value would be "None" and the attributes will be set to "Archive".
            Here is an example for when the var type is str: 'Temporary|Archive'.
            file_attributes value is not case sensitive.
        :type file_attributes: str or ~azure.storage.fileshare.NTFSAttributes or None
        :param file_creation_time: Creation time for the file
        :type file_creation_time: str or ~datetime.datetime or None
        :param file_last_write_time: Last write time for the file
        :type file_last_write_time: str or ~datetime.datetime or None
        :param file_permission: If specified the permission (security
            descriptor) shall be set for the directory/file. This header can be
            used if Permission size is <= 8KB, else x-ms-file-permission-key
            header shall be used. Default value: Inherit. If SDDL is specified as
            input, it must have owner, group and dacl. Note: Only one of the
            x-ms-file-permission or x-ms-file-permission-key should be specified.
        :type file_permission: str
        :param permission_key: Key of the permission to be set for the
            directory/file. Note: Only one of the x-ms-file-permission or
            x-ms-file-permission-key should be specified.
        :type permission_key: str
        :keyword file_permission_format:
            Specifies the format in which the permission is returned. If not specified, SDDL will be the default.
        :paramtype file_permission_format: Literal['sddl', 'binary']
        :keyword file_change_time:
            Change time for the file. If not specified, change time will be set to the current date/time.

            .. versionadded:: 12.8.0

                This parameter was introduced in API version '2021-06-08'.

        :paramtype file_change_time: str or ~datetime.datetime
        :keyword ~azure.storage.fileshare.ContentSettings content_settings:
            ContentSettings object used to set file properties. Used to set content type, encoding,
            language, disposition, md5, and cache control.
        :keyword metadata:
            Name-value pairs associated with the file as metadata.
        :paramtype metadata: Optional[dict[str, str]]
        :keyword lease:
            Required if the file has an active lease. Value can be a ShareLeaseClient object
            or the lease ID as a string.

            .. versionadded:: 12.1.0

        :paramtype lease: ~azure.storage.fileshare.aio.ShareLeaseClient or str
        :keyword str owner:
            NFS only. The owner of the file.
        :keyword str group:
            NFS only. The owning group of the file.
        :keyword str file_mode:
            NFS only. The file mode of the file.
        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :returns: File-updated property dict (Etag and last modified).
        :rtype: dict[str, Any]

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_client_async.py
                :start-after: [START create_file]
                :end-before: [END create_file]
                :language: python
                :dedent: 16
                :caption: Create a file.
        """
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        content_settings = kwargs.pop('content_settings', None)
        metadata = kwargs.pop('metadata', None)
        timeout = kwargs.pop('timeout', None)
        headers = kwargs.pop("headers", {})
        headers.update(add_metadata_headers(metadata))
        data = kwargs.pop('data', None)
        file_http_headers = None
        if content_settings:
            file_http_headers = FileHTTPHeaders(
                file_cache_control=content_settings.cache_control,
                file_content_type=content_settings.content_type,
                file_content_md5=bytearray(content_settings.content_md5) if content_settings.content_md5 else None,
                file_content_encoding=content_settings.content_encoding,
                file_content_language=content_settings.content_language,
                file_content_disposition=content_settings.content_disposition,
            )
        file_permission = _get_file_permission(file_permission, permission_key, None)
        file_change_time = kwargs.pop('file_change_time', None)
        try:
            return cast(Dict[str, Any], await self._client.file.create(
                file_content_length=size,
                metadata=metadata,
                file_attributes=str(file_attributes) if file_attributes is not None else file_attributes,
                file_creation_time=_datetime_to_str(file_creation_time),
                file_last_write_time=_datetime_to_str(file_last_write_time),
                file_change_time=_datetime_to_str(file_change_time),
                file_permission=file_permission,
                file_permission_key=permission_key,
                file_http_headers=file_http_headers,
                optionalbody=data,
                content_length=len(data) if data is not None else None,
                lease_access_conditions=access_conditions,
                headers=headers,
                timeout=timeout,
                cls=return_response_headers,
                **kwargs
            ))
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def upload_file(
        self, data: Union[bytes, str, Iterable[AnyStr], AsyncIterable[AnyStr], IO[AnyStr]],
        length: Optional[int] = None,
        file_attributes: Optional[Union[str, "NTFSAttributes"]] = None,
        file_creation_time: Optional[Union[str, datetime]] = None,
        file_last_write_time: Optional[Union[str, datetime]] = None,
        file_permission: Optional[str] = None,
        permission_key: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Uploads a new file.

        :param data:
            Content of the file.
        :type data: Union[bytes, str, Iterable[AnyStr], AsyncIterable[AnyStr], IO[AnyStr]]
        :param int length:
            Length of the file in bytes. Specify its maximum size, up to 1 TiB.
        :param file_attributes:
            The file system attributes for files and directories.
            If not set, the default value would be "None" and the attributes will be set to "Archive".
            Here is an example for when the var type is str: 'Temporary|Archive'.
            file_attributes value is not case sensitive.
        :type file_attributes: str or ~azure.storage.fileshare.NTFSAttributes or None
        :param file_creation_time: Creation time for the file
        :type file_creation_time: str or ~datetime.datetime or None
        :param file_last_write_time: Last write time for the file
        :type file_last_write_time: str or ~datetime.datetime or None
        :param file_permission: If specified the permission (security
            descriptor) shall be set for the directory/file. This header can be
            used if Permission size is <= 8KB, else x-ms-file-permission-key
            header shall be used. Default value: Inherit. If SDDL is specified as
            input, it must have owner, group and dacl. Note: Only one of the
            x-ms-file-permission or x-ms-file-permission-key should be specified.
        :type file_permission: str
        :param permission_key: Key of the permission to be set for the
            directory/file. Note: Only one of the x-ms-file-permission or
            x-ms-file-permission-key should be specified.
        :type permission_key: str
        :keyword file_change_time:
            Change time for the file. If not specified, change time will be set to the current date/time.

            .. versionadded:: 12.8.0

                This parameter was introduced in API version '2021-06-08'.

        :paramtype file_change_time: str or ~datetime.datetime
        :keyword metadata:
            Name-value pairs associated with the file as metadata.
        :paramtype metadata: Optional[dict[str, str]]
        :keyword ~azure.storage.fileshare.ContentSettings content_settings:
            ContentSettings object used to set file properties. Used to set content type, encoding,
            language, disposition, md5, and cache control.
        :keyword bool validate_content:
            If true, calculates an MD5 hash for each range of the file. The storage
            service checks the hash of the content that has arrived with the hash
            that was sent. This is primarily valuable for detecting bitflips on
            the wire if using http instead of https as https (the default) will
            already validate. Note that this MD5 hash is not stored with the
            file.
        :keyword int max_concurrency:
            Maximum number of parallel connections to use when transferring the file in chunks.
            This option does not affect the underlying connection pool, and may
            require a separate configuration of the connection pool.
        :keyword str encoding:
            Defaults to UTF-8.
        :keyword lease:
            Required if the file has an active lease. Value can be a ShareLeaseClient object
            or the lease ID as a string.

            .. versionadded:: 12.1.0

        :paramtype lease: ~azure.storage.fileshare.aio.ShareLeaseClient or str
        :keyword progress_hook:
            An async callback to track the progress of a long running upload. The signature is
            function(current: int, total: Optional[int]) where current is the number of bytes transferred
            so far, and total is the size of the blob or None if the size is unknown.
        :paramtype progress_hook: Callable[[int, Optional[int]], Awaitable[None]]
        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :returns: File-updated property dict (Etag and last modified).
        :rtype: dict[str, Any]

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_client_async.py
                :start-after: [START upload_file]
                :end-before: [END upload_file]
                :language: python
                :dedent: 16
                :caption: Upload a file.
        """
        metadata = kwargs.pop('metadata', None)
        content_settings = kwargs.pop('content_settings', None)
        max_concurrency = kwargs.pop('max_concurrency', 1)
        validate_content = kwargs.pop('validate_content', False)
        progress_hook = kwargs.pop('progress_hook', None)
        timeout = kwargs.pop('timeout', None)
        encoding = kwargs.pop('encoding', 'UTF-8')

        if isinstance(data, str):
            data = data.encode(encoding)
        if length is None:
            length = get_length(data)
        if isinstance(data, bytes):
            data = data[:length]

        stream: Optional[Any] = None
        if isinstance(data, bytes):
            stream = BytesIO(data)
        elif hasattr(data, "read"):
            stream = data
        elif hasattr(data, "__iter__"):
            stream = IterStreamer(data, encoding=encoding)
        elif hasattr(data, '__aiter__'):
            stream = AsyncIterStreamer(cast(AsyncGenerator, data), encoding=encoding)
        else:
            raise TypeError(f"Unsupported data type: {type(data)}")
        return await _upload_file_helper(
            self,
            stream,
            length,
            metadata,
            content_settings,
            validate_content,
            timeout,
            max_concurrency,
            self._config,
            file_attributes=file_attributes,
            file_creation_time=file_creation_time,
            file_last_write_time=file_last_write_time,
            file_permission=file_permission,
            file_permission_key=permission_key,
            progress_hook=progress_hook,
            **kwargs)

    @distributed_trace_async
    async def start_copy_from_url(self, source_url: str, **kwargs: Any) -> Dict[str, Any]:
        """Initiates the copying of data from a source URL into the file
        referenced by the client.

        The status of this copy operation can be found using the `get_properties`
        method.

        :param str source_url:
            Specifies the URL of the source file.
        :keyword str file_permission:
            If specified the permission (security descriptor) shall be set for the directory/file.
            This value can be set to "source" to copy the security descriptor from the source file.
            Otherwise if set, this value will be used to override the source value. If not set, permission value
            is inherited from the parent directory of the target file. This setting can be
            used if Permission size is <= 8KB, otherwise permission_key shall be used.
            If SDDL is specified as input, it must have owner, group and dacl.
            Note: Only one of the file_permission or permission_key should be specified.

            .. versionadded:: 12.1.0

                This parameter was introduced in API version '2019-07-07'.

        :keyword str permission_key:
            Key of the permission to be set for the directory/file.
            This value can be set to "source" to copy the security descriptor from the source file.
            Otherwise if set, this value will be used to override the source value. If not set, permission value
            is inherited from the parent directory of the target file.
            Note: Only one of the file_permission or permission_key should be specified.

            .. versionadded:: 12.1.0

                This parameter was introduced in API version '2019-07-07'.

        :keyword file_permission_format:
            Specifies the format in which the permission is returned. If not specified, SDDL will be the default.
        :paramtype file_permission_format: Literal['sddl', 'binary']
        :keyword file_attributes:
            This value can be set to "source" to copy file attributes from the source file to the target file,
            or to clear all attributes, it can be set to "None". Otherwise it can be set to a list of attributes
            to set on the target file. If this is not set, the default value is "Archive".

            .. versionadded:: 12.1.0

                This parameter was introduced in API version '2019-07-07'.

        :paramtype file_attributes: str or ~azure.storage.fileshare.NTFSAttributes
        :keyword file_creation_time:
            This value can be set to "source" to copy the creation time from the source file to the target file,
            or a datetime to set as creation time on the target file. This could also be a string in ISO 8601 format.
            If this is not set, creation time will be set to the date time value of the creation
            (or when it was overwritten) of the target file by copy engine.

            .. versionadded:: 12.1.0

                This parameter was introduced in API version '2019-07-07'.

        :paramtype file_creation_time: str or ~datetime.datetime
        :keyword file_last_write_time:
            This value can be set to "source" to copy the last write time from the source file to the target file, or
            a datetime to set as the last write time on the target file. This could also be a string in ISO 8601 format.
            If this is not set, value will be the last write time to the file by the copy engine.

            .. versionadded:: 12.1.0

                This parameter was introduced in API version '2019-07-07'.

        :paramtype file_last_write_time: str or ~datetime.datetime
        :keyword file_change_time:
            Change time for the file. If not specified, change time will be set to the current date/time.

            .. versionadded:: 12.9.0

                This parameter was introduced in API version '2021-06-08'.

        :paramtype file_change_time: str or ~datetime.datetime
        :keyword bool ignore_read_only:
            Specifies the option to overwrite the target file if it already exists and has read-only attribute set.

            .. versionadded:: 12.1.0

                This parameter was introduced in API version '2019-07-07'.

        :keyword bool set_archive_attribute:
            Specifies the option to set the archive attribute on the target file.
            True means the archive attribute will be set on the target file despite attribute
            overrides or the source file state.

            .. versionadded:: 12.1.0

                This parameter was introduced in API version '2019-07-07'.

        :keyword metadata:
            Name-value pairs associated with the file as metadata.
        :paramtype metadata: Optional[dict[str, str]]
        :keyword lease:
            Required if the file has an active lease. Value can be a ShareLeaseClient object
            or the lease ID as a string.

            .. versionadded:: 12.1.0

        :paramtype lease: ~azure.storage.fileshare.aio.ShareLeaseClient or str
        :keyword str owner:
            NFS only. The owner of the file.
        :keyword str group:
            NFS only. The owning group of the file.
        :keyword str file_mode:
            NFS only. The file mode of the file.
        :keyword file_mode_copy_mode:
            NFS only. Applicable only when the copy source is a File. Determines the copy behavior
            of the mode bits of the file. Possible values are:

            source - The mode on the destination file is copied from the source file.
            override - The mode on the destination file is determined via the file_mode keyword.
        :paramtype file_mode_copy_mode: Literal['source', 'override']
        :keyword owner_copy_mode:
            NFS only. Applicable only when the copy source is a File. Determines the copy behavior
            of the owner and group of the file. Possible values are:

            source - The owner and group on the destination file is copied from the source file.
            override - The owner and group on the destination file is determined via the owner and group keywords.
        :paramtype owner_copy_mode: Literal['source', 'override']
        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :returns: Response after data copying operation has been initiated.
        :rtype: dict[str, Any]

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_client_async.py
                :start-after: [START copy_file_from_url]
                :end-before: [END copy_file_from_url]
                :language: python
                :dedent: 16
                :caption: Copy a file from a URL
        """
        metadata = kwargs.pop('metadata', None)
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        timeout = kwargs.pop('timeout', None)
        owner = kwargs.pop('owner', None)
        group = kwargs.pop('group', None)
        file_mode = kwargs.pop('file_mode', None)
        file_mode_copy_mode = kwargs.pop('file_mode_copy_mode', None)
        file_owner_copy_mode = kwargs.pop('owner_copy_mode', None)
        headers = kwargs.pop("headers", {})
        headers.update(add_metadata_headers(metadata))
        kwargs.update(get_smb_properties(kwargs))
        try:
            return cast(Dict[str, Any], await self._client.file.start_copy(
                source_url,
                metadata=metadata,
                lease_access_conditions=access_conditions,
                owner=owner,
                group=group,
                file_mode=file_mode,
                file_mode_copy_mode=file_mode_copy_mode,
                file_owner_copy_mode=file_owner_copy_mode,
                headers=headers,
                cls=return_response_headers,
                timeout=timeout,
                **kwargs
            ))
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def abort_copy(self, copy_id: Union[str, FileProperties], **kwargs: Any) -> None:
        """Abort an ongoing copy operation.

        This will leave a destination file with zero length and full metadata.
        This will raise an error if the copy operation has already ended.

        :param copy_id:
            The copy operation to abort. This can be either an ID, or an
            instance of FileProperties.
        :type copy_id: str or ~azure.storage.fileshare.FileProperties
        :keyword lease:
            Required if the file has an active lease. Value can be a ShareLeaseClient object
            or the lease ID as a string.

            .. versionadded:: 12.1.0

        :paramtype lease: ~azure.storage.fileshare.aio.ShareLeaseClient or str
        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :rtype: None
        """
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        timeout = kwargs.pop('timeout', None)
        if isinstance(copy_id, FileProperties):
            copy_id = copy_id.copy.id
        elif isinstance(copy_id, Dict):
            copy_id = copy_id['copy_id']
        try:
            await self._client.file.abort_copy(copy_id=copy_id,
                                               lease_access_conditions=access_conditions,
                                               timeout=timeout, **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def download_file(
        self, offset: Optional[int] = None,
        length: Optional[int] = None,
        **kwargs: Any
    ) -> StorageStreamDownloader:
        """Downloads a file to the StorageStreamDownloader. The readall() method must
        be used to read all the content or readinto() must be used to download the file into
        a stream. Using chunks() returns an async iterator which allows the user to iterate over the content in chunks.

        :param int offset:
            Start of byte range to use for downloading a section of the file.
            Must be set if length is provided.
        :param int length:
            Number of bytes to read from the stream. This is optional, but
            should be supplied for optimal performance.
        :keyword int max_concurrency:
            Maximum number of parallel connections to use when transferring the file in chunks.
            This option does not affect the underlying connection pool, and may
            require a separate configuration of the connection pool.
        :keyword bool validate_content:
            If true, calculates an MD5 hash for each chunk of the file. The storage
            service checks the hash of the content that has arrived with the hash
            that was sent. This is primarily valuable for detecting bitflips on
            the wire if using http instead of https as https (the default) will
            already validate. Note that this MD5 hash is not stored with the
            file. Also note that if enabled, the memory-efficient upload algorithm
            will not be used, because computing the MD5 hash requires buffering
            entire blocks, and doing so defeats the purpose of the memory-efficient algorithm.
        :keyword lease:
            Required if the file has an active lease. Value can be a ShareLeaseClient object
            or the lease ID as a string.

            .. versionadded:: 12.1.0

        :paramtype lease: ~azure.storage.fileshare.aio.ShareLeaseClient or str
        :keyword progress_hook:
            An async callback to track the progress of a long running download. The signature is
            function(current: int, total: int) where current is the number of bytes transferred
            so far, and total is the size of the blob or None if the size is unknown.
        :paramtype progress_hook: Callable[[int, int], Awaitable[None]]
        :keyword bool decompress: If True, any compressed content, identified by the Content-Encoding header, will be
            decompressed automatically before being returned. Default value is True.
        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :returns: A streaming object (StorageStreamDownloader)
        :rtype: ~azure.storage.fileshare.aio.StorageStreamDownloader

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_client_async.py
                :start-after: [START download_file]
                :end-before: [END download_file]
                :language: python
                :dedent: 16
                :caption: Download a file.
        """
        if length is not None and offset is None:
            raise ValueError("Offset value must not be None if length is set.")

        range_end = None
        if length is not None:
            if offset is None:
                raise ValueError("Offset value must not be None if length is set.")
            range_end = offset + length - 1  # Service actually uses an end-range inclusive index

        access_conditions = get_access_conditions(kwargs.pop('lease', None))

        downloader = StorageStreamDownloader(
            client=self._client.file,
            config=self._config,
            start_range=offset,
            end_range=range_end,
            name=self.file_name,
            path='/'.join(self.file_path),
            share=self.share_name,
            lease_access_conditions=access_conditions,
            cls=deserialize_file_stream,
            **kwargs
        )
        await downloader._setup()  # pylint: disable=protected-access
        return downloader

    @distributed_trace_async
    async def delete_file(self, **kwargs: Any) -> None:
        """Marks the specified file for deletion. The file is
        later deleted during garbage collection.

        :keyword lease:
            Required if the file has an active lease. Value can be a ShareLeaseClient object
            or the lease ID as a string.

            .. versionadded:: 12.1.0

        :paramtype lease: ~azure.storage.fileshare.aio.ShareLeaseClient or str
        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :rtype: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/file_samples_client_async.py
                :start-after: [START delete_file]
                :end-before: [END delete_file]
                :language: python
                :dedent: 16
                :caption: Delete a file.
        """
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        timeout = kwargs.pop('timeout', None)
        try:
            await self._client.file.delete(lease_access_conditions=access_conditions, timeout=timeout, **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def rename_file(self, new_name: str, **kwargs: Any) -> "ShareFileClient":
        """
        Rename the source file.

        :param str new_name:
            The new file name.
        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :keyword bool overwrite:
            A boolean value for if the destination file already exists, whether this request will
            overwrite the file or not. If true, the rename will succeed and will overwrite the
            destination file. If not provided or if false and the destination file does exist, the
            request will not overwrite the destination file. If provided and the destination file
            doesn't exist, the rename will succeed.
        :keyword bool ignore_read_only:
            A boolean value that specifies whether the ReadOnly attribute on a preexisting destination
            file should be respected. If true, the rename will succeed, otherwise, a previous file at the
            destination with the ReadOnly attribute set will cause the rename to fail.
        :keyword str file_permission:
            If specified the permission (security descriptor) shall be set for the file. This header
            can be used if Permission size is <= 8KB, else file_permission_key shall be used.
            If SDDL is specified as input, it must have owner, group and dacl.
            A value of 'preserve' can be passed to preserve source permissions.
            Note: Only one of the file_permission or file_permission_key should be specified.
        :keyword str file_permission_key:
            Key of the permission to be set for the file.
            Note: Only one of the file-permission or file-permission-key should be specified.
        :keyword file_permission_format:
            Specifies the format in which the permission is returned. If not specified, SDDL will be the default.
        :paramtype file_permission_format: Literal['sddl', 'binary']
        :keyword file_attributes:
            The file system attributes for the file.
        :paramtype file_attributes: ~azure.storage.fileshare.NTFSAttributes or str
        :keyword file_creation_time:
            Creation time for the file.
        :paramtype file_creation_time: ~datetime.datetime or str
        :keyword file_last_write_time:
            Last write time for the file.
        :paramtype file_last_write_time: ~datetime.datetime or str
        :keyword file_change_time:
            Change time for the file. If not specified, change time will be set to the current date/time.

            .. versionadded:: 12.8.0

                This parameter was introduced in API version '2021-06-08'.

        :paramtype file_change_time: str or ~datetime.datetime
        :keyword str content_type:
            The Content Type of the new file.

            .. versionadded:: 12.8.0

                This parameter was introduced in API version '2021-06-08'.

        :keyword Dict[str,str] metadata:
            A name-value pair to associate with a file storage object.
        :keyword source_lease:
            Required if the source file has an active lease. Value can be a ShareLeaseClient object
            or the lease ID as a string.
        :paramtype source_lease: ~azure.storage.fileshare.ShareLeaseClient or str
        :keyword destination_lease:
            Required if the destination file has an active lease. Value can be a ShareLeaseClient object
            or the lease ID as a string.
        :paramtype destination_lease: ~azure.storage.fileshare.ShareLeaseClient or str
        :returns: The new File Client.
        :rtype: ~azure.storage.fileshare.ShareFileClient
        """
        if not new_name:
            raise ValueError("Please specify a new file name.")

        new_name = new_name.strip('/')
        new_path_and_query = new_name.split('?')
        new_file_path = new_path_and_query[0]
        if len(new_path_and_query) == 2:
            new_file_sas = new_path_and_query[1] or self._query_str.strip('?')
        else:
            new_file_sas = self._query_str.strip('?')

        new_file_client = ShareFileClient(
            f'{self.scheme}://{self.primary_hostname}', self.share_name, new_file_path,
            credential=new_file_sas or self.credential, api_version=self.api_version,
            _hosts=self._hosts, _configuration=self._config, _pipeline=self._pipeline,
            _location_mode=self._location_mode, allow_trailing_dot=self.allow_trailing_dot,
            allow_source_trailing_dot=self.allow_source_trailing_dot, token_intent=self.file_request_intent
        )

        kwargs.update(get_rename_smb_properties(kwargs))

        file_http_headers = None
        content_type = kwargs.pop('content_type', None)
        if content_type:
            file_http_headers = FileHTTPHeaders(
                file_content_type=content_type
            )

        timeout = kwargs.pop('timeout', None)
        overwrite = kwargs.pop('overwrite', None)
        metadata = kwargs.pop('metadata', None)
        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata))

        source_access_conditions = get_source_access_conditions(kwargs.pop('source_lease', None))
        dest_access_conditions = get_dest_access_conditions(kwargs.pop('destination_lease', None))

        try:
            await new_file_client._client.file.rename(  # pylint: disable=protected-access
                self.url,
                timeout=timeout,
                replace_if_exists=overwrite,
                file_http_headers=file_http_headers,
                source_lease_access_conditions=source_access_conditions,
                destination_lease_access_conditions=dest_access_conditions,
                headers=headers,
                **kwargs)

            return new_file_client
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def get_file_properties(self, **kwargs: Any) -> FileProperties:
        """Returns all user-defined metadata, standard HTTP properties, and
        system properties for the file.

        :keyword lease:
            Required if the file has an active lease. Value can be a ShareLeaseClient object
            or the lease ID as a string.

            .. versionadded:: 12.1.0

        :paramtype lease: ~azure.storage.fileshare.aio.ShareLeaseClient or str
        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :returns: FileProperties
        :rtype: ~azure.storage.fileshare.FileProperties
        """
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        timeout = kwargs.pop('timeout', None)
        try:
            file_props = cast(FileProperties, await self._client.file.get_properties(
                sharesnapshot=self.snapshot,
                lease_access_conditions=access_conditions,
                timeout=timeout,
                cls=deserialize_file_properties,
                **kwargs
            ))
        except HttpResponseError as error:
            process_storage_error(error)
        file_props.name = self.file_name
        file_props.share = self.share_name
        file_props.snapshot = self.snapshot
        file_props.path = "/".join(self.file_path)
        return file_props

    @distributed_trace_async
    async def set_http_headers(
        self, content_settings: "ContentSettings",
        file_attributes: Optional[Union[str, "NTFSAttributes"]] = None,
        file_creation_time: Optional[Union[str, datetime]] = None,
        file_last_write_time: Optional[Union[str, datetime]] = None,
        file_permission: Optional[str] = None,
        permission_key: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Sets HTTP headers on the file.

        :param ~azure.storage.fileshare.ContentSettings content_settings:
            ContentSettings object used to set file properties. Used to set content type, encoding,
            language, disposition, md5, and cache control.
        :param file_attributes:
            The file system attributes for files and directories.
            If not set, indicates preservation of existing values.
            Here is an example for when the var type is str: 'Temporary|Archive'
        :type file_attributes: str or ~azure.storage.fileshare.NTFSAttributes or None
        :param file_creation_time: Creation time for the file
        :type file_creation_time: str or ~datetime.datetime or None
        :param file_last_write_time: Last write time for the file
        :type file_last_write_time: str or ~datetime.datetime or None
        :param file_permission: If specified the permission (security
            descriptor) shall be set for the directory/file. This header can be
            used if Permission size is <= 8KB, else x-ms-file-permission-key
            header shall be used. Default value: Inherit. If SDDL is specified as
            input, it must have owner, group and dacl. Note: Only one of the
            x-ms-file-permission or x-ms-file-permission-key should be specified.
        :type file_permission: str
        :param permission_key: Key of the permission to be set for the
            directory/file. Note: Only one of the x-ms-file-permission or
            x-ms-file-permission-key should be specified.
        :type permission_key: str
        :keyword file_permission_format:
            Specifies the format in which the permission is returned. If not specified, SDDL will be the default.
        :paramtype file_permission_format: Literal['sddl', 'binary']
        :keyword file_change_time:
            Change time for the file. If not specified, change time will be set to the current date/time.

            .. versionadded:: 12.8.0

                This parameter was introduced in API version '2021-06-08'.

        :paramtype file_change_time: str or ~datetime.datetime
        :keyword lease:
            Required if the file has an active lease. Value can be a ShareLeaseClient object
            or the lease ID as a string.

            .. versionadded:: 12.1.0

        :paramtype lease: ~azure.storage.fileshare.aio.ShareLeaseClient or str
        :keyword str owner:
            NFS only. The owner of the file.
        :keyword str group:
            NFS only. The owning group of the file.
        :keyword str file_mode:
            NFS only. The file mode of the file.
        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :returns: File-updated property dict (Etag and last modified).
        :rtype: dict[str, Any]
        """
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        timeout = kwargs.pop('timeout', None)
        file_content_length = kwargs.pop("size", None)
        file_http_headers = FileHTTPHeaders(
            file_cache_control=content_settings.cache_control,
            file_content_type=content_settings.content_type,
            file_content_md5=bytearray(content_settings.content_md5) if content_settings.content_md5 else None,
            file_content_encoding=content_settings.content_encoding,
            file_content_language=content_settings.content_language,
            file_content_disposition=content_settings.content_disposition,
        )
        file_permission = _get_file_permission(file_permission, permission_key, None)
        file_change_time = kwargs.pop('file_change_time', None)
        try:
            return cast(Dict[str, Any], await self._client.file.set_http_headers(
                file_content_length=file_content_length,
                file_http_headers=file_http_headers,
                file_attributes=str(file_attributes) if file_attributes is not None else file_attributes,
                file_creation_time=_datetime_to_str(file_creation_time),
                file_last_write_time=_datetime_to_str(file_last_write_time),
                file_change_time=_datetime_to_str(file_change_time),
                file_permission=file_permission,
                file_permission_key=permission_key,
                lease_access_conditions=access_conditions,
                timeout=timeout,
                cls=return_response_headers,
                **kwargs
            ))
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def set_file_metadata(self, metadata: Optional[Dict[str, Any]] = None, **kwargs: Any) -> Dict[str, Any]:
        """Sets user-defined metadata for the specified file as one or more
        name-value pairs.

        Each call to this operation replaces all existing metadata
        attached to the file. To remove all metadata from the file,
        call this operation with no metadata dict.

        :param metadata:
            Name-value pairs associated with the file as metadata.
        :type metadata: dict[str, str]
        :keyword lease:
            Required if the file has an active lease. Value can be a ShareLeaseClient object
            or the lease ID as a string.

            .. versionadded:: 12.1.0

        :paramtype lease: ~azure.storage.fileshare.aio.ShareLeaseClient or str
        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :returns: File-updated property dict (Etag and last modified).
        :rtype: dict[str, Any]
        """
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        timeout = kwargs.pop('timeout', None)
        headers = kwargs.pop("headers", {})
        headers.update(add_metadata_headers(metadata))
        try:
            return cast(Dict[str, Any], await self._client.file.set_metadata(
                metadata=metadata, lease_access_conditions=access_conditions,
                timeout=timeout, cls=return_response_headers, headers=headers, **kwargs
            ))
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def upload_range(
        self, data: bytes,
        offset: int,
        length: int,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Upload a range of bytes to a file.

        :param bytes data:
            The data to upload.
        :param int offset:
            Start of byte range to use for uploading a section of the file.
            The range can be up to 4 MB in size.
        :param int length:
            Number of bytes to use for uploading a section of the file.
            The range can be up to 4 MB in size.
        :keyword bool validate_content:
            If true, calculates an MD5 hash of the page content. The storage
            service checks the hash of the content that has arrived
            with the hash that was sent. This is primarily valuable for detecting
            bitflips on the wire if using http instead of https as https (the default)
            will already validate. Note that this MD5 hash is not stored with the
            file.
        :keyword file_last_write_mode:
            If the file last write time should be preserved or overwritten. Possible values
            are "preserve" or "now". If not specified, file last write time will be changed to
            the current date/time.

            .. versionadded:: 12.8.0

                This parameter was introduced in API version '2021-06-08'.

        :paramtype file_last_write_mode: Literal["preserve", "now"]
        :keyword lease:
            Required if the file has an active lease. Value can be a ShareLeaseClient object
            or the lease ID as a string.

            .. versionadded:: 12.1.0

        :paramtype lease: ~azure.storage.fileshare.aio.ShareLeaseClient or str
        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :keyword str encoding:
            Defaults to UTF-8.
        :returns: File-updated property dict (Etag and last modified).
        :rtype: Dict[str, Any]
        """
        validate_content = kwargs.pop('validate_content', False)
        timeout = kwargs.pop('timeout', None)
        encoding = kwargs.pop('encoding', 'UTF-8')
        file_last_write_mode = kwargs.pop('file_last_write_mode', None)
        if isinstance(data, str):
            data = data.encode(encoding)
        end_range = offset + length - 1  # Reformat to an inclusive range index
        content_range = f'bytes={offset}-{end_range}'
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        try:
            return cast(Dict[str, Any], await self._client.file.upload_range(
                range=content_range,
                content_length=length,
                optionalbody=data,
                timeout=timeout,
                validate_content=validate_content,
                file_last_written_mode=file_last_write_mode,
                lease_access_conditions=access_conditions,
                cls=return_response_headers,
                **kwargs
            ))
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def upload_range_from_url(
        self, source_url: str,
        offset: int,
        length: int,
        source_offset: int,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Writes the bytes from one Azure File endpoint into the specified range of another Azure File endpoint.

        :param int offset:
            Start of byte range to use for updating a section of the file.
            The range can be up to 4 MB in size.
        :param int length:
            Number of bytes to use for updating a section of the file.
            The range can be up to 4 MB in size.
        :param str source_url:
            A URL of up to 2 KB in length that specifies an Azure file or blob.
            The value should be URL-encoded as it would appear in a request URI.
            If the source is in another account, the source must either be public
            or must be authenticated via a shared access signature. If the source
            is public, no authentication is required.
            Examples:
            https://myaccount.file.core.windows.net/myshare/mydir/myfile
            https://otheraccount.file.core.windows.net/myshare/mydir/myfile?sastoken
        :param int source_offset:
            This indicates the start of the range of bytes(inclusive) that has to be taken from the copy source.
            The service will read the same number of bytes as the destination range (length-offset).
        :keyword ~datetime.datetime source_if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this conditional header to copy the blob only if the source
            blob has been modified since the specified date/time.
        :keyword ~datetime.datetime source_if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this conditional header to copy the blob only if the source blob
            has not been modified since the specified date/time.
        :keyword str source_etag:
            The source ETag value, or the wildcard character (*). Used to check if the resource has changed,
            and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions source_match_condition:
            The source match condition to use upon the etag.
        :keyword file_last_write_mode:
            If the file last write time should be preserved or overwritten. Possible values
            are "preserve" or "now". If not specified, file last write time will be changed to
            the current date/time.

            .. versionadded:: 12.8.0

                This parameter was introduced in API version '2021-06-08'.

        :paramtype file_last_write_mode: Literal["preserve", "now"]
        :keyword lease:
            Required if the file has an active lease. Value can be a ShareLeaseClient object
            or the lease ID as a string.

            .. versionadded:: 12.1.0

        :paramtype lease: ~azure.storage.fileshare.aio.ShareLeaseClient or str
        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :keyword str source_authorization:
            Authenticate as a service principal using a client secret to access a source blob. Ensure "bearer " is
            the prefix of the source_authorization string.
        :returns: Result after writing to the specified range of the destination Azure File endpoint.
        :rtype: dict[str, Any]
        """
        options = _upload_range_from_url_options(
            source_url=source_url,
            offset=offset,
            length=length,
            source_offset=source_offset,
            **kwargs
        )
        try:
            return cast(Dict[str, Any], await self._client.file.upload_range_from_url(**options))
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def get_ranges(
        self, offset: Optional[int] = None,
        length: Optional[int] = None,
        **kwargs: Any
    ) -> List[Dict[str, int]]:
        """Returns the list of valid page ranges for a file or snapshot
        of a file.

        :param int offset:
            Specifies the start offset of bytes over which to get ranges.
        :param int length:
           Number of bytes to use over which to get ranges.
        :keyword lease:
            Required if the file has an active lease. Value can be a ShareLeaseClient object
            or the lease ID as a string.

            .. versionadded:: 12.1.0

        :paramtype lease: ~azure.storage.fileshare.ShareLeaseClient or str
        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :returns:
            A list of valid ranges.
        :rtype: List[dict[str, int]]
        """
        options = _get_ranges_options(
            snapshot=self.snapshot,
            offset=offset,
            length=length,
            **kwargs)
        try:
            ranges = await self._client.file.get_range_list(**options)
        except HttpResponseError as error:
            process_storage_error(error)
        return [{'start': file_range.start, 'end': file_range.end} for file_range in ranges.ranges]

    @distributed_trace_async
    async def get_ranges_diff(
        self, previous_sharesnapshot: Union[str, Dict[str, Any]],
        offset: Optional[int] = None,
        length: Optional[int] = None,
        *,
        include_renames: Optional[bool] = None,
        **kwargs: Any
    ) -> Tuple[List[Dict[str, int]], List[Dict[str, int]]]:
        """Returns the list of valid page ranges for a file or snapshot
        of a file.

        .. versionadded:: 12.6.0

        :param int offset:
            Specifies the start offset of bytes over which to get ranges.
        :param int length:
           Number of bytes to use over which to get ranges.
        :param str previous_sharesnapshot:
            The snapshot diff parameter that contains an opaque DateTime value that
            specifies a previous file snapshot to be compared
            against a more recent snapshot or the current file.
        :keyword Optional[bool] include_renames:
            Only valid if previous_sharesnapshot parameter is provided. Specifies whether the changed ranges for
            a file that has been renamed or moved between the target snapshot (or live file) and the previous
            snapshot should be listed. If set to True, the valid changed ranges for the file will be returned.
            If set to False, the operation will result in a 409 (Conflict) response.
        :keyword lease:
            Required if the file has an active lease. Value can be a ShareLeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.fileshare.ShareLeaseClient or str
        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :returns:
            A tuple of two lists of file ranges as dictionaries with 'start' and 'end' keys.
            The first element are filled file ranges, the 2nd element is cleared file ranges.
        :rtype: tuple[list[dict[str, int]], list[dict[str, int]]]
        """
        options = _get_ranges_options(
            snapshot=self.snapshot,
            offset=offset,
            length=length,
            previous_sharesnapshot=previous_sharesnapshot,
            support_rename=include_renames,
            **kwargs)
        try:
            ranges = await self._client.file.get_range_list(**options)
        except HttpResponseError as error:
            process_storage_error(error)
        return get_file_ranges_result(ranges)

    @distributed_trace_async
    async def clear_range(self, offset: int, length: int, **kwargs: Any) -> Dict[str, Any]:
        """Clears the specified range and releases the space used in storage for
        that range.

        :param int offset:
            Start of byte range to use for clearing a section of the file.
            The range can be up to 4 MB in size.
        :param int length:
            Number of bytes to use for clearing a section of the file.
            The range can be up to 4 MB in size.
        :keyword lease:
            Required if the file has an active lease. Value can be a ShareLeaseClient object
            or the lease ID as a string.

            .. versionadded:: 12.1.0

        :paramtype lease: ~azure.storage.fileshare.aio.ShareLeaseClient or str
        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :returns: File-updated property dict (Etag and last modified).
        :rtype: Dict[str, Any]
        """
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        timeout = kwargs.pop('timeout', None)

        if offset is None or offset % 512 != 0:
            raise ValueError("offset must be an integer that aligns with 512 bytes file size")
        if length is None or length % 512 != 0:
            raise ValueError("length must be an integer that aligns with 512 bytes file size")
        end_range = length + offset - 1  # Reformat to an inclusive range index
        content_range = f"bytes={offset}-{end_range}"
        try:
            return cast(Dict[str, Any], await self._client.file.upload_range(
                timeout=timeout,
                cls=return_response_headers,
                content_length=0,
                optionalbody=None,
                file_range_write="clear",
                range=content_range,
                lease_access_conditions=access_conditions,
                **kwargs
            ))
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def resize_file(self, size: int, **kwargs: Any) -> Dict[str, Any]:
        """Resizes a file to the specified size.

        :param int size:
            Size to resize file to (in bytes)
        :keyword lease:
            Required if the file has an active lease. Value can be a ShareLeaseClient object
            or the lease ID as a string.

            .. versionadded:: 12.1.0

        :paramtype lease: ~azure.storage.fileshare.aio.ShareLeaseClient or str
        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :returns: File-updated property dict (Etag and last modified).
        :rtype: Dict[str, Any]
        """
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        timeout = kwargs.pop('timeout', None)
        try:
            return cast(Dict[str, Any], await self._client.file.set_http_headers(
                file_content_length=size,
                file_attributes=None,
                file_creation_time=None,
                file_last_write_time=None,
                file_permission="preserve",
                lease_access_conditions=access_conditions,
                cls=return_response_headers,
                timeout=timeout,
                **kwargs
            ))
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace
    def list_handles(self, **kwargs: Any) -> AsyncItemPaged[Handle]:
        """Lists handles for file.

        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :returns: An auto-paging iterable of Handle
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.storage.fileshare.Handle]
        """
        timeout = kwargs.pop('timeout', None)
        results_per_page = kwargs.pop("results_per_page", None)
        command = functools.partial(
            self._client.file.list_handles,
            sharesnapshot=self.snapshot,
            timeout=timeout,
            **kwargs)
        return AsyncItemPaged(
            command, results_per_page=results_per_page,
            page_iterator_class=HandlesPaged)

    @distributed_trace_async
    async def close_handle(self, handle: Union[str, Handle], **kwargs: Any) -> Dict[str, int]:
        """Close an open file handle.

        :param handle:
            A specific handle to close.
        :type handle: str or ~azure.storage.fileshare.Handle
        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :returns:
            The number of handles closed (this may be 0 if the specified handle was not found)
            and the number of handles failed to close in a dict.
        :rtype: dict[str, int]
        """
        if isinstance(handle, Handle):
            handle_id = handle.id
        else:
            handle_id = handle
        if handle_id == '*':
            raise ValueError("Handle ID '*' is not supported. Use 'close_all_handles' instead.")
        try:
            response = await self._client.file.force_close_handles(
                handle_id,
                marker=None,
                sharesnapshot=self.snapshot,
                cls=return_response_headers,
                **kwargs
            )
            return {
                'closed_handles_count': response.get('number_of_handles_closed', 0),
                'failed_handles_count': response.get('number_of_handles_failed', 0)
            }
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def close_all_handles(self, **kwargs: Any) -> Dict[str, int]:
        """Close any open file handles.

        This operation will block until the service has closed all open handles.

        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :returns:
            The number of handles closed (this may be 0 if the specified handle was not found)
            and the number of handles failed to close in a dict.
        :rtype: dict[str, int]
        """
        timeout = kwargs.pop('timeout', None)
        start_time = time.time()

        try_close = True
        continuation_token = None
        total_closed = 0
        total_failed = 0
        while try_close:
            try:
                response = await self._client.file.force_close_handles(
                    handle_id='*',
                    timeout=timeout,
                    marker=continuation_token,
                    sharesnapshot=self.snapshot,
                    cls=return_response_headers,
                    **kwargs
                )
            except HttpResponseError as error:
                process_storage_error(error)
            continuation_token = response.get('marker')
            try_close = bool(continuation_token)
            total_closed += response.get('number_of_handles_closed', 0)
            total_failed += response.get('number_of_handles_failed', 0)
            if timeout:
                timeout = max(0, timeout - (time.time() - start_time))
        return {
            'closed_handles_count': total_closed,
            'failed_handles_count': total_failed
        }

    @distributed_trace_async
    async def create_hardlink(
        self, target: str,
        *,
        lease: Optional[Union[ShareLeaseClient, str]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """NFS only. Creates a hard link to the file specified by path.

        :param str target:
            Specifies the path of the target file to which the link will be created, up to 2 KiB in length.
            It should be the full path of the target starting from the root. The target file must be in the
            same share and the same storage account.
        :keyword lease:
            Required if the file has an active lease. Value can be a ShareLeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.fileshare.ShareLeaseClient or str or None
        :keyword Optional[int] timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :returns: File-updated property dict (ETag and last modified).
        :rtype: dict[str, Any]
        """
        try:
            return cast(Dict[str, Any], await self._client.file.create_hard_link(
                target_file=target,
                lease_access_conditions=lease,
                timeout=timeout,
                cls=return_response_headers,
                **kwargs
            ))
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def create_symlink(
        self, target: str,
        *,
        metadata: Optional[Dict[str, str]] = None,
        file_creation_time: Optional[Union[str, datetime]] = None,
        file_last_write_time: Optional[Union[str, datetime]] = None,
        owner: Optional[str] = None,
        group: Optional[str] = None,
        lease: Optional[Union[ShareLeaseClient, str]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """NFS only. Creates a symbolic link to the specified file.

        :param str target:
            Specifies the file path the symbolic link will point to. The file path can be either relative or absolute.
        :keyword dict[str, str] metadata:
            Name-value pairs associated with the file as metadata.
        :keyword file_creation_time: Creation time for the file.
        :paramtype file_creation_time: str or ~datetime.datetime
        :keyword file_last_write_time: Last write time for the file.
        :paramtype file_last_write_time: str or ~datetime.datetime
        :keyword str owner: The owner of the file.
        :keyword str group: The owning group of the file.
        :keyword lease:
            Required if the file has an active lease. Value can be a ShareLeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.fileshare.ShareLeaseClient or str
        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :returns: File-updated property dict (ETag and last modified).
        :rtype: dict[str, Any]
        """
        try:
            return cast(Dict[str, Any], await self._client.file.create_symbolic_link(
                link_text=target,
                metadata=metadata,
                file_creation_time=file_creation_time,
                file_last_write_time=file_last_write_time,
                owner=owner,
                group=group,
                lease_access_conditions=lease,
                timeout=timeout,
                cls=return_response_headers,
                **kwargs
            ))
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def get_symlink(
        self,
        *,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """NFS only. Gets the symbolic link for the file client.

        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timeouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :returns: File-updated property dict (ETag and last modified).
        :rtype: dict[str, Any]
        """
        try:
            return cast(Dict[str, Any], await self._client.file.get_symbolic_link(
                timeout=timeout,
                cls=return_response_headers,
                **kwargs
            ))
        except HttpResponseError as error:
            process_storage_error(error)
