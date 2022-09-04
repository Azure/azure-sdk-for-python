# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-many-lines, invalid-overridden-method, too-many-public-methods
import functools
import sys
import time
import warnings
from io import BytesIO
from typing import Optional, Union, IO, List, Tuple, Dict, Any, Iterable, TYPE_CHECKING  # pylint: disable=unused-import

import six
from azure.core.async_paging import AsyncItemPaged
from azure.core.exceptions import HttpResponseError

from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async
from .._parser import _datetime_to_str, _get_file_permission
from .._shared.parser import _str

from .._generated.aio import AzureFileStorage
from .._generated.models import FileHTTPHeaders
from .._shared.policies_async import ExponentialRetry
from .._shared.uploads_async import upload_data_chunks, FileChunkUploader, IterStreamer
from .._shared.base_client_async import AsyncStorageAccountHostsMixin
from .._shared.request_handlers import add_metadata_headers, get_length
from .._shared.response_handlers import return_response_headers, process_storage_error
from .._deserialize import deserialize_file_properties, deserialize_file_stream, get_file_ranges_result
from .._serialize import (
    get_access_conditions,
    get_api_version,
    get_dest_access_conditions,
    get_rename_smb_properties,
    get_smb_properties,
    get_source_access_conditions)
from .._file_client import ShareFileClient as ShareFileClientBase
from ._models import HandlesPaged
from ._lease_async import ShareLeaseClient
from ._download_async import StorageStreamDownloader

if TYPE_CHECKING:
    from datetime import datetime
    from .._models import ShareProperties, ContentSettings, FileProperties, NTFSAttributes
    from .._generated.models import HandleItem


async def _upload_file_helper(
    client,
    stream,
    size,
    metadata,
    content_settings,
    validate_content,
    timeout,
    max_concurrency,
    file_settings,
    file_attributes="none",
    file_creation_time="now",
    file_last_write_time="now",
    file_permission=None,
    file_permission_key=None,
    progress_hook=None,
    **kwargs
):
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
        return sorted(responses, key=lambda r: r.get('last_modified'))[-1]
    except HttpResponseError as error:
        process_storage_error(error)


