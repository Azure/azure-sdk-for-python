# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from datetime import datetime
from typing import ( # pylint: disable=unused-import
    Any, Dict, Optional, Union,
    TYPE_CHECKING)

try:
    from urllib.parse import urlparse, quote
except ImportError:
    from urlparse import urlparse # type: ignore
    from urllib2 import quote  # type: ignore

import six

from azure.core.exceptions import AzureError, HttpResponseError
from azure.storage.blob import BlobClient
from ._data_lake_lease import DataLakeLeaseClient
from ._deserialize import process_storage_error
from ._generated import AzureDataLakeStorageRESTAPI
from ._models import LocationMode, DirectoryProperties, AccessControlChangeResult, AccessControlChanges, \
    AccessControlChangeCounters, AccessControlChangeFailure
from ._serialize import convert_dfs_url_to_blob_url, get_mod_conditions, \
    get_path_http_headers, add_metadata_headers, get_lease_id, get_source_mod_conditions, get_access_conditions, \
    get_api_version, get_cpk_info, convert_datetime_to_rfc1123
from ._shared.base_client import StorageAccountHostsMixin, parse_query
from ._shared.response_handlers import return_response_headers, return_headers_and_deserialized

if TYPE_CHECKING:
    from ._models import ContentSettings, FileProperties


