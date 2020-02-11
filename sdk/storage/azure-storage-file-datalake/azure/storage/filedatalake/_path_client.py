# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

try:
    from urllib.parse import urlparse, quote
except ImportError:
    from urlparse import urlparse # type: ignore
    from urllib2 import quote  # type: ignore

import six

from azure.storage.blob import BlobClient
from ._shared.base_client import StorageAccountHostsMixin, parse_query
from ._shared.response_handlers import return_response_headers
from ._serialize import convert_dfs_url_to_blob_url, get_mod_conditions, \
    get_path_http_headers, add_metadata_headers, get_lease_id, get_source_mod_conditions, get_access_conditions
from ._models import LocationMode, DirectoryProperties
from ._generated import DataLakeStorageClient
from ._data_lake_lease import DataLakeLeaseClient
from ._generated.models import StorageErrorException
from ._deserialize import process_storage_error

_ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION = (
    'The require_encryption flag is set, but encryption is not supported'
    ' for this method.')


class PathClient(StorageAccountHostsMixin):
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
        path_name = path_name.strip('/')
        if not (file_system_name and path_name):
            raise ValueError("Please specify a container name and blob name.")
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(account_url))

        blob_account_url = convert_dfs_url_to_blob_url(account_url)
        self._blob_account_url = blob_account_url

        datalake_hosts = kwargs.pop('_hosts', None)
        blob_hosts = None
        if datalake_hosts:
            blob_primary_account_url = convert_dfs_url_to_blob_url(datalake_hosts[LocationMode.PRIMARY])
            blob_secondary_account_url = convert_dfs_url_to_blob_url(datalake_hosts[LocationMode.SECONDARY])
            blob_hosts = {LocationMode.PRIMARY: blob_primary_account_url,
                          LocationMode.SECONDARY: blob_secondary_account_url}
        self._blob_client = BlobClient(blob_account_url, file_system_name, path_name,
                                       credential=credential, _hosts=blob_hosts, **kwargs)

        _, sas_token = parse_query(parsed_url.query)
        self.file_system_name = file_system_name
        self.path_name = path_name

        self._query_str, self._raw_credential = self._format_query_string(sas_token, credential)

        super(PathClient, self).__init__(parsed_url, service='dfs', credential=self._raw_credential,
                                         _hosts=datalake_hosts, **kwargs)
        self._client = DataLakeStorageClient(self.url, file_system_name, path_name, pipeline=self._pipeline)

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

    def _create_path_options(self, resource_type, content_settings=None, metadata=None, **kwargs):
        # type: (Optional[ContentSettings], Optional[Dict[str, str]], **Any) -> Dict[str, Any]
        if self.require_encryption or (self.key_encryption_key is not None):
            raise ValueError(_ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)

        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_mod_conditions(kwargs)

        path_http_headers = None
        if content_settings:
            path_http_headers = get_path_http_headers(content_settings)

        options = {
            'resource': resource_type,
            'properties': add_metadata_headers(metadata),
            'permissions': kwargs.pop('permissions', None),
            'umask': kwargs.pop('umask', None),
            'path_http_headers': path_http_headers,
            'lease_access_conditions': access_conditions,
            'modified_access_conditions': mod_conditions,
            'timeout': kwargs.pop('timeout', None),
            'cls': return_response_headers}
        options.update(kwargs)
        return options

    def _create(self, resource_type, content_settings=None, metadata=None, **kwargs):
        # type: (...) -> Dict[str, Union[str, datetime]]
        """
        Create directory or file

        :param resource_type: Required for Create File and Create Directory.
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
        :type lease: ~azure.storage.filedatalake.DataLakeLeaseClient or str
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
        :keyword str etag:
            An ETag value, or the wildcard character (*). Used to check if the resource has changed,
            and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition:
            The match condition to use upon the etag.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :return: Dict[str, Union[str, datetime]]
        """
        options = self._create_path_options(
            resource_type,
            content_settings=content_settings,
            metadata=metadata,
            **kwargs)
        try:
            return self._client.path.create(**options)
        except StorageErrorException as error:
            process_storage_error(error)

    @staticmethod
    def _delete_path_options(**kwargs):
        # type: (Optional[ContentSettings], Optional[Dict[str, str]], **Any) -> Dict[str, Any]

        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_mod_conditions(kwargs)

        options = {
            'recursive': True,
            'lease_access_conditions': access_conditions,
            'modified_access_conditions': mod_conditions,
            'timeout': kwargs.pop('timeout', None)}
        options.update(kwargs)
        return options

    def _delete(self, **kwargs):
        # type: (bool, **Any) -> None
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
        :return: None
        """
        options = self._delete_path_options(**kwargs)
        try:
            return self._client.path.delete(**options)
        except StorageErrorException as error:
            process_storage_error(error)

    @staticmethod
    def _set_access_control_options(owner=None, group=None, permissions=None, acl=None, **kwargs):
        # type: (Optional[ContentSettings], Optional[Dict[str, str]], **Any) -> Dict[str, Any]

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

        :param owner: Optional. The owner of the file or directory.
        :type owner: str
        :param group: Optional. The owning group of the file or directory.
        :type group: str
        :param permissions: Optional and only valid if Hierarchical Namespace
         is enabled for the account. Sets POSIX access permissions for the file
         owner, the file owning group, and others. Each class may be granted
         read, write, or execute permission.  The sticky bit is also supported.
         Both symbolic (rwxrw-rw-) and 4-digit octal notation (e.g. 0766) are
         supported.
         permissions and acl are mutually exclusive.
        :type permissions: str
        :param acl: Sets POSIX access control rights on files and directories.
         The value is a comma-separated list of access control entries. Each
         access control entry (ACE) consists of a scope, a type, a user or
         group identifier, and permissions in the format
         "[scope:][type]:[id]:[permissions]".
         permissions and acl are mutually exclusive.
        :type acl: str
        :keyword lease:
            Required if the file/directory has an active lease. Value can be a LeaseClient object
            or the lease ID as a string.
        :type lease: ~azure.storage.filedatalake.DataLakeLeaseClient or str
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
            return self._client.path.set_access_control(**options)
        except StorageErrorException as error:
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
        :param upn: Optional. Valid only when Hierarchical Namespace is
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
        :type lease: ~azure.storage.filedatalake.DataLakeLeaseClient or str
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
        except StorageErrorException as error:
            process_storage_error(error)

    def _rename_path_options(self, rename_source, content_settings=None, metadata=None, **kwargs):
        # type: (Optional[ContentSettings], Optional[Dict[str, str]], **Any) -> Dict[str, Any]
        if self.require_encryption or (self.key_encryption_key is not None):
            raise ValueError(_ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)

        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        source_lease_id = get_lease_id(kwargs.pop('source_lease', None))
        mod_conditions = get_mod_conditions(kwargs)
        source_mod_conditions = get_source_mod_conditions(kwargs)

        path_http_headers = None
        if content_settings:
            path_http_headers = get_path_http_headers(content_settings)

        options = {
            'rename_source': rename_source,
            'properties': add_metadata_headers(metadata),
            'permissions': kwargs.pop('permissions', None),
            'umask': kwargs.pop('umask', None),
            'path_http_headers': path_http_headers,
            'lease_access_conditions': access_conditions,
            'source_lease_id': source_lease_id,
            'modified_access_conditions': mod_conditions,
            'source_modified_access_conditions':source_mod_conditions,
            'timeout': kwargs.pop('timeout', None),
            'mode': 'legacy',
            'cls': return_response_headers}
        options.update(kwargs)
        return options

    def _rename_path(self, rename_source,
                     **kwargs):
        # type: (**Any) -> Dict[str, Any]
        """
        Rename directory or file

        :param rename_source: The value must have the following format: "/{filesystem}/{path}".
        :type rename_source: str
        :param source_lease: A lease ID for the source path. If specified,
         the source path must have an active lease and the leaase ID must
         match.
        :type source_lease: ~azure.storage.filedatalake.DataLakeLeaseClient or str
        :param ~azure.storage.filedatalake.ContentSettings content_settings:
            ContentSettings object used to set path properties.
        :param lease:
            Required if the file/directory has an active lease. Value can be a LeaseClient object
            or the lease ID as a string.
        :type lease: ~azure.storage.filedatalake.DataLakeLeaseClient or str
        :param str umask: Optional and only valid if Hierarchical Namespace is enabled for the account.
            When creating a file or directory and the parent folder does not have a default ACL,
            the umask restricts the permissions of the file or directory to be created.
            The resulting permission is given by p & ^u, where p is the permission and u is the umask.
            For example, if p is 0777 and u is 0057, then the resulting permission is 0720.
            The default permission is 0777 for a directory and 0666 for a file. The default umask is 0027.
            The umask must be specified in 4-digit octal notation (e.g. 0766).
        :param permissions: Optional and only valid if Hierarchical Namespace
         is enabled for the account. Sets POSIX access permissions for the file
         owner, the file owning group, and others. Each class may be granted
         read, write, or execute permission.  The sticky bit is also supported.
         Both symbolic (rwxrw-rw-) and 4-digit octal notation (e.g. 0766) are
         supported.
        :type permissions: str
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
        :param ~datetime.datetime source_if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param ~datetime.datetime source_if_unmodified_since:
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
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return:
        """
        options = self._rename_path_options(
            rename_source,
            **kwargs)
        try:
            return self._client.path.create(**options)
        except StorageErrorException as error:
            process_storage_error(error)

    def _get_path_properties(self, **kwargs):
        # type: (**Any) -> Union[FileProperties, DirectoryProperties]
        """Returns all user-defined metadata, standard HTTP properties, and
        system properties for the file or directory. It does not return the content of the directory or file.

        :keyword lease:
            Required if the directory or file has an active lease. Value can be a DataLakeLeaseClient object
            or the lease ID as a string.
        :type lease: ~azure.storage.filedatalake.DataLakeLeaseClient or str
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
        path_properties.__class__ = DirectoryProperties
        return path_properties

    def set_metadata(self, metadata=None,  # type: Optional[Dict[str, str]]
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
        return self._blob_client.set_blob_metadata(metadata=metadata, **kwargs)

    def set_http_headers(self, content_settings=None,  # type: Optional[ContentSettings]
                         **kwargs):
        # type: (...) -> Dict[str, Any]
        """Sets system properties on the file or directory.

        If one property is set for the content_settings, all properties will be overriden.

        :param ~azure.storage.filedatalake.ContentSettings content_settings:
            ContentSettings object used to set file/directory properties.
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

        .. admonition:: Example:

            .. literalinclude:: ../samples/test_file_system_samples.py
                :start-after: [START acquire_lease_on_file_system]
                :end-before: [END acquire_lease_on_file_system]
                :language: python
                :dedent: 8
                :caption: Acquiring a lease on the file_system.
        """
        lease = DataLakeLeaseClient(self, lease_id=lease_id)  # type: ignore
        lease.acquire(lease_duration=lease_duration, **kwargs)
        return lease
