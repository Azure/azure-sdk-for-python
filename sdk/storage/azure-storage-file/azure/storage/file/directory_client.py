# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import functools

try:
    from urllib.parse import urlparse, quote, unquote
except ImportError:
    from urlparse import urlparse
    from urllib2 import quote, unquote

import six
from azure.core.polling import LROPoller

from .file_client import FileClient

from .models import DirectoryPropertiesPaged, HandlesPaged
from ._generated import AzureFileStorage
from ._generated.version import VERSION
from ._generated.models import StorageErrorException, SignedIdentifier
from ._shared.utils import (
    StorageAccountHostsMixin,
    serialize_iso,
    return_headers_and_deserialized,
    parse_query,
    return_response_headers,
    add_metadata_headers,
    process_storage_error,
    parse_connection_str)

from ._share_utils import deserialize_directory_properties
from .polling import CloseHandles


class DirectoryClient(StorageAccountHostsMixin):
    """
    A client to interact with the sirectory.
    """

    def __init__(
            self, directory_url,  # type: str
            share=None, # type: Optional[Union[str, ShareProperties]]
            directory_path=None, # type: Optional[str]
            snapshot=None,  # type: Optional[Union[str, Dict[str, Any]]]
            credential=None, # type: Optional[Any]
            **kwargs # type: Optional[Any]
        ):
        # type: (...) -> DirectoryClient
        """Creates a new DirectoryClient. This client represents interaction with a specific
        directory, although it may not yet exist.
        :param share: The directory with which to interact. If specified, this value will override
         a directory value specified in the directory URL.
        :type share: str or ~azure.storage.file.models.DirectoryProperties
        :param str directory: The full URI to the directory.
        :param credential:
        """
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
            self.snapshot = snapshot.snapshot
        except AttributeError:
            try:
                self.snapshot = snapshot['snapshot']
            except TypeError:
                self.snapshot = snapshot or path_snapshot
        try:
            self.share_name = share.name
        except AttributeError:
            self.share_name = share or unquote(share)
        self.directory_path = directory_path or path_dir

        self._query_str, credential = self._format_query_string(
            sas_token, credential, share_snapshot=self.snapshot)
        super(DirectoryClient, self).__init__(parsed_url, 'file', credential, **kwargs)
        self._client = AzureFileStorage(version=VERSION, url=self.url, pipeline=self._pipeline)

    def _format_url(self, hostname):
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
            credential=None, # type: Optiona[Any]
            **kwargs # type: Any
        ):
        # type: (...) -> DirectoryClient
        """
        Create DirectoryClient from a Connection String.
        """
        account_url, secondary, credential = parse_connection_str(conn_str, credential, 'file')
        if 'secondary_hostname' not in kwargs:
            kwargs['secondary_hostname'] = secondary
        return cls(
            account_url, share=share, directory_path=directory_path, credential=credential, **kwargs)
    
    def get_file_client(self, file_name, **kwargs):
        """Get a client to interact with the specified file.
        The file need not already exist.

        :param directory_name:
            The name of the directory.
        :type directory_name: str
        :returns: A File Client.
        :rtype: ~azure.core.file.file_client.FileClient
        """
        if self.directory_path:
            file_name = self.directory_path.rstrip('/') + "/" + file_name
        return FileClient(
            self.url, file_path=file_name, snapshot=self.snapshot, credential=self.credential,
            _hosts=self._hosts, _configuration=self._config, _pipeline=self._pipeline,
            _location_mode=self._location_mode, **kwargs)

    def get_subdirectory_client(self, directory_name, **kwargs):
        """Get a client to interact with the specified subdirectory.
        The subdirectory need not already exist.

        :param directory_name:
            The name of the subdirectory.
        :type directory_name: str
        :returns: A Directory Client.
        :rtype: ~azure.core.file.directory_client.DirectoryClient
        """
        directory_path = self.directory_path.rstrip('/') + "/" + directory_name
        return DirectoryClient(
            self.url, directory_path=directory_path, snapshot=self.snapshot, credential=self.credential,
            _hosts=self._hosts, _configuration=self._config, _pipeline=self._pipeline,
            _location_mode=self._location_mode, **kwargs)

    def create_directory(
            self, metadata=None,  # type: Optional[Dict[str, str]]
            timeout=None, # type: Optional[int]
            **kwargs # type: Optional[Any]
        ):
        # type: (...) -> Dict[str, Any]
        """Creates a new Directory.
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
            return self._client.directory.create(
                timeout=timeout,
                cls=return_response_headers,
                headers=headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    def delete_directory(self, timeout=None, **kwargs):
        # type: (Optional[int]) -> None
        """Marks the specified directory for deletion. The directory is
        later deleted during garbage collection.

        :param int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None
        """
        try:
            self._client.directory.delete(timeout=timeout, **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    def list_directories_and_files(self, name_starts_with=None, marker=None, timeout=None, **kwargs):
        # type: (Optional[str], Optional[int]) -> DirectoryProperties
        """
        :returns: An auto-paging iterable of dict-like DirectoryProperties and FileProperties
        """
        results_per_page = kwargs.pop('results_per_page', None)
        command = functools.partial(
            self._client.directory.list_files_and_directories_segment,
            sharesnapshot=self.snapshot,
            timeout=timeout,
            **kwargs)
        return DirectoryPropertiesPaged(
            command, prefix=name_starts_with, results_per_page=results_per_page, marker=marker)

    def list_handles(self, marker=None, timeout=None, recursive=False, **kwargs):
        """
        :returns: An auto-paging iterable of HandleItems
        """
        results_per_page = kwargs.pop('results_per_page', None)
        command = functools.partial(
            self._client.directory.list_handles,
            sharesnapshot=self.snapshot,
            timeout=timeout,
            recursive=recursive,
            **kwargs)
        return HandlesPaged(
            command, results_per_page=results_per_page, marker=marker)

    def close_handles(
            self, handle=None, # type: Union[str, HandleItem]
            recursive=False,  # type: bool
            timeout=None, # type: Optional[int]
            **kwargs # type: Any
        ):
        # type: (...) -> Any
        try:
            handle_id = handle.id
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

        polling_method = CloseHandles(self._config.data_settings.copy_polling_interval)
        return LROPoller(
            command,
            start_close,
            None,
            polling_method)

    def get_directory_properties(self, timeout=None, **kwargs):
        # type: (Optional[int], Any) -> DirectoryProperties
        """
        :returns: DirectoryProperties
        """
        try:
            response = self._client.directory.get_properties(
                timeout=timeout,
                cls=deserialize_directory_properties,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)
        return response

    def set_directory_metadata(self, metadata, timeout=None, **kwargs):
        # type: (Dict[str, Any], Optional[int], Any) ->  Dict[str, Any]
        """ Sets the metadata for the directory.
        :param metadata:
            Name-value pairs associated with the directory as metadata.
        :type metadata: dict(str, str)
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: directory-updated property dict (Etag and last modified).
        :rtype: dict(str, Any)
        """
        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata))
        try:
            return self._client.directory.set_metadata(
                timeout=timeout,
                cls=return_response_headers,
                headers=headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    def create_subdirectory(
            self, directory_name,  # type: str,
            metadata=None, #type: Optional[Dict[str, Any]]
            timeout=None, # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> DirectoryClient
        """Creates a new Sub Directory.
        :param directory_name:
            The name of the subdirectory.
        :type directory_name: str
        :param metadata:
            Name-value pairs associated with the directory as metadata.
        :type metadata: dict(str, str)
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: DirectoryClient
        :rtype: DirectoryClient
        """
        subdir = self.get_subdirectory_client(directory_name)
        subdir.create_directory(metadata=metadata, timeout=timeout, **kwargs)
        return subdir

    def delete_subdirectory(
            self, directory_name,  # type: str,
            timeout=None, # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> None
        """Deletes a Sub Directory.
        :param directory_name:
            The name of the subdirectory.
        :type directory_name: str
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: None
        """
        subdir = self.get_subdirectory_client(directory_name)
        subdir.delete_directory(timeout=timeout, **kwargs)

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
        """Creates a new file.
        :param file_name:
            The name of the file.
        :type file_name: str
        :param size:
            The max size of the file.
        :type size: int
        :param content_settings:
            The content settings.
        :param metadata:
            Name-value pairs associated with the file as metadata.
        :type metadata: dict(str, str)
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: FileClient
        :rtype: FileClient
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
        return file_client

    def delete_file(
            self, file_name,  # type: str,
            timeout=None, # type: Optional[int],
            **kwargs # type: Optional[Any] 
        ):
        # type: (...) -> None
        """Deletes a file.
        :param file_name:
            The name of the file.
        :type file_name: str
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: None
        """
        file_client = self.get_file_client(file_name)
        file_client.delete_file(timeout, **kwargs)
