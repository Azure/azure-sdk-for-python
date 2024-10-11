# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from base64 import b64encode
import functools
from io import BytesIO
import json
from datetime import datetime, timedelta
from time import time
import uuid
from wsgiref.handlers import format_date_time
from urllib.parse import urlparse, quote
from typing import IO, Any, Dict, Generator, Generic, Iterable, Mapping, Optional, Protocol, Self, Tuple, Type, TypeVar, Union, overload, Literal
from threading import Thread
from concurrent.futures import Executor, Future

from azure.core.exceptions import HttpResponseError
from azure.core.pipeline.transport import HttpTransport, PipelineRequest
from azure.core.rest import HttpRequest, HttpResponse
from azure.core import PipelineClient, MatchCondition
from azure.core.utils import case_insensitive_dict
from azure.core.pipeline.policies import HeadersPolicy


from ._eventlistener import cloudmachine_events
from ._base import CloudMachineClientlet
from ._utils import (
    Stream,
    PartialStream,
    serialize_rfc,
    deserialize_rfc,
    prep_if_match,
    prep_if_none_match,
    parse_content_range,
    get_length,
    serialize_tags_header,
)

FILE_UPLOADED = cloudmachine_events.signal('Microsoft.Storage.BlobCreated')
FILE_DELETED = cloudmachine_events.signal('Microsoft.Storage.BlobDeleted')
FILE_RENAMED = cloudmachine_events.signal('Microsoft.Storage.BlobRenamed')

_ERROR_CODE = "x-ms-error-code"
_METADATA = "x-ms-meta-"
_DEFAULT_CHUNK_SIZE = 32 * 1024 * 1024
_DEFAULT_BLOCK_SIZE = 256 * 1024 * 1024


def _format_url(endpoint: str, container: str) -> str:
    parsed_url = urlparse(endpoint)
    return f"{parsed_url.scheme}://{parsed_url.hostname}/{quote(container)}{parsed_url.query}"


class StorageHeadersPolicy(HeadersPolicy):
    def on_request(self, request: PipelineRequest) -> None:
        super(StorageHeadersPolicy, self).on_request(request)
        current_time = format_date_time(time())
        request.http_request.headers['x-ms-date'] = current_time


T = TypeVar("T")

class StorageFile(Generic[T]):
    last_modified: datetime
    metadata: Dict[str, str]
    tags: int
    length: int
    etag: str
    content: T
    filename: str
    headers: Mapping[str, Any]

    def __init__(
            self,
            *,
            filename: str,
            headers: Dict[str, str],
            length: int,
            metadata: Optional[Dict[str, str]],
            tags: Optional[int],
            content: T
    ) -> None:
        self.content = content
        self.length = length
        self.last_modified = deserialize_rfc(headers['Last-Modified'])
        self.etag = headers['ETag']
        self.filename = filename
        self.metadata = metadata or {k[len(_METADATA):]: v for k, v in headers.items() if k.startswith(_METADATA)}
        self.tags = tags if tags is not None else headers.get('x-ms-tag-count', 0)
        self.headers = headers


