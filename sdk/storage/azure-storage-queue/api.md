```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.storage.queue

    def azure.storage.queue.generate_account_sas(
            account_name: str, 
            account_key: str, 
            resource_types: Union[ResourceTypes, str], 
            permission: Union[AccountSasPermissions, str], 
            expiry: Union[datetime, str], 
            start: Optional[Union[datetime, str]] = None, 
            ip: Optional[str] = None, 
            *, 
            protocol: Optional[str] = ..., 
            services: Union[Services, str] = Services(queue=True), 
            sts_hook: Optional[Callable[[str], None]] = ..., 
            **kwargs: Any
        ) -> str: ...


    def azure.storage.queue.generate_queue_sas(
            account_name: str, 
            queue_name: str, 
            account_key: Optional[str] = None, 
            permission: Optional[Union[QueueSasPermissions, str]] = None, 
            expiry: Optional[Union[datetime, str]] = None, 
            start: Optional[Union[datetime, str]] = None, 
            policy_id: Optional[str] = None, 
            ip: Optional[str] = None, 
            *, 
            protocol: Optional[str] = ..., 
            sts_hook: Optional[Callable[[str], None]] = ..., 
            user_delegation_key: Optional[UserDelegationKey] = ..., 
            user_delegation_oid: Optional[str] = ..., 
            **kwargs: Any
        ) -> str: ...


    class azure.storage.queue.AccessPolicy(GenAccessPolicy):
        expiry: Optional[Union[datetime, str]]
        permission: Optional[Union[QueueSasPermissions, str]]
        start: Optional[Union[datetime, str]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                permission: Optional[Union[QueueSasPermissions, str]] = None, 
                expiry: Optional[Union[datetime, str]] = None, 
                start: Optional[Union[datetime, str]] = None
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


    class azure.storage.queue.AccountSasPermissions:
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


    class azure.storage.queue.BinaryBase64DecodePolicy(MessageDecodePolicy):
        require_encryption = False

        def __call__(
                self, 
                response: PipelineResponse, 
                obj: Iterable, 
                headers: Dict[str, Any]
            ) -> object: ...

        def __init__(self) -> None: ...

        def configure(
                self, 
                require_encryption: bool, 
                key_encryption_key: Optional[KeyEncryptionKey], 
                resolver: Optional[Callable[[str], KeyEncryptionKey]]
            ) -> None: ...

        def decode(
                self, 
                content: str, 
                response: PipelineResponse
            ) -> bytes: ...


    class azure.storage.queue.BinaryBase64EncodePolicy(MessageEncodePolicy):

        def __call__(self, content: Any) -> str: ...

        def __init__(self) -> None: ...

        def configure(
                self, 
                require_encryption: bool, 
                key_encryption_key: Optional[KeyEncryptionKey], 
                resolver: Optional[Callable[[str], KeyEncryptionKey]], 
                encryption_version: str = _ENCRYPTION_PROTOCOL_V1
            ) -> None: ...

        def encode(self, content: bytes) -> str: ...


    class azure.storage.queue.CorsRule(GeneratedCorsRule):
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
                allowed_headers: Optional[List[str]] = ..., 
                exposed_headers: Optional[List[str]] = ..., 
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


    class azure.storage.queue.ExponentialRetry(StorageRetryPolicy):
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


    class azure.storage.queue.LinearRetry(StorageRetryPolicy):
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


    class azure.storage.queue.LocationMode:
        PRIMARY = primary
        SECONDARY = secondary


    class azure.storage.queue.Metrics(GeneratedMetrics):
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


    class azure.storage.queue.QueueAnalyticsLogging(GeneratedLogging):
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


    class azure.storage.queue.QueueClient(StorageAccountHostsMixin, StorageEncryptionMixin): implements ContextManager 
        property api_version: str    # Read-only
        property location_mode: str
        property primary_endpoint: str    # Read-only
        property primary_hostname: str    # Read-only
        property secondary_endpoint: str    # Read-only
        property secondary_hostname: Optional[str]    # Read-only
        property url: str    # Read-only
        queue_name: str

        def __init__(
                self, 
                account_url: str, 
                queue_name: str, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]] = None, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                message_decode_policy: Optional[Union[BinaryBase64DecodePolicy, TextBase64DecodePolicy]] = ..., 
                message_encode_policy: Optional[Union[BinaryBase64EncodePolicy, TextBase64EncodePolicy]] = ..., 
                secondary_hostname: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                queue_name: str, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]] = None, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                message_decode_policy: Optional[Union[BinaryBase64DecodePolicy, TextBase64DecodePolicy]] = ..., 
                message_encode_policy: Optional[Union[BinaryBase64EncodePolicy, TextBase64EncodePolicy]] = ..., 
                secondary_hostname: Optional[str] = ..., 
                **kwargs: Any
            ) -> Self: ...

        @classmethod
        def from_queue_url(
                cls, 
                queue_url: str, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]] = None, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                message_decode_policy: Optional[Union[BinaryBase64DecodePolicy, TextBase64DecodePolicy]] = ..., 
                message_encode_policy: Optional[Union[BinaryBase64EncodePolicy, TextBase64EncodePolicy]] = ..., 
                secondary_hostname: Optional[str] = ..., 
                **kwargs: Any
            ) -> Self: ...

        @distributed_trace
        def clear_messages(
                self, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @distributed_trace
        def create_queue(
                self, 
                *, 
                metadata: Optional[Dict[str, str]] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_message(
                self, 
                message: Union[str, QueueMessage], 
                pop_receipt: Optional[str] = None, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_queue(
                self, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_queue_access_policy(
                self, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, AccessPolicy]: ...

        @distributed_trace
        def get_queue_properties(
                self, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> QueueProperties: ...

        @distributed_trace
        def peek_messages(
                self, 
                max_messages: Optional[int] = None, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[QueueMessage]: ...

        @distributed_trace
        def receive_message(
                self, 
                *, 
                timeout: Optional[int] = ..., 
                visibility_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Optional[QueueMessage]: ...

        @distributed_trace
        def receive_messages(
                self, 
                *, 
                max_messages: Optional[int] = ..., 
                messages_per_page: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                visibility_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[QueueMessage]: ...

        @distributed_trace
        def send_message(
                self, 
                content: Optional[object], 
                *, 
                time_to_live: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                visibility_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> QueueMessage: ...

        @distributed_trace
        def set_queue_access_policy(
                self, 
                signed_identifiers: Dict[str, AccessPolicy], 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def set_queue_metadata(
                self, 
                metadata: Optional[Dict[str, str]] = None, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace
        def update_message(
                self, 
                message: Union[str, QueueMessage], 
                pop_receipt: Optional[str] = None, 
                content: Optional[object] = None, 
                *, 
                timeout: Optional[int] = ..., 
                visibility_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> QueueMessage: ...


    class azure.storage.queue.QueueMessage(DictMixin):
        content: Any
        dequeue_count: Optional[int]
        expires_on: Optional[datetime]
        id: str
        inserted_on: Optional[datetime]
        next_visible_on: Optional[datetime]
        pop_receipt: Optional[str]

        def __contains__(self, key): ...

        def __delitem__(self, key): ...

        def __eq__(self, other): ...

        def __getitem__(self, key): ...

        def __init__(
                self, 
                content: Optional[Any] = None, 
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


    class azure.storage.queue.QueueProperties(DictMixin):
        approximate_message_count: Optional[int]
        metadata: Optional[Dict[str, str]]
        name: str

        def __contains__(self, key): ...

        def __delitem__(self, key): ...

        def __eq__(self, other): ...

        def __getitem__(self, key): ...

        def __init__(
                self, 
                *, 
                metadata: Optional[Dict[str, str]] = ..., 
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


    class azure.storage.queue.QueueSasPermissions:
        add: bool = False
        process: bool = False
        read: bool = False
        update: bool = False

        def __init__(
                self, 
                read: bool = False, 
                add: bool = False, 
                update: bool = False, 
                process: bool = False
            ) -> None: ...

        def __str__(self): ...

        @classmethod
        def from_string(cls, permission: str) -> Self: ...


    class azure.storage.queue.QueueServiceClient(StorageAccountHostsMixin, StorageEncryptionMixin): implements ContextManager 
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
                secondary_hostname: Optional[str] = ..., 
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
                secondary_hostname: Optional[str] = ..., 
                **kwargs: Any
            ) -> Self: ...

        def close(self) -> None: ...

        @distributed_trace
        def create_queue(
                self, 
                name: str, 
                metadata: Optional[Dict[str, str]] = None, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> QueueClient: ...

        @distributed_trace
        def delete_queue(
                self, 
                queue: Union[QueueProperties, str], 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def get_queue_client(
                self, 
                queue: Union[QueueProperties, str], 
                **kwargs: Any
            ) -> QueueClient: ...

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
                *, 
                delegated_user_tid: Optional[str] = ..., 
                expiry: datetime, 
                start: Optional[datetime] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> UserDelegationKey: ...

        @distributed_trace
        def list_queues(
                self, 
                name_starts_with: Optional[str] = None, 
                include_metadata: Optional[bool] = False, 
                *, 
                results_per_page: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[QueueProperties]: ...

        @distributed_trace
        def set_service_properties(
                self, 
                analytics_logging: Optional[QueueAnalyticsLogging] = None, 
                hour_metrics: Optional[Metrics] = None, 
                minute_metrics: Optional[Metrics] = None, 
                cors: Optional[List[CorsRule]] = None, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.storage.queue.ResourceTypes:
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


    class azure.storage.queue.RetentionPolicy(GeneratedRetentionPolicy):
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


    class azure.storage.queue.Services:

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


    class azure.storage.queue.StorageErrorCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
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


    class azure.storage.queue.TextBase64DecodePolicy(MessageDecodePolicy):
        require_encryption = False

        def __call__(
                self, 
                response: PipelineResponse, 
                obj: Iterable, 
                headers: Dict[str, Any]
            ) -> object: ...

        def __init__(self) -> None: ...

        def configure(
                self, 
                require_encryption: bool, 
                key_encryption_key: Optional[KeyEncryptionKey], 
                resolver: Optional[Callable[[str], KeyEncryptionKey]]
            ) -> None: ...

        def decode(
                self, 
                content: str, 
                response: PipelineResponse
            ) -> str: ...


    class azure.storage.queue.TextBase64EncodePolicy(MessageEncodePolicy):

        def __call__(self, content: Any) -> str: ...

        def __init__(self) -> None: ...

        def configure(
                self, 
                require_encryption: bool, 
                key_encryption_key: Optional[KeyEncryptionKey], 
                resolver: Optional[Callable[[str], KeyEncryptionKey]], 
                encryption_version: str = _ENCRYPTION_PROTOCOL_V1
            ) -> None: ...

        def encode(self, content: str) -> str: ...


    class azure.storage.queue.UserDelegationKey:
        signed_delegated_user_tid: Optional[str]
        signed_expiry: Optional[str]
        signed_oid: Optional[str]
        signed_service: Optional[str]
        signed_start: Optional[str]
        signed_tid: Optional[str]
        signed_version: Optional[str]
        value: Optional[str]

        def __init__(self): ...


namespace azure.storage.queue.aio

    class azure.storage.queue.aio.QueueClient(AsyncStorageAccountHostsMixin, StorageAccountHostsMixin, StorageEncryptionMixin): implements AsyncContextManager 
        property api_version: str    # Read-only
        property location_mode: str
        property primary_endpoint: str    # Read-only
        property primary_hostname: str    # Read-only
        property secondary_endpoint: str    # Read-only
        property secondary_hostname: Optional[str]    # Read-only
        property url: str    # Read-only
        queue_name: str

        def __init__(
                self, 
                account_url: str, 
                queue_name: str, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, AsyncTokenCredential]] = None, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                message_decode_policy: Optional[Union[BinaryBase64DecodePolicy, TextBase64DecodePolicy]] = ..., 
                message_encode_policy: Optional[Union[BinaryBase64EncodePolicy, TextBase64EncodePolicy]] = ..., 
                secondary_hostname: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                queue_name: str, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, AsyncTokenCredential]] = None, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                message_decode_policy: Optional[Union[BinaryBase64DecodePolicy, TextBase64DecodePolicy]] = ..., 
                message_encode_policy: Optional[Union[BinaryBase64EncodePolicy, TextBase64EncodePolicy]] = ..., 
                secondary_hostname: Optional[str] = ..., 
                **kwargs: Any
            ) -> Self: ...

        @classmethod
        def from_queue_url(
                cls, 
                queue_url: str, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, AsyncTokenCredential]] = None, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                message_decode_policy: Optional[Union[BinaryBase64DecodePolicy, TextBase64DecodePolicy]] = ..., 
                message_encode_policy: Optional[Union[BinaryBase64EncodePolicy, TextBase64EncodePolicy]] = ..., 
                secondary_hostname: Optional[str] = ..., 
                **kwargs: Any
            ) -> Self: ...

        @distributed_trace_async
        async def clear_messages(
                self, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def create_queue(
                self, 
                *, 
                metadata: Optional[Dict[str, str]] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_message(
                self, 
                message: Union[str, QueueMessage], 
                pop_receipt: Optional[str] = None, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_queue(
                self, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_queue_access_policy(
                self, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, AccessPolicy]: ...

        @distributed_trace_async
        async def get_queue_properties(
                self, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> QueueProperties: ...

        @distributed_trace_async
        async def peek_messages(
                self, 
                max_messages: Optional[int] = None, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[QueueMessage]: ...

        @distributed_trace_async
        async def receive_message(
                self, 
                *, 
                timeout: Optional[int] = ..., 
                visibility_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Optional[QueueMessage]: ...

        @distributed_trace
        def receive_messages(
                self, 
                *, 
                max_messages: Optional[int] = ..., 
                messages_per_page: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                visibility_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[QueueMessage]: ...

        @distributed_trace_async
        async def send_message(
                self, 
                content: Optional[object], 
                *, 
                time_to_live: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                visibility_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> QueueMessage: ...

        @distributed_trace_async
        async def set_queue_access_policy(
                self, 
                signed_identifiers: Dict[str, AccessPolicy], 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def set_queue_metadata(
                self, 
                metadata: Optional[Dict[str, str]] = None, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace_async
        async def update_message(
                self, 
                message: Union[str, QueueMessage], 
                pop_receipt: Optional[str] = None, 
                content: Optional[object] = None, 
                *, 
                timeout: Optional[int] = ..., 
                visibility_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> QueueMessage: ...


    class azure.storage.queue.aio.QueueServiceClient(AsyncStorageAccountHostsMixin, StorageAccountHostsMixin, StorageEncryptionMixin): implements AsyncContextManager 
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
                secondary_hostname: Optional[str] = ..., 
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
                secondary_hostname: Optional[str] = ..., 
                **kwargs: Any
            ) -> Self: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def create_queue(
                self, 
                name: str, 
                metadata: Optional[Dict[str, str]] = None, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> QueueClient: ...

        @distributed_trace_async
        async def delete_queue(
                self, 
                queue: Union[QueueProperties, str], 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def get_queue_client(
                self, 
                queue: Union[QueueProperties, str], 
                **kwargs: Any
            ) -> QueueClient: ...

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
                *, 
                delegated_user_tid: Optional[str] = ..., 
                expiry: datetime, 
                start: Optional[datetime] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> UserDelegationKey: ...

        @distributed_trace
        def list_queues(
                self, 
                name_starts_with: Optional[str] = None, 
                include_metadata: Optional[bool] = False, 
                *, 
                results_per_page: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged: ...

        @distributed_trace_async
        async def set_service_properties(
                self, 
                analytics_logging: Optional[QueueAnalyticsLogging] = None, 
                hour_metrics: Optional[Metrics] = None, 
                minute_metrics: Optional[Metrics] = None, 
                cors: Optional[List[CorsRule]] = None, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...


```