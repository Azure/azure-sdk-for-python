# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=invalid-overridden-method
from datetime import datetime
from typing import ( # pylint: disable=unused-import
    Any, Dict, Optional, Union,
    TYPE_CHECKING)

from azure.core.exceptions import AzureError, HttpResponseError
from azure.storage.blob.aio import BlobClient
from .._serialize import get_api_version
from .._shared.base_client_async import AsyncStorageAccountHostsMixin
from .._path_client import PathClient as PathClientBase
from .._models import DirectoryProperties, AccessControlChangeResult, AccessControlChangeFailure, \
    AccessControlChangeCounters, AccessControlChanges
from .._generated.aio import AzureDataLakeStorageRESTAPI
from ._data_lake_lease_async import DataLakeLeaseClient
from .._deserialize import process_storage_error
from .._shared.policies_async import ExponentialRetry

if TYPE_CHECKING:
    from .._models import ContentSettings, FileProperties


class PathClient(AsyncStorageAccountHostsMixin, PathClientBase):
    """A base client for interacting with a DataLake file/directory, even if the file/directory may not
    yet exist.

    :param str account_url:
        The URI to the storage account.
    :param str file_system_name:
        The file system for the directory or files.
    :param str file_path:
        The whole file path, so that to interact with a specific file.
        eg. "{directory}/{subdirectory}/{file}"
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
    """
    def __init__(
            self, account_url,  # type: str
            file_system_name,  # type: str
            path_name,  # type: str
            credential=None,  # type: Optional[Any]
            **kwargs  # type: Any
    ):
        # type: (...) -> None
        kwargs['retry_policy'] = kwargs.get('retry_policy') or ExponentialRetry(**kwargs)

        super(PathClient, self).__init__(account_url,  # pylint: disable=specify-parameter-names-in-call
                                         file_system_name, path_name,
                                         credential=credential,
                                         **kwargs)  # type: ignore

        kwargs.pop('_hosts', None)

        self._blob_client = BlobClient(account_url=self._blob_account_url, container_name=self.file_system_name,
                                       blob_name=self.path_name,
                                       credential=credential,
                                       _hosts=self._blob_client._hosts,  # pylint: disable=protected-access
                                       **kwargs)

        self._client = AzureDataLakeStorageRESTAPI(self.url, base_url=self.url, file_system=self.file_system_name,
                                                   path=self.path_name, pipeline=self._pipeline)
        self._datalake_client_for_blob_operation = AzureDataLakeStorageRESTAPI(self._blob_client.url,
                                                                               base_url=self._blob_client.url,
                                                                               file_system=self.file_system_name,
                                                                               path=self.path_name,
                                                                               pipeline=self._pipeline)
        api_version = get_api_version(kwargs)
        self._client._config.version = api_version  # pylint: disable=protected-access
        self._datalake_client_for_blob_operation._config.version = api_version  # pylint: disable=protected-access

        self._loop = kwargs.get('loop', None)

    async def __aexit__(self, *args):
        await self._blob_client.close()
        await super(PathClient, self).__aexit__(*args)

    async def close(self):
        # type: () -> None
        """ This method is to close the sockets opened by the client.
        It need not be used when using with a context manager.
        """
        await self._blob_client.close()
        await self.__aexit__()

    async def _create(self, resource_type, content_settings=None, metadata=None, **kwargs):
        # type: (...) -> Dict[str, Union[str, datetime]]
        """
        Create directory or file

        :param resource_type:
            Required for Create File and Create Directory.
            The value must be "file" or "directory". Possible values include:
            'directory', 'file'
        :type resource_type: str
        :param ~azure.storage.filedatalake.ContentSettings content_settings:
            ContentSettings object used to set path properties.
        :param metadata:
            Name-value pairs associated with the file/directory as metadata.
        :type metadata: dict(str, str)
        :keyword lease:
            Required if the file/directory has an active lease. Value can be a DataLakeLeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.filedatalake.aio.DataLakeLeaseClient or str
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
        :keyword permissions:
            Optional and only valid if Hierarchical Namespace
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
        :keyword str etag:
            An ETag value, or the wildcard character (*). Used to check if the resource has changed,
            and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition:
            The match condition to use upon the etag.
        :keyword ~azure.storage.filedatalake.CustomerProvidedEncryptionKey cpk:
            Encrypts the data on the service-side with the given key.
            Use of customer-provided keys must be done over HTTPS.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :return: A dictionary of response headers.
        :rtype: Dict[str, Union[str, datetime]]
        """
        lease_id = kwargs.get('lease_id', None)
        lease_duration = kwargs.get('lease_duration', None)
        if lease_id and not lease_duration:
            raise ValueError("Please specify a lease_id and a lease_duration.")
        if lease_duration and not lease_id:
            raise ValueError("Please specify a lease_id and a lease_duration.")
        options = self._create_path_options(
            resource_type,
            content_settings=content_settings,
            metadata=metadata,
            **kwargs)
        try:
            return await self._client.path.create(**options)
        except HttpResponseError as error:
            process_storage_error(error)

    async def _delete(self, **kwargs):
        # type: (**Any) -> Dict[Union[datetime, str]]
        """
        Marks the specified path for deletion.

        :keyword lease:
            Required if the file/directory has an active lease. Value can be a LeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.filedatalake.aio.DataLakeLeaseClient or str
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
        :return: None
        """
        options = self._delete_path_options(**kwargs)
        try:
            return await self._client.path.delete(**options)
        except HttpResponseError as error:
            process_storage_error(error)

    async def set_access_control(self, owner=None,  # type: Optional[str]
                                 group=None,  # type: Optional[str]
                                 permissions=None,  # type: Optional[str]
                                 acl=None,  # type: Optional[str]
                                 **kwargs):
        # type: (...) -> Dict[str, Union[str, datetime]]
        """
        Set the owner, group, permissions, or access control list for a path.

        :param owner:
            Optional. The owner of the file or directory.
        :type owner: str
        :param group:
            Optional. The owning group of the file or directory.
        :type group: str
        :param permissions:
            Optional and only valid if Hierarchical Namespace
            is enabled for the account. Sets POSIX access permissions for the file
            owner, the file owning group, and others. Each class may be granted
            read, write, or execute permission.  The sticky bit is also supported.
            Both symbolic (rwxrw-rw-) and 4-digit octal notation (e.g. 0766) are
            supported.
            permissions and acl are mutually exclusive.
        :type permissions: str
        :param acl:
            Sets POSIX access control rights on files and directories.
            The value is a comma-separated list of access control entries. Each
            access control entry (ACE) consists of a scope, a type, a user or
            group identifier, and permissions in the format
            "[scope:][type]:[id]:[permissions]".
            permissions and acl are mutually exclusive.
        :type acl: str
        :keyword lease:
            Required if the file/directory has an active lease. Value can be a LeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.filedatalake.aio.DataLakeLeaseClient or str
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
        :keyword: response dict (Etag and last modified).
        """
        options = self._set_access_control_options(owner=owner, group=group, permissions=permissions, acl=acl, **kwargs)
        try:
            return await self._client.path.set_access_control(**options)
        except HttpResponseError as error:
            process_storage_error(error)

    async def get_access_control(self, upn=None,  # type: Optional[bool]
                                 **kwargs):
        # type: (...) -> Dict[str, Any]
        """
        Get the owner, group, permissions, or access control list for a path.

        :param upn:
            Optional. Valid only when Hierarchical Namespace is
            enabled for the account. If "true", the user identity values returned
            in the x-ms-owner, x-ms-group, and x-ms-acl response headers will be
            transformed from Azure Active Directory Object IDs to User Principal
            Names.  If "false", the values will be returned as Azure Active
            Directory Object IDs. The default value is false. Note that group and
            application Object IDs are not translated because they do not have
            unique friendly names.
        :type upn: bool
        :keyword lease:
            Required if the file/directory has an active lease. Value can be a LeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.filedatalake.aio.DataLakeLeaseClient or str
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
        :keyword: response dict.
        """
        options = self._get_access_control_options(upn=upn, **kwargs)
        try:
            return await self._client.path.get_properties(**options)
        except HttpResponseError as error:
            process_storage_error(error)

    async def set_access_control_recursive(self,
                                           acl,
                                           **kwargs):
        # type: (str, **Any) -> AccessControlChangeResult
        """
        Sets the Access Control on a path and sub-paths.

        :param acl:
            Sets POSIX access control rights on files and directories.
            The value is a comma-separated list of access control entries. Each
            access control entry (ACE) consists of a scope, a type, a user or
            group identifier, and permissions in the format
            "[scope:][type]:[id]:[permissions]".
        :type acl: str
        :keyword func(~azure.storage.filedatalake.AccessControlChanges) progress_hook:
            Callback where the caller can track progress of the operation
            as well as collect paths that failed to change Access Control.
        :keyword str continuation_token:
            Optional continuation token that can be used to resume previously stopped operation.
        :keyword int batch_size:
            Optional. If data set size exceeds batch size then operation will be split into multiple
            requests so that progress can be tracked. Batch size should be between 1 and 2000.
            The default when unspecified is 2000.
        :keyword int max_batches:
            Optional. Defines maximum number of batches that single change Access Control operation can execute.
            If maximum is reached before all sub-paths are processed,
            then continuation token can be used to resume operation.
            Empty value indicates that maximum number of batches in unbound and operation continues till end.
        :keyword bool continue_on_failure:
            If set to False, the operation will terminate quickly on encountering user errors (4XX).
            If True, the operation will ignore user errors and proceed with the operation on other sub-entities of
            the directory.
            Continuation token will only be returned when continue_on_failure is True in case of user errors.
            If not set the default value is False for this.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :return: A summary of the recursive operations, including the count of successes and failures,
            as well as a continuation token in case the operation was terminated prematurely.
        :rtype: :~azure.storage.filedatalake.AccessControlChangeResult`
        :raises ~azure.core.exceptions.AzureError:
            User can restart the operation using continuation_token field of AzureError if the token is available.
        """
        if not acl:
            raise ValueError("The Access Control List must be set for this operation")

        progress_hook = kwargs.pop('progress_hook', None)
        max_batches = kwargs.pop('max_batches', None)
        options = self._set_access_control_recursive_options(mode='set', acl=acl, **kwargs)
        return await self._set_access_control_internal(options=options, progress_hook=progress_hook,
                                                       max_batches=max_batches)

    async def update_access_control_recursive(self, acl, **kwargs):
        # type: (str, **Any) -> AccessControlChangeResult
        """
        Modifies the Access Control on a path and sub-paths.

        :param acl:
            Modifies POSIX access control rights on files and directories.
            The value is a comma-separated list of access control entries. Each
            access control entry (ACE) consists of a scope, a type, a user or
            group identifier, and permissions in the format
            "[scope:][type]:[id]:[permissions]".
        :type acl: str
        :keyword func(~azure.storage.filedatalake.AccessControlChanges) progress_hook:
            Callback where the caller can track progress of the operation
            as well as collect paths that failed to change Access Control.
        :keyword str continuation_token:
            Optional continuation token that can be used to resume previously stopped operation.
        :keyword int batch_size:
            Optional. If data set size exceeds batch size then operation will be split into multiple
            requests so that progress can be tracked. Batch size should be between 1 and 2000.
            The default when unspecified is 2000.
        :keyword int max_batches:
            Optional. Defines maximum number of batches that single,
            change Access Control operation can execute.
            If maximum is reached before all sub-paths are processed,
            then continuation token can be used to resume operation.
            Empty value indicates that maximum number of batches in unbound and operation continues till end.
        :keyword bool continue_on_failure:
            If set to False, the operation will terminate quickly on encountering user errors (4XX).
            If True, the operation will ignore user errors and proceed with the operation on other sub-entities of
            the directory.
            Continuation token will only be returned when continue_on_failure is True in case of user errors.
            If not set the default value is False for this.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :return: A summary of the recursive operations, including the count of successes and failures,
            as well as a continuation token in case the operation was terminated prematurely.
        :rtype: :~azure.storage.filedatalake.AccessControlChangeResult`
        :raises ~azure.core.exceptions.AzureError:
            User can restart the operation using continuation_token field of AzureError if the token is available.
        """
        if not acl:
            raise ValueError("The Access Control List must be set for this operation")

        progress_hook = kwargs.pop('progress_hook', None)
        max_batches = kwargs.pop('max_batches', None)
        options = self._set_access_control_recursive_options(mode='modify', acl=acl, **kwargs)
        return await self._set_access_control_internal(options=options, progress_hook=progress_hook,
                                                       max_batches=max_batches)

    async def remove_access_control_recursive(self,
                                              acl,
                                              **kwargs):
        # type: (str, **Any) -> AccessControlChangeResult
        """
        Removes the Access Control on a path and sub-paths.

        :param acl:
            Removes POSIX access control rights on files and directories.
            The value is a comma-separated list of access control entries. Each
            access control entry (ACE) consists of a scope, a type, and a user or
            group identifier in the format "[scope:][type]:[id]".
        :type acl: str
        :keyword func(~azure.storage.filedatalake.AccessControlChanges) progress_hook:
            Callback where the caller can track progress of the operation
            as well as collect paths that failed to change Access Control.
        :keyword str continuation_token:
            Optional continuation token that can be used to resume previously stopped operation.
        :keyword int batch_size:
            Optional. If data set size exceeds batch size then operation will be split into multiple
            requests so that progress can be tracked. Batch size should be between 1 and 2000.
            The default when unspecified is 2000.
        :keyword int max_batches:
            Optional. Defines maximum number of batches that single change Access Control operation can execute.
            If maximum is reached before all sub-paths are processed,
            then continuation token can be used to resume operation.
            Empty value indicates that maximum number of batches in unbound and operation continues till end.
        :keyword bool continue_on_failure:
            If set to False, the operation will terminate quickly on encountering user errors (4XX).
            If True, the operation will ignore user errors and proceed with the operation on other sub-entities of
            the directory.
            Continuation token will only be returned when continue_on_failure is True in case of user errors.
            If not set the default value is False for this.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :return: A summary of the recursive operations, including the count of successes and failures,
            as well as a continuation token in case the operation was terminated prematurely.
        :rtype: :~azure.storage.filedatalake.AccessControlChangeResult`
        :raises ~azure.core.exceptions.AzureError:
            User can restart the operation using continuation_token field of AzureError if the token is available.
        """
        if not acl:
            raise ValueError("The Access Control List must be set for this operation")

        progress_hook = kwargs.pop('progress_hook', None)
        max_batches = kwargs.pop('max_batches', None)
        options = self._set_access_control_recursive_options(mode='remove', acl=acl, **kwargs)
        return await self._set_access_control_internal(options=options, progress_hook=progress_hook,
                                                       max_batches=max_batches)

    async def _set_access_control_internal(self, options, progress_hook, max_batches=None):
        try:
            continue_on_failure = options.get('force_flag')
            total_directories_successful = 0
            total_files_success = 0
            total_failure_count = 0
            batch_count = 0
            last_continuation_token = None
            current_continuation_token = None
            continue_operation = True
            while continue_operation:
                headers, resp = await self._client.path.set_access_control_recursive(**options)

                # make a running tally so that we can report the final results
                total_directories_successful += resp.directories_successful
                total_files_success += resp.files_successful
                total_failure_count += resp.failure_count
                batch_count += 1
                current_continuation_token = headers['continuation']

                if current_continuation_token is not None:
                    last_continuation_token = current_continuation_token

                if progress_hook is not None:
                    await progress_hook(AccessControlChanges(
                        batch_counters=AccessControlChangeCounters(
                            directories_successful=resp.directories_successful,
                            files_successful=resp.files_successful,
                            failure_count=resp.failure_count,
                        ),
                        aggregate_counters=AccessControlChangeCounters(
                            directories_successful=total_directories_successful,
                            files_successful=total_files_success,
                            failure_count=total_failure_count,
                        ),
                        batch_failures=[AccessControlChangeFailure(
                            name=failure.name,
                            is_directory=failure.type == 'DIRECTORY',
                            error_message=failure.error_message) for failure in resp.failed_entries],
                        continuation=last_continuation_token))

                # update the continuation token, if there are more operations that cannot be completed in a single call
                max_batches_satisfied = (max_batches is not None and batch_count == max_batches)
                continue_operation = bool(current_continuation_token) and not max_batches_satisfied
                options['continuation'] = current_continuation_token

            # currently the service stops on any failure, so we should send back the last continuation token
            # for the user to retry the failed updates
            # otherwise we should just return what the service gave us
            return AccessControlChangeResult(counters=AccessControlChangeCounters(
                directories_successful=total_directories_successful,
                files_successful=total_files_success,
                failure_count=total_failure_count),
                continuation=last_continuation_token
                if total_failure_count > 0 and not continue_on_failure else current_continuation_token)
        except HttpResponseError as error:
            error.continuation_token = last_continuation_token
            process_storage_error(error)
        except AzureError as error:
            error.continuation_token = last_continuation_token
            raise error

    async def _rename_path(self, rename_source, **kwargs):
        # type: (str, **Any) -> Dict[str, Any]
        """
        Rename directory or file

        :param rename_source: The value must have the following format: "/{filesystem}/{path}".
        :type rename_source: str
        :keyword ~azure.storage.filedatalake.ContentSettings content_settings:
            ContentSettings object used to set path properties.
        :keyword source_lease: A lease ID for the source path. If specified,
            the source path must have an active lease and the leaase ID must
            match.
        :paramtype source_lease: ~azure.storage.filedatalake.aio.DataLakeLeaseClient or str
        :keyword lease:
            Required if the file/directory has an active lease. Value can be a LeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.filedatalake.aio.DataLakeLeaseClient or str
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
        :keyword str source_etag:
            The source ETag value, or the wildcard character (*). Used to check if the resource has changed,
            and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions source_match_condition:
            The source match condition to use upon the etag.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        """
        options = self._rename_path_options(
            rename_source,
            **kwargs)
        try:
            return await self._client.path.create(**options)
        except HttpResponseError as error:
            process_storage_error(error)

    async def _get_path_properties(self, **kwargs):
        # type: (**Any) -> Union[FileProperties, DirectoryProperties]
        """Returns all user-defined metadata, standard HTTP properties, and
        system properties for the file or directory. It does not return the content of the directory or file.

        :keyword lease:
            Required if the directory or file has an active lease. Value can be a DataLakeLeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.filedatalake.aio.DataLakeLeaseClient or str
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
        :keyword ~azure.storage.filedatalake.CustomerProvidedEncryptionKey cpk:
            Decrypts the data on the service-side with the given key.
            Use of customer-provided keys must be done over HTTPS.
            Required if the file/directory was created with a customer-provided key.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: DirectoryProperties or FileProperties
        """
        path_properties = await self._blob_client.get_blob_properties(**kwargs)
        return path_properties

    async def _exists(self, **kwargs):
        # type: (**Any) -> bool
        """
        Returns True if a path exists and returns False otherwise.

        :kwarg int timeout:
            The timeout parameter is expressed in seconds.
        :returns: boolean
        """
        return await self._blob_client.exists(**kwargs)

    async def set_metadata(self, metadata,  # type: Dict[str, str]
                           **kwargs):
        # type: (...) -> Dict[str, Union[str, datetime]]
        """Sets one or more user-defined name-value pairs for the specified
        file system. Each call to this operation replaces all existing metadata
        attached to the file system. To remove all metadata from the file system,
        call this operation with no metadata dict.

        :param metadata:
            A dict containing name-value pairs to associate with the file system as
            metadata. Example: {'category':'test'}
        :type metadata: dict[str, str]
        :keyword lease:
            If specified, set_file_system_metadata only succeeds if the
            file system's lease is active and matches this ID.
        :paramtype lease: ~azure.storage.filedatalake.aio.DataLakeLeaseClient or str
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
        :keyword ~azure.storage.filedatalake.CustomerProvidedEncryptionKey cpk:
            Encrypts the data on the service-side with the given key.
            Use of customer-provided keys must be done over HTTPS.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: file system-updated property dict (Etag and last modified).
        """
        return await self._blob_client.set_blob_metadata(metadata=metadata, **kwargs)

    async def set_http_headers(self, content_settings=None,  # type: Optional[ContentSettings]
                               **kwargs):
        # type: (...) -> Dict[str, Any]
        """Sets system properties on the file or directory.

        If one property is set for the content_settings, all properties will be overriden.

        :param ~azure.storage.filedatalake.ContentSettings content_settings:
            ContentSettings object used to set file/directory properties.
        :keyword lease:
            If specified, set_file_system_metadata only succeeds if the
            file system's lease is active and matches this ID.
        :paramtype lease: ~azure.storage.filedatalake.aio.DataLakeLeaseClient or str
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
        :returns: file/directory-updated property dict (Etag and last modified)
        :rtype: Dict[str, Any]
        """
        return await self._blob_client.set_http_headers(content_settings=content_settings, **kwargs)

    async def acquire_lease(self, lease_duration=-1,  # type: Optional[int]
                            lease_id=None,  # type: Optional[str]
                            **kwargs):
        # type: (...) -> DataLakeLeaseClient
        """
        Requests a new lease. If the file or directory does not have an active lease,
        the DataLake service creates a lease on the file/directory and returns a new
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
        :rtype: ~azure.storage.filedatalake.aio.DataLakeLeaseClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/test_file_system_samples.py
                :start-after: [START acquire_lease_on_file_system]
                :end-before: [END acquire_lease_on_file_system]
                :language: python
                :dedent: 8
                :caption: Acquiring a lease on the file_system.
        """
        lease = DataLakeLeaseClient(self, lease_id=lease_id)  # type: ignore
        await lease.acquire(lease_duration=lease_duration, **kwargs)
        return lease
