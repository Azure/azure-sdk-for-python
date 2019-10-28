# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools

try:
    from urllib.parse import urlparse, quote, unquote
except ImportError:
    from urlparse import urlparse # type: ignore
    from urllib2 import quote, unquote # type: ignore

import six
from azure.core.paging import ItemPaged
from azure.storage.blob import ContainerClient
from azure.storage.blob._shared.base_client import StorageAccountHostsMixin, parse_query, parse_connection_str
from azure.storage.file.datalake._serialize import convert_dfs_url_to_blob_url
from azure.storage.file.datalake._models import LocationMode, FileSystemProperties, PathPropertiesPaged
from azure.storage.file.datalake import DataLakeFileClient, DataLakeDirectoryClient
from ._generated import DataLakeStorageClient


class FileSystemClient(StorageAccountHostsMixin):
    def __init__(
        self, account_url,  # type: str
        file_system_name,  # type: str
        credential=None,  # type: Optional[Any]
        **kwargs  # type: Any
    ):
        try:
            if not account_url.lower().startswith('http'):
                account_url = "https://" + account_url
        except AttributeError:
            raise ValueError("Container URL must be a string.")
        parsed_url = urlparse(account_url.rstrip('/'))
        if not file_system_name:
            raise ValueError("Please specify a file system name.")
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(account_url))

        blob_account_url = convert_dfs_url_to_blob_url(account_url)

        datalake_hosts = kwargs.pop('_hosts', None)
        blob_hosts = None
        if datalake_hosts:
            blob_primary_account_url = convert_dfs_url_to_blob_url(datalake_hosts[LocationMode.PRIMARY])
            blob_secondary_account_url = convert_dfs_url_to_blob_url(datalake_hosts[LocationMode.SECONDARY])
            blob_hosts = {LocationMode.PRIMARY: blob_primary_account_url,
                          LocationMode.SECONDARY: blob_secondary_account_url}
        self._container_client = ContainerClient(blob_account_url, file_system_name, credential, _hosts=blob_hosts, **kwargs)

        _, sas_token = parse_query(parsed_url.query)
        self.file_system_name = file_system_name
        self._query_str, credential = self._format_query_string(sas_token, credential)

        super(FileSystemClient, self).__init__(parsed_url, service='dfs', credential=credential, _hosts=datalake_hosts, **kwargs)
        self._client = DataLakeStorageClient(self.url, file_system_name, None, pipeline=self._pipeline)

    def _format_url(self, hostname):
        file_system_name = self.file_system_name
        if isinstance(file_system_name, six.text_type):
            file_system_name = file_system_name.encode('UTF-8')
        return "{}://{}/{}{}".format(
            self.scheme,
            hostname,
            quote(file_system_name),
            self._query_str)

    @classmethod
    def from_connection_string(
            cls, conn_str,  # type: str
            file_system_name,  # type: str
            credential=None,  # type: Optional[Any]
            **kwargs  # type: Any
        ):  # type: (...) -> FileSystemClient
        """
        Create FileSystemClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Storage account.
        :param file_system_name: The name of file system to interact with.
        :type file_system_name: str
        :param credential:
            The credentials with which to authenticate. This is optional if the
            account URL already has a SAS token, or the connection string already has shared
            access key values. The value can be a SAS token string, and account shared access
            key, or an instance of a TokenCredentials class from azure.identity.
            Credentials provided here will take precedence over those in the connection string.
        :return a FileSystemClient
        :rtype ~azure.storage.file.datalake.FileSystemClient
        """
        account_url, secondary, credential = parse_connection_str(conn_str, credential, 'dfs')
        if 'secondary_hostname' not in kwargs:
            kwargs['secondary_hostname'] = secondary
        return cls(
            account_url, file_system_name=file_system_name, credential=credential, **kwargs)

    def acquire_lease(
        self, lease_duration=-1,  # type: int
        lease_id=None,  # type: Optional[str]
        **kwargs
    ):
        # type: (...) -> DataLakeLeaseClient
        pass

    def create_file_system(self, metadata=None,  # type: Optional[Dict[str, str]]
                           **kwargs):
        # type: (...) -> None
        return self._container_client.create_container(metadata=metadata, **kwargs)

    def delete_file_system(self, **kwargs):
        # type: (Any) -> None
        """
        :rtype: None
        """
        self._container_client.delete_container(**kwargs)

    def get_file_system_properties(self, **kwargs):
        # type: (Any) -> FileSystemProperties
        container_properties = self._container_client.get_container_properties(**kwargs)
        container_properties.__class__ = FileSystemProperties
        return container_properties

    def set_file_system_metadata(  # type: ignore
        self, metadata=None,  # type: Optional[Dict[str, str]]
        **kwargs
    ):
        # type: (...) -> Dict[str, Union[str, datetime]]
        return self._container_client.set_container_metadata(metadata=metadata, **kwargs)

    def get_paths(self, path=None, # type: Optional[str]
                  recursive=True,  # type: Optional[bool]
                  max_results=None,  # type: Optional[int]
                  **kwargs):
        # type: (...) -> ItemPaged[PathProperties]

        timeout = kwargs.pop('timeout', None)
        command = functools.partial(
            self._client.file_system.list_paths,
            path=path,
            timeout=timeout,
            **kwargs)
        return ItemPaged(
            command, recursive, path=path, max_results=max_results,
            page_iterator_class=PathPropertiesPaged, **kwargs)

    def create_directory(self, directory,  # type: Union[DirectoryProperties, str]
                         content_settings=None,  # type: Optional[ContentSettings]
                         metadata=None,  # type: Optional[Dict[str, str]]
                         **kwargs):
        # type: (...) -> Dict[str, Union[str, datetime]]
        directory_client = self.get_directory_client(directory)
        return directory_client.create_directory(content_settings=content_settings, metadata=metadata, **kwargs)

    def delete_directory(self, directory,  # type: Union[DirectoryProperties, str]
                         **kwargs):
        # type: (...) -> None
        directory_client = self.get_directory_client(directory)
        return directory_client.delete_directory(**kwargs)

    def create_file(self, file,  # type: Union[FileProperties, str]
                    **kwargs):
        # type: (...) -> Dict[str, Union[str, datetime]]
        pass

    def delete_file(self, file,  # type: Union[FileProperties, str]
                    lease=None,  # type: Optional[Union[DataLakeLeaseClient, str]]
                    **kwargs):
        # type: (...) -> None
        pass

    def get_directory_client(self, directory  # type: Union[DirectoryProperties, str]
                             ):
        # type: (...) -> DataLakeDirectoryClient
        return DataLakeDirectoryClient(self.url, self.file_system_name, directory, credential=self.credential,
                                       _configuration=self._config, _pipeline=self._pipeline,
                                       _location_mode=self._location_mode, _hosts=self._hosts,
                                       require_encryption=self.require_encryption, key_encryption_key=self.key_encryption_key,
                                       key_resolver_function=self.key_resolver_function
                                       )

    def get_file_client(self, directory,  # type: Union[DirectoryProperties, str]
                        file  # type: Union[FileProperties, str]
                        ):
        # type: (...) -> DataLakeFileClient
        return DataLakeFileClient(
            self.url, self.file_system_name, directory, file, credential=self.credential,
            _hosts=self._hosts, _configuration=self._config, _pipeline=self._pipeline,
            _location_mode=self._location_mode, require_encryption=self.require_encryption,
            key_encryption_key=self.key_encryption_key,
            key_resolver_function=self.key_resolver_function)
