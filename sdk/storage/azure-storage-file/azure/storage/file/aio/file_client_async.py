# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import functools
from io import BytesIO
from typing import Optional, Union, IO, List, Dict, Any, Iterable, TYPE_CHECKING  # pylint: disable=unused-import

import six
from azure.core.polling import async_poller
from azure.core.async_paging import AsyncItemPaged

from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async

from .._generated.aio import AzureFileStorage
from .._generated.version import VERSION
from .._generated.models import StorageErrorException, FileHTTPHeaders
from .._shared.policies_async import ExponentialRetry
from .._shared.uploads_async import upload_data_chunks, FileChunkUploader, IterStreamer
from .._shared.downloads_async import StorageStreamDownloader
from .._shared.base_client_async import AsyncStorageAccountHostsMixin
from .._shared.request_handlers import add_metadata_headers, get_length
from .._shared.response_handlers import return_response_headers, process_storage_error
from .._deserialize import deserialize_file_properties, deserialize_file_stream
from ..file_client import FileClient as FileClientBase
from ._polling_async import CloseHandlesAsync
from .models import HandlesPaged

if TYPE_CHECKING:
    from datetime import datetime
    from ..models import ShareProperties, FilePermissions, ContentSettings, FileProperties
    from .._generated.models import HandleItem


async def _upload_file_helper(
    client,
    stream,
    size,
    metadata,
    content_settings,
    validate_content,
    timeout,
    max_connections,
    file_settings,
    **kwargs
):
    try:
        if size is None or size < 0:
            raise ValueError("A content size must be specified for a File.")
        response = await client.create_file(
            size, content_settings=content_settings, metadata=metadata, timeout=timeout, **kwargs
        )
        if size == 0:
            return response

        return await upload_data_chunks(
            service=client,
            uploader_class=FileChunkUploader,
            total_size=size,
            chunk_size=file_settings.max_range_size,
            stream=stream,
            max_connections=max_connections,
            validate_content=validate_content,
            timeout=timeout,
            **kwargs
        )
    except StorageErrorException as error:
        process_storage_error(error)