class CloudMachineStorage(CloudMachineClientlet):
    _id: Literal['Blob'] = 'Blob'
    default_container_name: str = "default"
    
    def __init__(
            self,
            *,
            transport: Optional[HttpTransport] = None,
            name: Optional[str] = None,
            executor: Optional[Executor] = None,
            **kwargs
    ):
        headers_policy = StorageHeadersPolicy(**kwargs)
        super().__init__(
            transport=transport,
            name=name,
            executor=executor,
            headers_policy=headers_policy,
            **kwargs
        )
        self._containers: Dict[str, PipelineClient] = {}

    def _get_container_client(self, container: Optional[str]) -> PipelineClient:
        container = container or self.default_container_name
        try:
            return self._containers[container]
        except KeyError:
            container_endpoint = _format_url(self._endpoint, container)
            container_client = PipelineClient(
                base_url=container_endpoint,
                pipeline=self._config.pipeline
            )
            container_client.endpoint = container_endpoint
            self._containers[container] = container_client
            return container_client

    def get_client(self, **kwargs) -> 'azure.storage.blob.BlobServiceClient':
        try:
            from azure.storage.blob import BlobServiceClient
        except ImportError as e:
            raise ImportError("Please install azure-storage-blob SDK to use SDK client.") from e
        return BlobServiceClient(
            fully_qualified_namespace=self._endpoint,
            credential=self._credential,
            api_version=self._config.api_version,
            transport=self._config.transport,
            **kwargs
        )

    # def list(
    #         self,
    #         *,
    #         prefix: Optional[str] = None,
    #         container: Optional[str] = None
    # ) -> Generator[str, None, None]:
    #     client = self._get_container_client(container)
    #     for blob in client.list_blobs(name_starts_with=prefix):
    #         yield blob.name

    # TODO: Delete should use a batch request and support multiple files
    @overload
    def delete(
            self,
            file: StorageFile,
            *,
            container: Optional[str] = None,
            condition: MatchCondition = MatchCondition.IfPresent,
            **kwargs
    ) -> None:
        ...
    @overload
    def delete(
            self,
            file: str,
            *,
            container: Optional[str] = None,
            condition: MatchCondition = MatchCondition.IfPresent,
            etag: Optional[str] = None,
            **kwargs
    ) -> None:
        ...
    def delete(self, file: Union[StorageFile, str], *, container: Optional[str] = None, **kwargs) -> None:
        client = self._get_container_client(container)
        kwargs['version'] = self._config.api_version
        condition = kwargs.pop('condition', MatchCondition.IfPresent)
        try:
            kwargs['if_match'] = prep_if_match(file.etag, condition)
            kwargs['if_none_match'] = prep_if_none_match(file.etag, condition)
            request = build_delete_container_request(
                container.endpoint,
                file.filename,
                kwargs
            )
        except AttributeError:
            etag = kwargs.pop('etag', None)
            kwargs['if_match'] = prep_if_match(etag, condition)
            kwargs['if_none_match'] = prep_if_none_match(etag, condition)
            request = build_delete_container_request(
                container.endpoint,
                file,
                kwargs
            )
        response = client.send_request(request, **kwargs)
        if ((response.status_code == 202) or
            (response.status_code == 404 and response.headers.get(_ERROR_CODE) == 'BlobNotFound') or
            (response.status_code == 404 and response.headers.get(_ERROR_CODE) == 'ContainerNotFound') or
            (response.status_code == 409 and response.headers.get(_ERROR_CODE) == 'ContainerBeingDeleted')):
            self._containers.pop(container, None)
            return
        raise HttpResponseError(response=response)

    def _upload(
            self,
            data: IO[bytes],
            *,
            content_length: Optional[int] = None,
            filename: Optional[str] = None,
            container: Optional[str] = None,
            condition: MatchCondition = MatchCondition.IfMissing,
            metadata: Optional[Dict[str, str]],
            etag: Optional[str] = None,
            tags: Optional[Dict[str, str]] = None,
            **kwargs
    ) -> StorageFile[None]:
        # TODO: support upload by block list + commit
        # TODO: support content validation
        client = self._get_container_client(container)
        filename = filename or str(uuid.uuid4())
        content_length=content_length or get_length(data)
        kwargs['version'] = self._config.api_version
        kwargs['if_match'] = prep_if_match(etag, condition)
        kwargs['if_none_match'] = prep_if_none_match(etag, condition)
        kwargs['blob_content_type'] = kwargs.pop('content_type', None)
        kwargs['blob_content_encoding'] = kwargs.pop('content_encoding', None)
        kwargs['blob_content_language'] = kwargs.pop('content_language', None)
        kwargs['blob_content_disposition'] = kwargs.pop('content_disposition', None)
        kwargs['blob_tags_string'] = serialize_tags_header(tags)
        expiry = kwargs.pop('expiry', None)
        if isinstance(expiry, timedelta):
            kwargs['expiry_relative'] = int(expiry.microseconds/1000)
        elif expiry:
            kwargs['expiry_absolute'] = expiry
        request = build_upload_blob_request(
            client.endpoint + f"/{quote(filename)}",
            content_length=content_length,
            content=data if hasattr(data, 'read') else BytesIO(data),
            kwargs=kwargs
        )
        response = client.send_request(request, **kwargs)
        if response.status_code == 404 and response.headers.get(_ERROR_CODE) == 'ContainerNotFound':
            self._create_container(container, **kwargs)
            # TODO: Retry the request once we've created the container
            # Need to confirm whether we need to rewind the payload.
            response = client.send_request(request, **kwargs)
        if response.status_code not in [201]:
            raise HttpResponseError(response=response)
        return StorageFile(
            filename=filename,
            length=content_length,
            headers=response.headers,
            metadata=metadata,
            tags=len(tags),
            content=None,
        )
    @overload
    def upload(
            self,
            data: Union[bytes, IO[bytes]],
            *,
            content_length: Optional[int] = None,
            content_type: Optional[str] = None,
            content_encoding: Optional[str] = None,
            content_language: Optional[str] = None,
            content_disposition: Optional[str] = None,
            filename: Optional[str] = None,
            container: Optional[str] = None,
            condition: MatchCondition = MatchCondition.IfMissing,
            etag: Optional[str] = None,
            metadata: Optional[Dict[str, str]] = None,
            tags: Optional[Dict[str, str]] = None,
            expiry: Optional[Union[datetime, timedelta]] = None,
            wait: Literal[True] = True,
            **kwargs
    ) -> StorageFile[None]:
        ...
    @overload
    def upload(
            self,
            data: Union[bytes, IO[bytes]],
            *,
            content_length: Optional[int] = None,
            content_type: Optional[str] = None,
            content_encoding: Optional[str] = None,
            content_language: Optional[str] = None,
            content_disposition: Optional[str] = None,
            filename: Optional[str] = None,
            container: Optional[str] = None,
            condition: MatchCondition = MatchCondition.IfMissing,
            etag: Optional[str] = None,
            metadata: Optional[Dict[str, str]] = None,
            tags: Optional[Dict[str, str]] = None,
            expiry: Optional[Union[datetime, timedelta]] = None,
            wait: Literal[False],
            **kwargs
    ) -> Future[StorageFile[None]]:
        ...
    def upload(
            self,
            data: Union[bytes, IO[bytes]],
            *,
            content_length: Optional[int] = None,
            filename: Optional[str] = None,
            container: Optional[str] = None,
            condition: MatchCondition = MatchCondition.IfMissing,
            etag: Optional[str] = None,
            metadata: Optional[Dict[str, str]] = None,
            tags: Optional[Dict[str, str]] = None,
            wait: bool = True,
            **kwargs
    ) -> Union[Future[StorageFile[None]], StorageFile[None]]:
        if wait:
            return self._upload(
                data,
                content_length=content_length,
                filename=filename,
                container=container,
                condition=condition,
                metadata=metadata,
                tags=tags,
                etag=etag,
                **kwargs
            )
        return self._executor.submit(
            self._upload,
            data,
            content_length=content_length,
            filename=filename,
            container=container,
            condition=condition,
            metadata=metadata,
            tags=tags,
            etag=etag,
            **kwargs
        )
        
    def _download(
            self,
            filename: str,
            *,
            range: Optional[Tuple[int, Optional[int]]] = None,
            container: Optional[str] = None,
            condition: MatchCondition = MatchCondition.IfPresent,
            etag: Optional[str] = None,
            validate: bool = False,
            **kwargs
    ) -> StorageFile[Stream]:
        client = self._get_container_client(container)
        chunk_size = kwargs.pop('chunk_size', None)
        if chunk_size and validate and chunk_size > 4 * 1024 * 1024:
            raise ValueError("Validation only possible with max chunk size of 4mb.")
        elif not chunk_size:
            chunk_size = _DEFAULT_CHUNK_SIZE if not validate else 4 * 1024 * 1024

        def _download(request: HttpRequest, **kwargs) -> Tuple[HttpResponse, int, int, int]:
            response = client.send_request(request, stream=True, **kwargs)
            if response.status_code not in [200, 206]:
                raise HttpResponseError(response=response)
            response_start, response_end, filelength = parse_content_range(
                response.headers['Content-Range']
            )
            return response, response_start, response_end, filelength

        kwargs['version'] = self._config.api_version
        kwargs['if_match'] = prep_if_match(etag, condition)
        kwargs['if_none_match'] = prep_if_none_match(etag, condition)
        if validate:
            kwargs['range_get_content_crc64'] = True

        request_builder = functools.partial(
            build_download_blob_request,
            container.endpoint,
            filename,
            kwargs
        )
        request_start = 0 if range is None else range[0]
        request_end = chunk_size if range is None or range[1] is None or range[1] > chunk_size else range[1]
        range_header = f'bytes={request_start}-{request_end}'
        request = request_builder(range_header)
        response, response_start, response_end, filelength = _download(request, **kwargs)
        first_chunk = PartialStream(
            start=response_start,
            end=response_end,
            response=response
        )
        downloaded = response_end - response_start
        if range:
            if range[1]:
                expected_length = range[1] - range[0]
            else:
                expected_length = filelength - range[0]
        else:
            expected_length = filelength
        if downloaded < expected_length:
            download_end = filelength if range is None or range[1] is None else range[1]
            chunk_iter = range(response_end + 1, download_end, chunk_size)
            request_gen = (request_builder(f'bytes={r}-{r + chunk_size}') for r in chunk_iter)
            response_gen = (_download(r, **kwargs) for r in request_gen)
            stream = Stream(
                content_length=expected_length,
                content_range=f'bytes {request_start}-{download_end}/{filelength}',
                first_chunk=stream,
                next_chunks=response_gen
            )
        else:
            stream = Stream(
                content_length=downloaded,
                content_range=f'bytes {response_start}-{response_end}/{filelength}',
                first_chunk=first_chunk
            )
        return StorageFile(
            filename=filename,
            length=filelength,
            headers=response.headers,
            content=stream
        )
    @overload
    def download(
            self,
            filename: str,
            *,
            range: Optional[Tuple[int, Optional[int]]] = None,
            container: Optional[str] = None,
            condition: MatchCondition = MatchCondition.IfPresent,
            etag: Optional[str] = None,
            validate: bool = False,
            chunk_size: int = _DEFAULT_CHUNK_SIZE,
            wait: Literal[True] = True,
            **kwargs
    ) -> StorageFile[Stream]:
        ...
    @overload
    def download(
            self,
            filename: str,
            *,
            range: Optional[Tuple[int, Optional[int]]] = None,
            container: Optional[str] = None,
            condition: MatchCondition = MatchCondition.IfPresent,
            etag: Optional[str] = None,
            validate: bool = False,
            chunk_size: int = _DEFAULT_CHUNK_SIZE,
            wait: Literal[False],
            **kwargs
    ) -> Future[StorageFile[Stream]]:
        ...
    def download(
            self,
            filename: str,
            *,
            range: Optional[Tuple[int, Optional[int]]] = None,
            container: Optional[str] = None,
            condition: MatchCondition = MatchCondition.IfPresent,
            etag: Optional[str] = None,
            validate: bool = False,
            wait: bool = True,
            **kwargs
    ) -> Union[StorageFile[Stream], Future[StorageFile[Stream]]]:
        if wait:
            return self._download(
                filename=filename,
                range=range,
                container=container,
                condition=condition,
                etag=etag,
                validate=validate,
                **kwargs
            )
        return self._executor.submit(
            self._download,
            filename=filename,
            range=range,
            container=container,
            condition=condition,
            etag=etag,
            validate=validate,
            **kwargs
        )

    def _create_container(self, name: str, **kwargs) -> None:
        container = self._get_container_client(name)
        kwargs['version'] = self._config.api_version
        request = build_create_container_request(
            container.endpoint,
            kwargs
        )
        response = self._client.send_request(request, **kwargs)
        if ((response.status_code == 201) or
            (response.status_code == 409 and response.headers.get(_ERROR_CODE) == 'ContainerAlreadyExists')):
            return
        self._containers.pop(name)
        raise HttpResponseError(response=response)
    
    def _delete_container(self, name: str, **kwargs) -> None:
        if name.lower() == self.default_container_name.lower():
            raise ValueError("Default container cannot be deleted.")
        container = self._get_container_client(name)
        kwargs['version'] = self._config.api_version
        request = build_delete_container_request(
            container.endpoint,
            kwargs
        )
        response = self._client.send_request(request, **kwargs)
        if ((response.status_code == 202) or
            (response.status_code == 404 and response.headers.get(_ERROR_CODE) == 'ContainerNotFound') or
            (response.status_code == 409 and response.headers.get(_ERROR_CODE) == 'ContainerBeingDeleted')):
            self._containers.pop(container, None)
            return
        raise HttpResponseError(response=response)


