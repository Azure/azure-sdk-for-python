# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-many-lines
import functools
from typing import Any, Dict, Optional, Type, TypeVar, Union, TYPE_CHECKING

try:
    from urllib.parse import urlparse, quote, unquote
except ImportError:
    from urlparse import urlparse # type: ignore
    from urllib2 import quote, unquote  # type: ignore
import six

from azure.core.pipeline import Pipeline
from azure.core.exceptions import HttpResponseError
from azure.core.paging import ItemPaged
from azure.storage.blob import ContainerClient
from ._shared.base_client import TransportWrapper, StorageAccountHostsMixin, parse_query, parse_connection_str
from ._serialize import convert_dfs_url_to_blob_url, get_api_version
from ._list_paths_helper import DeletedPathPropertiesPaged, PathPropertiesPaged
from ._models import LocationMode, FileSystemProperties, PublicAccess, DeletedPathProperties, FileProperties, \
    DirectoryProperties
from ._data_lake_file_client import DataLakeFileClient
from ._data_lake_directory_client import DataLakeDirectoryClient
from ._data_lake_lease import DataLakeLeaseClient
from ._generated import AzureDataLakeStorageRESTAPI
from ._generated.models import ListBlobsIncludeItem
from ._deserialize import process_storage_error, is_file_path

if TYPE_CHECKING:
    from datetime import datetime