class FileClient(AsyncStorageAccountHostsMixin, FileClientBase):
    """A client to interact with a specific file, although that file may not yet exist.

    :ivar str url:
        The full endpoint URL to the File, including SAS token if used. This could be
        either the primary endpoint, or the secondard endpoint depending on the current `location_mode`.
    :ivar str primary_endpoint:
        The full primary endpoint URL.
    :ivar str primary_hostname:
        The hostname of the primary endpoint.
    :ivar str secondary_endpoint:
        The full secondard endpoint URL if configured. If not available
        a ValueError will be raised. To explicitly specify a secondary hostname, use the optional
        `secondary_hostname` keyword argument on instantiation.
    :ivar str secondary_hostname:
        The hostname of the secondary endpoint. If not available this
        will be None. To explicitly specify a secondary hostname, use the optional
        `secondary_hostname` keyword argument on instantiation.
    :ivar str location_mode:
        The location mode that the client is currently using. By default
        this will be "primary". Options include "primary" and "secondary".
    :param str file_url: The full URI to the file. This can also be a URL to the storage account
        or share, in which case the file and/or share must also be specified.
    :param share: The share for the file. If specified, this value will override
        a share value specified in the file URL.
    :type share: str or ~azure.storage.file.models.ShareProperties
    :param str file_path:
        The file path to the file with which to interact. If specified, this value will override
        a file value specified in the file URL.
    :param str snapshot:
        An optional file snapshot on which to operate.
    :param credential:
        The credential with which to authenticate. This is optional if the
        account URL already has a SAS token. The value can be a SAS token string or an account
        shared access key.
    """

    def __init__(  # type: ignore
        self,
        file_url,  # type: str
        share=None,  # type: Optional[Union[str, ShareProperties]]
        file_path=None,  # type: Optional[str]
        snapshot=None,  # type: Optional[Union[str, Dict[str, Any]]]
        credential=None,  # type: Optional[Any]
        loop=None,  # type: Any
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        kwargs["retry_policy"] = kwargs.get("retry_policy") or ExponentialRetry(**kwargs)
        super(FileClient, self).__init__(
            file_url, share=share, file_path=file_path, snapshot=snapshot, credential=credential, loop=loop, **kwargs
        )
        self._client = AzureFileStorage(version=VERSION, url=self.url, pipeline=self._pipeline, loop=loop)
        self._loop = loop

    @distributed_trace_async
    async def create_file(  # type: ignore
        self,
        size,  # type: int
        content_settings=None,  # type: Optional[ContentSettings]
        metadata=None,  # type: Optional[Dict[str, str]]
        timeout=None,  # type: Optional[int]
        **kwargs  # type: Any
    ):
        # type: (...) -> Dict[str, Any]
        """Creates a new file.

        Note that it only initializes the file with no content.

        :param int size: Specifies the maximum size for the file,
            up to 1 TB.
        :param ~azure.storage.file.models.ContentSettings content_settings:
            ContentSettings object used to set file properties.
        :param metadata:
            Name-value pairs associated with the file as metadata.
        :type metadata: dict(str, str)
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: File-updated property dict (Etag and last modified).
        :rtype: dict(str, Any)

        Example:
            .. literalinclude:: ../tests/test_file_samples_file.py
                :start-after: [START create_file]
                :end-before: [END create_file]
                :language: python
                :dedent: 12
                :caption: Create a file.
        """
        if self.require_encryption and not self.key_encryption_key:
            raise ValueError("Encryption required but no key was provided.")

        headers = kwargs.pop("headers", {})
        headers.update(add_metadata_headers(metadata))
        file_http_headers = None
        if content_settings:
            file_http_headers = FileHTTPHeaders(
                file_cache_control=content_settings.cache_control,
                file_content_type=content_settings.content_type,
                file_content_md5=bytearray(content_settings.content_md5) if content_settings.content_md5 else None,
                file_content_encoding=content_settings.content_encoding,
                file_content_language=content_settings.content_language,
                file_content_disposition=content_settings.content_disposition,
            )
        try:
            return await self._client.file.create(  # type: ignore
                file_content_length=size,
                timeout=timeout,
                metadata=metadata,
                file_http_headers=file_http_headers,
                headers=headers,
                cls=return_response_headers,
                **kwargs
            )
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace_async
    async def upload_file(
        self,
        data,  # type: Any
        length=None,  # type: Optional[int]
        metadata=None,  # type: Optional[Dict[str, str]]
        content_settings=None,  # type: Optional[ContentSettings]
        validate_content=False,  # type: bool
        max_connections=1,  # type: Optional[int]
        timeout=None,  # type: Optional[int]
        encoding="UTF-8",  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> Dict[str, Any]
        """Uploads a new file.

        :param Any data:
            Content of the file.
        :param int length:
            Length of the file in bytes. Specify its maximum size, up to 1 TiB.
        :param metadata:
            Name-value pairs associated with the file as metadata.
        :type metadata: dict(str, str)
        :param ~azure.storage.file.models.ContentSettings content_settings:
            ContentSettings object used to set file properties.
        :param bool validate_content:
            If true, calculates an MD5 hash for each range of the file. The storage
            service checks the hash of the content that has arrived with the hash
            that was sent. This is primarily valuable for detecting bitflips on
            the wire if using http instead of https as https (the default) will
            already validate. Note that this MD5 hash is not stored with the
            file.
        :param int max_connections:
            Maximum number of parallel connections to use.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :param str encoding:
            Defaults to UTF-8.
        :returns: File-updated property dict (Etag and last modified).
        :rtype: dict(str, Any)

        Example:
            .. literalinclude:: ../tests/test_file_samples_file.py
                :start-after: [START upload_file]
                :end-before: [END upload_file]
                :language: python
                :dedent: 12
                :caption: Upload a file.
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
        elif hasattr(data, "read"):
            stream = data
        elif hasattr(data, "__iter__"):
            stream = IterStreamer(data, encoding=encoding)  # type: ignore
        else:
            raise TypeError("Unsupported data type: {}".format(type(data)))
        return await _upload_file_helper(  # type: ignore
            self,
            stream,
            length,
            metadata,
            content_settings,
            validate_content,
            timeout,
            max_connections,
            self._config,
            **kwargs
        )

    @distributed_trace_async
    async def start_copy_from_url(
        self,
        source_url,  # type: str
        metadata=None,  # type: Optional[Dict[str, str]]
        timeout=None,  # type: Optional[int]
        **kwargs  # type: Any
    ):
        # type: (...) -> Any
        """Initiates the copying of data from a source URL into the file
        referenced by the client.

        The status of this copy operation can be found using the `get_properties`
        method.

        :param str source_url:
            Specifies the URL of the source file.
        :param metadata:
            Name-value pairs associated with the file as metadata.
        :type metadata: dict(str, str)
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: dict(str, Any)

        Example:
            .. literalinclude:: ../tests/test_file_samples_file.py
                :start-after: [START copy_file_from_url]
                :end-before: [END copy_file_from_url]
                :language: python
                :dedent: 12
                :caption: Copy a file from a URL
        """
        headers = kwargs.pop("headers", {})
        headers.update(add_metadata_headers(metadata))

        try:
            return await self._client.file.start_copy(
                source_url, timeout=timeout, metadata=metadata, headers=headers, cls=return_response_headers, **kwargs
            )
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace_async
    async def abort_copy(self, copy_id, timeout=None, **kwargs):
        # type: (Union[str, FileProperties], Optional[int], Any) -> Dict[str, Any]
        """Abort an ongoing copy operation.

        This will leave a destination file with zero length and full metadata.
        This will raise an error if the copy operation has already ended.

        :param copy_id:
            The copy operation to abort. This can be either an ID, or an
            instance of FileProperties.
        :type copy_id: str or ~azure.storage.file.models.FileProperties
        :rtype: None
        """
        try:
            copy_id = copy_id.copy.id
        except AttributeError:
            try:
                copy_id = copy_id["copy_id"]
            except TypeError:
                pass
        try:
            await self._client.file.abort_copy(copy_id=copy_id, timeout=timeout, **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace_async
    async def download_file(
        self,
        offset=None,  # type: Optional[int]
        length=None,  # type: Optional[int]
        validate_content=False,  # type: bool
        timeout=None,  # type: Optional[int]
        **kwargs
    ):
        # type: (...) -> Iterable[bytes]
        """Downloads a file to a stream with automatic chunking.

        :param int offset:
            Start of byte range to use for downloading a section of the file.
            Must be set if length is provided.
        :param int length:
            Number of bytes to read from the stream. This is optional, but
            should be supplied for optimal performance.
        :param bool validate_content:
            If true, calculates an MD5 hash for each chunk of the file. The storage
            service checks the hash of the content that has arrived with the hash
            that was sent. This is primarily valuable for detecting bitflips on
            the wire if using http instead of https as https (the default) will
            already validate. Note that this MD5 hash is not stored with the
            file. Also note that if enabled, the memory-efficient upload algorithm
            will not be used, because computing the MD5 hash requires buffering
            entire blocks, and doing so defeats the purpose of the memory-efficient algorithm.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: A iterable data generator (stream)

        Example:
            .. literalinclude:: ../tests/test_file_samples_file.py
                :start-after: [START download_file]
                :end-before: [END download_file]
                :language: python
                :dedent: 12
                :caption: Download a file.
        """
        if self.require_encryption or (self.key_encryption_key is not None):
            raise ValueError("Encryption not supported.")
        if length is not None and offset is None:
            raise ValueError("Offset value must not be None is length is set.")

        downloader = StorageStreamDownloader(
            service=self._client.file,
            config=self._config,
            offset=offset,
            length=length,
            validate_content=validate_content,
            encryption_options=None,
            cls=deserialize_file_stream,
            timeout=timeout,
            **kwargs
        )
        await downloader.setup(
            extra_properties={"share": self.share_name, "name": self.file_name, "path": "/".join(self.file_path)}
        )
        return downloader

    @distributed_trace_async
    async def delete_file(self, timeout=None, **kwargs):
        # type: (Optional[int], Optional[Any]) -> None
        """Marks the specified file for deletion. The file is
        later deleted during garbage collection.

        :param int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None

        Example:
            .. literalinclude:: ../tests/test_file_samples_file.py
                :start-after: [START delete_file]
                :end-before: [END delete_file]
                :language: python
                :dedent: 12
                :caption: Delete a file.
        """
        try:
            await self._client.file.delete(timeout=timeout, **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace_async
    async def get_file_properties(self, timeout=None, **kwargs):
        # type: (Optional[int], Any) -> FileProperties
        """Returns all user-defined metadata, standard HTTP properties, and
        system properties for the file.

        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: FileProperties
        :rtype: ~azure.storage.file.models.FileProperties
        """
        try:
            file_props = await self._client.file.get_properties(
                sharesnapshot=self.snapshot, timeout=timeout, cls=deserialize_file_properties, **kwargs
            )
        except StorageErrorException as error:
            process_storage_error(error)
        file_props.name = self.file_name
        file_props.share = self.share_name
        file_props.snapshot = self.snapshot
        file_props.path = "/".join(self.file_path)
        return file_props  # type: ignore

    @distributed_trace_async
    async def set_http_headers(self, content_settings, timeout=None, **kwargs):  # type: ignore
        # type: (ContentSettings, Optional[int], Optional[Any]) -> Dict[str, Any]
        """Sets HTTP headers on the file.

        :param ~azure.storage.file.models.ContentSettings content_settings:
            ContentSettings object used to set file properties.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: File-updated property dict (Etag and last modified).
        :rtype: dict(str, Any)
        """
        file_content_length = kwargs.pop("size", None)
        file_http_headers = FileHTTPHeaders(
            file_cache_control=content_settings.cache_control,
            file_content_type=content_settings.content_type,
            file_content_md5=bytearray(content_settings.content_md5) if content_settings.content_md5 else None,
            file_content_encoding=content_settings.content_encoding,
            file_content_language=content_settings.content_language,
            file_content_disposition=content_settings.content_disposition,
        )
        try:
            return await self._client.file.set_http_headers(  # type: ignore
                timeout=timeout,
                file_content_length=file_content_length,
                file_http_headers=file_http_headers,
                cls=return_response_headers,
                **kwargs
            )
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace_async
    async def set_file_metadata(self, metadata=None, timeout=None, **kwargs):  # type: ignore
        # type: (Optional[Dict[str, Any]], Optional[int], Optional[Any]) -> Dict[str, Any]
        """Sets user-defined metadata for the specified file as one or more
        name-value pairs.

        Each call to this operation replaces all existing metadata
        attached to the file. To remove all metadata from the file,
        call this operation with no metadata dict.

        :param metadata:
            Name-value pairs associated with the file as metadata.
        :type metadata: dict(str, str)
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: File-updated property dict (Etag and last modified).
        :rtype: dict(str, Any)
        """
        headers = kwargs.pop("headers", {})
        headers.update(add_metadata_headers(metadata))  # type: ignore
        try:
            return await self._client.file.set_metadata(  # type: ignore
                timeout=timeout, cls=return_response_headers, headers=headers, metadata=metadata, **kwargs
            )
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace_async
    async def upload_range(  # type: ignore
        self,
        data,  # type: bytes
        start_range,  # type: int
        end_range,  # type: int
        validate_content=False,  # type: Optional[bool]
        timeout=None,  # type: Optional[int]
        encoding="UTF-8",
        **kwargs
    ):
        # type: (...) -> Dict[str, Any]
        """Upload a range of bytes to a file.

        :param bytes data:
            The data to upload.
        :param int start_range:
            Start of byte range to use for uploading a section of the file.
            The range can be up to 4 MB in size.
            The start_range and end_range params are inclusive.
            Ex: start_range=0, end_range=511 will upload first 512 bytes of file.
        :param int end_range:
            End of byte range to use for uploading a section of the file.
            The range can be up to 4 MB in size.
            The start_range and end_range params are inclusive.
            Ex: start_range=0, end_range=511 will upload first 512 bytes of file.
        :param bool validate_content:
            If true, calculates an MD5 hash of the page content. The storage
            service checks the hash of the content that has arrived
            with the hash that was sent. This is primarily valuable for detecting
            bitflips on the wire if using http instead of https as https (the default)
            will already validate. Note that this MD5 hash is not stored with the
            file.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :param str encoding:
            Defaults to UTF-8.
        :returns: File-updated property dict (Etag and last modified).
        :rtype: Dict[str, Any]
        """
        if self.require_encryption or (self.key_encryption_key is not None):
            raise ValueError("Encryption not supported.")
        if isinstance(data, six.text_type):
            data = data.encode(encoding)

        content_range = "bytes={0}-{1}".format(start_range, end_range)
        content_length = end_range - start_range + 1
        try:
            return await self._client.file.upload_range(  # type: ignore
                range=content_range,
                content_length=content_length,
                optionalbody=data,
                timeout=timeout,
                validate_content=validate_content,
                cls=return_response_headers,
                **kwargs
            )
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace_async
    async def get_ranges(  # type: ignore
        self,
        start_range=None,  # type: Optional[int]
        end_range=None,  # type: Optional[int]
        timeout=None,  # type: Optional[int]
        **kwargs
    ):
        # type: (...) -> List[dict[str, int]]
        """Returns the list of valid ranges of a file.

        :param int start_range:
            Specifies the start offset of bytes over which to get ranges.
            The start_range and end_range params are inclusive.
            Ex: start_range=0, end_range=511 will download first 512 bytes of file.
        :param int end_range:
            Specifies the end offset of bytes over which to get ranges.
            The start_range and end_range params are inclusive.
            Ex: start_range=0, end_range=511 will download first 512 bytes of file.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: A list of valid ranges.
        :rtype: List[dict[str, int]]
        """
        if self.require_encryption or (self.key_encryption_key is not None):
            raise ValueError("Unsupported method for encryption.")

        content_range = None
        if start_range is not None:
            if end_range is not None:
                content_range = "bytes={0}-{1}".format(start_range, end_range)
            else:
                content_range = "bytes={0}-".format(start_range)
        try:
            ranges = await self._client.file.get_range_list(
                sharesnapshot=self.snapshot, timeout=timeout, range=content_range, **kwargs
            )
        except StorageErrorException as error:
            process_storage_error(error)
        return [{"start": b.start, "end": b.end} for b in ranges]

    @distributed_trace_async
    async def clear_range(  # type: ignore
        self,
        start_range,  # type: int
        end_range,  # type: int
        timeout=None,  # type: Optional[int]
        **kwargs
    ):
        # type: (...) -> Dict[str, Any]
        """Clears the specified range and releases the space used in storage for
        that range.

        :param int start_range:
            Start of byte range to use for clearing a section of the file.
            The range can be up to 4 MB in size.
            The start_range and end_range params are inclusive.
            Ex: start_range=0, end_range=511 will download first 512 bytes of file.
        :param int end_range:
            End of byte range to use for clearing a section of the file.
            The range can be up to 4 MB in size.
            The start_range and end_range params are inclusive.
            Ex: start_range=0, end_range=511 will download first 512 bytes of file.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: File-updated property dict (Etag and last modified).
        :rtype: Dict[str, Any]
        """
        if self.require_encryption or (self.key_encryption_key is not None):
            raise ValueError("Unsupported method for encryption.")

        if start_range is None or start_range % 512 != 0:
            raise ValueError("start_range must be an integer that aligns with 512 file size")
        if end_range is None or end_range % 512 != 511:
            raise ValueError("end_range must be an integer that aligns with 512 file size")
        content_range = "bytes={0}-{1}".format(start_range, end_range)
        try:
            return await self._client.file.upload_range(  # type: ignore
                timeout=timeout,
                cls=return_response_headers,
                content_length=0,
                file_range_write="clear",
                range=content_range,
                **kwargs
            )
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace_async
    async def resize_file(self, size, timeout=None, **kwargs):  # type: ignore
        # type: (int, Optional[int], Optional[Any]) -> Dict[str, Any]
        """Resizes a file to the specified size.

        :param int size:
            Size to resize file to (in bytes)
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: File-updated property dict (Etag and last modified).
        :rtype: Dict[str, Any]
        """
        try:
            return await self._client.file.set_http_headers(  # type: ignore
                timeout=timeout, file_content_length=size, cls=return_response_headers, **kwargs
            )
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace
    def list_handles(self, timeout=None, **kwargs) -> AsyncItemPaged:
        """Lists handles for file.

        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: An auto-paging iterable of HandleItems
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.storage.file.models.Handle]
        """
        results_per_page = kwargs.pop("results_per_page", None)
        command = functools.partial(
            self._client.file.list_handles,
            sharesnapshot=self.snapshot,
            timeout=timeout,
            **kwargs)
        return AsyncItemPaged(
            command, results_per_page=results_per_page,
            page_iterator_class=HandlesPaged)

    @distributed_trace_async
    async def close_handles(
        self,
        handle=None,  # type: Union[str, HandleItem]
        timeout=None,  # type: Optional[int]
        **kwargs  # type: Any
    ):
        # type: (...) -> Any
        """Close open file handles.

        This operation may not finish with a single call, so a long-running poller
        is returned that can be used to wait until the operation is complete.

        :param handle:
            Optionally, a specific handle to close. The default value is '*'
            which will attempt to close all open handles.
        :type handle: str or ~azure.storage.file.models.Handle
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: A long-running poller to get operation status.
        :rtype: ~azure.core.polling.LROPoller
        """
        try:
            handle_id = handle.id  # type: ignore
        except AttributeError:
            handle_id = handle or "*"
        command = functools.partial(
            self._client.file.force_close_handles,
            handle_id,
            timeout=timeout,
            sharesnapshot=self.snapshot,
            cls=return_response_headers,
            **kwargs
        )
        try:
            start_close = await command()
        except StorageErrorException as error:
            process_storage_error(error)

        polling_method = CloseHandlesAsync(self._config.copy_polling_interval)
        return async_poller(command, start_close, None, polling_method)
