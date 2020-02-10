# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.core.paging import ItemPaged

from azure.storage.blob.aio import BlobServiceClient
from .._generated.aio import DataLakeStorageClient
from .._shared.base_client_async import AsyncStorageAccountHostsMixin
from ._file_system_client_async import FileSystemClient
from .._data_lake_service_client import DataLakeServiceClient as DataLakeServiceClientBase
from .._shared.policies_async import ExponentialRetry
from ._data_lake_directory_client_async import DataLakeDirectoryClient
from ._data_lake_file_client_async import DataLakeFileClient
from ._models import FileSystemPropertiesPaged
from .._models import UserDelegationKey


class DataLakeServiceClient(AsyncStorageAccountHostsMixin, DataLakeServiceClientBase):
    """A client to interact with the DataLake Service at the account level.

    This client provides operations to retrieve and configure the account properties
    as well as list, create and delete file systems within the account.
    For operations relating to a specific file system, directory or file, clients for those entities
    can also be retrieved using the `get_client` functions.

    :ivar str url:
        The full endpoint URL to the datalake service endpoint. This could be either the
        primary endpoint, or the secondary endpoint depending on the current `location_mode`.
    :ivar str primary_endpoint:
        The full primary endpoint URL.
    :ivar str primary_hostname:
        The hostname of the primary endpoint.
    :param str account_url:
        The URL to the DataLake storage account. Any other entities included
        in the URL path (e.g. file system or file) will be discarded. This URL can be optionally
        authenticated with a SAS token.
    :param credential:
        The credentials with which to authenticate. This is optional if the
        account URL already has a SAS token. The value can be a SAS token string, and account
        shared access key, or an instance of a TokenCredentials class from azure.identity.
        If the URL already has a SAS token, specifying an explicit credential will take priority.

    .. admonition:: Example:

        .. literalinclude:: ../samples/test_datalake_authentication_samples.py
            :start-after: [START create_datalake_service_client]
            :end-before: [END create_datalake_service_client]
            :language: python
            :dedent: 8
            :caption: Creating the DataLakeServiceClient with account url and credential.

        .. literalinclude:: ../samples/test_datalake_authentication_samples.py
            :start-after: [START create_datalake_service_client_oauth]
            :end-before: [END create_datalake_service_client_oauth]
            :language: python
            :dedent: 8
            :caption: Creating the DataLakeServiceClient with Azure Identity credentials.
    """

    def __init__(
            self, account_url,  # type: str
            credential=None,  # type: Optional[Any]
            **kwargs  # type: Any
    ):
        # type: (...) -> None
        kwargs['retry_policy'] = kwargs.get('retry_policy') or ExponentialRetry(**kwargs)
        super(DataLakeServiceClient, self).__init__(
            account_url,
            credential=credential,
            **kwargs
        )
        self._blob_service_client = BlobServiceClient(self._blob_account_url, credential, **kwargs)
        self._client = DataLakeStorageClient(self.url, None, None, pipeline=self._pipeline)
        self._loop = kwargs.get('loop', None)

    async def get_user_delegation_key(self, key_start_time,  # type: datetime
                                      key_expiry_time,  # type: datetime
                                      **kwargs  # type: Any
                                      ):
        # type: (...) -> UserDelegationKey
        """
        Obtain a user delegation key for the purpose of signing SAS tokens.
        A token credential must be present on the service object for this request to succeed.

        :param ~datetime.datetime key_start_time:
            A DateTime value. Indicates when the key becomes valid.
        :param ~datetime.datetime key_expiry_time:
            A DateTime value. Indicates when the key stops being valid.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :return: The user delegation key.
        :rtype: ~azure.storage.filedatalake.UserDelegationKey
        """
        delegation_key = await self._blob_service_client.get_user_delegation_key(
            key_start_time=key_start_time,
            key_expiry_time=key_expiry_time,
            **kwargs)  # pylint: disable=protected-access
        delegation_key._class_ = UserDelegationKey  # pylint: disable=protected-access
        return delegation_key

    def list_file_systems(self, name_starts_with=None,  # type: Optional[str]
                          include_metadata=None,  # type: Optional[bool]
                          **kwargs):
        # type: (...) -> ItemPaged[FileSystemProperties]
        """Returns a generator to list the file systems under the specified account.

        The generator will lazily follow the continuation tokens returned by
        the service and stop when all file systems have been returned.

        :param str name_starts_with:
            Filters the results to return only file systems whose names
            begin with the specified prefix.
        :param bool include_metadata:
            Specifies that file system metadata be returned in the response.
            The default value is `False`.
        :keyword int results_per_page:
            The maximum number of file system names to retrieve per API
            call. If the request does not specify the server will return up to 5,000 items per page.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: An iterable (auto-paging) of FileSystemProperties.
        :rtype: ~azure.core.paging.ItemPaged[~azure.storage.filedatalake.FileSystemProperties]

        .. admonition:: Example:

            .. literalinclude:: ../samples/test_datalake_service_samples.py
                :start-after: [START dsc_list_file_systems]
                :end-before: [END dsc_list_file_systems]
                :language: python
                :dedent: 12
                :caption: Listing the file systems in the datalake service.
        """
        item_paged = self._blob_service_client.list_containers(name_starts_with=name_starts_with,
                                                               include_metadata=include_metadata,
                                                               **kwargs)  # pylint: disable=protected-access
        item_paged._page_iterator_class = FileSystemPropertiesPaged  # pylint: disable=protected-access
        return item_paged

    async def create_file_system(self, file_system,  # type: Union[FileSystemProperties, str]
                                 metadata=None,  # type: Optional[Dict[str, str]]
                                 public_access=None,  # type: Optional[PublicAccess]
                                 **kwargs):
        # type: (...) -> FileSystemClient
        """Creates a new file system under the specified account.

        If the file system with the same name already exists, a ResourceExistsError will
        be raised. This method returns a client with which to interact with the newly
        created file system.

        :param str file_system: The name of the file system to create.
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

            .. literalinclude:: ../samples/test_datalake_service_samples.py
                :start-after: [START dsc_create_file_system]
                :end-before: [END dsc_create_file_system]
                :language: python
                :dedent: 12
                :caption: Creating a file system in the datalake service.
        """
        file_system_client = self.get_file_system_client(file_system)
        await file_system_client.create_file_system(metadata=metadata, public_access=public_access, **kwargs)
        return file_system_client

    async def delete_file_system(self, file_system,  # type: Union[FileSystemProperties, str]
                                 **kwargs):
        # type: (...) -> FileSystemClient
        """Marks the specified file system for deletion.

        The file system and any files contained within it are later deleted during garbage collection.
        If the file system is not found, a ResourceNotFoundError will be raised.

        :param file_system:
            The file system to delete. This can either be the name of the file system,
            or an instance of FileSystemProperties.
        :type file_system: str or ~azure.storage.filedatalake.FileSystemProperties
        :keyword ~azure.storage.filedatalake.DataLakeLeaseClient lease:
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

            .. literalinclude:: ../samples/test_datalake_service_samples.py
                :start-after: [START bsc_delete_file_system]
                :end-before: [END bsc_delete_file_system]
                :language: python
                :dedent: 12
                :caption: Deleting a file system in the datalake service.
        """
        file_system_client = self.get_file_system_client(file_system)
        await file_system_client.delete_file_system(**kwargs)
        return file_system_client

    def get_file_system_client(self, file_system  # type: Union[FileSystemProperties, str]
                               ):
        # type: (...) -> FileSystemClient
        """Get a client to interact with the specified file system.

        The file system need not already exist.

        :param file_system:
            The file system. This can either be the name of the file system,
            or an instance of FileSystemProperties.
        :type file_system: str or ~azure.storage.filedatalake.FileSystemProperties
        :returns: A FileSystemClient.
        :rtype: ~azure.storage.filedatalake.FileSystemClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/test_datalake_service_samples.py
                :start-after: [START bsc_get_file_system_client]
                :end-before: [END bsc_get_file_system_client]
                :language: python
                :dedent: 8
                :caption: Getting the file system client to interact with a specific file system.
        """
        return FileSystemClient(self.url, file_system, credential=self._raw_credential, _configuration=self._config,
                                _pipeline=self._pipeline, _location_mode=self._location_mode, _hosts=self._hosts,
                                require_encryption=self.require_encryption, key_encryption_key=self.key_encryption_key,
                                key_resolver_function=self.key_resolver_function)

    def get_directory_client(self, file_system,  # type: Union[FileSystemProperties, str]
                             directory  # type: Union[DirectoryProperties, str]
                             ):
        # type: (...) -> DataLakeDirectoryClient
        """Get a client to interact with the specified directory.

        The directory need not already exist.

        :param file_system:
            The file system that the directory is in. This can either be the name of the file system,
            or an instance of FileSystemProperties.
        :type file_system: str or ~azure.storage.filedatalake.FileSystemProperties
        :param directory:
            The directory with which to interact. This can either be the name of the directory,
            or an instance of DirectoryProperties.
        :type directory: str or ~azure.storage.filedatalake.DirectoryProperties
        :returns: A DataLakeDirectoryClient.
        :rtype: ~azure.storage.filedatalake.DataLakeDirectoryClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/test_datalake_service_samples.py
                :start-after: [START bsc_get_directory_client]
                :end-before: [END bsc_get_directory_client]
                :language: python
                :dedent: 12
                :caption: Getting the directory client to interact with a specific directory.
        """
        return DataLakeDirectoryClient(self.url, file_system, directory_name=directory,
                                       credential=self._raw_credential,
                                       _configuration=self._config, _pipeline=self._pipeline,
                                       _location_mode=self._location_mode, _hosts=self._hosts,
                                       require_encryption=self.require_encryption,
                                       key_encryption_key=self.key_encryption_key,
                                       key_resolver_function=self.key_resolver_function
                                       )

    def get_file_client(self, file_system,  # type: Union[FileSystemProperties, str]
                        file_path  # type: Union[FileProperties, str]
                        ):
        # type: (...) -> DataLakeFileClient
        """Get a client to interact with the specified file.

        The file need not already exist.

        :param file_system:
            The file system that the file is in. This can either be the name of the file system,
            or an instance of FileSystemProperties.
        :type file_system: str or ~azure.storage.filedatalake.FileSystemProperties
        :param file_path:
            The file with which to interact. This can either be the full path of the file(from the root directory),
            or an instance of FileProperties. eg. directory/subdirectory/file
        :type file_path: str or ~azure.storage.filedatalake.FileProperties
        :returns: A DataLakeFileClient.
        :rtype: ~azure.storage.filedatalake..DataLakeFileClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/test_datalake_service_samples.py
                :start-after: [START bsc_get_file_client]
                :end-before: [END bsc_get_file_client]
                :language: python
                :dedent: 12
                :caption: Getting the file client to interact with a specific file.
        """
        try:
            file_path = file_path.name
        except AttributeError:
            pass

        return DataLakeFileClient(
            self.url, file_system, file_path=file_path, credential=self._raw_credential,
            _hosts=self._hosts, _configuration=self._config, _pipeline=self._pipeline,
            _location_mode=self._location_mode, require_encryption=self.require_encryption,
            key_encryption_key=self.key_encryption_key,
            key_resolver_function=self.key_resolver_function)