class ShareFileClient(AsyncStorageAccountHostsMixin, ShareFileClientBase):
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
        an account shared access key, or an instance of a TokenCredentials class from azure.identity.
        If the resource URI already contains a SAS token, this will be ignored in favor of an explicit credential
        - except in the case of AzureSasCredential, where the conflicting SAS tokens will raise a ValueError.
        If using an instance of AzureNamedKeyCredential, "name" should be the storage account name, and "key"
        should be the storage account key.
    :keyword str api_version:
        The Storage API version to use for requests. Default value is the most recent service version that is
        compatible with the current SDK. Setting to an older version may result in reduced feature compatibility.

        .. versionadded:: 12.1.0

    :keyword str secondary_hostname:
        The hostname of the secondary endpoint.
    :keyword int max_range_size: The maximum range size used for a file upload. Defaults to 4*1024*1024.
    """

    def __init__(  # type: ignore
        self,
        account_url,  # type: str
        share_name,  # type: str
        file_path,  # type: str
        snapshot=None,  # type: Optional[Union[str, Dict[str, Any]]]
        credential=None,  # type: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, "TokenCredential"]] # pylint: disable=line-too-long
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        kwargs["retry_policy"] = kwargs.get("retry_policy") or ExponentialRetry(**kwargs)
        loop = kwargs.pop('loop', None)
        if loop and sys.version_info >= (3, 8):
            warnings.warn("The 'loop' parameter was deprecated from asyncio's high-level"
            "APIs in Python 3.8 and is no longer supported.", DeprecationWarning)
        super(ShareFileClient, self).__init__(
            account_url, share_name=share_name, file_path=file_path, snapshot=snapshot,
            credential=credential, **kwargs
        )
        self._client = AzureFileStorage(self.url, base_url=self.url, pipeline=self._pipeline)
        self._client._config.version = get_api_version(kwargs) # pylint: disable=protected-access

    @distributed_trace_async
    async def acquire_lease(self, lease_id=None, **kwargs):
        # type: (Optional[str], **Any) -> ShareLeaseClient
        """Requests a new lease.

        If the file does not have an active lease, the File
        Service creates a lease on the blob and returns a new lease.

        :param str lease_id:
            Proposed lease ID, in a GUID string format. The File Service
            returns 400 (Invalid request) if the proposed lease ID is not
            in the correct format.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: A ShareLeaseClient object.
        :rtype: ~azure.storage.fileshare.aio.ShareLeaseClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/blob_samples_common.py
                :start-after: [START acquire_lease_on_blob]
                :end-before: [END acquire_lease_on_blob]
                :language: python
                :dedent: 8
                :caption: Acquiring a lease on a blob.
        """
        kwargs['lease_duration'] = -1
        lease = ShareLeaseClient(self, lease_id=lease_id)  # type: ignore
        await lease.acquire(**kwargs)
        return lease

    @distributed_trace_async
    async def create_file(  # type: ignore
        self,
        size,  # type: int
        file_attributes="none",  # type: Union[str, NTFSAttributes]
        file_creation_time="now",  # type: Optional[Union[str, datetime]]
        file_last_write_time="now",  # type: Optional[Union[str, datetime]]
        file_permission=None,  # type: Optional[str]
        permission_key=None,  # type: Optional[str]
        **kwargs  # type: Any
    ):
        # type: (...) -> Dict[str, Any]
        """Creates a new file.

        Note that it only initializes the file with no content.

        :param int size: Specifies the maximum size for the file,
            up to 1 TB.
        :param file_attributes:
            The file system attributes for files and directories.
            If not set, the default value would be "None" and the attributes will be set to "Archive".
            Here is an example for when the var type is str: 'Temporary|Archive'.
            file_attributes value is not case sensitive.
        :type file_attributes: str or :class:`~azure.storage.fileshare.NTFSAttributes`
        :param file_creation_time: Creation time for the file
            Default value: Now.
        :type file_creation_time: str or ~datetime.datetime
        :param file_last_write_time: Last write time for the file
            Default value: Now.
        :type file_last_write_time: str or ~datetime.datetime
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
        :keyword ~azure.storage.fileshare.ContentSettings content_settings:
            ContentSettings object used to set file properties. Used to set content type, encoding,
            language, disposition, md5, and cache control.
        :keyword dict(str,str) metadata:
            Name-value pairs associated with the file as metadata.
        :keyword lease:
            Required if the file has an active lease. Value can be a ShareLeaseClient object
            or the lease ID as a string.

            .. versionadded:: 12.1.0

        :paramtype lease: ~azure.storage.fileshare.aio.ShareLeaseClient or str
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: File-updated property dict (Etag and last modified).
        :rtype: dict(str, Any)

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
        file_permission = _get_file_permission(file_permission, permission_key, 'Inherit')
        file_change_time = kwargs.pop('file_change_time', None)
        try:
            return await self._client.file.create(  # type: ignore
                file_content_length=size,
                metadata=metadata,
                file_attributes=_str(file_attributes),
                file_creation_time=_datetime_to_str(file_creation_time),
                file_last_write_time=_datetime_to_str(file_last_write_time),
                file_change_time=_datetime_to_str(file_change_time),
                file_permission=file_permission,
                file_permission_key=permission_key,
                file_http_headers=file_http_headers,
                lease_access_conditions=access_conditions,
                headers=headers,
                timeout=timeout,
                cls=return_response_headers,
                **kwargs
            )
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def upload_file(
        self, data,  # type: Any
        length=None,  # type: Optional[int]
        file_attributes="none",  # type: Union[str, NTFSAttributes]
        file_creation_time="now",  # type: Optional[Union[str, datetime]]
        file_last_write_time="now",  # type: Optional[Union[str, datetime]]
        file_permission=None,  # type: Optional[str]
        permission_key=None,  # type: Optional[str]
        **kwargs  # type: Any
    ):
        # type: (...) -> Dict[str, Any]
        """Uploads a new file.

        :param Any data:
            Content of the file.
        :param int length:
            Length of the file in bytes. Specify its maximum size, up to 1 TiB.
        :param file_attributes:
            The file system attributes for files and directories.
            If not set, the default value would be "None" and the attributes will be set to "Archive".
            Here is an example for when the var type is str: 'Temporary|Archive'.
            file_attributes value is not case sensitive.
        :type file_attributes: str or ~azure.storage.fileshare.NTFSAttributes
        :param file_creation_time: Creation time for the file
            Default value: Now.
        :type file_creation_time: str or ~datetime.datetime
        :param file_last_write_time: Last write time for the file
            Default value: Now.
        :type file_last_write_time: str or ~datetime.datetime
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
        :keyword dict(str,str) metadata:
            Name-value pairs associated with the file as metadata.
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
            Maximum number of parallel connections to use.
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
            The timeout parameter is expressed in seconds.
        :returns: File-updated property dict (Etag and last modified).
        :rtype: dict(str, Any)

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

        if isinstance(data, six.text_type):
            data = data.encode(encoding)
        if length is None:
            length = get_length(data)
        if isinstance(data, bytes):
            data = data[:length]

        if isinstance(data, bytes):
            stream = BytesIO(data)
        elif hasattr(data, "read"):
            stream = data
        elif hasattr(data, "__iter__"):
            stream = IterStreamer(data, encoding=encoding)  # type: ignore
        else:
            raise TypeError("Unsupported data type: {}".format(type(data)))
        return await _upload_file_helper(  # type: ignore
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
            **kwargs
        )

    @distributed_trace_async
    async def start_copy_from_url(self, source_url, **kwargs):
        # type: (str, Any) -> Any
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

        :keyword file_attributes:
            This value can be set to "source" to copy file attributes from the source file to the target file,
            or to clear all attributes, it can be set to "None". Otherwise it can be set to a list of attributes
            to set on the target file. If this is not set, the default value is "Archive".

            .. versionadded:: 12.1.0
                This parameter was introduced in API version '2019-07-07'.

        :paramtype file_attributes: str or :class:`~azure.storage.fileshare.NTFSAttributes`
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
        :type metadata: dict(str, str)
        :keyword lease:
            Required if the file has an active lease. Value can be a ShareLeaseClient object
            or the lease ID as a string.

            .. versionadded:: 12.1.0

        :paramtype lease: ~azure.storage.fileshare.aio.ShareLeaseClient or str
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: dict(str, Any)

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
        headers = kwargs.pop("headers", {})
        headers.update(add_metadata_headers(metadata))
        kwargs.update(get_smb_properties(kwargs))
        try:
            return await self._client.file.start_copy(
                source_url,
                metadata=metadata,
                lease_access_conditions=access_conditions,
                headers=headers,
                cls=return_response_headers,
                timeout=timeout,
                **kwargs
            )
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def abort_copy(self, copy_id, **kwargs):
        # type: (Union[str, FileProperties], Any) -> None
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
            The timeout parameter is expressed in seconds.
        :rtype: None
        """
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        timeout = kwargs.pop('timeout', None)
        try:
            copy_id = copy_id.copy.id
        except AttributeError:
            try:
                copy_id = copy_id["copy_id"]
            except TypeError:
                pass
        try:
            await self._client.file.abort_copy(copy_id=copy_id,
                                               lease_access_conditions=access_conditions,
                                               timeout=timeout, **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def download_file(
        self,
        offset=None,  # type: Optional[int]
        length=None,  # type: Optional[int]
        **kwargs  # type: Any
    ):
        # type: (...) -> StorageStreamDownloader
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
            Maximum number of parallel connections to use.
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
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
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
    async def delete_file(self, **kwargs):
        # type: (Any) -> None
        """Marks the specified file for deletion. The file is
        later deleted during garbage collection.

        :keyword lease:
            Required if the file has an active lease. Value can be a ShareLeaseClient object
            or the lease ID as a string.

            .. versionadded:: 12.1.0

        :paramtype lease: ~azure.storage.fileshare.aio.ShareLeaseClient or str
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
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
    async def rename_file(
            self, new_name, # type: str
            **kwargs # type: Any
        ):
        # type: (...) -> ShareFileClient
        """
        Rename the source file.

        :param str new_name:
            The new file name.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
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
        :keyword file_attributes:
            The file system attributes for the file.
        :paramtype file_attributes:~azure.storage.fileshare.NTFSAttributes or str
        :keyword file_creation_time:
            Creation time for the file.
        :paramtype file_creation_time:~datetime.datetime or str
        :keyword file_last_write_time:
            Last write time for the file.
        :paramtype file_last_write_time:~datetime.datetime or str
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
            '{}://{}'.format(self.scheme, self.primary_hostname), self.share_name, new_file_path,
            credential=new_file_sas or self.credential, api_version=self.api_version,
            _hosts=self._hosts, _configuration=self._config, _pipeline=self._pipeline,
            _location_mode=self._location_mode
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
    async def get_file_properties(self, **kwargs):
        # type: (Any) -> FileProperties
        """Returns all user-defined metadata, standard HTTP properties, and
        system properties for the file.

        :keyword lease:
            Required if the file has an active lease. Value can be a ShareLeaseClient object
            or the lease ID as a string.

            .. versionadded:: 12.1.0

        :paramtype lease: ~azure.storage.fileshare.aio.ShareLeaseClient or str
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: FileProperties
        :rtype: ~azure.storage.fileshare.FileProperties
        """
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        timeout = kwargs.pop('timeout', None)
        try:
            file_props = await self._client.file.get_properties(
                sharesnapshot=self.snapshot,
                lease_access_conditions=access_conditions,
                timeout=timeout,
                cls=deserialize_file_properties,
                **kwargs
            )
        except HttpResponseError as error:
            process_storage_error(error)
        file_props.name = self.file_name
        file_props.share = self.share_name
        file_props.snapshot = self.snapshot
        file_props.path = "/".join(self.file_path)
        return file_props  # type: ignore

    @distributed_trace_async
    async def set_http_headers(self, content_settings,  # type: ContentSettings
                               file_attributes="preserve",  # type: Union[str, NTFSAttributes]
                               file_creation_time="preserve",  # type: Optional[Union[str, datetime]]
                               file_last_write_time="preserve",  # type: Optional[Union[str, datetime]]
                               file_permission=None,  # type: Optional[str]
                               permission_key=None,  # type: Optional[str]
                               **kwargs  # type: Any
                               ):
        # type: (...) -> Dict[str, Any]
        """Sets HTTP headers on the file.

        :param ~azure.storage.fileshare.ContentSettings content_settings:
            ContentSettings object used to set file properties. Used to set content type, encoding,
            language, disposition, md5, and cache control.
        :param file_attributes:
            The file system attributes for files and directories.
            If not set, indicates preservation of existing values.
            Here is an example for when the var type is str: 'Temporary|Archive'
        :type file_attributes: str or :class:`~azure.storage.fileshare.NTFSAttributes`
        :param file_creation_time: Creation time for the file
            Default value: Preserve.
        :type file_creation_time: str or ~datetime.datetime
        :param file_last_write_time: Last write time for the file
            Default value: Preserve.
        :type file_last_write_time: str or ~datetime.datetime
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
        :keyword lease:
            Required if the file has an active lease. Value can be a ShareLeaseClient object
            or the lease ID as a string.

            .. versionadded:: 12.1.0

        :paramtype lease: ~azure.storage.fileshare.aio.ShareLeaseClient or str
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: File-updated property dict (Etag and last modified).
        :rtype: dict(str, Any)
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
        file_permission = _get_file_permission(file_permission, permission_key, 'preserve')
        file_change_time = kwargs.pop('file_change_time', None)
        try:
            return await self._client.file.set_http_headers(  # type: ignore
                file_content_length=file_content_length,
                file_http_headers=file_http_headers,
                file_attributes=_str(file_attributes),
                file_creation_time=_datetime_to_str(file_creation_time),
                file_last_write_time=_datetime_to_str(file_last_write_time),
                file_change_time=_datetime_to_str(file_change_time),
                file_permission=file_permission,
                file_permission_key=permission_key,
                lease_access_conditions=access_conditions,
                timeout=timeout,
                cls=return_response_headers,
                **kwargs
            )
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def set_file_metadata(self, metadata=None, **kwargs):  # type: ignore
        # type: (Optional[Dict[str, Any]], Any) -> Dict[str, Any]
        """Sets user-defined metadata for the specified file as one or more
        name-value pairs.

        Each call to this operation replaces all existing metadata
        attached to the file. To remove all metadata from the file,
        call this operation with no metadata dict.

        :param metadata:
            Name-value pairs associated with the file as metadata.
        :type metadata: dict(str, str)
        :keyword lease:
            Required if the file has an active lease. Value can be a ShareLeaseClient object
            or the lease ID as a string.

            .. versionadded:: 12.1.0

        :paramtype lease: ~azure.storage.fileshare.aio.ShareLeaseClient or str
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: File-updated property dict (Etag and last modified).
        :rtype: dict(str, Any)
        """
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        timeout = kwargs.pop('timeout', None)
        headers = kwargs.pop("headers", {})
        headers.update(add_metadata_headers(metadata))  # type: ignore
        try:
            return await self._client.file.set_metadata(  # type: ignore
                metadata=metadata, lease_access_conditions=access_conditions,
                timeout=timeout, cls=return_response_headers, headers=headers, **kwargs
            )
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def upload_range(  # type: ignore
        self,
        data,  # type: bytes
        offset,  # type: int
        length,  # type: int
        **kwargs
    ):
        # type: (...) -> Dict[str, Any]
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
            The timeout parameter is expressed in seconds.
        :keyword str encoding:
            Defaults to UTF-8.
        :returns: File-updated property dict (Etag and last modified).
        :rtype: Dict[str, Any]
        """
        validate_content = kwargs.pop('validate_content', False)
        timeout = kwargs.pop('timeout', None)
        encoding = kwargs.pop('encoding', 'UTF-8')
        file_last_write_mode = kwargs.pop('file_last_write_mode', None)
        if isinstance(data, six.text_type):
            data = data.encode(encoding)
        end_range = offset + length - 1  # Reformat to an inclusive range index
        content_range = 'bytes={0}-{1}'.format(offset, end_range)
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        try:
            return await self._client.file.upload_range(  # type: ignore
                range=content_range,
                content_length=length,
                optionalbody=data,
                timeout=timeout,
                validate_content=validate_content,
                file_last_written_mode=file_last_write_mode,
                lease_access_conditions=access_conditions,
                cls=return_response_headers,
                **kwargs
            )
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def upload_range_from_url(self, source_url,
                                    offset,
                                    length,
                                    source_offset,
                                    **kwargs
                                    ):
        # type: (str, int, int, int, **Any) -> Dict[str, Any]
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
            The timeout parameter is expressed in seconds.
        :keyword str source_authorization:
            Authenticate as a service principal using a client secret to access a source blob. Ensure "bearer " is
            the prefix of the source_authorization string.
        """
        options = self._upload_range_from_url_options(
            source_url=source_url,
            offset=offset,
            length=length,
            source_offset=source_offset,
            **kwargs
        )
        try:
            return await self._client.file.upload_range_from_url(**options)  # type: ignore
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def get_ranges(  # type: ignore
            self, offset=None,  # type: Optional[int]
            length=None,  # type: Optional[int]
            **kwargs  # type: Any
        ):
        # type: (...) -> List[Dict[str, int]]
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
            The timeout parameter is expressed in seconds.
        :returns:
            A list of valid ranges.
        :rtype: List[dict[str, int]]
        """
        options = self._get_ranges_options(
            offset=offset,
            length=length,
            **kwargs)
        try:
            ranges = await self._client.file.get_range_list(**options)
        except HttpResponseError as error:
            process_storage_error(error)
        return [{'start': file_range.start, 'end': file_range.end} for file_range in ranges.ranges]

    @distributed_trace_async
    async def get_ranges_diff(  # type: ignore
            self,
            previous_sharesnapshot,  # type: Union[str, Dict[str, Any]]
            offset=None,  # type: Optional[int]
            length=None,  # type: Optional[int]
            **kwargs  # type: Any
            ):
        # type: (...) -> Tuple[List[Dict[str, int]], List[Dict[str, int]]]
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
        :keyword lease:
            Required if the file has an active lease. Value can be a ShareLeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.fileshare.ShareLeaseClient or str
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns:
            A tuple of two lists of file ranges as dictionaries with 'start' and 'end' keys.
            The first element are filled file ranges, the 2nd element is cleared file ranges.
        :rtype: tuple(list(dict(str, str), list(dict(str, str))
        """
        options = self._get_ranges_options(
            offset=offset,
            length=length,
            previous_sharesnapshot=previous_sharesnapshot,
            **kwargs)
        try:
            ranges = await self._client.file.get_range_list(**options)
        except HttpResponseError as error:
            process_storage_error(error)
        return get_file_ranges_result(ranges)

    @distributed_trace_async
    async def clear_range(  # type: ignore
        self,
        offset,  # type: int
        length,  # type: int
        **kwargs
    ):
        # type: (...) -> Dict[str, Any]
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
            The timeout parameter is expressed in seconds.
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
        content_range = "bytes={0}-{1}".format(offset, end_range)
        try:
            return await self._client.file.upload_range(  # type: ignore
                timeout=timeout,
                cls=return_response_headers,
                content_length=0,
                optionalbody=None,
                file_range_write="clear",
                range=content_range,
                lease_access_conditions=access_conditions,
                **kwargs
            )
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def resize_file(self, size, **kwargs):
        # type: (int, Any) -> Dict[str, Any]
        """Resizes a file to the specified size.

        :param int size:
            Size to resize file to (in bytes)
        :keyword lease:
            Required if the file has an active lease. Value can be a ShareLeaseClient object
            or the lease ID as a string.

            .. versionadded:: 12.1.0

        :paramtype lease: ~azure.storage.fileshare.aio.ShareLeaseClient or str
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: File-updated property dict (Etag and last modified).
        :rtype: Dict[str, Any]
        """
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        timeout = kwargs.pop('timeout', None)
        try:
            return await self._client.file.set_http_headers(  # type: ignore
                file_content_length=size,
                file_attributes="preserve",
                file_creation_time="preserve",
                file_last_write_time="preserve",
                file_permission="preserve",
                lease_access_conditions=access_conditions,
                cls=return_response_headers,
                timeout=timeout,
                **kwargs
            )
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace
    def list_handles(self, **kwargs):
        # type: (Any) -> AsyncItemPaged
        """Lists handles for file.

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: An auto-paging iterable of HandleItem
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.storage.fileshare.HandleItem]
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
    async def close_handle(self, handle, **kwargs):
        # type: (Union[str, HandleItem], Any) -> Dict[str, int]
        """Close an open file handle.

        :param handle:
            A specific handle to close.
        :type handle: str or ~azure.storage.fileshare.Handle
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns:
            The number of handles closed (this may be 0 if the specified handle was not found)
            and the number of handles failed to close in a dict.
        :rtype: dict[str, int]
        """
        try:
            handle_id = handle.id # type: ignore
        except AttributeError:
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
    async def close_all_handles(self, **kwargs):
        # type: (Any) -> Dict[str, int]
        """Close any open file handles.

        This operation will block until the service has closed all open handles.

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
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
