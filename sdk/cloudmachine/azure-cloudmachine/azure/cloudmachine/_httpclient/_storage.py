# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from base64 import b64encode
import functools
from io import BytesIO
import json
from datetime import datetime, timedelta, timezone
from time import time
import uuid
from wsgiref.handlers import format_date_time
from urllib.parse import urlparse, quote, urljoin
from typing import IO, Any, Dict, Generator, Generic, Iterable, List, Mapping, Optional, Tuple, Type, TypeVar, Union, overload, Literal
from threading import Thread
from concurrent.futures import Executor, Future
import xml.etree.ElementTree as ET

from azure.core.exceptions import HttpResponseError
from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential, SupportsTokenInfo
from azure.core.pipeline.transport import HttpTransport
from azure.core.rest import HttpRequest, HttpResponse
from azure.core import PipelineClient, MatchConditions
from azure.core.utils import case_insensitive_dict
from azure.core.pipeline.policies import HeadersPolicy

from ._config import CloudMachinePipelineConfig
from ..events import cloudmachine_events
from ._base import CloudMachineClientlet
from ._utils import (
    Pages,
    Stream,
    PartialStream,
    serialize_rfc,
    deserialize_rfc,
    prep_if_match,
    prep_if_none_match,
    parse_content_range,
    get_length,
    serialize_tags_header,
    deserialize_metadata_header
)

_ERROR_CODE = "x-ms-error-code"
_DEFAULT_CHUNK_SIZE = 32 * 1024 * 1024
_DEFAULT_BLOCK_SIZE = 256 * 1024 * 1024
SasPermissions = Literal['read', 'write', 'delete', 'tag', 'create', 'execute']


def _format_url(endpoint: str, container: str) -> str:
    parsed_url = urlparse(endpoint)
    return f"{parsed_url.scheme}://{parsed_url.hostname}/{quote(container)}{parsed_url.query}"


def _build_dict(element: ET) -> Union[str, Dict[str, Any]]:
    if element.text:
        return element.text
    children = [(e.tag, _build_dict(e)) for e in element]
    as_dict = dict(children)
    if len(as_dict) != len(children):
        return children
    return as_dict or None


class StorageHeadersPolicy(HeadersPolicy):
    def on_request(self, request: 'PipelineRequest') -> None:
        super(StorageHeadersPolicy, self).on_request(request)
        current_time = format_date_time(time())
        request.http_request.headers['x-ms-date'] = current_time

class StorageBatchError(HttpResponseError):
    succeeded: List[Union[str, 'StorageFile']]
    failed: List[Tuple[Union[str, 'StorageFile'], HttpResponseError]]

    def __init__(
            self,
            *args,
            succeeded: List[Union[str, 'StorageFile']],
            failed: List[Tuple[Union[str, 'StorageFile'], HttpResponseError]],
            response: HttpResponse,
            **kwargs):
        self.succeeded = succeeded
        self.failed = failed
        super().__init__(*args, response=response, **kwargs)


T = TypeVar("T")

class DeletedFile:
    __responsedata__: Dict[str, Any]
    filename: str
    container: str
    endpoint: str

    def __init__(
            self,
            *,
            filename: str,
            container: str,
            endpoint: str,
            responsedata: Dict[str, Any]
    ) -> None:
        self.filename = filename
        self.container = container
        self.endpoint = endpoint
        self.__responsedata__ = responsedata

    def __repr__(self) -> str:
        return f"DeletedStorageFile(filename={self.filename})"

    def __str__(self) -> str:
        return f"{self.container}/{self.filename}"

