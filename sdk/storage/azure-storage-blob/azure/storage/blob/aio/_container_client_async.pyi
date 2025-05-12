# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=unused-argument

from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async

class ContainerClient(AsyncStorageAccountHostsMixin, StorageAccountHostsMixin, StorageEncryptionMixin):
    account_name: str
    container_name: str
    def __init__(
        self,
        account_url: str,
        container_name: str,
        credential: Optional[
            Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, AsyncTokenCredential]
        ] = None,
        *,
        api_version: Optional[str] = None,
        secondary_hostname: Optional[str] = None,
        audience: Optional[str] = None,
        max_block_size: int = 4 * 1024 * 1024,
        max_page_size: int = 4 * 1024 * 1024,
        max_chunk_get_size: int = 4 * 1024 * 1024,
        max_single_put_size: int = 64 * 1024 * 1024,
        max_single_get_size: int = 32 * 1024 * 1024,
        min_large_block_upload_threshold: int = 4 * 1024 * 1024 + 1,
        use_byte_buffer: Optional[bool] = None,
        **kwargs: Any
    ) -> None: ...
    @classmethod
    def from_container_url(
        cls,
        container_url: str,
        credential: Optional[
            Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, AsyncTokenCredential]
        ] = None,
        *,
        api_version: Optional[str] = None,
        secondary_hostname: Optional[str] = None,
        audience: Optional[str] = None,
        max_block_size: int = 4 * 1024 * 1024,
        max_page_size: int = 4 * 1024 * 1024,
        max_chunk_get_size: int = 4 * 1024 * 1024,
        max_single_put_size: int = 64 * 1024 * 1024,
        max_single_get_size: int = 32 * 1024 * 1024,
        min_large_block_upload_threshold: int = 4 * 1024 * 1024 + 1,
        use_byte_buffer: Optional[bool] = None,
        **kwargs: Any
    ) -> Self: ...
    @classmethod
    def from_connection_string(
        cls,
        conn_str: str,
        container_name: str,
        credential: Optional[
            Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, AsyncTokenCredential]
        ] = None,
        *,
        api_version: Optional[str] = None,
        secondary_hostname: Optional[str] = None,
        audience: Optional[str] = None,
        max_block_size: int = 4 * 1024 * 1024,
        max_page_size: int = 4 * 1024 * 1024,
        max_chunk_get_size: int = 4 * 1024 * 1024,
        max_single_put_size: int = 64 * 1024 * 1024,
        max_single_get_size: int = 32 * 1024 * 1024,
        min_large_block_upload_threshold: int = 4 * 1024 * 1024 + 1,
        use_byte_buffer: Optional[bool] = None,
        **kwargs: Any
    ) -> Self: ...
    @distributed_trace_async
    async def create_container(
        self,
        metadata: Optional[Dict[str, str]] = None,
        public_access: Optional[Union[PublicAccess, str]] = None,
        *,
        container_encryption_scope: Optional[Union[Dict[str, Any], ContainerEncryptionScope]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Union[str, datetime]]: ...
    @distributed_trace_async
    async def _rename_container(
        self,
        new_name: str,
        *,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> ContainerClient: ...
    @distributed_trace_async
    async def delete_container(
        self,
        *,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> None: ...
    @distributed_trace_async
    async def acquire_lease(
        self,
        lease_duration: int = -1,
        lease_id: Optional[str] = None,
        *,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> BlobLeaseClient: ...
    @distributed_trace_async
    async def get_account_information(self, **kwargs: Any) -> Dict[str, str]: ...
    @distributed_trace_async
    async def get_container_properties(
        self, *, lease: Optional[Union[BlobLeaseClient, str]] = None, timeout: Optional[int] = None, **kwargs: Any
    ) -> ContainerProperties: ...
    @distributed_trace_async
    async def exists(self, *, timeout: Optional[int] = None, **kwargs: Any) -> bool: ...
    @distributed_trace_async
    async def set_container_metadata(
        self,
        metadata: Optional[Dict[str, str]] = None,
        *,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Union[str, datetime]]: ...
    @distributed_trace
    def _get_blob_service_client(self) -> BlobServiceClient: ...
    @distributed_trace_async
    async def get_container_access_policy(
        self, *, lease: Optional[Union[BlobLeaseClient, str]] = None, timeout: Optional[int] = None, **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace_async
    async def set_container_access_policy(
        self,
        signed_identifiers: Dict[str, AccessPolicy],
        public_access: Optional[Union[str, PublicAccess]] = None,
        *,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Union[str, datetime]]: ...
    @distributed_trace
    def list_blobs(
        self,
        name_starts_with: Optional[str] = None,
        include: Optional[Union[str, List[str]]] = None,
        *,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[BlobProperties]: ...
    @distributed_trace
    def list_blob_names(
        self, *, name_starts_with: Optional[str] = None, timeout: Optional[int] = None, **kwargs: Any
    ) -> AsyncItemPaged[str]: ...
    @distributed_trace
    def walk_blobs(
        self,
        name_starts_with: Optional[str] = None,
        include: Optional[Union[List[str], str]] = None,
        delimiter: str = "/",
        **kwargs: Any
    ) -> AsyncItemPaged[Union[BlobProperties, BlobPrefix]]: ...
    @distributed_trace
    def find_blobs_by_tags(
        self,
        filter_expression: str,
        *,
        results_per_page: Optional[int] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[FilteredBlob]: ...
    @distributed_trace_async
    async def upload_blob(
        self,
        name: str,
        data: Union[bytes, str, Iterable[AnyStr], AsyncIterable[AnyStr], IO[AnyStr]],
        blob_type: Union[str, BlobType] = BlobType.BLOCKBLOB,
        length: Optional[int] = None,
        metadata: Optional[Dict[str, str]] = None,
        *,
        overwrite: Optional[bool] = None,
        content_settings: Optional[ContentSettings] = None,
        validate_content: Optional[bool] = None,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        if_tags_match_condition: Optional[str] = None,
        timeout: Optional[int] = None,
        premium_page_blob_tier: Optional[PremiumPageBlobTier] = None,
        standard_blob_tier: Optional[StandardBlobTier] = None,
        maxsize_condition: Optional[int] = None,
        max_concurrency: Optional[int] = None,
        cpk: Optional[CustomerProvidedEncryptionKey] = None,
        encryption_scope: Optional[str] = None,
        encoding: Optional[str] = None,
        progress_hook: Optional[Callable[[int, Optional[int]], Awaitable[None]]] = None,
        **kwargs: Any
    ) -> BlobClient: ...
    @distributed_trace_async
    async def delete_blob(
        self,
        blob: str,
        delete_snapshots: Optional[str] = None,
        *,
        version_id: Optional[str] = None,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        if_tags_match_condition: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> None: ...
    @distributed_trace_async
    async def download_blob(
        self,
        blob: str,
        offset: Optional[int] = None,
        length: Optional[int] = None,
        *,
        version_id: Optional[str] = None,
        validate_content: Optional[bool] = None,
        lease: Optional[Union[BlobLeaseClient, str]] = None,
        if_modified_since: Optional[datetime] = None,
        if_unmodified_since: Optional[datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        if_tags_match_condition: Optional[str] = None,
        cpk: Optional[CustomerProvidedEncryptionKey] = None,
        max_concurrency: Optional[int] = None,
        encoding: Optional[str] = None,
        progress_hook: Optional[Callable[[int, int], Awaitable[None]]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Union[StorageStreamDownloader[str], StorageStreamDownloader[bytes]]: ...
    @distributed_trace_async
    async def delete_blobs(self, *args, **kwargs) -> None: ...