class PathClient(StorageAccountHostsMixin):
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

        try:
            if not account_url.lower().startswith('http'):
                account_url = "https://" + account_url
        except AttributeError:
            raise ValueError("Account URL must be a string.")
        parsed_url = urlparse(account_url.rstrip('/'))

        # remove the preceding/trailing delimiter from the path components
        file_system_name = file_system_name.strip('/')

        # the name of root directory is /
        if path_name != '/':
            path_name = path_name.strip('/')

        if not (file_system_name and path_name):
            raise ValueError("Please specify a file system name and file path.")
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(account_url))

        blob_account_url = convert_dfs_url_to_blob_url(account_url)
        self._blob_account_url = blob_account_url

        datalake_hosts = kwargs.pop('_hosts', None)
        blob_hosts = None
        if datalake_hosts:
            blob_primary_account_url = convert_dfs_url_to_blob_url(datalake_hosts[LocationMode.PRIMARY])
            blob_hosts = {LocationMode.PRIMARY: blob_primary_account_url, LocationMode.SECONDARY: ""}
        self._blob_client = BlobClient(blob_account_url, file_system_name, path_name,
                                       credential=credential, _hosts=blob_hosts, **kwargs)

        _, sas_token = parse_query(parsed_url.query)
        self.file_system_name = file_system_name
        self.path_name = path_name

        self._query_str, self._raw_credential = self._format_query_string(sas_token, credential)

        super(PathClient, self).__init__(parsed_url, service='dfs', credential=self._raw_credential,
                                         _hosts=datalake_hosts, **kwargs)
        # ADLS doesn't support secondary endpoint, make sure it's empty
        self._hosts[LocationMode.SECONDARY] = ""
        api_version = get_api_version(kwargs)

        self._client = AzureDataLakeStorageRESTAPI(self.url, base_url=self.url, file_system=file_system_name,
                                                   path=path_name, pipeline=self._pipeline)
        self._client._config.version = api_version  # pylint: disable=protected-access

        self._datalake_client_for_blob_operation = AzureDataLakeStorageRESTAPI(
            self._blob_client.url,
            base_url=self._blob_client.url,
            file_system=file_system_name,
            path=path_name,
            pipeline=self._pipeline)
        self._datalake_client_for_blob_operation._config.version = api_version  # pylint: disable=protected-access

    def __exit__(self, *args):
        self._blob_client.close()
        super(PathClient, self).__exit__(*args)

    def close(self):
        # type: () -> None
        """ This method is to close the sockets opened by the client.
        It need not be used when using with a context manager.
        """
        self._blob_client.close()
        self.__exit__()

    def _format_url(self, hostname):
        file_system_name = self.file_system_name
        if isinstance(file_system_name, six.text_type):
            file_system_name = file_system_name.encode('UTF-8')
        return "{}://{}/{}/{}{}".format(
            self.scheme,
            hostname,
            quote(file_system_name),
            quote(self.path_name, safe='~'),
            self._query_str)

    def _create_path_options(self, resource_type,
                             content_settings=None,  # type: Optional[ContentSettings]
                             metadata=None,  # type: Optional[Dict[str, str]]
                             **kwargs):
        # type: (...) -> Dict[str, Any]
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_mod_conditions(kwargs)

        path_http_headers = None
        if content_settings:
            path_http_headers = get_path_http_headers(content_settings)

        cpk_info = get_cpk_info(self.scheme, kwargs)

        expires_on = kwargs.pop('expires_on', None)
        if expires_on:
            try:
                expires_on = convert_datetime_to_rfc1123(expires_on)
                kwargs['expiry_options'] = 'Absolute'
            except AttributeError:
                expires_on = str(expires_on)
                kwargs['expiry_options'] = 'RelativeToNow'

        options = {
            'resource': resource_type,
            'properties': add_metadata_headers(metadata),
            'permissions': kwargs.pop('permissions', None),
            'umask': kwargs.pop('umask', None),
            'owner': kwargs.pop('owner', None),
            'group': kwargs.pop('group', None),
            'acl': kwargs.pop('acl', None),
            'proposed_lease_id': kwargs.pop('lease_id', None),
            'lease_duration': kwargs.pop('lease_duration', None),
            'expiry_options': kwargs.pop('expiry_options', None),
            'expires_on': expires_on,
            'path_http_headers': path_http_headers,
            'lease_access_conditions': access_conditions,
            'modified_access_conditions': mod_conditions,
            'cpk_info': cpk_info,
            'timeout': kwargs.pop('timeout', None),
            'cls': return_response_headers}
        options.update(kwargs)
        return options

    def _create(self, resource_type, content_settings=None, metadata=None, **kwargs):
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
            Required if the file/directory has an active lease. Value can be a LeaseClient object
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
            return self._client.path.create(**options)
        except HttpResponseError as error:
            process_storage_error(error)

    @staticmethod
    def _delete_path_options(**kwargs):
        # type: (**Any) -> Dict[str, Any]

        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_mod_conditions(kwargs)

        options = {
            'lease_access_conditions': access_conditions,
            'modified_access_conditions': mod_conditions,
            'cls': return_response_headers,
            'timeout': kwargs.pop('timeout', None)}
        options.update(kwargs)
        return options

    def _delete(self, **kwargs):
        # type: (**Any) -> Dict[Union[datetime, str]]
        """
        Marks the specified path for deletion.

        :keyword lease:
            Required if the file/directory has an active lease. Value can be a LeaseClient object
            or the lease ID as a string.
        :type lease: ~azure.storage.filedatalake.DataLakeLeaseClient or str
        :param ~datetime.datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param ~datetime.datetime if_unmodified_since:
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
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: A dictionary of response headers.
        :rtype: Dict[str, Union[str, datetime]]
        """
        options = self._delete_path_options(**kwargs)
        try:
            return self._client.path.delete(**options)
        except HttpResponseError as error:
            process_storage_error(error)

    @staticmethod
    def _set_access_control_options(owner=None, group=None, permissions=None, acl=None, **kwargs):
        # type: (...) -> Dict[str, Any]

        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_mod_conditions(kwargs)

        options = {
            'owner': owner,
            'group': group,
            'permissions': permissions,
            'acl': acl,
            'lease_access_conditions': access_conditions,
            'modified_access_conditions': mod_conditions,
            'timeout': kwargs.pop('timeout', None),
            'cls': return_response_headers}
        options.update(kwargs)
        return options

    def set_access_control(self, owner=None,  # type: Optional[str]
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
        :keyword: response dict (Etag and last modified).
        """
        if not any([owner, group, permissions, acl]):
            raise ValueError("At least one parameter should be set for set_access_control API")
        options = self._set_access_control_options(owner=owner, group=group, permissions=permissions, acl=acl, **kwargs)
        try:
            return self._client.path.set_access_control(**options)
        except HttpResponseError as error:
            process_storage_error(error)

    @staticmethod
    def _get_access_control_options(upn=None,  # type: Optional[bool]
                                    **kwargs):
        # type: (...) -> Dict[str, Any]

        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_mod_conditions(kwargs)

        options = {
            'action': 'getAccessControl',
            'upn': upn if upn else False,
            'lease_access_conditions': access_conditions,
            'modified_access_conditions': mod_conditions,
            'timeout': kwargs.pop('timeout', None),
            'cls': return_response_headers}
        options.update(kwargs)
        return options

    def get_access_control(self, upn=None,  # type: Optional[bool]
                           **kwargs):
        # type: (...) -> Dict[str, Any]
        """
        :param upn: Optional.
            Valid only when Hierarchical Namespace is
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
        :keyword: response dict.
        """
        options = self._get_access_control_options(upn=upn, **kwargs)
        try:
            return self._client.path.get_properties(**options)
        except HttpResponseError as error:
            process_storage_error(error)

    @staticmethod
    def _set_access_control_recursive_options(mode, acl, **kwargs):
        # type: (str, str, **Any) -> Dict[str, Any]

        options = {
            'mode': mode,
            'force_flag': kwargs.pop('continue_on_failure', None),
            'timeout': kwargs.pop('timeout', None),
            'continuation': kwargs.pop('continuation_token', None),
            'max_records': kwargs.pop('batch_size', None),
            'acl': acl,
            'cls': return_headers_and_deserialized}
        options.update(kwargs)
        return options

    def set_access_control_recursive(self,
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
        :rtype: :class:`~azure.storage.filedatalake.AccessControlChangeResult`
        :raises ~azure.core.exceptions.AzureError:
            User can restart the operation using continuation_token field of AzureError if the token is available.
        """
        if not acl:
            raise ValueError("The Access Control List must be set for this operation")

        progress_hook = kwargs.pop('progress_hook', None)
        max_batches = kwargs.pop('max_batches', None)
        options = self._set_access_control_recursive_options(mode='set', acl=acl, **kwargs)
        return self._set_access_control_internal(options=options, progress_hook=progress_hook,
                                                 max_batches=max_batches)

    def update_access_control_recursive(self,
                                        acl,
                                        **kwargs):
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
        :rtype: :class:`~azure.storage.filedatalake.AccessControlChangeResult`
        :raises ~azure.core.exceptions.AzureError:
            User can restart the operation using continuation_token field of AzureError if the token is available.
        """
        if not acl:
            raise ValueError("The Access Control List must be set for this operation")

        progress_hook = kwargs.pop('progress_hook', None)
        max_batches = kwargs.pop('max_batches', None)
        options = self._set_access_control_recursive_options(mode='modify', acl=acl, **kwargs)
        return self._set_access_control_internal(options=options, progress_hook=progress_hook,
                                                 max_batches=max_batches)

    def remove_access_control_recursive(self,
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
            If maximum is reached before all sub-paths are processed then,
            continuation token can be used to resume operation.
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
        :rtype: :class:`~azure.storage.filedatalake.AccessControlChangeResult`
        :raises ~azure.core.exceptions.AzureError:
            User can restart the operation using continuation_token field of AzureError if the token is available.
        """
        if not acl:
            raise ValueError("The Access Control List must be set for this operation")

        progress_hook = kwargs.pop('progress_hook', None)
        max_batches = kwargs.pop('max_batches', None)
        options = self._set_access_control_recursive_options(mode='remove', acl=acl, **kwargs)
        return self._set_access_control_internal(options=options, progress_hook=progress_hook,
                                                 max_batches=max_batches)

    def _set_access_control_internal(self, options, progress_hook, max_batches=None):
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
                headers, resp = self._client.path.set_access_control_recursive(**options)

                # make a running tally so that we can report the final results
                total_directories_successful += resp.directories_successful
                total_files_success += resp.files_successful
                total_failure_count += resp.failure_count
                batch_count += 1
                current_continuation_token = headers['continuation']

                if current_continuation_token is not None:
                    last_continuation_token = current_continuation_token

                if progress_hook is not None:
                    progress_hook(AccessControlChanges(
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

    def _rename_path_options(self,  # pylint: disable=no-self-use
                             rename_source,  # type: str
                             content_settings=None,  # type: Optional[ContentSettings]
                             metadata=None,  # type: Optional[Dict[str, str]]
                             **kwargs):
        # type: (...) -> Dict[str, Any]
        if metadata or kwargs.pop('permissions', None) or kwargs.pop('umask', None):
            raise ValueError("metadata, permissions, umask is not supported for this operation")

        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        source_lease_id = get_lease_id(kwargs.pop('source_lease', None))
        mod_conditions = get_mod_conditions(kwargs)
        source_mod_conditions = get_source_mod_conditions(kwargs)

        path_http_headers = None
        if content_settings:
            path_http_headers = get_path_http_headers(content_settings)

        options = {
            'rename_source': rename_source,
            'path_http_headers': path_http_headers,
            'lease_access_conditions': access_conditions,
            'source_lease_id': source_lease_id,
            'modified_access_conditions': mod_conditions,
            'source_modified_access_conditions': source_mod_conditions,
            'timeout': kwargs.pop('timeout', None),
            'mode': 'legacy',
            'cls': return_response_headers}
        options.update(kwargs)
        return options

    def _rename_path(self, rename_source, **kwargs):
        # type: (str, **Any) -> Dict[str, Any]
        """
        Rename directory or file

        :param rename_source:
            The value must have the following format: "/{filesystem}/{path}".
        :type rename_source: str
        :keyword ~azure.storage.filedatalake.ContentSettings content_settings:
            ContentSettings object used to set path properties.
        :keyword source_lease:
            A lease ID for the source path. If specified,
            the source path must have an active lease and the leaase ID must
            match.
        :paramtype source_lease: ~azure.storage.filedatalake.DataLakeLeaseClient or str
        :keyword lease:
            Required if the file/directory has an active lease. Value can be a LeaseClient object
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
            return self._client.path.create(**options)
        except HttpResponseError as error:
            process_storage_error(error)

    def _get_path_properties(self, **kwargs):
        # type: (**Any) -> Union[FileProperties, DirectoryProperties]
        """Returns all user-defined metadata, standard HTTP properties, and
        system properties for the file or directory. It does not return the content of the directory or file.

        :keyword lease:
            Required if the directory or file has an active lease. Value can be a DataLakeLeaseClient object
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
        :keyword ~azure.storage.filedatalake.CustomerProvidedEncryptionKey cpk:
            Decrypts the data on the service-side with the given key.
            Use of customer-provided keys must be done over HTTPS.
            Required if the file/directory was created with a customer-provided key.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: DirectoryProperties or FileProperties

        .. admonition:: Example:

            .. literalinclude:: ../tests/test_blob_samples_common.py
                :start-after: [START get_blob_properties]
                :end-before: [END get_blob_properties]
                :language: python
                :dedent: 8
                :caption: Getting the properties for a file/directory.
        """
        path_properties = self._blob_client.get_blob_properties(**kwargs)
        return path_properties

    def _exists(self, **kwargs):
        # type: (**Any) -> bool
        """
        Returns True if a path exists and returns False otherwise.

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: boolean
        """
        return self._blob_client.exists(**kwargs)

    def set_metadata(self, metadata,  # type: Dict[str, str]
                     **kwargs):
        # type: (...) -> Dict[str, Union[str, datetime]]
        """Sets one or more user-defined name-value pairs for the specified
        file system. Each call to this operation replaces all existing metadata
        attached to the file system. To remove all metadata from the file system,
        call this operation with no metadata dict.

        :param metadata:
            A dict containing name-value pairs to associate with the file system as
            metadata. Example: {'category':'test'}
        :type metadata: Dict[str, str]
        :keyword lease:
            If specified, set_file_system_metadata only succeeds if the
            file system's lease is active and matches this ID.
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
        :keyword ~azure.storage.filedatalake.CustomerProvidedEncryptionKey cpk:
            Encrypts the data on the service-side with the given key.
            Use of customer-provided keys must be done over HTTPS.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: file system-updated property dict (Etag and last modified).
        """
        return self._blob_client.set_blob_metadata(metadata=metadata, **kwargs)

    def set_http_headers(self, content_settings=None,  # type: Optional[ContentSettings]
                         **kwargs):
        # type: (...) -> Dict[str, Any]
        """Sets system properties on the file or directory.

        If one property is set for the content_settings, all properties will be overriden.

        :param ~azure.storage.filedatalake.ContentSettings content_settings:
            ContentSettings object used to set file/directory properties.
        :keyword lease:
            If specified, set_file_system_metadata only succeeds if the
            file system's lease is active and matches this ID.
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
        :returns: file/directory-updated property dict (Etag and last modified)
        :rtype: Dict[str, Any]
        """
        return self._blob_client.set_http_headers(content_settings=content_settings, **kwargs)

    def acquire_lease(self, lease_duration=-1,  # type: Optional[int]
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
        :rtype: ~azure.storage.filedatalake.DataLakeLeaseClient
        """
        lease = DataLakeLeaseClient(self, lease_id=lease_id)  # type: ignore
        lease.acquire(lease_duration=lease_duration, **kwargs)
        return lease
