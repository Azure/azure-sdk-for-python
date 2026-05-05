```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.healthbot

    class azure.mgmt.healthbot.HealthBotMgmtClient: implements ContextManager 
        bots: BotsOperations
        operations: Operations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.mgmt.healthbot.aio

    class azure.mgmt.healthbot.aio.HealthBotMgmtClient: implements AsyncContextManager 
        bots: BotsOperations
        operations: Operations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.mgmt.healthbot.aio.operations

    class azure.mgmt.healthbot.aio.operations.BotsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                bot_name: str, 
                parameters: HealthBot, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HealthBot]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                bot_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HealthBot]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                bot_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HealthBot]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                bot_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                bot_name: str, 
                parameters: HealthBotUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HealthBot]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                bot_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HealthBot]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                bot_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HealthBot]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                bot_name: str, 
                **kwargs: Any
            ) -> HealthBot: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[HealthBot]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[HealthBot]: ...

        @distributed_trace_async
        async def list_secrets(
                self, 
                resource_group_name: str, 
                bot_name: str, 
                **kwargs: Any
            ) -> HealthBotKeysResponse: ...

        @distributed_trace_async
        async def regenerate_api_jwt_secret(
                self, 
                resource_group_name: str, 
                bot_name: str, 
                **kwargs: Any
            ) -> HealthBotKey: ...


    class azure.mgmt.healthbot.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[OperationDetail]: ...


namespace azure.mgmt.healthbot.models

    class azure.mgmt.healthbot.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.healthbot.models.Error(_Model):
        error: Optional[ErrorError]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorError] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.healthbot.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.healthbot.models.ErrorError(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[Error]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.healthbot.models.HealthBot(TrackedResource):
        id: str
        identity: Optional[Identity]
        location: str
        name: str
        properties: Optional[HealthBotProperties]
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[Identity] = ..., 
                location: str, 
                properties: Optional[HealthBotProperties] = ..., 
                sku: Sku, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.healthbot.models.HealthBotKey(_Model):
        key_name: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key_name: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.healthbot.models.HealthBotKeysResponse(_Model):
        secrets: Optional[list[HealthBotKey]]

        @overload
        def __init__(
                self, 
                *, 
                secrets: Optional[list[HealthBotKey]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.healthbot.models.HealthBotProperties(_Model):
        access_control_method: Optional[str]
        bot_management_portal_link: Optional[str]
        key_vault_properties: Optional[KeyVaultProperties]
        provisioning_state: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key_vault_properties: Optional[KeyVaultProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.healthbot.models.HealthBotUpdateParameters(_Model):
        identity: Optional[Identity]
        location: Optional[str]
        properties: Optional[HealthBotProperties]
        sku: Optional[Sku]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[Identity] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[HealthBotProperties] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.healthbot.models.Identity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Optional[Union[str, ResourceIdentityType]]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ResourceIdentityType]] = ..., 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.healthbot.models.KeyVaultProperties(_Model):
        key_name: str
        key_vault_uri: str
        key_version: Optional[str]
        user_identity: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key_name: str, 
                key_vault_uri: str, 
                key_version: Optional[str] = ..., 
                user_identity: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.healthbot.models.OperationDetail(_Model):
        display: Optional[OperationDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]
        origin: Optional[str]
        properties: Optional[Any]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                is_data_action: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ..., 
                properties: Optional[Any] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.healthbot.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.healthbot.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.healthbot.models.ResourceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned, UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.healthbot.models.Sku(_Model):
        name: Union[str, SkuName]

        @overload
        def __init__(
                self, 
                *, 
                name: Union[str, SkuName]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.healthbot.models.SkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        C0 = "C0"
        C1 = "C1"
        F0 = "F0"
        PES = "PES"


    class azure.mgmt.healthbot.models.SystemData(_Model):
        created_at: Optional[datetime]
        created_by: Optional[str]
        created_by_type: Optional[Union[str, CreatedByType]]
        last_modified_at: Optional[datetime]
        last_modified_by: Optional[str]
        last_modified_by_type: Optional[Union[str, CreatedByType]]

        @overload
        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                created_by_type: Optional[Union[str, CreatedByType]] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_by_type: Optional[Union[str, CreatedByType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.healthbot.models.TrackedResource(Resource):
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.healthbot.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


namespace azure.mgmt.healthbot.operations

    class azure.mgmt.healthbot.operations.BotsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                bot_name: str, 
                parameters: HealthBot, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HealthBot]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                bot_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HealthBot]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                bot_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HealthBot]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                bot_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                bot_name: str, 
                parameters: HealthBotUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HealthBot]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                bot_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HealthBot]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                bot_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HealthBot]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                bot_name: str, 
                **kwargs: Any
            ) -> HealthBot: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[HealthBot]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[HealthBot]: ...

        @distributed_trace
        def list_secrets(
                self, 
                resource_group_name: str, 
                bot_name: str, 
                **kwargs: Any
            ) -> HealthBotKeysResponse: ...

        @distributed_trace
        def regenerate_api_jwt_secret(
                self, 
                resource_group_name: str, 
                bot_name: str, 
                **kwargs: Any
            ) -> HealthBotKey: ...


    class azure.mgmt.healthbot.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[OperationDetail]: ...


```