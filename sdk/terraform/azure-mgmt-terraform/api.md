```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.terraform

    class azure.mgmt.terraform.TerraformMgmtClient: implements ContextManager 
        operations: Operations
        terraform: TerraformOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
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
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
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
        def list(self, **kwargs: Any) -> AsyncIterable[Operation]: ...


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
                body: JSON, 
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


    class azure.mgmt.terraform.models.BaseExportModel(Model):
        full_properties: Optional[bool]
        mask_sensitive: Optional[bool]
        target_provider: Optional[Union[str, TargetProvider]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                full_properties: Optional[bool] = ..., 
                mask_sensitive: Optional[bool] = ..., 
                target_provider: Optional[Union[str, TargetProvider]] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.terraform.models.ErrorAdditionalInfo(Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.terraform.models.ErrorDetail(Model):
        additional_info: Optional[List[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[List[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.terraform.models.ErrorResponse(Model):
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
        full_properties: bool
        mask_sensitive: bool
        name_pattern: Optional[str]
        query: str
        recursive: Optional[bool]
        target_provider: Union[str, TargetProvider]
        type: Literal[Type.EXPORT_QUERY]

        @overload
        def __init__(
                self, 
                *, 
                full_properties: Optional[bool] = ..., 
                mask_sensitive: Optional[bool] = ..., 
                name_pattern: Optional[str] = ..., 
                query: str, 
                recursive: Optional[bool] = ..., 
                target_provider: Optional[Union[str, TargetProvider]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.terraform.models.ExportResource(BaseExportModel, discriminator='ExportResource'):
        full_properties: bool
        mask_sensitive: bool
        name_pattern: Optional[str]
        resource_ids: List[str]
        resource_name: Optional[str]
        resource_type: Optional[str]
        target_provider: Union[str, TargetProvider]
        type: Literal[Type.EXPORT_RESOURCE]

        @overload
        def __init__(
                self, 
                *, 
                full_properties: Optional[bool] = ..., 
                mask_sensitive: Optional[bool] = ..., 
                name_pattern: Optional[str] = ..., 
                resource_ids: List[str], 
                resource_name: Optional[str] = ..., 
                resource_type: Optional[str] = ..., 
                target_provider: Optional[Union[str, TargetProvider]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.terraform.models.ExportResourceGroup(BaseExportModel, discriminator='ExportResourceGroup'):
        full_properties: bool
        mask_sensitive: bool
        name_pattern: Optional[str]
        resource_group_name: str
        target_provider: Union[str, TargetProvider]
        type: Literal[Type.EXPORT_RESOURCE_GROUP]

        @overload
        def __init__(
                self, 
                *, 
                full_properties: Optional[bool] = ..., 
                mask_sensitive: Optional[bool] = ..., 
                name_pattern: Optional[str] = ..., 
                resource_group_name: str, 
                target_provider: Optional[Union[str, TargetProvider]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.terraform.models.ExportResult(Model):
        configuration: Optional[str]
        errors: Optional[List[ErrorDetail]]
        skipped_resources: Optional[List[str]]

        @overload
        def __init__(
                self, 
                *, 
                configuration: Optional[str] = ..., 
                errors: Optional[List[ErrorDetail]] = ..., 
                skipped_resources: Optional[List[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.terraform.models.Operation(Model):
        action_type: Optional[Union[str, ActionType]]
        display: Optional[OperationDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]
        origin: Optional[Union[str, Origin]]

        @overload
        def __init__(
                self, 
                *, 
                action_type: Optional[Union[str, ActionType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.terraform.models.OperationDisplay(Model):
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


    class azure.mgmt.terraform.models.TerraformOperationStatus(Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        name: Optional[str]
        percent_complete: Optional[float]
        properties: Optional[ExportResult]
        start_time: Optional[datetime]
        status: Union[str, ResourceProvisioningState]

        @overload
        def __init__(
                self, 
                *, 
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
            ): ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[Operation]: ...


    class azure.mgmt.terraform.operations.TerraformOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
                body: JSON, 
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


```