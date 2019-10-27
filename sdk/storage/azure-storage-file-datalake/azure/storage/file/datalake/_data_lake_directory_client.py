# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.storage.blob._shared.base_client import parse_connection_str
from azure.storage.file.datalake import DataLakeFileClient
from ._path_client import PathClient


class DataLakeDirectoryClient(PathClient):
    def __init__(
        self, account_url,  # type: str
        file_system_name,  # type: str
        directory_name,  # type: str
        credential=None,  # type: Optional[Any]
        **kwargs  # type: Any
    ):
        super(DataLakeDirectoryClient, self).__init__(account_url, file_system_name, directory_name,
                                                      credential=credential, **kwargs)

    def generate_shared_access_signature(self):
        # ???
        pass

    @classmethod
    def from_connection_string(
            cls, conn_str,  # type: str
            file_system_name,  # type: str
            directory_name,  # type: str
            credential=None,  # type: Optional[Any]
            **kwargs  # type: Any
        ):  # type: (...) -> DataLakeDirectoryClient
        """
        Create DataLakeDirectoryClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Storage account.
        :param file_system_name: The name of file system to interact with.
        :type file_system_name: str
        :param directory_name: The name of directory to interact with. The directory is under file system.
        :type directory_name: str
        :param credential:
            The credentials with which to authenticate. This is optional if the
            account URL already has a SAS token, or the connection string already has shared
            access key values. The value can be a SAS token string, and account shared access
            key, or an instance of a TokenCredentials class from azure.identity.
            Credentials provided here will take precedence over those in the connection string.
        :return a DataLakeDirectoryClient
        :rtype ~azure.storage.file.datalake.DataLakeDirectoryClient
        """
        account_url, secondary, credential = parse_connection_str(conn_str, credential, 'dfs')
        if 'secondary_hostname' not in kwargs:
            kwargs['secondary_hostname'] = secondary
        return cls(
            account_url, file_system_name=file_system_name, directory_name=directory_name,
            credential=credential, **kwargs)

    def create_directory(self, content_settings=None,  # type: Optional[ContentSettings]
                         metadata=None,  # type: Optional[Dict[str, str]]
                         **kwargs):
        # type: (...) -> Dict[str, Union[str, datetime]]
        """
        Create directory
        :return:
        """
        return self._create('directory', content_settings=content_settings, metadata=metadata, **kwargs)

    def delete_directory(self, **kwargs):
        # type: (...) -> ItemPaged[Response]
        """
        Marks the specified directory for deletion.
        :return:
        """
        return self._delete(**kwargs)

    def get_directory_properties(self, **kwargs):
        # type: (**Any) -> DirectoryProperties
        return self._get_path_properties(**kwargs)

    def create_sub_directory(self, sub_directory,  # type: Union[DirectoryProperties, str]
                             content_settings=None,  # type: Optional[ContentSettings]
                             metadata=None,  # type: Optional[Dict[str, str]]
                             **kwargs):
        # type: (...) -> Dict[str, Union[str, datetime]]
        subdir = self.get_sub_directory_client(sub_directory)
        return subdir.create_directory(content_settings=content_settings, metadata=metadata, **kwargs)

    def delete_sub_directory(self, sub_directory,  # type: Union[DirectoryProperties, str]
                             **kwargs):
        # type: (...) -> ItemPaged[Response]
        subdir = self.get_sub_directory_client(sub_directory)
        return subdir.delete_directory(**kwargs)

    def get_file_client(self, file  # type: Union[FileProperties, str]
                        ):
        # type: (...) -> DataLakeFileClient
        return DataLakeFileClient(
            self.url, self.file_system_name, self.path_name, file, credential=self.credential,
            _hosts=self._hosts, _configuration=self._config, _pipeline=self._pipeline,
            _location_mode=self._location_mode, require_encryption=self.require_encryption,
            key_encryption_key=self.key_encryption_key,
            key_resolver_function=self.key_resolver_function)

    def get_sub_directory_client(self, sub_directory  # type: Union[DirectoryProperties, str]
                                 ):
        # type: (...) -> DataLakeDirectoryClient
        directory = self.path_name.rstrip('/') + "/" + sub_directory
        return DataLakeDirectoryClient(
            self.url, self.file_system_name, directory, credential=self.credential,
            _hosts=self._hosts, _configuration=self._config, _pipeline=self._pipeline,
            _location_mode=self._location_mode, require_encryption=self.require_encryption,
            key_encryption_key=self.key_encryption_key,
            key_resolver_function=self.key_resolver_function)
