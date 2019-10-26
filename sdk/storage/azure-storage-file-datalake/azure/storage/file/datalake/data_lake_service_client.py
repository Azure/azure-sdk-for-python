# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools

from azure.storage.file.datalake import DirectoryClient, FileClient

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse  # type: ignore

from azure.core.paging import ItemPaged

from azure.storage.blob import BlobServiceClient
from azure.storage.blob._shared.base_client import StorageAccountHostsMixin, parse_query, parse_connection_str
from .file_system_client import FileSystemClient

from ._serialize import convert_dfs_url_to_blob_url
from .models import FileSystemPropertiesPaged


class DataLakeServiceClient(StorageAccountHostsMixin):
    def __init__(
            self, account_url,  # type: str
            credential=None,  # type: Optional[Any]
            **kwargs  # type: Any
    ):
        try:
            if not account_url.lower().startswith('http'):
                account_url = "https://" + account_url
        except AttributeError:
            raise ValueError("Account URL must be a string.")
        parsed_url = urlparse(account_url.rstrip('/'))
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(account_url))

        blob_account_url = convert_dfs_url_to_blob_url(account_url)
        self._blob_service_client = BlobServiceClient(blob_account_url, credential, **kwargs)

        _, sas_token = parse_query(parsed_url.query)
        self._query_str, credential = self._format_query_string(sas_token, credential)

        super(DataLakeServiceClient, self).__init__(parsed_url, service='dfs', credential=credential, **kwargs)

    def _format_url(self, hostname):
        """Format the endpoint URL according to the current location
        mode hostname.
        """
        formated_url = "{}://{}/{}".format(self.scheme, hostname, self._query_str)
        return formated_url

    @classmethod
    def from_connection_string(
            cls, conn_str,  # type: str
            credential=None,  # type: Optional[Any]
            **kwargs  # type: Any
        ):  # type: (...) -> DataLakeServiceClient
        """
        Create DataLakeServiceClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Storage account.
        :param credential:
            The credentials with which to authenticate. This is optional if the
            account URL already has a SAS token, or the connection string already has shared
            access key values. The value can be a SAS token string, and account shared access
            key, or an instance of a TokenCredentials class from azure.identity.
            Credentials provided here will take precedence over those in the connection string.
        :return a DataLakeServiceClient
        :rtype ~azure.storage.file.datalake.DataLakeServiceClient
        """
        account_url, secondary, credential = parse_connection_str(conn_str, credential, 'dfs')
        if 'secondary_hostname' not in kwargs:
            kwargs['secondary_hostname'] = secondary
        return cls(account_url, credential=credential, **kwargs)

    def get_user_delegation_key(self, key_start_time,  # type: datetime
                                key_expiry_time,  # type: datetime
                                **kwargs  # type: Any
                                ):
        # type: (...) -> UserDelegationKey
        return self._blob_service_client.get_user_delegation_key(key_start_time=key_start_time,
                                                                 key_expiry_time=key_expiry_time,
                                                                 **kwargs)

    def list_file_systems(self, name_starts_with=None,  # type: Optional[str]
                          **kwargs):
        # type: (...) -> ItemPaged[FileSystemProperties]

        item_paged = self._blob_service_client.list_containers(name_starts_with=name_starts_with, **kwargs)
        item_paged._page_iterator_class = FileSystemPropertiesPaged
        return item_paged

    def create_file_system(self, file_system_name,  # type: str
                           metadata=None,  # type: Optional[Dict[str, str]]
                           **kwargs):
        # type: (...) -> FileSystemClient
        file_system_client = self.get_file_system_client(file_system_name)
        file_system_client.create_file_system(metadata=metadata, **kwargs)
        return file_system_client

    def delete_file_system(self, file_system,  # type: Union[FileSystemProperties, str]
                           **kwargs):
        # type: (Any) -> None
        file_system_client = self.get_file_system_client(file_system)
        file_system_client.delete_file_system(**kwargs)

    def get_file_system_client(self, file_system  # type: Union[FileSystemProperties, str]
                               ):
        # type: (...) -> FileSystemClient
        return FileSystemClient(self.url, file_system, credential=self.credential, _configuration=self._config,
                                _pipeline=self._pipeline, _location_mode=self._location_mode, _hosts=self._hosts,
                                require_encryption=self.require_encryption, key_encryption_key=self.key_encryption_key,
                                key_resolver_function=self.key_resolver_function)

    def get_directory_client(self, file_system,  # type: Union[FileSystemProperties, str]
                             directory  # type: # type: Union[DirectoryProperties, str]
                             ):
        # type: (...) -> DirectoryClient
        return DirectoryClient(self.url, file_system, directory, credential=self.credential,
                               _configuration=self._config, _pipeline=self._pipeline,
                               _location_mode=self._location_mode, _hosts=self._hosts,
                               require_encryption=self.require_encryption, key_encryption_key=self.key_encryption_key,
                               key_resolver_function=self.key_resolver_function
                               )

    def get_file_client(self, file_system,  # type: Union[FileSystemProperties, str]
                        directory,  # type: # type: Union[DirectoryProperties, str]
                        file  # type: Union[FileProperties, str]
                        ):
        # type: (...) -> FileClient
        return FileClient(
            self.url, file_system, directory, file, credential=self.credential,
            _hosts=self._hosts, _configuration=self._config, _pipeline=self._pipeline,
            _location_mode=self._location_mode, require_encryption=self.require_encryption,
            key_encryption_key=self.key_encryption_key,
            key_resolver_function=self.key_resolver_function)
