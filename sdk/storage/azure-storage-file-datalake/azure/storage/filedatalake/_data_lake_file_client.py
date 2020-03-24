# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from io import BytesIO
import six

from ._shared.base_client import parse_connection_str
from ._shared.request_handlers import get_length, read_length
from ._shared.response_handlers import return_response_headers
from ._shared.uploads import IterStreamer
from ._upload_helper import upload_datalake_file
from ._generated.models import StorageErrorException
from ._download import StorageStreamDownloader
from ._path_client import PathClient
from ._serialize import get_mod_conditions, get_path_http_headers, get_access_conditions, add_metadata_headers
from ._deserialize import process_storage_error
from ._models import FileProperties


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
        account URL already has a SAS token. The value can be a SAS token string, and account
        shared access key, or an instance of a TokenCredentials class from azure.identity.
        If the URL already has a SAS token, specifying an explicit credential will take priority.

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
            cls, conn_str,  # type: str
            file_system_name,  # type: str
            file_path,  # type: str
            credential=None,  # type: Optional[Any]
            **kwargs  # type: Any
        ):  # type: (...) -> DataLakeFileClient
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
            access key values. The value can be a SAS token string, and account shared access
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
        blob_properties = self._get_path_properties(**kwargs)
        return FileProperties._from_blob_properties(blob_properties)  # pylint: disable=protected-access

    def _upload_options(  # pylint:disable=too-many-statements
            self, data,  # type: Union[Iterable[AnyStr], IO[AnyStr]]
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

        if content_settings:
            kwargs['path_http_headers'] = get_path_http_headers(content_settings)

        kwargs['stream'] = stream
        kwargs['length'] = length
        kwargs['validate_content'] = validate_content
        kwargs['max_concurrency'] = max_concurrency
        kwargs['client'] = self._client.path

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
        :keyword str umaskoverwrite: Optional and only valid if Hierarchical Namespace is enabled for the account.
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
        :return: response dict (Etag and last modified).
        """
        options = self._upload_options(
            data,
            length=length,
            overwrite=overwrite,
            **kwargs)
        return upload_datalake_file(**options)

    @staticmethod
    def _append_data_options(data, offset, length=None, **kwargs):
        # type: (Optional[ContentSettings], Optional[Dict[str, str]], **Any) -> Dict[str, Any]

        if isinstance(data, six.text_type):
            data = data.encode(kwargs.pop('encoding', 'UTF-8'))  # type: ignore
        if length is None:
            length = get_length(data)
            if length is None:
                length, data = read_length(data)
        if isinstance(data, bytes):
            data = data[:length]

        access_conditions = get_access_conditions(kwargs.pop('lease', None))

        options = {
            'body': data,
            'position': offset,
            'content_length': length,
            'lease_access_conditions': access_conditions,
            'validate_content': kwargs.pop('validate_content', False),
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
            data,
            offset,
            length=length,
            **kwargs)
        try:
            return self._client.path.append_data(**options)
        except StorageErrorException as error:
            process_storage_error(error)

    @staticmethod
    def _flush_data_options(offset, content_settings=None, retain_uncommitted_data=False, **kwargs):
        # type: (Optional[ContentSettings], Optional[Dict[str, str]], **Any) -> Dict[str, Any]

        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_mod_conditions(kwargs)

        path_http_headers = None
        if content_settings:
            path_http_headers = get_path_http_headers(content_settings)

        options = {
            'position': offset,
            'content_length': 0,
            'path_http_headers': path_http_headers,
            'retain_uncommitted_data': retain_uncommitted_data,
            'close': kwargs.pop('close', False),
            'lease_access_conditions': access_conditions,
            'modified_access_conditions': mod_conditions,
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
            retain_uncommitted_data=retain_uncommitted_data, **kwargs)
        try:
            return self._client.path.flush_data(**options)
        except StorageErrorException as error:
            process_storage_error(error)

    def download_file(self, offset=None, length=None, **kwargs):
        # type: (Optional[int], Optional[int], Any) -> StorageStreamDownloader
        """Downloads a file to the StorageStreamDownloader. The readall() method must
        be used to read all the content, or readinto() must be used to download the file into
        a stream.

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

    def rename_file(self, new_name,  # type: str
                    **kwargs):
        # type: (**Any) -> DataLakeFileClient
        """
        Rename the source file.

        :param str new_name: the new file name the user want to rename to.
            The value must have the following format: "{filesystem}/{directory}/{subdirectory}/{file}".
        :keyword source_lease: A lease ID for the source path. If specified,
         the source path must have an active lease and the leaase ID must
         match.
        :paramtype source_lease: ~azure.storage.filedatalake.DataLakeLeaseClient or str
        :keyword ~azure.storage.filedatalake.ContentSettings content_settings:
            ContentSettings object used to set path properties.
        :keyword lease:
            Required if the file/directory has an active lease. Value can be a LeaseClient object
            or the lease ID as a string.
        :type lease: ~azure.storage.filedatalake.DataLakeLeaseClient or str
        :keyword str umask:
            Optional and only valid if Hierarchical Namespace is enabled for the account.
            When creating a file or directory and the parent folder does not have a default ACL,
            the umask restricts the permissions of the file or directory to be created.
            The resulting permission is given by p & ^u, where p is the permission and u is the umask.
            For example, if p is 0777 and u is 0057, then the resulting permission is 0720.
            The default permission is 0777 for a directory and 0666 for a file. The default umask is 0027.
            The umask must be specified in 4-digit octal notation (e.g. 0766).
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
        path = new_name[len(new_file_system):]

        new_directory_client = DataLakeFileClient(
            self.url, new_file_system, file_path=path, credential=self._raw_credential,
            _hosts=self._hosts, _configuration=self._config, _pipeline=self._pipeline,
            _location_mode=self._location_mode, require_encryption=self.require_encryption,
            key_encryption_key=self.key_encryption_key,
            key_resolver_function=self.key_resolver_function)
        new_directory_client._rename_path('/'+self.file_system_name+'/'+self.path_name,  # pylint: disable=protected-access
                                          **kwargs)
        return new_directory_client
