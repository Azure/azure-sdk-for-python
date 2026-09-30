```py
namespace azure.mgmt.managedapplications

    class azure.mgmt.managedapplications.ManagedApplicationsMgmtClient(_ManagedApplicationsMgmtClientOperationsMixin): implements ContextManager 
        application_definitions: ApplicationDefinitionsOperations
        applications: ApplicationsOperations
        jit_requests: JitRequestsOperations

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

        @distributed_trace
        def list_operations(self, **kwargs: Any) -> ItemPaged[Operation]: ...

        @overload
        def portal_registry_package(
                self, 
                parameters: RegistryPackagePlan, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RegistryPackage: ...

        @overload
        def portal_registry_package(
                self, 
                parameters: RegistryPackagePlan, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RegistryPackage: ...

        @overload
        def portal_registry_package(
                self, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RegistryPackage: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.mgmt.managedapplications.aio

    class azure.mgmt.managedapplications.aio.ManagedApplicationsMgmtClient(_ManagedApplicationsMgmtClientOperationsMixin): implements AsyncContextManager 
        application_definitions: ApplicationDefinitionsOperations
        applications: ApplicationsOperations
        jit_requests: JitRequestsOperations

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

        @distributed_trace
        def list_operations(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...

        @overload
        async def portal_registry_package(
                self, 
                parameters: RegistryPackagePlan, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RegistryPackage: ...

        @overload
        async def portal_registry_package(
                self, 
                parameters: RegistryPackagePlan, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RegistryPackage: ...

        @overload
        async def portal_registry_package(
                self, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RegistryPackage: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.mgmt.managedapplications.aio.operations

    class azure.mgmt.managedapplications.aio.operations.ApplicationDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                application_definition_name: str, 
                parameters: ApplicationDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationDefinition: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                application_definition_name: str, 
                parameters: ApplicationDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationDefinition: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                application_definition_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationDefinition: ...

        @overload
        async def create_or_update_by_id(
                self, 
                resource_group_name: str, 
                application_definition_name: str, 
                parameters: ApplicationDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationDefinition: ...

        @overload
        async def create_or_update_by_id(
                self, 
                resource_group_name: str, 
                application_definition_name: str, 
                parameters: ApplicationDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationDefinition: ...

        @overload
        async def create_or_update_by_id(
                self, 
                resource_group_name: str, 
                application_definition_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationDefinition: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                application_definition_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_by_id(
                self, 
                resource_group_name: str, 
                application_definition_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                application_definition_name: str, 
                **kwargs: Any
            ) -> Optional[ApplicationDefinition]: ...

        @distributed_trace_async
        async def get_by_id(
                self, 
                resource_group_name: str, 
                application_definition_name: str, 
                **kwargs: Any
            ) -> Optional[ApplicationDefinition]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ApplicationDefinition]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[ApplicationDefinition]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                application_definition_name: str, 
                parameters: ApplicationDefinitionPatchable, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationDefinition: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                application_definition_name: str, 
                parameters: ApplicationDefinitionPatchable, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationDefinition: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                application_definition_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationDefinition: ...

        @overload
        async def update_by_id(
                self, 
                resource_group_name: str, 
                application_definition_name: str, 
                parameters: ApplicationDefinitionPatchable, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationDefinition: ...

        @overload
        async def update_by_id(
                self, 
                resource_group_name: str, 
                application_definition_name: str, 
                parameters: ApplicationDefinitionPatchable, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationDefinition: ...

        @overload
        async def update_by_id(
                self, 
                resource_group_name: str, 
                application_definition_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationDefinition: ...


    class azure.mgmt.managedapplications.aio.operations.ApplicationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                application_name: str, 
                parameters: Application, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Application]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                application_name: str, 
                parameters: Application, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Application]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                application_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Application]: ...

        @overload
        async def begin_create_or_update_by_id(
                self, 
                application_id: str, 
                parameters: Application, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Application]: ...

        @overload
        async def begin_create_or_update_by_id(
                self, 
                application_id: str, 
                parameters: Application, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Application]: ...

        @overload
        async def begin_create_or_update_by_id(
                self, 
                application_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Application]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                application_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_by_id(
                self, 
                application_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_refresh_permissions(
                self, 
                resource_group_name: str, 
                application_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                application_name: str, 
                parameters: Optional[ApplicationPatchable] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Application]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                application_name: str, 
                parameters: Optional[ApplicationPatchable] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Application]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                application_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Application]: ...

        @overload
        async def begin_update_access(
                self, 
                resource_group_name: str, 
                application_name: str, 
                parameters: UpdateAccessDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateAccessDefinition]: ...

        @overload
        async def begin_update_access(
                self, 
                resource_group_name: str, 
                application_name: str, 
                parameters: UpdateAccessDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateAccessDefinition]: ...

        @overload
        async def begin_update_access(
                self, 
                resource_group_name: str, 
                application_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateAccessDefinition]: ...

        @overload
        async def begin_update_by_id(
                self, 
                application_id: str, 
                parameters: Optional[ApplicationPatchable] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Application]: ...

        @overload
        async def begin_update_by_id(
                self, 
                application_id: str, 
                parameters: Optional[ApplicationPatchable] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Application]: ...

        @overload
        async def begin_update_by_id(
                self, 
                application_id: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Application]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                application_name: str, 
                **kwargs: Any
            ) -> Optional[Application]: ...

        @distributed_trace_async
        async def get_by_id(
                self, 
                application_id: str, 
                **kwargs: Any
            ) -> Optional[Application]: ...

        @distributed_trace_async
        async def list_allowed_upgrade_plans(
                self, 
                resource_group_name: str, 
                application_name: str, 
                **kwargs: Any
            ) -> AllowedUpgradePlansResult: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Application]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Application]: ...

        @overload
        async def list_tokens(
                self, 
                resource_group_name: str, 
                application_name: str, 
                parameters: ListTokenRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedIdentityTokenResult: ...

        @overload
        async def list_tokens(
                self, 
                resource_group_name: str, 
                application_name: str, 
                parameters: ListTokenRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedIdentityTokenResult: ...

        @overload
        async def list_tokens(
                self, 
                resource_group_name: str, 
                application_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedIdentityTokenResult: ...


    class azure.mgmt.managedapplications.aio.operations.JitRequestsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                jit_request_name: str, 
                parameters: JitRequestDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[JitRequestDefinition]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                jit_request_name: str, 
                parameters: JitRequestDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[JitRequestDefinition]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                jit_request_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[JitRequestDefinition]: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                jit_request_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                jit_request_name: str, 
                **kwargs: Any
            ) -> Optional[JitRequestDefinition]: ...

        @distributed_trace_async
        async def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> JitRequestDefinitionListResult: ...

        @distributed_trace_async
        async def list_by_subscription(self, **kwargs: Any) -> JitRequestDefinitionListResult: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                jit_request_name: str, 
                parameters: JitRequestPatchable, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JitRequestDefinition: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                jit_request_name: str, 
                parameters: JitRequestPatchable, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JitRequestDefinition: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                jit_request_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JitRequestDefinition: ...


namespace azure.mgmt.managedapplications.models

    class azure.mgmt.managedapplications.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.managedapplications.models.AllowedUpgradePlansResult(_Model):
        value: Optional[list[Plan]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[Plan]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedapplications.models.Application(GenericResource):
        id: str
        identity: Optional[Identity]
        kind: str
        location: str
        managed_by: str
        name: str
        plan: Optional[Plan]
        properties: ApplicationProperties
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[Identity] = ..., 
                kind: str, 
                location: Optional[str] = ..., 
                managed_by: Optional[str] = ..., 
                plan: Optional[Plan] = ..., 
                properties: ApplicationProperties, 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managedapplications.models.ApplicationArtifact(_Model):
        name: Union[str, ApplicationArtifactName]
        type: Union[str, ApplicationArtifactType]
        uri: str

        @overload
        def __init__(
                self, 
                *, 
                name: Union[str, ApplicationArtifactName], 
                type: Union[str, ApplicationArtifactType], 
                uri: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedapplications.models.ApplicationArtifactName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTHORIZATIONS = "Authorizations"
        CUSTOM_ROLE_DEFINITION = "CustomRoleDefinition"
        NOT_SPECIFIED = "NotSpecified"
        VIEW_DEFINITION = "ViewDefinition"


    class azure.mgmt.managedapplications.models.ApplicationArtifactType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM = "Custom"
        NOT_SPECIFIED = "NotSpecified"
        TEMPLATE = "Template"


    class azure.mgmt.managedapplications.models.ApplicationAuthorization(_Model):
        principal_id: str
        role_definition_id: str

        @overload
        def __init__(
                self, 
                *, 
                principal_id: str, 
                role_definition_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedapplications.models.ApplicationBillingDetailsDefinition(_Model):
        resource_usage_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_usage_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedapplications.models.ApplicationClientDetails(_Model):
        application_id: Optional[str]
        oid: Optional[str]
        puid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                application_id: Optional[str] = ..., 
                oid: Optional[str] = ..., 
                puid: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedapplications.models.ApplicationDefinition(GenericResource):
        id: str
        location: str
        managed_by: str
        name: str
        properties: ApplicationDefinitionProperties
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                managed_by: Optional[str] = ..., 
                properties: ApplicationDefinitionProperties, 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managedapplications.models.ApplicationDefinitionArtifact(_Model):
        name: Union[str, ApplicationDefinitionArtifactName]
        type: Union[str, ApplicationArtifactType]
        uri: str

        @overload
        def __init__(
                self, 
                *, 
                name: Union[str, ApplicationDefinitionArtifactName], 
                type: Union[str, ApplicationArtifactType], 
                uri: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedapplications.models.ApplicationDefinitionArtifactName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION_RESOURCE_TEMPLATE = "ApplicationResourceTemplate"
        CREATE_UI_DEFINITION = "CreateUiDefinition"
        MAIN_TEMPLATE_PARAMETERS = "MainTemplateParameters"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.managedapplications.models.ApplicationDefinitionPatchable(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedapplications.models.ApplicationDefinitionProperties(_Model):
        artifacts: Optional[list[ApplicationDefinitionArtifact]]
        authorizations: Optional[list[ApplicationAuthorization]]
        create_ui_definition: Optional[Any]
        deployment_policy: Optional[ApplicationDeploymentPolicy]
        description: Optional[str]
        display_name: Optional[str]
        is_enabled: Optional[bool]
        lock_level: Union[str, ApplicationLockLevel]
        locking_policy: Optional[ApplicationPackageLockingPolicyDefinition]
        main_template: Optional[Any]
        management_policy: Optional[ApplicationManagementPolicy]
        notification_policy: Optional[ApplicationNotificationPolicy]
        package_file_uri: Optional[str]
        policies: Optional[list[ApplicationPolicy]]
        storage_account_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                artifacts: Optional[list[ApplicationDefinitionArtifact]] = ..., 
                authorizations: Optional[list[ApplicationAuthorization]] = ..., 
                create_ui_definition: Optional[Any] = ..., 
                deployment_policy: Optional[ApplicationDeploymentPolicy] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                is_enabled: Optional[bool] = ..., 
                lock_level: Union[str, ApplicationLockLevel], 
                locking_policy: Optional[ApplicationPackageLockingPolicyDefinition] = ..., 
                main_template: Optional[Any] = ..., 
                management_policy: Optional[ApplicationManagementPolicy] = ..., 
                notification_policy: Optional[ApplicationNotificationPolicy] = ..., 
                package_file_uri: Optional[str] = ..., 
                policies: Optional[list[ApplicationPolicy]] = ..., 
                storage_account_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedapplications.models.ApplicationDeploymentPolicy(_Model):
        deployment_mode: Union[str, DeploymentMode]

        @overload
        def __init__(
                self, 
                *, 
                deployment_mode: Union[str, DeploymentMode]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedapplications.models.ApplicationJitAccessPolicy(_Model):
        jit_access_enabled: bool
        jit_approval_mode: Optional[Union[str, JitApprovalMode]]
        jit_approvers: Optional[list[JitApproverDefinition]]
        maximum_jit_access_duration: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                jit_access_enabled: bool, 
                jit_approval_mode: Optional[Union[str, JitApprovalMode]] = ..., 
                jit_approvers: Optional[list[JitApproverDefinition]] = ..., 
                maximum_jit_access_duration: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedapplications.models.ApplicationLockLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CAN_NOT_DELETE = "CanNotDelete"
        NONE = "None"
        READ_ONLY = "ReadOnly"


    class azure.mgmt.managedapplications.models.ApplicationManagementMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANAGED = "Managed"
        NOT_SPECIFIED = "NotSpecified"
        UNMANAGED = "Unmanaged"


    class azure.mgmt.managedapplications.models.ApplicationManagementPolicy(_Model):
        mode: Optional[Union[str, ApplicationManagementMode]]

        @overload
        def __init__(
                self, 
                *, 
                mode: Optional[Union[str, ApplicationManagementMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedapplications.models.ApplicationNotificationEndpoint(_Model):
        uri: str

        @overload
        def __init__(
                self, 
                *, 
                uri: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedapplications.models.ApplicationNotificationPolicy(_Model):
        notification_endpoints: list[ApplicationNotificationEndpoint]

        @overload
        def __init__(
                self, 
                *, 
                notification_endpoints: list[ApplicationNotificationEndpoint]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedapplications.models.ApplicationPackageContact(_Model):
        contact_name: Optional[str]
        email: str
        phone: str

        @overload
        def __init__(
                self, 
                *, 
                contact_name: Optional[str] = ..., 
                email: str, 
                phone: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedapplications.models.ApplicationPackageLockingPolicyDefinition(_Model):
        allowed_actions: Optional[list[str]]
        allowed_data_actions: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                allowed_actions: Optional[list[str]] = ..., 
                allowed_data_actions: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedapplications.models.ApplicationPackageSupportUrls(_Model):
        government_cloud: Optional[str]
        public_azure: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                government_cloud: Optional[str] = ..., 
                public_azure: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedapplications.models.ApplicationPatchable(GenericResource):
        id: str
        identity: Optional[Identity]
        kind: Optional[str]
        location: str
        managed_by: str
        name: str
        plan: Optional[PlanPatchable]
        properties: Optional[ApplicationProperties]
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[Identity] = ..., 
                kind: Optional[str] = ..., 
                location: Optional[str] = ..., 
                managed_by: Optional[str] = ..., 
                plan: Optional[PlanPatchable] = ..., 
                properties: Optional[ApplicationProperties] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managedapplications.models.ApplicationPolicy(_Model):
        name: Optional[str]
        parameters: Optional[str]
        policy_definition_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                parameters: Optional[str] = ..., 
                policy_definition_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedapplications.models.ApplicationProperties(_Model):
        application_definition_id: Optional[str]
        artifacts: Optional[list[ApplicationArtifact]]
        authorizations: Optional[list[ApplicationAuthorization]]
        billing_details: Optional[ApplicationBillingDetailsDefinition]
        created_by: Optional[ApplicationClientDetails]
        customer_support: Optional[ApplicationPackageContact]
        jit_access_policy: Optional[ApplicationJitAccessPolicy]
        managed_resource_group_id: Optional[str]
        management_mode: Optional[Union[str, ApplicationManagementMode]]
        outputs: Optional[Any]
        parameters: Optional[Any]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        publisher_tenant_id: Optional[str]
        support_urls: Optional[ApplicationPackageSupportUrls]
        updated_by: Optional[ApplicationClientDetails]

        @overload
        def __init__(
                self, 
                *, 
                application_definition_id: Optional[str] = ..., 
                jit_access_policy: Optional[ApplicationJitAccessPolicy] = ..., 
                managed_resource_group_id: Optional[str] = ..., 
                parameters: Optional[Any] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedapplications.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.managedapplications.models.DeploymentMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETE = "Complete"
        INCREMENTAL = "Incremental"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.managedapplications.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.managedapplications.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.managedapplications.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedapplications.models.GenericResource(Resource):
        id: str
        location: str
        managed_by: Optional[str]
        name: str
        sku: Optional[Sku]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                managed_by: Optional[str] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedapplications.models.Identity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Optional[Union[str, ResourceIdentityType]]
        user_assigned_identities: Optional[dict[str, UserAssignedResourceIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ResourceIdentityType]] = ..., 
                user_assigned_identities: Optional[dict[str, UserAssignedResourceIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedapplications.models.JitApprovalMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO_APPROVE = "AutoApprove"
        MANUAL_APPROVE = "ManualApprove"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.managedapplications.models.JitApproverDefinition(_Model):
        display_name: Optional[str]
        id: str
        type: Optional[Union[str, JitApproverType]]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                id: str, 
                type: Optional[Union[str, JitApproverType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedapplications.models.JitApproverType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GROUP = "group"
        USER = "user"


    class azure.mgmt.managedapplications.models.JitAuthorizationPolicies(_Model):
        principal_id: str
        role_definition_id: str

        @overload
        def __init__(
                self, 
                *, 
                principal_id: str, 
                role_definition_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedapplications.models.JitRequestDefinition(Resource):
        id: str
        location: str
        name: str
        properties: Optional[JitRequestProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[JitRequestProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managedapplications.models.JitRequestDefinitionListResult(_Model):
        next_link: Optional[str]
        value: list[JitRequestDefinition]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[JitRequestDefinition]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedapplications.models.JitRequestMetadata(_Model):
        origin_request_id: Optional[str]
        requestor_id: Optional[str]
        subject_display_name: Optional[str]
        tenant_display_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                origin_request_id: Optional[str] = ..., 
                requestor_id: Optional[str] = ..., 
                subject_display_name: Optional[str] = ..., 
                tenant_display_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedapplications.models.JitRequestPatchable(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedapplications.models.JitRequestProperties(_Model):
        application_resource_id: str
        created_by: Optional[ApplicationClientDetails]
        jit_authorization_policies: list[JitAuthorizationPolicies]
        jit_request_state: Optional[Union[str, JitRequestState]]
        jit_scheduling_policy: JitSchedulingPolicy
        provisioning_state: Optional[Union[str, ProvisioningState]]
        publisher_tenant_id: Optional[str]
        updated_by: Optional[ApplicationClientDetails]

        @overload
        def __init__(
                self, 
                *, 
                application_resource_id: str, 
                jit_authorization_policies: list[JitAuthorizationPolicies], 
                jit_scheduling_policy: JitSchedulingPolicy
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedapplications.models.JitRequestState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        CANCELED = "Canceled"
        DENIED = "Denied"
        EXPIRED = "Expired"
        FAILED = "Failed"
        NOT_SPECIFIED = "NotSpecified"
        PENDING = "Pending"
        TIMEOUT = "Timeout"


    class azure.mgmt.managedapplications.models.JitSchedulingPolicy(_Model):
        duration: timedelta
        start_time: datetime
        type: Union[str, JitSchedulingType]

        @overload
        def __init__(
                self, 
                *, 
                duration: timedelta, 
                start_time: datetime, 
                type: Union[str, JitSchedulingType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedapplications.models.JitSchedulingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_SPECIFIED = "NotSpecified"
        ONCE = "Once"
        RECURRING = "Recurring"


    class azure.mgmt.managedapplications.models.ListTokenRequest(_Model):
        authorization_audience: Optional[str]
        user_assigned_identities: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                authorization_audience: Optional[str] = ..., 
                user_assigned_identities: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedapplications.models.ManagedIdentityToken(_Model):
        access_token: Optional[str]
        authorization_audience: Optional[str]
        expires_in: Optional[str]
        expires_on: Optional[str]
        not_before: Optional[str]
        resource_id: Optional[str]
        token_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                access_token: Optional[str] = ..., 
                authorization_audience: Optional[str] = ..., 
                expires_in: Optional[str] = ..., 
                expires_on: Optional[str] = ..., 
                not_before: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
                token_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedapplications.models.ManagedIdentityTokenResult(_Model):
        value: Optional[list[ManagedIdentityToken]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[ManagedIdentityToken]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedapplications.models.Operation(_Model):
        action_type: Optional[Union[str, ActionType]]
        display: Optional[OperationDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]
        origin: Optional[Union[str, Origin]]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedapplications.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.managedapplications.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.managedapplications.models.Plan(_Model):
        name: str
        product: str
        promotion_code: Optional[str]
        publisher: str
        version: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                product: str, 
                promotion_code: Optional[str] = ..., 
                publisher: str, 
                version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedapplications.models.PlanPatchable(_Model):
        name: Optional[str]
        product: Optional[str]
        promotion_code: Optional[str]
        publisher: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                product: Optional[str] = ..., 
                promotion_code: Optional[str] = ..., 
                publisher: Optional[str] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedapplications.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        DELETED = "Deleted"
        DELETING = "Deleting"
        FAILED = "Failed"
        NOT_SPECIFIED = "NotSpecified"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.managedapplications.models.RegistryPackage(_Model):
        offer: str
        package_links: RegistryPackageLinks
        plan: str
        publisher: str
        version: str

        @overload
        def __init__(
                self, 
                *, 
                offer: str, 
                package_links: RegistryPackageLinks, 
                plan: str, 
                publisher: str, 
                version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedapplications.models.RegistryPackageLinks(_Model):
        create_ui_definition_link: Optional[str]
        deployment_template_link: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                create_ui_definition_link: Optional[str] = ..., 
                deployment_template_link: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedapplications.models.RegistryPackagePlan(_Model):
        offer: str
        plan: str
        publisher: str
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                offer: str, 
                plan: str, 
                publisher: str, 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedapplications.models.Resource(_Model):
        id: Optional[str]
        location: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        tags: Optional[dict[str, str]]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedapplications.models.ResourceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned, UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.managedapplications.models.Sku(_Model):
        capacity: Optional[int]
        family: Optional[str]
        model: Optional[str]
        name: str
        size: Optional[str]
        tier: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                family: Optional[str] = ..., 
                model: Optional[str] = ..., 
                name: str, 
                size: Optional[str] = ..., 
                tier: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedapplications.models.Status(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ELEVATE = "Elevate"
        NOT_SPECIFIED = "NotSpecified"
        REMOVE = "Remove"


    class azure.mgmt.managedapplications.models.Substatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        DENIED = "Denied"
        EXPIRED = "Expired"
        FAILED = "Failed"
        NOT_SPECIFIED = "NotSpecified"
        TIMEOUT = "Timeout"


    class azure.mgmt.managedapplications.models.SystemData(_Model):
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


    class azure.mgmt.managedapplications.models.UpdateAccessDefinition(_Model):
        approver: Optional[str]
        metadata: JitRequestMetadata
        status: Union[str, Status]
        sub_status: Union[str, Substatus]

        @overload
        def __init__(
                self, 
                *, 
                approver: Optional[str] = ..., 
                metadata: JitRequestMetadata, 
                status: Union[str, Status], 
                sub_status: Union[str, Substatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedapplications.models.UserAssignedResourceIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]


namespace azure.mgmt.managedapplications.operations

    class azure.mgmt.managedapplications.operations.ApplicationDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                application_definition_name: str, 
                parameters: ApplicationDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationDefinition: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                application_definition_name: str, 
                parameters: ApplicationDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationDefinition: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                application_definition_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationDefinition: ...

        @overload
        def create_or_update_by_id(
                self, 
                resource_group_name: str, 
                application_definition_name: str, 
                parameters: ApplicationDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationDefinition: ...

        @overload
        def create_or_update_by_id(
                self, 
                resource_group_name: str, 
                application_definition_name: str, 
                parameters: ApplicationDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationDefinition: ...

        @overload
        def create_or_update_by_id(
                self, 
                resource_group_name: str, 
                application_definition_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationDefinition: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                application_definition_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_by_id(
                self, 
                resource_group_name: str, 
                application_definition_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                application_definition_name: str, 
                **kwargs: Any
            ) -> Optional[ApplicationDefinition]: ...

        @distributed_trace
        def get_by_id(
                self, 
                resource_group_name: str, 
                application_definition_name: str, 
                **kwargs: Any
            ) -> Optional[ApplicationDefinition]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ApplicationDefinition]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[ApplicationDefinition]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                application_definition_name: str, 
                parameters: ApplicationDefinitionPatchable, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationDefinition: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                application_definition_name: str, 
                parameters: ApplicationDefinitionPatchable, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationDefinition: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                application_definition_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationDefinition: ...

        @overload
        def update_by_id(
                self, 
                resource_group_name: str, 
                application_definition_name: str, 
                parameters: ApplicationDefinitionPatchable, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationDefinition: ...

        @overload
        def update_by_id(
                self, 
                resource_group_name: str, 
                application_definition_name: str, 
                parameters: ApplicationDefinitionPatchable, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationDefinition: ...

        @overload
        def update_by_id(
                self, 
                resource_group_name: str, 
                application_definition_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationDefinition: ...


    class azure.mgmt.managedapplications.operations.ApplicationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                application_name: str, 
                parameters: Application, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Application]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                application_name: str, 
                parameters: Application, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Application]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                application_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Application]: ...

        @overload
        def begin_create_or_update_by_id(
                self, 
                application_id: str, 
                parameters: Application, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Application]: ...

        @overload
        def begin_create_or_update_by_id(
                self, 
                application_id: str, 
                parameters: Application, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Application]: ...

        @overload
        def begin_create_or_update_by_id(
                self, 
                application_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Application]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                application_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_by_id(
                self, 
                application_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_refresh_permissions(
                self, 
                resource_group_name: str, 
                application_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                application_name: str, 
                parameters: Optional[ApplicationPatchable] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Application]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                application_name: str, 
                parameters: Optional[ApplicationPatchable] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Application]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                application_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Application]: ...

        @overload
        def begin_update_access(
                self, 
                resource_group_name: str, 
                application_name: str, 
                parameters: UpdateAccessDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[UpdateAccessDefinition]: ...

        @overload
        def begin_update_access(
                self, 
                resource_group_name: str, 
                application_name: str, 
                parameters: UpdateAccessDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[UpdateAccessDefinition]: ...

        @overload
        def begin_update_access(
                self, 
                resource_group_name: str, 
                application_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[UpdateAccessDefinition]: ...

        @overload
        def begin_update_by_id(
                self, 
                application_id: str, 
                parameters: Optional[ApplicationPatchable] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Application]: ...

        @overload
        def begin_update_by_id(
                self, 
                application_id: str, 
                parameters: Optional[ApplicationPatchable] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Application]: ...

        @overload
        def begin_update_by_id(
                self, 
                application_id: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Application]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                application_name: str, 
                **kwargs: Any
            ) -> Optional[Application]: ...

        @distributed_trace
        def get_by_id(
                self, 
                application_id: str, 
                **kwargs: Any
            ) -> Optional[Application]: ...

        @distributed_trace
        def list_allowed_upgrade_plans(
                self, 
                resource_group_name: str, 
                application_name: str, 
                **kwargs: Any
            ) -> AllowedUpgradePlansResult: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Application]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Application]: ...

        @overload
        def list_tokens(
                self, 
                resource_group_name: str, 
                application_name: str, 
                parameters: ListTokenRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedIdentityTokenResult: ...

        @overload
        def list_tokens(
                self, 
                resource_group_name: str, 
                application_name: str, 
                parameters: ListTokenRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedIdentityTokenResult: ...

        @overload
        def list_tokens(
                self, 
                resource_group_name: str, 
                application_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedIdentityTokenResult: ...


    class azure.mgmt.managedapplications.operations.JitRequestsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                jit_request_name: str, 
                parameters: JitRequestDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[JitRequestDefinition]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                jit_request_name: str, 
                parameters: JitRequestDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[JitRequestDefinition]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                jit_request_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[JitRequestDefinition]: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                jit_request_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                jit_request_name: str, 
                **kwargs: Any
            ) -> Optional[JitRequestDefinition]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> JitRequestDefinitionListResult: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> JitRequestDefinitionListResult: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                jit_request_name: str, 
                parameters: JitRequestPatchable, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JitRequestDefinition: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                jit_request_name: str, 
                parameters: JitRequestPatchable, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JitRequestDefinition: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                jit_request_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JitRequestDefinition: ...


namespace azure.mgmt.managedapplications.types

    class azure.mgmt.managedapplications.types.Application(GenericResource):
        key "id": str
        key "identity": ForwardRef('Identity', module='types')
        key "kind": Required[str]
        key "location": str
        key "managedBy": str
        key "name": str
        key "plan": ForwardRef('Plan', module='types')
        key "properties": Required[ApplicationProperties]
        key "sku": ForwardRef('Sku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: Identity
        kind: str
        location: str
        managed_by: str
        name: str
        plan: Plan
        properties: ApplicationProperties
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.managedapplications.types.ApplicationArtifact(TypedDict, total=False):
        key "name": Required[Union[str, ApplicationArtifactName]]
        key "type": Required[Union[str, ApplicationArtifactType]]
        key "uri": Required[str]
        name: Union[str, ApplicationArtifactName]
        type: Union[str, ApplicationArtifactType]
        uri: str


    class azure.mgmt.managedapplications.types.ApplicationAuthorization(TypedDict, total=False):
        key "principalId": Required[str]
        key "roleDefinitionId": Required[str]
        principal_id: str
        role_definition_id: str


    class azure.mgmt.managedapplications.types.ApplicationBillingDetailsDefinition(TypedDict, total=False):
        key "resourceUsageId": str
        resource_usage_id: str


    class azure.mgmt.managedapplications.types.ApplicationClientDetails(TypedDict, total=False):
        key "applicationId": str
        key "oid": str
        key "puid": str
        application_id: str
        oid: str
        puid: str


    class azure.mgmt.managedapplications.types.ApplicationDefinition(GenericResource):
        key "id": str
        key "location": str
        key "managedBy": str
        key "name": str
        key "properties": Required[ApplicationDefinitionProperties]
        key "sku": ForwardRef('Sku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        managed_by: str
        name: str
        properties: ApplicationDefinitionProperties
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.managedapplications.types.ApplicationDefinitionArtifact(TypedDict, total=False):
        key "name": Required[Union[str, ApplicationDefinitionArtifactName]]
        key "type": Required[Union[str, ApplicationArtifactType]]
        key "uri": Required[str]
        name: Union[str, ApplicationDefinitionArtifactName]
        type: Union[str, ApplicationArtifactType]
        uri: str


    class azure.mgmt.managedapplications.types.ApplicationDefinitionPatchable(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.managedapplications.types.ApplicationDefinitionProperties(TypedDict, total=False):
        key "createUiDefinition": Any
        key "deploymentPolicy": ForwardRef('ApplicationDeploymentPolicy', module='types')
        key "description": str
        key "displayName": str
        key "isEnabled": bool
        key "lockLevel": Required[Union[str, ApplicationLockLevel]]
        key "lockingPolicy": ForwardRef('ApplicationPackageLockingPolicyDefinition', module='types')
        key "mainTemplate": Any
        key "managementPolicy": ForwardRef('ApplicationManagementPolicy', module='types')
        key "notificationPolicy": ForwardRef('ApplicationNotificationPolicy', module='types')
        key "packageFileUri": str
        key "storageAccountId": str
        artifacts: list[ApplicationDefinitionArtifact]
        authorizations: list[ApplicationAuthorization]
        create_ui_definition: Any
        deployment_policy: ApplicationDeploymentPolicy
        description: str
        display_name: str
        is_enabled: bool
        lock_level: Union[str, ApplicationLockLevel]
        locking_policy: ApplicationPackageLockingPolicyDefinition
        main_template: Any
        management_policy: ApplicationManagementPolicy
        notification_policy: ApplicationNotificationPolicy
        package_file_uri: str
        policies: list[ApplicationPolicy]
        storage_account_id: str


    class azure.mgmt.managedapplications.types.ApplicationDeploymentPolicy(TypedDict, total=False):
        key "deploymentMode": Required[Union[str, DeploymentMode]]
        deployment_mode: Union[str, DeploymentMode]


    class azure.mgmt.managedapplications.types.ApplicationJitAccessPolicy(TypedDict, total=False):
        key "jitAccessEnabled": Required[bool]
        key "jitApprovalMode": Union[str, JitApprovalMode]
        key "maximumJitAccessDuration": str
        jitApprovers: list[JitApproverDefinition]
        jit_access_enabled: bool
        jit_approval_mode: Union[str, JitApprovalMode]
        jit_approvers: list[JitApproverDefinition]
        maximum_jit_access_duration: str


    class azure.mgmt.managedapplications.types.ApplicationManagementPolicy(TypedDict, total=False):
        key "mode": Union[str, ApplicationManagementMode]
        mode: Union[str, ApplicationManagementMode]


    class azure.mgmt.managedapplications.types.ApplicationNotificationEndpoint(TypedDict, total=False):
        key "uri": Required[str]
        uri: str


    class azure.mgmt.managedapplications.types.ApplicationNotificationPolicy(TypedDict, total=False):
        key "notificationEndpoints": Required[list[ApplicationNotificationEndpoint]]
        notification_endpoints: list[ApplicationNotificationEndpoint]


    class azure.mgmt.managedapplications.types.ApplicationPackageContact(TypedDict, total=False):
        key "contactName": str
        key "email": Required[str]
        key "phone": Required[str]
        contact_name: str
        email: str
        phone: str


    class azure.mgmt.managedapplications.types.ApplicationPackageLockingPolicyDefinition(TypedDict, total=False):
        allowedActions: list[str]
        allowedDataActions: list[str]
        allowed_actions: list[str]
        allowed_data_actions: list[str]


    class azure.mgmt.managedapplications.types.ApplicationPackageSupportUrls(TypedDict, total=False):
        key "governmentCloud": str
        key "publicAzure": str
        government_cloud: str
        public_azure: str


    class azure.mgmt.managedapplications.types.ApplicationPatchable(GenericResource):
        key "id": str
        key "identity": ForwardRef('Identity', module='types')
        key "kind": str
        key "location": str
        key "managedBy": str
        key "name": str
        key "plan": ForwardRef('PlanPatchable', module='types')
        key "properties": ForwardRef('ApplicationProperties', module='types')
        key "sku": ForwardRef('Sku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: Identity
        kind: str
        location: str
        managed_by: str
        name: str
        plan: PlanPatchable
        properties: ApplicationProperties
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.managedapplications.types.ApplicationPolicy(TypedDict, total=False):
        key "name": str
        key "parameters": str
        key "policyDefinitionId": str
        name: str
        parameters: str
        policy_definition_id: str


    class azure.mgmt.managedapplications.types.ApplicationProperties(TypedDict, total=False):
        key "applicationDefinitionId": str
        key "billingDetails": ForwardRef('ApplicationBillingDetailsDefinition', module='types')
        key "createdBy": ForwardRef('ApplicationClientDetails', module='types')
        key "customerSupport": ForwardRef('ApplicationPackageContact', module='types')
        key "jitAccessPolicy": ForwardRef('ApplicationJitAccessPolicy', module='types')
        key "managedResourceGroupId": str
        key "managementMode": Union[str, ApplicationManagementMode]
        key "outputs": Any
        key "parameters": Any
        key "provisioningState": Union[str, ProvisioningState]
        key "publisherTenantId": str
        key "supportUrls": ForwardRef('ApplicationPackageSupportUrls', module='types')
        key "updatedBy": ForwardRef('ApplicationClientDetails', module='types')
        application_definition_id: str
        artifacts: list[ApplicationArtifact]
        authorizations: list[ApplicationAuthorization]
        billing_details: ApplicationBillingDetailsDefinition
        created_by: ApplicationClientDetails
        customer_support: ApplicationPackageContact
        jit_access_policy: ApplicationJitAccessPolicy
        managed_resource_group_id: str
        management_mode: Union[str, ApplicationManagementMode]
        outputs: Any
        parameters: Any
        provisioning_state: Union[str, ProvisioningState]
        publisher_tenant_id: str
        support_urls: ApplicationPackageSupportUrls
        updated_by: ApplicationClientDetails


    class azure.mgmt.managedapplications.types.GenericResource(Resource):
        key "id": str
        key "location": str
        key "managedBy": str
        key "name": str
        key "sku": ForwardRef('Sku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        managed_by: str
        name: str
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.managedapplications.types.Identity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Union[str, ResourceIdentityType]
        principal_id: str
        tenant_id: str
        type: Union[str, ResourceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedResourceIdentity]
        user_assigned_identities: dict[str, UserAssignedResourceIdentity]


    class azure.mgmt.managedapplications.types.JitApproverDefinition(TypedDict, total=False):
        key "displayName": str
        key "id": Required[str]
        key "type": Union[str, JitApproverType]
        display_name: str
        id: str
        type: Union[str, JitApproverType]


    class azure.mgmt.managedapplications.types.JitAuthorizationPolicies(TypedDict, total=False):
        key "principalId": Required[str]
        key "roleDefinitionId": Required[str]
        principal_id: str
        role_definition_id: str


    class azure.mgmt.managedapplications.types.JitRequestDefinition(Resource):
        key "id": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('JitRequestProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: JitRequestProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.managedapplications.types.JitRequestMetadata(TypedDict, total=False):
        key "originRequestId": str
        key "requestorId": str
        key "subjectDisplayName": str
        key "tenantDisplayName": str
        origin_request_id: str
        requestor_id: str
        subject_display_name: str
        tenant_display_name: str


    class azure.mgmt.managedapplications.types.JitRequestPatchable(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.managedapplications.types.JitRequestProperties(TypedDict, total=False):
        key "applicationResourceId": Required[str]
        key "createdBy": ForwardRef('ApplicationClientDetails', module='types')
        key "jitAuthorizationPolicies": Required[list[JitAuthorizationPolicies]]
        key "jitRequestState": Union[str, JitRequestState]
        key "jitSchedulingPolicy": Required[JitSchedulingPolicy]
        key "provisioningState": Union[str, ProvisioningState]
        key "publisherTenantId": str
        key "updatedBy": ForwardRef('ApplicationClientDetails', module='types')
        application_resource_id: str
        created_by: ApplicationClientDetails
        jit_authorization_policies: list[JitAuthorizationPolicies]
        jit_request_state: Union[str, JitRequestState]
        jit_scheduling_policy: JitSchedulingPolicy
        provisioning_state: Union[str, ProvisioningState]
        publisher_tenant_id: str
        updated_by: ApplicationClientDetails


    class azure.mgmt.managedapplications.types.JitSchedulingPolicy(TypedDict, total=False):
        key "duration": Required[str]
        key "startTime": Required[str]
        key "type": Required[Union[str, JitSchedulingType]]
        duration: str
        start_time: str
        type: Union[str, JitSchedulingType]


    class azure.mgmt.managedapplications.types.ListTokenRequest(TypedDict, total=False):
        key "authorizationAudience": str
        authorization_audience: str
        userAssignedIdentities: list[str]
        user_assigned_identities: list[str]


    class azure.mgmt.managedapplications.types.Plan(TypedDict, total=False):
        key "name": Required[str]
        key "product": Required[str]
        key "promotionCode": str
        key "publisher": Required[str]
        key "version": Required[str]
        name: str
        product: str
        promotion_code: str
        publisher: str
        version: str


    class azure.mgmt.managedapplications.types.PlanPatchable(TypedDict, total=False):
        key "name": str
        key "product": str
        key "promotionCode": str
        key "publisher": str
        key "version": str
        name: str
        product: str
        promotion_code: str
        publisher: str
        version: str


    class azure.mgmt.managedapplications.types.RegistryPackagePlan(TypedDict, total=False):
        key "offer": Required[str]
        key "plan": Required[str]
        key "publisher": Required[str]
        key "version": str
        offer: str
        plan: str
        publisher: str
        version: str


    class azure.mgmt.managedapplications.types.Resource(TypedDict, total=False):
        key "id": str
        key "location": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.managedapplications.types.Sku(TypedDict, total=False):
        key "capacity": int
        key "family": str
        key "model": str
        key "name": Required[str]
        key "size": str
        key "tier": str
        capacity: int
        family: str
        model: str
        name: str
        size: str
        tier: str


    class azure.mgmt.managedapplications.types.SystemData(TypedDict, total=False):
        key "createdAt": str
        key "createdBy": str
        key "createdByType": Union[str, CreatedByType]
        key "lastModifiedAt": str
        key "lastModifiedBy": str
        key "lastModifiedByType": Union[str, CreatedByType]
        created_at: str
        created_by: str
        created_by_type: Union[str, CreatedByType]
        last_modified_at: str
        last_modified_by: str
        last_modified_by_type: Union[str, CreatedByType]


    class azure.mgmt.managedapplications.types.UpdateAccessDefinition(TypedDict, total=False):
        key "Approver": str
        key "Metadata": Required[JitRequestMetadata]
        key "Status": Required[Union[str, Status]]
        key "SubStatus": Required[Union[str, Substatus]]
        approver: str
        metadata: JitRequestMetadata
        status: Union[str, Status]
        sub_status: Union[str, Substatus]


    class azure.mgmt.managedapplications.types.UserAssignedResourceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        principal_id: str
        tenant_id: str


```