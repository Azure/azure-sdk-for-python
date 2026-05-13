```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.appconfiguration

    class azure.appconfiguration.AzureAppConfigurationClient: implements ContextManager 

        def __init__(
                self, 
                base_url: str, 
                credential: TokenCredential, 
                *, 
                api_version: str = ..., 
                audience: str = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                connection_string: str, 
                **kwargs: Any
            ) -> AzureAppConfigurationClient: ...

        @distributed_trace
        def add_configuration_setting(
                self, 
                configuration_setting: ConfigurationSetting, 
                **kwargs: Any
            ) -> ConfigurationSetting: ...

        @distributed_trace
        def archive_snapshot(
                self, 
                name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                **kwargs: Any
            ) -> ConfigurationSnapshot: ...

        @distributed_trace
        def begin_create_snapshot(
                self, 
                name: str, 
                filters: List[ConfigurationSettingsFilter], 
                *, 
                composition_type: Optional[Union[str, SnapshotComposition]] = ..., 
                retention_period: Optional[int] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> LROPoller[ConfigurationSnapshot]: ...

        def close(self) -> None: ...

        @distributed_trace
        def delete_configuration_setting(
                self, 
                key: str, 
                label: Optional[str] = None, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                **kwargs: Any
            ) -> Union[None, ConfigurationSetting]: ...

        @distributed_trace
        def get_configuration_setting(
                self, 
                key: str, 
                label: Optional[str] = None, 
                etag: Optional[str] = "*", 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                *, 
                accept_datetime: Optional[Union[datetime, str]] = ..., 
                **kwargs: Any
            ) -> Union[None, ConfigurationSetting]: ...

        @distributed_trace
        def get_snapshot(
                self, 
                name: str, 
                *, 
                fields: Optional[List[Union[str, SnapshotFields]]] = ..., 
                **kwargs: Any
            ) -> ConfigurationSnapshot: ...

        @overload
        def list_configuration_settings(
                self, 
                *, 
                accept_datetime: Optional[Union[datetime, str]] = ..., 
                fields: Optional[List[Union[str, ConfigurationSettingFields]]] = ..., 
                key_filter: Optional[str] = ..., 
                label_filter: Optional[str] = ..., 
                tags_filter: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ConfigurationSetting]: ...

        @overload
        def list_configuration_settings(
                self, 
                *, 
                fields: Optional[List[Union[str, ConfigurationSettingFields]]] = ..., 
                snapshot_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ConfigurationSetting]: ...

        @distributed_trace
        def list_labels(
                self, 
                *, 
                accept_datetime: Optional[Union[datetime, str]] = ..., 
                after: Optional[str] = ..., 
                fields: Optional[List[Union[str, LabelFields]]] = ..., 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ConfigurationSettingLabel]: ...

        @distributed_trace
        def list_revisions(
                self, 
                key_filter: Optional[str] = None, 
                label_filter: Optional[str] = None, 
                *, 
                accept_datetime: Optional[Union[datetime, str]] = ..., 
                fields: Optional[List[Union[str, ConfigurationSettingFields]]] = ..., 
                tags_filter: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ConfigurationSetting]: ...

        @distributed_trace
        def list_snapshots(
                self, 
                *, 
                fields: Optional[List[Union[str, SnapshotFields]]] = ..., 
                name: Optional[str] = ..., 
                status: Optional[List[Union[str, SnapshotStatus]]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ConfigurationSnapshot]: ...

        @distributed_trace
        def recover_snapshot(
                self, 
                name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                **kwargs: Any
            ) -> ConfigurationSnapshot: ...

        @distributed_trace
        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...

        @distributed_trace
        def set_configuration_setting(
                self, 
                configuration_setting: ConfigurationSetting, 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                *, 
                etag: Optional[str] = ..., 
                **kwargs: Any
            ) -> ConfigurationSetting: ...

        @distributed_trace
        def set_read_only(
                self, 
                configuration_setting: ConfigurationSetting, 
                read_only: bool = True, 
                *, 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                **kwargs: Any
            ) -> ConfigurationSetting: ...

        def update_sync_token(self, token: str) -> None: ...


    class azure.appconfiguration.ConfigurationSetting(Model):
        content_type: Optional[str]
        etag: str
        key: str
        kind = Generic
        label: str
        last_modified: datetime
        read_only: bool
        tags: Dict[str, str]
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.appconfiguration.ConfigurationSettingFields(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTENT_TYPE = "content_type"
        ETAG = "etag"
        KEY = "key"
        LABEL = "label"
        LAST_MODIFIED = "last_modified"
        LOCKED = "locked"
        TAGS = "tags"
        VALUE = "value"


    class azure.appconfiguration.ConfigurationSettingLabel:
        name: Optional[str]

        def __init__(
                self, 
                *, 
                name: Optional[str] = ...
            ) -> None: ...


    class azure.appconfiguration.ConfigurationSettingsFilter:
        key: str
        label: Optional[str]
        tags: Optional[List[str]]

        def __init__(
                self, 
                *, 
                key: str, 
                label: Optional[str] = ..., 
                tags: Optional[List[str]] = ...
            ) -> None: ...


    class azure.appconfiguration.ConfigurationSnapshot:
        composition_type: Optional[Union[str, SnapshotComposition]]
        created: Optional[datetime]
        etag: Optional[str]
        expires: Optional[datetime]
        filters: List[ConfigurationSettingsFilter]
        items_count: Optional[int]
        name: Optional[str]
        retention_period: Optional[int]
        size: Optional[int]
        status: Optional[Union[str, SnapshotStatus]]
        tags: Optional[Dict[str, str]]

        def __init__(
                self, 
                filters: List[ConfigurationSettingsFilter], 
                *, 
                composition_type: Optional[Union[str, SnapshotComposition]] = ..., 
                retention_period: Optional[int] = ..., 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...


    class azure.appconfiguration.FeatureFlagConfigurationSetting(ConfigurationSetting):
        property value: str
        content_type: str
        description: str
        display_name: str
        enabled: bool
        etag: str
        feature_id: str
        filters: Optional[List[Dict[str, Any]]]
        key: str
        kind = FeatureFlag
        label: str
        last_modified: datetime
        read_only: bool
        tags: Dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                feature_id: str, 
                *, 
                enabled: bool = False, 
                filters: Optional[List[Dict[str, Any]]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.appconfiguration.LabelFields(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NAME = "name"


    class azure.appconfiguration.ResourceReadOnlyError(HttpResponseError):


    class azure.appconfiguration.SecretReferenceConfigurationSetting(ConfigurationSetting):
        property value: str
        content_type: str
        etag: str
        key: str
        kind = SecretReference
        label: str
        last_modified: datetime
        read_only: bool
        secret_id: Optional[str]
        tags: Dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                key: str, 
                secret_id: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.appconfiguration.SnapshotComposition(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        KEY = "key"
        KEY_LABEL = "key_label"


    class azure.appconfiguration.SnapshotFields(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPOSITION_TYPE = "composition_type"
        CREATED = "created"
        ETAG = "etag"
        EXPIRES = "expires"
        FILTERS = "filters"
        ITEMS_COUNT = "items_count"
        NAME = "name"
        RETENTION_PERIOD = "retention_period"
        SIZE = "size"
        STATUS = "status"
        TAGS = "tags"


    class azure.appconfiguration.SnapshotStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARCHIVED = "archived"
        FAILED = "failed"
        PROVISIONING = "provisioning"
        READY = "ready"


namespace azure.appconfiguration.aio

    class azure.appconfiguration.aio.AzureAppConfigurationClient: implements AsyncContextManager 

        def __init__(
                self, 
                base_url: str, 
                credential: AsyncTokenCredential, 
                *, 
                api_version: str = ..., 
                audience: str = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                connection_string: str, 
                **kwargs: Any
            ) -> AzureAppConfigurationClient: ...

        @distributed_trace_async
        async def add_configuration_setting(
                self, 
                configuration_setting: ConfigurationSetting, 
                **kwargs: Any
            ) -> ConfigurationSetting: ...

        @distributed_trace_async
        async def archive_snapshot(
                self, 
                name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                **kwargs: Any
            ) -> ConfigurationSnapshot: ...

        @distributed_trace_async
        async def begin_create_snapshot(
                self, 
                name: str, 
                filters: List[ConfigurationSettingsFilter], 
                *, 
                composition_type: Optional[Union[str, SnapshotComposition]] = ..., 
                retention_period: Optional[int] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[ConfigurationSnapshot]: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def delete_configuration_setting(
                self, 
                key: str, 
                label: Optional[str] = None, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                **kwargs: Any
            ) -> Union[None, ConfigurationSetting]: ...

        @distributed_trace_async
        async def get_configuration_setting(
                self, 
                key: str, 
                label: Optional[str] = None, 
                etag: Optional[str] = "*", 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                *, 
                accept_datetime: Optional[Union[datetime, str]] = ..., 
                **kwargs: Any
            ) -> Union[None, ConfigurationSetting]: ...

        @distributed_trace_async
        async def get_snapshot(
                self, 
                name: str, 
                *, 
                fields: Optional[List[Union[str, SnapshotFields]]] = ..., 
                **kwargs: Any
            ) -> ConfigurationSnapshot: ...

        @overload
        def list_configuration_settings(
                self, 
                *, 
                accept_datetime: Optional[Union[datetime, str]] = ..., 
                fields: Optional[List[Union[str, ConfigurationSettingFields]]] = ..., 
                key_filter: Optional[str] = ..., 
                label_filter: Optional[str] = ..., 
                tags_filter: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ConfigurationSetting]: ...

        @overload
        def list_configuration_settings(
                self, 
                *, 
                fields: Optional[List[Union[str, ConfigurationSettingFields]]] = ..., 
                snapshot_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ConfigurationSetting]: ...

        @distributed_trace
        def list_labels(
                self, 
                *, 
                accept_datetime: Optional[Union[datetime, str]] = ..., 
                after: Optional[str] = ..., 
                fields: Optional[List[Union[str, LabelFields]]] = ..., 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ConfigurationSettingLabel]: ...

        @distributed_trace
        def list_revisions(
                self, 
                key_filter: Optional[str] = None, 
                label_filter: Optional[str] = None, 
                *, 
                accept_datetime: Optional[Union[datetime, str]] = ..., 
                fields: Optional[List[Union[str, ConfigurationSettingFields]]] = ..., 
                tags_filter: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ConfigurationSetting]: ...

        @distributed_trace
        def list_snapshots(
                self, 
                *, 
                fields: Optional[List[Union[str, SnapshotFields]]] = ..., 
                name: Optional[str] = ..., 
                status: Optional[List[Union[str, SnapshotStatus]]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ConfigurationSnapshot]: ...

        @distributed_trace_async
        async def recover_snapshot(
                self, 
                name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                **kwargs: Any
            ) -> ConfigurationSnapshot: ...

        @distributed_trace_async
        async def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> AsyncHttpResponse: ...

        @distributed_trace_async
        async def set_configuration_setting(
                self, 
                configuration_setting: ConfigurationSetting, 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                *, 
                etag: Optional[str] = ..., 
                **kwargs: Any
            ) -> ConfigurationSetting: ...

        @distributed_trace_async
        async def set_read_only(
                self, 
                configuration_setting: ConfigurationSetting, 
                read_only: bool = True, 
                *, 
                match_condition: MatchConditions = MatchConditions.Unconditionally, 
                **kwargs: Any
            ) -> ConfigurationSetting: ...

        async def update_sync_token(self, token: str) -> None: ...


```