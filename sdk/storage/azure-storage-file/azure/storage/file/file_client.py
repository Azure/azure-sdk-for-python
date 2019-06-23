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

from .models import DirectoryPropertiesPaged
from ._generated import AzureFileStorage
from ._generated.version import VERSION
from ._generated.models import StorageErrorException, FileHTTPHeaders
from ._shared.utils import (
    StorageAccountHostsMixin,
    parse_query,
    return_response_headers,
    add_metadata_headers,
    process_storage_error,
    parse_connection_str)
from ._shared.encryption import _generate_file_encryption_data
from ._share_utils import upload_file_helper, deserialize_file_properties, StorageStreamDownloader
from ._upload_chunking import IterStreamer
from .polling import CopyStatusPoller

from ._share_utils import deserialize_directory_properties


class FileClient(StorageAccountHostsMixin):
    """
    A client to interact with the file.
    """
    def __init__(
            self, file_url,  # type: str
            share_name=None,  # type: Optional[Union[str, ShareProperties]]
            directory_path=None, # type: Optional[str]
            snapshot=None,  # type: Optional[Union[str, Dict[str, Any]]]
            credential=None,  # type: Optional[Any]
            configuration=None,  # type: Optional[Configuration]
            **kwargs  # type: Any
        ):
        # type: (...) -> FileClient
        """ Creates a new FileClient. This client represents interaction with a specific
        file, although that file may not yet exist.
        :param str file_url: The full URI to the file.
        :param share_name: The share with which to interact. If specified, this value will override
         a share value specified in the share URL.
        :type share_name: str or ~azure.storage.file.models.ShareProperties
        :param credentials:
        :param configuration: A optional pipeline configuration.
        """
        try:
            if not file_url.lower().startswith('http'):
                file_url = "https://" + file_url
        except AttributeError:
            raise ValueError("File URL must be a string.")
        parsed_url = urlparse(file_url.rstrip('/'))
        if not parsed_url.path and not (share_name and directory_path):
            raise ValueError("Please specify a directory_path and share_name.")
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(file_url))

        path_share = ""
        if parsed_url.path:
            path_share, _, path_file = parsed_url.path.lstrip('/').partition('/')
        _, sas_token = parse_query(parsed_url.query)

        try:
            self.share_name = share_name.name
        except AttributeError:
            self.share_name = share_name or unquote(path_share)
        self.file_name = unquote(path_file.split('/')[-1]) or ""
        self.directory_name = unquote(path_file.split('/')[-2]) if directory_path else ""
        self._query_str, credential = self._format_query_string(sas_token, credential)
        super(FileClient, self).__init__(parsed_url, credential, configuration, **kwargs)
        self._client = AzureFileStorage(version=VERSION, url=self.url, pipeline=self._pipeline)
    
    @classmethod
    def from_connection_string(
            cls, conn_str,  # type: str
            share_name=None, # type: Optional[Union[str, ShareProperties]]
            directory_path=None, # type: Optional[str]
            file_name=None, # type: Optional[str]
            credential=None,  # type: Optional[Any]
            configuration=None, # type: Optional[Configuration]
            **kwargs # type: Any
        ):
        # type: (...) -> FileClient
        """
        Create FileClient from a Connection String.
        """
        account_url, credential = parse_connection_str(conn_str, credential)

        return cls(
            account_url, share_name=share_name, directory_path=directory_path,
            credential=credential, configuration=configuration, **kwargs)

    def create_file(
            self, size=None, # type: Optional[int]
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
            size=None, # type: Optional[int]
            content_settings=None, # type: Optional[ContentSettings]
            metadata=None,  # type: Optional[Dict[str, str]]
            validate_content=False,  # type: bool
            max_connections=1,  # type: Optional[int]
            timeout=None, # type: Optional[int]
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
        if self.require_encryption and not self.key_encryption_key:
            raise ValueError("Encryption required but no key was provided.")

        _, _, encryption_data = None, None, None
        if self.key_encryption_key is not None:
            _, _, encryption_data = _generate_file_encryption_data(self.key_encryption_key)

        if isinstance(data, bytes):
            data = data[:size]

        if isinstance(data, bytes):
            stream = BytesIO(data)
        elif hasattr(data, 'read'):
            stream = data
        elif hasattr(data, '__iter__'):
            stream = IterStreamer(data)
        else:
            raise TypeError("Unsupported data type: {}".format(type(data)))

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
        return upload_file_helper(
            self._client.file,
            self.share_name,
            self.directory_name,
            self.file_name,
            stream,
            size,
            headers,
            file_http_headers,
            validate_content,
            timeout,
            max_connections,
            self._config.file_settings,
            encryption_data,
            **kwargs)

    def copy_from_url(
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
            self, start_range=None,  # type: Optional[int]
            end_range=None, # type: Optional[int]
            length=None,  # type: Optional[int]
            validate_content=False,  # type: bool
            timeout=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> Iterable[bytes]
        """
        :returns: A iterable data generator (stream)
        """
        if self.require_encryption and not self.key_encryption_key:
            raise ValueError("Encryption required but no key was provided.")

        return StorageStreamDownloader(
            name=self.file_name,
            share_name=self.share_name,
            directory_name=self.directory_name,
            service=self._client.file,
            config=self._config.file_settings,
            length=length,
            validate_content=validate_content,
            timeout=timeout,
            require_encryption=self.require_encryption,
            key_encryption_key=self.key_encryption_key,
            key_resolver_function=self.key_resolver_function,
            **kwargs)

    def download_file_to_stream(
            self, stream, # type: Any
            start_range=None,  # type: Optional[int]
            end_range=None, # type: Optional[int]
            length=None,  # type: Optional[int]
            validate_content=False,  # type: bool
            max_connections=1,  # type: Optional[int]
            timeout=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> FileProperties
        """
        :returns: FileProperties
        """

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

    def update_ranges(
            self, start_range=None, # type: Optional[int]
            end_range=None, # type: Optional[int]
            validate_content=False, # type: Optional[bool]
            timeout=None, # type: Optional[int]
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
            raise ValueError("Unsupported method for encryption.")

        if start_range is None or start_range % 512 != 0:
            raise ValueError("start_range must be an integer that aligns with 512 file size")
        if end_range is None or end_range % 512 != 511:
            raise ValueError("end_range must be an integer that aligns with 512 file size")
        content_range = 'bytes={0}-{1}'.format(start_range, end_range)
        try:
            return self._client.file.upload_range(
                range=content_range,
                timeout=timeout,
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

        if start_range is None or start_range % 512 != 0:
            raise ValueError("start_range must be an integer that aligns with 512 file size")
        if end_range is None or end_range % 512 != 511:
            raise ValueError("end_range must be an integer that aligns with 512 file size")
        content_range = 'bytes={0}-{1}'.format(start_range, end_range)
        try:
            return self._client.file.get_range_list(
                timeout=timeout,
                cls=return_response_headers,
                range=content_range,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)
    
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