class StorageFile(Generic[T]):
    __responsedata__: Dict[str, Any]
    metadata: Dict[str, str]
    tags: Dict[str, str]
    etag: str
    content: T
    filename: str
    container: str
    endpoint: str
    content_length: int
    content_type: Optional[str]
    content_encoding: Optional[str]
    content_language: Optional[str]
    content_disposition: Optional[str]
    cache_control: Optional[str]

    def __init__(
            self,
            *,
            filename: str,
            container: str,
            content: T,
            content_length: Union[int, str],
            etag: str,
            endpoint: str,
            **kwargs
    ) -> None:
        self.content = content
        self.content_length = int(content_length)
        self.etag = etag
        self.filename = filename
        self.container = container
        self.endpoint = endpoint
        self.metadata = kwargs.get('metadata') or {}
        self.tags = kwargs.get('tags') or {}
        self.content_type = kwargs.get('content_type')
        self.content_encoding = kwargs.get('content_type')
        self.content_language = kwargs.get('content_type')
        self.content_disposition = kwargs.get('content_type')
        self.cache_control = kwargs.get('content_type')
        self.__responsedata__ = kwargs.get('responsedata', {})

    def __repr__(self) -> str:
        return f"StorageFile(filename={self.filename}, content_length={self.content_length})"

    def __str__(self) -> str:
        return f"{self.container}/{self.filename}"


