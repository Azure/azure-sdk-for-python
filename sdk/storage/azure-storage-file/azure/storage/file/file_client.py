# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import functools
from io import BytesIO

try:
    from urllib.parse import urlparse, quote, unquote
except ImportError:
    from urlparse import urlparse
    from urllib2 import quote, unquote

import six

from ._generated import AzureFileStorage
from ._generated.version import VERSION
from ._generated.models import StorageErrorException, FileHTTPHeaders
from ._shared.upload_chunking import IterStreamer
from ._shared.shared_access_signature import FileSharedAccessSignature
from ._shared.utils import (
    StorageAccountHostsMixin,
    parse_query,
    get_length,
    return_response_headers,
    add_metadata_headers,
    process_storage_error,
    parse_connection_str)
from ._share_utils import upload_file_helper, deserialize_file_properties, StorageStreamDownloader
from .polling import CopyStatusPoller

from ._share_utils import deserialize_directory_properties


class FileClient(StorageAccountHostsMixin):
    """
    A client to interact with the file.
    """
    def __init__(
            self, file_url,  # type: str
            share=None,  # type: Optional[Union[str, ShareProperties]]
            file_path=None,  # type: Optional[str]
            snapshot=None,  # type: Optional[Union[str, Dict[str, Any]]]
            credential=None,  # type: Optional[Any]
            **kwargs  # type: Any
        ):
        # type: (...) -> FileClient
        """ Creates a new FileClient. This client represents interaction with a specific
        file, although that file may not yet exist.
        :param str file_url: The full URI to the file.
        :param share: The share with which to interact. If specified, this value will override
         a share value specified in the share URL.
        :type share: str or ~azure.storage.file.models.ShareProperties
        :param credentials:
        :param configuration: A optional pipeline configuration.
        """
        try:
            if not file_url.lower().startswith('http'):
                file_url = "https://" + file_url
        except AttributeError:
            raise ValueError("File URL must be a string.")
        parsed_url = urlparse(file_url.rstrip('/'))
        if not parsed_url.path and not (share and file_path):
            raise ValueError("Please specify a share and file name.")
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(file_url))
        if hasattr(credential, 'get_token'):
            raise ValueError("Token credentials not supported by the File service.")

        path_share, path_file = "", ""
        path_snapshot = None
        if parsed_url.path:
            path_share, _, path_file = parsed_url.path.lstrip('/').partition('/')
        path_snapshot, sas_token = parse_query(parsed_url.query)
        if not sas_token and not credential:
            raise ValueError(
                'You need to provide either an account key or SAS token when creating a storage service.')
        try:
            self.snapshot = snapshot.snapshot
        except AttributeError:
            try:
                self.snapshot = snapshot['snapshot']
            except TypeError:
                self.snapshot = snapshot or path_snapshot

        try:
            self.share_name = share.name
        except AttributeError:
            self.share_name = share or unquote(path_share)
        if file_path:
            self.file_path = file_path.split('/')
        else:
            self.file_path = [unquote(p) for p in path_file.split('/')]

        self.file_name = self.file_path[-1]
        self.directory_path = "/".join(self.file_path[:-1])
        self._query_str, credential = self._format_query_string(
            sas_token, credential, share_snapshot=self.snapshot)
        super(FileClient, self).__init__(parsed_url, 'file', credential, **kwargs)
        self._client = AzureFileStorage(version=VERSION, url=self.url, pipeline=self._pipeline)

    def _format_url(self, hostname):
        share_name = self.share_name
        if isinstance(share_name, six.text_type):
            share_name = share_name.encode('UTF-8')
        return "{}://{}/{}/{}{}".format(
            self.scheme,
            hostname,
            quote(share_name),
            "/".join([quote(p, safe='~') for p in self.file_path]),
            self._query_str)

    @classmethod
    def from_connection_string(
            cls, conn_str,  # type: str
            share=None, # type: Optional[Union[str, ShareProperties]]
            file_path=None, # type: Optional[str]
            snapshot=None,  # type: Optional[Union[str, Dict[str, Any]]]
            credential=None,  # type: Optional[Any]
            **kwargs # type: Any
        ):
        # type: (...) -> FileClient
        """
        Create FileClient from a Connection String.
        """
        account_url, secondary, credential = parse_connection_str(conn_str, credential, 'file')
        if 'secondary_hostname' not in kwargs:
            kwargs['secondary_hostname'] = secondary
        return cls(
            account_url, share=share, file_path=file_path, snapshot=snapshot, credential=credential, **kwargs)

    def generate_shared_access_signature(
            self, permission=None,  # type: Optional[Union[FilePermissions, str]]
            expiry=None,  # type: Optional[Union[datetime, str]]
            start=None,  # type: Optional[Union[datetime, str]]
            policy_id=None,  # type: Optional[str]
            ip=None,  # type: Optional[str]
            protocol=None,  # type: Optional[str]
            cache_control=None,  # type: Optional[str]
            content_disposition=None,  # type: Optional[str]
            content_encoding=None,  # type: Optional[str]
            content_language=None,  # type: Optional[str]
            content_type=None  # type: Optional[str]
        ):
        # type: (...) -> str
        """
        Generates a shared access signature for the blob.
        Use the returned signature with the credential parameter of any BlobServiceClient,
        ContainerClient or BlobClient.

        :param ~azure.storage.file.models.FilePermissions permission:
            The permissions associated with the shared access signature. The
            user is restricted to operations allowed by the permissions.
            Permissions must be ordered read, write, delete, list.
            Required unless an id is given referencing a stored access policy
            which contains this field. This field must be omitted if it has been
            specified in an associated stored access policy.
        :param expiry:
            The time at which the shared access signature becomes invalid.
            Required unless an id is given referencing a stored access policy
            which contains this field. This field must be omitted if it has
            been specified in an associated stored access policy. Azure will always
            convert values to UTC. If a date is passed in without timezone info, it
            is assumed to be UTC.
        :type expiry: datetime or str
        :param start:
            The time at which the shared access signature becomes valid. If
            omitted, start time for this call is assumed to be the time when the
            storage service receives the request. Azure will always convert values
            to UTC. If a date is passed in without timezone info, it is assumed to
            be UTC.
        :type start: datetime or str
        :param str policy_id:
            A unique value up to 64 characters in length that correlates to a
            stored access policy. To create a stored access policy, use
            :func:`~ContainerClient.set_container_access_policy()`.
        :param str ip:
            Specifies an IP address or a range of IP addresses from which to accept requests.
            If the IP address from which the request originates does not match the IP address
            or address range specified on the SAS token, the request is not authenticated.
            For example, specifying sip=168.1.5.65 or sip=168.1.5.60-168.1.5.70 on the SAS
            restricts the request to those IP addresses.
        :param str protocol:
            Specifies the protocol permitted for a request made. The default value is https.
        :param str cache_control:
            Response header value for Cache-Control when resource is accessed
            using this shared access signature.
        :param str content_disposition:
            Response header value for Content-Disposition when resource is accessed
            using this shared access signature.
        :param str content_encoding:
            Response header value for Content-Encoding when resource is accessed
            using this shared access signature.
        :param str content_language:
            Response header value for Content-Language when resource is accessed
            using this shared access signature.
        :param str content_type:
            Response header value for Content-Type when resource is accessed
            using this shared access signature.
        :return: A Shared Access Signature (sas) token.
        :rtype: str
        """
        if not hasattr(self.credential, 'account_key') or not self.credential.account_key:
            raise ValueError("No account SAS key available.")
        sas = FileSharedAccessSignature(self.credential.account_name, self.credential.account_key)
        if len(self.file_path) > 1:
            file_path = '/'.join(self.file_path[:-1])
        else:
            file_path = None
        return sas.generate_file(
            self.share_name,
            file_path,
            self.file_name,
            permission,
            expiry,
            start=start,
            policy_id=policy_id,
            ip=ip,
            protocol=protocol,
            cache_control=cache_control,
            content_disposition=content_disposition,
            content_encoding=content_encoding,
            content_language=content_language,
            content_type=content_type)

    def create_file(
            self, size, # type: int
            content_settings=None, # type: Optional[ContentSettings]
            metadata=None,  # type: Optional[Dict[str, str]]
            timeout=None, # type: Optional[int]
            **kwargs # type: Any
        ):
        # type: (...) -> Dict[str, Any]
        """Creates a new FileClient.
        :param metadata:
            Name-value pairs associated with the file as metadata.
        :type metadata: dict(str, str)
        :param int quota:
            The quota to be alloted.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: File-updated property dict (Etag and last modified).
        :rtype: dict(str, Any)
        """
        if self.require_encryption and not self.key_encryption_key:
            raise ValueError("Encryption required but no key was provided.")

        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata))
        file_http_headers = None
        if content_settings:
            file_http_headers = FileHTTPHeaders(
                file_cache_control=content_settings.cache_control,
                file_content_type=content_settings.content_type,
                file_content_md5=bytearray(content_settings.content_md5) if content_settings.content_md5 else None,
                file_content_encoding=content_settings.content_encoding,
                file_content_language=content_settings.content_language,
                file_content_disposition=content_settings.content_disposition
            )
        try:
            return self._client.file.create(
                file_content_length=size,
                timeout=timeout,
                metadata=metadata,
                file_http_headers=file_http_headers,
                headers=headers,
                cls=return_response_headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    def upload_file(
            self, data, # type: Any
            length=None, # type: Optional[int]
            metadata=None,  # type: Optional[Dict[str, str]]
            content_settings=None, # type: Optional[ContentSettings]
            validate_content=False,  # type: bool
            max_connections=1,  # type: Optional[int]
            timeout=None, # type: Optional[int]
            encoding='UTF-8',  # type: str
            **kwargs # type: Any
        ):
        # type: (...) -> Dict[str, Any]
        """Uploads a new file.
        :param data:
            Data of the file.
        :type data: Any
        :param size:
            The max size of the file.
        :type size: int
        :param content_settings:
            The content settings
        :param metadata:
            Name-value pairs associated with the file as metadata.
        :type metadata: dict(str, str)
        :param validate_content:
            If the content is validated or not.
        :type validate_content: bool
        :param int max_connections:
            The max_connections to be alloted.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: File-updated property dict (Etag and last modified).
        :rtype: dict(str, Any)
        """
        if self.require_encryption or (self.key_encryption_key is not None):
            raise ValueError("Encryption not supported.")

        if isinstance(data, six.text_type):
            data = data.encode(encoding)
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
        return upload_file_helper(
            self,
            stream,
            length,
            metadata,
            content_settings,
            validate_content,
            timeout,
            max_connections,
            self._config.data_settings,
            **kwargs)

    def copy_file_from_url(
            self, source_url, # type: str
            metadata=None,  # type: Optional[Dict[str, str]]
            timeout=None, # type: Optional[int]
            **kwargs # type: Any
        ):
        # type: (...) -> Any
        """Creates a new FileClient.
        :param metadata:
            Name-value pairs associated with the file as metadata.
        :type metadata: dict(str, str)
        :param int quota:
            The quota to be alloted.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: Polling object in order to wait on or abort the operation
        :rtype: Any
        """
        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata))

        try:
            start_copy = self._client.file.start_copy(
                source_url,
                timeout=None,
                metadata=metadata,
                headers=headers,
                cls=return_response_headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

        poller = CopyStatusPoller(
            self, start_copy,
            configuration=self._config,
            timeout=timeout)
        return poller

    def download_file(
            self, offset=None,  # type: Optional[int]
            length=None,  # type: Optional[int]
            validate_content=False,  # type: bool
            timeout=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> Iterable[bytes]
        """
        :returns: A iterable data generator (stream)
        """
        if self.require_encryption or (self.key_encryption_key is not None):
            raise ValueError("Encryption not supported.")
        if length is not None and offset is None:
            raise ValueError("Offset value must not be None is length is set.")

        return StorageStreamDownloader(
            share=self.share_name,
            file_name=self.file_name,
            file_path='/'.join(self.file_path),
            service=self._client.file,
            config=self._config.data_settings,
            offset=offset,
            length=length,
            validate_content=validate_content,
            timeout=timeout,
            **kwargs)

    def delete_file(self, timeout=None, **kwargs):
        # type: (Optional[int], Optional[Any]) -> None
        """Marks the specified file for deletion. The file is
        later deleted during garbage collection.

        :param int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None
        """
        try:
            self._client.file.delete(timeout=timeout, **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    def get_file_properties(self, timeout=None, **kwargs):
        # type: (Optional[int], Any) -> FileProperties
        """
        :returns: FileProperties
        """
        try:
            file_props = self._client.file.get_properties(
                sharesnapshot=self.snapshot,
                timeout=timeout,
                cls=deserialize_file_properties,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)
        file_props.name = self.file_name
        file_props.share_name = self.share_name
        return file_props

    def set_http_headers(self, content_settings, timeout=None, **kwargs):
        #type: (ContentSettings, Optional[int], Optional[Any]) -> Dict[str, Any]
        """
        :returns: File-updated property dict (Etag and last modified).
        :rtype: dict(str, Any) 
        """
        file_content_length = kwargs.pop('size', None)
        file_http_headers = FileHTTPHeaders(
                file_cache_control=content_settings.cache_control,
                file_content_type=content_settings.content_type,
                file_content_md5=bytearray(content_settings.content_md5) if content_settings.content_md5 else None,
                file_content_encoding=content_settings.content_encoding,
                file_content_language=content_settings.content_language,
                file_content_disposition=content_settings.content_disposition
            )
        try:
            return self._client.file.set_http_headers(
                timeout=timeout,
                file_content_length=file_content_length,
                file_http_headers=file_http_headers,
                cls=return_response_headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    def set_file_metadata(self, metadata=None, timeout=None, **kwargs):
        #type: (Optional[Dict[str, Any]], Optional[int], Optional[Any]) -> Dict[str, Any]
        """
        :returns: File-updated property dict (Etag and last modified).
        :rtype: dict(str, Any) 
        """
        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata))
        try:
            return self._client.file.set_metadata(
                timeout=timeout,
                cls=return_response_headers,
                headers=headers,
                metadata=metadata,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    def upload_range(
            self, data,  # type: bytes
            start_range, # type: int
            end_range, # type: int
            validate_content=False, # type: Optional[bool]
            timeout=None, # type: Optional[int]
            encoding='UTF-8',
            **kwargs
        ):
        # type: (...) -> List[dict[str, int]]
        """
        Returns dict with etag and last-modified.
        :param int start_range:
            Start of byte range to use for getting valid page ranges.
            If no end_range is given, all bytes after the start_range will be searched.
            Pages must be aligned with 512-byte boundaries, the start offset
            must be a modulus of 512 and the end offset must be a modulus of
            512-1. Examples of valid byte ranges are 0-511, 512-, etc.
        :param int end_range:
            End of byte range to use for getting valid page ranges.
            If end_range is given, start_range must be provided.
            This range will return valid page ranges for from the offset start up to
            offset end.
            Pages must be aligned with 512-byte boundaries, the start offset
            must be a modulus of 512 and the end offset must be a modulus of
            512-1. Examples of valid byte ranges are 0-511, 512-, etc.
        :param validate_content:
            If the content is validated or not.
        :type validate_content: bool
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: Returns dict with etag and last-modified .
        """
        if self.require_encryption or (self.key_encryption_key is not None):
            raise ValueError("Encryption not supported.")
        if isinstance(data, six.text_type):
            data = data.encode(encoding)

        content_range = 'bytes={0}-{1}'.format(start_range, end_range)
        content_length = end_range - start_range + 1
        try:
            return self._client.file.upload_range(
                range=content_range,
                content_length=content_length,
                optionalbody=data,
                timeout=timeout,
                validate_content=validate_content,
                cls=return_response_headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    def get_ranges(
            self, start_range=None, # type: Optional[int]
            end_range=None, # type: Optional[int]
            timeout=None, # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> List[dict[str, int]]
        """
        Returns the list of valid ranges of a file.
        :param int start_range:
            Start of byte range to use for getting valid page ranges.
            If no end_range is given, all bytes after the start_range will be searched.
            Pages must be aligned with 512-byte boundaries, the start offset
            must be a modulus of 512 and the end offset must be a modulus of
            512-1. Examples of valid byte ranges are 0-511, 512-, etc.
        :param int end_range:
            End of byte range to use for getting valid page ranges.
            If end_range is given, start_range must be provided.
            This range will return valid page ranges for from the offset start up to
            offset end.
            Pages must be aligned with 512-byte boundaries, the start offset
            must be a modulus of 512 and the end offset must be a modulus of
            512-1. Examples of valid byte ranges are 0-511, 512-, etc.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: A list of page ranges.
        """
        if self.require_encryption or (self.key_encryption_key is not None):
            raise ValueError("Unsupported method for encryption.")

        content_range = None
        if start_range is not None:
            if end_range is not None:
                content_range = 'bytes={0}-{1}'.format(start_range, end_range)
            else:
                content_range = 'bytes={0}-'.format(start_range)
        try:
            ranges = self._client.file.get_range_list(
                sharesnapshot=self.snapshot,
                timeout=timeout,
                range=content_range,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)
        return [{'start': b.start, 'end': b.end} for b in ranges]

    def clear_range(
            self, start_range,  # type: int
            end_range,  # type: int
            timeout=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> Dict[str, Any]
        """
        :param int start_range:
            Start of byte range to use for writing to a section of the file.
            Pages must be aligned with 512-byte boundaries, the start offset
            must be a modulus of 512 and the end offset must be a modulus of
            512-1. Examples of valid byte ranges are 0-511, 512-1023, etc.
        :param int end_range:
            End of byte range to use for writing to a section of the file.
            Pages must be aligned with 512-byte boundaries, the start offset
            must be a modulus of 512 and the end offset must be a modulus of
            512-1. Examples of valid byte ranges are 0-511, 512-1023, etc.
        :returns: File-updated property dict (Etag and last modified).
        :rtype: Dict[str, Any]
        """
        if self.require_encryption or (self.key_encryption_key is not None):
            raise ValueError("Unsupported method for encryption.")

        if start_range is None or start_range % 512 != 0:
            raise ValueError("start_range must be an integer that aligns with 512 file size")
        if end_range is None or end_range % 512 != 511:
            raise ValueError("end_range must be an integer that aligns with 512 file size")
        content_range = 'bytes={0}-{1}'.format(start_range, end_range)
        try:
            return self._client.file.upload_range(
                timeout=timeout,
                cls=return_response_headers,
                content_length=0,
                file_range_write="clear",
                range=content_range,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    def resize_file(self, size, timeout=None, **kwargs):
        # type: (int, Optional[int], Optional[Any]) -> Dict[str, Any]
        """Resizes a file to the specified size.
        :param int size:
            Size to resize file to.
        :param str timeout:
            The timeout parameter is expressed in seconds.
        :returns: File-updated property dict (Etag and last modified).
        :rtype: Dict[str, Any]
        """
        try:
            return self._client.file.set_http_headers(
                timeout=timeout,
                file_content_length=size,
                cls=return_response_headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)
