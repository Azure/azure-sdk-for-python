# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.storage.blob._lease import get_access_conditions
from azure.storage.file.datalake._generated.models import StorageErrorException
from .lease import DataLakeLeaseClient

try:
    from urllib.parse import urlparse, quote, unquote
except ImportError:
    from urlparse import urlparse # type: ignore
    from urllib2 import quote, unquote # type: ignore

import six

from azure.core.paging import ItemPaged
from azure.storage.blob import ContainerClient, BlobClient
from azure.storage.blob._shared.base_client import StorageAccountHostsMixin, parse_query
from azure.storage.blob._shared.response_handlers import process_storage_error, return_response_headers
from azure.storage.file.datalake._serialize import convert_dfs_url_to_blob_url, get_mod_conditions, \
    get_path_http_headers, add_metadata_headers
from azure.storage.file.datalake.models import LocationMode, FileSystemProperties, PathPropertiesPaged, DirectoryProperties
from ._generated import DataLakeStorageClient

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

        if not (file_system_name and path_name):
            raise ValueError("Please specify a container name and blob name.")
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(account_url))

        datalake_hosts = kwargs.pop('_hosts', None)

        blob_account_url = convert_dfs_url_to_blob_url(account_url)
        blob_primary_account_url = convert_dfs_url_to_blob_url(datalake_hosts[LocationMode.PRIMARY])
        blob_secondary_account_url = convert_dfs_url_to_blob_url(datalake_hosts[LocationMode.SECONDARY])
        blob_hosts = {LocationMode.PRIMARY: blob_primary_account_url,
                      LocationMode.SECONDARY: blob_secondary_account_url}
        self._blob_client = BlobClient(blob_account_url, file_system_name, path_name, credential=credential, _hosts=blob_hosts, **kwargs)

        _, sas_token = parse_query(parsed_url.query)
        self.file_system_name = file_system_name
        self.path_name = path_name

        self._query_str, credential = self._format_query_string(sas_token, credential)
        super(PathClient, self).__init__(parsed_url, service='dfs', credential=credential, **kwargs)
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

        access_conditions = get_access_conditions(kwargs.pop('lease', None)) # TODO: move the method to a right place
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
        :param ~azure.storage.file.datalake.ContentSettings content_settings:
            ContentSettings object used to set path properties.
        :param metadata:
            Name-value pairs associated with the blob as metadata.
        :type metadata: dict(str, str)
        :param lease:
            Required if the blob has an active lease. Value can be a LeaseClient object
            or the lease ID as a string.
        :type lease: ~azure.storage.blob.LeaseClient or str
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
        :param str if_match:
            An ETag value, or the wildcard character (*). Specify this header to perform
            the operation only if the resource's ETag matches the value specified.
        :param str if_none_match:
            An ETag value, or the wildcard character (*). Specify this header
            to perform the operation only if the resource's ETag does not match
            the value specified. Specify the wildcard character (*) to perform
            the operation only if the resource does not exist, and fail the
            operation if it does exist.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return:
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

    def _delete_path_options(self, **kwargs):
        # type: (Optional[ContentSettings], Optional[Dict[str, str]], **Any) -> Dict[str, Any]

        access_conditions = get_access_conditions(kwargs.pop('lease', None)) # TODO: move the method to a right place
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

        :param lease:
            Required if the blob has an active lease. Value can be a LeaseClient object
            or the lease ID as a string.
        :type lease: ~azure.storage.blob.LeaseClient or str
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
        :param str if_match:
            An ETag value, or the wildcard character (*). Specify this header to perform
            the operation only if the resource's ETag matches the value specified.
        :param str if_none_match:
            An ETag value, or the wildcard character (*). Specify this header
            to perform the operation only if the resource's ETag does not match
            the value specified. Specify the wildcard character (*) to perform
            the operation only if the resource does not exist, and fail the
            operation if it does exist.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return:
        """
        options = self._delete_path_options(**kwargs)
        try:
            return self._client.path.delete(**options)
        except StorageErrorException as error:
            process_storage_error(error)

    def _set_access_control_options(self, owner=None, group=None, permissions=None, acl=None, **kwargs):
        # type: (Optional[ContentSettings], Optional[Dict[str, str]], **Any) -> Dict[str, Any]

        access_conditions = get_access_conditions(kwargs.pop('lease', None)) # TODO: move the method to a right place
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

        :param owner: Optional. The owner of the blob or directory.
        :type owner: str
        :param group: Optional. The owning group of the blob or directory.
        :type group: str
        :param permissions: Optional and only valid if Hierarchical Namespace
         is enabled for the account. Sets POSIX access permissions for the file
         owner, the file owning group, and others. Each class may be granted
         read, write, or execute permission.  The sticky bit is also supported.
         Both symbolic (rwxrw-rw-) and 4-digit octal notation (e.g. 0766) are
         supported.
        :type permissions: str
        :param acl: Sets POSIX access control rights on files and directories.
         The value is a comma-separated list of access control entries. Each
         access control entry (ACE) consists of a scope, a type, a user or
         group identifier, and permissions in the format
         "[scope:][type]:[id]:[permissions]".
        :type acl: str
        :param lease:
            Required if the blob has an active lease. Value can be a LeaseClient object
            or the lease ID as a string.
        :type lease: ~azure.storage.blob.LeaseClient or str
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
        :param str if_match:
            An ETag value, or the wildcard character (*). Specify this header to perform
            the operation only if the resource's ETag matches the value specified.
        :param str if_none_match:
            An ETag value, or the wildcard character (*). Specify this header
            to perform the operation only if the resource's ETag does not match
            the value specified. Specify the wildcard character (*) to perform
            the operation only if the resource does not exist, and fail the
            operation if it does exist.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return:
        """
        options = self._set_access_control_options(owner=owner, group=group, permissions=permissions, acl=acl, **kwargs)
        try:
            return self._client.path.set_access_control(**options)
        except StorageErrorException as error:
            process_storage_error(error)

    def _get_access_control_options(self, upn=None,  # type: Optional[bool]
                                    **kwargs):
        # type: (...) -> Dict[str, Any]

        access_conditions = get_access_conditions(kwargs.pop('lease', None)) # TODO: move the method to a right place
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
        # type: (**Any) -> Dict[str, Any]
        options = self._get_access_control_options(upn=upn, **kwargs)
        try:
            return self._client.path.get_properties(**options)
        except StorageErrorException as error:
            process_storage_error(error)

    def rename_path(self, rename_source,
                    **kwargs):
        # type: (**Any) -> Dict[str, Any]
        return self._client.path.create(rename_source=rename_source, **kwargs)

    def _get_path_properties(self, **kwargs):
        # type: (**Any) -> Union[FileProperties, DirectoryProperties]
        path_properties = self._blob_client.get_blob_properties(**kwargs)
        path_properties.__class__ = DirectoryProperties
        return path_properties

    def set_metadata(self, metadata=None,  # type: Optional[Dict[str, str]]
                     **kwargs):
        # type: (Optional[Dict[str, str]], **Any) -> Dict[str, Union[str, datetime]]
        return self._blob_client.set_blob_metadata(metadata=metadata, **kwargs)

    def set_http_headers(self, content_settings=None,# type: Optional[ContentSettings]
                         **kwargs):
        # type: (Optional[ContentSettings], **Any) -> None
        return self._blob_client.set_http_headers(content_settings=content_settings, **kwargs)

    def acquire_lease(self, lease_duration=-1,  # type: Optional[int]
                      lease_id=None,  # type: Optional[str]
                      **kwargs):
        # type: (int, Optional[str], **Any) -> DataLakeLeaseClient
        lease = DataLakeLeaseClient(self, lease_id=lease_id)  # type: ignore
        lease.acquire(lease_duration=lease_duration, **kwargs)
        return lease