ClassType = TypeVar("ClassType")


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
        account URL already has a SAS token. The value can be a SAS token string,
        an instance of a AzureSasCredential from azure.core.credentials, an account
        shared access key, or an instance of a TokenCredentials class from azure.identity.
        If the resource URI already contains a SAS token, this will be ignored in favor of an explicit credential
        - except in the case of AzureSasCredential, where the conflicting SAS tokens will raise a ValueError.
    :keyword str api_version:
        The Storage API version to use for requests. Default value is the most recent service version that is
        compatible with the current SDK. Setting to an older version may result in reduced feature compatibility.

    .. admonition:: Example:

        .. literalinclude:: ../samples/datalake_samples_file_system.py
            :start-after: [START create_file_system_client_from_service]
            :end-before: [END create_file_system_client_from_service]
            :language: python
            :dedent: 8
            :caption: Get a FileSystemClient from an existing DataLakeServiceClient.
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
            blob_hosts = {LocationMode.PRIMARY: blob_primary_account_url, LocationMode.SECONDARY: ""}
        self._container_client = ContainerClient(blob_account_url, file_system_name,
                                                 credential=credential, _hosts=blob_hosts, **kwargs)

        _, sas_token = parse_query(parsed_url.query)
        self.file_system_name = file_system_name
        self._query_str, self._raw_credential = self._format_query_string(sas_token, credential)

        super(FileSystemClient, self).__init__(parsed_url, service='dfs', credential=self._raw_credential,
                                               _hosts=datalake_hosts, **kwargs)
        # ADLS doesn't support secondary endpoint, make sure it's empty
        self._hosts[LocationMode.SECONDARY] = ""
        self._client = AzureDataLakeStorageRESTAPI(self.url, base_url=self.url,
                                                   file_system=file_system_name, pipeline=self._pipeline)
        api_version = get_api_version(kwargs)
        self._client._config.version = api_version  # pylint: disable=protected-access
        self._datalake_client_for_blob_operation = AzureDataLakeStorageRESTAPI(self._container_client.url,
                                                                               base_url=self._container_client.url,
                                                                               file_system=file_system_name,
                                                                               pipeline=self._pipeline)
        self._datalake_client_for_blob_operation._config.version = api_version  # pylint: disable=protected-access

    def _format_url(self, hostname):
        file_system_name = self.file_system_name
        if isinstance(file_system_name, six.text_type):
            file_system_name = file_system_name.encode('UTF-8')
        return "{}://{}/{}{}".format(
            self.scheme,
            hostname,
            quote(file_system_name),
            self._query_str)

    def __exit__(self, *args):
        self._container_client.close()
        super(FileSystemClient, self).__exit__(*args)

    def close(self):
        # type: () -> None
        """ This method is to close the sockets opened by the client.
        It need not be used when using with a context manager.
        """
        self._container_client.close()
        self.__exit__()

    @classmethod
    def from_connection_string(
            cls,  # type: Type[ClassType]
            conn_str,  # type: str
            file_system_name,  # type: str
            credential=None,  # type: Optional[Any]
            **kwargs  # type: Any
        ):  # type: (...) -> ClassType
        """
        Create FileSystemClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Storage account.
        :param file_system_name: The name of file system to interact with.
        :type file_system_name: str
        :param credential:
            The credentials with which to authenticate. This is optional if the
            account URL already has a SAS token, or the connection string already has shared
            access key values. The value can be a SAS token string,
            an instance of a AzureSasCredential from azure.core.credentials, an account shared access
            key, or an instance of a TokenCredentials class from azure.identity.
            Credentials provided here will take precedence over those in the connection string.
        :return a FileSystemClient
        :rtype ~azure.storage.filedatalake.FileSystemClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/datalake_samples_file_system.py
                :start-after: [START create_file_system_client_from_connection_string]
                :end-before: [END create_file_system_client_from_connection_string]
                :language: python
                :dedent: 8
                :caption: Create FileSystemClient from connection string
        """
        account_url, _, credential = parse_connection_str(conn_str, credential, 'dfs')
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

            .. literalinclude:: ../samples/datalake_samples_file_system.py
                :start-after: [START acquire_lease_on_file_system]
                :end-before: [END acquire_lease_on_file_system]
                :language: python
                :dedent: 8
                :caption: Acquiring a lease on the file system.
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
            To specify whether data in the file system may be accessed publicly and the level of access.
        :type public_access: ~azure.storage.filedatalake.PublicAccess
        :keyword file_system_encryption_scope:
            Specifies the default encryption scope to set on the file system and use for
            all future writes.

            .. versionadded:: 12.9.0

        :paramtype file_system_encryption_scope: dict or ~azure.storage.filedatalake.FileSystemEncryptionScope
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: A dictionary of response headers.
        :rtype: Dict[str, Union[str, datetime]]

        .. admonition:: Example:

            .. literalinclude:: ../samples/datalake_samples_file_system.py
                :start-after: [START create_file_system]
                :end-before: [END create_file_system]
                :language: python
                :dedent: 12
                :caption: Creating a file system in the datalake service.
        """
        file_system_encryption_scope = kwargs.pop('file_system_encryption_scope', None)
        return self._container_client.create_container(metadata=metadata,
                                                       public_access=public_access,
                                                       container_encryption_scope=file_system_encryption_scope,
                                                       **kwargs)

    def exists(self, **kwargs):
        # type: (**Any) -> bool
        """
        Returns True if a file system exists and returns False otherwise.

        :kwarg int timeout:
            The timeout parameter is expressed in seconds.
        :returns: boolean
        """
        return self._container_client.exists(**kwargs)

    def _rename_file_system(self, new_name, **kwargs):
        # type: (str, **Any) -> FileSystemClient
        """Renames a filesystem.

        Operation is successful only if the source filesystem exists.

        :param str new_name:
            The new filesystem name the user wants to rename to.
        :keyword lease:
            Specify this to perform only if the lease ID given
            matches the active lease ID of the source filesystem.
        :paramtype lease: ~azure.storage.filedatalake.DataLakeLeaseClient or str
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: ~azure.storage.filedatalake.FileSystemClient
        """
        self._container_client._rename_container(new_name, **kwargs)   # pylint: disable=protected-access
        #TODO: self._raw_credential would not work with SAS tokens
        renamed_file_system = FileSystemClient(
                "{}://{}".format(self.scheme, self.primary_hostname), file_system_name=new_name,
                credential=self._raw_credential, api_version=self.api_version, _configuration=self._config,
                _pipeline=self._pipeline, _location_mode=self._location_mode, _hosts=self._hosts)
        return renamed_file_system

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

            .. literalinclude:: ../samples/datalake_samples_file_system.py
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

            .. literalinclude:: ../samples/datalake_samples_file_system.py
                :start-after: [START get_file_system_properties]
                :end-before: [END get_file_system_properties]
                :language: python
                :dedent: 12
                :caption: Getting properties on the file system.
        """
        container_properties = self._container_client.get_container_properties(**kwargs)
        return FileSystemProperties._convert_from_container_props(container_properties)  # pylint: disable=protected-access

    def set_file_system_metadata(  # type: ignore
        self, metadata,  # type: Dict[str, str]
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
        :returns: filesystem-updated property dict (Etag and last modified).

        .. admonition:: Example:

            .. literalinclude:: ../samples/datalake_samples_file_system.py
                :start-after: [START set_file_system_metadata]
                :end-before: [END set_file_system_metadata]
                :language: python
                :dedent: 12
                :caption: Setting metadata on the file system.
        """
        return self._container_client.set_container_metadata(metadata=metadata, **kwargs)

    def set_file_system_access_policy(
            self, signed_identifiers,  # type: Dict[str, AccessPolicy]
            public_access=None,  # type: Optional[Union[str, PublicAccess]]
            **kwargs
    ):  # type: (...) -> Dict[str, Union[str, datetime]]
        """Sets the permissions for the specified file system or stored access
        policies that may be used with Shared Access Signatures. The permissions
        indicate whether files in a file system may be accessed publicly.

        :param signed_identifiers:
            A dictionary of access policies to associate with the file system. The
            dictionary may contain up to 5 elements. An empty dictionary
            will clear the access policies set on the service.
        :type signed_identifiers: dict[str, ~azure.storage.filedatalake.AccessPolicy]
        :param ~azure.storage.filedatalake.PublicAccess public_access:
            To specify whether data in the file system may be accessed publicly and the level of access.
        :keyword lease:
            Required if the file system has an active lease. Value can be a DataLakeLeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.filedatalake.DataLakeLeaseClient or str
        :keyword ~datetime.datetime if_modified_since:
            A datetime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only
            if the resource has been modified since the specified date/time.
        :keyword ~datetime.datetime if_unmodified_since:
            A datetime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: File System-updated property dict (Etag and last modified).
        :rtype: dict[str, str or ~datetime.datetime]
        """
        return self._container_client.set_container_access_policy(signed_identifiers,
                                                                  public_access=public_access, **kwargs)

    def get_file_system_access_policy(self, **kwargs):
        # type: (Any) -> Dict[str, Any]
        """Gets the permissions for the specified file system.
        The permissions indicate whether file system data may be accessed publicly.

        :keyword lease:
            If specified, the operation only succeeds if the
            file system's lease is active and matches this ID.
        :paramtype lease: ~azure.storage.filedatalake.DataLakeLeaseClient or str
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: Access policy information in a dict.
        :rtype: dict[str, Any]
        """
        access_policy = self._container_client.get_container_access_policy(**kwargs)
        return {
            'public_access': PublicAccess._from_generated(access_policy['public_access']),  # pylint: disable=protected-access
            'signed_identifiers': access_policy['signed_identifiers']
        }

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
        :keyword upn:
            Optional. Valid only when Hierarchical Namespace is
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

            .. literalinclude:: ../samples/datalake_samples_file_system.py
                :start-after: [START get_paths_in_file_system]
                :end-before: [END get_paths_in_file_system]
                :language: python
                :dedent: 8
                :caption: List the paths in the file system.
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
                         metadata=None,  # type: Optional[Dict[str, str]]
                         **kwargs):
        # type: (...) -> DataLakeDirectoryClient
        """
        Create directory

        :param directory:
            The directory with which to interact. This can either be the name of the directory,
            or an instance of DirectoryProperties.
        :type directory: str or ~azure.storage.filedatalake.DirectoryProperties
        :param metadata:
            Name-value pairs associated with the file as metadata.
        :type metadata: dict(str, str)
        :keyword ~azure.storage.filedatalake.ContentSettings content_settings:
            ContentSettings object used to set path properties.
        :keyword lease:
            Required if the file has an active lease. Value can be a DataLakeLeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.filedatalake.DataLakeLeaseClient or str
        :keyword str umask:
            Optional and only valid if Hierarchical Namespace is enabled for the account.
            When creating a file or directory and the parent folder does not have a default ACL,
            the umask restricts the permissions of the file or directory to be created.
            The resulting permission is given by p & ^u, where p is the permission and u is the umask.
            For example, if p is 0777 and u is 0057, then the resulting permission is 0720.
            The default permission is 0777 for a directory and 0666 for a file. The default umask is 0027.
            The umask must be specified in 4-digit octal notation (e.g. 0766).
        :keyword str owner:
            The owner of the file or directory.
        :keyword str group:
            The owning group of the file or directory.
        :keyword str acl:
            Sets POSIX access control rights on files and directories. The value is a
            comma-separated list of access control entries. Each access control entry (ACE) consists of a
            scope, a type, a user or group identifier, and permissions in the format
            "[scope:][type]:[id]:[permissions]".
        :keyword str lease_id:
            Proposed lease ID, in a GUID string format. The DataLake service returns
            400 (Invalid request) if the proposed lease ID is not in the correct format.
        :keyword int lease_duration:
            Specifies the duration of the lease, in seconds, or negative one
            (-1) for a lease that never expires. A non-infinite lease can be
            between 15 and 60 seconds. A lease duration cannot be changed
            using renew or change.
        :keyword str permissions:
            Optional and only valid if Hierarchical Namespace
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

        .. admonition:: Example:

            .. literalinclude:: ../samples/datalake_samples_file_system.py
                :start-after: [START create_directory_from_file_system]
                :end-before: [END create_directory_from_file_system]
                :language: python
                :dedent: 8
                :caption: Create directory in the file system.
        """
        directory_client = self.get_directory_client(directory)
        directory_client.create_directory(metadata=metadata, **kwargs)
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
            Required if the file has an active lease. Value can be a LeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.filedatalake.DataLakeLeaseClient or str
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

        .. admonition:: Example:

            .. literalinclude:: ../samples/datalake_samples_file_system.py
                :start-after: [START delete_directory_from_file_system]
                :end-before: [END delete_directory_from_file_system]
                :language: python
                :dedent: 8
                :caption: Delete directory in the file system.
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
            Name-value pairs associated with the file as metadata.
        :type metadata: dict(str, str)
        :keyword lease:
            Required if the file has an active lease. Value can be a DataLakeLeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.filedatalake.DataLakeLeaseClient or str
        :keyword str umask:
            Optional and only valid if Hierarchical Namespace is enabled for the account.
            When creating a file or directory and the parent folder does not have a default ACL,
            the umask restricts the permissions of the file or directory to be created.
            The resulting permission is given by p & ^u, where p is the permission and u is the umask.
            For example, if p is 0777 and u is 0057, then the resulting permission is 0720.
            The default permission is 0777 for a directory and 0666 for a file. The default umask is 0027.
            The umask must be specified in 4-digit octal notation (e.g. 0766).
        :keyword str owner:
            The owner of the file or directory.
        :keyword str group:
            The owning group of the file or directory.
        :keyword str acl:
            Sets POSIX access control rights on files and directories. The value is a
            comma-separated list of access control entries. Each access control entry (ACE) consists of a
            scope, a type, a user or group identifier, and permissions in the format
            "[scope:][type]:[id]:[permissions]".
        :keyword str lease_id:
            Proposed lease ID, in a GUID string format. The DataLake service returns
            400 (Invalid request) if the proposed lease ID is not in the correct format.
        :keyword int lease_duration:
            Specifies the duration of the lease, in seconds, or negative one
            (-1) for a lease that never expires. A non-infinite lease can be
            between 15 and 60 seconds. A lease duration cannot be changed
            using renew or change.
        :keyword expires_on:
            The time to set the file to expiry.
            If the type of expires_on is an int, expiration time will be set
            as the number of milliseconds elapsed from creation time.
            If the type of expires_on is datetime, expiration time will be set
            absolute to the time provided. If no time zone info is provided, this
            will be interpreted as UTC.
        :paramtype expires_on: datetime or int
        :keyword str permissions:
            Optional and only valid if Hierarchical Namespace
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

        .. admonition:: Example:

            .. literalinclude:: ../samples/datalake_samples_file_system.py
                :start-after: [START create_file_from_file_system]
                :end-before: [END create_file_from_file_system]
                :language: python
                :dedent: 8
                :caption: Create file in the file system.
        """
        file_client = self.get_file_client(file)
        file_client.create_file(**kwargs)
        return file_client

    def delete_file(self, file,  # type: Union[FileProperties, str]
                    **kwargs):
        # type: (...) -> DataLakeFileClient
        """
        Marks the specified file for deletion.

        :param file:
            The file with which to interact. This can either be the name of the file,
            or an instance of FileProperties.
        :type file: str or ~azure.storage.filedatalake.FileProperties
        :keyword lease:
            Required if the file has an active lease. Value can be a LeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.filedatalake.DataLakeLeaseClient or str
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

        .. admonition:: Example:

            .. literalinclude:: ../samples/datalake_samples_file_system.py
                :start-after: [START delete_file_from_file_system]
                :end-before: [END delete_file_from_file_system]
                :language: python
                :dedent: 8
                :caption: Delete file in the file system.
        """
        file_client = self.get_file_client(file)
        file_client.delete_file(**kwargs)
        return file_client

    def _undelete_path_options(self, deleted_path_name, deletion_id):
        quoted_path = quote(unquote(deleted_path_name.strip('/')))

        url_and_token = self.url.replace('.dfs.', '.blob.').split('?')
        try:
            url = url_and_token[0] + '/' + quoted_path + url_and_token[1]
        except IndexError:
            url = url_and_token[0] + '/' + quoted_path

        undelete_source = quoted_path + '?deletionid={}'.format(deletion_id) if deletion_id else None

        return quoted_path, url, undelete_source

    def _undelete_path(self, deleted_path_name, deletion_id, **kwargs):
        # type: (str, str, **Any) -> Union[DataLakeDirectoryClient, DataLakeFileClient]
        """Restores soft-deleted path.

        Operation will only be successful if used within the specified number of days
        set in the delete retention policy.

        .. versionadded:: 12.4.0
            This operation was introduced in API version '2020-06-12'.

        :param str deleted_path_name:
            Specifies the path (file or directory) to restore.
        :param str deletion_id:
            Specifies the version of the deleted path to restore.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: ~azure.storage.file.datalake.DataLakeDirectoryClient or azure.storage.file.datalake.DataLakeFileClient
        """
        _, url, undelete_source = self._undelete_path_options(deleted_path_name, deletion_id)

        pipeline = Pipeline(
            transport=TransportWrapper(self._pipeline._transport), # pylint: disable = protected-access
            policies=self._pipeline._impl_policies # pylint: disable = protected-access
        )
        path_client = AzureDataLakeStorageRESTAPI(
            url, filesystem=self.file_system_name, path=deleted_path_name, pipeline=pipeline)
        try:
            is_file = path_client.path.undelete(undelete_source=undelete_source, cls=is_file_path, **kwargs)
            if is_file:
                return self.get_file_client(deleted_path_name)
            return self.get_directory_client(deleted_path_name)
        except HttpResponseError as error:
            process_storage_error(error)

    def _get_root_directory_client(self):
        # type: () -> DataLakeDirectoryClient
        """Get a client to interact with the root directory.

        :returns: A DataLakeDirectoryClient.
        :rtype: ~azure.storage.filedatalake.DataLakeDirectoryClient
        """
        return self.get_directory_client('/')

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

            .. literalinclude:: ../samples/datalake_samples_file_system.py
                :start-after: [START get_directory_client_from_file_system]
                :end-before: [END get_directory_client_from_file_system]
                :language: python
                :dedent: 8
                :caption: Getting the directory client to interact with a specific directory.
        """
        try:
            directory_name = directory.get('name')
        except AttributeError:
            directory_name = str(directory)
        _pipeline = Pipeline(
            transport=TransportWrapper(self._pipeline._transport), # pylint: disable = protected-access
            policies=self._pipeline._impl_policies # pylint: disable = protected-access
        )
        return DataLakeDirectoryClient(self.url, self.file_system_name, directory_name=directory_name,
                                       credential=self._raw_credential,
                                       api_version=self.api_version,
                                       _configuration=self._config, _pipeline=_pipeline,
                                       _hosts=self._hosts)

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
        :rtype: ~azure.storage.filedatalake.DataLakeFileClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/datalake_samples_file_system.py
                :start-after: [START get_file_client_from_file_system]
                :end-before: [END get_file_client_from_file_system]
                :language: python
                :dedent: 8
                :caption: Getting the file client to interact with a specific file.
        """
        try:
            file_path = file_path.get('name')
        except AttributeError:
            file_path = str(file_path)
        _pipeline = Pipeline(
            transport=TransportWrapper(self._pipeline._transport), # pylint: disable = protected-access
            policies=self._pipeline._impl_policies # pylint: disable = protected-access
        )
        return DataLakeFileClient(
            self.url, self.file_system_name, file_path=file_path, credential=self._raw_credential,
            api_version=self.api_version,
            _hosts=self._hosts, _configuration=self._config, _pipeline=_pipeline)

    def list_deleted_paths(self, **kwargs):
        # type: (Any) -> ItemPaged[DeletedPathProperties]
        """Returns a generator to list the deleted (file or directory) paths under the specified file system.
        The generator will lazily follow the continuation tokens returned by
        the service.

        .. versionadded:: 12.4.0
            This operation was introduced in API version '2020-06-12'.

        :keyword str path_prefix:
            Filters the results to return only paths under the specified path.
        :keyword int results_per_page:
            An optional value that specifies the maximum number of items to return per page.
            If omitted or greater than 5,000, the response will include up to 5,000 items per page.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: An iterable (auto-paging) response of DeletedPathProperties.
        :rtype:
            ~azure.core.paging.ItemPaged[~azure.storage.filedatalake.DeletedPathProperties]
        """
        path_prefix = kwargs.pop('path_prefix', None)
        timeout = kwargs.pop('timeout', None)
        results_per_page = kwargs.pop('results_per_page', None)
        command = functools.partial(
            self._datalake_client_for_blob_operation.file_system.list_blob_hierarchy_segment,
            showonly=ListBlobsIncludeItem.deleted,
            timeout=timeout,
            **kwargs)
        return ItemPaged(
            command, prefix=path_prefix, page_iterator_class=DeletedPathPropertiesPaged,
            results_per_page=results_per_page, **kwargs)
