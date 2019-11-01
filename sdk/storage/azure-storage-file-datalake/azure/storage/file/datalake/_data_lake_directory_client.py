# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from ._shared.base_client import parse_connection_str
from ._data_lake_file_client import DataLakeFileClient
from ._models import DirectoryProperties
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
        """Returns all user-defined metadata, standard HTTP properties, and
        system properties for the directory. It does not return the content of the directory.

        :keyword lease:
            Required if the directory or file has an active lease. Value can be a DataLakeLeaseClient object
            or the lease ID as a string.
        :type lease: ~azure.storage.file.datalake.DataLakeLeaseClient or str
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
        :keyword str etag:
            An ETag value, or the wildcard character (*). Used to check if the resource has changed,
            and act according to the condition specified by the `match_condition` parameter.
        :keyword :class:`MatchConditions` match_condition:
            The match condition to use upon the etag.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: DirectoryProperties

        .. admonition:: Example:

            .. literalinclude:: ../tests/test_blob_samples_common.py
                :start-after: [START get_blob_properties]
                :end-before: [END get_blob_properties]
                :language: python
                :dedent: 8
                :caption: Getting the properties for a file/directory.
        """
        blob_properties = self._get_path_properties(**kwargs)
        return DirectoryProperties._from_blob_properties(blob_properties)

    def rename_directory(self, rename_destination, **kwargs):
        # type: (**Any) -> DataLakeDirectoryClient
        """
        Rename the source directory.

        :param str rename_destination: the new directory name the user want to rename to.
            The value must have the following format: "{filesystem}/{directory}/{subdirectory}".
        :keyword source_lease: A lease ID for the source path. If specified,
         the source path must have an active lease and the leaase ID must
         match.
        :keyword source_lease: ~azure.storage.file.datalake.DataLakeLeaseClient or str
        :param ~azure.storage.file.datalake.ContentSettings content_settings:
            ContentSettings object used to set path properties.
        :keyword lease:
            Required if the file/directory has an active lease. Value can be a LeaseClient object
            or the lease ID as a string.
        :type lease: ~azure.storage.file.datalake.DataLakeLeaseClient or str
        :keyword str umask: Optional and only valid if Hierarchical Namespace is enabled for the account.
            When creating a file or directory and the parent folder does not have a default ACL,
            the umask restricts the permissions of the file or directory to be created.
            The resulting permission is given by p & ^u, where p is the permission and u is the umask.
            For example, if p is 0777 and u is 0057, then the resulting permission is 0720.
            The default permission is 0777 for a directory and 0666 for a file. The default umask is 0027.
            The umask must be specified in 4-digit octal notation (e.g. 0766).
        :keyword permissions: Optional and only valid if Hierarchical Namespace
         is enabled for the account. Sets POSIX access permissions for the file
         owner, the file owning group, and others. Each class may be granted
         read, write, or execute permission.  The sticky bit is also supported.
         Both symbolic (rwxrw-rw-) and 4-digit octal notation (e.g. 0766) are
         supported.
        :type permissions: str
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
        :keyword ~datetime.datetime source_if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :keyword ~datetime.datetime source_if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :keyword str source_if_match:
            An ETag value, or the wildcard character (*). Specify this header to perform
            the operation only if the resource's ETag matches the value specified.
        :keyword str source_if_none_match:
            An ETag value, or the wildcard character (*). Specify this header
            to perform the operation only if the resource's ETag does not match
            the value specified. Specify the wildcard character (*) to perform
            the operation only if the resource does not exist, and fail the
            operation if it does exist.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :return: DataLakeDirectoryClient
        """
        rename_destination = rename_destination.strip('/')
        new_file_system = rename_destination.split('/')[0]
        path = rename_destination[len(new_file_system):]

        new_directory_client = DataLakeDirectoryClient(
            self.url, new_file_system, path, credential=self._raw_credential,
            _hosts=self._hosts, _configuration=self._config, _pipeline=self._pipeline,
            _location_mode=self._location_mode, require_encryption=self.require_encryption,
            key_encryption_key=self.key_encryption_key,
            key_resolver_function=self.key_resolver_function)
        new_directory_client._rename_path('/'+self.file_system_name+'/'+self.path_name, **kwargs)
        return new_directory_client

    def create_sub_directory(self, sub_directory,  # type: Union[DirectoryProperties, str]
                             content_settings=None,  # type: Optional[ContentSettings]
                             metadata=None,  # type: Optional[Dict[str, str]]
                             **kwargs):
        # type: (...) -> DataLakeDirectoryClient
        """
        Create subdirectory

        :param sub_directory:
            The directory with which to interact. This can either be the name of the directory,
            or an instance of DirectoryProperties.
        :type sub_directory: str or ~azure.storage.file.datalake.DirectoryProperties
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
        :return: DataLakeDirectoryClient for the subdirectory.
        """
        subdir = self.get_sub_directory_client(sub_directory)
        subdir.create_directory(content_settings=content_settings, metadata=metadata, **kwargs)
        return subdir

    def delete_sub_directory(self, sub_directory,  # type: Union[DirectoryProperties, str]
                             **kwargs):
        # type: (...) -> DataLakeDirectoryClient
        """
        Marks the specified subdirectory for deletion.

        :param sub_directory:
            The directory with which to interact. This can either be the name of the directory,
            or an instance of DirectoryProperties.
        :type sub_directory: str or ~azure.storage.file.datalake.DirectoryProperties
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
        :return: DataLakeDirectoryClient for the subdirectory
        """
        subdir = self.get_sub_directory_client(sub_directory)
        subdir.delete_directory(**kwargs)
        return subdir

    def create_file(self, file,  # type: Union[FileProperties, str]
                    **kwargs):
        # type: (...) -> DataLakeFileClient
        """
        Create file

        :param file:
            The file with which to interact. This can either be the name of the file,
            or an instance of FileProperties.
        :type file: str or ~azure.storage.file.datalake.FileProperties
        :keyword ~azure.storage.file.datalake.ContentSettings content_settings:
            ContentSettings object used to set path properties.
        :keyword metadata:
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
        :return: DataLakeFileClient
        """
        file_client = self.get_file_client(file)
        file_client.create_file(**kwargs)
        return file_client

    def get_file_client(self, file  # type: Union[FileProperties, str]
                        ):
        # type: (...) -> DataLakeFileClient
        """Get a client to interact with the specified file.

        The file need not already exist.

        :param file:
            The file with which to interact. This can either be the name of the file,
            or an instance of FileProperties. eg. directory/subdirectory/file
        :type file: str or ~azure.storage.file.datalake.FileProperties
        :returns: A DataLakeFileClient.
        :rtype: ~azure.storage.file.datalake..DataLakeFileClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/test_datalake_service_samples.py
                :start-after: [START bsc_get_file_client]
                :end-before: [END bsc_get_file_client]
                :language: python
                :dedent: 12
                :caption: Getting the file client to interact with a specific file.
        """
        try:
            file_path = file.name
        except AttributeError:
            file_path = self.path_name + '/' + file

        return DataLakeFileClient(
            self.url, self.file_system_name, file_path, credential=self._raw_credential,
            _hosts=self._hosts, _configuration=self._config, _pipeline=self._pipeline,
            _location_mode=self._location_mode, require_encryption=self.require_encryption,
            key_encryption_key=self.key_encryption_key,
            key_resolver_function=self.key_resolver_function)

    def get_sub_directory_client(self, sub_directory  # type: Union[DirectoryProperties, str]
                                 ):
        # type: (...) -> DataLakeDirectoryClient
        """Get a client to interact with the specified subdirectory of the current directory.

        The sub subdirectory need not already exist.

        :param sub_directory:
            The directory with which to interact. This can either be the name of the directory,
            or an instance of DirectoryProperties.
        :type sub_directory: str or ~azure.storage.file.datalake.DirectoryProperties
        :returns: A DataLakeDirectoryClient.
        :rtype: ~azure.storage.file.datalake.DataLakeDirectoryClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/test_datalake_service_samples.py
                :start-after: [START bsc_get_directory_client]
                :end-before: [END bsc_get_directory_client]
                :language: python
                :dedent: 12
                :caption: Getting the directory client to interact with a specific directory.
        """
        directory = self.path_name.rstrip('/') + "/" + sub_directory
        return DataLakeDirectoryClient(
            self.url, self.file_system_name, directory, credential=self._raw_credential,
            _hosts=self._hosts, _configuration=self._config, _pipeline=self._pipeline,
            _location_mode=self._location_mode, require_encryption=self.require_encryption,
            key_encryption_key=self.key_encryption_key,
            key_resolver_function=self.key_resolver_function)
