```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.storage.fileshare

    def azure.storage.fileshare.generate_account_sas(
            account_name: str, 
            account_key: str, 
            resource_types: Union[ResourceTypes, str], 
            permission: Union[AccountSasPermissions, str], 
            expiry: Union[datetime, str], 
            start: Optional[Union[datetime, str]] = None, 
            ip: Optional[str] = None, 
            *, 
            protocol: Optional[str] = ..., 
            services: Union[Services, str] = Services(fileshare=True), 
            sts_hook: Optional[Callable[[str], None]] = ..., 
            **kwargs: Any
        ) -> str: ...


    def azure.storage.fileshare.generate_file_sas(
            account_name: str, 
            share_name: str, 
            file_path: List[str], 
            account_key: Optional[str] = None, 
            permission: Optional[Union[FileSasPermissions, str]] = None, 
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
            protocol: Optional[str] = ..., 
            sts_hook: Optional[Callable[[str], None]] = ..., 
            user_delegation_key: Optional[UserDelegationKey] = ..., 
            user_delegation_oid: Optional[str] = ..., 
            **kwargs: Any
        ) -> str: ...


    def azure.storage.fileshare.generate_share_sas(
            account_name: str, 
            share_name: str, 
            account_key: Optional[str] = None, 
            permission: Optional[Union[ShareSasPermissions, str]] = None, 
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
            protocol: Optional[str] = ..., 
            sts_hook: Optional[Callable[[str], None]] = ..., 
            user_delegation_key: Optional[UserDelegationKey] = ..., 
            user_delegation_oid: Optional[str] = ..., 
            **kwargs: Any
        ) -> str: ...


    class azure.storage.fileshare.AccessPolicy(GenAccessPolicy):
        expiry: Optional[Union[datetime, str]]
        permission: Optional[Union[ShareSasPermissions, str]]
        start: Optional[Union[datetime, str]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                permission: Optional[Union[ShareSasPermissions, str]] = None, 
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


    class azure.storage.fileshare.AccountSasPermissions:
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


    class azure.storage.fileshare.ContentSettings(DictMixin):
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


    class azure.storage.fileshare.CorsRule(GeneratedCorsRule):
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


    class azure.storage.fileshare.DirectoryProperties(DictMixin):
        change_time: Optional[Union[datetime, str]]
        creation_time: Optional[Union[datetime, str]]
        etag: str
        file_attributes: Union[str, NTFSAttributes]
        file_id: str
        file_mode: Optional[str]
        group: Optional[str]
        is_directory: bool = True
        last_access_time: Optional[datetime]
        last_modified: datetime
        last_write_time: Optional[Union[datetime, str]]
        metadata: Dict[str, str]
        name: str
        nfs_file_type: Optional[Literal["Directory"]]
        owner: Optional[str]
        parent_id: str
        permission_key: str
        server_encrypted: bool

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


    class azure.storage.fileshare.ExponentialRetry(StorageRetryPolicy):
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


    class azure.storage.fileshare.FileProperties(DictMixin):
        change_time: Optional[Union[datetime, str]]
        content_length: int
        content_range: Optional[str]
        content_settings: ContentSettings
        copy: CopyProperties
        creation_time: Optional[Union[datetime, str]]
        etag: str
        file_attributes: Union[str, NTFSAttributes]
        file_id: str
        file_mode: Optional[str]
        file_type: str
        group: Optional[str]
        is_directory: bool = False
        last_access_time: Optional[datetime]
        last_modified: datetime
        last_write_time: Optional[Union[datetime, str]]
        lease: LeaseProperties
        link_count: Optional[int]
        metadata: Dict[str, str]
        name: str
        nfs_file_type: Optional[Literal["Regular"]]
        owner: Optional[str]
        parent_id: Optional[str]
        path: Optional[str]
        permission_key: str
        server_encrypted: bool
        share: Optional[str]
        size: int
        snapshot: Optional[str]

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


    class azure.storage.fileshare.FileSasPermissions:
        create: bool = False
        delete: bool = False
        read: bool = False
        write: bool = False

        def __init__(
                self, 
                read: bool = False, 
                create: bool = False, 
                write: bool = False, 
                delete: bool = False
            ) -> None: ...

        def __str__(self): ...

        @classmethod
        def from_string(cls, permission: str) -> Self: ...


    class azure.storage.fileshare.Handle(DictMixin):
        access_rights: List[Literal["Read", "Write", "Delete"]]
        client_ip: str
        client_name: str
        file_id: str
        id: str
        last_reconnect_time: Optional[datetime]
        open_time: datetime
        parent_id: str
        path: str
        session_id: str

        def __contains__(self, key): ...

        def __delitem__(self, key): ...

        def __eq__(self, other): ...

        def __getitem__(self, key): ...

        def __init__(
                self, 
                *, 
                access_rights: List[Literal[Read, Write, Delete]] = ..., 
                client_ip: Optional[str] = ..., 
                client_name: Optional[str] = ..., 
                file_id: Optional[str] = ..., 
                handle_id: Optional[str] = ..., 
                last_reconnect_time: Optional[datetime] = ..., 
                open_time: Optional[datetime] = ..., 
                parent_id: Optional[str] = ..., 
                path: Optional[str] = ..., 
                session_id: Optional[str] = ..., 
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


    class azure.storage.fileshare.LinearRetry(StorageRetryPolicy):
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


    class azure.storage.fileshare.LocationMode:
        PRIMARY = primary
        SECONDARY = secondary


    class azure.storage.fileshare.Metrics(GeneratedMetrics):
        enabled: bool = False
        include_apis: bool
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


    class azure.storage.fileshare.NTFSAttributes:
        archive: bool = False
        directory: bool = False
        hidden: bool = False
        no_scrub_data: bool = False
        none: bool = False
        not_content_indexed: bool = False
        offline: bool = False
        read_only: bool = False
        system: bool = False
        temporary: bool = False

        def __init__(
                self, 
                read_only: bool = False, 
                hidden: bool = False, 
                system: bool = False, 
                none: bool = False, 
                directory: bool = False, 
                archive: bool = False, 
                temporary: bool = False, 
                offline: bool = False, 
                not_content_indexed: bool = False, 
                no_scrub_data: bool = False
            ) -> None: ...

        def __str__(self): ...

        @classmethod
        def from_string(cls, string: str) -> Self: ...


    class azure.storage.fileshare.NfsEncryptionInTransit(GeneratedNfsEncryptionInTransit):
        required: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                required: bool, 
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


    class azure.storage.fileshare.ResourceTypes:
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


    class azure.storage.fileshare.RetentionPolicy(GeneratedRetentionPolicy):
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


    class azure.storage.fileshare.Services:

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


    class azure.storage.fileshare.ShareAccessTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COOL = "Cool"
        HOT = "Hot"
        PREMIUM = "Premium"
        TRANSACTION_OPTIMIZED = "TransactionOptimized"


    class azure.storage.fileshare.ShareClient(StorageAccountHostsMixin): implements ContextManager 
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
                share_name: str, 
                snapshot: Optional[Union[str, Dict[str, Any]]] = None, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]] = None, 
                *, 
                allow_source_trailing_dot: Optional[bool] = ..., 
                allow_trailing_dot: Optional[bool] = ..., 
                api_version: Optional[str] = ..., 
                max_range_size: Optional[int] = ..., 
                secondary_hostname: Optional[str] = ..., 
                token_intent: Optional[Literal[backup]] = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                share_name: str, 
                snapshot: Optional[Union[str, Dict[str, Any]]] = None, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]] = None, 
                **kwargs: Any
            ) -> Self: ...

        @classmethod
        def from_share_url(
                cls, 
                share_url: str, 
                snapshot: Optional[Union[str, Dict[str, Any]]] = None, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]] = None, 
                **kwargs: Any
            ) -> Self: ...

        @distributed_trace
        def acquire_lease(
                self, 
                *, 
                lease_duration: Optional[int] = ..., 
                lease_id: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ShareLeaseClient: ...

        def close(self) -> None: ...

        @distributed_trace
        def create_directory(
                self, 
                directory_name: str, 
                *, 
                file_mode: Optional[str] = ..., 
                file_property_semantics: Optional[Literal[New, Restore]] = ..., 
                group: Optional[str] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                owner: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ShareDirectoryClient: ...

        @distributed_trace
        def create_permission_for_share(
                self, 
                file_permission: str, 
                *, 
                file_permission_format: Literal[sddl, binary] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Optional[str]: ...

        @distributed_trace
        def create_share(
                self, 
                *, 
                access_tier: Union[str, ShareAccessTier] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                paid_bursting_bandwidth_mibps: Optional[int] = ..., 
                paid_bursting_enabled: Optional[bool] = ..., 
                paid_bursting_iops: Optional[int] = ..., 
                protocols: Union[str, ShareProtocols] = ..., 
                provisioned_bandwidth_mibps: Optional[int] = ..., 
                provisioned_iops: Optional[int] = ..., 
                quota: Optional[int] = ..., 
                root_squash: Union[str, ShareRootSquash] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace
        def create_snapshot(
                self, 
                *, 
                metadata: Optional[dict[str, str]] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace
        def delete_directory(
                self, 
                directory_name: str, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_share(
                self, 
                delete_snapshots: Optional[Union[bool, Literal[include, include-leased]]] = False, 
                *, 
                lease = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def get_directory_client(self, directory_path: Optional[str] = None) -> ShareDirectoryClient: ...

        def get_file_client(self, file_path: str) -> ShareFileClient: ...

        @distributed_trace
        def get_permission_for_share(
                self, 
                permission_key: str, 
                *, 
                file_permission_format: Literal[sddl, binary] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> str: ...

        @distributed_trace
        def get_share_access_policy(
                self, 
                *, 
                lease = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace
        def get_share_properties(
                self, 
                *, 
                lease = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ShareProperties: ...

        @distributed_trace
        def get_share_stats(
                self, 
                *, 
                lease = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> int: ...

        @distributed_trace
        def list_directories_and_files(
                self, 
                directory_name: Optional[str] = None, 
                name_starts_with: Optional[str] = None, 
                marker: Optional[str] = None, 
                *, 
                include: Optional[List[str]] = ..., 
                include_extended_info: Optional[bool] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Union[DirectoryProperties, FileProperties]]: ...

        @distributed_trace
        def set_share_access_policy(
                self, 
                signed_identifiers: Dict[str, AccessPolicy], 
                *, 
                lease = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace
        def set_share_metadata(
                self, 
                metadata: Dict[str, str], 
                *, 
                lease = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace
        def set_share_properties(
                self, 
                *, 
                access_tier: Union[str, ShareAccessTier] = ..., 
                lease = ..., 
                paid_bursting_bandwidth_mibps: Optional[int] = ..., 
                paid_bursting_enabled: Optional[bool] = ..., 
                paid_bursting_iops: Optional[int] = ..., 
                provisioned_bandwidth_mibps: Optional[int] = ..., 
                provisioned_iops: Optional[int] = ..., 
                quota: Optional[int] = ..., 
                root_squash: Union[str, ShareRootSquash] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace
        def set_share_quota(
                self, 
                quota: int, 
                *, 
                lease = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...


    class azure.storage.fileshare.ShareDirectoryClient(StorageAccountHostsMixin): implements ContextManager 
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
                share_name: str, 
                directory_path: str, 
                snapshot: Optional[Union[str, Dict[str, Any]]] = None, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]] = None, 
                *, 
                allow_source_trailing_dot: Optional[bool] = ..., 
                allow_trailing_dot: Optional[bool] = ..., 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                max_range_size: Optional[int] = ..., 
                secondary_hostname: Optional[str] = ..., 
                token_intent: Optional[Literal[backup]] = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                share_name: str, 
                directory_path: str, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]] = None, 
                *, 
                audience: Optional[str] = ..., 
                **kwargs: Any
            ) -> Self: ...

        @classmethod
        def from_directory_url(
                cls, 
                directory_url: str, 
                snapshot: Optional[Union[str, Dict[str, Any]]] = None, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]] = None, 
                *, 
                audience: Optional[str] = ..., 
                **kwargs: Any
            ) -> Self: ...

        def close(self) -> None: ...

        @distributed_trace
        def close_all_handles(
                self, 
                recursive: bool = False, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, int]: ...

        @distributed_trace
        def close_handle(
                self, 
                handle: Union[str, Handle], 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, int]: ...

        @distributed_trace
        def create_directory(
                self, 
                *, 
                file_attributes: Union[str, NTFSAttributes, None] = ..., 
                file_change_time: Union[str, datetime] = ..., 
                file_creation_time: Union[str, datetime, None] = ..., 
                file_last_write_time: Union[str, datetime, None] = ..., 
                file_mode: Optional[str] = ..., 
                file_permission: Optional[str] = ..., 
                file_permission_format: Literal[sddl, binary] = ..., 
                file_permission_key: Optional[str] = ..., 
                file_property_semantics: Optional[Literal[New, Restore]] = ..., 
                group: Optional[str] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                owner: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace
        def create_subdirectory(
                self, 
                directory_name: str, 
                *, 
                metadata: Optional[dict[str, str]] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ShareDirectoryClient: ...

        @distributed_trace
        def delete_directory(
                self, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_file(
                self, 
                file_name: str, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_subdirectory(
                self, 
                directory_name: str, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def exists(self, **kwargs: Any) -> bool: ...

        @distributed_trace
        def get_directory_properties(
                self, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> DirectoryProperties: ...

        def get_file_client(
                self, 
                file_name: str, 
                **kwargs: Any
            ) -> ShareFileClient: ...

        def get_subdirectory_client(
                self, 
                directory_name: str, 
                **kwargs: Any
            ) -> ShareDirectoryClient: ...

        @distributed_trace
        def list_directories_and_files(
                self, 
                name_starts_with: Optional[str] = None, 
                *, 
                include: Optional[List[str]] = ..., 
                include_extended_info: Optional[bool] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Union[DirectoryProperties, FileProperties]]: ...

        @distributed_trace
        def list_handles(
                self, 
                recursive: bool = False, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Handle]: ...

        @distributed_trace
        def rename_directory(
                self, 
                new_name: str, 
                *, 
                destination_lease: Union[ShareLeaseClient, str] = ..., 
                file_attributes: Union[NTFSAttributes, str] = ..., 
                file_change_time: Union[str, datetime] = ..., 
                file_creation_time: Union[datetime, str] = ..., 
                file_last_write_time: Union[datetime, str] = ..., 
                file_permission: Optional[str] = ..., 
                file_permission_format: Literal[sddl, binary] = ..., 
                file_permission_key: Optional[str] = ..., 
                ignore_read_only: Optional[bool] = ..., 
                metadata: Optional[Dict[str,str]] = ..., 
                overwrite: Optional[bool] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ShareDirectoryClient: ...

        @distributed_trace
        def set_directory_metadata(
                self, 
                metadata: Dict[str, Any], 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace
        def set_http_headers(
                self, 
                file_attributes: Optional[Union[str, NTFSAttributes]] = None, 
                file_creation_time: Optional[Union[str, datetime]] = None, 
                file_last_write_time: Optional[Union[str, datetime]] = None, 
                file_permission: Optional[str] = None, 
                permission_key: Optional[str] = None, 
                *, 
                file_change_time: Union[str, datetime] = ..., 
                file_mode: Optional[str] = ..., 
                file_permission_format: Literal[sddl, binary] = ..., 
                group: Optional[str] = ..., 
                owner: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace
        def upload_file(
                self, 
                file_name: str, 
                data: Union[bytes, str, Iterable[AnyStr], IO[AnyStr]], 
                length: Optional[int] = None, 
                *, 
                content_settings: Optional[ContentSettings] = ..., 
                encoding: Optional[str] = ..., 
                max_concurrency: Optional[int] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                progress_hook: Callable[[int, Optional[int]], None] = ..., 
                timeout: Optional[int] = ..., 
                validate_content: Optional[bool] = ..., 
                **kwargs: Any
            ) -> ShareFileClient: ...


    class azure.storage.fileshare.ShareFileClient(StorageAccountHostsMixin): implements ContextManager 
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
                share_name: str, 
                file_path: str, 
                snapshot: Optional[Union[str, Dict[str, Any]]] = None, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]] = None, 
                *, 
                allow_source_trailing_dot: Optional[bool] = ..., 
                allow_trailing_dot: Optional[bool] = ..., 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                max_range_size: Optional[int] = ..., 
                secondary_hostname: Optional[str] = ..., 
                token_intent: Optional[Literal[backup]] = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                share_name: str, 
                file_path: str, 
                snapshot: Optional[Union[str, Dict[str, Any]]] = None, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]] = None, 
                *, 
                audience: Optional[str] = ..., 
                **kwargs: Any
            ) -> Self: ...

        @classmethod
        def from_file_url(
                cls, 
                file_url: str, 
                snapshot: Optional[Union[str, Dict[str, Any]]] = None, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]] = None, 
                *, 
                audience: Optional[str] = ..., 
                **kwargs: Any
            ) -> Self: ...

        @distributed_trace
        def abort_copy(
                self, 
                copy_id: Union[str, FileProperties], 
                *, 
                lease: Union[ShareLeaseClient, str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def acquire_lease(
                self, 
                lease_id: Optional[str] = None, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ShareLeaseClient: ...

        @distributed_trace
        def clear_range(
                self, 
                offset: int, 
                length: int, 
                *, 
                lease: Union[ShareLeaseClient, str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        def close(self) -> None: ...

        @distributed_trace
        def close_all_handles(
                self, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, int]: ...

        @distributed_trace
        def close_handle(
                self, 
                handle: Union[str, Handle], 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, int]: ...

        @distributed_trace
        def create_file(
                self, 
                size: int, 
                file_attributes: Optional[Union[str, NTFSAttributes]] = None, 
                file_creation_time: Optional[Union[str, datetime]] = None, 
                file_last_write_time: Optional[Union[str, datetime]] = None, 
                file_permission: Optional[str] = None, 
                permission_key: Optional[str] = None, 
                *, 
                content_settings: Optional[ContentSettings] = ..., 
                data: bytes = ..., 
                file_change_time: Union[str, datetime] = ..., 
                file_mode: Optional[str] = ..., 
                file_permission_format: Literal[sddl, binary] = ..., 
                file_property_semantics: Optional[Literal[New, Restore]] = ..., 
                group: Optional[str] = ..., 
                lease: Union[ShareLeaseClient, str] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                owner: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace
        def create_hardlink(
                self, 
                target: str, 
                *, 
                lease: Optional[Union[ShareLeaseClient, str]] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace
        def create_symlink(
                self, 
                target: str, 
                *, 
                file_creation_time: Optional[Union[str, datetime]] = ..., 
                file_last_write_time: Optional[Union[str, datetime]] = ..., 
                group: Optional[str] = ..., 
                lease: Optional[Union[ShareLeaseClient, str]] = ..., 
                metadata: Optional[Dict[str, str]] = ..., 
                owner: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace
        def delete_file(
                self, 
                *, 
                lease: Union[ShareLeaseClient, str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def download_file(
                self, 
                offset: Optional[int] = None, 
                length: Optional[int] = None, 
                *, 
                decompress: Optional[bool] = ..., 
                lease: Union[ShareLeaseClient, str] = ..., 
                max_concurrency: Optional[int] = ..., 
                progress_hook: Callable[[int, int], None] = ..., 
                timeout: Optional[int] = ..., 
                validate_content: Optional[bool] = ..., 
                **kwargs: Any
            ) -> StorageStreamDownloader: ...

        @distributed_trace
        def exists(
                self, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> bool: ...

        @distributed_trace
        def get_file_properties(
                self, 
                *, 
                lease: Union[ShareLeaseClient, str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> FileProperties: ...

        @distributed_trace
        def get_ranges(
                self, 
                offset: Optional[int] = None, 
                length: Optional[int] = None, 
                *, 
                lease: Union[ShareLeaseClient, str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[Dict[str, int]]: ...

        @distributed_trace
        def get_ranges_diff(
                self, 
                previous_sharesnapshot: Union[str, Dict[str, Any]], 
                offset: Optional[int] = None, 
                length: Optional[int] = None, 
                *, 
                include_renames: Optional[bool] = ..., 
                lease: Union[ShareLeaseClient, str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Tuple[List[Dict[str, int]], List[Dict[str, int]]]: ...

        @distributed_trace
        def get_symlink(
                self, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace
        def list_handles(
                self, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Handle]: ...

        @distributed_trace
        def rename_file(
                self, 
                new_name: str, 
                *, 
                content_type: Optional[str] = ..., 
                destination_lease: Union[ShareLeaseClient, str] = ..., 
                file_attributes: Union[NTFSAttributes, str] = ..., 
                file_change_time: Union[str, datetime] = ..., 
                file_creation_time: Union[datetime, str] = ..., 
                file_last_write_time: Union[datetime, str] = ..., 
                file_permission: Optional[str] = ..., 
                file_permission_format: Literal[sddl, binary] = ..., 
                file_permission_key: Optional[str] = ..., 
                ignore_read_only: Optional[bool] = ..., 
                metadata: Optional[Dict[str,str]] = ..., 
                overwrite: Optional[bool] = ..., 
                source_lease: Union[ShareLeaseClient, str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ShareFileClient: ...

        @distributed_trace
        def resize_file(
                self, 
                size: int, 
                *, 
                lease: Union[ShareLeaseClient, str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace
        def set_file_metadata(
                self, 
                metadata: Optional[Dict[str, Any]] = None, 
                *, 
                lease: Union[ShareLeaseClient, str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace
        def set_http_headers(
                self, 
                content_settings: ContentSettings, 
                file_attributes: Optional[Union[str, NTFSAttributes]] = None, 
                file_creation_time: Optional[Union[str, datetime]] = None, 
                file_last_write_time: Optional[Union[str, datetime]] = None, 
                file_permission: Optional[str] = None, 
                permission_key: Optional[str] = None, 
                *, 
                file_change_time: Union[str, datetime] = ..., 
                file_mode: Optional[str] = ..., 
                file_permission_format: Literal[sddl, binary] = ..., 
                group: Optional[str] = ..., 
                lease: Union[ShareLeaseClient, str] = ..., 
                owner: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace
        def start_copy_from_url(
                self, 
                source_url: str, 
                *, 
                file_attributes: Union[str, NTFSAttributes] = ..., 
                file_change_time: Union[str, datetime] = ..., 
                file_creation_time: Union[str, datetime] = ..., 
                file_last_write_time: Union[str, datetime] = ..., 
                file_mode: Optional[str] = ..., 
                file_mode_copy_mode: Literal[source, override] = ..., 
                file_permission: Optional[str] = ..., 
                file_permission_format: Literal[sddl, binary] = ..., 
                group: Optional[str] = ..., 
                ignore_read_only: Optional[bool] = ..., 
                lease: Union[ShareLeaseClient, str] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                owner: Optional[str] = ..., 
                owner_copy_mode: Literal[source, override] = ..., 
                permission_key: Optional[str] = ..., 
                set_archive_attribute: Optional[bool] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace
        def upload_file(
                self, 
                data: Union[bytes, str, Iterable[AnyStr], IO[bytes]], 
                length: Optional[int] = None, 
                file_attributes: Optional[Union[str, NTFSAttributes]] = None, 
                file_creation_time: Optional[Union[str, datetime]] = None, 
                file_last_write_time: Optional[Union[str, datetime]] = None, 
                file_permission: Optional[str] = None, 
                permission_key: Optional[str] = None, 
                *, 
                content_settings: Optional[ContentSettings] = ..., 
                encoding: Optional[str] = ..., 
                file_change_time: Union[str, datetime] = ..., 
                lease: Union[ShareLeaseClient, str] = ..., 
                max_concurrency: Optional[int] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                progress_hook: Callable[[int, Optional[int]], None] = ..., 
                timeout: Optional[int] = ..., 
                validate_content: Optional[bool] = ..., 
                **kwargs
            ) -> Dict[str, Any]: ...

        @distributed_trace
        def upload_range(
                self, 
                data: bytes, 
                offset: int, 
                length: int, 
                *, 
                encoding: Optional[str] = ..., 
                file_last_write_mode: Literal[preserve, now] = ..., 
                lease: Union[ShareLeaseClient, str] = ..., 
                timeout: Optional[int] = ..., 
                validate_content: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace
        def upload_range_from_url(
                self, 
                source_url: str, 
                offset: int, 
                length: int, 
                source_offset: int, 
                *, 
                file_last_write_mode: Literal[preserve, now] = ..., 
                lease: Union[ShareLeaseClient, str] = ..., 
                source_authorization: Optional[str] = ..., 
                source_etag: Optional[str] = ..., 
                source_if_modified_since: Optional[datetime] = ..., 
                source_if_unmodified_since: Optional[datetime] = ..., 
                source_match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...


    class azure.storage.fileshare.ShareLeaseClient: implements ContextManager 
        etag: Optional[str]
        id: str
        last_modified: Optional[datetime]

        def __init__(
                self, 
                client: Union[ShareFileClient, ShareClient], 
                lease_id: Optional[str] = None
            ) -> None: ...

        @distributed_trace
        def acquire(
                self, 
                *, 
                lease_duration: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def break_lease(
                self, 
                *, 
                lease_break_period: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> int: ...

        @distributed_trace
        def change(
                self, 
                proposed_lease_id: str, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def release(
                self, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def renew(
                self, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.storage.fileshare.ShareNfsSettings(GeneratedShareNfsSettings):
        encryption_in_transit: NfsEncryptionInTransit

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                encryption_in_transit: NfsEncryptionInTransit, 
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


    class azure.storage.fileshare.ShareProperties(DictMixin):
        access_tier: str
        deleted: Optional[bool]
        deleted_time: Optional[datetime]
        enable_snapshot_virtual_directory_access: Optional[bool]
        etag: str
        last_modified: datetime
        lease: LeaseProperties
        metadata: Dict[str, str]
        name: str
        next_allowed_quota_downgrade_time: Optional[str]
        next_provisioned_bandwidth_downgrade: Optional[datetime]
        next_provisioned_iops_downgrade: Optional[datetime]
        paid_bursting_bandwidth_mibps: Optional[int]
        paid_bursting_enabled: Optional[int]
        paid_bursting_iops: Optional[int]
        protocols: Optional[List[str]]
        provisioned_bandwidth: Optional[int]
        provisioned_egress_mbps: Optional[int]
        provisioned_ingress_mbps: Optional[int]
        provisioned_iops: Optional[int]
        quota: int
        remaining_retention_days: Optional[int]
        root_squash: Optional[Union[ShareRootSquash, str]]
        snapshot: Optional[str]
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


    class azure.storage.fileshare.ShareProtocolSettings(GeneratedShareProtocolSettings):
        nfs: Optional[ShareNfsSettings]
        smb: Optional[ShareSmbSettings]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                nfs: Optional[ShareNfsSettings] = ..., 
                smb: Optional[ShareSmbSettings] = ..., 
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


    class azure.storage.fileshare.ShareProtocols(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NFS = "NFS"
        SMB = "SMB"


    class azure.storage.fileshare.ShareRootSquash(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL_SQUASH = "AllSquash"
        NO_ROOT_SQUASH = "NoRootSquash"
        ROOT_SQUASH = "RootSquash"


    class azure.storage.fileshare.ShareSasPermissions:
        create: bool = False
        delete: bool = False
        list: bool = False
        read: bool = False
        write: bool = False

        def __init__(
                self, 
                read: bool = False, 
                write: bool = False, 
                delete: bool = False, 
                list: bool = False, 
                create: bool = False
            ) -> None: ...

        def __str__(self) -> str: ...

        @classmethod
        def from_string(cls, permission: str) -> Self: ...


    class azure.storage.fileshare.ShareServiceClient(StorageAccountHostsMixin): implements ContextManager 
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
                allow_source_trailing_dot: Optional[bool] = ..., 
                allow_trailing_dot: Optional[bool] = ..., 
                api_version: Optional[str] = ..., 
                max_range_size: Optional[int] = ..., 
                secondary_hostname: Optional[str] = ..., 
                token_intent: Optional[Literal[backup]] = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]] = None, 
                **kwargs: Any
            ) -> Self: ...

        def close(self) -> None: ...

        @distributed_trace
        def create_share(
                self, 
                share_name: str, 
                *, 
                provisioned_bandwidth_mibps: Optional[int] = ..., 
                provisioned_iops: Optional[int] = ..., 
                quota: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ShareClient: ...

        @distributed_trace
        def delete_share(
                self, 
                share_name: Union[ShareProperties, str], 
                delete_snapshots: Optional[bool] = False, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_service_properties(
                self, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        def get_share_client(
                self, 
                share: Union[ShareProperties, str], 
                snapshot: Optional[Union[Dict[str, Any], str]] = None
            ) -> ShareClient: ...

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
        def list_shares(
                self, 
                name_starts_with: Optional[str] = None, 
                include_metadata: Optional[bool] = False, 
                include_snapshots: Optional[bool] = False, 
                *, 
                include_deleted: Optional[bool] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ShareProperties]: ...

        @distributed_trace
        def set_service_properties(
                self, 
                hour_metrics: Optional[Metrics] = None, 
                minute_metrics: Optional[Metrics] = None, 
                cors: Optional[List[CorsRule]] = None, 
                protocol: Optional[ShareProtocolSettings] = None, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def undelete_share(
                self, 
                deleted_share_name: str, 
                deleted_share_version: str, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ShareClient: ...


    class azure.storage.fileshare.ShareSmbSettings(GeneratedShareSmbSettings):
        encryption_in_transit: Optional[SmbEncryptionInTransit]
        multichannel: Optional[SmbMultichannel]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                encryption_in_transit: Optional[SmbEncryptionInTransit] = ..., 
                multichannel: Optional[SmbMultichannel] = ..., 
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


    class azure.storage.fileshare.SmbEncryptionInTransit(GeneratedSmbEncryptionInTransit):
        required: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                required: bool, 
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


    class azure.storage.fileshare.SmbMultichannel(GeneratedSmbMultichannel):
        enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enabled: bool, 
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


    class azure.storage.fileshare.StorageErrorCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
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


    class azure.storage.fileshare.UserDelegationKey:
        signed_delegated_user_tid: Optional[str]
        signed_expiry: Optional[str]
        signed_oid: Optional[str]
        signed_service: Optional[str]
        signed_start: Optional[str]
        signed_tid: Optional[str]
        signed_version: Optional[str]
        value: Optional[str]

        def __init__(self): ...


namespace azure.storage.fileshare.aio

    class azure.storage.fileshare.aio.ShareClient(AsyncStorageAccountHostsMixin, StorageAccountHostsMixin): implements AsyncContextManager 
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
                share_name: str, 
                snapshot: Optional[Union[str, Dict[str, Any]]] = None, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, AsyncTokenCredential]] = None, 
                *, 
                allow_source_trailing_dot: Optional[bool] = ..., 
                allow_trailing_dot: Optional[bool] = ..., 
                api_version: Optional[str] = ..., 
                max_range_size: Optional[int] = ..., 
                secondary_hostname: Optional[str] = ..., 
                token_intent: Optional[Literal[backup]] = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                share_name: str, 
                snapshot: Optional[Union[str, Dict[str, Any]]] = None, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, AsyncTokenCredential]] = None, 
                **kwargs: Any
            ) -> Self: ...

        @classmethod
        def from_share_url(
                cls, 
                share_url: str, 
                snapshot: Optional[Union[str, Dict[str, Any]]] = None, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, AsyncTokenCredential]] = None, 
                **kwargs: Any
            ) -> Self: ...

        @distributed_trace_async
        async def acquire_lease(
                self, 
                *, 
                lease_duration: Optional[int] = ..., 
                lease_id: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ShareLeaseClient: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def create_directory(
                self, 
                directory_name: str, 
                *, 
                file_mode: Optional[str] = ..., 
                file_property_semantics: Optional[Literal[New, Restore]] = ..., 
                group: Optional[str] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                owner: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ShareDirectoryClient: ...

        @distributed_trace_async
        async def create_permission_for_share(
                self, 
                file_permission: str, 
                *, 
                file_permission_format: Literal[sddl, binary] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Optional[str]: ...

        @distributed_trace_async
        async def create_share(
                self, 
                *, 
                access_tier: Union[str, ShareAccessTier] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                paid_bursting_bandwidth_mibps: Optional[int] = ..., 
                paid_bursting_enabled: Optional[bool] = ..., 
                paid_bursting_iops: Optional[int] = ..., 
                protocols: Union[str, ShareProtocols] = ..., 
                provisioned_bandwidth_mibps: Optional[int] = ..., 
                provisioned_iops: Optional[int] = ..., 
                quota: Optional[int] = ..., 
                root_squash: Union[str, ShareRootSquash] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace_async
        async def create_snapshot(
                self, 
                *, 
                metadata: Optional[dict[str, str]] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace_async
        async def delete_directory(
                self, 
                directory_name: str, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_share(
                self, 
                delete_snapshots: Optional[Union[bool, Literal[include, include-leased]]] = False, 
                *, 
                lease = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def get_directory_client(self, directory_path: Optional[str] = None) -> ShareDirectoryClient: ...

        def get_file_client(self, file_path: str) -> ShareFileClient: ...

        @distributed_trace_async
        async def get_permission_for_share(
                self, 
                permission_key: str, 
                *, 
                file_permission_format: Literal[sddl, binary] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> str: ...

        @distributed_trace_async
        async def get_share_access_policy(
                self, 
                *, 
                lease = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace_async
        async def get_share_properties(
                self, 
                *, 
                lease = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ShareProperties: ...

        @distributed_trace_async
        async def get_share_stats(
                self, 
                *, 
                lease = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> int: ...

        @distributed_trace
        def list_directories_and_files(
                self, 
                directory_name: Optional[str] = None, 
                name_starts_with: Optional[str] = None, 
                marker: Optional[str] = None, 
                *, 
                include: Optional[List[str]] = ..., 
                include_extended_info: Optional[bool] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Union[DirectoryProperties, FileProperties]]: ...

        @distributed_trace_async
        async def set_share_access_policy(
                self, 
                signed_identifiers: Dict[str, AccessPolicy], 
                *, 
                lease = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace_async
        async def set_share_metadata(
                self, 
                metadata: Dict[str, str], 
                *, 
                lease = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace_async
        async def set_share_properties(
                self, 
                *, 
                access_tier: Union[str, ShareAccessTier] = ..., 
                lease = ..., 
                paid_bursting_bandwidth_mibps: Optional[int] = ..., 
                paid_bursting_enabled: Optional[bool] = ..., 
                paid_bursting_iops: Optional[int] = ..., 
                provisioned_bandwidth_mibps: Optional[int] = ..., 
                provisioned_iops: Optional[int] = ..., 
                quota: Optional[int] = ..., 
                root_squash: Union[str, ShareRootSquash] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace_async
        async def set_share_quota(
                self, 
                quota: int, 
                *, 
                lease = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...


    class azure.storage.fileshare.aio.ShareDirectoryClient(AsyncStorageAccountHostsMixin, StorageAccountHostsMixin): implements AsyncContextManager 
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
                share_name: str, 
                directory_path: str, 
                snapshot: Optional[Union[str, Dict[str, Any]]] = None, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, AsyncTokenCredential]] = None, 
                *, 
                allow_source_trailing_dot: Optional[bool] = ..., 
                allow_trailing_dot: Optional[bool] = ..., 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                max_range_size: Optional[int] = ..., 
                secondary_hostname: Optional[str] = ..., 
                token_intent: Optional[Literal[backup]] = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                share_name: str, 
                directory_path: str, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, AsyncTokenCredential]] = None, 
                *, 
                audience: Optional[str] = ..., 
                **kwargs: Any
            ) -> Self: ...

        @classmethod
        def from_directory_url(
                cls, 
                directory_url: str, 
                snapshot: Optional[Union[str, Dict[str, Any]]] = None, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, AsyncTokenCredential]] = None, 
                *, 
                audience: Optional[str] = ..., 
                **kwargs: Any
            ) -> Self: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def close_all_handles(
                self, 
                recursive: bool = False, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, int]: ...

        @distributed_trace_async
        async def close_handle(
                self, 
                handle: Union[str, Handle], 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, int]: ...

        @distributed_trace_async
        async def create_directory(
                self, 
                *, 
                file_attributes: Union[str, NTFSAttributes, None] = ..., 
                file_change_time: Union[str, datetime] = ..., 
                file_creation_time: Union[str, datetime, None] = ..., 
                file_last_write_time: Union[str, datetime, None] = ..., 
                file_mode: Optional[str] = ..., 
                file_permission: Optional[str] = ..., 
                file_permission_format: Literal[sddl, binary] = ..., 
                file_permission_key: Optional[str] = ..., 
                file_property_semantics: Optional[Literal[New, Restore]] = ..., 
                group: Optional[str] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                owner: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace_async
        async def create_subdirectory(
                self, 
                directory_name: str, 
                *, 
                metadata: Optional[dict[str, str]] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ShareDirectoryClient: ...

        @distributed_trace_async
        async def delete_directory(
                self, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_file(
                self, 
                file_name: str, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_subdirectory(
                self, 
                directory_name: str, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def exists(self, **kwargs: Any) -> bool: ...

        @distributed_trace_async
        async def get_directory_properties(
                self, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> DirectoryProperties: ...

        def get_file_client(
                self, 
                file_name: str, 
                **kwargs: Any
            ) -> ShareFileClient: ...

        def get_subdirectory_client(
                self, 
                directory_name: str, 
                **kwargs
            ) -> ShareDirectoryClient: ...

        @distributed_trace
        def list_directories_and_files(
                self, 
                name_starts_with: Optional[str] = None, 
                *, 
                include: Optional[List[str]] = ..., 
                include_extended_info: Optional[bool] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Union[DirectoryProperties, FileProperties]]: ...

        @distributed_trace
        def list_handles(
                self, 
                recursive: bool = False, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Handle]: ...

        @distributed_trace_async
        async def rename_directory(
                self, 
                new_name: str, 
                *, 
                destination_lease: Union[ShareLeaseClient, str] = ..., 
                file_attributes: Union[NTFSAttributes, str] = ..., 
                file_change_time: Union[str, datetime] = ..., 
                file_creation_time: Union[datetime, str] = ..., 
                file_last_write_time: Union[datetime, str] = ..., 
                file_permission: Optional[str] = ..., 
                file_permission_format: Literal[sddl, binary] = ..., 
                file_permission_key: Optional[str] = ..., 
                ignore_read_only: Optional[bool] = ..., 
                metadata: Optional[Dict[str,str]] = ..., 
                overwrite: Optional[bool] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ShareDirectoryClient: ...

        @distributed_trace_async
        async def set_directory_metadata(
                self, 
                metadata: Dict[str, Any], 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace_async
        async def set_http_headers(
                self, 
                file_attributes: Optional[Union[str, NTFSAttributes]] = None, 
                file_creation_time: Optional[Union[str, datetime]] = None, 
                file_last_write_time: Optional[Union[str, datetime]] = None, 
                file_permission: Optional[str] = None, 
                permission_key: Optional[str] = None, 
                *, 
                file_change_time: Union[str, datetime] = ..., 
                file_mode: Optional[str] = ..., 
                file_permission_format: Literal[sddl, binary] = ..., 
                group: Optional[str] = ..., 
                owner: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace_async
        async def upload_file(
                self, 
                file_name: str, 
                data: Union[bytes, str, Iterable[AnyStr], AsyncIterable[AnyStr], IO[AnyStr]], 
                length: Optional[int] = None, 
                *, 
                content_settings: Optional[ContentSettings] = ..., 
                encoding: Optional[str] = ..., 
                max_concurrency: Optional[int] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                progress_hook: Callable[[int, Optional[int]], Awaitable[None]] = ..., 
                timeout: Optional[int] = ..., 
                validate_content: Optional[bool] = ..., 
                **kwargs: Any
            ) -> ShareFileClient: ...


    class azure.storage.fileshare.aio.ShareFileClient(AsyncStorageAccountHostsMixin, StorageAccountHostsMixin): implements AsyncContextManager 
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
                share_name: str, 
                file_path: str, 
                snapshot: Optional[Union[str, Dict[str, Any]]] = None, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, AsyncTokenCredential]] = None, 
                *, 
                allow_source_trailing_dot: Optional[bool] = ..., 
                allow_trailing_dot: Optional[bool] = ..., 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                max_range_size: Optional[int] = ..., 
                secondary_hostname: Optional[str] = ..., 
                token_intent: Optional[Literal[backup]] = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                share_name: str, 
                file_path: str, 
                snapshot: Optional[Union[str, Dict[str, Any]]] = None, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, AsyncTokenCredential]] = None, 
                *, 
                audience: Optional[str] = ..., 
                **kwargs: Any
            ) -> Self: ...

        @classmethod
        def from_file_url(
                cls, 
                file_url: str, 
                snapshot: Optional[Union[str, Dict[str, Any]]] = None, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, AsyncTokenCredential]] = None, 
                *, 
                audience: Optional[str] = ..., 
                **kwargs: Any
            ) -> Self: ...

        @distributed_trace_async
        async def abort_copy(
                self, 
                copy_id: Union[str, FileProperties], 
                *, 
                lease: Union[ShareLeaseClient, str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def acquire_lease(
                self, 
                lease_id: Optional[str] = None, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ShareLeaseClient: ...

        @distributed_trace_async
        async def clear_range(
                self, 
                offset: int, 
                length: int, 
                *, 
                lease: Union[ShareLeaseClient, str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def close_all_handles(
                self, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, int]: ...

        @distributed_trace_async
        async def close_handle(
                self, 
                handle: Union[str, Handle], 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, int]: ...

        @distributed_trace_async
        async def create_file(
                self, 
                size: int, 
                file_attributes: Optional[Union[str, NTFSAttributes]] = None, 
                file_creation_time: Optional[Union[str, datetime]] = None, 
                file_last_write_time: Optional[Union[str, datetime]] = None, 
                file_permission: Optional[str] = None, 
                permission_key: Optional[str] = None, 
                *, 
                content_settings: Optional[ContentSettings] = ..., 
                data: bytes = ..., 
                file_change_time: Union[str, datetime] = ..., 
                file_mode: Optional[str] = ..., 
                file_permission_format: Literal[sddl, binary] = ..., 
                file_property_semantics: Optional[Literal[New, Restore]] = ..., 
                group: Optional[str] = ..., 
                lease: Union[ShareLeaseClient, str] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                owner: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace_async
        async def create_hardlink(
                self, 
                target: str, 
                *, 
                lease: Optional[Union[ShareLeaseClient, str]] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace_async
        async def create_symlink(
                self, 
                target: str, 
                *, 
                file_creation_time: Optional[Union[str, datetime]] = ..., 
                file_last_write_time: Optional[Union[str, datetime]] = ..., 
                group: Optional[str] = ..., 
                lease: Optional[Union[ShareLeaseClient, str]] = ..., 
                metadata: Optional[Dict[str, str]] = ..., 
                owner: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace_async
        async def delete_file(
                self, 
                *, 
                lease: Union[ShareLeaseClient, str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def download_file(
                self, 
                offset: Optional[int] = None, 
                length: Optional[int] = None, 
                *, 
                decompress: Optional[bool] = ..., 
                lease: Union[ShareLeaseClient, str] = ..., 
                max_concurrency: Optional[int] = ..., 
                progress_hook: Callable[[int, int], Awaitable[None]] = ..., 
                timeout: Optional[int] = ..., 
                validate_content: Optional[bool] = ..., 
                **kwargs: Any
            ) -> StorageStreamDownloader: ...

        @distributed_trace_async
        async def exists(
                self, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> bool: ...

        @distributed_trace_async
        async def get_file_properties(
                self, 
                *, 
                lease: Union[ShareLeaseClient, str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> FileProperties: ...

        @distributed_trace_async
        async def get_ranges(
                self, 
                offset: Optional[int] = None, 
                length: Optional[int] = None, 
                *, 
                lease: Union[ShareLeaseClient, str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[Dict[str, int]]: ...

        @distributed_trace_async
        async def get_ranges_diff(
                self, 
                previous_sharesnapshot: Union[str, Dict[str, Any]], 
                offset: Optional[int] = None, 
                length: Optional[int] = None, 
                *, 
                include_renames: Optional[bool] = ..., 
                lease: Union[ShareLeaseClient, str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Tuple[List[Dict[str, int]], List[Dict[str, int]]]: ...

        @distributed_trace_async
        async def get_symlink(
                self, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace
        def list_handles(
                self, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Handle]: ...

        @distributed_trace_async
        async def rename_file(
                self, 
                new_name: str, 
                *, 
                content_type: Optional[str] = ..., 
                destination_lease: Union[ShareLeaseClient, str] = ..., 
                file_attributes: Union[NTFSAttributes, str] = ..., 
                file_change_time: Union[str, datetime] = ..., 
                file_creation_time: Union[datetime, str] = ..., 
                file_last_write_time: Union[datetime, str] = ..., 
                file_permission: Optional[str] = ..., 
                file_permission_format: Literal[sddl, binary] = ..., 
                file_permission_key: Optional[str] = ..., 
                ignore_read_only: Optional[bool] = ..., 
                metadata: Optional[Dict[str,str]] = ..., 
                overwrite: Optional[bool] = ..., 
                source_lease: Union[ShareLeaseClient, str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ShareFileClient: ...

        @distributed_trace_async
        async def resize_file(
                self, 
                size: int, 
                *, 
                lease: Union[ShareLeaseClient, str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace_async
        async def set_file_metadata(
                self, 
                metadata: Optional[Dict[str, Any]] = None, 
                *, 
                lease: Union[ShareLeaseClient, str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace_async
        async def set_http_headers(
                self, 
                content_settings: ContentSettings, 
                file_attributes: Optional[Union[str, NTFSAttributes]] = None, 
                file_creation_time: Optional[Union[str, datetime]] = None, 
                file_last_write_time: Optional[Union[str, datetime]] = None, 
                file_permission: Optional[str] = None, 
                permission_key: Optional[str] = None, 
                *, 
                file_change_time: Union[str, datetime] = ..., 
                file_mode: Optional[str] = ..., 
                file_permission_format: Literal[sddl, binary] = ..., 
                group: Optional[str] = ..., 
                lease: Union[ShareLeaseClient, str] = ..., 
                owner: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace_async
        async def start_copy_from_url(
                self, 
                source_url: str, 
                *, 
                file_attributes: Union[str, NTFSAttributes] = ..., 
                file_change_time: Union[str, datetime] = ..., 
                file_creation_time: Union[str, datetime] = ..., 
                file_last_write_time: Union[str, datetime] = ..., 
                file_mode: Optional[str] = ..., 
                file_mode_copy_mode: Literal[source, override] = ..., 
                file_permission: Optional[str] = ..., 
                file_permission_format: Literal[sddl, binary] = ..., 
                group: Optional[str] = ..., 
                ignore_read_only: Optional[bool] = ..., 
                lease: Union[ShareLeaseClient, str] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                owner: Optional[str] = ..., 
                owner_copy_mode: Literal[source, override] = ..., 
                permission_key: Optional[str] = ..., 
                set_archive_attribute: Optional[bool] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace_async
        async def upload_file(
                self, 
                data: Union[bytes, str, Iterable[AnyStr], AsyncIterable[AnyStr], IO[bytes]], 
                length: Optional[int] = None, 
                file_attributes: Optional[Union[str, NTFSAttributes]] = None, 
                file_creation_time: Optional[Union[str, datetime]] = None, 
                file_last_write_time: Optional[Union[str, datetime]] = None, 
                file_permission: Optional[str] = None, 
                permission_key: Optional[str] = None, 
                *, 
                content_settings: Optional[ContentSettings] = ..., 
                encoding: Optional[str] = ..., 
                file_change_time: Union[str, datetime] = ..., 
                lease: Union[ShareLeaseClient, str] = ..., 
                max_concurrency: Optional[int] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                progress_hook: Callable[[int, Optional[int]], Awaitable[None]] = ..., 
                timeout: Optional[int] = ..., 
                validate_content: Optional[bool] = ..., 
                **kwargs
            ) -> Dict[str, Any]: ...

        @distributed_trace_async
        async def upload_range(
                self, 
                data: bytes, 
                offset: int, 
                length: int, 
                *, 
                encoding: Optional[str] = ..., 
                file_last_write_mode: Literal[preserve, now] = ..., 
                lease: Union[ShareLeaseClient, str] = ..., 
                timeout: Optional[int] = ..., 
                validate_content: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace_async
        async def upload_range_from_url(
                self, 
                source_url: str, 
                offset: int, 
                length: int, 
                source_offset: int, 
                *, 
                file_last_write_mode: Literal[preserve, now] = ..., 
                lease: Union[ShareLeaseClient, str] = ..., 
                source_authorization: Optional[str] = ..., 
                source_etag: Optional[str] = ..., 
                source_if_modified_since: Optional[datetime] = ..., 
                source_if_unmodified_since: Optional[datetime] = ..., 
                source_match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...


    class azure.storage.fileshare.aio.ShareLeaseClient: implements AsyncContextManager 
        etag: Optional[str]
        id: str
        last_modified: Optional[datetime]

        def __init__(
                self, 
                client: Union[ShareFileClient, ShareClient], 
                lease_id: Optional[str] = None
            ) -> None: ...

        @distributed_trace_async
        async def acquire(
                self, 
                *, 
                lease_duration: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def break_lease(
                self, 
                *, 
                lease_break_period: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> int: ...

        @distributed_trace_async
        async def change(
                self, 
                proposed_lease_id: str, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def release(
                self, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def renew(
                self, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.storage.fileshare.aio.ShareServiceClient(AsyncStorageAccountHostsMixin, StorageAccountHostsMixin): implements AsyncContextManager 
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
                allow_source_trailing_dot: Optional[bool] = ..., 
                allow_trailing_dot: Optional[bool] = ..., 
                api_version: Optional[str] = ..., 
                max_range_size: Optional[int] = ..., 
                secondary_hostname: Optional[str] = ..., 
                token_intent: Optional[Literal[backup]] = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, AsyncTokenCredential]] = None, 
                **kwargs: Any
            ) -> Self: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def create_share(
                self, 
                share_name: str, 
                *, 
                provisioned_bandwidth_mibps: Optional[int] = ..., 
                provisioned_iops: Optional[int] = ..., 
                quota: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ShareClient: ...

        @distributed_trace_async
        async def delete_share(
                self, 
                share_name: Union[ShareProperties, str], 
                delete_snapshots: Optional[bool] = False, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_service_properties(
                self, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        def get_share_client(
                self, 
                share: Union[ShareProperties, str], 
                snapshot: Optional[Union[Dict[str, Any], str]] = None
            ) -> ShareClient: ...

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
        def list_shares(
                self, 
                name_starts_with: Optional[str] = None, 
                include_metadata: Optional[bool] = False, 
                include_snapshots: Optional[bool] = False, 
                *, 
                include_deleted: Optional[bool] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ShareProperties]: ...

        @distributed_trace_async
        async def set_service_properties(
                self, 
                hour_metrics: Optional[Metrics] = None, 
                minute_metrics: Optional[Metrics] = None, 
                cors: Optional[List[CorsRule]] = None, 
                protocol: Optional[ShareProtocolSettings] = None, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def undelete_share(
                self, 
                deleted_share_name: str, 
                deleted_share_version: str, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ShareClient: ...


```