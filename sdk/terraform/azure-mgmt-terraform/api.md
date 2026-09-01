```py
namespace azure.mgmt.terraform

    class azure.mgmt.terraform.TerraformMgmtClient: implements ContextManager 
        operations: Operations
        terraform: TerraformOperations

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


namespace azure.mgmt.terraform.aio

    class azure.mgmt.terraform.aio.TerraformMgmtClient: implements AsyncContextManager 
        operations: Operations
        terraform: TerraformOperations

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


namespace azure.mgmt.terraform.aio.operations

    class azure.mgmt.terraform.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.terraform.aio.operations.TerraformOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_export_terraform(
                self, 
                body: BaseExportModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TerraformOperationStatus]: ...

        @overload
        async def begin_export_terraform(
                self, 
                body: BaseExportModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TerraformOperationStatus]: ...

        @overload
        async def begin_export_terraform(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TerraformOperationStatus]: ...


namespace azure.mgmt.terraform.models

    class azure.mgmt.terraform.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.terraform.models.AuthorizationScopeFilter(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AT_SCOPE_ABOVE_AND_BELOW = "AtScopeAboveAndBelow"
        AT_SCOPE_AND_ABOVE = "AtScopeAndAbove"
        AT_SCOPE_AND_BELOW = "AtScopeAndBelow"
        AT_SCOPE_EXACT = "AtScopeExact"


    class azure.mgmt.terraform.models.AzureExtensionResourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DIAGNOSTIC_SETTINGS = "diagnostic-settings"
        LOCKS = "locks"
        ROLE_ASSIGNMENTS = "role-assignments"


    class azure.mgmt.terraform.models.BaseExportModel(_Model):
        exclude_azure_resource: Optional[list[str]]
        exclude_terraform_resource: Optional[list[str]]
        full_properties: Optional[bool]
        include_extensions: Optional[list[Union[str, AzureExtensionResourceType]]]
        include_managed_resource: Optional[bool]
        include_role_assignment: Optional[bool]
        mask_sensitive: Optional[bool]
        target_provider: Optional[Union[str, TargetProvider]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                exclude_azure_resource: Optional[list[str]] = ..., 
                exclude_terraform_resource: Optional[list[str]] = ..., 
                full_properties: Optional[bool] = ..., 
                include_extensions: Optional[list[Union[str, AzureExtensionResourceType]]] = ..., 
                include_managed_resource: Optional[bool] = ..., 
                include_role_assignment: Optional[bool] = ..., 
                mask_sensitive: Optional[bool] = ..., 
                target_provider: Optional[Union[str, TargetProvider]] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.terraform.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.terraform.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.terraform.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.terraform.models.ExportQuery(BaseExportModel, discriminator='ExportQuery'):
        authorization_scope_filter: Optional[Union[str, AuthorizationScopeFilter]]
        exclude_azure_resource: list[str]
        exclude_terraform_resource: list[str]
        full_properties: bool
        include_extensions: Union[list[str, AzureExtensionResourceType]]
        include_managed_resource: bool
        include_resource_group: Optional[bool]
        include_role_assignment: bool
        mask_sensitive: bool
        name_pattern: Optional[str]
        query: str
        recursive: Optional[bool]
        table: Optional[str]
        target_provider: Union[str, TargetProvider]
        type: Literal[Type.EXPORT_QUERY]

        @overload
        def __init__(
                self, 
                *, 
                authorization_scope_filter: Optional[Union[str, AuthorizationScopeFilter]] = ..., 
                exclude_azure_resource: Optional[list[str]] = ..., 
                exclude_terraform_resource: Optional[list[str]] = ..., 
                full_properties: Optional[bool] = ..., 
                include_extensions: Optional[list[Union[str, AzureExtensionResourceType]]] = ..., 
                include_managed_resource: Optional[bool] = ..., 
                include_resource_group: Optional[bool] = ..., 
                include_role_assignment: Optional[bool] = ..., 
                mask_sensitive: Optional[bool] = ..., 
                name_pattern: Optional[str] = ..., 
                query: str, 
                recursive: Optional[bool] = ..., 
                table: Optional[str] = ..., 
                target_provider: Optional[Union[str, TargetProvider]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.terraform.models.ExportResource(BaseExportModel, discriminator='ExportResource'):
        exclude_azure_resource: list[str]
        exclude_terraform_resource: list[str]
        full_properties: bool
        include_extensions: Union[list[str, AzureExtensionResourceType]]
        include_managed_resource: bool
        include_resource_group: Optional[bool]
        include_role_assignment: bool
        mask_sensitive: bool
        name_pattern: Optional[str]
        recursive: Optional[bool]
        resource_ids: list[str]
        resource_name: Optional[str]
        resource_type: Optional[str]
        target_provider: Union[str, TargetProvider]
        type: Literal[Type.EXPORT_RESOURCE]

        @overload
        def __init__(
                self, 
                *, 
                exclude_azure_resource: Optional[list[str]] = ..., 
                exclude_terraform_resource: Optional[list[str]] = ..., 
                full_properties: Optional[bool] = ..., 
                include_extensions: Optional[list[Union[str, AzureExtensionResourceType]]] = ..., 
                include_managed_resource: Optional[bool] = ..., 
                include_resource_group: Optional[bool] = ..., 
                include_role_assignment: Optional[bool] = ..., 
                mask_sensitive: Optional[bool] = ..., 
                name_pattern: Optional[str] = ..., 
                recursive: Optional[bool] = ..., 
                resource_ids: list[str], 
                resource_name: Optional[str] = ..., 
                resource_type: Optional[str] = ..., 
                target_provider: Optional[Union[str, TargetProvider]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.terraform.models.ExportResourceGroup(BaseExportModel, discriminator='ExportResourceGroup'):
        exclude_azure_resource: list[str]
        exclude_terraform_resource: list[str]
        full_properties: bool
        include_extensions: Union[list[str, AzureExtensionResourceType]]
        include_managed_resource: bool
        include_role_assignment: bool
        mask_sensitive: bool
        name_pattern: Optional[str]
        resource_group_name: str
        target_provider: Union[str, TargetProvider]
        type: Literal[Type.EXPORT_RESOURCE_GROUP]

        @overload
        def __init__(
                self, 
                *, 
                exclude_azure_resource: Optional[list[str]] = ..., 
                exclude_terraform_resource: Optional[list[str]] = ..., 
                full_properties: Optional[bool] = ..., 
                include_extensions: Optional[list[Union[str, AzureExtensionResourceType]]] = ..., 
                include_managed_resource: Optional[bool] = ..., 
                include_role_assignment: Optional[bool] = ..., 
                mask_sensitive: Optional[bool] = ..., 
                name_pattern: Optional[str] = ..., 
                resource_group_name: str, 
                target_provider: Optional[Union[str, TargetProvider]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.terraform.models.ExportResult(_Model):
        configuration: Optional[str]
        errors: Optional[list[ErrorDetail]]
        import_property: Optional[str]
        skipped_resources: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                configuration: Optional[str] = ..., 
                errors: Optional[list[ErrorDetail]] = ..., 
                import_property: Optional[str] = ..., 
                skipped_resources: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.terraform.models.Operation(_Model):
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


    class azure.mgmt.terraform.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.terraform.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.terraform.models.ResourceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.terraform.models.TargetProvider(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZAPI = "azapi"
        AZURERM = "azurerm"


    class azure.mgmt.terraform.models.TerraformOperationStatus(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: str
        name: Optional[str]
        percent_complete: Optional[float]
        properties: Optional[ExportResult]
        start_time: Optional[datetime]
        status: Union[str, ResourceProvisioningState]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                status: Union[str, ResourceProvisioningState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.terraform.models.Type(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXPORT_QUERY = "ExportQuery"
        EXPORT_RESOURCE = "ExportResource"
        EXPORT_RESOURCE_GROUP = "ExportResourceGroup"


namespace azure.mgmt.terraform.operations

    class azure.mgmt.terraform.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.terraform.operations.TerraformOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_export_terraform(
                self, 
                body: BaseExportModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TerraformOperationStatus]: ...

        @overload
        def begin_export_terraform(
                self, 
                body: BaseExportModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TerraformOperationStatus]: ...

        @overload
        def begin_export_terraform(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TerraformOperationStatus]: ...


namespace azure.mgmt.terraform.types

    class azure.mgmt.terraform.types.ExportQuery(TypedDict, total=False):
        key "authorizationScopeFilter": Union[str, AuthorizationScopeFilter]
        key "fullProperties": bool
        key "includeManagedResource": bool
        key "includeResourceGroup": bool
        key "includeRoleAssignment": bool
        key "maskSensitive": bool
        key "namePattern": str
        key "query": Required[str]
        key "recursive": bool
        key "table": str
        key "targetProvider": Union[str, TargetProvider]
        key "type": Required[Literal[Type.EXPORT_QUERY]]
        authorizationScopeFilter: Union[str, AuthorizationScopeFilter]
        excludeAzureResource: list[str]
        excludeTerraformResource: list[str]
        fullProperties: bool
        includeExtensions: list[Union[str, AzureExtensionResourceType]]
        includeManagedResource: bool
        includeResourceGroup: bool
        includeRoleAssignment: bool
        maskSensitive: bool
        namePattern: str
        query: str
        recursive: bool
        table: str
        targetProvider: Union[str, TargetProvider]
        type: Literal[Type.EXPORT_QUERY]


    class azure.mgmt.terraform.types.ExportResource(TypedDict, total=False):
        key "fullProperties": bool
        key "includeManagedResource": bool
        key "includeResourceGroup": bool
        key "includeRoleAssignment": bool
        key "maskSensitive": bool
        key "namePattern": str
        key "recursive": bool
        key "resourceIds": Required[list[str]]
        key "resourceName": str
        key "resourceType": str
        key "targetProvider": Union[str, TargetProvider]
        key "type": Required[Literal[Type.EXPORT_RESOURCE]]
        excludeAzureResource: list[str]
        excludeTerraformResource: list[str]
        fullProperties: bool
        includeExtensions: list[Union[str, AzureExtensionResourceType]]
        includeManagedResource: bool
        includeResourceGroup: bool
        includeRoleAssignment: bool
        maskSensitive: bool
        namePattern: str
        recursive: bool
        resourceIds: list[str]
        resourceName: str
        resourceType: str
        targetProvider: Union[str, TargetProvider]
        type: Literal[Type.EXPORT_RESOURCE]


    class azure.mgmt.terraform.types.ExportResourceGroup(TypedDict, total=False):
        key "fullProperties": bool
        key "includeManagedResource": bool
        key "includeRoleAssignment": bool
        key "maskSensitive": bool
        key "namePattern": str
        key "resourceGroupName": Required[str]
        key "targetProvider": Union[str, TargetProvider]
        key "type": Required[Literal[Type.EXPORT_RESOURCE_GROUP]]
        excludeAzureResource: list[str]
        excludeTerraformResource: list[str]
        fullProperties: bool
        includeExtensions: list[Union[str, AzureExtensionResourceType]]
        includeManagedResource: bool
        includeRoleAssignment: bool
        maskSensitive: bool
        namePattern: str
        resourceGroupName: str
        targetProvider: Union[str, TargetProvider]
        type: Literal[Type.EXPORT_RESOURCE_GROUP]


    class azure.mgmt.terraform.types.Type(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXPORT_QUERY = "ExportQuery"
        EXPORT_RESOURCE = "ExportResource"
        EXPORT_RESOURCE_GROUP = "ExportResourceGroup"


```