########## Request Builders ##########

def build_create_container_request(
    url: str,
    kwargs: Dict[str, Any]
) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
    _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

    timeout: Optional[int] = kwargs.pop('servicetimeout', None)
    metadata: Optional[Dict[str, str]] = kwargs.pop('metadata', None)
    access: Optional[str] = kwargs.pop('access', None)
    default_encryption_scope: Optional[str] = kwargs.pop('default_encryption_scope', None)
    prevent_encryption_scope_override: Optional[bool] = kwargs.pop('prevent_encryption_scope_override', None)
    restype: Literal["container"] = kwargs.pop("restype", _params.pop("restype", "container"))
    version: str = kwargs.pop("version", _headers.pop("x-ms-version", "2025-01-05"))
    accept = _headers.pop("Accept", "application/xml")

    # Construct URL
    _url = kwargs.pop("template_url", "{url}")
    path_format_arguments = {
        "url": url,
    }
    _url: str = _url.format(**path_format_arguments)  # type: ignore

    # Construct parameters
    _params["restype"] = quote(restype)
    if timeout is not None:
        _params["timeout"] = quote(str(timeout))

    # Construct headers
    if metadata is not None:
        for key, value in metadata.items():
            _headers[f'x-ms-meta-{key.strip()}'] = value.strip() if value else value
    if access is not None:
        _headers["x-ms-blob-public-access"] = access
    _headers["x-ms-version"] = version

    if default_encryption_scope is not None:
        _headers["x-ms-default-encryption-scope"] = default_encryption_scope
    if prevent_encryption_scope_override is not None:
        _headers["x-ms-deny-encryption-scope-override"] = json.dumps(prevent_encryption_scope_override)
    _headers["Accept"] = accept

    return HttpRequest(method="PUT", url=_url, params=_params, headers=_headers, **kwargs)


