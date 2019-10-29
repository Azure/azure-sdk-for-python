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

        :param ~azure.storage.file.datalake.ContentSettings content_settings:
            ContentSettings object used to set path properties.
        :param metadata:
            Name-value pairs associated with the blob as metadata.
        :type metadata: dict(str, str)
        :keyword ~azure.storage.file.datalake.DataLakeLeaseClient or str lease:
            Required if the blob has an active lease. Value can be a DataLakeLeaseClient object
            or the lease ID as a string.
        :keyword str umask: Optional and only valid if Hierarchical Namespace is enabled for the account.
            When creating a file or directory and the parent folder does not have a default ACL,
            the umask restricts the permissions of the file or directory to be created.
            The resulting permission is given by p & ^u, where p is the permission and u is the umask.
            For example, if p is 0777 and u is 0057, then the resulting permission is 0720.
            The default permission is 0777 for a directory and 0666 for a file. The default umask is 0027.
            The umask must be specified in 4-digit octal notation (e.g. 0766).
        :keyword str permissions: Optional and only valid if Hierarchical Namespace
         is enabled for the account. Sets POSIX access permissions for the file
         owner, the file owning group, and others. Each class may be granted
         read, write, or execute permission.  The sticky bit is also supported.
         Both symbolic (rwxrw-rw-) and 4-digit octal notation (e.g. 0766) are
         supported.
        :keyword ~datetime.datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :keyword ~datetime.datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :keyword str if_match:
            An ETag value, or the wildcard character (*). Specify this header to perform
            the operation only if the resource's ETag matches the value specified.
        :keyword str if_none_match:
            An ETag value, or the wildcard character (*). Specify this header
            to perform the operation only if the resource's ETag does not match
            the value specified. Specify the wildcard character (*) to perform
            the operation only if the resource does not exist, and fail the
            operation if it does exist.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :return: response dict (Etag and last modified).
        """
        return self._create('directory', content_settings=content_settings, metadata=metadata, **kwargs)

    def delete_directory(self, **kwargs):
        # type: (...) -> None
        """
        Marks the specified directory for deletion.

        :keyword lease:
            Required if the blob has an active lease. Value can be a LeaseClient object
            or the lease ID as a string.
        :type lease: ~azure.storage.blob.LeaseClient or str
        :keyword ~datetime.datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :keyword ~datetime.datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :keyword str if_match:
            An ETag value, or the wildcard character (*). Specify this header to perform
            the operation only if the resource's ETag matches the value specified.
        :keyword str if_none_match:
            An ETag value, or the wildcard character (*). Specify this header
            to perform the operation only if the resource's ETag does not match
            the value specified. Specify the wildcard character (*) to perform
            the operation only if the resource does not exist, and fail the
            operation if it does exist.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :return: None
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
