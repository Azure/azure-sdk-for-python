# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import functools
from typing import ( # pylint: disable=unused-import
    Optional, Union, Any, Dict, TYPE_CHECKING
)
try:
    from urllib.parse import urlparse, quote, unquote
except ImportError:
    from urlparse import urlparse # type: ignore
    from urllib2 import quote, unquote # type: ignore

import six
from azure.core.polling import LROPoller
from azure.core.paging import ItemPaged
from azure.core.tracing.decorator import distributed_trace

from ._generated import AzureFileStorage
from ._generated.version import VERSION
from ._generated.models import StorageErrorException
from ._shared.base_client import StorageAccountHostsMixin, parse_connection_str, parse_query
from ._shared.request_handlers import add_metadata_headers
from ._shared.response_handlers import return_response_headers, process_storage_error
from ._deserialize import deserialize_directory_properties
from ._polling import CloseHandles
from .file_client import FileClient
from .models import DirectoryPropertiesPaged, HandlesPaged

if TYPE_CHECKING:
    from .models import SharePermissions, ShareProperties, DirectoryProperties, ContentSettings
    from ._generated.models import HandleItem

class DirectoryClient(StorageAccountHostsMixin):
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
    :param str directory_url:
        The full URI to the directory. This can also be a URL to the storage account
        or share, in which case the directory and/or share must also be specified.
    :param share: The share for the directory. If specified, this value will override
        a share value specified in the directory URL.
    :type share: str or ~azure.storage.file.models.ShareProperties
    :param str directory_path:
        The directory path for the directory with which to interact.
        If specified, this value will override a directory value specified in the directory URL.
    :param str snapshot:
        An optional share snapshot on which to operate.
    :param credential:
        The credential with which to authenticate. This is optional if the
        account URL already has a SAS token. The value can be a SAS token string or an account
        shared access key.
    """
    def __init__( # type: ignore
            self, directory_url,  # type: str
            share=None, # type: Optional[Union[str, ShareProperties]]
            directory_path=None, # type: Optional[str]
            snapshot=None,  # type: Optional[Union[str, Dict[str, Any]]]
            credential=None, # type: Optional[Any]
            **kwargs # type: Optional[Any]
        ):
        # type: (...) -> None
        try:
            if not directory_url.lower().startswith('http'):
                directory_url = "https://" + directory_url
        except AttributeError:
            raise ValueError("Share URL must be a string.")
        parsed_url = urlparse(directory_url.rstrip('/'))
        if not parsed_url.path and not share:
            raise ValueError("Please specify a share name.")
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(directory_url))
        if hasattr(credential, 'get_token'):
            raise ValueError("Token credentials not supported by the File service.")

        share, path_dir = "", ""
        if parsed_url.path:
            share, _, path_dir = parsed_url.path.lstrip('/').partition('/')
        path_snapshot, sas_token = parse_query(parsed_url.query)
        if not sas_token and not credential:
            raise ValueError(
                'You need to provide either an account key or SAS token when creating a storage service.')
        try:
            self.snapshot = snapshot.snapshot # type: ignore
        except AttributeError:
            try:
                self.snapshot = snapshot['snapshot'] # type: ignore
            except TypeError:
                self.snapshot = snapshot or path_snapshot
        try:
            self.share_name = share.name # type: ignore
        except AttributeError:
            self.share_name = share or unquote(share)
        self.directory_path = directory_path or path_dir

        self._query_str, credential = self._format_query_string(
            sas_token, credential, share_snapshot=self.snapshot)
        super(DirectoryClient, self).__init__(parsed_url, 'file', credential, **kwargs)
        self._client = AzureFileStorage(version=VERSION, url=self.url, pipeline=self._pipeline)

    def _format_url(self, hostname):
        """Format the endpoint URL according to the current location
        mode hostname.
        """
        share_name = self.share_name
        if isinstance(share_name, six.text_type):
            share_name = share_name.encode('UTF-8')
        directory_path = ""
        if self.directory_path:
            directory_path = "/" + quote(self.directory_path, safe='~')
        return "{}://{}/{}{}{}".format(
            self.scheme,
            hostname,
            quote(share_name),
            directory_path,
            self._query_str)

    @classmethod
    def from_connection_string(
            cls, conn_str,  # type: str
            share=None, # type: Optional[Union[str, ShareProperties]]
            directory_path=None, # type: Optional[str]
            credential=None, # type: Optional[Any]
            **kwargs # type: Any
        ):
        # type: (...) -> DirectoryClient
        """Create DirectoryClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Storage account.
        :param share: The share. This can either be the name of the share,
            or an instance of ShareProperties
        :type share: str or ~azure.storage.file.models.ShareProperties
        :param str directory_path:
            The directory path.
        :param credential:
            The credential with which to authenticate. This is optional if the
            account URL already has a SAS token. The value can be a SAS token string or an account
            shared access key.
        """
        account_url, secondary, credential = parse_connection_str(conn_str, credential, 'file')
        if 'secondary_hostname' not in kwargs:
            kwargs['secondary_hostname'] = secondary
        return cls(
            account_url, share=share, directory_path=directory_path, credential=credential, **kwargs)

    def get_file_client(self, file_name, **kwargs):
        """Get a client to interact with a specific file.

        The file need not already exist.

        :param file_name:
            The name of the file.
        :returns: A File Client.
        :rtype: ~azure.storage.file.file_client.FileClient
        """
        if self.directory_path:
            file_name = self.directory_path.rstrip('/') + "/" + file_name
        return FileClient(
            self.url, file_path=file_name, snapshot=self.snapshot, credential=self.credential,
            _hosts=self._hosts, _configuration=self._config, _pipeline=self._pipeline,
            _location_mode=self._location_mode, **kwargs)

    def get_subdirectory_client(self, directory_name, **kwargs):
        """Get a client to interact with a specific subdirectory.

        The subdirectory need not already exist.

        :param str directory_name:
            The name of the subdirectory.
        :returns: A Directory Client.
        :rtype: ~azure.storage.file.directory_client.DirectoryClient

        Example:
            .. literalinclude:: ../tests/test_file_samples_directory.py
                :start-after: [START get_subdirectory_client]
                :end-before: [END get_subdirectory_client]
                :language: python
                :dedent: 12
                :caption: Gets the subdirectory client.
        """
        directory_path = self.directory_path.rstrip('/') + "/" + directory_name
        return DirectoryClient(
            self.url, directory_path=directory_path, snapshot=self.snapshot, credential=self.credential,
            _hosts=self._hosts, _configuration=self._config, _pipeline=self._pipeline,
            _location_mode=self._location_mode, **kwargs)

    @distributed_trace
    def create_directory( # type: ignore
            self, metadata=None,  # type: Optional[Dict[str, str]]
            timeout=None, # type: Optional[int]
            **kwargs # type: Optional[Any]
        ):
        # type: (...) -> Dict[str, Any]
        """Creates a new directory under the directory referenced by the client.

        :param metadata:
            Name-value pairs associated with the directory as metadata.
        :type metadata: dict(str, str)
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: Directory-updated property dict (Etag and last modified).
        :rtype: dict(str, Any)

        Example:
            .. literalinclude:: ../tests/test_file_samples_directory.py
                :start-after: [START create_directory]
                :end-before: [END create_directory]
                :language: python
                :dedent: 12
                :caption: Creates a directory.
        """
        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata)) # type: ignore
        try:
            return self._client.directory.create( # type: ignore
                timeout=timeout,
                cls=return_response_headers,
                headers=headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace
    def delete_directory(self, timeout=None, **kwargs):
        # type: (Optional[int], **Any) -> None
        """Marks the directory for deletion. The directory is
        later deleted during garbage collection.

        :param int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None

        Example:
            .. literalinclude:: ../tests/test_file_samples_directory.py
                :start-after: [START delete_directory]
                :end-before: [END delete_directory]
                :language: python
                :dedent: 12
                :caption: Deletes a directory.
        """
        try:
            self._client.directory.delete(timeout=timeout, **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace
    def list_directories_and_files(self, name_starts_with=None, timeout=None, **kwargs):
        # type: (Optional[str], Optional[int], **Any) -> ItemPaged
        """Lists all the directories and files under the directory.

        :param str name_starts_with:
            Filters the results to return only entities whose names
            begin with the specified prefix.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: An auto-paging iterable of dict-like DirectoryProperties and FileProperties
        :rtype: ~azure.core.paging.ItemPaged[~azure.storage.file.models.DirectoryProperties]

        Example:
            .. literalinclude:: ../tests/test_file_samples_directory.py
                :start-after: [START lists_directory]
                :end-before: [END lists_directory]
                :language: python
                :dedent: 12
                :caption: List directories and files.
        """
        results_per_page = kwargs.pop('results_per_page', None)
        command = functools.partial(
            self._client.directory.list_files_and_directories_segment,
            sharesnapshot=self.snapshot,
            timeout=timeout,
            **kwargs)
        return ItemPaged(
            command, prefix=name_starts_with, results_per_page=results_per_page,
            page_iterator_class=DirectoryPropertiesPaged)

    @distributed_trace
    def list_handles(self, recursive=False, timeout=None, **kwargs):
        """Lists opened handles on a directory or a file under the directory.

        :param bool recursive:
            Boolean that specifies if operation should apply to the directory specified by the client,
            its files, its subdirectories and their files. Default value is False.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: An auto-paging iterable of HandleItems
        :rtype: ~azure.core.paging.ItemPaged[~azure.storage.file.models.Handles]
        """
        results_per_page = kwargs.pop('results_per_page', None)
        command = functools.partial(
            self._client.directory.list_handles,
            sharesnapshot=self.snapshot,
            timeout=timeout,
            recursive=recursive,
            **kwargs)
        return ItemPaged(
            command, results_per_page=results_per_page,
            page_iterator_class=HandlesPaged)

    @distributed_trace
    def close_handles(
            self, handle=None, # type: Union[str, HandleItem]
            recursive=False,  # type: bool
            timeout=None, # type: Optional[int]
            **kwargs # type: Any
        ):
        # type: (...) -> Any
        """Close open file handles.

        This operation may not finish with a single call, so a long-running poller
        is returned that can be used to wait until the operation is complete.

        :param handle:
            Optionally, a specific handle to close. The default value is '*'
            which will attempt to close all open handles.
        :type handle: str or ~azure.storage.file.models.Handle
        :param bool recursive:
            Boolean that specifies if operation should apply to the directory specified by the client,
            its files, its subdirectories and their files. Default value is False.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: A long-running poller to get operation status.
        :rtype: ~azure.core.polling.LROPoller
        """
        try:
            handle_id = handle.id # type: ignore
        except AttributeError:
            handle_id = handle or '*'
        command = functools.partial(
            self._client.directory.force_close_handles,
            handle_id,
            timeout=timeout,
            sharesnapshot=self.snapshot,
            recursive=recursive,
            cls=return_response_headers,
            **kwargs)
        try:
            start_close = command()
        except StorageErrorException as error:
            process_storage_error(error)

        polling_method = CloseHandles(self._config.copy_polling_interval)
        return LROPoller(
            command,
            start_close,
            None,
            polling_method)

    @distributed_trace
    def get_directory_properties(self, timeout=None, **kwargs):
        # type: (Optional[int], Any) -> DirectoryProperties
        """Returns all user-defined metadata and system properties for the
        specified directory. The data returned does not include the directory's
        list of files.

        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: DirectoryProperties
        :rtype: ~azure.storage.file.models.DirectoryProperties
        """
        try:
            response = self._client.directory.get_properties(
                timeout=timeout,
                cls=deserialize_directory_properties,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)
        return response # type: ignore

    @distributed_trace
    def set_directory_metadata(self, metadata, timeout=None, **kwargs): # type: ignore
        # type: (Dict[str, Any], Optional[int], Any) ->  Dict[str, Any]
        """Sets the metadata for the directory.

        Each call to this operation replaces all existing metadata
        attached to the directory. To remove all metadata from the directory,
        call this operation with an empty metadata dict.

        :param metadata:
            Name-value pairs associated with the directory as metadata.
        :type metadata: dict(str, str)
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: Directory-updated property dict (Etag and last modified).
        :rtype: dict(str, Any)
        """
        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata))
        try:
            return self._client.directory.set_metadata( # type: ignore
                timeout=timeout,
                cls=return_response_headers,
                headers=headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace
    def create_subdirectory(
            self, directory_name,  # type: str
            metadata=None, #type: Optional[Dict[str, Any]]
            timeout=None, # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> DirectoryClient
        """Creates a new subdirectory and returns a client to interact
        with the subdirectory.

        :param str directory_name:
            The name of the subdirectory.
        :param metadata:
            Name-value pairs associated with the subdirectory as metadata.
        :type metadata: dict(str, str)
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: DirectoryClient
        :rtype: ~azure.storage.file.directory_client.DirectoryClient

        Example:
            .. literalinclude:: ../tests/test_file_samples_directory.py
                :start-after: [START create_subdirectory]
                :end-before: [END create_subdirectory]
                :language: python
                :dedent: 12
                :caption: Create a subdirectory.
        """
        subdir = self.get_subdirectory_client(directory_name)
        subdir.create_directory(metadata=metadata, timeout=timeout, **kwargs)
        return subdir # type: ignore

    @distributed_trace
    def delete_subdirectory(
            self, directory_name,  # type: str
            timeout=None, # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> None
        """Deletes a subdirectory.

        :param str directory_name:
            The name of the subdirectory.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None

        Example:
            .. literalinclude:: ../tests/test_file_samples_directory.py
                :start-after: [START delete_subdirectory]
                :end-before: [END delete_subdirectory]
                :language: python
                :dedent: 12
                :caption: Delete a subdirectory.
        """
        subdir = self.get_subdirectory_client(directory_name)
        subdir.delete_directory(timeout=timeout, **kwargs)

    @distributed_trace
    def upload_file(
            self, file_name,  # type: str
            data, # type: Any
            length=None, # type: Optional[int]
            metadata=None,  # type: Optional[Dict[str, str]]
            content_settings=None, # type: Optional[ContentSettings]
            validate_content=False,  # type: bool
            max_connections=1,  # type: Optional[int]
            timeout=None, # type: Optional[int]
            encoding='UTF-8',  # type: str
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
        :param metadata:
            Name-value pairs associated with the file as metadata.
        :type metadata: dict(str, str)
        :param ~azure.storage.file.models.ContentSettings content_settings:
            ContentSettings object used to set file properties.
        :param bool validate_content:
            If true, calculates an MD5 hash for each range of the file. The storage
            service checks the hash of the content that has arrived with the hash
            that was sent. This is primarily valuable for detecting bitflips on
            the wire if using http instead of https as https (the default) will
            already validate. Note that this MD5 hash is not stored with the
            file.
        :param int max_connections:
            Maximum number of parallel connections to use.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :param str encoding:
            Defaults to UTF-8.
        :returns: FileClient
        :rtype: ~azure.storage.file.file_client.FileClient

        Example:
            .. literalinclude:: ../tests/test_file_samples_directory.py
                :start-after: [START upload_file_to_directory]
                :end-before: [END upload_file_to_directory]
                :language: python
                :dedent: 12
                :caption: Upload a file to a directory.
        """
        file_client = self.get_file_client(file_name)
        file_client.upload_file(
            data,
            length=length,
            metadata=metadata,
            content_settings=content_settings,
            validate_content=validate_content,
            max_connections=max_connections,
            timeout=timeout,
            encoding=encoding,
            **kwargs)
        return file_client # type: ignore

    @distributed_trace
    def delete_file(
            self, file_name,  # type: str
            timeout=None,  # type: Optional[int]
            **kwargs  # type: Optional[Any]
        ):
        # type: (...) -> None
        """Marks the specified file for deletion. The file is later
        deleted during garbage collection.

        :param str file_name:
            The name of the file to delete.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None

        Example:
            .. literalinclude:: ../tests/test_file_samples_directory.py
                :start-after: [START delete_file_in_directory]
                :end-before: [END delete_file_in_directory]
                :language: python
                :dedent: 12
                :caption: Delete a file in a directory.
        """
        file_client = self.get_file_client(file_name)
        file_client.delete_file(timeout, **kwargs)
