```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.storage.blob

    def azure.storage.blob.download_blob_from_url(
            blob_url: str, 
            output: Union[str, IO[bytes]], 
            credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]] = None, 
            *, 
            length: Optional[int] = ..., 
            max_concurrency: Optional[int] = ..., 
            offset: Optional[int] = ..., 
            overwrite: Optional[bool] = ..., 
            validate_content: Optional[bool] = ..., 
            **kwargs: Any
        ) -> None: ...


    def azure.storage.blob.generate_account_sas(
            account_name: str, 
            account_key: str, 
            resource_types: Union[ResourceTypes, str], 
            permission: Union[AccountSasPermissions, str], 
            expiry: Union[datetime, str], 
            start: Optional[Union[datetime, str]] = None, 
            ip: Optional[str] = None, 
            *, 
            encryption_scope: Optional[str] = ..., 
            protocol: Optional[str] = ..., 
            services: Union[Services, str] = Services(blob=True), 
            sts_hook: Optional[Callable[[str], None]] = ..., 
            **kwargs: Any
        ) -> str: ...


    def azure.storage.blob.generate_blob_sas(
            account_name: str, 
            container_name: str, 
            blob_name: str, 
            snapshot: Optional[str] = None, 
            account_key: Optional[str] = None, 
            user_delegation_key: Optional[UserDelegationKey] = None, 
            permission: Optional[Union[BlobSasPermissions, str]] = None, 
            expiry: Optional[Union[datetime, str]] = None, 
            start: Optional[Union[datetime, str]] = None, 
            policy_id: Optional[str] = None, 
            ip: Optional[str] = None, 
            *, 
            cache_control: Optional[str] = ..., 
            content_disposition: Optional[str] = ..., 
            content_encoding: Optional[str] = ..., 
            content_language: Optional[str] = ..., 
            content_type: Optional[str] = ..., 
            correlation_id: Optional[str] = ..., 
            encryption_scope: Optional[str] = ..., 
            is_directory: Optional[bool] = ..., 
            protocol: Optional[str] = ..., 
            request_headers: Optional[Dict[str, str]] = ..., 
            request_query_params: Optional[Dict[str, str]] = ..., 
            sts_hook: Optional[Callable[[str], None]] = ..., 
            user_delegation_oid: Optional[str] = ..., 
            version_id: Optional[str] = ..., 
            **kwargs: Any
        ) -> str: ...


    def azure.storage.blob.generate_container_sas(
            account_name: str, 
            container_name: str, 
            account_key: Optional[str] = None, 
            user_delegation_key: Optional[UserDelegationKey] = None, 
            permission: Optional[Union[ContainerSasPermissions, str]] = None, 
            expiry: Optional[Union[datetime, str]] = None, 
            start: Optional[Union[datetime, str]] = None, 
            policy_id: Optional[str] = None, 
            ip: Optional[str] = None, 
            *, 
            cache_control: Optional[str] = ..., 
            content_disposition: Optional[str] = ..., 
            content_encoding: Optional[str] = ..., 
            content_language: Optional[str] = ..., 
            content_type: Optional[str] = ..., 
            correlation_id: Optional[str] = ..., 
            encryption_scope: Optional[str] = ..., 
            protocol: Optional[str] = ..., 
            request_headers: Optional[Dict[str, str]] = ..., 
            request_query_params: Optional[Dict[str, str]] = ..., 
            sts_hook: Optional[Callable[[str], None]] = ..., 
            user_delegation_oid: Optional[str] = ..., 
            **kwargs: Any
        ) -> str: ...


    def azure.storage.blob.upload_blob_to_url(
            blob_url: str, 
            data: Union[Iterable[AnyStr], IO[AnyStr]], 
            credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]] = None, 
            *, 
            encoding: Optional[str] = ..., 
            length: Optional[int] = ..., 
            max_concurrency: Optional[int] = ..., 
            metadata: Optional[dict(str,str)] = ..., 
            overwrite: Optional[bool] = ..., 
            validate_content: Optional[bool] = ..., 
            **kwargs: Any
        ) -> Dict[str, Any]: ...


    class azure.storage.blob.AccessPolicy(GenAccessPolicy):
        expiry: Optional[Union[datetime, str]]
        permission: Optional[Union[ContainerSasPermissions, str]]
        start: Optional[Union[datetime, str]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                permission: Optional[Union[ContainerSasPermissions, str]] = None, 
                expiry: Optional[Union[str, datetime]] = None, 
                start: Optional[Union[str, datetime]] = None
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.storage.blob.AccountSasPermissions:
        add: bool = False
        create: bool = False
        delete: bool = False
        delete_previous_version: bool = False
        filter_by_tags: bool = False
        list: bool = False
        permanent_delete: bool = False
        process: bool = False
        read: bool = False
        set_immutability_policy: bool = False
        tag: bool = False
        update: bool = False
        write: bool = False

        def __init__(
                self, 
                read: bool = False, 
                write: bool = False, 
                delete: bool = False, 
                list: bool = False, 
                add: bool = False, 
                create: bool = False, 
                update: bool = False, 
                process: bool = False, 
                delete_previous_version: bool = False, 
                *, 
                filter_by_tags: Optional[bool] = ..., 
                permanent_delete: Optional[bool] = ..., 
                set_immutability_policy: Optional[bool] = ..., 
                tag: Optional[bool] = ..., 
                **kwargs
            ) -> None: ...

        def __str__(self): ...

        @classmethod
        def from_string(cls, permission: str) -> AccountSasPermissions: ...


    class azure.storage.blob.ArrowDialect(ArrowField):

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                type: ArrowType, 
                *, 
                name: Optional[str] = ..., 
                precision: Optional[int] = ..., 
                scale: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.storage.blob.ArrowType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOOL = "bool"
        DECIMAL = "decimal"
        DOUBLE = "double"
        INT64 = "int64"
        STRING = "string"
        TIMESTAMP_MS = "timestamp[ms]"


    class azure.storage.blob.BlobAnalyticsLogging(GeneratedLogging):
        delete: bool = False
        read: bool = False
        retention_policy: RetentionPolicy
        version: str = "1.0"
        write: bool = False

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                delete: Optional[bool] = ..., 
                read: Optional[bool] = ..., 
                retention_policy: Optional[RetentionPolicy] = ..., 
                version: Optional[str] = ..., 
                write: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.storage.blob.BlobBlock(DictMixin):
        block_id: str
        size: int
        state: BlockState

        def __contains__(self, key): ...

        def __delitem__(self, key): ...

        def __eq__(self, other): ...

        def __getitem__(self, key): ...

        def __init__(
                self, 
                block_id: str, 
                state: BlockState = BlockState.LATEST
            ) -> None: ...

        def __len__(self): ...

        def __ne__(self, other): ...

        def __repr__(self): ...

        def __setitem__(
                self, 
                key, 
                item
            ): ...

        def __str__(self): ...

        def get(
                self, 
                key, 
                default = None
            ): ...

        def has_key(self, k): ...

        def items(self): ...

        def keys(self): ...

        def update(
                self, 
                *args, 
                **kwargs
            ): ...

        def values(self): ...


    class azure.storage.blob.BlobClient(StorageAccountHostsMixin, StorageEncryptionMixin): implements ContextManager 
        property api_version: str    # Read-only
        property location_mode: str
        property primary_endpoint: str    # Read-only
        property primary_hostname: str    # Read-only
        property secondary_endpoint: str    # Read-only
        property secondary_hostname: Optional[str]    # Read-only
        property url: str    # Read-only

        def __init__(
                self, 
                account_url: str, 
                container_name: str, 
                blob_name: str, 
                snapshot: Optional[Union[str, Dict[str, Any]]] = None, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]] = None, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                max_block_size: Optional[int] = ..., 
                max_chunk_get_size: Optional[int] = ..., 
                max_page_size: Optional[int] = ..., 
                max_single_get_size: Optional[int] = ..., 
                max_single_put_size: Optional[int] = ..., 
                min_large_block_upload_threshold: Optional[int] = ..., 
                secondary_hostname: Optional[str] = ..., 
                use_byte_buffer: Optional[bool] = ..., 
                version_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_blob_url(
                cls, 
                blob_url: str, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]] = None, 
                snapshot: Optional[Union[str, Dict[str, Any]]] = None, 
                *, 
                audience: Optional[str] = ..., 
                version_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> Self: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                container_name: str, 
                blob_name: str, 
                snapshot: Optional[Union[str, Dict[str, Any]]] = None, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]] = None, 
                *, 
                audience: Optional[str] = ..., 
                version_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> Self: ...

        @distributed_trace
        def abort_copy(
                self, 
                copy_id: Union[str, Dict[str, Any], BlobProperties], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def acquire_lease(
                self, 
                lease_duration: int = -1, 
                lease_id: Optional[str] = None, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> BlobLeaseClient: ...

        @distributed_trace
        def append_block(
                self, 
                data: Union[bytes, Iterable[bytes], IO[bytes]], 
                length: Optional[int] = None, 
                *, 
                appendpos_condition: Optional[int] = ..., 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                encoding: Optional[str] = ..., 
                encryption_scope: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                maxsize_condition: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                validate_content: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime, int]]: ...

        @distributed_trace
        def append_block_from_url(
                self, 
                copy_source_url: str, 
                source_offset: Optional[int] = None, 
                source_length: Optional[int] = None, 
                *, 
                appendpos_condition: Optional[int] = ..., 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                encryption_scope: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                maxsize_condition: Optional[int] = ..., 
                source_authorization: Optional[str] = ..., 
                source_content_md5: Optional[bytearray] = ..., 
                source_cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                source_etag: Optional[str] = ..., 
                source_if_modified_since: Optional[datetime] = ..., 
                source_if_unmodified_since: Optional[datetime] = ..., 
                source_match_condition: Optional[MatchConditions] = ..., 
                source_token_intent: Literal[backup] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime, int]]: ...

        @distributed_trace
        def clear_page(
                self, 
                offset: int, 
                length: int, 
                *, 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_sequence_number_eq: Optional[int] = ..., 
                if_sequence_number_lt: Optional[int] = ..., 
                if_sequence_number_lte: Optional[int] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime]]: ...

        def close(self) -> None: ...

        @distributed_trace
        def commit_block_list(
                self, 
                block_list: List[BlobBlock], 
                content_settings: Optional[ContentSettings] = None, 
                metadata: Optional[Dict[str, str]] = None, 
                *, 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                encryption_scope: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                immutability_policy: Optional[ImmutabilityPolicy] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                legal_hold: Optional[bool] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                standard_blob_tier: Optional[StandardBlobTier] = ..., 
                tags: dict(str, str) = ..., 
                timeout: Optional[int] = ..., 
                validate_content: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime]]: ...

        @distributed_trace
        def create_append_blob(
                self, 
                content_settings: Optional[ContentSettings] = None, 
                metadata: Optional[Dict[str, str]] = None, 
                *, 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                encryption_scope: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                immutability_policy: Optional[ImmutabilityPolicy] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                legal_hold: Optional[bool] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                tags: dict(str, str) = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime]]: ...

        @distributed_trace
        def create_page_blob(
                self, 
                size: int, 
                content_settings: Optional[ContentSettings] = None, 
                metadata: Optional[Dict[str, str]] = None, 
                premium_page_blob_tier: Optional[Union[str, PremiumPageBlobTier]] = None, 
                *, 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                encryption_scope: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                immutability_policy: Optional[ImmutabilityPolicy] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                legal_hold: Optional[bool] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                sequence_number: Optional[int] = ..., 
                tags: dict(str, str) = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime]]: ...

        @distributed_trace
        def create_snapshot(
                self, 
                metadata: Optional[Dict[str, str]] = None, 
                *, 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                encryption_scope: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime]]: ...

        @distributed_trace
        def delete_blob(
                self, 
                delete_snapshots: Optional[str] = None, 
                *, 
                access_tier_if_modified_since: Optional[datetime] = ..., 
                access_tier_if_unmodified_since: Optional[datetime] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                version_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_immutability_policy(
                self, 
                *, 
                timeout: Optional[int] = ..., 
                version_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def download_blob(
                self, 
                offset: Optional[int] = None, 
                length: Optional[int] = None, 
                *, 
                encoding: str, 
                **kwargs: Any
            ) -> StorageStreamDownloader[str]: ...

        @overload
        def download_blob(
                self, 
                offset: Optional[int] = None, 
                length: Optional[int] = None, 
                *, 
                encoding: None = ..., 
                **kwargs: Any
            ) -> StorageStreamDownloader[bytes]: ...

        @distributed_trace
        def exists(
                self, 
                *, 
                timeout: Optional[int] = ..., 
                version_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> bool: ...

        @distributed_trace
        def get_account_information(self, **kwargs: Any) -> Dict[str, str]: ...

        @distributed_trace
        def get_blob_properties(
                self, 
                *, 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                version_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> BlobProperties: ...

        @distributed_trace
        def get_blob_tags(
                self, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                version_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> Dict[str, str]: ...

        @distributed_trace
        def get_block_list(
                self, 
                block_list_type: str = "committed", 
                *, 
                if_tags_match_condition: Optional[str] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Tuple[List[BlobBlock], List[BlobBlock]]: ...

        @distributed_trace
        def get_page_range_diff_for_managed_disk(
                self, 
                previous_snapshot_url: str, 
                offset: Optional[int] = None, 
                length: Optional[int] = None, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Tuple[List[Dict[str, int]], List[Dict[str, int]]]: ...

        @distributed_trace
        def get_page_ranges(
                self, 
                offset: Optional[int] = None, 
                length: Optional[int] = None, 
                previous_snapshot_diff: Optional[Union[str, Dict[str, Any]]] = None, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Tuple[List[Dict[str, int]], List[Dict[str, int]]]: ...

        @distributed_trace
        def list_page_ranges(
                self, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                length: Optional[int] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                offset: Optional[int] = ..., 
                previous_snapshot: Optional[Union[str, Dict[str, Any]]] = ..., 
                results_per_page: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PageRange]: ...

        @distributed_trace
        def query_blob(
                self, 
                query_expression: str, 
                *, 
                blob_format: Union[DelimitedTextDialect, DelimitedJsonDialect] = ..., 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                on_error: Optional[Callable[BlobQueryError]] = ..., 
                output_format: Union[DelimitedTextDialect, DelimitedJsonDialect] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> BlobQueryReader: ...

        @distributed_trace
        def resize_blob(
                self, 
                size: int, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                premium_page_blob_tier: Optional[PremiumPageBlobTier] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime]]: ...

        @distributed_trace
        def seal_append_blob(
                self, 
                *, 
                appendpos_condition: Optional[int] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime, int]]: ...

        @distributed_trace
        def set_blob_metadata(
                self, 
                metadata: Optional[Dict[str, str]] = None, 
                *, 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                encryption_scope: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime]]: ...

        @distributed_trace
        def set_blob_tags(
                self, 
                tags: Optional[Dict[str, str]] = None, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                validate_content: Optional[bool] = ..., 
                version_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace
        def set_http_headers(
                self, 
                content_settings: Optional[ContentSettings] = None, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace
        def set_immutability_policy(
                self, 
                immutability_policy: ImmutabilityPolicy, 
                *, 
                timeout: Optional[int] = ..., 
                version_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> Dict[str, str]: ...

        @distributed_trace
        def set_legal_hold(
                self, 
                legal_hold: bool = False, 
                *, 
                timeout: Optional[int] = ..., 
                version_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime, bool]]: ...

        @distributed_trace
        def set_premium_page_blob_tier(
                self, 
                premium_page_blob_tier: PremiumPageBlobTier, 
                *, 
                if_tags_match_condition: Optional[str] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def set_sequence_number(
                self, 
                sequence_number_action: Union[str, SequenceNumberAction], 
                sequence_number: Optional[str] = None, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime]]: ...

        @distributed_trace
        def set_standard_blob_tier(
                self, 
                standard_blob_tier: Union[str, StandardBlobTier], 
                *, 
                if_tags_match_condition: Optional[str] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                rehydrate_priority: Optional[RehydratePriority] = ..., 
                timeout: Optional[int] = ..., 
                version_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def stage_block(
                self, 
                block_id: str, 
                data: Union[bytes, Iterable[bytes], IO[bytes]], 
                length: Optional[int] = None, 
                *, 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                encoding: Optional[str] = ..., 
                encryption_scope: Optional[str] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                timeout: Optional[int] = ..., 
                validate_content: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace
        def stage_block_from_url(
                self, 
                block_id: str, 
                source_url: str, 
                source_offset: Optional[int] = None, 
                source_length: Optional[int] = None, 
                source_content_md5: Optional[Union[bytes, bytearray]] = None, 
                *, 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                encryption_scope: Optional[str] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                source_authorization: Optional[str] = ..., 
                source_cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                source_token_intent: Literal[backup] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace
        def start_copy_from_url(
                self, 
                source_url: str, 
                metadata: Optional[Dict[str, str]] = None, 
                incremental_copy: bool = False, 
                *, 
                destination_lease: Union[BlobLeaseClient, str] = ..., 
                encryption_scope: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                immutability_policy: Optional[ImmutabilityPolicy] = ..., 
                legal_hold: Optional[bool] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                premium_page_blob_tier: Optional[PremiumPageBlobTier] = ..., 
                rehydrate_priority: Optional[RehydratePriority] = ..., 
                requires_sync: Optional[bool] = ..., 
                seal_destination_blob: Optional[bool] = ..., 
                source_authorization: Optional[str] = ..., 
                source_etag: Optional[str] = ..., 
                source_if_modified_since: Optional[datetime] = ..., 
                source_if_unmodified_since: Optional[datetime] = ..., 
                source_lease: Union[BlobLeaseClient, str] = ..., 
                source_match_condition: Optional[MatchConditions] = ..., 
                source_token_intent: Literal[backup] = ..., 
                standard_blob_tier: Optional[StandardBlobTier] = ..., 
                tags: Union[dict(str, str), Literal[COPY]] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime]]: ...

        @distributed_trace
        def undelete_blob(
                self, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def upload_blob(
                self, 
                data: Union[bytes, str, Iterable[AnyStr], IO[bytes]], 
                blob_type: Union[str, BlobType] = BlobType.BLOCKBLOB, 
                length: Optional[int] = None, 
                metadata: Optional[Dict[str, str]] = None, 
                *, 
                content_settings: Optional[ContentSettings] = ..., 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                encoding: Optional[str] = ..., 
                encryption_scope: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                immutability_policy: Optional[ImmutabilityPolicy] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                legal_hold: Optional[bool] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                max_concurrency: Optional[int] = ..., 
                maxsize_condition: Optional[int] = ..., 
                overwrite: Optional[bool] = ..., 
                premium_page_blob_tier: Optional[PremiumPageBlobTier] = ..., 
                progress_hook: Callable[[int, Optional[int]], None] = ..., 
                standard_blob_tier: Optional[StandardBlobTier] = ..., 
                tags: dict(str, str) = ..., 
                timeout: Optional[int] = ..., 
                validate_content: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace
        def upload_blob_from_url(
                self, 
                source_url: str, 
                *, 
                content_settings: Optional[ContentSettings] = ..., 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                destination_lease: Union[BlobLeaseClient, str] = ..., 
                encryption_scope: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                include_source_blob_properties: Optional[bool] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                metadata: Optional[Dict[str, str]] = ..., 
                overwrite: Optional[bool] = ..., 
                source_authorization: Optional[str] = ..., 
                source_content_md5: Optional[bytearray] = ..., 
                source_cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                source_etag: Optional[str] = ..., 
                source_if_modified_since: Optional[datetime] = ..., 
                source_if_unmodified_since: Optional[datetime] = ..., 
                source_match_condition: Optional[MatchConditions] = ..., 
                source_token_intent: Literal[backup] = ..., 
                standard_blob_tier: Optional[StandardBlobTier] = ..., 
                tags: dict(str, str) = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace
        def upload_page(
                self, 
                page: bytes, 
                offset: int, 
                length: int, 
                *, 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                encoding: Optional[str] = ..., 
                encryption_scope: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_sequence_number_eq: Optional[int] = ..., 
                if_sequence_number_lt: Optional[int] = ..., 
                if_sequence_number_lte: Optional[int] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                validate_content: Optional[bool] = ..., 
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
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                encryption_scope: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_sequence_number_eq: Optional[int] = ..., 
                if_sequence_number_lt: Optional[int] = ..., 
                if_sequence_number_lte: Optional[int] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                source_authorization: Optional[str] = ..., 
                source_content_md5: Optional[bytes] = ..., 
                source_cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                source_etag: Optional[str] = ..., 
                source_if_modified_since: Optional[datetime] = ..., 
                source_if_unmodified_since: Optional[datetime] = ..., 
                source_match_condition: Optional[MatchConditions] = ..., 
                source_token_intent: Literal[backup] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...


    class azure.storage.blob.BlobImmutabilityPolicyMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOCKED = "Locked"
        MUTABLE = "Mutable"
        UNLOCKED = "Unlocked"


    class azure.storage.blob.BlobLeaseClient: implements ContextManager 
        etag: Optional[str]
        id: str
        last_modified: Optional[datetime]

        def __init__(
                self, 
                client: Union[BlobClient, ContainerClient], 
                lease_id: Optional[str] = None
            ) -> None: ...

        @distributed_trace
        def acquire(
                self, 
                lease_duration: int = -1, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def break_lease(
                self, 
                lease_break_period: Optional[int] = None, 
                *, 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> int: ...

        @distributed_trace
        def change(
                self, 
                proposed_lease_id: str, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def release(
                self, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def renew(
                self, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.storage.blob.BlobPrefix(ItemPaged, DictMixin):
        command: Callable
        container: str
        current_page: Optional[List[BlobProperties]]
        delimiter: str
        location_mode: str
        marker: Optional[str]
        name: str
        next_marker: Optional[str]
        prefix: str
        results_per_page: Optional[int]
        service_endpoint: Optional[str]

        def __contains__(self, key): ...

        def __delitem__(self, key): ...

        def __eq__(self, other): ...

        def __getitem__(self, key): ...

        def __init__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def __len__(self): ...

        def __ne__(self, other): ...

        def __setitem__(
                self, 
                key, 
                item
            ): ...

        def __str__(self): ...

        def get(
                self, 
                key, 
                default = None
            ): ...

        def has_key(self, k): ...

        def items(self): ...

        def keys(self): ...

        def update(
                self, 
                *args, 
                **kwargs
            ): ...

        def values(self): ...


    class azure.storage.blob.BlobProperties(DictMixin):
        append_blob_committed_block_count: Optional[int]
        archive_status: Optional[str]
        blob_tier: Optional[StandardBlobTier]
        blob_tier_change_time: Optional[datetime]
        blob_tier_inferred: Optional[bool]
        blob_type: BlobType
        container: str
        content_range: Optional[str]
        content_settings: ContentSettings
        copy: CopyProperties
        creation_time: datetime
        deleted: Optional[bool]
        deleted_time: Optional[datetime]
        encryption_key_sha256: Optional[str]
        encryption_scope: Optional[str]
        etag: str
        has_legal_hold: Optional[bool]
        has_versions_only: Optional[bool]
        immutability_policy: ImmutabilityPolicy
        is_append_blob_sealed: Optional[bool]
        last_accessed_on: Optional[datetime]
        last_modified: datetime
        lease: LeaseProperties
        metadata: Dict[str, str]
        name: str
        object_replication_destination_policy: Optional[str]
        object_replication_source_properties: Optional[List[ObjectReplicationPolicy]]
        page_blob_sequence_number: Optional[int]
        rehydrate_priority: Optional[str]
        remaining_retention_days: Optional[int]
        request_server_encrypted: Optional[bool]
        server_encrypted: bool
        size: int
        smart_access_tier: Optional[str]
        snapshot: Optional[str]
        tag_count: Optional[int]
        tags: Optional[Dict[str, str]]

        def __contains__(self, key): ...

        def __delitem__(self, key): ...

        def __eq__(self, other): ...

        def __getitem__(self, key): ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __len__(self): ...

        def __ne__(self, other): ...

        def __repr__(self): ...

        def __setitem__(
                self, 
                key, 
                item
            ): ...

        def __str__(self): ...

        def get(
                self, 
                key, 
                default = None
            ): ...

        def has_key(self, k): ...

        def items(self): ...

        def keys(self): ...

        def update(
                self, 
                *args, 
                **kwargs
            ): ...

        def values(self): ...


    class azure.storage.blob.BlobQueryError:
        description: Optional[str]
        error: Optional[str]
        is_fatal: bool
        position: Optional[int]

        def __init__(
                self, 
                error: Optional[str] = None, 
                is_fatal: bool = False, 
                description: Optional[str] = None, 
                position: Optional[int] = None
            ) -> None: ...


    class azure.storage.blob.BlobQueryReader:
        container: str
        name: str
        record_delimiter: str
        response_headers: Dict[str, Any]

        def __init__(
                self, 
                name: str = None, 
                container: str = None, 
                errors: Any = None, 
                record_delimiter: str = "
", 
                encoding: Optional[str] = None, 
                headers: Dict[str, Any] = None, 
                response: Any = None, 
                error_cls: Type[BlobQueryError] = None
            ) -> None: ...

        def __len__(self) -> int: ...

        def readall(self) -> bytes: ...

        def readinto(self, stream: IO) -> None: ...

        def records(self) -> Iterable[bytes]: ...


    class azure.storage.blob.BlobSasPermissions:
        add: Optional[bool]
        create: Optional[bool]
        delete: bool = False
        delete_previous_version: bool = False
        execute: Optional[bool]
        move: Optional[bool]
        permanent_delete: Optional[bool]
        read: bool = False
        set_immutability_policy: Optional[bool]
        tag: bool = False
        write: bool = False

        def __init__(
                self, 
                read: bool = False, 
                add: bool = False, 
                create: bool = False, 
                write: bool = False, 
                delete: bool = False, 
                delete_previous_version: bool = False, 
                tag: bool = False, 
                *, 
                execute: Optional[bool] = ..., 
                move: Optional[bool] = ..., 
                permanent_delete: Optional[bool] = ..., 
                set_immutability_policy: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __str__(self): ...

        @classmethod
        def from_string(cls, permission: str) -> BlobSasPermissions: ...


    class azure.storage.blob.BlobServiceClient(StorageAccountHostsMixin, StorageEncryptionMixin): implements ContextManager 
        property api_version: str    # Read-only
        property location_mode: str
        property primary_endpoint: str    # Read-only
        property primary_hostname: str    # Read-only
        property secondary_endpoint: str    # Read-only
        property secondary_hostname: Optional[str]    # Read-only
        property url: str    # Read-only

        def __init__(
                self, 
                account_url: str, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]] = None, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                max_block_size: Optional[int] = ..., 
                max_chunk_get_size: Optional[int] = ..., 
                max_page_size: Optional[int] = ..., 
                max_single_get_size: Optional[int] = ..., 
                max_single_put_size: Optional[int] = ..., 
                min_large_block_upload_threshold: Optional[int] = ..., 
                secondary_hostname: Optional[str] = ..., 
                use_byte_buffer: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]] = None, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                max_block_size: Optional[int] = ..., 
                max_chunk_get_size: Optional[int] = ..., 
                max_page_size: Optional[int] = ..., 
                max_single_get_size: Optional[int] = ..., 
                max_single_put_size: Optional[int] = ..., 
                min_large_block_upload_threshold: Optional[int] = ..., 
                secondary_hostname: Optional[str] = ..., 
                use_byte_buffer: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Self: ...

        def close(self) -> None: ...

        @distributed_trace
        def create_container(
                self, 
                name: str, 
                metadata: Optional[Dict[str, str]] = None, 
                public_access: Optional[Union[PublicAccess, str]] = None, 
                *, 
                container_encryption_scope: Union[dict, ContainerEncryptionScope] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ContainerClient: ...

        @distributed_trace
        def delete_container(
                self, 
                container: Union[ContainerProperties, str], 
                lease: Optional[Union[BlobLeaseClient, str]] = None, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def find_blobs_by_tags(
                self, 
                filter_expression: str, 
                *, 
                results_per_page: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[FilteredBlob]: ...

        @distributed_trace
        def get_account_information(self, **kwargs: Any) -> Dict[str, str]: ...

        def get_blob_client(
                self, 
                container: Union[ContainerProperties, str], 
                blob: str, 
                snapshot: Optional[Union[Dict[str, Any], str]] = None, 
                *, 
                version_id: Optional[str] = ...
            ) -> BlobClient: ...

        def get_container_client(self, container: Union[ContainerProperties, str]) -> ContainerClient: ...

        @distributed_trace
        def get_service_properties(
                self, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace
        def get_service_stats(
                self, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace
        def get_user_delegation_key(
                self, 
                key_start_time: datetime, 
                key_expiry_time: datetime, 
                *, 
                delegated_user_tid: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> UserDelegationKey: ...

        @distributed_trace
        def list_containers(
                self, 
                name_starts_with: Optional[str] = None, 
                include_metadata: bool = False, 
                *, 
                include_deleted: Optional[bool] = ..., 
                include_system: Optional[bool] = ..., 
                results_per_page: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ContainerProperties]: ...

        @distributed_trace
        def set_service_properties(
                self, 
                analytics_logging: Optional[BlobAnalyticsLogging] = None, 
                hour_metrics: Optional[Metrics] = None, 
                minute_metrics: Optional[Metrics] = None, 
                cors: Optional[List[CorsRule]] = None, 
                target_version: Optional[str] = None, 
                delete_retention_policy: Optional[RetentionPolicy] = None, 
                static_website: Optional[StaticWebsite] = None, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def undelete_container(
                self, 
                deleted_container_name: str, 
                deleted_container_version: str, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ContainerClient: ...


    class azure.storage.blob.BlobType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPENDBLOB = "AppendBlob"
        BLOCKBLOB = "BlockBlob"
        PAGEBLOB = "PageBlob"


    class azure.storage.blob.BlockState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMMITTED = "Committed"
        LATEST = "Latest"
        UNCOMMITTED = "Uncommitted"


    class azure.storage.blob.ContainerClient(StorageAccountHostsMixin, StorageEncryptionMixin): implements ContextManager 
        property api_version: str    # Read-only
        property location_mode: str
        property primary_endpoint: str    # Read-only
        property primary_hostname: str    # Read-only
        property secondary_endpoint: str    # Read-only
        property secondary_hostname: Optional[str]    # Read-only
        property url: str    # Read-only

        def __init__(
                self, 
                account_url: str, 
                container_name: str, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]] = None, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                max_block_size: Optional[int] = ..., 
                max_chunk_get_size: Optional[int] = ..., 
                max_page_size: Optional[int] = ..., 
                max_single_get_size: Optional[int] = ..., 
                max_single_put_size: Optional[int] = ..., 
                min_large_block_upload_threshold: Optional[int] = ..., 
                secondary_hostname: Optional[str] = ..., 
                use_byte_buffer: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                container_name: str, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]] = None, 
                *, 
                audience: Optional[str] = ..., 
                **kwargs: Any
            ) -> Self: ...

        @classmethod
        def from_container_url(
                cls, 
                container_url: str, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]] = None, 
                *, 
                audience: Optional[str] = ..., 
                **kwargs: Any
            ) -> Self: ...

        @distributed_trace
        def acquire_lease(
                self, 
                lease_duration: int = -1, 
                lease_id: Optional[str] = None, 
                *, 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> BlobLeaseClient: ...

        def close(self) -> None: ...

        @distributed_trace
        def create_container(
                self, 
                metadata: Optional[Dict[str, str]] = None, 
                public_access: Optional[Union[PublicAccess, str]] = None, 
                *, 
                container_encryption_scope: Union[dict, ContainerEncryptionScope] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime]]: ...

        @distributed_trace
        def delete_blob(
                self, 
                blob: str, 
                delete_snapshots: Optional[str] = None, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                version_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_blobs(
                self, 
                *blobs: Union[str, Dict[str, Any], BlobProperties], 
                *, 
                delete_snapshots: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                raise_on_any_failure: Optional[bool] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Iterator[HttpResponse]: ...

        @distributed_trace
        def delete_container(
                self, 
                *, 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def download_blob(
                self, 
                blob: str, 
                offset: Optional[int] = None, 
                length: Optional[int] = None, 
                *, 
                encoding: str, 
                **kwargs: Any
            ) -> StorageStreamDownloader[str]: ...

        @overload
        def download_blob(
                self, 
                blob: str, 
                offset: Optional[int] = None, 
                length: Optional[int] = None, 
                *, 
                encoding: None = ..., 
                **kwargs: Any
            ) -> StorageStreamDownloader[bytes]: ...

        @distributed_trace
        def exists(self, **kwargs: Any) -> bool: ...

        @distributed_trace
        def find_blobs_by_tags(
                self, 
                filter_expression: str, 
                *, 
                results_per_page: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[FilteredBlob]: ...

        @distributed_trace
        def get_account_information(self, **kwargs: Any) -> Dict[str, str]: ...

        def get_blob_client(
                self, 
                blob: str, 
                snapshot: Optional[str] = None, 
                *, 
                version_id: Optional[str] = ...
            ) -> BlobClient: ...

        @distributed_trace
        def get_container_access_policy(
                self, 
                *, 
                lease: Union[BlobLeaseClient, str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace
        def get_container_properties(
                self, 
                *, 
                lease: Union[BlobLeaseClient, str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ContainerProperties: ...

        @distributed_trace
        def list_blob_names(
                self, 
                *, 
                name_starts_with: Optional[str] = ..., 
                results_per_page: Optional[int] = ..., 
                start_from: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[str]: ...

        @distributed_trace
        def list_blobs(
                self, 
                name_starts_with: Optional[str] = None, 
                include: Optional[Union[str, List[str]]] = None, 
                *, 
                results_per_page: Optional[int] = ..., 
                start_from: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BlobProperties]: ...

        @distributed_trace
        def set_container_access_policy(
                self, 
                signed_identifiers: Dict[str, AccessPolicy], 
                public_access: Optional[Union[str, PublicAccess]] = None, 
                *, 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime]]: ...

        @distributed_trace
        def set_container_metadata(
                self, 
                metadata: Optional[Dict[str, str]] = None, 
                *, 
                if_modified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime]]: ...

        @distributed_trace
        def set_premium_page_blob_tier_blobs(
                self, 
                premium_page_blob_tier: Optional[Union[str, PremiumPageBlobTier]], 
                *blobs: Union[str, Dict[str, Any], BlobProperties], 
                *, 
                raise_on_any_failure: Optional[bool] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Iterator[HttpResponse]: ...

        @distributed_trace
        def set_standard_blob_tier_blobs(
                self, 
                standard_blob_tier: Optional[Union[str, StandardBlobTier]], 
                *blobs: Union[str, Dict[str, Any], BlobProperties], 
                *, 
                if_tags_match_condition: Optional[str] = ..., 
                raise_on_any_failure: Optional[bool] = ..., 
                rehydrate_priority: Optional[RehydratePriority] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Iterator[HttpResponse]: ...

        @distributed_trace
        def upload_blob(
                self, 
                name: str, 
                data: Union[bytes, str, Iterable[AnyStr], IO[AnyStr]], 
                blob_type: Union[str, BlobType] = BlobType.BLOCKBLOB, 
                length: Optional[int] = None, 
                metadata: Optional[Dict[str, str]] = None, 
                *, 
                content_settings: Optional[ContentSettings] = ..., 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                encoding: Optional[str] = ..., 
                encryption_scope: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                max_concurrency: Optional[int] = ..., 
                maxsize_condition: Optional[int] = ..., 
                overwrite: Optional[bool] = ..., 
                premium_page_blob_tier: Optional[PremiumPageBlobTier] = ..., 
                progress_hook: Callable[[int, Optional[int]], None] = ..., 
                standard_blob_tier: Optional[StandardBlobTier] = ..., 
                timeout: Optional[int] = ..., 
                validate_content: Optional[bool] = ..., 
                **kwargs
            ) -> BlobClient: ...

        @distributed_trace
        def walk_blobs(
                self, 
                name_starts_with: Optional[str] = None, 
                include: Optional[Union[List[str], str]] = None, 
                delimiter: str = "/", 
                *, 
                start_from: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Union[BlobProperties, BlobPrefix]]: ...


    class azure.storage.blob.ContainerEncryptionScope:
        default_encryption_scope: str
        prevent_encryption_scope_override: bool

        def __init__(
                self, 
                default_encryption_scope: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.storage.blob.ContainerProperties(DictMixin):
        deleted: Optional[bool]
        encryption_scope: Optional[ContainerEncryptionScope]
        etag: str
        has_immutability_policy: bool
        has_legal_hold: bool
        immutable_storage_with_versioning_enabled: bool
        last_modified: datetime
        lease: LeaseProperties
        metadata: Dict[str, Any]
        name: str
        public_access: Optional[str]
        version: Optional[str]

        def __contains__(self, key): ...

        def __delitem__(self, key): ...

        def __eq__(self, other): ...

        def __getitem__(self, key): ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __len__(self): ...

        def __ne__(self, other): ...

        def __repr__(self): ...

        def __setitem__(
                self, 
                key, 
                item
            ): ...

        def __str__(self): ...

        def get(
                self, 
                key, 
                default = None
            ): ...

        def has_key(self, k): ...

        def items(self): ...

        def keys(self): ...

        def update(
                self, 
                *args, 
                **kwargs
            ): ...

        def values(self): ...


    class azure.storage.blob.ContainerSasPermissions:
        add: Optional[bool]
        create: Optional[bool]
        delete: bool = False
        delete_previous_version: bool = False
        execute: Optional[bool]
        list: bool = False
        move: Optional[bool]
        permanent_delete: Optional[bool]
        read: bool = False
        set_immutability_policy: Optional[bool]
        tag: bool = False
        write: bool = False

        def __init__(
                self, 
                read: bool = False, 
                write: bool = False, 
                delete: bool = False, 
                list: bool = False, 
                delete_previous_version: bool = False, 
                tag: bool = False, 
                *, 
                add: Optional[bool] = ..., 
                create: Optional[bool] = ..., 
                execute: Optional[bool] = ..., 
                filter_by_tags: Optional[bool] = ..., 
                move: Optional[bool] = ..., 
                permanent_delete: Optional[bool] = ..., 
                set_immutability_policy: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __str__(self): ...

        @classmethod
        def from_string(cls, permission: str) -> ContainerSasPermissions: ...


    class azure.storage.blob.ContentSettings(DictMixin):
        cache_control: Optional[str]
        content_disposition: Optional[str]
        content_encoding: Optional[str]
        content_language: Optional[str]
        content_md5: Optional[bytearray]
        content_type: Optional[str]

        def __contains__(self, key): ...

        def __delitem__(self, key): ...

        def __eq__(self, other): ...

        def __getitem__(self, key): ...

        def __init__(
                self, 
                content_type: Optional[str] = None, 
                content_encoding: Optional[str] = None, 
                content_language: Optional[str] = None, 
                content_disposition: Optional[str] = None, 
                cache_control: Optional[str] = None, 
                content_md5: Optional[bytearray] = None, 
                **kwargs: Any
            ) -> None: ...

        def __len__(self): ...

        def __ne__(self, other): ...

        def __repr__(self): ...

        def __setitem__(
                self, 
                key, 
                item
            ): ...

        def __str__(self): ...

        def get(
                self, 
                key, 
                default = None
            ): ...

        def has_key(self, k): ...

        def items(self): ...

        def keys(self): ...

        def update(
                self, 
                *args, 
                **kwargs
            ): ...

        def values(self): ...


    class azure.storage.blob.CopyProperties(DictMixin):
        completion_time: Optional[datetime]
        destination_snapshot: Optional[datetime]
        id: Optional[str]
        incremental_copy: Optional[bool]
        progress: Optional[str]
        source: Optional[str]
        status: Optional[str]
        status_description: Optional[str]

        def __contains__(self, key): ...

        def __delitem__(self, key): ...

        def __eq__(self, other): ...

        def __getitem__(self, key): ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __len__(self): ...

        def __ne__(self, other): ...

        def __repr__(self): ...

        def __setitem__(
                self, 
                key, 
                item
            ): ...

        def __str__(self): ...

        def get(
                self, 
                key, 
                default = None
            ): ...

        def has_key(self, k): ...

        def items(self): ...

        def keys(self): ...

        def update(
                self, 
                *args, 
                **kwargs
            ): ...

        def values(self): ...


    class azure.storage.blob.CorsRule(GeneratedCorsRule):
        allowed_headers: str
        allowed_methods: str
        allowed_origins: str
        exposed_headers: str
        max_age_in_seconds: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                allowed_origins: List[str], 
                allowed_methods: List[str], 
                *, 
                allowed_headers: Optional[list(str)] = ..., 
                exposed_headers: Optional[list(str)] = ..., 
                max_age_in_seconds: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.storage.blob.CustomerProvidedEncryptionKey:
        algorithm: str
        key_hash: str
        key_value: str

        def __init__(
                self, 
                key_value: str, 
                key_hash: str
            ) -> None: ...


    class azure.storage.blob.DelimitedJsonDialect(DictMixin):

        def __contains__(self, key): ...

        def __delitem__(self, key): ...

        def __eq__(self, other): ...

        def __getitem__(self, key): ...

        def __init__(
                self, 
                *, 
                delimiter: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __len__(self): ...

        def __ne__(self, other): ...

        def __repr__(self): ...

        def __setitem__(
                self, 
                key, 
                item
            ): ...

        def __str__(self): ...

        def get(
                self, 
                key, 
                default = None
            ): ...

        def has_key(self, k): ...

        def items(self): ...

        def keys(self): ...

        def update(
                self, 
                *args, 
                **kwargs
            ): ...

        def values(self): ...


    class azure.storage.blob.DelimitedTextDialect(DictMixin):

        def __contains__(self, key): ...

        def __delitem__(self, key): ...

        def __eq__(self, other): ...

        def __getitem__(self, key): ...

        def __init__(
                self, 
                *, 
                delimiter: Optional[str] = ..., 
                escapechar: Optional[str] = ..., 
                has_header: Optional[bool] = ..., 
                lineterminator: Optional[str] = ..., 
                quotechar: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __len__(self): ...

        def __ne__(self, other): ...

        def __repr__(self): ...

        def __setitem__(
                self, 
                key, 
                item
            ): ...

        def __str__(self): ...

        def get(
                self, 
                key, 
                default = None
            ): ...

        def has_key(self, k): ...

        def items(self): ...

        def keys(self): ...

        def update(
                self, 
                *args, 
                **kwargs
            ): ...

        def values(self): ...


    class azure.storage.blob.ExponentialRetry(StorageRetryPolicy):
        increment_base: int
        initial_backoff: int
        random_jitter_range: int

        def __init__(
                self, 
                initial_backoff: int = 15, 
                increment_base: int = 3, 
                retry_total: int = 3, 
                retry_to_secondary: bool = False, 
                random_jitter_range: int = 3, 
                **kwargs: Any
            ) -> None: ...

        def configure_retries(self, request: PipelineRequest) -> Dict[str, Any]: ...

        def get_backoff_time(self, settings: Dict[str, Any]) -> float: ...

        def increment(
                self, 
                settings: Dict[str, Any], 
                request: PipelineRequest, 
                response: Optional[PipelineResponse] = None, 
                error: Optional[AzureError] = None
            ) -> bool: ...

        def send(self, request: PipelineRequest) -> PipelineResponse: ...

        def sleep(
                self, 
                settings, 
                transport: AsyncioBaseTransport or
            ): ...


    class azure.storage.blob.FilteredBlob(DictMixin):
        container_name: Optional[str]
        name: str
        tags: Optional[Dict[str, str]]

        def __contains__(self, key): ...

        def __delitem__(self, key): ...

        def __eq__(self, other): ...

        def __getitem__(self, key): ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __len__(self): ...

        def __ne__(self, other): ...

        def __repr__(self): ...

        def __setitem__(
                self, 
                key, 
                item
            ): ...

        def __str__(self): ...

        def get(
                self, 
                key, 
                default = None
            ): ...

        def has_key(self, k): ...

        def items(self): ...

        def keys(self): ...

        def update(
                self, 
                *args, 
                **kwargs
            ): ...

        def values(self): ...


    class azure.storage.blob.ImmutabilityPolicy(DictMixin):
        expiry_time: Optional[datetime]
        policy_mode: Optional[str]

        def __contains__(self, key): ...

        def __delitem__(self, key): ...

        def __eq__(self, other): ...

        def __getitem__(self, key): ...

        def __init__(
                self, 
                *, 
                expiry_time: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __len__(self): ...

        def __ne__(self, other): ...

        def __repr__(self): ...

        def __setitem__(
                self, 
                key, 
                item
            ): ...

        def __str__(self): ...

        def get(
                self, 
                key, 
                default = None
            ): ...

        def has_key(self, k): ...

        def items(self): ...

        def keys(self): ...

        def update(
                self, 
                *args, 
                **kwargs
            ): ...

        def values(self): ...


    class azure.storage.blob.LeaseProperties(DictMixin):
        duration: Optional[str]
        state: str
        status: str

        def __contains__(self, key): ...

        def __delitem__(self, key): ...

        def __eq__(self, other): ...

        def __getitem__(self, key): ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __len__(self): ...

        def __ne__(self, other): ...

        def __repr__(self): ...

        def __setitem__(
                self, 
                key, 
                item
            ): ...

        def __str__(self): ...

        def get(
                self, 
                key, 
                default = None
            ): ...

        def has_key(self, k): ...

        def items(self): ...

        def keys(self): ...

        def update(
                self, 
                *args, 
                **kwargs
            ): ...

        def values(self): ...


    class azure.storage.blob.LinearRetry(StorageRetryPolicy):
        initial_backoff: int
        random_jitter_range: int

        def __init__(
                self, 
                backoff: int = 15, 
                retry_total: int = 3, 
                retry_to_secondary: bool = False, 
                random_jitter_range: int = 3, 
                **kwargs: Any
            ) -> None: ...

        def configure_retries(self, request: PipelineRequest) -> Dict[str, Any]: ...

        def get_backoff_time(self, settings: Dict[str, Any]) -> float: ...

        def increment(
                self, 
                settings: Dict[str, Any], 
                request: PipelineRequest, 
                response: Optional[PipelineResponse] = None, 
                error: Optional[AzureError] = None
            ) -> bool: ...

        def send(self, request: PipelineRequest) -> PipelineResponse: ...

        def sleep(
                self, 
                settings, 
                transport: AsyncioBaseTransport or
            ): ...


    class azure.storage.blob.LocationMode:
        PRIMARY = primary
        SECONDARY = secondary


    class azure.storage.blob.Metrics(GeneratedMetrics):
        enabled: bool = False
        include_apis: Optional[bool]
        retention_policy: RetentionPolicy
        version: str = "1.0"

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                include_apis: Optional[bool] = ..., 
                retention_policy: Optional[RetentionPolicy] = ..., 
                version: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.storage.blob.ObjectReplicationPolicy(DictMixin):
        policy_id: str
        rules: List[ObjectReplicationRule]

        def __contains__(self, key): ...

        def __delitem__(self, key): ...

        def __eq__(self, other): ...

        def __getitem__(self, key): ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __len__(self): ...

        def __ne__(self, other): ...

        def __repr__(self): ...

        def __setitem__(
                self, 
                key, 
                item
            ): ...

        def __str__(self): ...

        def get(
                self, 
                key, 
                default = None
            ): ...

        def has_key(self, k): ...

        def items(self): ...

        def keys(self): ...

        def update(
                self, 
                *args, 
                **kwargs
            ): ...

        def values(self): ...


    class azure.storage.blob.ObjectReplicationRule(DictMixin):
        rule_id: str
        status: str

        def __contains__(self, key): ...

        def __delitem__(self, key): ...

        def __eq__(self, other): ...

        def __getitem__(self, key): ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __len__(self): ...

        def __ne__(self, other): ...

        def __repr__(self): ...

        def __setitem__(
                self, 
                key, 
                item
            ): ...

        def __str__(self): ...

        def get(
                self, 
                key, 
                default = None
            ): ...

        def has_key(self, k): ...

        def items(self): ...

        def keys(self): ...

        def update(
                self, 
                *args, 
                **kwargs
            ): ...

        def values(self): ...


    class azure.storage.blob.PageRange(DictMixin):
        cleared: bool
        end: Optional[int]
        start: Optional[int]

        def __contains__(self, key): ...

        def __delitem__(self, key): ...

        def __eq__(self, other): ...

        def __getitem__(self, key): ...

        def __init__(
                self, 
                start: Optional[int] = None, 
                end: Optional[int] = None, 
                *, 
                cleared: bool = False
            ) -> None: ...

        def __len__(self): ...

        def __ne__(self, other): ...

        def __repr__(self): ...

        def __setitem__(
                self, 
                key, 
                item
            ): ...

        def __str__(self): ...

        def get(
                self, 
                key, 
                default = None
            ): ...

        def has_key(self, k): ...

        def items(self): ...

        def keys(self): ...

        def update(
                self, 
                *args, 
                **kwargs
            ): ...

        def values(self): ...


    class azure.storage.blob.PartialBatchErrorException(HttpResponseError):

        def __init__(
                self, 
                message: str, 
                response, 
                parts: list
            ): ...


    class azure.storage.blob.PremiumPageBlobTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        P10 = "P10"
        P15 = "P15"
        P20 = "P20"
        P30 = "P30"
        P4 = "P4"
        P40 = "P40"
        P50 = "P50"
        P6 = "P6"
        P60 = "P60"


    class azure.storage.blob.PublicAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOB = "blob"
        CONTAINER = "container"
        OFF = "off"


    class azure.storage.blob.QuickQueryDialect(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELIMITEDJSON = "DelimitedJsonDialect"
        DELIMITEDTEXT = "DelimitedTextDialect"
        PARQUET = "ParquetDialect"


    class azure.storage.blob.RehydratePriority(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        STANDARD = "Standard"


    class azure.storage.blob.ResourceTypes:
        container: bool = False
        object: bool = False
        service: bool = False

        def __init__(
                self, 
                service: bool = False, 
                container: bool = False, 
                object: bool = False
            ) -> None: ...

        def __str__(self): ...

        @classmethod
        def from_string(cls, string: str) -> ResourceTypes: ...


    class azure.storage.blob.RetentionPolicy(GeneratedRetentionPolicy):
        days: Optional[int]
        enabled: bool = False

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                enabled: bool = False, 
                days: Optional[int] = None
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.storage.blob.SequenceNumberAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INCREMENT = "increment"
        MAX = "max"
        UPDATE = "update"


    class azure.storage.blob.Services:

        def __init__(
                self, 
                *, 
                blob: bool = False, 
                fileshare: bool = False, 
                queue: bool = False
            ) -> None: ...

        def __str__(self): ...

        @classmethod
        def from_string(cls, string: str) -> Services: ...


    class azure.storage.blob.StandardBlobTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARCHIVE = "Archive"
        COLD = "Cold"
        COOL = "Cool"
        HOT = "Hot"
        SMART = "Smart"


    class azure.storage.blob.StaticWebsite(GeneratedStaticWebsite):
        default_index_document_path: Optional[str]
        enabled: bool = False
        error_document404_path: Optional[str]
        index_document: Optional[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                default_index_document_path: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                error_document404_path: Optional[str] = ..., 
                index_document: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.storage.blob.StorageErrorCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCOUNT_ALREADY_EXISTS = "AccountAlreadyExists"
        ACCOUNT_BEING_CREATED = "AccountBeingCreated"
        ACCOUNT_IS_DISABLED = "AccountIsDisabled"
        APPEND_POSITION_CONDITION_NOT_MET = "AppendPositionConditionNotMet"
        AUTHENTICATION_FAILED = "AuthenticationFailed"
        AUTHORIZATION_FAILURE = "AuthorizationFailure"
        BLOB_ACCESS_TIER_NOT_SUPPORTED_FOR_ACCOUNT_TYPE = "BlobAccessTierNotSupportedForAccountType"
        BLOB_ALREADY_EXISTS = "BlobAlreadyExists"
        BLOB_ARCHIVED = "BlobArchived"
        BLOB_BEING_REHYDRATED = "BlobBeingRehydrated"
        BLOB_NOT_ARCHIVED = "BlobNotArchived"
        BLOB_NOT_FOUND = "BlobNotFound"
        BLOB_OVERWRITTEN = "BlobOverwritten"
        BLOB_TIER_INADEQUATE_FOR_CONTENT_LENGTH = "BlobTierInadequateForContentLength"
        BLOCK_COUNT_EXCEEDS_LIMIT = "BlockCountExceedsLimit"
        BLOCK_LIST_TOO_LONG = "BlockListTooLong"
        CANNOT_CHANGE_TO_LOWER_TIER = "CannotChangeToLowerTier"
        CANNOT_DELETE_FILE_OR_DIRECTORY = "CannotDeleteFileOrDirectory"
        CANNOT_VERIFY_COPY_SOURCE = "CannotVerifyCopySource"
        CLIENT_CACHE_FLUSH_DELAY = "ClientCacheFlushDelay"
        CONDITION_HEADERS_NOT_SUPPORTED = "ConditionHeadersNotSupported"
        CONDITION_NOT_MET = "ConditionNotMet"
        CONTAINER_ALREADY_EXISTS = "ContainerAlreadyExists"
        CONTAINER_BEING_DELETED = "ContainerBeingDeleted"
        CONTAINER_DISABLED = "ContainerDisabled"
        CONTAINER_NOT_FOUND = "ContainerNotFound"
        CONTAINER_QUOTA_DOWNGRADE_NOT_ALLOWED = "ContainerQuotaDowngradeNotAllowed"
        CONTENT_LENGTH_LARGER_THAN_TIER_LIMIT = "ContentLengthLargerThanTierLimit"
        CONTENT_LENGTH_MUST_BE_ZERO = "ContentLengthMustBeZero"
        COPY_ACROSS_ACCOUNTS_NOT_SUPPORTED = "CopyAcrossAccountsNotSupported"
        COPY_ID_MISMATCH = "CopyIdMismatch"
        DELETE_PENDING = "DeletePending"
        DESTINATION_PATH_IS_BEING_DELETED = "DestinationPathIsBeingDeleted"
        DIRECTORY_NOT_EMPTY = "DirectoryNotEmpty"
        EMPTY_METADATA_KEY = "EmptyMetadataKey"
        FEATURE_VERSION_MISMATCH = "FeatureVersionMismatch"
        FILE_LOCK_CONFLICT = "FileLockConflict"
        FILE_SHARE_PROVISIONED_BANDWIDTH_DOWNGRADE_NOT_ALLOWED = "FileShareProvisionedBandwidthDowngradeNotAllowed"
        FILE_SHARE_PROVISIONED_BANDWIDTH_INVALID = "FileShareProvisionedBandwidthInvalid"
        FILE_SHARE_PROVISIONED_IOPS_DOWNGRADE_NOT_ALLOWED = "FileShareProvisionedIopsDowngradeNotAllowed"
        FILE_SHARE_PROVISIONED_IOPS_INVALID = "FileShareProvisionedIopsInvalid"
        FILE_SHARE_PROVISIONED_STORAGE_INVALID = "FileShareProvisionedStorageInvalid"
        FILE_SYSTEM_ALREADY_EXISTS = "FilesystemAlreadyExists"
        FILE_SYSTEM_BEING_DELETED = "FilesystemBeingDeleted"
        FILE_SYSTEM_NOT_FOUND = "FilesystemNotFound"
        INCREMENTAL_COPY_BLOB_MISMATCH = "IncrementalCopyBlobMismatch"
        INCREMENTAL_COPY_OF_EARLIER_SNAPSHOT_NOT_ALLOWED = "IncrementalCopyOfEarlierSnapshotNotAllowed"
        INCREMENTAL_COPY_OF_EARLIER_VERSION_SNAPSHOT_NOT_ALLOWED = "IncrementalCopyOfEarlierVersionSnapshotNotAllowed"
        INCREMENTAL_COPY_OF_ERALIER_VERSION_SNAPSHOT_NOT_ALLOWED = "IncrementalCopyOfEarlierVersionSnapshotNotAllowed"
        INCREMENTAL_COPY_SOURCE_MUST_BE_SNAPSHOT = "IncrementalCopySourceMustBeSnapshot"
        INFINITE_LEASE_DURATION_REQUIRED = "InfiniteLeaseDurationRequired"
        INSUFFICIENT_ACCOUNT_PERMISSIONS = "InsufficientAccountPermissions"
        INTERNAL_ERROR = "InternalError"
        INVALID_AUTHENTICATION_INFO = "InvalidAuthenticationInfo"
        INVALID_BLOB_OR_BLOCK = "InvalidBlobOrBlock"
        INVALID_BLOB_TIER = "InvalidBlobTier"
        INVALID_BLOB_TYPE = "InvalidBlobType"
        INVALID_BLOCK_ID = "InvalidBlockId"
        INVALID_BLOCK_LIST = "InvalidBlockList"
        INVALID_DESTINATION_PATH = "InvalidDestinationPath"
        INVALID_FILE_OR_DIRECTORY_PATH_NAME = "InvalidFileOrDirectoryPathName"
        INVALID_FLUSH_POSITION = "InvalidFlushPosition"
        INVALID_HEADER_VALUE = "InvalidHeaderValue"
        INVALID_HTTP_VERB = "InvalidHttpVerb"
        INVALID_INPUT = "InvalidInput"
        INVALID_MARKER = "InvalidMarker"
        INVALID_MD5 = "InvalidMd5"
        INVALID_METADATA = "InvalidMetadata"
        INVALID_OPERATION = "InvalidOperation"
        INVALID_PAGE_RANGE = "InvalidPageRange"
        INVALID_PROPERTY_NAME = "InvalidPropertyName"
        INVALID_QUERY_PARAMETER_VALUE = "InvalidQueryParameterValue"
        INVALID_RANGE = "InvalidRange"
        INVALID_RENAME_SOURCE_PATH = "InvalidRenameSourcePath"
        INVALID_RESOURCE_NAME = "InvalidResourceName"
        INVALID_SOURCE_BLOB_TYPE = "InvalidSourceBlobType"
        INVALID_SOURCE_BLOB_URL = "InvalidSourceBlobUrl"
        INVALID_SOURCE_OR_DESTINATION_RESOURCE_TYPE = "InvalidSourceOrDestinationResourceType"
        INVALID_SOURCE_URI = "InvalidSourceUri"
        INVALID_URI = "InvalidUri"
        INVALID_VERSION_FOR_PAGE_BLOB_OPERATION = "InvalidVersionForPageBlobOperation"
        INVALID_XML_DOCUMENT = "InvalidXmlDocument"
        INVALID_XML_NODE_VALUE = "InvalidXmlNodeValue"
        LEASE_ALREADY_BROKEN = "LeaseAlreadyBroken"
        LEASE_ALREADY_PRESENT = "LeaseAlreadyPresent"
        LEASE_ID_MISMATCH_WITH_BLOB_OPERATION = "LeaseIdMismatchWithBlobOperation"
        LEASE_ID_MISMATCH_WITH_CONTAINER_OPERATION = "LeaseIdMismatchWithContainerOperation"
        LEASE_ID_MISMATCH_WITH_LEASE_OPERATION = "LeaseIdMismatchWithLeaseOperation"
        LEASE_ID_MISSING = "LeaseIdMissing"
        LEASE_IS_ALREADY_BROKEN = "LeaseIsAlreadyBroken"
        LEASE_IS_BREAKING_AND_CANNOT_BE_ACQUIRED = "LeaseIsBreakingAndCannotBeAcquired"
        LEASE_IS_BREAKING_AND_CANNOT_BE_CHANGED = "LeaseIsBreakingAndCannotBeChanged"
        LEASE_IS_BROKEN_AND_CANNOT_BE_RENEWED = "LeaseIsBrokenAndCannotBeRenewed"
        LEASE_LOST = "LeaseLost"
        LEASE_NAME_MISMATCH = "LeaseNameMismatch"
        LEASE_NOT_PRESENT_WITH_BLOB_OPERATION = "LeaseNotPresentWithBlobOperation"
        LEASE_NOT_PRESENT_WITH_CONTAINER_OPERATION = "LeaseNotPresentWithContainerOperation"
        LEASE_NOT_PRESENT_WITH_LEASE_OPERATION = "LeaseNotPresentWithLeaseOperation"
        MAX_BLOB_SIZE_CONDITION_NOT_MET = "MaxBlobSizeConditionNotMet"
        MD5_MISMATCH = "Md5Mismatch"
        MESSAGE_NOT_FOUND = "MessageNotFound"
        MESSAGE_TOO_LARGE = "MessageTooLarge"
        METADATA_TOO_LARGE = "MetadataTooLarge"
        MISSING_CONTENT_LENGTH_HEADER = "MissingContentLengthHeader"
        MISSING_REQUIRED_HEADER = "MissingRequiredHeader"
        MISSING_REQUIRED_QUERY_PARAMETER = "MissingRequiredQueryParameter"
        MISSING_REQUIRED_XML_NODE = "MissingRequiredXmlNode"
        MULTIPLE_CONDITION_HEADERS_NOT_SUPPORTED = "MultipleConditionHeadersNotSupported"
        NO_AUTHENTICATION_INFORMATION = "NoAuthenticationInformation"
        NO_PENDING_COPY_OPERATION = "NoPendingCopyOperation"
        OPERATION_NOT_ALLOWED_ON_INCREMENTAL_COPY_BLOB = "OperationNotAllowedOnIncrementalCopyBlob"
        OPERATION_TIMED_OUT = "OperationTimedOut"
        OUT_OF_RANGE_INPUT = "OutOfRangeInput"
        OUT_OF_RANGE_QUERY_PARAMETER_VALUE = "OutOfRangeQueryParameterValue"
        PARENT_NOT_FOUND = "ParentNotFound"
        PATH_ALREADY_EXISTS = "PathAlreadyExists"
        PATH_CONFLICT = "PathConflict"
        PATH_NOT_FOUND = "PathNotFound"
        PENDING_COPY_OPERATION = "PendingCopyOperation"
        POP_RECEIPT_MISMATCH = "PopReceiptMismatch"
        PREVIOUS_SNAPSHOT_CANNOT_BE_NEWER = "PreviousSnapshotCannotBeNewer"
        PREVIOUS_SNAPSHOT_NOT_FOUND = "PreviousSnapshotNotFound"
        PREVIOUS_SNAPSHOT_OPERATION_NOT_SUPPORTED = "PreviousSnapshotOperationNotSupported"
        QUEUE_ALREADY_EXISTS = "QueueAlreadyExists"
        QUEUE_BEING_DELETED = "QueueBeingDeleted"
        QUEUE_DISABLED = "QueueDisabled"
        QUEUE_NOT_EMPTY = "QueueNotEmpty"
        QUEUE_NOT_FOUND = "QueueNotFound"
        READ_ONLY_ATTRIBUTE = "ReadOnlyAttribute"
        RENAME_DESTINATION_PARENT_PATH_NOT_FOUND = "RenameDestinationParentPathNotFound"
        REQUEST_BODY_TOO_LARGE = "RequestBodyTooLarge"
        REQUEST_URL_FAILED_TO_PARSE = "RequestUrlFailedToParse"
        RESOURCE_ALREADY_EXISTS = "ResourceAlreadyExists"
        RESOURCE_NOT_FOUND = "ResourceNotFound"
        RESOURCE_TYPE_MISMATCH = "ResourceTypeMismatch"
        SEQUENCE_NUMBER_CONDITION_NOT_MET = "SequenceNumberConditionNotMet"
        SEQUENCE_NUMBER_INCREMENT_TOO_LARGE = "SequenceNumberIncrementTooLarge"
        SERVER_BUSY = "ServerBusy"
        SHARE_ALREADY_EXISTS = "ShareAlreadyExists"
        SHARE_BEING_DELETED = "ShareBeingDeleted"
        SHARE_DISABLED = "ShareDisabled"
        SHARE_HAS_SNAPSHOTS = "ShareHasSnapshots"
        SHARE_NOT_FOUND = "ShareNotFound"
        SHARE_SNAPSHOT_COUNT_EXCEEDED = "ShareSnapshotCountExceeded"
        SHARE_SNAPSHOT_IN_PROGRESS = "ShareSnapshotInProgress"
        SHARE_SNAPSHOT_NOT_FOUND = "ShareSnapshotNotFound"
        SHARE_SNAPSHOT_OPERATION_NOT_SUPPORTED = "ShareSnapshotOperationNotSupported"
        SHARING_VIOLATION = "SharingViolation"
        SNAPHOT_OPERATION_RATE_EXCEEDED = "SnapshotOperationRateExceeded"
        SNAPSHOTS_PRESENT = "SnapshotsPresent"
        SNAPSHOT_COUNT_EXCEEDED = "SnapshotCountExceeded"
        SNAPSHOT_OPERATION_RATE_EXCEEDED = "SnapshotOperationRateExceeded"
        SOURCE_CONDITION_NOT_MET = "SourceConditionNotMet"
        SOURCE_PATH_IS_BEING_DELETED = "SourcePathIsBeingDeleted"
        SOURCE_PATH_NOT_FOUND = "SourcePathNotFound"
        SYSTEM_IN_USE = "SystemInUse"
        TARGET_CONDITION_NOT_MET = "TargetConditionNotMet"
        TOTAL_SHARES_COUNT_EXCEEDS_ACCOUNT_LIMIT = "TotalSharesCountExceedsAccountLimit"
        TOTAL_SHARES_PROVISIONED_BANDWIDTH_EXCEEDS_ACCOUNT_LIMIT = "TotalSharesProvisionedBandwidthExceedsAccountLimit"
        TOTAL_SHARES_PROVISIONED_CAPACITY_EXCEEDS_ACCOUNT_LIMIT = "TotalSharesProvisionedCapacityExceedsAccountLimit"
        TOTAL_SHARES_PROVISIONED_IOPS_EXCEEDS_ACCOUNT_LIMIT = "TotalSharesProvisionedIopsExceedsAccountLimit"
        UNAUTHORIZED_BLOB_OVERWRITE = "UnauthorizedBlobOverwrite"
        UNSUPPORTED_HEADER = "UnsupportedHeader"
        UNSUPPORTED_HTTP_VERB = "UnsupportedHttpVerb"
        UNSUPPORTED_QUERY_PARAMETER = "UnsupportedQueryParameter"
        UNSUPPORTED_REST_VERSION = "UnsupportedRestVersion"
        UNSUPPORTED_XML_NODE = "UnsupportedXmlNode"


    class azure.storage.blob.StorageStreamDownloader(Generic[T]):
        container: str
        name: str
        properties: BlobProperties
        size: int

        def __init__(
                self, 
                clients: AzureBlobStorage = None, 
                config: StorageConfiguration = None, 
                start_range: Optional[int] = None, 
                end_range: Optional[int] = None, 
                validate_content: bool = None, 
                encryption_options: Dict[str, Any] = None, 
                max_concurrency: Optional[int] = None, 
                name: str = None, 
                container: str = None, 
                encoding: Optional[str] = None, 
                download_cls: Optional[Callable] = None, 
                **kwargs: Any
            ) -> None: ...

        def __len__(self): ...

        def chunks(self) -> Iterator[bytes]: ...

        def content_as_bytes(self, max_concurrency: Optional[int] = None) -> bytes: ...

        def content_as_text(
                self, 
                max_concurrency: Optional[int] = None, 
                encoding: str = "UTF-8"
            ) -> str: ...

        def download_to_stream(
                self, 
                stream: IO[T], 
                max_concurrency: Optional[int] = None
            ) -> Any: ...

        @overload
        def read(self, size: int = -1) -> T: ...

        @overload
        def read(
                self, 
                *, 
                chars: Optional[int] = ...
            ) -> T: ...

        def readall(self) -> T: ...

        def readinto(self, stream: IO[bytes]) -> int: ...


    class azure.storage.blob.UserDelegationKey:
        signed_delegated_user_tid: Optional[str]
        signed_expiry: Optional[str]
        signed_oid: Optional[str]
        signed_service: Optional[str]
        signed_start: Optional[str]
        signed_tid: Optional[str]
        signed_version: Optional[str]
        value: Optional[str]

        def __init__(self): ...


namespace azure.storage.blob.aio

    async def azure.storage.blob.aio.download_blob_from_url:async(
            blob_url: str, 
            output: str, 
            credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, AsyncTokenCredential]] = None, 
            *, 
            length: Optional[int] = ..., 
            max_concurrency: Optional[int] = ..., 
            offset: Optional[int] = ..., 
            overwrite: Optional[bool] = ..., 
            validate_content: Optional[bool] = ..., 
            **kwargs: Any
        ) -> None: ...


    async def azure.storage.blob.aio.upload_blob_to_url:async(
            blob_url: str, 
            data: Union[Iterable[AnyStr], IO[AnyStr]], 
            credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, AsyncTokenCredential]] = None, 
            *, 
            encoding: Optional[str] = ..., 
            length: Optional[int] = ..., 
            max_concurrency: Optional[int] = ..., 
            metadata: Optional[dict(str,str)] = ..., 
            overwrite: Optional[bool] = ..., 
            validate_content: Optional[bool] = ..., 
            **kwargs: Any
        ) -> Dict[str, Any]: ...


    class azure.storage.blob.aio.BlobClient(AsyncStorageAccountHostsMixin, StorageAccountHostsMixin, StorageEncryptionMixin): implements AsyncContextManager 
        property api_version: str    # Read-only
        property location_mode: str
        property primary_endpoint: str    # Read-only
        property primary_hostname: str    # Read-only
        property secondary_endpoint: str    # Read-only
        property secondary_hostname: Optional[str]    # Read-only
        property url: str    # Read-only

        def __init__(
                self, 
                account_url: str, 
                container_name: str, 
                blob_name: str, 
                snapshot: Optional[Union[str, Dict[str, Any]]] = None, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, AsyncTokenCredential]] = None, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                max_block_size: Optional[int] = ..., 
                max_chunk_get_size: Optional[int] = ..., 
                max_page_size: Optional[int] = ..., 
                max_single_get_size: Optional[int] = ..., 
                max_single_put_size: Optional[int] = ..., 
                min_large_block_upload_threshold: Optional[int] = ..., 
                secondary_hostname: Optional[str] = ..., 
                use_byte_buffer: Optional[bool] = ..., 
                version_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_blob_url(
                cls, 
                blob_url: str, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, AsyncTokenCredential]] = None, 
                snapshot: Optional[Union[str, Dict[str, Any]]] = None, 
                *, 
                audience: Optional[str] = ..., 
                version_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> Self: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                container_name: str, 
                blob_name: str, 
                snapshot: Optional[Union[str, Dict[str, Any]]] = None, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, AsyncTokenCredential]] = None, 
                *, 
                audience: Optional[str] = ..., 
                version_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> Self: ...

        @distributed_trace_async
        async def abort_copy(
                self, 
                copy_id: Union[str, Dict[str, Any], BlobProperties], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def acquire_lease(
                self, 
                lease_duration: int = -1, 
                lease_id: Optional[str] = None, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> BlobLeaseClient: ...

        @distributed_trace_async
        async def append_block(
                self, 
                data: Union[bytes, Iterable[bytes], IO[bytes]], 
                length: Optional[int] = None, 
                *, 
                appendpos_condition: Optional[int] = ..., 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                encoding: Optional[str] = ..., 
                encryption_scope: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                maxsize_condition: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                validate_content: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime, int]]: ...

        @distributed_trace_async
        async def append_block_from_url(
                self, 
                copy_source_url: str, 
                source_offset: Optional[int] = None, 
                source_length: Optional[int] = None, 
                *, 
                appendpos_condition: Optional[int] = ..., 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                encryption_scope: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                maxsize_condition: Optional[int] = ..., 
                source_authorization: Optional[str] = ..., 
                source_content_md5: Optional[bytearray] = ..., 
                source_cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                source_etag: Optional[str] = ..., 
                source_if_modified_since: Optional[datetime] = ..., 
                source_if_unmodified_since: Optional[datetime] = ..., 
                source_match_condition: Optional[MatchConditions] = ..., 
                source_token_intent: Literal[backup] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime, int]]: ...

        @distributed_trace_async
        async def clear_page(
                self, 
                offset: int, 
                length: int, 
                *, 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_sequence_number_eq: Optional[int] = ..., 
                if_sequence_number_lt: Optional[int] = ..., 
                if_sequence_number_lte: Optional[int] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime]]: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def commit_block_list(
                self, 
                block_list: List[BlobBlock], 
                content_settings: Optional[ContentSettings] = None, 
                metadata: Optional[Dict[str, str]] = None, 
                *, 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                encryption_scope: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                immutability_policy: Optional[ImmutabilityPolicy] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                legal_hold: Optional[bool] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                standard_blob_tier: Optional[StandardBlobTier] = ..., 
                tags: dict(str, str) = ..., 
                timeout: Optional[int] = ..., 
                validate_content: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime]]: ...

        @distributed_trace_async
        async def create_append_blob(
                self, 
                content_settings: Optional[ContentSettings] = None, 
                metadata: Optional[Dict[str, str]] = None, 
                *, 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                encryption_scope: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                immutability_policy: Optional[ImmutabilityPolicy] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                legal_hold: Optional[bool] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                tags: dict(str, str) = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime]]: ...

        @distributed_trace_async
        async def create_page_blob(
                self, 
                size: int, 
                content_settings: Optional[ContentSettings] = None, 
                metadata: Optional[Dict[str, str]] = None, 
                premium_page_blob_tier: Optional[Union[str, PremiumPageBlobTier]] = None, 
                *, 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                encryption_scope: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                immutability_policy: Optional[ImmutabilityPolicy] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                legal_hold: Optional[bool] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                sequence_number: Optional[int] = ..., 
                tags: dict(str, str) = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime]]: ...

        @distributed_trace_async
        async def create_snapshot(
                self, 
                metadata: Optional[Dict[str, str]] = None, 
                *, 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                encryption_scope: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime]]: ...

        @distributed_trace_async
        async def delete_blob(
                self, 
                delete_snapshots: Optional[str] = None, 
                *, 
                access_tier_if_modified_since: Optional[datetime] = ..., 
                access_tier_if_unmodified_since: Optional[datetime] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                version_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_immutability_policy(
                self, 
                *, 
                timeout: Optional[int] = ..., 
                version_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def download_blob(
                self, 
                offset: Optional[int] = None, 
                length: Optional[int] = None, 
                *, 
                encoding: str, 
                **kwargs: Any
            ) -> StorageStreamDownloader[str]: ...

        @overload
        async def download_blob(
                self, 
                offset: Optional[int] = None, 
                length: Optional[int] = None, 
                *, 
                encoding: None = ..., 
                **kwargs: Any
            ) -> StorageStreamDownloader[bytes]: ...

        @distributed_trace_async
        async def exists(
                self, 
                *, 
                timeout: Optional[int] = ..., 
                version_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> bool: ...

        @distributed_trace_async
        async def get_account_information(self, **kwargs: Any) -> Dict[str, str]: ...

        @distributed_trace_async
        async def get_blob_properties(
                self, 
                *, 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                version_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> BlobProperties: ...

        @distributed_trace_async
        async def get_blob_tags(
                self, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                version_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> Dict[str, str]: ...

        @distributed_trace_async
        async def get_block_list(
                self, 
                block_list_type: str = "committed", 
                *, 
                if_tags_match_condition: Optional[str] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Tuple[List[BlobBlock], List[BlobBlock]]: ...

        @distributed_trace_async
        async def get_page_range_diff_for_managed_disk(
                self, 
                previous_snapshot_url: str, 
                offset: Optional[int] = None, 
                length: Optional[int] = None, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Tuple[List[Dict[str, int]], List[Dict[str, int]]]: ...

        @distributed_trace_async
        async def get_page_ranges(
                self, 
                offset: Optional[int] = None, 
                length: Optional[int] = None, 
                previous_snapshot_diff: Optional[Union[str, Dict[str, Any]]] = None, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Tuple[List[Dict[str, int]], List[Dict[str, int]]]: ...

        @distributed_trace
        def list_page_ranges(
                self, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                length: Optional[int] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                offset: Optional[int] = ..., 
                previous_snapshot: Optional[Union[str, Dict[str, Any]]] = ..., 
                results_per_page: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PageRange]: ...

        @distributed_trace_async
        async def query_blob(
                self, 
                query_expression: str, 
                *, 
                blob_format: Optional[Union[DelimitedTextDialect, DelimitedJsonDialect, QuickQueryDialect, str]] = ..., 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Optional[Union[BlobLeaseClient, str]] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                on_error: Optional[Callable[[BlobQueryError], None]] = ..., 
                output_format: Optional[Union[DelimitedTextDialect, DelimitedJsonDialect, QuickQueryDialect, List[ArrowDialect], str]] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> BlobQueryReader: ...

        @distributed_trace_async
        async def resize_blob(
                self, 
                size: int, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                premium_page_blob_tier: Optional[PremiumPageBlobTier] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime]]: ...

        @distributed_trace_async
        async def seal_append_blob(
                self, 
                *, 
                appendpos_condition: Optional[int] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime, int]]: ...

        @distributed_trace_async
        async def set_blob_metadata(
                self, 
                metadata: Optional[Dict[str, str]] = None, 
                *, 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                encryption_scope: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime]]: ...

        @distributed_trace_async
        async def set_blob_tags(
                self, 
                tags: Optional[Dict[str, str]] = None, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                validate_content: Optional[bool] = ..., 
                version_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace_async
        async def set_http_headers(
                self, 
                content_settings: Optional[ContentSettings] = None, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace_async
        async def set_immutability_policy(
                self, 
                immutability_policy: ImmutabilityPolicy, 
                *, 
                timeout: Optional[int] = ..., 
                version_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> Dict[str, str]: ...

        @distributed_trace_async
        async def set_legal_hold(
                self, 
                legal_hold: bool = False, 
                *, 
                timeout: Optional[int] = ..., 
                version_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime, bool]]: ...

        @distributed_trace_async
        async def set_premium_page_blob_tier(
                self, 
                premium_page_blob_tier: PremiumPageBlobTier, 
                *, 
                if_tags_match_condition: Optional[str] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def set_sequence_number(
                self, 
                sequence_number_action: Union[str, SequenceNumberAction], 
                sequence_number: Optional[str] = None, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime]]: ...

        @distributed_trace_async
        async def set_standard_blob_tier(
                self, 
                standard_blob_tier: Union[str, StandardBlobTier], 
                *, 
                if_tags_match_condition: Optional[str] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                rehydrate_priority: Optional[RehydratePriority] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def stage_block(
                self, 
                block_id: str, 
                data: Union[bytes, Iterable[bytes], IO[bytes]], 
                length: Optional[int] = None, 
                *, 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                encoding: Optional[str] = ..., 
                encryption_scope: Optional[str] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                timeout: Optional[int] = ..., 
                validate_content: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace_async
        async def stage_block_from_url(
                self, 
                block_id: str, 
                source_url: str, 
                source_offset: Optional[int] = None, 
                source_length: Optional[int] = None, 
                source_content_md5: Optional[Union[bytes, bytearray]] = None, 
                *, 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                encryption_scope: Optional[str] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                source_authorization: Optional[str] = ..., 
                source_cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                source_token_intent: Literal[backup] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace_async
        async def start_copy_from_url(
                self, 
                source_url: str, 
                metadata: Optional[Dict[str, str]] = None, 
                incremental_copy: bool = False, 
                *, 
                destination_lease: Union[BlobLeaseClient, str] = ..., 
                encryption_scope: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                immutability_policy: Optional[ImmutabilityPolicy] = ..., 
                legal_hold: Optional[bool] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                premium_page_blob_tier: Optional[PremiumPageBlobTier] = ..., 
                rehydrate_priority: Optional[RehydratePriority] = ..., 
                requires_sync: Optional[bool] = ..., 
                seal_destination_blob: Optional[bool] = ..., 
                source_authorization: Optional[str] = ..., 
                source_etag: Optional[str] = ..., 
                source_if_modified_since: Optional[datetime] = ..., 
                source_if_unmodified_since: Optional[datetime] = ..., 
                source_lease: Union[BlobLeaseClient, str] = ..., 
                source_match_condition: Optional[MatchConditions] = ..., 
                source_token_intent: Literal[backup] = ..., 
                standard_blob_tier: Optional[StandardBlobTier] = ..., 
                tags: Union[dict(str, str), Literal[COPY]] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime]]: ...

        @distributed_trace_async
        async def undelete_blob(
                self, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def upload_blob(
                self, 
                data: Union[bytes, str, Iterable[AnyStr], AsyncIterable[AnyStr], IO[bytes]], 
                blob_type: Union[str, BlobType] = BlobType.BLOCKBLOB, 
                length: Optional[int] = None, 
                metadata: Optional[Dict[str, str]] = None, 
                *, 
                content_settings: Optional[ContentSettings] = ..., 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                encoding: Optional[str] = ..., 
                encryption_scope: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                immutability_policy: Optional[ImmutabilityPolicy] = ..., 
                lease = ..., 
                legal_hold: Optional[bool] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                max_concurrency: Optional[int] = ..., 
                maxsize_condition: Optional[int] = ..., 
                overwrite: Optional[bool] = ..., 
                premium_page_blob_tier: Optional[PremiumPageBlobTier] = ..., 
                progress_hook: Callable[[int, Optional[int]], Awaitable[None]] = ..., 
                standard_blob_tier: Optional[StandardBlobTier] = ..., 
                tags: dict(str, str) = ..., 
                timeout: Optional[int] = ..., 
                validate_content: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace_async
        async def upload_blob_from_url(
                self, 
                source_url: str, 
                *, 
                content_settings: Optional[ContentSettings] = ..., 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                destination_lease: Union[BlobLeaseClient, str] = ..., 
                encryption_scope: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                include_source_blob_properties: Optional[bool] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                metadata: Optional[Dict[str, str]] = ..., 
                overwrite: Optional[bool] = ..., 
                source_authorization: Optional[str] = ..., 
                source_content_md5: Optional[bytearray] = ..., 
                source_cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                source_etag: Optional[str] = ..., 
                source_if_modified_since: Optional[datetime] = ..., 
                source_if_unmodified_since: Optional[datetime] = ..., 
                source_match_condition: Optional[MatchConditions] = ..., 
                source_token_intent: Literal[backup] = ..., 
                standard_blob_tier: Optional[StandardBlobTier] = ..., 
                tags: dict(str, str) = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace_async
        async def upload_page(
                self, 
                page: bytes, 
                offset: int, 
                length: int, 
                *, 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                encoding: Optional[str] = ..., 
                encryption_scope: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_sequence_number_eq: Optional[int] = ..., 
                if_sequence_number_lt: Optional[int] = ..., 
                if_sequence_number_lte: Optional[int] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                validate_content: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime]]: ...

        @distributed_trace_async
        async def upload_pages_from_url(
                self, 
                source_url: str, 
                offset: int, 
                length: int, 
                source_offset: int, 
                *, 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                encryption_scope: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_sequence_number_eq: Optional[int] = ..., 
                if_sequence_number_lt: Optional[int] = ..., 
                if_sequence_number_lte: Optional[int] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                source_authorization: Optional[str] = ..., 
                source_content_md5: Optional[bytes] = ..., 
                source_cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                source_etag: Optional[str] = ..., 
                source_if_modified_since: Optional[datetime] = ..., 
                source_if_unmodified_since: Optional[datetime] = ..., 
                source_match_condition: Optional[MatchConditions] = ..., 
                source_token_intent: Literal[backup] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...


    class azure.storage.blob.aio.BlobLeaseClient: implements ContextManager , AsyncContextManager 
        etag: Optional[str]
        id: str
        last_modified: Optional[datetime]

        def __init__(
                self, 
                client: Union[BlobClient, ContainerClient], 
                lease_id: Optional[str] = None
            ) -> None: ...

        @distributed_trace_async
        async def acquire(
                self, 
                lease_duration: int = -1, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def break_lease(
                self, 
                lease_break_period: Optional[int] = None, 
                *, 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> int: ...

        @distributed_trace_async
        async def change(
                self, 
                proposed_lease_id: str, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def release(
                self, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def renew(
                self, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.storage.blob.aio.BlobPrefix(AsyncItemPaged, DictMixin):
        command: Callable
        container: str
        current_page: Optional[List[BlobProperties]]
        delimiter: str
        location_mode: str
        marker: Optional[str]
        name: str
        next_marker: Optional[str]
        prefix: str
        results_per_page: Optional[int]
        service_endpoint: Optional[str]

        def __contains__(self, key): ...

        def __delitem__(self, key): ...

        def __eq__(self, other): ...

        def __getitem__(self, key): ...

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        def __len__(self): ...

        def __ne__(self, other): ...

        def __repr__(self): ...

        def __setitem__(
                self, 
                key, 
                item
            ): ...

        def __str__(self): ...

        def get(
                self, 
                key, 
                default = None
            ): ...

        def has_key(self, k): ...

        def items(self): ...

        def keys(self): ...

        def update(
                self, 
                *args, 
                **kwargs
            ): ...

        def values(self): ...


    class azure.storage.blob.aio.BlobServiceClient(AsyncStorageAccountHostsMixin, StorageAccountHostsMixin, StorageEncryptionMixin): implements AsyncContextManager 
        property api_version: str    # Read-only
        property location_mode: str
        property primary_endpoint: str    # Read-only
        property primary_hostname: str    # Read-only
        property secondary_endpoint: str    # Read-only
        property secondary_hostname: Optional[str]    # Read-only
        property url: str    # Read-only

        def __init__(
                self, 
                account_url: str, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, AsyncTokenCredential]] = None, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                max_block_size: Optional[int] = ..., 
                max_chunk_get_size: Optional[int] = ..., 
                max_page_size: Optional[int] = ..., 
                max_single_get_size: Optional[int] = ..., 
                max_single_put_size: Optional[int] = ..., 
                min_large_block_upload_threshold: Optional[int] = ..., 
                secondary_hostname: Optional[str] = ..., 
                use_byte_buffer: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, AsyncTokenCredential]] = None, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                max_block_size: Optional[int] = ..., 
                max_chunk_get_size: Optional[int] = ..., 
                max_page_size: Optional[int] = ..., 
                max_single_get_size: Optional[int] = ..., 
                max_single_put_size: Optional[int] = ..., 
                min_large_block_upload_threshold: Optional[int] = ..., 
                secondary_hostname: Optional[str] = ..., 
                use_byte_buffer: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Self: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def create_container(
                self, 
                name: str, 
                metadata: Optional[Dict[str, str]] = None, 
                public_access: Optional[Union[PublicAccess, str]] = None, 
                *, 
                container_encryption_scope: Union[dict, ContainerEncryptionScope] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ContainerClient: ...

        @distributed_trace_async
        async def delete_container(
                self, 
                container: Union[ContainerProperties, str], 
                lease: Optional[Union[BlobLeaseClient, str]] = None, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def find_blobs_by_tags(
                self, 
                filter_expression: str, 
                *, 
                results_per_page: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[FilteredBlob]: ...

        @distributed_trace_async
        async def get_account_information(self, **kwargs: Any) -> Dict[str, str]: ...

        def get_blob_client(
                self, 
                container: Union[ContainerProperties, str], 
                blob: str, 
                snapshot: Optional[Union[Dict[str, Any], str]] = None, 
                *, 
                version_id: Optional[str] = ...
            ) -> BlobClient: ...

        def get_container_client(self, container: Union[ContainerProperties, str]) -> ContainerClient: ...

        @distributed_trace_async
        async def get_service_properties(
                self, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace_async
        async def get_service_stats(
                self, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace_async
        async def get_user_delegation_key(
                self, 
                key_start_time: datetime, 
                key_expiry_time: datetime, 
                *, 
                delegated_user_tid: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> UserDelegationKey: ...

        @distributed_trace
        def list_containers(
                self, 
                name_starts_with: Optional[str] = None, 
                include_metadata: bool = False, 
                *, 
                include_deleted: Optional[bool] = ..., 
                include_system: Optional[bool] = ..., 
                results_per_page: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ContainerProperties]: ...

        @distributed_trace_async
        async def set_service_properties(
                self, 
                analytics_logging: Optional[BlobAnalyticsLogging] = None, 
                hour_metrics: Optional[Metrics] = None, 
                minute_metrics: Optional[Metrics] = None, 
                cors: Optional[List[CorsRule]] = None, 
                target_version: Optional[str] = None, 
                delete_retention_policy: Optional[RetentionPolicy] = None, 
                static_website: Optional[StaticWebsite] = None, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def undelete_container(
                self, 
                deleted_container_name: str, 
                deleted_container_version: str, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ContainerClient: ...


    class azure.storage.blob.aio.ContainerClient(AsyncStorageAccountHostsMixin, StorageAccountHostsMixin, StorageEncryptionMixin): implements AsyncContextManager 
        property api_version: str    # Read-only
        property location_mode: str
        property primary_endpoint: str    # Read-only
        property primary_hostname: str    # Read-only
        property secondary_endpoint: str    # Read-only
        property secondary_hostname: Optional[str]    # Read-only
        property url: str    # Read-only

        def __init__(
                self, 
                account_url: str, 
                container_name: str, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, AsyncTokenCredential]] = None, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                max_block_size: Optional[int] = ..., 
                max_chunk_get_size: Optional[int] = ..., 
                max_page_size: Optional[int] = ..., 
                max_single_get_size: Optional[int] = ..., 
                max_single_put_size: Optional[int] = ..., 
                min_large_block_upload_threshold: Optional[int] = ..., 
                secondary_hostname: Optional[str] = ..., 
                use_byte_buffer: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                container_name: str, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, AsyncTokenCredential]] = None, 
                *, 
                audience: Optional[str] = ..., 
                **kwargs: Any
            ) -> Self: ...

        @classmethod
        def from_container_url(
                cls, 
                container_url: str, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, AsyncTokenCredential]] = None, 
                *, 
                audience: Optional[str] = ..., 
                **kwargs: Any
            ) -> Self: ...

        @distributed_trace_async
        async def acquire_lease(
                self, 
                lease_duration: int = -1, 
                lease_id: Optional[str] = None, 
                *, 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> BlobLeaseClient: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def create_container(
                self, 
                metadata: Optional[Dict[str, str]] = None, 
                public_access: Optional[Union[PublicAccess, str]] = None, 
                *, 
                container_encryption_scope: Union[dict, ContainerEncryptionScope] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime]]: ...

        @distributed_trace_async
        async def delete_blob(
                self, 
                blob: str, 
                delete_snapshots: Optional[str] = None, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                version_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_blobs(
                self, 
                *blobs: Union[str, Dict[str, Any], BlobProperties], 
                *, 
                delete_snapshots: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                raise_on_any_failure: Optional[bool] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncIterator[AsyncHttpResponse]: ...

        @distributed_trace_async
        async def delete_container(
                self, 
                *, 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def download_blob(
                self, 
                blob: str, 
                offset: Optional[int] = None, 
                length: Optional[int] = None, 
                *, 
                encoding: str, 
                **kwargs: Any
            ) -> StorageStreamDownloader[str]: ...

        @overload
        async def download_blob(
                self, 
                blob: str, 
                offset: Optional[int] = None, 
                length: Optional[int] = None, 
                *, 
                encoding: None = ..., 
                **kwargs: Any
            ) -> StorageStreamDownloader[bytes]: ...

        @distributed_trace_async
        async def exists(self, **kwargs: Any) -> bool: ...

        @distributed_trace
        def find_blobs_by_tags(
                self, 
                filter_expression: str, 
                *, 
                results_per_page: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[FilteredBlob]: ...

        @distributed_trace_async
        async def get_account_information(self, **kwargs: Any) -> Dict[str, str]: ...

        def get_blob_client(
                self, 
                blob: str, 
                snapshot: Optional[str] = None, 
                *, 
                version_id: Optional[str] = ...
            ) -> BlobClient: ...

        @distributed_trace_async
        async def get_container_access_policy(
                self, 
                *, 
                lease: Union[BlobLeaseClient, str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace_async
        async def get_container_properties(
                self, 
                *, 
                lease: Union[BlobLeaseClient, str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ContainerProperties: ...

        @distributed_trace
        def list_blob_names(
                self, 
                *, 
                name_starts_with: Optional[str] = ..., 
                results_per_page: Optional[int] = ..., 
                start_from: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[str]: ...

        @distributed_trace
        def list_blobs(
                self, 
                name_starts_with: Optional[str] = None, 
                include: Optional[Union[str, List[str]]] = None, 
                *, 
                results_per_page: Optional[int] = ..., 
                start_from: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BlobProperties]: ...

        @distributed_trace_async
        async def set_container_access_policy(
                self, 
                signed_identifiers: Dict[str, AccessPolicy], 
                public_access: Optional[Union[str, PublicAccess]] = None, 
                *, 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime]]: ...

        @distributed_trace_async
        async def set_container_metadata(
                self, 
                metadata: Optional[Dict[str, str]] = None, 
                *, 
                if_modified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime]]: ...

        @distributed_trace_async
        async def set_premium_page_blob_tier_blobs(
                self, 
                premium_page_blob_tier: Union[str, PremiumPageBlobTier], 
                *blobs: Union[str, Dict[str, Any], BlobProperties], 
                *, 
                raise_on_any_failure: Optional[bool] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncIterator[AsyncHttpResponse]: ...

        @distributed_trace_async
        async def set_standard_blob_tier_blobs(
                self, 
                standard_blob_tier: Union[str, StandardBlobTier], 
                *blobs: Union[str, Dict[str, Any], BlobProperties], 
                *, 
                if_tags_match_condition: Optional[str] = ..., 
                raise_on_any_failure: Optional[bool] = ..., 
                rehydrate_priority: Optional[RehydratePriority] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncIterator[AsyncHttpResponse]: ...

        @distributed_trace_async
        async def upload_blob(
                self, 
                name: str, 
                data: Union[bytes, str, Iterable[AnyStr], AsyncIterable[AnyStr], IO[AnyStr]], 
                blob_type: Union[str, BlobType] = BlobType.BLOCKBLOB, 
                length: Optional[int] = None, 
                metadata: Optional[Dict[str, str]] = None, 
                *, 
                content_settings: Optional[ContentSettings] = ..., 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                encoding: Optional[str] = ..., 
                encryption_scope: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[BlobLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                max_concurrency: Optional[int] = ..., 
                maxsize_condition: Optional[int] = ..., 
                overwrite: Optional[bool] = ..., 
                premium_page_blob_tier: Optional[PremiumPageBlobTier] = ..., 
                progress_hook: Callable[[int, Optional[int]], Awaitable[None]] = ..., 
                standard_blob_tier: Optional[StandardBlobTier] = ..., 
                timeout: Optional[int] = ..., 
                validate_content: Optional[bool] = ..., 
                **kwargs
            ) -> BlobClient: ...

        @distributed_trace
        def walk_blobs(
                self, 
                name_starts_with: Optional[str] = None, 
                include: Optional[Union[List[str], str]] = None, 
                delimiter: str = "/", 
                *, 
                start_from: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Union[BlobProperties, BlobPrefix]]: ...


    class azure.storage.blob.aio.ExponentialRetry(AsyncStorageRetryPolicy):
        increment_base: int
        initial_backoff: int
        random_jitter_range: int

        def __init__(
                self, 
                initial_backoff: int = 15, 
                increment_base: int = 3, 
                retry_total: int = 3, 
                retry_to_secondary: bool = False, 
                random_jitter_range: int = 3, 
                **kwargs
            ) -> None: ...

        def configure_retries(self, request: PipelineRequest) -> Dict[str, Any]: ...

        def get_backoff_time(self, settings: Dict[str, Any]) -> float: ...

        def increment(
                self, 
                settings: Dict[str, Any], 
                request: PipelineRequest, 
                response: Optional[PipelineResponse] = None, 
                error: Optional[AzureError] = None
            ) -> bool: ...

        async def send(self, request): ...

        async def sleep(
                self, 
                settings, 
                transport
            ): ...


    class azure.storage.blob.aio.LinearRetry(AsyncStorageRetryPolicy):
        initial_backoff: int
        random_jitter_range: int

        def __init__(
                self, 
                backoff: int = 15, 
                retry_total: int = 3, 
                retry_to_secondary: bool = False, 
                random_jitter_range: int = 3, 
                **kwargs: Any
            ) -> None: ...

        def configure_retries(self, request: PipelineRequest) -> Dict[str, Any]: ...

        def get_backoff_time(self, settings: Dict[str, Any]) -> float: ...

        def increment(
                self, 
                settings: Dict[str, Any], 
                request: PipelineRequest, 
                response: Optional[PipelineResponse] = None, 
                error: Optional[AzureError] = None
            ) -> bool: ...

        async def send(self, request): ...

        async def sleep(
                self, 
                settings, 
                transport
            ): ...


    class azure.storage.blob.aio.StorageStreamDownloader(Generic[T]):
        container: str
        name: str
        properties: BlobProperties
        size: int

        def __init__(
                self, 
                clients: AzureBlobStorage = None, 
                config: StorageConfiguration = None, 
                start_range: Optional[int] = None, 
                end_range: Optional[int] = None, 
                validate_content: bool = None, 
                encryption_options: Dict[str, Any] = None, 
                max_concurrency: Optional[int] = None, 
                name: str = None, 
                container: str = None, 
                encoding: Optional[str] = None, 
                download_cls: Optional[Callable] = None, 
                **kwargs: Any
            ) -> None: ...

        def __len__(self): ...

        def chunks(self) -> AsyncIterator[bytes]: ...

        async def content_as_bytes(self, max_concurrency: Optional[int] = None) -> bytes: ...

        async def content_as_text(
                self, 
                max_concurrency: Optional[int] = None, 
                encoding: str = "UTF-8"
            ) -> str: ...

        async def download_to_stream(
                self, 
                stream: IO[T], 
                max_concurrency: Optional[int] = None
            ) -> Any: ...

        @overload
        async def read(self, size: int = -1) -> T: ...

        @overload
        async def read(
                self, 
                *, 
                chars: Optional[int] = ...
            ) -> T: ...

        async def readall(self) -> T: ...

        async def readinto(self, stream: IO[bytes]) -> int: ...


```