def build_delete_container_request(
    url: str,
    kwargs: Dict[str, Any]
) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
    _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

    timeout: Optional[int] = kwargs.pop("servicetimeout", None)
    lease_id: Optional[str] = kwargs.pop("lease_id", None)
    if_modified_since: Optional[datetime] = kwargs.pop("if_modified_since", None)
    if_unmodified_since: Optional[datetime] = kwargs.pop("if_unmodified_since", None)
    restype: Literal["container"] = kwargs.pop("restype", _params.pop("restype", "container"))
    version: str = kwargs.pop("version", _headers.pop("x-ms-version", "2025-01-05"))
    accept = _headers.pop("Accept", "application/xml")

    # Construct URL
    _url = kwargs.pop("template_url", "{url}")
    path_format_arguments = {
        "url": url,
    }
    _url: str = _url.format(**path_format_arguments)  # type: ignore

    # Construct parameters
    _params["restype"] = quote(restype)
    if timeout is not None:
        _params["timeout"] = quote(str(timeout))

    # Construct headers
    if lease_id is not None:
        _headers["x-ms-lease-id"] = lease_id
    if if_modified_since is not None:
        _headers["If-Modified-Since"] = serialize_rfc(if_modified_since)
    if if_unmodified_since is not None:
        _headers["If-Unmodified-Since"] = serialize_rfc(if_unmodified_since)
    _headers["x-ms-version"] = version
    _headers["Accept"] = accept

    return HttpRequest(method="DELETE", url=_url, params=_params, headers=_headers, **kwargs)


