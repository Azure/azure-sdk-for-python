```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.storage.filedatalake

    def azure.storage.filedatalake.generate_account_sas(
            account_name: str, 
            account_key: str, 
            resource_types: Union[ResourceTypes, str], 
            permission: Union[AccountSasPermissions, str], 
            expiry: Union[datetime, str], 
            *, 
            encryption_scope: Optional[str] = ..., 
            ip: Optional[str] = ..., 
            protocol: Optional[str] = ..., 
            services: Union[Services, str] = Services(blob=True), 
            start: Union[datetime, str] = ..., 
            sts_hook: Optional[Callable[[str], None]] = ..., 
            **kwargs: Any
        ) -> str: ...


    def azure.storage.filedatalake.generate_directory_sas(
            account_name: str, 
            file_system_name: str, 
            directory_name: str, 
            credential: Union[str, UserDelegationKey], 
            permission: Optional[Union[DirectorySasPermissions, str]] = None, 
            expiry: Optional[Union[datetime, str]] = None, 
            *, 
            agent_object_id: Optional[str] = ..., 
            cache_control: Optional[str] = ..., 
            content_disposition: Optional[str] = ..., 
            content_encoding: Optional[str] = ..., 
            content_language: Optional[str] = ..., 
            content_type: Optional[str] = ..., 
            correlation_id: Optional[str] = ..., 
            encryption_scope: Optional[str] = ..., 
            ip: Optional[str] = ..., 
            policy_id: Optional[str] = ..., 
            preauthorized_agent_object_id: Optional[str] = ..., 
            protocol: Optional[str] = ..., 
            request_headers: Optional[Dict[str, str]] = ..., 
            request_query_params: Optional[Dict[str, str]] = ..., 
            start: Union[datetime, str] = ..., 
            sts_hook: Optional[Callable[[str], None]] = ..., 
            user_delegation_oid: Optional[str] = ..., 
            **kwargs: Any
        ) -> str: ...


    def azure.storage.filedatalake.generate_file_sas(
            account_name: str, 
            file_system_name: str, 
            directory_name: str, 
            file_name: str, 
            credential: Union[str, UserDelegationKey], 
            permission: Optional[Union[FileSasPermissions, str]] = None, 
            expiry: Optional[Union[datetime, str]] = None, 
            *, 
            agent_object_id: Optional[str] = ..., 
            cache_control: Optional[str] = ..., 
            content_disposition: Optional[str] = ..., 
            content_encoding: Optional[str] = ..., 
            content_language: Optional[str] = ..., 
            content_type: Optional[str] = ..., 
            correlation_id: Optional[str] = ..., 
            encryption_scope: Optional[str] = ..., 
            ip: Optional[str] = ..., 
            policy_id: Optional[str] = ..., 
            preauthorized_agent_object_id: Optional[str] = ..., 
            protocol: Optional[str] = ..., 
            request_headers: Optional[Dict[str, str]] = ..., 
            request_query_params: Optional[Dict[str, str]] = ..., 
            start: Union[datetime, str] = ..., 
            sts_hook: Optional[Callable[[str], None]] = ..., 
            user_delegation_oid: Optional[str] = ..., 
            **kwargs: Any
        ) -> str: ...


    def azure.storage.filedatalake.generate_file_system_sas(
            account_name: str, 
            file_system_name: str, 
            credential: Union[str, UserDelegationKey], 
            permission: Optional[Union[FileSystemSasPermissions, str]] = None, 
            expiry: Optional[Union[datetime, str]] = None, 
            *, 
            agent_object_id: Optional[str] = ..., 
            cache_control: Optional[str] = ..., 
            content_disposition: Optional[str] = ..., 
            content_encoding: Optional[str] = ..., 
            content_language: Optional[str] = ..., 
            content_type: Optional[str] = ..., 
            correlation_id: Optional[str] = ..., 
            encryption_scope: Optional[str] = ..., 
            ip: Optional[str] = ..., 
            policy_id: Optional[str] = ..., 
            preauthorized_agent_object_id: Optional[str] = ..., 
            protocol: Optional[str] = ..., 
            request_headers: Optional[Dict[str, str]] = ..., 
            request_query_params: Optional[Dict[str, str]] = ..., 
            start: Union[datetime, str] = ..., 
            sts_hook: Optional[Callable[[str], None]] = ..., 
            user_delegation_oid: Optional[str] = ..., 
            **kwargs: Any
        ) -> str: ...


    class azure.storage.filedatalake.AccessControlChangeCounters(DictMixin):
        directories_successful: int
        failure_count: int
        files_successful: int

        def __contains__(self, key): ...

        def __delitem__(self, key): ...

        def __eq__(self, other): ...

        def __getitem__(self, key): ...

        def __init__(
                self, 
                directories_successful: int, 
                files_successful: int, 
                failure_count: int
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


    class azure.storage.filedatalake.AccessControlChangeFailure(DictMixin):
        error_message: str
        is_directory: bool
        name: str

        def __contains__(self, key): ...

        def __delitem__(self, key): ...

        def __eq__(self, other): ...

        def __getitem__(self, key): ...

        def __init__(
                self, 
                name: str, 
                is_directory: bool, 
                error_message: str
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


    class azure.storage.filedatalake.AccessControlChangeResult(DictMixin):
        continuation: Optional[str]
        counters: Optional[AccessControlChangeCounters]

        def __contains__(self, key): ...

        def __delitem__(self, key): ...

        def __eq__(self, other): ...

        def __getitem__(self, key): ...

        def __init__(
                self, 
                counters: Optional[AccessControlChangeCounters], 
                continuation: Optional[str]
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


    class azure.storage.filedatalake.AccessControlChanges(DictMixin):
        aggregate_counters: AccessControlChangeCounters
        batch_counters: AccessControlChangeCounters
        batch_failures: List[AccessControlChangeFailure]
        continuation: Optional[str]

        def __contains__(self, key): ...

        def __delitem__(self, key): ...

        def __eq__(self, other): ...

        def __getitem__(self, key): ...

        def __init__(
                self, 
                batch_counters: AccessControlChangeCounters, 
                aggregate_counters: AccessControlChangeCounters, 
                batch_failures: List[AccessControlChangeFailure], 
                continuation: Optional[str]
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


    class azure.storage.filedatalake.AccessPolicy(BlobAccessPolicy):

        def __init__(
                self, 
                permission: Optional[Union[FileSystemSasPermissions, str]] = None, 
                expiry: Optional[Union[datetime, str]] = None, 
                *, 
                start: Union[datetime, str] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.storage.filedatalake.AccountSasPermissions(BlobAccountSasPermissions):
        add = False
        create = False
        delete = False
        delete_previous_version = False
        filter_by_tags = False
        list = False
        permanent_delete = False
        process = False
        read = False
        set_immutability_policy = False
        tag = False
        update = False
        write = False

        def __init__(
                self, 
                read: bool = False, 
                write: bool = False, 
                delete: bool = False, 
                list: bool = False, 
                create: bool = False
            ) -> None: ...


    class azure.storage.filedatalake.AnalyticsLogging(GenLogging):
        delete: bool
        read: bool
        retention_policy: RetentionPolicy
        version: str
        write: bool

        def __init__(self, **kwargs: Any) -> None: ...


    class azure.storage.filedatalake.ArrowDialect(BlobArrowDialect):


    class azure.storage.filedatalake.ArrowType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOOL = "bool"
        DECIMAL = "decimal"
        DOUBLE = "double"
        INT64 = "int64"
        STRING = "string"
        TIMESTAMP_MS = "timestamp[ms]"


    class azure.storage.filedatalake.ContentSettings(BlobContentSettings):

        def __init__(
                self, 
                *, 
                cache_control: Optional[str] = ..., 
                content_disposition: Optional[str] = ..., 
                content_encoding: Optional[str] = ..., 
                content_language: Optional[str] = ..., 
                content_md5: Optional[bytearray] = ..., 
                content_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.storage.filedatalake.CorsRule(GenCorsRule):
        allowed_headers: str
        allowed_methods: str
        allowed_origins: str
        exposed_headers: str
        max_age_in_seconds: int

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


    class azure.storage.filedatalake.CustomerProvidedEncryptionKey(BlobCustomerProvidedEncryptionKey):


    class azure.storage.filedatalake.DataLakeDirectoryClient(PathClient): implements ContextManager 
        property api_version: str    # Read-only
        property location_mode: str
        property primary_endpoint: str    # Read-only
        property primary_hostname: str    # Read-only
        property secondary_endpoint: str    # Read-only
        property secondary_hostname: Optional[str]    # Read-only
        property url: str    # Read-only
        primary_endpoint: str
        primary_hostname: str
        url: str

        def __init__(
                self, 
                account_url: str, 
                file_system_name: str, 
                directory_name: str, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]] = None, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                file_system_name: str, 
                directory_name: str, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]] = None, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                **kwargs: Any
            ) -> Self: ...

        @distributed_trace
        def acquire_lease(
                self, 
                lease_duration: int = -1, 
                lease_id: Optional[str] = None, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> DataLakeLeaseClient: ...

        def close(self) -> None: ...

        @distributed_trace
        def create_directory(
                self, 
                metadata: Optional[Dict[str, str]] = None, 
                *, 
                acl: Optional[str] = ..., 
                content_settings: Optional[ContentSettings] = ..., 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                etag: Optional[str] = ..., 
                group: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                lease_duration: Optional[int] = ..., 
                lease_id: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                owner: Optional[str] = ..., 
                permissions: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                umask: Optional[str] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime]]: ...

        @distributed_trace
        def create_file(
                self, 
                file: Union[FileProperties, str], 
                *, 
                acl: Optional[str] = ..., 
                content_settings: Optional[ContentSettings] = ..., 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                etag: Optional[str] = ..., 
                expires_on: Union[datetime, int] = ..., 
                group: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                lease_duration: Optional[int] = ..., 
                lease_id: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                metadata = ..., 
                owner: Optional[str] = ..., 
                permissions: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                umask: Optional[str] = ..., 
                **kwargs: Any
            ) -> DataLakeFileClient: ...

        @distributed_trace
        def create_sub_directory(
                self, 
                sub_directory: Union[DirectoryProperties, str], 
                metadata: Optional[Dict[str, str]] = None, 
                *, 
                acl: Optional[str] = ..., 
                content_settings: Optional[ContentSettings] = ..., 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                etag: Optional[str] = ..., 
                group: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                lease_duration: Optional[int] = ..., 
                lease_id: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                owner: Optional[str] = ..., 
                permissions: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                umask: Optional[str] = ..., 
                **kwargs: Any
            ) -> DataLakeDirectoryClient: ...

        @distributed_trace
        def delete_directory(
                self, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_sub_directory(
                self, 
                sub_directory: Union[DirectoryProperties, str], 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> DataLakeDirectoryClient: ...

        @distributed_trace
        def exists(
                self, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> bool: ...

        @distributed_trace
        def get_access_control(
                self, 
                upn: Optional[bool] = None, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace
        def get_directory_properties(
                self, 
                *, 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                upn: Optional[bool] = ..., 
                **kwargs: Any
            ) -> DirectoryProperties: ...

        def get_file_client(self, file: Union[FileProperties, str]) -> DataLakeFileClient: ...

        @distributed_trace
        def get_paths(
                self, 
                *, 
                max_results: Optional[int] = ..., 
                recursive: bool = True, 
                start_from: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                upn: Optional[bool] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PathProperties]: ...

        def get_sub_directory_client(self, sub_directory: Union[DirectoryProperties, str]) -> DataLakeDirectoryClient: ...

        @distributed_trace
        def get_tags(
                self, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                version_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> Dict[str, str]: ...

        @distributed_trace
        def remove_access_control_recursive(
                self, 
                acl: str, 
                *, 
                batch_size: Optional[int] = ..., 
                continuation_token: Optional[str] = ..., 
                continue_on_failure: Optional[bool] = ..., 
                max_batches: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AccessControlChangeResult: ...

        @distributed_trace
        def rename_directory(
                self, 
                new_name: str, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                source_etag: Optional[str] = ..., 
                source_if_modified_since: Optional[datetime] = ..., 
                source_if_unmodified_since: Optional[datetime] = ..., 
                source_lease: Union[DataLakeLeaseClient, str] = ..., 
                source_match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> DataLakeDirectoryClient: ...

        @distributed_trace
        def set_access_control(
                self, 
                owner: Optional[str] = None, 
                group: Optional[str] = None, 
                permissions: Optional[str] = None, 
                acl: Optional[str] = None, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime]]: ...

        @distributed_trace
        def set_access_control_recursive(
                self, 
                acl: str, 
                *, 
                batch_size: Optional[int] = ..., 
                continuation_token: Optional[str] = ..., 
                continue_on_failure: Optional[bool] = ..., 
                max_batches: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AccessControlChangeResult: ...

        @distributed_trace
        def set_http_headers(
                self, 
                content_settings: Optional[ContentSettings] = None, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace
        def set_metadata(
                self, 
                metadata: Dict[str, str], 
                *, 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime]]: ...

        @distributed_trace
        def set_tags(
                self, 
                tags: Optional[Dict[str, str]] = None, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                validate_content: Optional[bool] = ..., 
                version_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace
        def update_access_control_recursive(
                self, 
                acl: str, 
                *, 
                batch_size: Optional[int] = ..., 
                continuation_token: Optional[str] = ..., 
                continue_on_failure: Optional[bool] = ..., 
                max_batches: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AccessControlChangeResult: ...


    class azure.storage.filedatalake.DataLakeFileClient(PathClient): implements ContextManager 
        property api_version: str    # Read-only
        property location_mode: str
        property primary_endpoint: str    # Read-only
        property primary_hostname: str    # Read-only
        property secondary_endpoint: str    # Read-only
        property secondary_hostname: Optional[str]    # Read-only
        property url: str    # Read-only
        primary_endpoint: str
        primary_hostname: str
        url: str

        def __init__(
                self, 
                account_url: str, 
                file_system_name: str, 
                file_path: str, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]] = None, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                file_system_name: str, 
                file_path: str, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]] = None, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                **kwargs: Any
            ) -> Self: ...

        @distributed_trace
        def acquire_lease(
                self, 
                lease_duration: int = -1, 
                lease_id: Optional[str] = None, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> DataLakeLeaseClient: ...

        @distributed_trace
        def append_data(
                self, 
                data: Union[bytes, Iterable[bytes], IO[bytes]], 
                offset: int, 
                length: Optional[int] = None, 
                *, 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                flush: Optional[bool] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                lease_action: Literal[acquire, auto-renew, release, acquire-release] = ..., 
                lease_duration: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                validate_content: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        def close(self) -> None: ...

        @distributed_trace
        def create_file(
                self, 
                content_settings: Optional[ContentSettings] = None, 
                metadata: Optional[Dict[str, str]] = None, 
                *, 
                acl: Optional[str] = ..., 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                encryption_context: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                expires_on: Union[datetime, int] = ..., 
                group: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                lease_duration: Optional[int] = ..., 
                lease_id: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                owner: Optional[str] = ..., 
                permissions: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                umask: Optional[str] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime]]: ...

        @distributed_trace
        def delete_file(
                self, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def download_file(
                self, 
                offset: Optional[int] = None, 
                length: Optional[int] = None, 
                *, 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                decompress: Optional[bool] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                max_concurrency: Optional[int] = ..., 
                progress_hook: Callable[[int, int], None] = ..., 
                timeout: Optional[int] = ..., 
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
        def flush_data(
                self, 
                offset: int, 
                retain_uncommitted_data: Optional[bool] = False, 
                *, 
                close: Optional[bool] = ..., 
                content_settings: Optional[ContentSettings] = ..., 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                lease_action: Literal[acquire, auto-renew, release, acquire-release] = ..., 
                lease_duration: Optional[int] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace
        def get_access_control(
                self, 
                upn: Optional[bool] = None, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace
        def get_file_properties(
                self, 
                *, 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                upn: Optional[bool] = ..., 
                **kwargs: Any
            ) -> FileProperties: ...

        @distributed_trace
        def get_tags(
                self, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                version_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> Dict[str, str]: ...

        @distributed_trace
        def query_file(
                self, 
                query_expression: str, 
                *, 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                etag: Optional[str] = ..., 
                file_format: Union[DelimitedTextDialect, DelimitedJsonDialect or] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                on_error: Callable[DataLakeFileQueryError] = ..., 
                output_format: Union[DelimitedTextDialect, DelimitedJsonDialect] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> DataLakeFileQueryReader: ...

        @distributed_trace
        def remove_access_control_recursive(
                self, 
                acl: str, 
                *, 
                batch_size: Optional[int] = ..., 
                continuation_token: Optional[str] = ..., 
                continue_on_failure: Optional[bool] = ..., 
                max_batches: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AccessControlChangeResult: ...

        @distributed_trace
        def rename_file(
                self, 
                new_name: str, 
                *, 
                content_settings: Optional[ContentSettings] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                source_etag: Optional[str] = ..., 
                source_if_modified_since: Optional[datetime] = ..., 
                source_if_unmodified_since: Optional[datetime] = ..., 
                source_lease: Union[DataLakeLeaseClient, str] = ..., 
                source_match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> DataLakeFileClient: ...

        @distributed_trace
        def set_access_control(
                self, 
                owner: Optional[str] = None, 
                group: Optional[str] = None, 
                permissions: Optional[str] = None, 
                acl: Optional[str] = None, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime]]: ...

        @distributed_trace
        def set_access_control_recursive(
                self, 
                acl: str, 
                *, 
                batch_size: Optional[int] = ..., 
                continuation_token: Optional[str] = ..., 
                continue_on_failure: Optional[bool] = ..., 
                max_batches: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AccessControlChangeResult: ...

        @distributed_trace
        def set_file_expiry(
                self, 
                expiry_options: str, 
                expires_on: Optional[Union[datetime, int]] = None, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def set_http_headers(
                self, 
                content_settings: Optional[ContentSettings] = None, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace
        def set_metadata(
                self, 
                metadata: Dict[str, str], 
                *, 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime]]: ...

        @distributed_trace
        def set_tags(
                self, 
                tags: Optional[Dict[str, str]] = None, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                validate_content: Optional[bool] = ..., 
                version_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace
        def update_access_control_recursive(
                self, 
                acl: str, 
                *, 
                batch_size: Optional[int] = ..., 
                continuation_token: Optional[str] = ..., 
                continue_on_failure: Optional[bool] = ..., 
                max_batches: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AccessControlChangeResult: ...

        @distributed_trace
        def upload_data(
                self, 
                data: Union[bytes, str, Iterable[AnyStr], IO[bytes]], 
                length: Optional[int] = None, 
                overwrite: Optional[bool] = False, 
                *, 
                chunk_size: Optional[int] = ..., 
                content_settings: Optional[ContentSettings] = ..., 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                encryption_context: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                max_concurrency: Optional[int] = ..., 
                metadata: Optional[Dict[str, str]] = ..., 
                permissions: Optional[str] = ..., 
                progress_hook: Callable[[int, int], None] = ..., 
                timeout: Optional[int] = ..., 
                umask: Optional[str] = ..., 
                validate_content: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...


    class azure.storage.filedatalake.DataLakeFileQueryError:
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


    class azure.storage.filedatalake.DataLakeLeaseClient: implements ContextManager 
        etag: Optional[str]
        id: str
        last_modified: Optional[datetime]

        def __init__(
                self, 
                client: Union[FileSystemClient, DataLakeDirectoryClient, DataLakeFileClient], 
                lease_id: Optional[str] = None
            ) -> None: ...

        @distributed_trace
        def acquire(
                self, 
                lease_duration: int = -1, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
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
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.storage.filedatalake.DataLakeServiceClient(StorageAccountHostsMixin): implements ContextManager 
        property api_version: str    # Read-only
        property location_mode: str
        property primary_endpoint: str    # Read-only
        property primary_hostname: str    # Read-only
        property secondary_endpoint: str    # Read-only
        property secondary_hostname: Optional[str]    # Read-only
        property url: str    # Read-only
        primary_endpoint: str
        primary_hostname: str
        url: str

        def __init__(
                self, 
                account_url: str, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]] = None, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
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
                **kwargs: Any
            ) -> Self: ...

        def close(self) -> None: ...

        @distributed_trace
        def create_file_system(
                self, 
                file_system: Union[FileSystemProperties, str], 
                metadata: Optional[Dict[str, str]] = None, 
                public_access: Optional[PublicAccess] = None, 
                *, 
                encryption_scope_options: Union[dict, EncryptionScopeOptions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> FileSystemClient: ...

        @distributed_trace
        def delete_file_system(
                self, 
                file_system: Union[FileSystemProperties, str], 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> FileSystemClient: ...

        def get_directory_client(
                self, 
                file_system: Union[FileSystemProperties, str], 
                directory: Union[DirectoryProperties, str]
            ) -> DataLakeDirectoryClient: ...

        def get_file_client(
                self, 
                file_system: Union[FileSystemProperties, str], 
                file_path: Union[FileProperties, str]
            ) -> DataLakeFileClient: ...

        def get_file_system_client(self, file_system: Union[FileSystemProperties, str]) -> FileSystemClient: ...

        @distributed_trace
        def get_service_properties(
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
        def list_file_systems(
                self, 
                name_starts_with: Optional[str] = None, 
                include_metadata: bool = False, 
                *, 
                include_deleted: Optional[bool] = ..., 
                include_system: Optional[bool] = ..., 
                results_per_page: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[FileSystemProperties]: ...

        @distributed_trace
        def set_service_properties(
                self, 
                *, 
                analytics_logging = ..., 
                cors = ..., 
                delete_retention_policy = ..., 
                hour_metrics = ..., 
                minute_metrics = ..., 
                static_website = ..., 
                target_version: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def undelete_file_system(
                self, 
                name: str, 
                deleted_version: str, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> FileSystemClient: ...


    class azure.storage.filedatalake.DeletedPathProperties(DictMixin):
        deleted_time: Optional[datetime]
        deletion_id: Optional[str]
        file_system: Optional[str]
        name: str
        remaining_retention_days: Optional[int]

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


    class azure.storage.filedatalake.DelimitedJsonDialect(BlobDelimitedJSON):


    class azure.storage.filedatalake.DelimitedTextDialect(BlobDelimitedTextDialect):


    class azure.storage.filedatalake.DirectoryProperties(DictMixin):
        acl: Optional[str]
        creation_time: datetime
        deleted: bool
        deleted_time: Optional[datetime]
        encryption_scope: Optional[str]
        etag: str
        group: Optional[str]
        last_modified: datetime
        lease: LeaseProperties
        metadata: Dict[str, str]
        name: str
        owner: Optional[str]
        permissions: Optional[str]
        remaining_retention_days: Optional[int]

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


    class azure.storage.filedatalake.DirectorySasPermissions:
        add: Optional[bool] = False
        create: bool = False
        delete: bool = False
        execute: Optional[bool] = False
        list: Optional[bool] = False
        manage_access_control: Optional[bool] = False
        manage_ownership: Optional[bool] = False
        move: Optional[bool] = False
        read: bool = False
        tags: Optional[bool]
        write: bool = False

        def __init__(
                self, 
                read: bool = False, 
                create: bool = False, 
                write: bool = False, 
                delete: bool = False, 
                *, 
                add: Optional[bool] = ..., 
                execute: Optional[bool] = ..., 
                list: Optional[bool] = ..., 
                manage_access_control: Optional[bool] = ..., 
                manage_ownership: Optional[bool] = ..., 
                move: Optional[bool] = ..., 
                tags: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __str__(self): ...

        @classmethod
        def from_string(cls, permission: str) -> Self: ...


    class azure.storage.filedatalake.EncryptionScopeOptions(BlobContainerEncryptionScope):


    class azure.storage.filedatalake.ExponentialRetry(StorageRetryPolicy):
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


    class azure.storage.filedatalake.FileProperties(DictMixin):
        acl: Optional[str]
        content_settings: ContentSettings
        creation_time: datetime
        deleted: Optional[bool]
        deleted_time: Optional[datetime]
        encryption_context: Optional[str]
        encryption_scope: Optional[str]
        etag: str
        expiry_time: Optional[datetime]
        group: Optional[str]
        last_modified: datetime
        lease: LeaseProperties
        metadata: Dict[str, str]
        name: str
        owner: Optional[str]
        permissions: Optional[str]
        remaining_retention_days: Optional[int]
        size: int

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


    class azure.storage.filedatalake.FileSasPermissions:
        add: Optional[bool]
        create: bool = False
        delete: bool = False
        execute: Optional[bool]
        manage_access_control: Optional[bool]
        manage_ownership: Optional[bool]
        move: Optional[bool]
        read: bool = False
        tags: Optional[bool]
        write: bool = False

        def __init__(
                self, 
                read: bool = False, 
                create: bool = False, 
                write: bool = False, 
                delete: bool = False, 
                *, 
                add: Optional[bool] = ..., 
                execute: Optional[bool] = ..., 
                manage_access_control: Optional[bool] = ..., 
                manage_ownership: Optional[bool] = ..., 
                move: Optional[bool] = ..., 
                tags: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __str__(self): ...

        @classmethod
        def from_string(cls, permission: str) -> Self: ...


    class azure.storage.filedatalake.FileSystemClient(StorageAccountHostsMixin): implements ContextManager 
        property api_version: str    # Read-only
        property location_mode: str
        property primary_endpoint: str    # Read-only
        property primary_hostname: str    # Read-only
        property secondary_endpoint: str    # Read-only
        property secondary_hostname: Optional[str]    # Read-only
        property url: str    # Read-only
        primary_endpoint: str
        primary_hostname: str
        url: str

        def __init__(
                self, 
                account_url: str, 
                file_system_name: str, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]] = None, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                file_system_name: str, 
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
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> DataLakeLeaseClient: ...

        def close(self) -> None: ...

        @distributed_trace
        def create_directory(
                self, 
                directory: Union[DirectoryProperties, str], 
                metadata: Optional[Dict[str, str]] = None, 
                *, 
                acl: Optional[str] = ..., 
                content_settings: Optional[ContentSettings] = ..., 
                etag: Optional[str] = ..., 
                group: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                lease_duration: Optional[int] = ..., 
                lease_id: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                owner: Optional[str] = ..., 
                permissions: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                umask: Optional[str] = ..., 
                **kwargs: Any
            ) -> DataLakeDirectoryClient: ...

        @distributed_trace
        def create_file(
                self, 
                file: Union[FileProperties, str], 
                *, 
                acl: Optional[str] = ..., 
                content_settings: Optional[ContentSettings] = ..., 
                etag: Optional[str] = ..., 
                expires_on: Union[datetime, int] = ..., 
                group: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                lease_duration: Optional[int] = ..., 
                lease_id: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                metadata: Dict[str, str] = ..., 
                owner: Optional[str] = ..., 
                permissions: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                umask: Optional[str] = ..., 
                **kwargs: Any
            ) -> DataLakeFileClient: ...

        @distributed_trace
        def create_file_system(
                self, 
                metadata: Optional[Dict[str, str]] = None, 
                public_access: Optional[PublicAccess] = None, 
                *, 
                encryption_scope_options: Union[dict, EncryptionScopeOptions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime]]: ...

        @distributed_trace
        def delete_directory(
                self, 
                directory: Union[DirectoryProperties, str], 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> DataLakeDirectoryClient: ...

        @distributed_trace
        def delete_file(
                self, 
                file: Union[FileProperties, str], 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> DataLakeFileClient: ...

        @distributed_trace
        def delete_file_system(
                self, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def exists(
                self, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> bool: ...

        def get_directory_client(self, directory: Union[DirectoryProperties, str]) -> DataLakeDirectoryClient: ...

        def get_file_client(self, file_path: Union[FileProperties, str]) -> DataLakeFileClient: ...

        @distributed_trace
        def get_file_system_access_policy(
                self, 
                *, 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace
        def get_file_system_properties(
                self, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> FileSystemProperties: ...

        @distributed_trace
        def get_paths(
                self, 
                path: Optional[str] = None, 
                recursive: Optional[bool] = True, 
                max_results: Optional[int] = None, 
                *, 
                start_from: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                upn: Optional[bool] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PathProperties]: ...

        @distributed_trace
        def list_deleted_paths(
                self, 
                *, 
                path_prefix: Optional[str] = ..., 
                results_per_page: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DeletedPathProperties]: ...

        @distributed_trace
        def set_file_system_access_policy(
                self, 
                signed_identifiers: Dict[str, AccessPolicy], 
                public_access: Optional[Union[str, PublicAccess]] = None, 
                *, 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime]]: ...

        @distributed_trace
        def set_file_system_metadata(
                self, 
                metadata: Dict[str, str], 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime]]: ...


    class azure.storage.filedatalake.FileSystemProperties(DictMixin):
        deleted: Optional[bool]
        deleted_version: Optional[str]
        encryption_scope: EncryptionScopeOptions
        etag: str
        has_immutability_policy: bool
        has_legal_hold: bool
        last_modified: datetime
        lease: LeaseProperties
        metadata: Dict[str, str]
        name: str
        public_access: Optional[str]

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


    class azure.storage.filedatalake.FileSystemPropertiesPaged(ContainerPropertiesPaged):

        def __init__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.storage.filedatalake.FileSystemSasPermissions:
        add: Optional[bool]
        create: Optional[bool]
        delete: bool = False
        execute: Optional[bool]
        list: bool = False
        manage_access_control: Optional[bool] = False
        manage_ownership: Optional[bool] = False
        move: Optional[bool]
        read: bool = False
        tags: Optional[bool]
        write: bool = False

        def __init__(
                self, 
                read: bool = False, 
                write: bool = False, 
                delete: bool = False, 
                list: bool = False, 
                *, 
                add: Optional[bool] = ..., 
                create: Optional[bool] = ..., 
                execute: Optional[bool] = ..., 
                manage_access_control: Optional[bool] = ..., 
                manage_ownership: Optional[bool] = ..., 
                move: Optional[bool] = ..., 
                tags: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __str__(self): ...

        @classmethod
        def from_string(cls, permission: str) -> Self: ...


    class azure.storage.filedatalake.LeaseProperties(BlobLeaseProperties):


    class azure.storage.filedatalake.LinearRetry(StorageRetryPolicy):
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


    class azure.storage.filedatalake.LocationMode:
        PRIMARY = primary
        SECONDARY = secondary


    class azure.storage.filedatalake.Metrics(GenMetrics):
        enabled: bool = False
        include_apis: Optional[bool]
        retention_policy: RetentionPolicy
        version: str = "1.0"

        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                include_apis: Optional[bool] = ..., 
                retention_policy: Optional[RetentionPolicy] = ..., 
                version: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.storage.filedatalake.PathProperties(DictMixin):
        content_length: int
        creation_time: datetime
        encryption_context: Optional[str]
        encryption_scope: Optional[str]
        etag: str
        expiry_time: Optional[datetime]
        group: str
        is_directory: bool
        last_modified: datetime
        name: str
        owner: str
        permissions: str

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


    class azure.storage.filedatalake.PublicAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FILE = "blob"
        FILESYSTEM = "container"


    class azure.storage.filedatalake.QuickQueryDialect(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELIMITEDJSON = "DelimitedJsonDialect"
        DELIMITEDTEXT = "DelimitedTextDialect"
        PARQUET = "ParquetDialect"


    class azure.storage.filedatalake.ResourceTypes(BlobResourceTypes):
        container = False
        object = False
        service = False

        def __init__(
                self, 
                service: bool = False, 
                file_system: bool = False, 
                object: bool = False
            ) -> None: ...


    class azure.storage.filedatalake.RetentionPolicy(GenRetentionPolicy):
        days: Optional[int]
        enabled: bool = False

        def __init__(
                self, 
                enabled: bool = False, 
                days: Optional[int] = None
            ) -> None: ...


    class azure.storage.filedatalake.Services:

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


    class azure.storage.filedatalake.StaticWebsite(GenStaticWebsite):
        default_index_document_path: Optional[str]
        enabled: bool
        error_document404_path: Optional[str]
        index_document: Optional[str]

        def __init__(
                self, 
                *, 
                default_index_document_path: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                error_document404_path: Optional[str] = ..., 
                index_document: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.storage.filedatalake.StorageErrorCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
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


    class azure.storage.filedatalake.StorageStreamDownloader:
        name: str
        properties: FileProperties
        size: int

        def __init__(self, downloader: Any) -> None: ...

        def __len__(self) -> int: ...

        def chunks(self) -> Iterator[bytes]: ...

        def read(self, size: int = -1) -> bytes: ...

        def readall(self) -> bytes: ...

        def readinto(self, stream: IO[bytes]) -> int: ...


    class azure.storage.filedatalake.UserDelegationKey(BlobUserDelegationKey):


namespace azure.storage.filedatalake.aio

    class azure.storage.filedatalake.aio.DataLakeDirectoryClient(PathClient): implements AsyncContextManager 
        property api_version: str    # Read-only
        property location_mode: str
        property primary_endpoint: str    # Read-only
        property primary_hostname: str    # Read-only
        property secondary_endpoint: str    # Read-only
        property secondary_hostname: Optional[str]    # Read-only
        property url: str    # Read-only
        primary_endpoint: str
        primary_hostname: str
        url: str

        def __init__(
                self, 
                account_url: str, 
                file_system_name: str, 
                directory_name: str, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, AsyncTokenCredential]] = None, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                file_system_name: str, 
                directory_name: str, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, AsyncTokenCredential]] = None, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                **kwargs: Any
            ) -> Self: ...

        @distributed_trace_async
        async def acquire_lease(
                self, 
                lease_duration: int = -1, 
                lease_id: Optional[str] = None, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> DataLakeLeaseClient: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def create_directory(
                self, 
                metadata: Optional[Dict[str, str]] = None, 
                *, 
                acl: Optional[str] = ..., 
                content_settings: Optional[ContentSettings] = ..., 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                etag: Optional[str] = ..., 
                group: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                lease_duration: Optional[int] = ..., 
                lease_id: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                owner: Optional[str] = ..., 
                permissions: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                umask: Optional[str] = ..., 
                **kwargs
            ) -> Dict[str, Union[str, datetime]]: ...

        @distributed_trace_async
        async def create_file(
                self, 
                file: Union[FileProperties, str], 
                *, 
                acl: Optional[str] = ..., 
                content_settings: Optional[ContentSettings] = ..., 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                etag: Optional[str] = ..., 
                expires_on: Union[datetime, int] = ..., 
                group: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                lease_duration: Optional[int] = ..., 
                lease_id: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                metadata = ..., 
                owner: Optional[str] = ..., 
                permissions: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                umask: Optional[str] = ..., 
                **kwargs: Any
            ) -> DataLakeFileClient: ...

        @distributed_trace_async
        async def create_sub_directory(
                self, 
                sub_directory: Union[DirectoryProperties, str], 
                metadata: Optional[Dict[str, str]] = None, 
                *, 
                acl: Optional[str] = ..., 
                content_settings: Optional[ContentSettings] = ..., 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                etag: Optional[str] = ..., 
                group: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                lease_duration: Optional[int] = ..., 
                lease_id: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                owner: Optional[str] = ..., 
                permissions: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                umask: Optional[str] = ..., 
                **kwargs: Any
            ) -> DataLakeDirectoryClient: ...

        @distributed_trace_async
        async def delete_directory(
                self, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_sub_directory(
                self, 
                sub_directory: Union[DirectoryProperties, str], 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> DataLakeDirectoryClient: ...

        @distributed_trace_async
        async def exists(self, **kwargs: Any) -> bool: ...

        @distributed_trace_async
        async def get_access_control(
                self, 
                upn: Optional[bool] = None, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace_async
        async def get_directory_properties(
                self, 
                *, 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                upn: Optional[bool] = ..., 
                **kwargs: Any
            ) -> DirectoryProperties: ...

        def get_file_client(self, file: Union[FileProperties, str]) -> DataLakeFileClient: ...

        @distributed_trace
        def get_paths(
                self, 
                *, 
                max_results: Optional[int] = ..., 
                recursive: bool = True, 
                start_from: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                upn: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PathProperties]: ...

        def get_sub_directory_client(self, sub_directory: Union[DirectoryProperties, str]) -> DataLakeDirectoryClient: ...

        @distributed_trace_async
        async def get_tags(
                self, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                version_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> Dict[str, str]: ...

        @distributed_trace_async
        async def remove_access_control_recursive(
                self, 
                acl: str, 
                *, 
                batch_size: Optional[int] = ..., 
                continuation_token: Optional[str] = ..., 
                continue_on_failure: Optional[bool] = ..., 
                max_batches: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AccessControlChangeResult: ...

        @distributed_trace_async
        async def rename_directory(
                self, 
                new_name: str, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                source_etag: Optional[str] = ..., 
                source_if_modified_since: Optional[datetime] = ..., 
                source_if_unmodified_since: Optional[datetime] = ..., 
                source_lease: Union[DataLakeLeaseClient, str] = ..., 
                source_match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> DataLakeDirectoryClient: ...

        @distributed_trace_async
        async def set_access_control(
                self, 
                owner: Optional[str] = None, 
                group: Optional[str] = None, 
                permissions: Optional[str] = None, 
                acl: Optional[str] = None, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime]]: ...

        @distributed_trace_async
        async def set_access_control_recursive(
                self, 
                acl: str, 
                *, 
                batch_size: Optional[int] = ..., 
                continuation_token: Optional[str] = ..., 
                continue_on_failure: Optional[bool] = ..., 
                max_batches: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AccessControlChangeResult: ...

        @distributed_trace_async
        async def set_http_headers(
                self, 
                content_settings: Optional[ContentSettings] = None, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace_async
        async def set_metadata(
                self, 
                metadata: Dict[str, str], 
                *, 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime]]: ...

        @distributed_trace_async
        async def set_tags(
                self, 
                tags: Optional[Dict[str, str]] = None, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                validate_content: Optional[bool] = ..., 
                version_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace_async
        async def update_access_control_recursive(
                self, 
                acl: str, 
                *, 
                batch_size: Optional[int] = ..., 
                continuation_token: Optional[str] = ..., 
                continue_on_failure: Optional[bool] = ..., 
                max_batches: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AccessControlChangeResult: ...


    class azure.storage.filedatalake.aio.DataLakeFileClient(PathClient): implements AsyncContextManager 
        property api_version: str    # Read-only
        property location_mode: str
        property primary_endpoint: str    # Read-only
        property primary_hostname: str    # Read-only
        property secondary_endpoint: str    # Read-only
        property secondary_hostname: Optional[str]    # Read-only
        property url: str    # Read-only
        primary_endpoint: str
        primary_hostname: str
        url: str

        def __init__(
                self, 
                account_url: str, 
                file_system_name: str, 
                file_path: str, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, AsyncTokenCredential]] = None, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                file_system_name: str, 
                file_path: str, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, AsyncTokenCredential]] = None, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                **kwargs: Any
            ) -> Self: ...

        @distributed_trace_async
        async def acquire_lease(
                self, 
                lease_duration: int = -1, 
                lease_id: Optional[str] = None, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> DataLakeLeaseClient: ...

        @distributed_trace_async
        async def append_data(
                self, 
                data: Union[bytes, Iterable[bytes], AsyncIterable[bytes], IO[bytes]], 
                offset: int, 
                length: Optional[int] = None, 
                *, 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                flush: Optional[bool] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                lease_action: Literal[acquire, auto-renew, release, acquire-release] = ..., 
                lease_duration: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                validate_content: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def create_file(
                self, 
                content_settings: Optional[ContentSettings] = None, 
                metadata: Optional[Dict[str, str]] = None, 
                *, 
                acl: Optional[str] = ..., 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                encryption_context: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                expires_on: Union[datetime, int] = ..., 
                group: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                lease_duration: Optional[int] = ..., 
                lease_id: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                owner: Optional[str] = ..., 
                permissions: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                umask: Optional[str] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime]]: ...

        @distributed_trace_async
        async def delete_file(
                self, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def download_file(
                self, 
                offset: Optional[int] = None, 
                length: Optional[int] = None, 
                *, 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                decompress: Optional[bool] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                max_concurrency: Optional[int] = ..., 
                progress_hook: Callable[[int, Optional[int]], Awaitable[None]] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> StorageStreamDownloader: ...

        @distributed_trace_async
        async def exists(self, **kwargs: Any) -> bool: ...

        @distributed_trace_async
        async def flush_data(
                self, 
                offset: int, 
                retain_uncommitted_data: Optional[bool] = False, 
                *, 
                close: Optional[bool] = ..., 
                content_settings: Optional[ContentSettings] = ..., 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                lease_action: Literal[acquire, auto-renew, release, acquire-release] = ..., 
                lease_duration: Optional[int] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace_async
        async def get_access_control(
                self, 
                upn: Optional[bool] = None, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace_async
        async def get_file_properties(
                self, 
                *, 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                upn: Optional[bool] = ..., 
                **kwargs: Any
            ) -> FileProperties: ...

        @distributed_trace_async
        async def get_tags(
                self, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                version_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> Dict[str, str]: ...

        @distributed_trace_async
        async def remove_access_control_recursive(
                self, 
                acl: str, 
                *, 
                batch_size: Optional[int] = ..., 
                continuation_token: Optional[str] = ..., 
                continue_on_failure: Optional[bool] = ..., 
                max_batches: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AccessControlChangeResult: ...

        @distributed_trace_async
        async def rename_file(
                self, 
                new_name: str, 
                *, 
                content_settings: Optional[ContentSettings] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                source_etag: Optional[str] = ..., 
                source_if_modified_since: Optional[datetime] = ..., 
                source_if_unmodified_since: Optional[datetime] = ..., 
                source_lease: Union[DataLakeLeaseClient, str] = ..., 
                source_match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> DataLakeFileClient: ...

        @distributed_trace_async
        async def set_access_control(
                self, 
                owner: Optional[str] = None, 
                group: Optional[str] = None, 
                permissions: Optional[str] = None, 
                acl: Optional[str] = None, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime]]: ...

        @distributed_trace_async
        async def set_access_control_recursive(
                self, 
                acl: str, 
                *, 
                batch_size: Optional[int] = ..., 
                continuation_token: Optional[str] = ..., 
                continue_on_failure: Optional[bool] = ..., 
                max_batches: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AccessControlChangeResult: ...

        @distributed_trace_async
        async def set_file_expiry(
                self, 
                expiry_options: str, 
                expires_on: Optional[Union[datetime, int]] = None, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def set_http_headers(
                self, 
                content_settings: Optional[ContentSettings] = None, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace_async
        async def set_metadata(
                self, 
                metadata: Dict[str, str], 
                *, 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime]]: ...

        @distributed_trace_async
        async def set_tags(
                self, 
                tags: Optional[Dict[str, str]] = None, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_tags_match_condition: Optional[str] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                validate_content: Optional[bool] = ..., 
                version_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace_async
        async def update_access_control_recursive(
                self, 
                acl: str, 
                *, 
                batch_size: Optional[int] = ..., 
                continuation_token: Optional[str] = ..., 
                continue_on_failure: Optional[bool] = ..., 
                max_batches: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AccessControlChangeResult: ...

        @distributed_trace_async
        async def upload_data(
                self, 
                data: Union[bytes, str, Iterable[AnyStr], AsyncIterable[AnyStr], IO[bytes]], 
                length: Optional[int] = None, 
                overwrite: Optional[bool] = False, 
                *, 
                chunk_size: Optional[int] = ..., 
                content_settings: Optional[ContentSettings] = ..., 
                cpk: Optional[CustomerProvidedEncryptionKey] = ..., 
                encryption_context: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                max_concurrency: Optional[int] = ..., 
                metadata: Union[Dict[str, str], None] = ..., 
                permissions: Optional[str] = ..., 
                progress_hook: Callable[[int, Optional[int]], Awaitable[None]] = ..., 
                timeout: Optional[int] = ..., 
                umask: Optional[str] = ..., 
                validate_content: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...


    class azure.storage.filedatalake.aio.DataLakeLeaseClient: implements AsyncContextManager 
        etag: Optional[str]
        id: str
        last_modified: Optional[datetime]

        def __init__(
                self, 
                client: Union[FileSystemClient, DataLakeDirectoryClient, DataLakeFileClient], 
                lease_id: Optional[str] = None
            ) -> None: ...

        @distributed_trace_async
        async def acquire(
                self, 
                lease_duration: int = -1, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
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
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.storage.filedatalake.aio.DataLakeServiceClient(AsyncStorageAccountHostsMixin, StorageAccountHostsMixin): implements AsyncContextManager 
        property api_version: str    # Read-only
        property location_mode: str
        property primary_endpoint: str    # Read-only
        property primary_hostname: str    # Read-only
        property secondary_endpoint: str    # Read-only
        property secondary_hostname: Optional[str]    # Read-only
        property url: str    # Read-only
        primary_endpoint: str
        primary_hostname: str
        url: str

        def __init__(
                self, 
                account_url: str, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, AsyncTokenCredential]] = None, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
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
                **kwargs: Any
            ) -> Self: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def create_file_system(
                self, 
                file_system: Union[FileSystemProperties, str], 
                metadata: Optional[Dict[str, str]] = None, 
                public_access: Optional[PublicAccess] = None, 
                *, 
                encryption_scope_options: Union[dict, EncryptionScopeOptions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> FileSystemClient: ...

        @distributed_trace_async
        async def delete_file_system(
                self, 
                file_system: Union[FileSystemProperties, str], 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> FileSystemClient: ...

        def get_directory_client(
                self, 
                file_system: Union[FileSystemProperties, str], 
                directory: Union[DirectoryProperties, str]
            ) -> DataLakeDirectoryClient: ...

        def get_file_client(
                self, 
                file_system: Union[FileSystemProperties, str], 
                file_path: Union[FileProperties, str]
            ) -> DataLakeFileClient: ...

        def get_file_system_client(self, file_system: Union[FileSystemProperties, str]) -> FileSystemClient: ...

        @distributed_trace_async
        async def get_service_properties(
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
        def list_file_systems(
                self, 
                name_starts_with: Optional[str] = None, 
                include_metadata: bool = False, 
                *, 
                include_deleted: Optional[bool] = ..., 
                include_system: Optional[bool] = ..., 
                results_per_page: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[FileSystemProperties]: ...

        @distributed_trace_async
        async def set_service_properties(
                self, 
                *, 
                analytics_logging = ..., 
                cors = ..., 
                delete_retention_policy = ..., 
                hour_metrics = ..., 
                minute_metrics = ..., 
                static_website = ..., 
                target_version: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def undelete_file_system(
                self, 
                name: str, 
                deleted_version: str, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> FileSystemClient: ...


    class azure.storage.filedatalake.aio.ExponentialRetry(AsyncStorageRetryPolicy):
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


    class azure.storage.filedatalake.aio.FileSystemClient(AsyncStorageAccountHostsMixin, StorageAccountHostsMixin): implements AsyncContextManager 
        property api_version: str    # Read-only
        property location_mode: str
        property primary_endpoint: str    # Read-only
        property primary_hostname: str    # Read-only
        property secondary_endpoint: str    # Read-only
        property secondary_hostname: Optional[str]    # Read-only
        property url: str    # Read-only
        primary_endpoint: str
        primary_hostname: str
        url: str

        def __init__(
                self, 
                account_url: str, 
                file_system_name: str, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, AsyncTokenCredential]] = None, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                file_system_name: str, 
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
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> DataLakeLeaseClient: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def create_directory(
                self, 
                directory: Union[DirectoryProperties, str], 
                metadata: Optional[Dict[str, str]] = None, 
                *, 
                acl: Optional[str] = ..., 
                content_settings: Optional[ContentSettings] = ..., 
                etag: Optional[str] = ..., 
                group: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                lease_duration: Optional[int] = ..., 
                lease_id: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                owner: Optional[str] = ..., 
                permissions: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                umask: Optional[str] = ..., 
                **kwargs: Any
            ) -> DataLakeDirectoryClient: ...

        @distributed_trace_async
        async def create_file(
                self, 
                file: Union[FileProperties, str], 
                *, 
                acl: Optional[str] = ..., 
                content_settings: Optional[ContentSettings] = ..., 
                etag: Optional[str] = ..., 
                expires_on: Union[datetime, int] = ..., 
                group: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                lease_duration: Optional[int] = ..., 
                lease_id: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                metadata: Dict[str, str] = ..., 
                owner: Optional[str] = ..., 
                permissions: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                umask: Optional[str] = ..., 
                **kwargs: Any
            ) -> DataLakeFileClient: ...

        @distributed_trace_async
        async def create_file_system(
                self, 
                metadata: Optional[Dict[str, str]] = None, 
                public_access: Optional[PublicAccess] = None, 
                *, 
                encryption_scope_options: Union[dict, EncryptionScopeOptions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime]]: ...

        @distributed_trace_async
        async def delete_directory(
                self, 
                directory: Union[DirectoryProperties, str], 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> DataLakeDirectoryClient: ...

        @distributed_trace_async
        async def delete_file(
                self, 
                file: Union[FileProperties, str], 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> DataLakeFileClient: ...

        @distributed_trace_async
        async def delete_file_system(
                self, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def exists(
                self, 
                *, 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> bool: ...

        def get_directory_client(self, directory: Union[DirectoryProperties, str]) -> DataLakeDirectoryClient: ...

        def get_file_client(self, file_path: Union[FileProperties, str]) -> DataLakeFileClient: ...

        @distributed_trace_async
        async def get_file_system_access_policy(
                self, 
                *, 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace_async
        async def get_file_system_properties(
                self, 
                *, 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> FileSystemProperties: ...

        @distributed_trace
        def get_paths(
                self, 
                path: Optional[str] = None, 
                recursive: Optional[bool] = True, 
                max_results: Optional[int] = None, 
                *, 
                start_from: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                upn: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PathProperties]: ...

        @distributed_trace
        def list_deleted_paths(
                self, 
                *, 
                path_prefix: Optional[str] = ..., 
                results_per_page: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DeletedPathProperties]: ...

        @distributed_trace_async
        async def set_file_system_access_policy(
                self, 
                signed_identifiers: Dict[str, AccessPolicy], 
                public_access: Optional[Union[str, PublicAccess]] = None, 
                *, 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime]]: ...

        @distributed_trace_async
        async def set_file_system_metadata(
                self, 
                metadata: Dict[str, str], 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                lease: Union[DataLakeLeaseClient, str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Dict[str, Union[str, datetime]]: ...


    class azure.storage.filedatalake.aio.LinearRetry(AsyncStorageRetryPolicy):
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


    class azure.storage.filedatalake.aio.StorageStreamDownloader:
        name: str
        properties: FileProperties
        size: int

        def __init__(self, downloader: Any) -> None: ...

        def __len__(self) -> int: ...

        def chunks(self) -> AsyncIterator[bytes]: ...

        async def read(self, size: int = -1) -> bytes: ...

        async def readall(self) -> bytes: ...

        async def readinto(self, stream: IO[bytes]) -> int: ...


```