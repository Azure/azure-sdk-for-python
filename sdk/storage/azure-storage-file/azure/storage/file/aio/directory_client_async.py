# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import functools
import time
from typing import ( # pylint: disable=unused-import
    Optional, Union, Any, Dict, TYPE_CHECKING
)

from azure.core.async_paging import AsyncItemPaged
from azure.core.pipeline import AsyncPipeline
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async
from .._parser import _get_file_permission, _datetime_to_str
from .._shared.parser import _str

from .._generated.aio import AzureFileStorage
from .._generated.version import VERSION
from .._generated.models import StorageErrorException
from .._shared.base_client_async import AsyncStorageAccountHostsMixin, AsyncTransportWrapper
from .._shared.policies_async import ExponentialRetry
from .._shared.request_handlers import add_metadata_headers
from .._shared.response_handlers import return_response_headers, process_storage_error
from .._deserialize import deserialize_directory_properties
from ..directory_client import DirectoryClient as DirectoryClientBase
from .file_client_async import FileClient
from .models import DirectoryPropertiesPaged, HandlesPaged

if TYPE_CHECKING:
    from ..models import ShareProperties, DirectoryProperties, ContentSettings, NTFSAttributes
    from .._generated.models import HandleItem


class DirectoryClient(AsyncStorageAccountHostsMixin, DirectoryClientBase):
    """A client to interact with a specific directory, although it may not yet exist.

    For operations relating to a specific subdirectory or file in this share, the clients for those
    entities can also be retrieved using the `get_subdirectory_client` and `get_file_client` functions.s

    :ivar str url:
        The full endpoint URL to the Directory, including SAS token if used. This could be
        either the primary endpoint, or the secondard endpoint depending on the current `location_mode`.
    :ivar str primary_endpoint:
        The full primary endpoint URL.
    :ivar str primary_hostname:
        The hostname of the primary endpoint.
    :ivar str secondary_endpoint:
        The full secondard endpoint URL if configured. If not available
        a ValueError will be raised. To explicitly specify a secondary hostname, use the optional
        `secondary_hostname` keyword argument on instantiation.
    :ivar str secondary_hostname:
        The hostname of the secondary endpoint. If not available this
        will be None. To explicitly specify a secondary hostname, use the optional
        `secondary_hostname` keyword argument on instantiation.
    :ivar str location_mode:
        The location mode that the client is currently using. By default
        this will be "primary". Options include "primary" and "secondary".
    :param str account_url:
        The URI to the storage account. In order to create a client given the full URI to the
        directory, use the from_directory_url classmethod.
    :param share_name:
        The name of the share for the directory.
    :type share_name: str
    :param str directory_path:
        The directory path for the directory with which to interact.
        If specified, this value will override a directory value specified in the directory URL.
    :param str snapshot:
        An optional share snapshot on which to operate.
    :param credential:
        The credential with which to authenticate. This is optional if the
        account URL already has a SAS token. The value can be a SAS token string or an account
        shared access key.
    :keyword loop:
        The event loop to run the asynchronous tasks.
    """
    def __init__( # type: ignore
            self, account_url,  # type: str
            share_name, # type: str
            directory_path, # type: str
            snapshot=None,  # type: Optional[Union[str, Dict[str, Any]]]
            credential=None, # type: Optional[Any]
            **kwargs # type: Optional[Any]
        ):
        # type: (...) -> None
        kwargs['retry_policy'] = kwargs.get('retry_policy') or ExponentialRetry(**kwargs)
        loop = kwargs.pop('loop', None)
        super(DirectoryClient, self).__init__(
            account_url,
            share_name=share_name,
            directory_path=directory_path,
            snapshot=snapshot,
            credential=credential,
            loop=loop,
            **kwargs)
        self._client = AzureFileStorage(version=VERSION, url=self.url, pipeline=self._pipeline, loop=loop)
        self._loop = loop

    def get_file_client(self, file_name, **kwargs):
        # type: (str, Any) -> FileClient
        """Get a client to interact with a specific file.

        The file need not already exist.

        :param file_name:
            The name of the file.
        :returns: A File Client.
        :rtype: ~azure.storage.file.FileClient
        """
        if self.directory_path:
            file_name = self.directory_path.rstrip('/') + "/" + file_name

        _pipeline = AsyncPipeline(
            transport=AsyncTransportWrapper(self._pipeline._transport), # pylint: disable = protected-access
            policies=self._pipeline._impl_policies # pylint: disable = protected-access
        )
        return FileClient(
            self.url, file_path=file_name, share_name=self.share_name, snapshot=self.snapshot,
            credential=self.credential, _hosts=self._hosts, _configuration=self._config,
            _pipeline=_pipeline, _location_mode=self._location_mode, loop=self._loop, **kwargs)

    def get_subdirectory_client(self, directory_name, **kwargs):
        # type: (str, Any) -> DirectoryClient
        """Get a client to interact with a specific subdirectory.

        The subdirectory need not already exist.

        :param str directory_name:
            The name of the subdirectory.
        :returns: A Directory Client.
        :rtype: ~azure.storage.file.aio.DirectoryClient

        .. admonition:: Example:

            .. literalinclude:: ../tests/test_file_samples_directory_async.py
                :start-after: [START get_subdirectory_client]
                :end-before: [END get_subdirectory_client]
                :language: python
                :dedent: 12
                :caption: Gets the subdirectory client.
        """
        directory_path = self.directory_path.rstrip('/') + "/" + directory_name

        _pipeline = AsyncPipeline(
            transport=AsyncTransportWrapper(self._pipeline._transport), # pylint: disable = protected-access
            policies=self._pipeline._impl_policies # pylint: disable = protected-access
        )
        return DirectoryClient(
            self.url, share_name=self.share_name, directory_path=directory_path, snapshot=self.snapshot,
            credential=self.credential, _hosts=self._hosts, _configuration=self._config,
            _pipeline=_pipeline, _location_mode=self._location_mode, loop=self._loop, **kwargs)

    @distributed_trace_async
    async def create_directory(self, **kwargs): # type: ignore
        # type: (Any) -> Dict[str, Any]
        """Creates a new directory under the directory referenced by the client.

        :keyword metadata:
            Name-value pairs associated with the directory as metadata.
        :type metadata: dict(str, str)
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: Directory-updated property dict (Etag and last modified).
        :rtype: dict(str, Any)

        .. admonition:: Example:

            .. literalinclude:: ../tests/test_file_samples_directory_async.py
                :start-after: [START create_directory]
                :end-before: [END create_directory]
                :language: python
                :dedent: 12
                :caption: Creates a directory.
        """
        metadata = kwargs.pop('metadata', None)
        timeout = kwargs.pop('timeout', None)
        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata)) # type: ignore
        try:
            return await self._client.directory.create( # type: ignore
                timeout=timeout,
                cls=return_response_headers,
                headers=headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace_async
    async def delete_directory(self, **kwargs):
        # type: (**Any) -> None
        """Marks the directory for deletion. The directory is
        later deleted during garbage collection.

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None

        .. admonition:: Example:

            .. literalinclude:: ../tests/test_file_samples_directory_async.py
                :start-after: [START delete_directory]
                :end-before: [END delete_directory]
                :language: python
                :dedent: 12
                :caption: Deletes a directory.
        """
        timeout = kwargs.pop('timeout', None)
        try:
            await self._client.directory.delete(timeout=timeout, **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace
    def list_directories_and_files(self, name_starts_with=None, **kwargs):
        # type: (Optional[str], Any) -> AsyncItemPaged
        """Lists all the directories and files under the directory.

        :param str name_starts_with:
            Filters the results to return only entities whose names
            begin with the specified prefix.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: An auto-paging iterable of dict-like DirectoryProperties and FileProperties
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.storage.file.DirectoryProperties]

        .. admonition:: Example:

            .. literalinclude:: ../tests/test_file_samples_directory_async.py
                :start-after: [START lists_directory]
                :end-before: [END lists_directory]
                :language: python
                :dedent: 12
                :caption: List directories and files.
        """
        timeout = kwargs.pop('timeout', None)
        results_per_page = kwargs.pop('results_per_page', None)
        command = functools.partial(
            self._client.directory.list_files_and_directories_segment,
            sharesnapshot=self.snapshot,
            timeout=timeout,
            **kwargs)
        return AsyncItemPaged(
            command, prefix=name_starts_with, results_per_page=results_per_page,
            page_iterator_class=DirectoryPropertiesPaged)

    @distributed_trace
    def list_handles(self, recursive=False, **kwargs):
        # type: (bool, Any) -> AsyncItemPaged
        """Lists opened handles on a directory or a file under the directory.

        :param bool recursive:
            Boolean that specifies if operation should apply to the directory specified by the client,
            its files, its subdirectories and their files. Default value is False.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: An auto-paging iterable of HandleItem
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.storage.file.HandleItem]
        """
        timeout = kwargs.pop('timeout', None)
        results_per_page = kwargs.pop('results_per_page', None)
        command = functools.partial(
            self._client.directory.list_handles,
            sharesnapshot=self.snapshot,
            timeout=timeout,
            recursive=recursive,
            **kwargs)
        return AsyncItemPaged(
            command, results_per_page=results_per_page,
            page_iterator_class=HandlesPaged)

    @distributed_trace_async
    async def close_handle(self, handle, **kwargs):
        # type: (Union[str, HandleItem], Any) -> int
        """Close an open file handle.

        :param handle:
            A specific handle to close.
        :type handle: str or ~azure.storage.file.Handle
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns:
            The total number of handles closed. This could be 0 if the supplied
            handle was not found.
        :rtype: int
        """
        try:
            handle_id = handle.id # type: ignore
        except AttributeError:
            handle_id = handle
        if handle_id == '*':
            raise ValueError("Handle ID '*' is not supported. Use 'close_all_handles' instead.")
        try:
            response = await self._client.directory.force_close_handles(
                handle_id,
                marker=None,
                recursive=None,
                sharesnapshot=self.snapshot,
                cls=return_response_headers,
                **kwargs
            )
            return response.get('number_of_handles_closed', 0)
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace_async
    async def close_all_handles(self, recursive=False, **kwargs):
        # type: (bool, Any) -> int
        """Close any open file handles.

        This operation will block until the service has closed all open handles.

        :param bool recursive:
            Boolean that specifies if operation should apply to the directory specified by the client,
            its files, its subdirectories and their files. Default value is False.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: The total number of handles closed.
        :rtype: int
        """
        timeout = kwargs.pop('timeout', None)
        start_time = time.time()

        try_close = True
        continuation_token = None
        total_handles = 0
        while try_close:
            try:
                response = await self._client.directory.force_close_handles(
                    handle_id='*',
                    timeout=timeout,
                    marker=continuation_token,
                    recursive=recursive,
                    sharesnapshot=self.snapshot,
                    cls=return_response_headers,
                    **kwargs
                )
            except StorageErrorException as error:
                process_storage_error(error)
            continuation_token = response.get('marker')
            try_close = bool(continuation_token)
            total_handles += response.get('number_of_handles_closed', 0)
            if timeout:
                timeout = max(0, timeout - (time.time() - start_time))
        return total_handles

    @distributed_trace_async
    async def get_directory_properties(self, **kwargs):
        # type: (Any) -> DirectoryProperties
        """Returns all user-defined metadata and system properties for the
        specified directory. The data returned does not include the directory's
        list of files.

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: DirectoryProperties
        :rtype: ~azure.storage.file.DirectoryProperties
        """
        timeout = kwargs.pop('timeout', None)
        try:
            response = await self._client.directory.get_properties(
                timeout=timeout,
                cls=deserialize_directory_properties,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)
        return response # type: ignore

    @distributed_trace_async
    async def set_directory_metadata(self, metadata, **kwargs): # type: ignore
        # type: (Dict[str, Any], Any) ->  Dict[str, Any]
        """Sets the metadata for the directory.

        Each call to this operation replaces all existing metadata
        attached to the directory. To remove all metadata from the directory,
        call this operation with an empty metadata dict.

        :param metadata:
            Name-value pairs associated with the directory as metadata.
        :type metadata: dict(str, str)
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: Directory-updated property dict (Etag and last modified).
        :rtype: dict(str, Any)
        """
        timeout = kwargs.pop('timeout', None)
        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata))
        try:
            return await self._client.directory.set_metadata( # type: ignore
                timeout=timeout,
                cls=return_response_headers,
                headers=headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace_async
    async def set_http_headers(self, file_attributes="none",  # type: Union[str, NTFSAttributes]
                               file_creation_time="preserve",  # type: Union[str, datetime]
                               file_last_write_time="preserve",  # type: Union[str, datetime]
                               file_permission=None,  # type: Optional[str]
                               permission_key=None,  # type: Optional[str]
                               **kwargs):  # type: ignore
        # type: (...) -> Dict[str, Any]
        """Sets HTTP headers on the directory.

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :param file_attributes:
            The file system attributes for files and directories.
            If not set, indicates preservation of existing values.
            Here is an example for when the var type is str: 'Temporary|Archive'
        :type file_attributes: str or :class:`~azure.storage.file.NTFSAttributes`
        :param file_creation_time: Creation time for the file
            Default value: Now.
        :type file_creation_time: str or datetime
        :param file_last_write_time: Last write time for the file
            Default value: Now.
        :type file_last_write_time: str or datetime
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
        :returns: File-updated property dict (Etag and last modified).
        :rtype: dict(str, Any)
        """
        timeout = kwargs.pop('timeout', None)
        file_permission = _get_file_permission(file_permission, permission_key, 'preserve')
        try:
            return await self._client.directory.set_properties(  # type: ignore
                file_attributes=_str(file_attributes),
                file_creation_time=_datetime_to_str(file_creation_time),
                file_last_write_time=_datetime_to_str(file_last_write_time),
                file_permission=file_permission,
                file_permission_key=permission_key,
                timeout=timeout,
                cls=return_response_headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace_async
    async def create_subdirectory(
            self, directory_name,  # type: str
            **kwargs
        ):
        # type: (...) -> DirectoryClient
        """Creates a new subdirectory and returns a client to interact
        with the subdirectory.

        :param str directory_name:
            The name of the subdirectory.
        :keyword metadata:
            Name-value pairs associated with the subdirectory as metadata.
        :type metadata: dict(str, str)
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: DirectoryClient
        :rtype: ~azure.storage.file.aio.directory_client_async.DirectoryClient

        .. admonition:: Example:

            .. literalinclude:: ../tests/test_file_samples_directory_async.py
                :start-after: [START create_subdirectory]
                :end-before: [END create_subdirectory]
                :language: python
                :dedent: 12
                :caption: Create a subdirectory.
        """
        metadata = kwargs.pop('metadata', None)
        timeout = kwargs.pop('timeout', None)
        subdir = self.get_subdirectory_client(directory_name)
        await subdir.create_directory(metadata=metadata, timeout=timeout, **kwargs)
        return subdir # type: ignore

    @distributed_trace_async
    async def delete_subdirectory(
            self, directory_name,  # type: str
            **kwargs
        ):
        # type: (...) -> None
        """Deletes a subdirectory.

        :param str directory_name:
            The name of the subdirectory.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None

        .. admonition:: Example:

            .. literalinclude:: ../tests/test_file_samples_directory_async.py
                :start-after: [START delete_subdirectory]
                :end-before: [END delete_subdirectory]
                :language: python
                :dedent: 12
                :caption: Delete a subdirectory.
        """
        timeout = kwargs.pop('timeout', None)
        subdir = self.get_subdirectory_client(directory_name)
        await subdir.delete_directory(timeout=timeout, **kwargs)

    @distributed_trace_async
    async def upload_file(
            self, file_name,  # type: str
            data, # type: Any
            length=None, # type: Optional[int]
            **kwargs # type: Any
        ):
        # type: (...) -> FileClient
        """Creates a new file in the directory and returns a FileClient
        to interact with the file.

        :param str file_name:
            The name of the file.
        :param Any data:
            Content of the file.
        :param int length:
            Length of the file in bytes. Specify its maximum size, up to 1 TiB.
        :keyword metadata:
            Name-value pairs associated with the file as metadata.
        :type metadata: dict(str, str)
        :keyword ~azure.storage.file.ContentSettings content_settings:
            ContentSettings object used to set file properties.
        :keyword bool validate_content:
            If true, calculates an MD5 hash for each range of the file. The storage
            service checks the hash of the content that has arrived with the hash
            that was sent. This is primarily valuable for detecting bitflips on
            the wire if using http instead of https as https (the default) will
            already validate. Note that this MD5 hash is not stored with the
            file.
        :keyword int max_concurrency:
            Maximum number of parallel connections to use.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :keyword str encoding:
            Defaults to UTF-8.
        :returns: FileClient
        :rtype: ~azure.storage.file.aio.file_client_async.FileClient

        .. admonition:: Example:

            .. literalinclude:: ../tests/test_file_samples_directory_async.py
                :start-after: [START upload_file_to_directory]
                :end-before: [END upload_file_to_directory]
                :language: python
                :dedent: 12
                :caption: Upload a file to a directory.
        """
        file_client = self.get_file_client(file_name)
        await file_client.upload_file(
            data,
            length=length,
            **kwargs)
        return file_client # type: ignore

    @distributed_trace_async
    async def delete_file(
            self, file_name,  # type: str
            **kwargs  # type: Optional[Any]
        ):
        # type: (...) -> None
        """Marks the specified file for deletion. The file is later
        deleted during garbage collection.

        :param str file_name:
            The name of the file to delete.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None

        .. admonition:: Example:

            .. literalinclude:: ../tests/test_file_samples_directory_async.py
                :start-after: [START delete_file_in_directory]
                :end-before: [END delete_file_in_directory]
                :language: python
                :dedent: 12
                :caption: Delete a file in a directory.
        """
        file_client = self.get_file_client(file_name)
        await file_client.delete_file(**kwargs)
