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

from .file_client import FileClient

from .models import DirectoryPropertiesPaged
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

class DirectoryClient(StorageAccountHostsMixin):
    """
    A client to interact with the sirectory.
    """

    def __init__(
            self, share_name=None, # type: Optional[Union[str, ShareProperties]]
            directory_path=None, # type: Optional[str]
            credential=None, # type: Optional[Any]
            configuration=None, # type: Optional[Configuration]
            **kwargs, # type: Optional[Any]
        ):
        # type: (...) -> DirectoryClient
        """Creates a new DirectoryClient. This client represents interaction with a specific
        directory, although it may not yet exist.
        :param share_name: The directory with which to interact. If specified, this value will override
         a directory value specified in the directory URL.
        :type share_name: str or ~azure.storage.file.models.DirectoryProperties
        :param str directory_path: The full URI to the directory.
        :param credential:
        :param configuration: A optional pipeline configuration.
         This can be retrieved with :func:`DirectoryClient.create_configuration()`
        """
        try:
            if not directory_path.lower().startswith('http'):
                directory_path = "https://" + directory_path
        except AttributeError:
            raise ValueError("directory_path must be a string.")
        parsed_url = urlparse(directory_path.rstrip('/'))
        if not parsed_url.path and not share_name:
            raise ValueError("Please specify a share name.")
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(directory_path))

        share, path_dir = "", ""
        if parsed_url.path:
            share, _, path_dir = parsed_url.path.lstrip('/').partition('/')
        _, sas_token = parse_query(parsed_url.query)
        try:
            self.share_name = share_name.name
        except AttributeError:
            self.share_name = share_name or unquote(share)
        
        self.directory_path = path_dir or ""

        self._query_str, credential = self._format_query_string(sas_token, credential)
        super(DirectoryClient, self).__init__(parsed_url, credential, configuration, **kwargs)
        self._client = AzureFileStorage(version=VERSION, url=self.url, pipeline=self._pipeline)

    @classmethod
    def from_connection_string(
            cls, conn_str,  # type: str
            share_name=None, # type: Optional[Union[str, ShareProperties]]
            directory_path=None, # type: Optional[str]
            configuration=None, # type: Optional[Configuration]
            credential=None, # type: Optiona[Any]
            **kwargs # type: Any
        ):
        # type: (...) -> DirectoryClient
        """
        Create DirectoryClient from a Connection String.
        """
        _, credential = parse_connection_str(conn_str, credential)
        return cls(share_name, directory_path, credential=credential, configuration=configuration, **kwargs)
    
    def get_file_client(self, file_name):
        """Get a client to interact with the specified file.
        The file need not already exist.

        :param directory_name:
            The name of the directory.
        :type directory_name: str
        :returns: A File Client.
        :rtype: ~azure.core.file.file_client.FileClient
        """
        file_url = self.directory_path.rstrip('/') + "/" + quote(file_name)
        return FileClient(
            file_url=file_url,
            share_name=self.share_name,
            directory_path=self.directory_path,
            credential=self.credential,
            configuration=self._config)

    def get_subdirectory_client(self, directory_name, **kwargs):
        """Get a client to interact with the specified subdirectory.
        The subdirectory need not already exist.

        :param directory_name:
            The name of the subdirectory.
        :type directory_name: str
        :returns: A Directory Client.
        :rtype: ~azure.core.file.directory_client.DirectoryClient
        """
        directory_path = self.directory_path.rstrip('/') + "/" + quote(directory_name)
        return DirectoryClient(self.share_name, directory_path, self.credential, self._config, **kwargs)

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

    def list_directies_and_files(self, prefix=None, timeout=None, **kwargs):
        # type: (Optional[str], Optional[int]) -> DirectoryProperties
        """
        :returns: An auto-paging iterable of dict-like DirectoryProperties and FileProperties
        """
        results_per_page = kwargs.pop('results_per_page', None)
        command = functools.partial(
            self._client.directory.list_files_and_directories_segment,
            prefix=prefix,
            timeout=timeout,
            **kwargs)
        return DirectoryPropertiesPaged(command, prefix=prefix, results_per_page=results_per_page)

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
            timeout=None # type: Optional[int]
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

    def delete_subdirectory(
            self, directory_name,  # type: str,
            timeout=None # type: Optional[int]
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

    def create_file(
            self, file_name,  # type: str,
            size, # type: int
            content_settings=None, # type: Any
            metadata=None, #type: Optional[Dict[str, Any]]
            timeout=None, # type: Optional[int]
            **kwargs # type: Optional[Any]
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
        file_client.create_file(size, content_settings, metadata, timeout, **kwargs)
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
