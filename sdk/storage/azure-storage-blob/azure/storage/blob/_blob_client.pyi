# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from datetime import datetime
from typing import (
    Any,
    AnyStr,
    Callable,
    Dict,
    IO,
    Iterable,
    List,
    Literal,
    Optional,
    overload,
    Tuple,
    Union,
)
from typing_extensions import Self

from azure.core import MatchConditions
from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential, TokenCredential
from azure.core.paging import ItemPaged
from azure.core.tracing.decorator import distributed_trace
from ._download import StorageStreamDownloader
from ._generated.models import RehydratePriority
from ._lease import BlobLeaseClient
from ._models import (
    ArrowDialect,
    BlobBlock,
    BlobProperties,
    BlobQueryError,
    BlobType,
    ContentSettings,
    CustomerProvidedEncryptionKey,
    DelimitedTextDialect,
    DelimitedJsonDialect,
    ImmutabilityPolicy,
    PageRange,
    PremiumPageBlobTier,
    QuickQueryDialect,
    SequenceNumberAction,
    StandardBlobTier,
)
from ._quick_query_helper import BlobQueryReader

class BlobClient:
    def __init__(
        self,
        account_url: str,
        container_name: str,
        blob_name: str,
        snapshot: Optional[Union[str, Dict[str, Any]]],
        credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]],
        *,
        api_version: Optional[str],
        secondary_hostname: Optional[str],
        version_id: Optional[str],
        audience: Optional[str],
        max_block_size: int,
        max_page_size: int,
        max_chunk_get_size: int,
        max_single_put_size: int,
        max_single_get_size: int,
        min_large_block_upload_threshold: int,
        use_byte_buffer: Optional[bool],
        **kwargs: Any
    ) -> None: ...
    @classmethod
    def from_blob_url(
        cls,
        blob_url: str,
        credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]],
        snapshot: Optional[Union[str, Dict[str, Any]]],
        *,
        api_version: Optional[str],
        secondary_hostname: Optional[str],
        version_id: Optional[str],
        audience: Optional[str],
        max_block_size: int,
        max_page_size: int,
        max_chunk_get_size: int,
        max_single_put_size: int,
        max_single_get_size: int,
        min_large_block_upload_threshold: int,
        use_byte_buffer: Optional[bool],
        **kwargs: Any
    ) -> Self: ...
    @classmethod
    def from_connection_string(
        cls,
        conn_str: str,
        container_name: str,
        blob_name: str,
        snapshot: Optional[Union[str, Dict[str, Any]]],
        credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]],
        *,
        api_version: Optional[str],
        secondary_hostname: Optional[str],
        version_id: Optional[str],
        audience: Optional[str],
        max_block_size: int,
        max_page_size: int,
        max_chunk_get_size: int,
        max_single_put_size: int,
        max_single_get_size: int,
        min_large_block_upload_threshold: int,
        use_byte_buffer: Optional[bool],
        **kwargs: Any
    ) -> Self: ...
    @distributed_trace
    def get_account_information(self, **kwargs: Any) -> Dict[str, str]: ...
    @distributed_trace
    def upload_blob_from_url(
        self,
        source_url: str,
        *,
        metadata: Optional[Dict[str, str]],
        overwrite: Optional[bool],
        include_source_blob_properties: bool,
        tags: Optional[Dict[str, str]],
        source_content_md5: Optional[bytearray],
        source_if_modified_since: Optional[datetime],
        source_if_unmodified_since: Optional[datetime],
        source_etag: Optional[str],
        source_match_condition: Optional[MatchConditions],
        if_modified_since: Optional[datetime],
        if_unmodified_since: Optional[datetime],
        etag: Optional[str],
        match_condition: Optional[MatchConditions],
        destination_lease: Optional[Union[BlobLeaseClient, str]],
        timeout: Optional[int],
        content_settings: Optional[ContentSettings],
        cpk: Optional[CustomerProvidedEncryptionKey],
        encryption_scope: Optional[str],
        standard_blob_tier: Optional[StandardBlobTier],
        source_authorization: Optional[str],
        **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace
    def upload_blob(
        self,
        data: Union[bytes, str, Iterable[AnyStr], IO[bytes]],
        blob_type: Union[str, BlobType],
        length: Optional[int],
        metadata: Optional[Dict[str, str]],
        *,
        tags: Optional[Dict[str, str]],
        overwrite: bool,
        content_settings: Optional[ContentSettings],
        validate_content: bool,
        lease: Optional[BlobLeaseClient],
        if_modified_since: Optional[datetime],
        if_unmodified_since: Optional[datetime],
        etag: Optional[str],
        match_condition: Optional[MatchConditions],
        if_tags_match_condition: Optional[str],
        premium_page_blob_tier: Optional[PremiumPageBlobTier],
        immutability_policy: Optional[ImmutabilityPolicy],
        legal_hold: Optional[bool],
        standard_blob_tier: Optional[StandardBlobTier],
        maxsize_condition: Optional[int],
        max_concurrency: int,
        cpk: Optional[CustomerProvidedEncryptionKey],
        encryption_scope: Optional[str],
        encoding: str,
        progress_hook: Optional[Callable[[int, Optional[int]], None]],
        timeout: Optional[int],
        **kwargs: Any
    ) -> Dict[str, Any]: ...
    @overload
    def download_blob(
        self,
        offset: Optional[int],
        length: Optional[int],
        *,
        version_id: Optional[str],
        validate_content: bool,
        lease: Optional[Union[BlobLeaseClient, str]],
        if_modified_since: Optional[datetime],
        if_unmodified_since: Optional[datetime],
        etag: Optional[str],
        match_condition: Optional[MatchConditions],
        if_tags_match_condition: Optional[str],
        cpk: Optional[CustomerProvidedEncryptionKey],
        max_concurrency: int,
        encoding: str,
        progress_hook: Optional[Callable[[int, int], None]],
        timeout: Optional[int],
        **kwargs: Any
    ) -> StorageStreamDownloader[str]: ...
    @overload
    def download_blob(
        self,
        offset: Optional[int],
        length: Optional[int],
        *,
        version_id: Optional[str],
        validate_content: bool,
        lease: Optional[Union[BlobLeaseClient, str]],
        if_modified_since: Optional[datetime],
        if_unmodified_since: Optional[datetime],
        etag: Optional[str],
        match_condition: Optional[MatchConditions],
        if_tags_match_condition: Optional[str],
        cpk: Optional[CustomerProvidedEncryptionKey],
        max_concurrency: int,
        encoding: None,
        progress_hook: Optional[Callable[[int, int], None]],
        timeout: Optional[int],
        **kwargs: Any
    ) -> StorageStreamDownloader[bytes]: ...
    @distributed_trace
    def download_blob(
        self,
        offset: Optional[int],
        length: Optional[int],
        *,
        version_id: Optional[str],
        validate_content: bool,
        lease: Optional[Union[BlobLeaseClient, str]],
        if_modified_since: Optional[datetime],
        if_unmodified_since: Optional[datetime],
        etag: Optional[str],
        match_condition: Optional[MatchConditions],
        if_tags_match_condition: Optional[str],
        cpk: Optional[CustomerProvidedEncryptionKey],
        max_concurrency: int,
        encoding: Optional[str],
        progress_hook: Optional[Callable[[int, int], None]],
        timeout: Optional[int],
        **kwargs: Any
    ) -> Union[StorageStreamDownloader[str], StorageStreamDownloader[bytes]]: ...
    @distributed_trace
    def query_blob(
        self,
        query_expression: str,
        *,
        on_error: Optional[Callable[[BlobQueryError], None]],
        blob_format: Optional[Union[DelimitedTextDialect, DelimitedJsonDialect, QuickQueryDialect, str]],
        output_format: Optional[
            Union[DelimitedTextDialect, DelimitedJsonDialect, QuickQueryDialect, List[ArrowDialect], str]
        ],
        lease: Optional[Union[BlobLeaseClient, str]],
        if_modified_since: Optional[datetime],
        if_unmodified_since: Optional[datetime],
        etag: Optional[str],
        match_condition: Optional[MatchConditions],
        if_tags_match_condition: Optional[str],
        cpk: Optional[CustomerProvidedEncryptionKey],
        timeout: Optional[int],
        **kwargs: Any
    ) -> BlobQueryReader: ...
    @distributed_trace
    def delete_blob(
        self,
        delete_snapshots: Optional[str],
        *,
        version_id: Optional[str],
        lease: Optional[Union[BlobLeaseClient, str]],
        if_modified_since: Optional[datetime],
        if_unmodified_since: Optional[datetime],
        etag: Optional[str],
        match_condition: Optional[MatchConditions],
        if_tags_match_condition: Optional[str],
        timeout: Optional[int],
        **kwargs: Any
    ) -> None: ...
    @distributed_trace
    def undelete_blob(self, *, timeout: Optional[int], **kwargs: Any) -> None: ...
    @distributed_trace
    def exists(self, *, version_id: Optional[str], timeout: Optional[int], **kwargs: Any) -> bool: ...
    @distributed_trace
    def get_blob_properties(
        self,
        *,
        lease: Optional[Union[BlobLeaseClient, str]],
        version_id: Optional[str],
        if_modified_since: Optional[datetime],
        if_unmodified_since: Optional[datetime],
        etag: Optional[str],
        match_condition: Optional[MatchConditions],
        if_tags_match_condition: Optional[str],
        cpk: Optional[CustomerProvidedEncryptionKey],
        timeout: Optional[int],
        **kwargs: Any
    ) -> BlobProperties: ...
    @distributed_trace
    def set_http_headers(
        self,
        content_settings: Optional[ContentSettings],
        *,
        lease: Optional[Union[BlobLeaseClient, str]],
        if_modified_since: Optional[datetime],
        if_unmodified_since: Optional[datetime],
        etag: Optional[str],
        match_condition: Optional[MatchConditions],
        if_tags_match_condition: Optional[str],
        timeout: Optional[int],
        **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace
    def set_blob_metadata(
        self,
        metadata: Optional[Dict[str, str]],
        *,
        lease: Optional[Union[BlobLeaseClient, str]],
        if_modified_since: Optional[datetime],
        if_unmodified_since: Optional[datetime],
        etag: Optional[str],
        match_condition: Optional[MatchConditions],
        if_tags_match_condition: Optional[str],
        cpk: Optional[CustomerProvidedEncryptionKey],
        encryption_scope: Optional[str],
        timeout: Optional[int],
        **kwargs: Any
    ) -> Dict[str, Union[str, datetime]]: ...
    @distributed_trace
    def set_immutability_policy(
        self,
        immutability_policy: ImmutabilityPolicy,
        *,
        version_id: Optional[str],
        timeout: Optional[int],
        **kwargs: Any
    ) -> Dict[str, str]: ...
    @distributed_trace
    def delete_immutability_policy(
        self, *, version_id: Optional[str], timeout: Optional[int], **kwargs: Any
    ) -> None: ...
    @distributed_trace
    def set_legal_hold(
        self, legal_hold: bool, *, version_id: Optional[str], timeout: Optional[int], **kwargs: Any
    ) -> Dict[str, Union[str, datetime, bool]]: ...
    @distributed_trace
    def create_page_blob(
        self,
        size: int,
        content_settings: Optional[ContentSettings],
        metadata: Optional[Dict[str, str]],
        premium_page_blob_tier: Optional[Union[str, PremiumPageBlobTier]],
        *,
        tags: Optional[Dict[str, str]],
        sequence_number: Optional[int],
        lease: Optional[Union[BlobLeaseClient, str]],
        immutability_policy: Optional[ImmutabilityPolicy],
        legal_hold: Optional[bool],
        if_modified_since: Optional[datetime],
        if_unmodified_since: Optional[datetime],
        etag: Optional[str],
        match_condition: Optional[MatchConditions],
        cpk: Optional[CustomerProvidedEncryptionKey],
        encryption_scope: Optional[str],
        timeout: Optional[int],
        **kwargs: Any
    ) -> Dict[str, Union[str, datetime]]: ...
    @distributed_trace
    def create_append_blob(
        self,
        content_settings: Optional[ContentSettings],
        metadata: Optional[Dict[str, str]],
        *,
        tags: Optional[Dict[str, str]],
        immutability_policy: Optional[ImmutabilityPolicy],
        legal_hold: Optional[bool],
        lease: Optional[Union[BlobLeaseClient, str]],
        if_modified_since: Optional[datetime],
        if_unmodified_since: Optional[datetime],
        etag: Optional[str],
        match_condition: Optional[MatchConditions],
        cpk: Optional[CustomerProvidedEncryptionKey],
        encryption_scope: Optional[str],
        timeout: Optional[int],
        **kwargs: Any
    ) -> Dict[str, Union[str, datetime]]: ...
    @distributed_trace
    def create_snapshot(
        self,
        metadata: Optional[Dict[str, str]],
        *,
        if_modified_since: Optional[datetime],
        if_unmodified_since: Optional[datetime],
        etag: Optional[str],
        match_condition: Optional[MatchConditions],
        if_tags_match_condition: Optional[str],
        lease: Optional[Union[BlobLeaseClient, str]],
        cpk: Optional[CustomerProvidedEncryptionKey],
        encryption_scope: Optional[str],
        timeout: Optional[int],
        **kwargs: Any
    ) -> Dict[str, Union[str, datetime]]: ...
    @distributed_trace
    def start_copy_from_url(
        self,
        source_url: str,
        metadata: Optional[Dict[str, str]],
        incremental_copy: bool,
        *,
        tags: Optional[Union[Dict[str, str], Literal["COPY"]]],
        immutability_policy: Optional[ImmutabilityPolicy],
        legal_hold: Optional[bool],
        source_if_modified_since: Optional[datetime],
        source_if_unmodified_since: Optional[datetime],
        source_etag: Optional[str],
        source_match_condition: Optional[MatchConditions],
        if_modified_since: Optional[datetime],
        if_unmodified_since: Optional[datetime],
        etag: Optional[str],
        match_condition: Optional[MatchConditions],
        if_tags_match_condition: Optional[str],
        destination_lease: Optional[Union[BlobLeaseClient, str]],
        source_lease: Optional[Union[BlobLeaseClient, str]],
        premium_page_blob_tier: Optional[PremiumPageBlobTier],
        standard_blob_tier: Optional[StandardBlobTier],
        rehydrate_priority: Optional[RehydratePriority],
        seal_destination_blob: Optional[bool],
        requires_sync: Optional[bool],
        source_authorization: Optional[str],
        encryption_scope: Optional[str],
        timeout: Optional[int],
        **kwargs: Any
    ) -> Dict[str, Union[str, datetime]]: ...
    @distributed_trace
    def abort_copy(self, copy_id: Union[str, Dict[str, Any], BlobProperties], **kwargs: Any) -> None: ...
    @distributed_trace
    def acquire_lease(
        self,
        lease_duration: int,
        lease_id: Optional[str],
        *,
        if_modified_since: Optional[datetime],
        if_unmodified_since: Optional[datetime],
        etag: Optional[str],
        match_condition: Optional[MatchConditions],
        if_tags_match_condition: Optional[str],
        timeout: Optional[int],
        **kwargs: Any
    ) -> BlobLeaseClient: ...
    @distributed_trace
    def set_standard_blob_tier(
        self,
        standard_blob_tier: Union[str, StandardBlobTier],
        *,
        rehydrate_priority: Optional[RehydratePriority],
        version_id: Optional[str],
        if_tags_match_condition: Optional[str],
        lease: Optional[Union[BlobLeaseClient, str]],
        timeout: Optional[int],
        **kwargs: Any
    ) -> None: ...
    @distributed_trace
    def stage_block(
        self,
        block_id: str,
        data: Union[bytes, str, Iterable[AnyStr], IO[AnyStr]],
        length: Optional[int],
        *,
        validate_content: Optional[bool],
        lease: Optional[Union[BlobLeaseClient, str]],
        encoding: Optional[str],
        cpk: Optional[CustomerProvidedEncryptionKey],
        encryption_scope: Optional[str],
        timeout: Optional[int],
        **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace
    def stage_block_from_url(
        self,
        block_id: str,
        source_url: str,
        source_offset: Optional[int],
        source_length: Optional[int],
        source_content_md5: Optional[Union[bytes, bytearray]],
        *,
        lease: Optional[Union[BlobLeaseClient, str]],
        cpk: Optional[CustomerProvidedEncryptionKey],
        encryption_scope: Optional[str],
        source_authorization: Optional[str],
        timeout: Optional[int],
        **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace
    def get_block_list(
        self,
        block_list_type: str,
        *,
        lease: Optional[Union[BlobLeaseClient, str]],
        if_tags_match_condition: Optional[str],
        timeout: Optional[int],
        **kwargs: Any
    ) -> Tuple[List[BlobBlock], List[BlobBlock]]: ...
    @distributed_trace
    def commit_block_list(
        self,
        block_list: List[BlobBlock],
        content_settings: Optional[ContentSettings],
        metadata: Optional[Dict[str, str]],
        *,
        tags: Optional[Dict[str, str]],
        lease: Optional[Union[BlobLeaseClient, str]],
        immutability_policy: Optional[ImmutabilityPolicy],
        legal_hold: Optional[bool],
        validate_content: Optional[bool],
        if_modified_since: Optional[datetime],
        if_unmodified_since: Optional[datetime],
        etag: Optional[str],
        match_condition: Optional[MatchConditions],
        if_tags_match_condition: Optional[str],
        standard_blob_tier: Optional[StandardBlobTier],
        cpk: Optional[CustomerProvidedEncryptionKey],
        encryption_scope: Optional[str],
        timeout: Optional[int],
        **kwargs: Any
    ) -> Dict[str, Union[str, datetime]]: ...
    @distributed_trace
    def set_premium_page_blob_tier(
        self,
        premium_page_blob_tier: PremiumPageBlobTier,
        *,
        if_tags_match_condition: Optional[str],
        lease: Optional[Union[BlobLeaseClient, str]],
        timeout: Optional[int],
        **kwargs: Any
    ) -> None: ...
    @distributed_trace
    def set_blob_tags(
        self,
        tags: Optional[Dict[str, str]],
        *,
        version_id: Optional[str],
        validate_content: Optional[bool],
        if_tags_match_condition: Optional[str],
        lease: Optional[Union[BlobLeaseClient, str]],
        timeout: Optional[int],
        **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace
    def get_blob_tags(
        self,
        *,
        version_id: Optional[str],
        if_tags_match_condition: Optional[str],
        lease: Optional[Union[BlobLeaseClient, str]],
        timeout: Optional[int],
        **kwargs: Any
    ) -> Dict[str, str]: ...
    @distributed_trace
    def get_page_ranges(
        self,
        offset: Optional[int],
        length: Optional[int],
        previous_snapshot_diff: Optional[Union[str, Dict[str, Any]]],
        *,
        lease: Optional[Union[BlobLeaseClient, str]],
        if_modified_since: Optional[datetime],
        if_unmodified_since: Optional[datetime],
        etag: Optional[str],
        match_condition: Optional[MatchConditions],
        if_tags_match_condition: Optional[str],
        timeout: Optional[int],
        **kwargs: Any
    ) -> Tuple[List[Dict[str, int]], List[Dict[str, int]]]: ...
    @distributed_trace
    def list_page_ranges(
        self,
        *,
        offset: Optional[int],
        length: Optional[int],
        previous_snapshot: Optional[Union[str, Dict[str, Any]]],
        lease: Optional[Union[BlobLeaseClient, str]],
        if_modified_since: Optional[datetime],
        if_unmodified_since: Optional[datetime],
        etag: Optional[str],
        match_condition: Optional[MatchConditions],
        if_tags_match_condition: Optional[str],
        results_per_page: Optional[int],
        timeout: Optional[int],
        **kwargs: Any
    ) -> ItemPaged[PageRange]: ...
    @distributed_trace
    def get_page_range_diff_for_managed_disk(
        self,
        previous_snapshot_url: str,
        offset: Optional[int],
        length: Optional[int],
        *,
        lease: Optional[Union[BlobLeaseClient, str]],
        if_modified_since: Optional[datetime],
        if_unmodified_since: Optional[datetime],
        etag: Optional[str],
        match_condition: Optional[MatchConditions],
        timeout: Optional[int],
        **kwargs: Any
    ) -> Tuple[List[Dict[str, int]], List[Dict[str, int]]]: ...
    @distributed_trace
    def set_sequence_number(
        self,
        sequence_number_action: Union[str, SequenceNumberAction],
        sequence_number: Optional[str],
        *,
        lease: Optional[Union[BlobLeaseClient, str]],
        if_modified_since: Optional[datetime],
        if_unmodified_since: Optional[datetime],
        etag: Optional[str],
        match_condition: Optional[MatchConditions],
        if_tags_match_condition: Optional[str],
        timeout: Optional[int],
        **kwargs: Any
    ) -> Dict[str, Union[str, datetime]]: ...
    @distributed_trace
    def resize_blob(
        self,
        size: int,
        *,
        lease: Optional[Union[BlobLeaseClient, str]],
        if_modified_since: Optional[datetime],
        if_unmodified_since: Optional[datetime],
        etag: Optional[str],
        match_condition: Optional[MatchConditions],
        if_tags_match_condition: Optional[str],
        premium_page_blob_tier: Optional[PremiumPageBlobTier],
        timeout: Optional[int],
        **kwargs: Any
    ) -> Dict[str, Union[str, datetime]]: ...
    @distributed_trace
    def upload_page(
        self,
        page: bytes,
        offset: int,
        length: int,
        *,
        lease: Optional[Union[BlobLeaseClient, str]],
        validate_content: Optional[bool],
        if_sequence_number_lte: Optional[int],
        if_sequence_number_lt: Optional[int],
        if_sequence_number_eq: Optional[int],
        if_modified_since: Optional[datetime],
        if_unmodified_since: Optional[datetime],
        etag: Optional[str],
        match_condition: Optional[MatchConditions],
        if_tags_match_condition: Optional[str],
        cpk: Optional[CustomerProvidedEncryptionKey],
        encryption_scope: Optional[str],
        encoding: Optional[str],
        timeout: Optional[int],
        **kwargs: Any
    ) -> Dict[str, Union[str, datetime]]: ...
    @distributed_trace
    def upload_pages_from_url(
        self,
        source_url: str,
        offset: int,
        length: int,
        source_offset: int,
        *,
        source_content_md5: Optional[bytes],
        source_if_modified_since: Optional[datetime],
        source_if_unmodified_since: Optional[datetime],
        source_etag: Optional[str],
        source_match_condition: Optional[MatchConditions],
        lease: Optional[Union[BlobLeaseClient, str]],
        if_sequence_number_lte: Optional[int],
        if_sequence_number_lt: Optional[int],
        if_sequence_number_eq: Optional[int],
        if_modified_since: Optional[datetime],
        if_unmodified_since: Optional[datetime],
        etag: Optional[str],
        match_condition: Optional[MatchConditions],
        if_tags_match_condition: Optional[str],
        cpk: Optional[CustomerProvidedEncryptionKey],
        encryption_scope: Optional[str],
        source_authorization: Optional[str],
        timeout: Optional[int],
        **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace
    def clear_page(
        self,
        offset: int,
        length: int,
        *,
        lease: Optional[Union[BlobLeaseClient, str]],
        if_sequence_number_lte: Optional[int],
        if_sequence_number_lt: Optional[int],
        if_sequence_number_eq: Optional[int],
        if_modified_since: Optional[datetime],
        if_unmodified_since: Optional[datetime],
        etag: Optional[str],
        match_condition: Optional[MatchConditions],
        if_tags_match_condition: Optional[str],
        cpk: Optional[CustomerProvidedEncryptionKey],
        timeout: Optional[int],
        **kwargs: Any
    ) -> Dict[str, Union[str, datetime]]: ...
    @distributed_trace
    def append_block(
        self,
        data: Union[bytes, str, Iterable[AnyStr], IO[AnyStr]],
        length: Optional[int],
        *,
        validate_content: Optional[bool],
        maxsize_condition: Optional[int],
        appendpos_condition: Optional[int],
        lease: Optional[Union[BlobLeaseClient, str]],
        if_modified_since: Optional[datetime],
        if_unmodified_since: Optional[datetime],
        etag: Optional[str],
        match_condition: Optional[MatchConditions],
        if_tags_match_condition: Optional[str],
        encoding: Optional[str],
        cpk: Optional[CustomerProvidedEncryptionKey],
        encryption_scope: Optional[str],
        timeout: Optional[int],
        **kwargs: Any
    ) -> Dict[str, Union[str, datetime, int]]: ...
    @distributed_trace
    def append_block_from_url(
        self,
        copy_source_url: str,
        source_offset: Optional[int],
        source_length: Optional[int],
        *,
        source_content_md5: Optional[bytearray],
        maxsize_condition: Optional[int],
        appendpos_condition: Optional[int],
        lease: Optional[Union[BlobLeaseClient, str]],
        if_modified_since: Optional[datetime],
        if_unmodified_since: Optional[datetime],
        etag: Optional[str],
        match_condition: Optional[MatchConditions],
        if_tags_match_condition: Optional[str],
        source_if_modified_since: Optional[datetime],
        source_if_unmodified_since: Optional[datetime],
        source_etag: Optional[str],
        source_match_condition: Optional[MatchConditions],
        cpk: Optional[CustomerProvidedEncryptionKey],
        encryption_scope: Optional[str],
        source_authorization: Optional[str],
        timeout: Optional[int],
        **kwargs: Any
    ) -> Dict[str, Union[str, datetime, int]]: ...
    @distributed_trace
    def seal_append_blob(
        self,
        *,
        appendpos_condition: Optional[int],
        lease: Optional[Union[BlobLeaseClient, str]],
        if_modified_since: Optional[datetime],
        if_unmodified_since: Optional[datetime],
        etag: Optional[str],
        match_condition: Optional[MatchConditions],
        timeout: Optional[int],
        **kwargs: Any
    ) -> Dict[str, Union[str, datetime, int]]: ...
