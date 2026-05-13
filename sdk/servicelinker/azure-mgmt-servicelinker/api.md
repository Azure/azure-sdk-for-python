```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.servicelinker

    class azure.mgmt.servicelinker.ServiceLinkerManagementClient: implements ContextManager 
        configuration_names: ConfigurationNamesOperations
        connector: ConnectorOperations
        linker: LinkerOperations
        linkers: LinkersOperations
        operations: Operations

        def __init__(
                self, 
                credential: TokenCredential, 
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...


namespace azure.mgmt.servicelinker.aio

    class azure.mgmt.servicelinker.aio.ServiceLinkerManagementClient: implements AsyncContextManager 
        configuration_names: ConfigurationNamesOperations
        connector: ConnectorOperations
        linker: LinkerOperations
        linkers: LinkersOperations
        operations: Operations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...


namespace azure.mgmt.servicelinker.aio.operations

    class azure.mgmt.servicelinker.aio.operations.ConfigurationNamesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                filter: Optional[str] = None, 
                skip_token: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[ConfigurationNameItem]: ...


    class azure.mgmt.servicelinker.aio.operations.ConnectorOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_dryrun(
                self, 
                subscription_id: str, 
                resource_group_name: str, 
                location: str, 
                dryrun_name: str, 
                parameters: DryrunResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DryrunResource]: ...

        @overload
        async def begin_create_dryrun(
                self, 
                subscription_id: str, 
                resource_group_name: str, 
                location: str, 
                dryrun_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DryrunResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                subscription_id: str, 
                resource_group_name: str, 
                location: str, 
                connector_name: str, 
                parameters: LinkerResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LinkerResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                subscription_id: str, 
                resource_group_name: str, 
                location: str, 
                connector_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LinkerResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                subscription_id: str, 
                resource_group_name: str, 
                location: str, 
                connector_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                subscription_id: str, 
                resource_group_name: str, 
                location: str, 
                connector_name: str, 
                parameters: LinkerPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LinkerResource]: ...

        @overload
        async def begin_update(
                self, 
                subscription_id: str, 
                resource_group_name: str, 
                location: str, 
                connector_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LinkerResource]: ...

        @overload
        async def begin_update_dryrun(
                self, 
                subscription_id: str, 
                resource_group_name: str, 
                location: str, 
                dryrun_name: str, 
                parameters: DryrunPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DryrunResource]: ...

        @overload
        async def begin_update_dryrun(
                self, 
                subscription_id: str, 
                resource_group_name: str, 
                location: str, 
                dryrun_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DryrunResource]: ...

        @distributed_trace_async
        async def begin_validate(
                self, 
                subscription_id: str, 
                resource_group_name: str, 
                location: str, 
                connector_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ValidateOperationResult]: ...

        @distributed_trace_async
        async def delete_dryrun(
                self, 
                subscription_id: str, 
                resource_group_name: str, 
                location: str, 
                dryrun_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def generate_configurations(
                self, 
                subscription_id: str, 
                resource_group_name: str, 
                location: str, 
                connector_name: str, 
                parameters: Optional[ConfigurationInfo] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationResult: ...

        @overload
        async def generate_configurations(
                self, 
                subscription_id: str, 
                resource_group_name: str, 
                location: str, 
                connector_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationResult: ...

        @distributed_trace_async
        async def get(
                self, 
                subscription_id: str, 
                resource_group_name: str, 
                location: str, 
                connector_name: str, 
                **kwargs: Any
            ) -> LinkerResource: ...

        @distributed_trace_async
        async def get_dryrun(
                self, 
                subscription_id: str, 
                resource_group_name: str, 
                location: str, 
                dryrun_name: str, 
                **kwargs: Any
            ) -> DryrunResource: ...

        @distributed_trace
        def list(
                self, 
                subscription_id: str, 
                resource_group_name: str, 
                location: str, 
                **kwargs: Any
            ) -> AsyncIterable[LinkerResource]: ...

        @distributed_trace
        def list_dryrun(
                self, 
                subscription_id: str, 
                resource_group_name: str, 
                location: str, 
                **kwargs: Any
            ) -> AsyncIterable[DryrunResource]: ...


    class azure.mgmt.servicelinker.aio.operations.LinkerOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_uri: str, 
                linker_name: str, 
                parameters: LinkerResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LinkerResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_uri: str, 
                linker_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LinkerResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_uri: str, 
                linker_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_uri: str, 
                linker_name: str, 
                parameters: LinkerPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LinkerResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_uri: str, 
                linker_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LinkerResource]: ...

        @distributed_trace_async
        async def begin_validate(
                self, 
                resource_uri: str, 
                linker_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ValidateOperationResult]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_uri: str, 
                linker_name: str, 
                **kwargs: Any
            ) -> LinkerResource: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> AsyncIterable[LinkerResource]: ...

        @distributed_trace_async
        async def list_configurations(
                self, 
                resource_uri: str, 
                linker_name: str, 
                **kwargs: Any
            ) -> ConfigurationResult: ...


    class azure.mgmt.servicelinker.aio.operations.LinkersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_dryrun(
                self, 
                resource_uri: str, 
                dryrun_name: str, 
                parameters: DryrunResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DryrunResource]: ...

        @overload
        async def begin_create_dryrun(
                self, 
                resource_uri: str, 
                dryrun_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DryrunResource]: ...

        @overload
        async def begin_update_dryrun(
                self, 
                resource_uri: str, 
                dryrun_name: str, 
                parameters: DryrunPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DryrunResource]: ...

        @overload
        async def begin_update_dryrun(
                self, 
                resource_uri: str, 
                dryrun_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DryrunResource]: ...

        @distributed_trace_async
        async def delete_dryrun(
                self, 
                resource_uri: str, 
                dryrun_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def generate_configurations(
                self, 
                resource_uri: str, 
                linker_name: str, 
                parameters: Optional[ConfigurationInfo] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationResult: ...

        @overload
        async def generate_configurations(
                self, 
                resource_uri: str, 
                linker_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationResult: ...

        @distributed_trace_async
        async def get_dryrun(
                self, 
                resource_uri: str, 
                dryrun_name: str, 
                **kwargs: Any
            ) -> DryrunResource: ...

        @distributed_trace
        def list_dapr_configurations(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> AsyncIterable[DaprConfigurationResource]: ...

        @distributed_trace
        def list_dryrun(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> AsyncIterable[DryrunResource]: ...


    class azure.mgmt.servicelinker.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncIterable[Operation]: ...


namespace azure.mgmt.servicelinker.models

    class azure.mgmt.servicelinker.models.AccessKeyInfoBase(AuthInfoBase):
        auth_mode: Union[str, AuthMode]
        auth_type: Union[str, AuthType]
        permissions: Union[list[str, AccessKeyPermissions]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auth_mode: Optional[Union[str, AuthMode]] = ..., 
                permissions: Optional[List[Union[str, AccessKeyPermissions]]] = ..., 
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


    class azure.mgmt.servicelinker.models.AccessKeyPermissions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LISTEN = "Listen"
        MANAGE = "Manage"
        READ = "Read"
        SEND = "Send"
        WRITE = "Write"


    class azure.mgmt.servicelinker.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENABLE = "enable"
        INTERNAL = "Internal"
        OPT_OUT = "optOut"


    class azure.mgmt.servicelinker.models.AllowType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "false"
        TRUE = "true"


    class azure.mgmt.servicelinker.models.AuthInfoBase(Model):
        auth_mode: Union[str, AuthMode]
        auth_type: Union[str, AuthType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auth_mode: Optional[Union[str, AuthMode]] = ..., 
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


    class azure.mgmt.servicelinker.models.AuthMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OPT_IN_ALL_AUTH = "optInAllAuth"
        OPT_OUT_ALL_AUTH = "optOutAllAuth"


    class azure.mgmt.servicelinker.models.AuthType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCESS_KEY = "accessKey"
        EASY_AUTH_MICROSOFT_ENTRA_ID = "easyAuthMicrosoftEntraID"
        SECRET = "secret"
        SERVICE_PRINCIPAL_CERTIFICATE = "servicePrincipalCertificate"
        SERVICE_PRINCIPAL_SECRET = "servicePrincipalSecret"
        SYSTEM_ASSIGNED_IDENTITY = "systemAssignedIdentity"
        USER_ACCOUNT = "userAccount"
        USER_ASSIGNED_IDENTITY = "userAssignedIdentity"


    class azure.mgmt.servicelinker.models.AzureAppConfigProperties(AzureResourcePropertiesBase):
        connect_with_kubernetes_extension: bool
        type: Union[str, AzureResourceType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                connect_with_kubernetes_extension: Optional[bool] = ..., 
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


    class azure.mgmt.servicelinker.models.AzureKeyVaultProperties(AzureResourcePropertiesBase):
        connect_as_kubernetes_csi_driver: bool
        type: Union[str, AzureResourceType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                connect_as_kubernetes_csi_driver: Optional[bool] = ..., 
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


    class azure.mgmt.servicelinker.models.AzureResource(TargetServiceBase):
        id: str
        resource_properties: AzureResourcePropertiesBase
        type: Union[str, TargetServiceType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                resource_properties: Optional[AzureResourcePropertiesBase] = ..., 
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


    class azure.mgmt.servicelinker.models.AzureResourcePropertiesBase(Model):
        type: Union[str, AzureResourceType]

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


    class azure.mgmt.servicelinker.models.AzureResourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APP_CONFIG = "AppConfig"
        KEY_VAULT = "KeyVault"


    class azure.mgmt.servicelinker.models.BasicErrorDryrunPrerequisiteResult(DryrunPrerequisiteResult):
        code: str
        message: str
        type: Union[str, DryrunPrerequisiteResultType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
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


    class azure.mgmt.servicelinker.models.ClientType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAPR = "dapr"
        DJANGO = "django"
        DOTNET = "dotnet"
        GO = "go"
        JAVA = "java"
        JMS_SPRING_BOOT = "jms-springBoot"
        KAFKA_SPRING_BOOT = "kafka-springBoot"
        NODEJS = "nodejs"
        NONE = "none"
        PHP = "php"
        PYTHON = "python"
        RUBY = "ruby"
        SPRING_BOOT = "springBoot"


    class azure.mgmt.servicelinker.models.ConfigurationInfo(Model):
        action: Union[str, ActionType]
        additional_configurations: dict[str, str]
        additional_connection_string_properties: dict[str, str]
        configuration_store: ConfigurationStore
        customized_keys: dict[str, str]
        dapr_properties: DaprProperties
        delete_or_update_behavior: Union[str, DeleteOrUpdateBehavior]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                action: Optional[Union[str, ActionType]] = ..., 
                additional_configurations: Optional[Dict[str, str]] = ..., 
                additional_connection_string_properties: Optional[Dict[str, str]] = ..., 
                configuration_store: Optional[ConfigurationStore] = ..., 
                customized_keys: Optional[Dict[str, str]] = ..., 
                dapr_properties: Optional[DaprProperties] = ..., 
                delete_or_update_behavior: Optional[Union[str, DeleteOrUpdateBehavior]] = ..., 
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


    class azure.mgmt.servicelinker.models.ConfigurationName(Model):
        description: str
        required: bool
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                required: Optional[bool] = ..., 
                value: Optional[str] = ..., 
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


    class azure.mgmt.servicelinker.models.ConfigurationNameItem(Model):
        auth_type: Union[str, AuthType]
        client_type: Union[str, ClientType]
        dapr_properties: DaprProperties
        names: list[ConfigurationName]
        secret_type: Union[str, SecretSourceType]
        target_service: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auth_type: Optional[Union[str, AuthType]] = ..., 
                client_type: Optional[Union[str, ClientType]] = ..., 
                dapr_properties: Optional[DaprProperties] = ..., 
                names: Optional[List[ConfigurationName]] = ..., 
                secret_type: Optional[Union[str, SecretSourceType]] = ..., 
                target_service: Optional[str] = ..., 
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


    class azure.mgmt.servicelinker.models.ConfigurationNameResult(Model):
        next_link: str
        value: list[ConfigurationNameItem]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[ConfigurationNameItem]] = ..., 
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


    class azure.mgmt.servicelinker.models.ConfigurationResult(Model):
        configurations: list[SourceConfiguration]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                configurations: Optional[List[SourceConfiguration]] = ..., 
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


    class azure.mgmt.servicelinker.models.ConfigurationStore(Model):
        app_configuration_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                app_configuration_id: Optional[str] = ..., 
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


    class azure.mgmt.servicelinker.models.ConfluentBootstrapServer(TargetServiceBase):
        endpoint: str
        type: Union[str, TargetServiceType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                endpoint: Optional[str] = ..., 
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


    class azure.mgmt.servicelinker.models.ConfluentSchemaRegistry(TargetServiceBase):
        endpoint: str
        type: Union[str, TargetServiceType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                endpoint: Optional[str] = ..., 
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


    class azure.mgmt.servicelinker.models.CreateOrUpdateDryrunParameters(DryrunParameters, LinkerProperties):
        action_name: Union[str, DryrunActionName]
        auth_info: AuthInfoBase
        client_type: Union[str, ClientType]
        configuration_info: ConfigurationInfo
        provisioning_state: str
        public_network_solution: PublicNetworkSolution
        scope: str
        secret_store: SecretStore
        target_service: TargetServiceBase
        v_net_solution: VNetSolution

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auth_info: Optional[AuthInfoBase] = ..., 
                client_type: Optional[Union[str, ClientType]] = ..., 
                configuration_info: Optional[ConfigurationInfo] = ..., 
                public_network_solution: Optional[PublicNetworkSolution] = ..., 
                scope: Optional[str] = ..., 
                secret_store: Optional[SecretStore] = ..., 
                target_service: Optional[TargetServiceBase] = ..., 
                v_net_solution: Optional[VNetSolution] = ..., 
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


    class azure.mgmt.servicelinker.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.servicelinker.models.DaprBindingComponentDirection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INPUT = "input"
        OUTPUT = "output"


    class azure.mgmt.servicelinker.models.DaprConfigurationList(Model):
        next_link: str
        value: list[DaprConfigurationResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[DaprConfigurationResource]] = ..., 
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


    class azure.mgmt.servicelinker.models.DaprConfigurationResource(Model):
        auth_type: Union[str, AuthType]
        dapr_properties: DaprProperties
        target_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auth_type: Optional[Union[str, AuthType]] = ..., 
                dapr_properties: Optional[DaprProperties] = ..., 
                target_type: Optional[str] = ..., 
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


    class azure.mgmt.servicelinker.models.DaprMetadata(Model):
        description: str
        name: str
        required: Union[str, DaprMetadataRequired]
        secret_ref: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                required: Optional[Union[str, DaprMetadataRequired]] = ..., 
                secret_ref: Optional[str] = ..., 
                value: Optional[str] = ..., 
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


    class azure.mgmt.servicelinker.models.DaprMetadataRequired(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "false"
        TRUE = "true"


    class azure.mgmt.servicelinker.models.DaprProperties(Model):
        binding_component_direction: Union[str, DaprBindingComponentDirection]
        component_type: str
        metadata: list[DaprMetadata]
        runtime_version: str
        scopes: list[str]
        secret_store_component: str
        version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                component_type: Optional[str] = ..., 
                metadata: Optional[List[DaprMetadata]] = ..., 
                scopes: Optional[List[str]] = ..., 
                secret_store_component: Optional[str] = ..., 
                version: Optional[str] = ..., 
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


    class azure.mgmt.servicelinker.models.DatabaseAadAuthInfo(Model):
        user_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                user_name: Optional[str] = ..., 
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


    class azure.mgmt.servicelinker.models.DeleteOrUpdateBehavior(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        FORCED_CLEANUP = "ForcedCleanup"


    class azure.mgmt.servicelinker.models.DryrunActionName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATE_OR_UPDATE = "createOrUpdate"


    class azure.mgmt.servicelinker.models.DryrunList(Model):
        next_link: str
        value: list[DryrunResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[DryrunResource]] = ..., 
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


    class azure.mgmt.servicelinker.models.DryrunOperationPreview(Model):
        action: str
        description: str
        name: str
        operation_type: Union[str, DryrunPreviewOperationType]
        scope: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                action: Optional[str] = ..., 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operation_type: Optional[Union[str, DryrunPreviewOperationType]] = ..., 
                scope: Optional[str] = ..., 
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


    class azure.mgmt.servicelinker.models.DryrunParameters(Model):
        action_name: Union[str, DryrunActionName]

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


    class azure.mgmt.servicelinker.models.DryrunPatch(Model):
        operation_previews: list[DryrunOperationPreview]
        parameters: DryrunParameters
        prerequisite_results: list[DryrunPrerequisiteResult]
        provisioning_state: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameters: Optional[DryrunParameters] = ..., 
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


    class azure.mgmt.servicelinker.models.DryrunPrerequisiteResult(Model):
        type: Union[str, DryrunPrerequisiteResultType]

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


    class azure.mgmt.servicelinker.models.DryrunPrerequisiteResultType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC_ERROR = "basicError"
        PERMISSIONS_MISSING = "permissionsMissing"


    class azure.mgmt.servicelinker.models.DryrunPreviewOperationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONFIG_AUTH = "configAuth"
        CONFIG_CONNECTION = "configConnection"
        CONFIG_NETWORK = "configNetwork"


    class azure.mgmt.servicelinker.models.DryrunResource(ProxyResource):
        id: str
        name: str
        operation_previews: list[DryrunOperationPreview]
        parameters: DryrunParameters
        prerequisite_results: list[DryrunPrerequisiteResult]
        provisioning_state: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameters: Optional[DryrunParameters] = ..., 
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


    class azure.mgmt.servicelinker.models.EasyAuthMicrosoftEntraIDAuthInfo(AuthInfoBase):
        auth_mode: Union[str, AuthMode]
        auth_type: Union[str, AuthType]
        client_id: str
        delete_or_update_behavior: Union[str, DeleteOrUpdateBehavior]
        secret: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auth_mode: Optional[Union[str, AuthMode]] = ..., 
                client_id: Optional[str] = ..., 
                delete_or_update_behavior: Optional[Union[str, DeleteOrUpdateBehavior]] = ..., 
                secret: Optional[str] = ..., 
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


    class azure.mgmt.servicelinker.models.ErrorAdditionalInfo(Model):
        info: JSON
        type: str

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


    class azure.mgmt.servicelinker.models.ErrorDetail(Model):
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str

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


    class azure.mgmt.servicelinker.models.ErrorResponse(Model):
        error: ErrorDetail

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ..., 
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


    class azure.mgmt.servicelinker.models.FabricPlatform(TargetServiceBase):
        endpoint: str
        type: Union[str, TargetServiceType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                endpoint: Optional[str] = ..., 
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


    class azure.mgmt.servicelinker.models.FirewallRules(Model):
        azure_services: Union[str, AllowType]
        caller_client_ip: Union[str, AllowType]
        ip_ranges: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                azure_services: Optional[Union[str, AllowType]] = ..., 
                caller_client_ip: Optional[Union[str, AllowType]] = ..., 
                ip_ranges: Optional[List[str]] = ..., 
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


    class azure.mgmt.servicelinker.models.KeyVaultSecretReferenceSecretInfo(SecretInfoBase):
        name: str
        secret_type: Union[str, SecretType]
        version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                version: Optional[str] = ..., 
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


    class azure.mgmt.servicelinker.models.KeyVaultSecretUriSecretInfo(SecretInfoBase):
        secret_type: Union[str, SecretType]
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[str] = ..., 
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


    class azure.mgmt.servicelinker.models.LinkerConfigurationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        KEY_VAULT_SECRET = "KeyVaultSecret"


    class azure.mgmt.servicelinker.models.LinkerPatch(Model):
        auth_info: AuthInfoBase
        client_type: Union[str, ClientType]
        configuration_info: ConfigurationInfo
        provisioning_state: str
        public_network_solution: PublicNetworkSolution
        scope: str
        secret_store: SecretStore
        target_service: TargetServiceBase
        v_net_solution: VNetSolution

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auth_info: Optional[AuthInfoBase] = ..., 
                client_type: Optional[Union[str, ClientType]] = ..., 
                configuration_info: Optional[ConfigurationInfo] = ..., 
                public_network_solution: Optional[PublicNetworkSolution] = ..., 
                scope: Optional[str] = ..., 
                secret_store: Optional[SecretStore] = ..., 
                target_service: Optional[TargetServiceBase] = ..., 
                v_net_solution: Optional[VNetSolution] = ..., 
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


    class azure.mgmt.servicelinker.models.LinkerProperties(Model):
        auth_info: AuthInfoBase
        client_type: Union[str, ClientType]
        configuration_info: ConfigurationInfo
        provisioning_state: str
        public_network_solution: PublicNetworkSolution
        scope: str
        secret_store: SecretStore
        target_service: TargetServiceBase
        v_net_solution: VNetSolution

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auth_info: Optional[AuthInfoBase] = ..., 
                client_type: Optional[Union[str, ClientType]] = ..., 
                configuration_info: Optional[ConfigurationInfo] = ..., 
                public_network_solution: Optional[PublicNetworkSolution] = ..., 
                scope: Optional[str] = ..., 
                secret_store: Optional[SecretStore] = ..., 
                target_service: Optional[TargetServiceBase] = ..., 
                v_net_solution: Optional[VNetSolution] = ..., 
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


    class azure.mgmt.servicelinker.models.LinkerResource(ProxyResource):
        auth_info: AuthInfoBase
        client_type: Union[str, ClientType]
        configuration_info: ConfigurationInfo
        id: str
        name: str
        provisioning_state: str
        public_network_solution: PublicNetworkSolution
        scope: str
        secret_store: SecretStore
        system_data: SystemData
        target_service: TargetServiceBase
        type: str
        v_net_solution: VNetSolution

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auth_info: Optional[AuthInfoBase] = ..., 
                client_type: Optional[Union[str, ClientType]] = ..., 
                configuration_info: Optional[ConfigurationInfo] = ..., 
                public_network_solution: Optional[PublicNetworkSolution] = ..., 
                scope: Optional[str] = ..., 
                secret_store: Optional[SecretStore] = ..., 
                target_service: Optional[TargetServiceBase] = ..., 
                v_net_solution: Optional[VNetSolution] = ..., 
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


    class azure.mgmt.servicelinker.models.Operation(Model):
        action_type: Union[str, ActionType]
        display: OperationDisplay
        is_data_action: bool
        name: str
        origin: Union[str, Origin]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
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


    class azure.mgmt.servicelinker.models.OperationDisplay(Model):
        description: str
        operation: str
        provider: str
        resource: str

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


    class azure.mgmt.servicelinker.models.OperationListResult(Model):
        next_link: str
        value: list[Operation]

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


    class azure.mgmt.servicelinker.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.servicelinker.models.PermissionsMissingDryrunPrerequisiteResult(DryrunPrerequisiteResult):
        permissions: list[str]
        recommended_role: str
        scope: str
        type: Union[str, DryrunPrerequisiteResultType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                permissions: Optional[List[str]] = ..., 
                recommended_role: Optional[str] = ..., 
                scope: Optional[str] = ..., 
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


    class azure.mgmt.servicelinker.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str

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


    class azure.mgmt.servicelinker.models.PublicNetworkSolution(Model):
        action: Union[str, ActionType]
        delete_or_update_behavior: Union[str, DeleteOrUpdateBehavior]
        firewall_rules: FirewallRules

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                action: Optional[Union[str, ActionType]] = ..., 
                delete_or_update_behavior: Optional[Union[str, DeleteOrUpdateBehavior]] = ..., 
                firewall_rules: Optional[FirewallRules] = ..., 
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


    class azure.mgmt.servicelinker.models.Resource(Model):
        id: str
        name: str
        system_data: SystemData
        type: str

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


    class azure.mgmt.servicelinker.models.ResourceList(Model):
        next_link: str
        value: list[LinkerResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[LinkerResource]] = ..., 
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


    class azure.mgmt.servicelinker.models.SecretAuthInfo(AuthInfoBase):
        auth_mode: Union[str, AuthMode]
        auth_type: Union[str, AuthType]
        name: str
        secret_info: SecretInfoBase

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auth_mode: Optional[Union[str, AuthMode]] = ..., 
                name: Optional[str] = ..., 
                secret_info: Optional[SecretInfoBase] = ..., 
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


    class azure.mgmt.servicelinker.models.SecretInfoBase(Model):
        secret_type: Union[str, SecretType]

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


    class azure.mgmt.servicelinker.models.SecretSourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        KEY_VAULT_SECRET = "keyVaultSecret"
        RAW_VALUE = "rawValue"


    class azure.mgmt.servicelinker.models.SecretStore(Model):
        key_vault_id: str
        key_vault_secret_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key_vault_id: Optional[str] = ..., 
                key_vault_secret_name: Optional[str] = ..., 
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


    class azure.mgmt.servicelinker.models.SecretType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        KEY_VAULT_SECRET_REFERENCE = "keyVaultSecretReference"
        KEY_VAULT_SECRET_URI = "keyVaultSecretUri"
        RAW_VALUE = "rawValue"


    class azure.mgmt.servicelinker.models.SelfHostedServer(TargetServiceBase):
        endpoint: str
        type: Union[str, TargetServiceType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                endpoint: Optional[str] = ..., 
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


    class azure.mgmt.servicelinker.models.ServicePrincipalCertificateAuthInfo(AuthInfoBase):
        auth_mode: Union[str, AuthMode]
        auth_type: Union[str, AuthType]
        certificate: str
        client_id: str
        delete_or_update_behavior: Union[str, DeleteOrUpdateBehavior]
        principal_id: str
        roles: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auth_mode: Optional[Union[str, AuthMode]] = ..., 
                certificate: str, 
                client_id: str, 
                delete_or_update_behavior: Optional[Union[str, DeleteOrUpdateBehavior]] = ..., 
                principal_id: str, 
                roles: Optional[List[str]] = ..., 
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


    class azure.mgmt.servicelinker.models.ServicePrincipalSecretAuthInfo(AuthInfoBase, DatabaseAadAuthInfo):
        auth_mode: Union[str, AuthMode]
        auth_type: Union[str, AuthType]
        client_id: str
        delete_or_update_behavior: Union[str, DeleteOrUpdateBehavior]
        principal_id: str
        roles: list[str]
        secret: str
        user_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auth_mode: Optional[Union[str, AuthMode]] = ..., 
                client_id: str, 
                delete_or_update_behavior: Optional[Union[str, DeleteOrUpdateBehavior]] = ..., 
                principal_id: str, 
                roles: Optional[List[str]] = ..., 
                secret: str, 
                user_name: Optional[str] = ..., 
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


    class azure.mgmt.servicelinker.models.SourceConfiguration(Model):
        config_type: Union[str, LinkerConfigurationType]
        description: str
        key_vault_reference_identity: str
        name: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                key_vault_reference_identity: Optional[str] = ..., 
                name: Optional[str] = ..., 
                value: Optional[str] = ..., 
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


    class azure.mgmt.servicelinker.models.SystemAssignedIdentityAuthInfo(AuthInfoBase, DatabaseAadAuthInfo):
        auth_mode: Union[str, AuthMode]
        auth_type: Union[str, AuthType]
        delete_or_update_behavior: Union[str, DeleteOrUpdateBehavior]
        roles: list[str]
        user_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auth_mode: Optional[Union[str, AuthMode]] = ..., 
                delete_or_update_behavior: Optional[Union[str, DeleteOrUpdateBehavior]] = ..., 
                roles: Optional[List[str]] = ..., 
                user_name: Optional[str] = ..., 
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


    class azure.mgmt.servicelinker.models.SystemData(Model):
        created_at: datetime
        created_by: str
        created_by_type: Union[str, CreatedByType]
        last_modified_at: datetime
        last_modified_by: str
        last_modified_by_type: Union[str, CreatedByType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                created_by_type: Optional[Union[str, CreatedByType]] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_by_type: Optional[Union[str, CreatedByType]] = ..., 
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


    class azure.mgmt.servicelinker.models.TargetServiceBase(Model):
        type: Union[str, TargetServiceType]

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


    class azure.mgmt.servicelinker.models.TargetServiceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_RESOURCE = "AzureResource"
        CONFLUENT_BOOTSTRAP_SERVER = "ConfluentBootstrapServer"
        CONFLUENT_SCHEMA_REGISTRY = "ConfluentSchemaRegistry"
        FABRIC_PLATFORM = "FabricPlatform"
        SELF_HOSTED_SERVER = "SelfHostedServer"


    class azure.mgmt.servicelinker.models.UserAccountAuthInfo(AuthInfoBase, DatabaseAadAuthInfo):
        auth_mode: Union[str, AuthMode]
        auth_type: Union[str, AuthType]
        delete_or_update_behavior: Union[str, DeleteOrUpdateBehavior]
        principal_id: str
        roles: list[str]
        user_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auth_mode: Optional[Union[str, AuthMode]] = ..., 
                delete_or_update_behavior: Optional[Union[str, DeleteOrUpdateBehavior]] = ..., 
                principal_id: Optional[str] = ..., 
                roles: Optional[List[str]] = ..., 
                user_name: Optional[str] = ..., 
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


    class azure.mgmt.servicelinker.models.UserAssignedIdentityAuthInfo(AuthInfoBase, DatabaseAadAuthInfo):
        auth_mode: Union[str, AuthMode]
        auth_type: Union[str, AuthType]
        client_id: str
        delete_or_update_behavior: Union[str, DeleteOrUpdateBehavior]
        roles: list[str]
        subscription_id: str
        user_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auth_mode: Optional[Union[str, AuthMode]] = ..., 
                client_id: Optional[str] = ..., 
                delete_or_update_behavior: Optional[Union[str, DeleteOrUpdateBehavior]] = ..., 
                roles: Optional[List[str]] = ..., 
                subscription_id: Optional[str] = ..., 
                user_name: Optional[str] = ..., 
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


    class azure.mgmt.servicelinker.models.VNetSolution(Model):
        delete_or_update_behavior: Union[str, DeleteOrUpdateBehavior]
        type: Union[str, VNetSolutionType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                delete_or_update_behavior: Optional[Union[str, DeleteOrUpdateBehavior]] = ..., 
                type: Optional[Union[str, VNetSolutionType]] = ..., 
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


    class azure.mgmt.servicelinker.models.VNetSolutionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIVATE_LINK = "privateLink"
        SERVICE_ENDPOINT = "serviceEndpoint"


    class azure.mgmt.servicelinker.models.ValidateOperationResult(Model):
        auth_type: Union[str, AuthType]
        is_connection_available: bool
        linker_name: str
        report_end_time_utc: datetime
        report_start_time_utc: datetime
        resource_id: str
        source_id: str
        status: str
        target_id: str
        validation_detail: list[ValidationResultItem]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auth_type: Optional[Union[str, AuthType]] = ..., 
                is_connection_available: Optional[bool] = ..., 
                linker_name: Optional[str] = ..., 
                report_end_time_utc: Optional[datetime] = ..., 
                report_start_time_utc: Optional[datetime] = ..., 
                resource_id: Optional[str] = ..., 
                source_id: Optional[str] = ..., 
                status: Optional[str] = ..., 
                target_id: Optional[str] = ..., 
                validation_detail: Optional[List[ValidationResultItem]] = ..., 
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


    class azure.mgmt.servicelinker.models.ValidationResultItem(Model):
        description: str
        error_code: str
        error_message: str
        name: str
        result: Union[str, ValidationResultStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                error_code: Optional[str] = ..., 
                error_message: Optional[str] = ..., 
                name: Optional[str] = ..., 
                result: Optional[Union[str, ValidationResultStatus]] = ..., 
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


    class azure.mgmt.servicelinker.models.ValidationResultStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILURE = "failure"
        SUCCESS = "success"
        WARNING = "warning"


    class azure.mgmt.servicelinker.models.ValueSecretInfo(SecretInfoBase):
        secret_type: Union[str, SecretType]
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[str] = ..., 
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


namespace azure.mgmt.servicelinker.operations

    class azure.mgmt.servicelinker.operations.ConfigurationNamesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                filter: Optional[str] = None, 
                skip_token: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[ConfigurationNameItem]: ...


    class azure.mgmt.servicelinker.operations.ConnectorOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_dryrun(
                self, 
                subscription_id: str, 
                resource_group_name: str, 
                location: str, 
                dryrun_name: str, 
                parameters: DryrunResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DryrunResource]: ...

        @overload
        def begin_create_dryrun(
                self, 
                subscription_id: str, 
                resource_group_name: str, 
                location: str, 
                dryrun_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DryrunResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                subscription_id: str, 
                resource_group_name: str, 
                location: str, 
                connector_name: str, 
                parameters: LinkerResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LinkerResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                subscription_id: str, 
                resource_group_name: str, 
                location: str, 
                connector_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LinkerResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                subscription_id: str, 
                resource_group_name: str, 
                location: str, 
                connector_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                subscription_id: str, 
                resource_group_name: str, 
                location: str, 
                connector_name: str, 
                parameters: LinkerPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LinkerResource]: ...

        @overload
        def begin_update(
                self, 
                subscription_id: str, 
                resource_group_name: str, 
                location: str, 
                connector_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LinkerResource]: ...

        @overload
        def begin_update_dryrun(
                self, 
                subscription_id: str, 
                resource_group_name: str, 
                location: str, 
                dryrun_name: str, 
                parameters: DryrunPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DryrunResource]: ...

        @overload
        def begin_update_dryrun(
                self, 
                subscription_id: str, 
                resource_group_name: str, 
                location: str, 
                dryrun_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DryrunResource]: ...

        @distributed_trace
        def begin_validate(
                self, 
                subscription_id: str, 
                resource_group_name: str, 
                location: str, 
                connector_name: str, 
                **kwargs: Any
            ) -> LROPoller[ValidateOperationResult]: ...

        @distributed_trace
        def delete_dryrun(
                self, 
                subscription_id: str, 
                resource_group_name: str, 
                location: str, 
                dryrun_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def generate_configurations(
                self, 
                subscription_id: str, 
                resource_group_name: str, 
                location: str, 
                connector_name: str, 
                parameters: Optional[ConfigurationInfo] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationResult: ...

        @overload
        def generate_configurations(
                self, 
                subscription_id: str, 
                resource_group_name: str, 
                location: str, 
                connector_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationResult: ...

        @distributed_trace
        def get(
                self, 
                subscription_id: str, 
                resource_group_name: str, 
                location: str, 
                connector_name: str, 
                **kwargs: Any
            ) -> LinkerResource: ...

        @distributed_trace
        def get_dryrun(
                self, 
                subscription_id: str, 
                resource_group_name: str, 
                location: str, 
                dryrun_name: str, 
                **kwargs: Any
            ) -> DryrunResource: ...

        @distributed_trace
        def list(
                self, 
                subscription_id: str, 
                resource_group_name: str, 
                location: str, 
                **kwargs: Any
            ) -> Iterable[LinkerResource]: ...

        @distributed_trace
        def list_dryrun(
                self, 
                subscription_id: str, 
                resource_group_name: str, 
                location: str, 
                **kwargs: Any
            ) -> Iterable[DryrunResource]: ...


    class azure.mgmt.servicelinker.operations.LinkerOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_uri: str, 
                linker_name: str, 
                parameters: LinkerResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LinkerResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_uri: str, 
                linker_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LinkerResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_uri: str, 
                linker_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_uri: str, 
                linker_name: str, 
                parameters: LinkerPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LinkerResource]: ...

        @overload
        def begin_update(
                self, 
                resource_uri: str, 
                linker_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LinkerResource]: ...

        @distributed_trace
        def begin_validate(
                self, 
                resource_uri: str, 
                linker_name: str, 
                **kwargs: Any
            ) -> LROPoller[ValidateOperationResult]: ...

        @distributed_trace
        def get(
                self, 
                resource_uri: str, 
                linker_name: str, 
                **kwargs: Any
            ) -> LinkerResource: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> Iterable[LinkerResource]: ...

        @distributed_trace
        def list_configurations(
                self, 
                resource_uri: str, 
                linker_name: str, 
                **kwargs: Any
            ) -> ConfigurationResult: ...


    class azure.mgmt.servicelinker.operations.LinkersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_dryrun(
                self, 
                resource_uri: str, 
                dryrun_name: str, 
                parameters: DryrunResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DryrunResource]: ...

        @overload
        def begin_create_dryrun(
                self, 
                resource_uri: str, 
                dryrun_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DryrunResource]: ...

        @overload
        def begin_update_dryrun(
                self, 
                resource_uri: str, 
                dryrun_name: str, 
                parameters: DryrunPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DryrunResource]: ...

        @overload
        def begin_update_dryrun(
                self, 
                resource_uri: str, 
                dryrun_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DryrunResource]: ...

        @distributed_trace
        def delete_dryrun(
                self, 
                resource_uri: str, 
                dryrun_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def generate_configurations(
                self, 
                resource_uri: str, 
                linker_name: str, 
                parameters: Optional[ConfigurationInfo] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationResult: ...

        @overload
        def generate_configurations(
                self, 
                resource_uri: str, 
                linker_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationResult: ...

        @distributed_trace
        def get_dryrun(
                self, 
                resource_uri: str, 
                dryrun_name: str, 
                **kwargs: Any
            ) -> DryrunResource: ...

        @distributed_trace
        def list_dapr_configurations(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> Iterable[DaprConfigurationResource]: ...

        @distributed_trace
        def list_dryrun(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> Iterable[DryrunResource]: ...


    class azure.mgmt.servicelinker.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[Operation]: ...


```