class CloudMachineStorage(CloudMachineClientlet):
    _id: Literal['Blob'] = 'storage:blob'
    default_container_name: str
    
    def __init__(
            self,
            endpoint: str,
            account_name: str,
            credential: Union[AzureNamedKeyCredential, AzureSasCredential, SupportsTokenInfo],
            *,
            container_name: str,
            transport: Optional[HttpTransport] = None,
            api_version: Optional[str] = None,
            executor: Optional[Executor] = None,
            config: Optional[CloudMachinePipelineConfig] = None,
            resource_id: Optional[str] = None,
            scope: str,
            **kwargs
    ):
        headers_policy = StorageHeadersPolicy(**kwargs)
        super().__init__(
            endpoint=endpoint,
            credential=credential,
            transport=transport,
            api_version=api_version,
            config=config,
            scope=scope,
            executor=executor,
            headers_policy=headers_policy,
            resource_id=resource_id,
            **kwargs
        )
        self.default_container_name = container_name
        self._account_name = account_name
        self._containers: Dict[str, PipelineClient] = {}
        self._user_delegation_key: Optional[str] = None

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

    def _batch_send(self, *reqs: HttpRequest, **kwargs) -> None:
        policies = [StorageHeadersPolicy(), self._config.authentication_policy]
        request = HttpRequest(
            method="POST",
            url=self._endpoint,
            params={'comp': 'batch'},
            headers={"x-ms-version": self._config.api_version},
        )
        request.set_multipart_mixed(
            *reqs,
            policies=policies,
            enforce_https=False,
            boundary=f"batch_{uuid.uuid4()}",
        )
        response = self._client.send_request(request, stream=True, **kwargs)
        if response.status_code not in [202]:
            raise HttpResponseError(response=response)
        return response

    @overload
    def get_url(
            self,
            *,
            file: StorageFile,
            permissions: Union[str, List[SasPermissions]] = 'r',
            expiry: Union[datetime, timedelta, Literal['never']] = 'never',
            start: Union[datetime, timedelta, Literal['now']] = 'now',
    ) -> str:
        ...
    @overload
    def get_url(
            self,
            *,
            file: Optional[str] = None,
            container: Optional[str] = None,
            permissions: Union[str, List[Union[SasPermissions, Literal['list', 'filter']]]] = 'r',
            expiry: Union[datetime, timedelta, Literal['never']] = 'never',
            start: Union[datetime, timedelta, Literal['now']] = 'now',
    ) -> str:
        ...
    def get_url(
            self,
            *,
            file: Optional[Union[str, StorageFile]] = None,
            container: Optional[str] = None,
            permissions: Union[str, List[SasPermissions]] = 'r',
            expiry: Union[datetime, timedelta, int] = 60,
            start: Union[datetime, timedelta, Literal['now']] = 'now',
    ) -> str:
        from azure.storage.blob import generate_blob_sas, generate_container_sas, BlobServiceClient
        kwargs = {}
        if isinstance(start, timedelta):
            kwargs['start'] = datetime.now(timezone.utc) + start
        elif start != 'now':
            kwargs['start'] = start
        if isinstance(expiry, int):
            expiry = timedelta(minutes=expiry)
        if isinstance(expiry, timedelta):
            kwargs['expiry'] = datetime.now(timezone.utc) + expiry
        else:
            kwargs['expiry'] = expiry
        kwargs['permission'] = permissions if isinstance(permissions, str) else "".join(p[0] for p in permissions)
        if isinstance(self._credential, AzureNamedKeyCredential):
            named_key = self._credential.named_key
            kwargs['account_name'] = self._account_name
            kwargs['account_key'] = named_key.key
        elif isinstance(self._credential, SupportsTokenInfo):
            kwargs['account_name'] = self._account_name
            # if not self._user_delegation_key or self._user_delegation_key.signed_expiry < kwargs['expiry']:
            service_client = BlobServiceClient(self._endpoint, self._credential)
            self._user_delegation_key = service_client.get_user_delegation_key(
                key_start_time=datetime.now(timezone.utc),
                key_expiry_time=kwargs['expiry']
            )
            kwargs['user_delegation_key'] = self._user_delegation_key
        else:
            raise NotImplementedError('AzureSasCredential does not support SAS URL generation.')
        kwargs['container_name'] = file.container if isinstance(file, StorageFile) else container or self.default_container_name
        if file:
            kwargs['blob_name'] = file.filename if isinstance(file, StorageFile) else file
            sas_token = generate_blob_sas(**kwargs)
            endpoint = urljoin(self._endpoint, f"{kwargs['container_name']}/{kwargs['blob_name']}")
            return f"{endpoint}?{sas_token}"
        else:
            sas_token = generate_container_sas(**kwargs)
            return f"{urljoin(self._endpoint, kwargs['container_name'])}?{sas_token}"

    def list(
            self,
            *,
            prefix: Optional[str] = None,
            container: Optional[str] = None,
            include_metadata: bool = False,
            include_tags: bool = False,
            minimal: bool = False,
            continue_from: Optional[str] = None,
            pages: Optional[int] = None,
            pagesize: int = 100,
            **kwargs
    ) -> Generator[StorageFile[None], None, Optional[str]]:
        client = self._get_container_client(container)
        include = []
        if include_metadata:
            include.append('metadata')
        if include_tags:
            include.append('tags')
        kwargs['delimiter'] = kwargs.pop('delimiter', None)
        kwargs['showonly'] = kwargs.pop('showonly', 'files')
        kwargs['maxresults'] = pagesize
        kwargs['prefix'] = prefix
        kwargs['include'] = include
        kwargs['version'] = self._config.api_version

        def _request_one_page(marker: Optional[str]) -> Generator[StorageFile[None], None, Optional[str]]:
            request_params = dict(kwargs)
            request = build_list_blob_page_request(
                url=client.endpoint,
                marker=marker,
                kwargs=request_params,
            )
            response = client.send_request(request, **request_params)
            if response.status_code == 404 and response.headers.get(_ERROR_CODE) == 'ContainerNotFound':
                return None
            if response.status_code != 200:
                raise HttpResponseError(response=response)
            page = ET.fromstring(response.read().decode('utf-8'))
            for xmlblob in page.find('Blobs'):
                if xmlblob.tag == 'Blob':
                    if minimal:
                        properties = xmlblob.find('Properties')
                        filename = xmlblob[0].text
                        yield StorageFile(
                            filename=filename,
                            container=container or self.default_container_name,
                            content=None,
                            content_length=properties.find('Content-Length').text,
                            etag=properties.find('Etag').text,
                            endpoint=urljoin(client.endpoint, quote(filename))
                        )
                    else:
                        blob = _build_dict(xmlblob)
                        properties = blob['Properties']
                        filename = blob['Name']
                        tags = None
                        if include_tags:
                            tags = {t['Key']: t['Value'] for t in blob.get('Tags', {}).get('TagSet', [])}
                        yield StorageFile(
                            filename=filename,
                            content=None,
                            container=container or self.default_container_name,
                            content_length=properties['Content-Length'],
                            etag=properties['Etag'],
                            metadata=blob.get('Metadata', {}),
                            tags=tags,
                            endpoint=urljoin(client.endpoint, quote(filename)),
                            content_type = properties['Content-Type'],
                            content_encoding = properties['Content-Encoding'],
                            content_language = properties['Content-Language'],
                            content_disposition = properties['Content-Disposition'],
                            cache_control = properties['Cache-Control'],
                            responsedata=blob,
                        )
            next_page = page.find('NextMarker')
            return next_page.text if next_page is not None else None
            
        return Pages(
            _request_one_page,
            n_pages=pages,
            continuation=continue_from,
        )
            
    # TODO: Scope batch delete to specific container to prevent accidental delete outside of scope.
    def _delete(self, *files: Union[str, StorageFile], container: Optional[str] = None, **kwargs) -> None:
        if not files:
            return
        condition = kwargs.pop('condition', MatchConditions.Unconditionally)
        requests = []
        etag = kwargs.pop('etag', None)
        for file in files:
            try:
                etag = file.etag
                filename = file.filename
                file_container = file.container
            except AttributeError:
                filename = file
                file_container = container or self.default_container_name

            kwargs['if_match'] = prep_if_match(etag, condition)
            kwargs['if_none_match'] = prep_if_none_match(etag, condition)
            requests.append(
                build_delete_blob_request(
                    f"/{quote(file_container)}",
                    filename,
                    kwargs
                )
            )
        response = self._batch_send(*requests)
        succeeded = []
        failed = []
        for file, part_response in zip(files, response.parts()):
            if ((part_response.status_code == 202) or
                (part_response.status_code == 404 and part_response.headers.get(_ERROR_CODE) == 'BlobNotFound') or
                (part_response.status_code == 404 and part_response.headers.get(_ERROR_CODE) == 'ContainerNotFound') or
                (part_response.status_code == 409 and part_response.headers.get(_ERROR_CODE) == 'ContainerBeingDeleted')):
                succeeded.append(file)
            else:
                failed.append((file, HttpResponseError(response=response)))
        if failed:
            raise StorageBatchError(response=response, succeeded=succeeded, failed=failed)

    @overload
    def delete(
            self,
            *files: Union[str, StorageFile],
            container: Optional[str] = None,
            condition: MatchConditions = MatchConditions.Unconditionally,
            etag: Optional[str] = None,
            wait: Literal[True] = True,
            **kwargs
    ) -> None:
        ...
    @overload
    def delete(
            self,
            *files: Union[str, StorageFile],
            container: Optional[str] = None,
            condition: MatchConditions = MatchConditions.Unconditionally,
            etag: Optional[str] = None,
            wait: Literal[False],
            **kwargs
    ) -> Future[None]:
        ...
    def delete(
            self,
            *files: Union[StorageFile, str],
            container: Optional[str] = None,
            condition: MatchConditions = MatchConditions.Unconditionally,
            etag: Optional[str] = None,
            wait: bool = True,
            **kwargs) -> None:
        if wait:
            return self._delete(
                *files,
                container=container,
                condition=condition,
                etag=etag,
                **kwargs
            )
        return self._executor.submit(
                self._delete,
                *files,
                container=container,
                condition=condition,
                etag=etag,
                **kwargs
            )

    def _upload(
            self,
            data: IO[bytes],
            *,
            content_length: Optional[int] = None,
            filename: Optional[str] = None,
            container: Optional[str] = None,
            condition: MatchConditions = MatchConditions.IfMissing,
            metadata: Optional[Dict[str, str]],
            etag: Optional[str] = None,
            tags: Optional[Dict[str, str]] = None,
            content_type: Optional[str] = None,
            content_encoding: Optional[str] = None,
            content_language: Optional[str] = None,
            content_disposition: Optional[str] = None,
            cache_control: Optional[str] = None,
            **kwargs
    ) -> StorageFile[None]:
        # TODO: support upload by block list + commit
        # TODO: support content validation
        client = self._get_container_client(container)
        filename = filename or data.filename if hasattr(data, 'filename') else str(uuid.uuid4())
        content_length=content_length or get_length(data)
        kwargs['version'] = self._config.api_version
        kwargs['if_match'] = prep_if_match(etag, condition)
        kwargs['if_none_match'] = prep_if_none_match(etag, condition)
        kwargs['blob_content_type'] = content_type
        kwargs['blob_content_encoding'] = content_encoding
        kwargs['blob_content_language'] = content_language
        kwargs['blob_content_disposition'] = content_disposition
        kwargs['blob_cache_control'] = cache_control
        kwargs['blob_tags_string'] = serialize_tags_header(tags)
        expiry = kwargs.pop('expiry', None)
        if isinstance(expiry, timedelta):
            kwargs['expiry_relative'] = int(expiry.microseconds/1000)
        elif expiry:
            kwargs['expiry_absolute'] = expiry
        content = data if hasattr(data, 'read') else BytesIO(data)
        initial_index = content.tell()
        request = build_upload_blob_request(
            client.endpoint + f"/{quote(filename)}",
            content_length=content_length,
            content=content,
            kwargs=kwargs
        )
        response = client.send_request(request, **kwargs)
        if response.status_code == 404 and response.headers.get(_ERROR_CODE) == 'ContainerNotFound':
            # TODO: if this is an authenticated session - set acl
            self._create_container(container, **kwargs)
            content.seek(initial_index)  # TODO: need to test this...
            response = client.send_request(request, **kwargs)
        if response.status_code not in [201]:
            raise HttpResponseError(response=response)
        return StorageFile(
            filename = filename,
            container = container or self.default_container_name,
            content_length = content_length,
            last_modified = response.headers['Last-Modified'],
            etag = response.headers['ETag'],
            responsedata = response.headers,
            content_type = content_type,
            content_encoding = content_encoding,
            content_language = content_language,
            content_disposition = content_disposition,
            cache_control = cache_control,
            metadata=metadata,
            endpoint=urljoin(client.endpoint, quote(filename)),
            tags=tags,
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
            overwrite: bool = False,
            condition: MatchConditions = MatchConditions.IfMissing,
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
            overwrite: bool = False,
            condition: MatchConditions = MatchConditions.IfMissing,
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
            overwrite: bool = False,
            condition: MatchConditions = MatchConditions.IfMissing,
            etag: Optional[str] = None,
            metadata: Optional[Dict[str, str]] = None,
            tags: Optional[Dict[str, str]] = None,
            wait: bool = True,
            **kwargs
    ) -> Union[Future[StorageFile[None]], StorageFile[None]]:
        if overwrite:
            condition = MatchConditions.Unconditionally
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
            content_range: Optional[Tuple[int, Optional[int]]] = None,
            container: Optional[str] = None,
            condition: MatchConditions = MatchConditions.IfPresent,
            etag: Optional[str] = None,
            validate: bool = False,
            **kwargs
    ) -> StorageFile[IO[bytes]]:
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
            client.endpoint,
            filename,
            kwargs
        )
        request_start = 0 if content_range is None else content_range[0]
        request_end = chunk_size if content_range is None or content_range[1] is None or content_range[1] > chunk_size else content_range[1]
        range_header = f'bytes={request_start}-{request_end}'
        request = request_builder(range_header)
        response, response_start, response_end, filelength = _download(request, **kwargs)
        first_chunk = PartialStream(
            start=response_start,
            end=response_end,
            response=response
        )
        downloaded = response_end - response_start
        if content_range:
            if content_range[1]:
                expected_length = content_range[1] - content_range[0]
            else:
                expected_length = filelength - content_range[0]
        else:
            expected_length = filelength
        if downloaded < expected_length:
            download_end = filelength if content_range is None or content_range[1] is None else content_range[1]
            chunk_iter = range(response_end + 1, download_end, chunk_size)
            request_gen = (request_builder(f'bytes={r}-{r + chunk_size}') for r in chunk_iter)
            response_gen = (_download(r, **kwargs) for r in request_gen)
            stream = Stream(
                content_length=expected_length,
                content_range=f'bytes {request_start}-{download_end}/{filelength}',
                first_chunk=first_chunk,
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
            container=container or self.default_container_name,
            content_length=filelength,
            last_modified = response.headers['Last-Modified'],
            etag = response.headers['ETag'],
            content_type = response.headers['Content-Type'],
            content_encoding = response.headers.get('Content-Encoding'),
            content_language = response.headers.get('Content-Language'),
            content_disposition = response.headers.get('Content-Disposition'),
            cache_control = response.headers.get('Cache-Control'),
            metadata = deserialize_metadata_header(response.headers),
            responsedata=response.headers,
            content=stream,
            endpoint=urljoin(client.endpoint, quote(filename))
        )
    @overload
    def download(
            self,
            filename: str,
            *,
            range: Optional[Tuple[int, Optional[int]]] = None,
            container: Optional[str] = None,
            condition: MatchConditions = MatchConditions.IfPresent,
            etag: Optional[str] = None,
            validate: bool = False,
            chunk_size: int = _DEFAULT_CHUNK_SIZE,
            wait: Literal[True] = True,
            **kwargs
    ) -> StorageFile[IO[bytes]]:
        ...
    @overload
    def download(
            self,
            filename: str,
            *,
            range: Optional[Tuple[int, Optional[int]]] = None,
            container: Optional[str] = None,
            condition: MatchConditions = MatchConditions.IfPresent,
            etag: Optional[str] = None,
            validate: bool = False,
            chunk_size: int = _DEFAULT_CHUNK_SIZE,
            wait: Literal[False],
            **kwargs
    ) -> Future[StorageFile[IO[bytes]]]:
        ...
    def download(
            self,
            filename: str,
            *,
            range: Optional[Tuple[int, Optional[int]]] = None,
            container: Optional[str] = None,
            condition: MatchConditions = MatchConditions.IfPresent,
            etag: Optional[str] = None,
            validate: bool = False,
            wait: bool = True,
            **kwargs
    ) -> Union[StorageFile[IO[bytes]], Future[StorageFile[IO[bytes]]]]:
        # Remove page number from path, filename-1.txt -> filename.txt
        # This shouldn't typically be necessary as browsers don't send hash fragments to servers
        if filename.find("#page=") > 0:
            path_parts = filename.rsplit("#page=", 1)
            filename = path_parts[0]
        if wait:
            return self._download(
                filename=filename,
                content_range=range,
                container=container,
                condition=condition,
                etag=etag,
                validate=validate,
                **kwargs
            )
        return self._executor.submit(
            self._download,
            filename=filename,
            content_range=range,
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
    version: str = kwargs.pop("version")
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
        _headers["x-ms-blob-public-access"] = str(access)
    _headers["x-ms-version"] = str(version)

    if default_encryption_scope is not None:
        _headers["x-ms-default-encryption-scope"] = str(default_encryption_scope)
    if prevent_encryption_scope_override is not None:
        _headers["x-ms-deny-encryption-scope-override"] = json.dumps(prevent_encryption_scope_override)
    _headers["Accept"] = str(accept)

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
    version: str = kwargs.pop("version")
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
        _headers["x-ms-lease-id"] = str(lease_id)
    if if_modified_since is not None:
        _headers["If-Modified-Since"] = serialize_rfc(if_modified_since)
    if if_unmodified_since is not None:
        _headers["If-Unmodified-Since"] = serialize_rfc(if_unmodified_since)
    _headers["x-ms-version"] = str(version)
    _headers["Accept"] = str(accept)

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
    blob_delete_type: Optional[Literal["Permanent"]] = None
    version: Optional[str] = kwargs.pop("version", None)
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
    if version:
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
    version: str = kwargs.pop("version")
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
    version: str = kwargs.pop("version")
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


def build_list_blob_page_request(
    url: str,
    kwargs: Any,
    marker: Optional[str] = None,
) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
    _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

    delimiter: Optional[str] = kwargs.pop("delimiter", None)
    prefix: Optional[str] = kwargs.pop("prefix", None)
    showonly: Optional[str] = kwargs.pop("showonly", None)
    maxresults: Optional[int] = kwargs.pop("maxresults", None)
    include: Optional[List[str]] = kwargs.pop("include", None)
    timeout: Optional[int] = kwargs.pop("servicetimeout", None)
    restype: Literal["container"] = kwargs.pop("restype", _params.pop("restype", "container"))
    comp: Literal["list"] = kwargs.pop("comp", _params.pop("comp", "list"))
    version: str = kwargs.pop("version")
    accept = _headers.pop("Accept", "application/xml")

    # Construct URL
    _url = kwargs.pop("template_url", "{url}")
    path_format_arguments = {
        "url": url,
    }
    _url: str = _url.format(**path_format_arguments)  # type: ignore

    # Construct parameters
    _params["restype"] = quote(restype)
    _params["comp"] = quote(comp)
    if prefix is not None:
        _params["prefix"] = quote(prefix)
    if showonly is not None:
        _params["showonly"] = quote(showonly)
    if delimiter is not None:
        _params["delimiter"] = quote(delimiter)
    if marker is not None:
        _params["marker"] = quote(marker)
    if maxresults is not None:
        _params["maxresults"] = quote(str(maxresults))
    if include is not None:
        _params["include"] = quote(",".join(include))
    if timeout is not None:
        _params["timeout"] = quote(str(timeout))

    # Construct headers
    _headers["x-ms-version"] = str(version)
    _headers["Accept"] = str(accept)

    return HttpRequest(method="GET", url=_url, params=_params, headers=_headers, **kwargs)


def build_get_user_delegation_key_request(
    url: str, *, content: Any, servicetimeout: Optional[int] = None, **kwargs: Any
) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
    _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

    restype: Literal["service"] = kwargs.pop("restype", _params.pop("restype", "service"))
    comp: Literal["userdelegationkey"] = kwargs.pop("comp", _params.pop("comp", "userdelegationkey"))
    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    version: Literal["2024-08-04"] = kwargs.pop("version", _headers.pop("x-ms-version", "2024-08-04"))
    accept = _headers.pop("Accept", "application/xml")

    # Construct URL
    _url = kwargs.pop("template_url", "{url}")
    path_format_arguments = {
        "url": _SERIALIZER.url("url", url, "str", skip_quote=True),
    }

    _url: str = _url.format(**path_format_arguments)  # type: ignore

    # Construct parameters
    _params["restype"] = _SERIALIZER.query("restype", restype, "str")
    _params["comp"] = _SERIALIZER.query("comp", comp, "str")
    if timeout is not None:
        _params["timeout"] = _SERIALIZER.query("servicetimeout", servicetimeout, "int", minimum=0)

    # Construct headers
    _headers["x-ms-version"] = _SERIALIZER.header("version", version, "str")
    if content_type is not None:
        _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="POST", url=_url, params=_params, headers=_headers, content=content, **kwargs)
