# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools

try:
    from urllib.parse import urlparse, quote
except ImportError:
    from urlparse import urlparse # type: ignore
    from urllib2 import quote  # type: ignore

import six
from azure.core.paging import ItemPaged
from azure.storage.blob import ContainerClient
from ._shared.base_client import StorageAccountHostsMixin, parse_query, parse_connection_str
from ._serialize import convert_dfs_url_to_blob_url
from ._models import LocationMode, FileSystemProperties, PathPropertiesPaged
from ._data_lake_file_client import DataLakeFileClient
from ._data_lake_directory_client import DataLakeDirectoryClient
from ._data_lake_lease import DataLakeLeaseClient
from ._generated import DataLakeStorageClient


class FileSystemClient(StorageAccountHostsMixin):
    """A client to interact with a specific file system, even if that file system
    may not yet exist.

    For operations relating to a specific directory or file within this file system, a directory client or file client
    can be retrieved using the :func:`~get_directory_client` or :func:`~get_file_client` functions.

    :ivar str url:
        The full endpoint URL to the file system, including SAS token if used.
    :ivar str primary_endpoint:
        The full primary endpoint URL.
    :ivar str primary_hostname:
        The hostname of the primary endpoint.
    :param str account_url:
        The URI to the storage account.
    :param file_system_name:
        The file system for the directory or files.
    :type file_system_name: str
    :param credential:
        The credentials with which to authenticate. This is optional if the
        account URL already has a SAS token. The value can be a SAS token string, and account
        shared access key, or an instance of a TokenCredentials class from azure.identity.
        If the URL already has a SAS token, specifying an explicit credential will take priority.

    .. admonition:: Example:

        .. literalinclude:: ../samples/test_file_system_samples.py
            :start-after: [START create_file_system_client_from_service]
            :end-before: [END create_file_system_client_from_service]
            :language: python
            :dedent: 8
            :caption: Get a FileSystemClient from an existing DataLakeServiceClient.

        .. literalinclude:: ../samples/test_file_system_samples.py
            :start-after: [START create_file_system_client_sasurl]
            :end-before: [END create_file_system_client_sasurl]
            :language: python
            :dedent: 8
            :caption: Creating the FileSystemClient client directly.
    """
    def __init__(
        self, account_url,  # type: str
        file_system_name,  # type: str
        credential=None,  # type: Optional[Any]
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        try:
            if not account_url.lower().startswith('http'):
                account_url = "https://" + account_url
        except AttributeError:
            raise ValueError("account URL must be a string.")
        parsed_url = urlparse(account_url.rstrip('/'))
        if not file_system_name:
            raise ValueError("Please specify a file system name.")
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(account_url))

        blob_account_url = convert_dfs_url_to_blob_url(account_url)
        # TODO: add self.account_url to base_client and remove _blob_account_url
        self._blob_account_url = blob_account_url

        datalake_hosts = kwargs.pop('_hosts', None)
        blob_hosts = None
        if datalake_hosts:
            blob_primary_account_url = convert_dfs_url_to_blob_url(datalake_hosts[LocationMode.PRIMARY])
            blob_secondary_account_url = convert_dfs_url_to_blob_url(datalake_hosts[LocationMode.SECONDARY])
            blob_hosts = {LocationMode.PRIMARY: blob_primary_account_url,
                          LocationMode.SECONDARY: blob_secondary_account_url}
        self._container_client = ContainerClient(blob_account_url, file_system_name,
                                                 credential=credential, _hosts=blob_hosts, **kwargs)

        _, sas_token = parse_query(parsed_url.query)
        self.file_system_name = file_system_name
        self._query_str, self._raw_credential = self._format_query_string(sas_token, credential)

        super(FileSystemClient, self).__init__(parsed_url, service='dfs', credential=self._raw_credential,
                                               _hosts=datalake_hosts, **kwargs)
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
        :rtype ~azure.storage.filedatalake.FileSystemClient
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
        """
        Requests a new lease. If the file system does not have an active lease,
        the DataLake service creates a lease on the file system and returns a new
        lease ID.

        :param int lease_duration:
            Specifies the duration of the lease, in seconds, or negative one
            (-1) for a lease that never expires. A non-infinite lease can be
            between 15 and 60 seconds. A lease duration cannot be changed
            using renew or change. Default is -1 (infinite lease).
        :param str lease_id:
            Proposed lease ID, in a GUID string format. The DataLake service returns
            400 (Invalid request) if the proposed lease ID is not in the correct format.
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
        :keyword ~azure.core.MatchConditions match_condition:
            The match condition to use upon the etag.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: A DataLakeLeaseClient object, that can be run in a context manager.
        :rtype: ~azure.storage.filedatalake.DataLakeLeaseClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/test_file_system_samples.py
                :start-after: [START acquire_lease_on_file_system]
                :end-before: [END acquire_lease_on_file_system]
                :language: python
                :dedent: 8
                :caption: Acquiring a lease on the file_system.
        """
        lease = DataLakeLeaseClient(self, lease_id=lease_id)
        lease.acquire(lease_duration=lease_duration, **kwargs)
        return lease

    def create_file_system(self, metadata=None,  # type: Optional[Dict[str, str]]
                           public_access=None,  # type: Optional[PublicAccess]
                           **kwargs):
        # type: (...) ->  Dict[str, Union[str, datetime]]
        """Creates a new file system under the specified account.

        If the file system with the same name already exists, a ResourceExistsError will
        be raised. This method returns a client with which to interact with the newly
        created file system.

        :param metadata:
            A dict with name-value pairs to associate with the
            file system as metadata. Example: `{'Category':'test'}`
        :type metadata: dict(str, str)
        :param public_access:
            Possible values include: file system, file.
        :type public_access: ~azure.storage.filedatalake.PublicAccess
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: ~azure.storage.filedatalake.FileSystemClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/test_file_system_samples.py
                :start-after: [START create_file_system]
                :end-before: [END create_file_system]
                :language: python
                :dedent: 12
                :caption: Creating a file system in the datalake service.
        """
        return self._container_client.create_container(metadata=metadata,
                                                       public_access=public_access,
                                                       **kwargs)

    def delete_file_system(self, **kwargs):
        # type: (Any) -> None
        """Marks the specified file system for deletion.

        The file system and any files contained within it are later deleted during garbage collection.
        If the file system is not found, a ResourceNotFoundError will be raised.

        :keyword str or ~azure.storage.filedatalake.DataLakeLeaseClient lease:
            If specified, delete_file_system only succeeds if the
            file system's lease is active and matches this ID.
            Required if the file system has an active lease.
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
        :keyword ~azure.core.MatchConditions match_condition:
            The match condition to use upon the etag.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/test_file_system_samples.py
                :start-after: [START delete_file_system]
                :end-before: [END delete_file_system]
                :language: python
                :dedent: 12
                :caption: Deleting a file system in the datalake service.
        """
        self._container_client.delete_container(**kwargs)

    def get_file_system_properties(self, **kwargs):
        # type: (Any) -> FileSystemProperties
        """Returns all user-defined metadata and system properties for the specified
        file system. The data returned does not include the file system's list of paths.

        :keyword str or ~azure.storage.filedatalake.DataLakeLeaseClient lease:
            If specified, get_file_system_properties only succeeds if the
            file system's lease is active and matches this ID.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :return: Properties for the specified file system within a file system object.
        :rtype: ~azure.storage.filedatalake.FileSystemProperties

        .. admonition:: Example:

            .. literalinclude:: ../samples/test_file_system_samples.py
                :start-after: [START get_file_system_properties]
                :end-before: [END get_file_system_properties]
                :language: python
                :dedent: 12
                :caption: Getting properties on the file system.
        """
        container_properties = self._container_client.get_container_properties(**kwargs)
        return FileSystemProperties._convert_from_container_props(container_properties)  # pylint: disable=protected-access

    def set_file_system_metadata(  # type: ignore
        self, metadata=None,  # type: Optional[Dict[str, str]]
        **kwargs
    ):
        # type: (...) -> Dict[str, Union[str, datetime]]
        """Sets one or more user-defined name-value pairs for the specified
        file system. Each call to this operation replaces all existing metadata
        attached to the file system. To remove all metadata from the file system,
        call this operation with no metadata dict.

        :param metadata:
            A dict containing name-value pairs to associate with the file system as
            metadata. Example: {'category':'test'}
        :type metadata: dict[str, str]
        :keyword str or ~azure.storage.filedatalake.DataLakeLeaseClient lease:
            If specified, set_file_system_metadata only succeeds if the
            file system's lease is active and matches this ID.
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
        :keyword ~azure.core.MatchConditions match_condition:
            The match condition to use upon the etag.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: file system-updated property dict (Etag and last modified).

        .. admonition:: Example:

            .. literalinclude:: ../samples/test_file_system_samples.py
                :start-after: [START set_file_system_metadata]
                :end-before: [END set_file_system_metadata]
                :language: python
                :dedent: 12
                :caption: Setting metadata on the container.
        """
        return self._container_client.set_container_metadata(metadata=metadata, **kwargs)

    def get_paths(self, path=None, # type: Optional[str]
                  recursive=True,  # type: Optional[bool]
                  max_results=None,  # type: Optional[int]
                  **kwargs):
        # type: (...) -> ItemPaged[PathProperties]
        """Returns a generator to list the paths(could be files or directories) under the specified file system.
        The generator will lazily follow the continuation tokens returned by
        the service.

        :param str path:
            Filters the results to return only paths under the specified path.
        :param int max_results: An optional value that specifies the maximum
            number of items to return per page. If omitted or greater than 5,000, the
            response will include up to 5,000 items per page.
        :keyword upn: Optional. Valid only when Hierarchical Namespace is
         enabled for the account. If "true", the user identity values returned
         in the x-ms-owner, x-ms-group, and x-ms-acl response headers will be
         transformed from Azure Active Directory Object IDs to User Principal
         Names.  If "false", the values will be returned as Azure Active
         Directory Object IDs. The default value is false. Note that group and
         application Object IDs are not translated because they do not have
         unique friendly names.
        :type upn: bool
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: An iterable (auto-paging) response of PathProperties.
        :rtype: ~azure.core.paging.ItemPaged[~azure.storage.filedatalake.PathProperties]

        .. admonition:: Example:

            .. literalinclude:: ../tests/test_blob_samples_containers.py
                :start-after: [START list_blobs_in_container]
                :end-before: [END list_blobs_in_container]
                :language: python
                :dedent: 8
                :caption: List the blobs in the container.
        """
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
        # type: (...) -> DataLakeDirectoryClient
        """
        Create directory

        :param directory:
            The directory with which to interact. This can either be the name of the directory,
            or an instance of DirectoryProperties.
        :type directory: str or ~azure.storage.filedatalake.DirectoryProperties
        :param ~azure.storage.filedatalake.ContentSettings content_settings:
            ContentSettings object used to set path properties.
        :param metadata:
            Name-value pairs associated with the blob as metadata.
        :type metadata: dict(str, str)
        :keyword ~azure.storage.filedatalake.DataLakeLeaseClient or str lease:
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
        :keyword str etag:
            An ETag value, or the wildcard character (*). Used to check if the resource has changed,
            and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition:
            The match condition to use upon the etag.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :return: DataLakeDirectoryClient
        """
        directory_client = self.get_directory_client(directory)
        directory_client.create_directory(content_settings=content_settings, metadata=metadata, **kwargs)
        return directory_client

    def delete_directory(self, directory,  # type: Union[DirectoryProperties, str]
                         **kwargs):
        # type: (...) -> DataLakeDirectoryClient
        """
        Marks the specified path for deletion.

        :param directory:
            The directory with which to interact. This can either be the name of the directory,
            or an instance of DirectoryProperties.
        :type directory: str or ~azure.storage.filedatalake.DirectoryProperties
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
        :keyword str etag:
            An ETag value, or the wildcard character (*). Used to check if the resource has changed,
            and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition:
            The match condition to use upon the etag.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :return: DataLakeDirectoryClient
        """
        directory_client = self.get_directory_client(directory)
        directory_client.delete_directory(**kwargs)
        return directory_client

    def create_file(self, file,  # type: Union[FileProperties, str]
                    **kwargs):
        # type: (...) -> DataLakeFileClient
        """
        Create file

        :param file:
            The file with which to interact. This can either be the name of the file,
            or an instance of FileProperties.
        :type file: str or ~azure.storage.filedatalake.FileProperties
        :param ~azure.storage.filedatalake.ContentSettings content_settings:
            ContentSettings object used to set path properties.
        :param metadata:
            Name-value pairs associated with the blob as metadata.
        :type metadata: dict(str, str)
        :keyword ~azure.storage.filedatalake.DataLakeLeaseClient or str lease:
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
        :keyword str etag:
            An ETag value, or the wildcard character (*). Used to check if the resource has changed,
            and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition:
            The match condition to use upon the etag.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :return: DataLakeFileClient
        """
        file_client = self.get_file_client(file)
        file_client.create_file(**kwargs)
        return file_client

    def delete_file(self, file,  # type: Union[FileProperties, str]
                    lease=None,  # type: Optional[Union[DataLakeLeaseClient, str]]
                    **kwargs):
        # type: (...) -> DataLakeFileClient
        """
        Marks the specified file for deletion.

        :param file:
            The file with which to interact. This can either be the name of the file,
            or an instance of FileProperties.
        :type file: str or ~azure.storage.filedatalake.FileProperties
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
        :keyword str etag:
            An ETag value, or the wildcard character (*). Used to check if the resource has changed,
            and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition:
            The match condition to use upon the etag.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :return: DataLakeFileClient
        """
        file_client = self.get_file_client(file)
        file_client.delete_file(lease=lease, **kwargs)
        return file_client

    def get_directory_client(self, directory  # type: Union[DirectoryProperties, str]
                             ):
        # type: (...) -> DataLakeDirectoryClient
        """Get a client to interact with the specified directory.

        The directory need not already exist.

        :param directory:
            The directory with which to interact. This can either be the name of the directory,
            or an instance of DirectoryProperties.
        :type directory: str or ~azure.storage.filedatalake.DirectoryProperties
        :returns: A DataLakeDirectoryClient.
        :rtype: ~azure.storage.filedatalake.DataLakeDirectoryClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/test_file_system_samples.py
                :start-after: [START get_directory_client_from_file_system]
                :end-before: [END get_directory_client_from_file_system]
                :language: python
                :dedent: 12
                :caption: Getting the directory client to interact with a specific directory.
        """
        return DataLakeDirectoryClient(self.url, self.file_system_name, directory_name=directory,
                                       credential=self._raw_credential,
                                       _configuration=self._config, _pipeline=self._pipeline,
                                       _location_mode=self._location_mode, _hosts=self._hosts,
                                       require_encryption=self.require_encryption,
                                       key_encryption_key=self.key_encryption_key,
                                       key_resolver_function=self.key_resolver_function
                                       )

    def get_file_client(self, file_path  # type: Union[FileProperties, str]
                        ):
        # type: (...) -> DataLakeFileClient
        """Get a client to interact with the specified file.

        The file need not already exist.

        :param file_path:
            The file with which to interact. This can either be the path of the file(from root directory),
            or an instance of FileProperties. eg. directory/subdirectory/file
        :type file_path: str or ~azure.storage.filedatalake.FileProperties
        :returns: A DataLakeFileClient.
        :rtype: ~azure.storage.filedatalake..DataLakeFileClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/test_file_system_samples.py
                :start-after: [START get_file_client_from_file_system]
                :end-before: [END get_file_client_from_file_system]
                :language: python
                :dedent: 12
                :caption: Getting the file client to interact with a specific file.
        """
        try:
            file_path = file_path.name
        except AttributeError:
            pass

        return DataLakeFileClient(
            self.url, self.file_system_name, file_path=file_path, credential=self._raw_credential,
            _hosts=self._hosts, _configuration=self._config, _pipeline=self._pipeline,
            _location_mode=self._location_mode, require_encryption=self.require_encryption,
            key_encryption_key=self.key_encryption_key,
            key_resolver_function=self.key_resolver_function)