def build_delete_blob_request(
    url: str,
    blob: str,
    kwargs: Dict[str, Any]
) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
    _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

    snapshot: Optional[str] = kwargs.pop("snapshot", None)
    version_id: Optional[str] = kwargs.pop("version_id", None)
    timeout: Optional[int] = kwargs.pop("servicetimeout", None)
    lease_id: Optional[str] = kwargs.pop("lease_id", None)
    delete_snapshots: Optional[str] = kwargs.pop("delete_snapshots", None)
    if_modified_since: Optional[datetime] = kwargs.pop("if_modified_since", None)
    if_unmodified_since: Optional[datetime] = kwargs.pop("if_unmodified_since", None)
    if_match: Optional[str] = kwargs.pop("if_match", None)
    if_none_match: Optional[str] = kwargs.pop("if_none_match", None)
    if_tags: Optional[str] = kwargs.pop("if_tags", None)
    blob_delete_type: Literal["Permanent"] = "Permanent"
    version: str = kwargs.pop("version", _headers.pop("x-ms-version", "2025-01-05"))
    accept = _headers.pop("Accept", "application/xml")

    # Construct URL
    _url = kwargs.pop("template_url", "{url}/{blob}")
    path_format_arguments = {
        "url": url,
        "blob": quote(blob),
    }
    _url: str = _url.format(**path_format_arguments)  # type: ignore

    # Construct parameters
    if snapshot is not None:
        _params["snapshot"] = quote(snapshot)
    if version_id is not None:
        _params["versionid"] = quote(version_id)
    if timeout is not None:
        _params["timeout"] = quote(str(timeout))
    if blob_delete_type is not None:
        _params["deletetype"] = quote(blob_delete_type)

    # Construct headers
    if lease_id is not None:
        _headers["x-ms-lease-id"] = lease_id
    if delete_snapshots is not None:
        _headers["x-ms-delete-snapshots"] = delete_snapshots
    if if_modified_since is not None:
        _headers["If-Modified-Since"] = serialize_rfc(if_modified_since)
    if if_unmodified_since is not None:
        _headers["If-Unmodified-Since"] = serialize_rfc(if_unmodified_since)
    if if_match is not None:
        _headers["If-Match"] = if_match
    if if_none_match is not None:
        _headers["If-None-Match"] = if_none_match
    if if_tags is not None:
        _headers["x-ms-if-tags"] = if_tags
    _headers["x-ms-version"] = version
    _headers["Accept"] = accept

    return HttpRequest(method="DELETE", url=_url, params=_params, headers=_headers, **kwargs)


