# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from io import BytesIO
from typing import ( # pylint: disable=unused-import
    Any, AnyStr, Dict, IO, Iterable, Optional, Type, TypeVar, Union,
    TYPE_CHECKING)

try:
    from urllib.parse import quote, unquote
except ImportError:
    from urllib2 import quote, unquote # type: ignore

import six

from azure.core.exceptions import HttpResponseError
from ._quick_query_helper import DataLakeFileQueryReader
from ._shared.base_client import parse_connection_str
from ._shared.request_handlers import get_length, read_length
from ._shared.response_handlers import return_response_headers
from ._shared.uploads import IterStreamer
from ._upload_helper import upload_datalake_file
from ._download import StorageStreamDownloader
from ._path_client import PathClient
from ._serialize import get_mod_conditions, get_path_http_headers, get_access_conditions, add_metadata_headers, \
    convert_datetime_to_rfc1123, get_cpk_info
from ._deserialize import process_storage_error, deserialize_file_properties
from ._models import FileProperties, DataLakeFileQueryError

if TYPE_CHECKING:
    from datetime import datetime
    from ._models import ContentSettings

ClassType = TypeVar("ClassType")


class DataLakeFileClient(PathClient):
    """A client to interact with the DataLake file, even if the file may not yet exist.

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
    :param file_path:
        The whole file path, so that to interact with a specific file.
        eg. "{directory}/{subdirectory}/{file}"
    :type file_path: str
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

        .. literalinclude:: ../samples/datalake_samples_instantiate_client.py
            :start-after: [START instantiate_file_client_from_conn_str]
            :end-before: [END instantiate_file_client_from_conn_str]
            :language: python
            :dedent: 4
            :caption: Creating the DataLakeServiceClient from connection string.
    """
    def __init__(
        self, account_url,  # type: str
        file_system_name,  # type: str
        file_path,  # type: str
        credential=None,  # type: Optional[Any]
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        super(DataLakeFileClient, self).__init__(account_url, file_system_name, path_name=file_path,
                                                 credential=credential, **kwargs)

    @classmethod
    def from_connection_string(
            cls,  # type: Type[ClassType]
            conn_str,  # type: str
            file_system_name,  # type: str
            file_path,  # type: str
            credential=None,  # type: Optional[Any]
            **kwargs  # type: Any
        ):  # type: (...) -> ClassType
        """
        Create DataLakeFileClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Storage account.
        :param file_system_name: The name of file system to interact with.
        :type file_system_name: str
        :param directory_name: The name of directory to interact with. The directory is under file system.
        :type directory_name: str
        :param file_name: The name of file to interact with. The file is under directory.
        :type file_name: str
        :param credential:
            The credentials with which to authenticate. This is optional if the
            account URL already has a SAS token, or the connection string already has shared
            access key values. The value can be a SAS token string,
            an instance of a AzureSasCredential from azure.core.credentials, an account shared access
            key, or an instance of a TokenCredentials class from azure.identity.
            Credentials provided here will take precedence over those in the connection string.
        :return a DataLakeFileClient
        :rtype ~azure.storage.filedatalake.DataLakeFileClient
        """
        account_url, _, credential = parse_connection_str(conn_str, credential, 'dfs')
        return cls(
            account_url, file_system_name=file_system_name, file_path=file_path,
            credential=credential, **kwargs)

    def create_file(self, content_settings=None,  # type: Optional[ContentSettings]
                    metadata=None,  # type: Optional[Dict[str, str]]
                    **kwargs):
        # type: (...) -> Dict[str, Union[str, datetime]]
        """
        Create a new file.

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
        :keyword ~azure.storage.filedatalake.CustomerProvidedEncryptionKey cpk:
            Encrypts the data on the service-side with the given key.
            Use of customer-provided keys must be done over HTTPS.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :return: response dict (Etag and last modified).

        .. admonition:: Example:

            .. literalinclude:: ../samples/datalake_samples_upload_download.py
                :start-after: [START create_file]
                :end-before: [END create_file]
                :language: python
                :dedent: 4
                :caption: Create file.
        """
        return self._create('file', content_settings=content_settings, metadata=metadata, **kwargs)

    def delete_file(self, **kwargs):
        # type: (...) -> None
        """
        Marks the specified file for deletion.

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
        :return: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/datalake_samples_upload_download.py
                :start-after: [START delete_file]
                :end-before: [END delete_file]
                :language: python
                :dedent: 4
                :caption: Delete file.
        """
        return self._delete(**kwargs)

    def get_file_properties(self, **kwargs):
        # type: (**Any) -> FileProperties
        """Returns all user-defined metadata, standard HTTP properties, and
        system properties for the file. It does not return the content of the file.

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
        :keyword ~azure.storage.filedatalake.CustomerProvidedEncryptionKey cpk:
            Decrypts the data on the service-side with the given key.
            Use of customer-provided keys must be done over HTTPS.
            Required if the file was created with a customer-provided key.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: FileProperties

        .. admonition:: Example:

            .. literalinclude:: ../samples/datalake_samples_upload_download.py
                :start-after: [START get_file_properties]
                :end-before: [END get_file_properties]
                :language: python
                :dedent: 4
                :caption: Getting the properties for a file.
        """
        return self._get_path_properties(cls=deserialize_file_properties, **kwargs)  # pylint: disable=protected-access

    def set_file_expiry(self, expiry_options,  # type: str
                        expires_on=None,   # type: Optional[Union[datetime, int]]
                        **kwargs):
        # type: (...) -> None
        """Sets the time a file will expire and be deleted.

        :param str expiry_options:
            Required. Indicates mode of the expiry time.
            Possible values include: 'NeverExpire', 'RelativeToCreation', 'RelativeToNow', 'Absolute'
        :param datetime or int expires_on:
            The time to set the file to expiry.
            When expiry_options is RelativeTo*, expires_on should be an int in milliseconds.
            If the type of expires_on is datetime, it should be in UTC time.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None
        """
        try:
            expires_on = convert_datetime_to_rfc1123(expires_on)
        except AttributeError:
            expires_on = str(expires_on)
        self._datalake_client_for_blob_operation.path \
            .set_expiry(expiry_options, expires_on=expires_on, **kwargs)  # pylint: disable=protected-access

    def _upload_options(  # pylint:disable=too-many-statements
            self, data,  # type: Union[AnyStr, Iterable[AnyStr], IO[AnyStr]]
            length=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> Dict[str, Any]

        encoding = kwargs.pop('encoding', 'UTF-8')
        if isinstance(data, six.text_type):
            data = data.encode(encoding) # type: ignore
        if length is None:
            length = get_length(data)
        if isinstance(data, bytes):
            data = data[:length]

        if isinstance(data, bytes):
            stream = BytesIO(data)
        elif hasattr(data, 'read'):
            stream = data
        elif hasattr(data, '__iter__'):
            stream = IterStreamer(data, encoding=encoding)
        else:
            raise TypeError("Unsupported data type: {}".format(type(data)))

        validate_content = kwargs.pop('validate_content', False)
        content_settings = kwargs.pop('content_settings', None)
        metadata = kwargs.pop('metadata', None)
        max_concurrency = kwargs.pop('max_concurrency', 1)

        kwargs['properties'] = add_metadata_headers(metadata)
        kwargs['lease_access_conditions'] = get_access_conditions(kwargs.pop('lease', None))
        kwargs['modified_access_conditions'] = get_mod_conditions(kwargs)
        kwargs['cpk_info'] = get_cpk_info(self.scheme, kwargs)

        if content_settings:
            kwargs['path_http_headers'] = get_path_http_headers(content_settings)

        kwargs['stream'] = stream
        kwargs['length'] = length
        kwargs['validate_content'] = validate_content
        kwargs['max_concurrency'] = max_concurrency
        kwargs['client'] = self._client.path
        kwargs['file_settings'] = self._config

        return kwargs

    def upload_data(self, data,  # type: Union[AnyStr, Iterable[AnyStr], IO[AnyStr]]
                    length=None,  # type: Optional[int]
                    overwrite=False,  # type: Optional[bool]
                    **kwargs):
        # type: (...) -> Dict[str, Any]
        """
        Upload data to a file.

        :param data: Content to be uploaded to file
        :param int length: Size of the data in bytes.
        :param bool overwrite: to overwrite an existing file or not.
        :keyword ~azure.storage.filedatalake.ContentSettings content_settings:
            ContentSettings object used to set path properties.
        :keyword metadata:
            Name-value pairs associated with the blob as metadata.
        :paramtype metadata: dict(str, str)
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
        :keyword bool validate_content:
            If true, calculates an MD5 hash for each chunk of the file. The storage
            service checks the hash of the content that has arrived with the hash
            that was sent. This is primarily valuable for detecting bitflips on
            the wire if using http instead of https, as https (the default), will
            already validate. Note that this MD5 hash is not stored with the
            blob. Also note that if enabled, the memory-efficient upload algorithm
            will not be used because computing the MD5 hash requires buffering
            entire blocks, and doing so defeats the purpose of the memory-efficient algorithm.
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
        :keyword int chunk_size:
            The maximum chunk size for uploading a file in chunks.
            Defaults to 100*1024*1024, or 100MB.
        :return: response dict (Etag and last modified).
        """
        options = self._upload_options(
            data,
            length=length,
            overwrite=overwrite,
            **kwargs)
        return upload_datalake_file(**options)

    @staticmethod
    def _append_data_options(
            data, # type: Union[AnyStr, Iterable[AnyStr], IO[AnyStr]]
            offset, # type: int
            scheme, # type: str
            length=None, # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> Dict[str, Any]

        if isinstance(data, six.text_type):
            data = data.encode(kwargs.pop('encoding', 'UTF-8'))  # type: ignore
        if length is None:
            length = get_length(data)
            if length is None:
                length, data = read_length(data)
        if isinstance(data, bytes):
            data = data[:length]

        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        cpk_info = get_cpk_info(scheme, kwargs)

        options = {
            'body': data,
            'position': offset,
            'content_length': length,
            'lease_access_conditions': access_conditions,
            'validate_content': kwargs.pop('validate_content', False),
            'cpk_info': cpk_info,
            'timeout': kwargs.pop('timeout', None),
            'cls': return_response_headers}
        options.update(kwargs)
        return options

    def append_data(self, data,  # type: Union[AnyStr, Iterable[AnyStr], IO[AnyStr]]
                    offset,  # type: int
                    length=None,  # type: Optional[int]
                    **kwargs):
        # type: (...) -> Dict[str, Union[str, datetime, int]]
        """Append data to the file.

        :param data: Content to be appended to file
        :param offset: start position of the data to be appended to.
        :param length: Size of the data in bytes.
        :keyword bool flush:
            If file should be flushed after the append. Default value is None.
        :keyword bool validate_content:
            If true, calculates an MD5 hash of the block content. The storage
            service checks the hash of the content that has arrived
            with the hash that was sent. This is primarily valuable for detecting
            bitflips on the wire if using http instead of https as https (the default)
            will already validate. Note that this MD5 hash is not stored with the
            file.
        :keyword lease:
            Required if the file has an active lease. Value can be a DataLakeLeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.filedatalake.DataLakeLeaseClient or str
        :keyword ~azure.storage.filedatalake.CustomerProvidedEncryptionKey cpk:
            Encrypts the data on the service-side with the given key.
            Use of customer-provided keys must be done over HTTPS.
        :return: dict of the response header

        .. admonition:: Example:

            .. literalinclude:: ../samples/datalake_samples_upload_download.py
                :start-after: [START append_data]
                :end-before: [END append_data]
                :language: python
                :dedent: 4
                :caption: Append data to the file.
        """
        options = self._append_data_options(
            data=data,
            offset=offset,
            scheme=self.scheme,
            length=length,
            **kwargs)
        try:
            return self._client.path.append_data(**options)
        except HttpResponseError as error:
            process_storage_error(error)

    @staticmethod
    def _flush_data_options(
            offset, # type: int
            scheme, # type: str
            content_settings=None, # type: Optional[ContentSettings]
            retain_uncommitted_data=False, # type: Optional[bool]
            **kwargs
        ):
        # type: (...) -> Dict[str, Any]

        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_mod_conditions(kwargs)

        path_http_headers = None
        if content_settings:
            path_http_headers = get_path_http_headers(content_settings)

        cpk_info = get_cpk_info(scheme, kwargs)

        options = {
            'position': offset,
            'content_length': 0,
            'path_http_headers': path_http_headers,
            'retain_uncommitted_data': retain_uncommitted_data,
            'close': kwargs.pop('close', False),
            'lease_access_conditions': access_conditions,
            'modified_access_conditions': mod_conditions,
            'cpk_info': cpk_info,
            'timeout': kwargs.pop('timeout', None),
            'cls': return_response_headers}
        options.update(kwargs)
        return options

    def flush_data(self, offset,  # type: int
                   retain_uncommitted_data=False,   # type: Optional[bool]
                   **kwargs):
        # type: (...) -> Dict[str, Union[str, datetime]]
        """ Commit the previous appended data.

        :param offset: offset is equal to the length of the file after commit the
            previous appended data.
        :param bool retain_uncommitted_data: Valid only for flush operations.  If
            "true", uncommitted data is retained after the flush operation
            completes; otherwise, the uncommitted data is deleted after the flush
            operation.  The default is false.  Data at offsets less than the
            specified position are written to the file when flush succeeds, but
            this optional parameter allows data after the flush position to be
            retained for a future flush operation.
        :keyword ~azure.storage.filedatalake.ContentSettings content_settings:
            ContentSettings object used to set path properties.
        :keyword bool close: Azure Storage Events allow applications to receive
            notifications when files change. When Azure Storage Events are
            enabled, a file changed event is raised. This event has a property
            indicating whether this is the final change to distinguish the
            difference between an intermediate flush to a file stream and the
            final close of a file stream. The close query parameter is valid only
            when the action is "flush" and change notifications are enabled. If
            the value of close is "true" and the flush operation completes
            successfully, the service raises a file change notification with a
            property indicating that this is the final update (the file stream has
            been closed). If "false" a change notification is raised indicating
            the file has changed. The default is false. This query parameter is
            set to true by the Hadoop ABFS driver to indicate that the file stream
            has been closed."
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
        :return: response header in dict

        .. admonition:: Example:

            .. literalinclude:: ../samples/datalake_samples_file_system.py
                :start-after: [START upload_file_to_file_system]
                :end-before: [END upload_file_to_file_system]
                :language: python
                :dedent: 8
                :caption: Commit the previous appended data.
        """
        options = self._flush_data_options(
            offset,
            self.scheme,
            retain_uncommitted_data=retain_uncommitted_data, **kwargs)
        try:
            return self._client.path.flush_data(**options)
        except HttpResponseError as error:
            process_storage_error(error)

    def download_file(self, offset=None, length=None, **kwargs):
        # type: (Optional[int], Optional[int], Any) -> StorageStreamDownloader
        """Downloads a file to the StorageStreamDownloader. The readall() method must
        be used to read all the content, or readinto() must be used to download the file into
        a stream. Using chunks() returns an iterator which allows the user to iterate over the content in chunks.

        :param int offset:
            Start of byte range to use for downloading a section of the file.
            Must be set if length is provided.
        :param int length:
            Number of bytes to read from the stream. This is optional, but
            should be supplied for optimal performance.
        :keyword lease:
            If specified, download only succeeds if the file's lease is active
            and matches this ID. Required if the file has an active lease.
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
            Required if the file was created with a Customer-Provided Key.
        :keyword int max_concurrency:
            The number of parallel connections with which to download.
        :keyword int timeout:
            The timeout parameter is expressed in seconds. This method may make
            multiple calls to the Azure service and the timeout will apply to
            each call individually.
        :returns: A streaming object (StorageStreamDownloader)
        :rtype: ~azure.storage.filedatalake.StorageStreamDownloader

        .. admonition:: Example:

            .. literalinclude:: ../samples/datalake_samples_upload_download.py
                :start-after: [START read_file]
                :end-before: [END read_file]
                :language: python
                :dedent: 4
                :caption: Return the downloaded data.
        """
        downloader = self._blob_client.download_blob(offset=offset, length=length, **kwargs)
        return StorageStreamDownloader(downloader)

    def exists(self, **kwargs):
        # type: (**Any) -> bool
        """
        Returns True if a file exists and returns False otherwise.

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: boolean
        """
        return self._exists(**kwargs)

    def rename_file(self, new_name, **kwargs):
        # type: (str, **Any) -> DataLakeFileClient
        """
        Rename the source file.

        :param str new_name: the new file name the user want to rename to.
            The value must have the following format: "{filesystem}/{directory}/{subdirectory}/{file}".
        :keyword ~azure.storage.filedatalake.ContentSettings content_settings:
            ContentSettings object used to set path properties.
        :keyword source_lease: A lease ID for the source path. If specified,
         the source path must have an active lease and the leaase ID must
         match.
        :paramtype source_lease: ~azure.storage.filedatalake.DataLakeLeaseClient or str
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
        :return: the renamed file client
        :rtype: DataLakeFileClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/datalake_samples_upload_download.py
                :start-after: [START rename_file]
                :end-before: [END rename_file]
                :language: python
                :dedent: 4
                :caption: Rename the source file.
        """
        new_name = new_name.strip('/')
        new_file_system = new_name.split('/')[0]
        new_path_and_token = new_name[len(new_file_system):].strip('/').split('?')
        new_path = new_path_and_token[0]
        try:
            new_file_sas = new_path_and_token[1] or self._query_str.strip('?')
        except IndexError:
            if not self._raw_credential and new_file_system != self.file_system_name:
                raise ValueError("please provide the sas token for the new file")
            if not self._raw_credential and new_file_system == self.file_system_name:
                new_file_sas = self._query_str.strip('?')

        new_file_client = DataLakeFileClient(
            "{}://{}".format(self.scheme, self.primary_hostname), new_file_system, file_path=new_path,
            credential=self._raw_credential or new_file_sas,
            _hosts=self._hosts, _configuration=self._config, _pipeline=self._pipeline,
            _location_mode=self._location_mode
        )
        new_file_client._rename_path(  # pylint: disable=protected-access
            '/{}/{}{}'.format(quote(unquote(self.file_system_name)),
                              quote(unquote(self.path_name)),
                              self._query_str),
            **kwargs)
        return new_file_client

    def query_file(self, query_expression, **kwargs):
        # type: (str, **Any) -> DataLakeFileQueryReader
        """
        Enables users to select/project on datalake file data by providing simple query expressions.
        This operations returns a DataLakeFileQueryReader, users need to use readall() or readinto() to get query data.

        :param str query_expression:
            Required. a query statement.
            eg. Select * from DataLakeStorage
        :keyword Callable[~azure.storage.filedatalake.DataLakeFileQueryError] on_error:
            A function to be called on any processing errors returned by the service.
        :keyword file_format:
            Optional. Defines the serialization of the data currently stored in the file. The default is to
            treat the file data as CSV data formatted in the default dialect. This can be overridden with
            a custom DelimitedTextDialect, or DelimitedJsonDialect or "ParquetDialect" (passed as a string or enum).
            These dialects can be passed through their respective classes, the QuickQueryDialect enum or as a string.
        :paramtype file_format:
            ~azure.storage.filedatalake.DelimitedTextDialect or ~azure.storage.filedatalake.DelimitedJsonDialect or
            ~azure.storage.filedatalake.QuickQueryDialect or str
        :keyword output_format:
            Optional. Defines the output serialization for the data stream. By default the data will be returned
            as it is represented in the file. By providing an output format,
            the file data will be reformatted according to that profile.
            This value can be a DelimitedTextDialect or a DelimitedJsonDialect or ArrowDialect.
            These dialects can be passed through their respective classes, the QuickQueryDialect enum or as a string.
        :paramtype output_format:
            ~azure.storage.filedatalake.DelimitedTextDialect or ~azure.storage.filedatalake.DelimitedJsonDialect
            or list[~azure.storage.filedatalake.ArrowDialect] or ~azure.storage.filedatalake.QuickQueryDialect or str
        :keyword lease:
            Required if the file has an active lease. Value can be a DataLakeLeaseClient object
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
            Required if the file was created with a Customer-Provided Key.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: A streaming object (DataLakeFileQueryReader)
        :rtype: ~azure.storage.filedatalake.DataLakeFileQueryReader

        .. admonition:: Example:

            .. literalinclude:: ../samples/datalake_samples_query.py
                :start-after: [START query]
                :end-before: [END query]
                :language: python
                :dedent: 4
                :caption: select/project on datalake file data by providing simple query expressions.
        """
        query_expression = query_expression.replace("from DataLakeStorage", "from BlobStorage")
        blob_quick_query_reader = self._blob_client.query_blob(query_expression,
                                                               blob_format=kwargs.pop('file_format', None),
                                                               error_cls=DataLakeFileQueryError,
                                                               **kwargs)
        return DataLakeFileQueryReader(blob_quick_query_reader)