def build_download_blob_request(
    url: str,
    blob: str,
    kwargs: Dict[str, Any],
    range: str,
) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
    _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

    snapshot: Optional[str] = kwargs.pop("snapshot", None)
    version_id: Optional[str] = kwargs.pop("version_id", None)
    timeout: Optional[int] = kwargs.pop("servicetimeout", None)
    range: Optional[str] = range
    lease_id: Optional[str] = kwargs.pop("lease_id", None)
    range_get_content_md5: Optional[bool] = kwargs.pop("range_get_content_md5", None)
    range_get_content_crc64: Optional[bool] = kwargs.pop("range_get_content_crc64", None)
    structured_body_type: Optional[str] = kwargs.pop("structured_body_type", None)
    encryption_key: Optional[str] = kwargs.pop("encryption_key", None)
    encryption_key_sha256: Optional[str] = kwargs.pop("encryption_key_sha256", None)
    encryption_algorithm: Optional[str] = kwargs.pop("encryption_algorithm", None)
    if_modified_since: Optional[datetime] = kwargs.pop("if_modified_since", None)
    if_unmodified_since: Optional[datetime] = kwargs.pop("if_unmodified_since", None)
    if_match: Optional[str] = kwargs.pop("if_match", None)
    if_none_match: Optional[str] = kwargs.pop("if_none_match", None)
    if_tags: Optional[str] = kwargs.pop("if_tags", None)
    version: str = kwargs.pop("version", _headers.pop("x-ms-version", "2025-01-05"))
    accept = _headers.pop("Accept", "application/xml")

    # Construct URL
    _url = kwargs.pop("template_url", "{url}")
    path_format_arguments = {
        "url": url,
        "blob": quote(blob),
    }
    _url: str = _url.format(**path_format_arguments)  # type: ignore

    # Construct parameters
    if snapshot is not None:
        _params["snapshot"] = quote(snapshot)
    if version_id is not None:
        _params["versionid"] = quote(version_id)
    if timeout is not None:
        _params["timeout"] = quote(str(timeout))

    # Construct headers
    if range is not None:
        _headers["x-ms-range"] = range
    if lease_id is not None:
        _headers["x-ms-lease-id"] = lease_id
    if range_get_content_md5 is not None:
        _headers["x-ms-range-get-content-md5"] = json.dumps(range_get_content_md5)
    if range_get_content_crc64 is not None:
        _headers["x-ms-range-get-content-crc64"] = json.dumps(range_get_content_crc64)
    if structured_body_type is not None:
        _headers["x-ms-structured-body"] = structured_body_type
    if encryption_key is not None:
        _headers["x-ms-encryption-key"] = encryption_key
    if encryption_key_sha256 is not None:
        _headers["x-ms-encryption-key-sha256"] = encryption_key_sha256
    if encryption_algorithm is not None:
        _headers["x-ms-encryption-algorithm"] = encryption_algorithm
    if if_modified_since is not None:
        _headers["If-Modified-Since"] = serialize_rfc(if_modified_since)
    if if_unmodified_since is not None:
        _headers["If-Unmodified-Since"] = serialize_rfc(if_unmodified_since)
    if if_match is not None:
        _headers["If-Match"] = if_match
    if if_none_match is not None:
        _headers["If-None-Match"] = if_none_match
    if if_tags is not None:
        _headers["x-ms-if-tags"] = if_tags
    _headers["x-ms-version"] = version
    _headers["Accept"] = accept

    return HttpRequest(method="GET", url=_url, params=_params, headers=_headers, **kwargs)


def build_upload_blob_request(
    url: str,
    content_length: int,
    content: IO[bytes],
    kwargs: Any
) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
    _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

    timeout: Optional[int] = kwargs.pop("servicetimeout", None)
    transactional_content_md5: Optional[bytes] = kwargs.pop("transactional_content_md5", None)
    blob_content_type: Optional[str] = kwargs.pop("blob_content_type", None)
    blob_content_encoding: Optional[str] = kwargs.pop("blob_content_encoding", None)
    blob_content_language: Optional[str] = kwargs.pop("blob_content_language", None)
    blob_content_md5: Optional[bytes] = kwargs.pop("blob_content_md5", None)
    blob_cache_control: Optional[str] = kwargs.pop("blob_cache_control", None)
    metadata: Optional[Dict[str, str]] = kwargs.pop("metadata", None)
    lease_id: Optional[str] = kwargs.pop("lease_id", None)
    blob_content_disposition: Optional[str] = kwargs.pop("blob_content_disposition", None)
    encryption_key: Optional[str] = kwargs.pop("encryption_key", None)
    encryption_key_sha256: Optional[str] = kwargs.pop("encryption_key_sha256", None)
    encryption_algorithm: Optional[str] = kwargs.pop("encryption_algorithm", None)
    encryption_scope: Optional[str] = kwargs.pop("encryption_scope", None)
    tier: Optional[str] = kwargs.pop("tier", None)
    if_modified_since: Optional[datetime] = kwargs.pop("if_modified_since", None)
    if_unmodified_since: Optional[datetime] = kwargs.pop("if_unmodified_since", None)
    if_match: Optional[str] = kwargs.pop("if_match", None)
    if_none_match: Optional[str] = kwargs.pop("if_none_match", None)
    if_tags: Optional[str] = kwargs.pop("if_tags", None)
    blob_tags_string: Optional[str] = kwargs.pop("blob_tags_string", None)
    immutability_policy_expiry: Optional[datetime] = kwargs.pop("immutability_policy_expiry", None)
    immutability_policy_mode: Optional[str] = kwargs.pop("immutability_policy_mode", None)
    legal_hold: Optional[bool] = kwargs.pop("legal_hold", None)
    transactional_content_crc64: Optional[bytes] = kwargs.pop("transactional_content_crc64", None)
    structured_body_type: Optional[str] = kwargs.pop("structured_body_type", None)
    structured_content_length: Optional[int] = kwargs.pop("structured_content_length", None)
    expiry_relative: Optional[int] = kwargs.pop("expiry_relative", None)
    expiry_absolute: Optional[datetime] = kwargs.pop("expiry_absolute", None)
    blob_type: Literal["BlockBlob"] = kwargs.pop("blob_type", _headers.pop("x-ms-blob-type", "BlockBlob"))
    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    version: Literal["2025-01-05"] = kwargs.pop("version", _headers.pop("x-ms-version", "2025-01-05"))
    accept = _headers.pop("Accept", "application/xml")

    # Construct URL
    _url = kwargs.pop("template_url", "{url}")
    path_format_arguments = {
        "url": url,
    }

    _url: str = _url.format(**path_format_arguments)  # type: ignore

    # Construct parameters
    if timeout is not None:
        _params["timeout"] = quote(timeout)

    # Construct headers
    _headers["x-ms-blob-type"] = blob_type
    if transactional_content_md5 is not None:
        _headers["Content-MD5"] = b64encode(transactional_content_md5).decode()
    _headers["Content-Length"] = str(content_length)
    if blob_content_type is not None:
        _headers["x-ms-blob-content-type"] = blob_content_type
    if blob_content_encoding is not None:
        _headers["x-ms-blob-content-encoding"] = blob_content_encoding
    if blob_content_language is not None:
        _headers["x-ms-blob-content-language"] = blob_content_language
    if blob_content_md5 is not None:
        _headers["x-ms-blob-content-md5"] = b64encode(blob_content_md5).decode()
    if blob_cache_control is not None:
        _headers["x-ms-blob-cache-control"] = blob_cache_control
    if metadata is not None:
        for key, value in metadata.items():
            _headers[f'x-ms-meta-{key.strip()}'] = value.strip() if value else value
    if lease_id is not None:
        _headers["x-ms-lease-id"] = lease_id
    if blob_content_disposition is not None:
        _headers["x-ms-blob-content-disposition"] = blob_content_disposition
    if encryption_key is not None:
        _headers["x-ms-encryption-key"] = encryption_key
    if encryption_key_sha256 is not None:
        _headers["x-ms-encryption-key-sha256"] = encryption_key_sha256
    if encryption_algorithm is not None:
        _headers["x-ms-encryption-algorithm"] = encryption_algorithm
    if encryption_scope is not None:
        _headers["x-ms-encryption-scope"] = encryption_scope
    if tier is not None:
        _headers["x-ms-access-tier"] = tier
    if if_modified_since is not None:
        _headers["If-Modified-Since"] = serialize_rfc(if_modified_since)
    if if_unmodified_since is not None:
        _headers["If-Unmodified-Since"] = serialize_rfc(if_unmodified_since)
    if if_match is not None:
        _headers["If-Match"] = if_match
    if if_none_match is not None:
        _headers["If-None-Match"] = if_none_match
    if if_tags is not None:
        _headers["x-ms-if-tags"] = if_tags
    _headers["x-ms-version"] = version
    if blob_tags_string is not None:
        _headers["x-ms-tags"] = blob_tags_string
    if immutability_policy_expiry is not None:
        _headers["x-ms-immutability-policy-until-date"] = serialize_rfc(immutability_policy_expiry)
    if immutability_policy_mode is not None:
        _headers["x-ms-immutability-policy-mode"] = immutability_policy_mode
    if legal_hold is not None:
        _headers["x-ms-legal-hold"] = json.dumps(legal_hold)
    if transactional_content_crc64 is not None:
        _headers["x-ms-content-crc64"] = b64encode(transactional_content_crc64).decode()
    if structured_body_type is not None:
        _headers["x-ms-structured-body"] = structured_body_type
    if structured_content_length is not None:
        _headers["x-ms-structured-content-length"] = str(structured_content_length)
    if content_type is not None:
        _headers["Content-Type"] = quote(content_type)
    _headers["Accept"] = quote(accept)
    if expiry_relative is not None:
        _headers["x-ms-expiry-time"] = str(expiry_relative)
        _headers["x-ms-expiry-option"] = "RelativeToNow"
    if expiry_absolute is not None:
        _headers["x-ms-expiry-time"] = serialize_rfc(expiry_relative)
        _headers["x-ms-expiry-option"] = "Absolute"

    return HttpRequest(method="PUT", url=_url, params=_params, headers=_headers, content=content, **kwargs)

