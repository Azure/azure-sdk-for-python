```py
namespace azure.mgmt.resource.deployments

    class azure.mgmt.resource.deployments.DeploymentsMgmtClient: implements ContextManager 
        deployment_operations: DeploymentOperationsOperations
        deployments: DeploymentsOperations

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


namespace azure.mgmt.resource.deployments.aio

    class azure.mgmt.resource.deployments.aio.DeploymentsMgmtClient: implements AsyncContextManager 
        deployment_operations: DeploymentOperationsOperations
        deployments: DeploymentsOperations

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


namespace azure.mgmt.resource.deployments.aio.operations

    class azure.mgmt.resource.deployments.aio.operations.DeploymentOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> DeploymentOperation: ...

        @distributed_trace_async
        async def get_at_management_group_scope(
                self, 
                group_id: str, 
                deployment_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> DeploymentOperation: ...

        @distributed_trace_async
        async def get_at_scope(
                self, 
                scope: str, 
                deployment_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> DeploymentOperation: ...

        @distributed_trace_async
        async def get_at_subscription_scope(
                self, 
                deployment_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> DeploymentOperation: ...

        @distributed_trace_async
        async def get_at_tenant_scope(
                self, 
                deployment_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> DeploymentOperation: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DeploymentOperation]: ...

        @distributed_trace
        def list_at_management_group_scope(
                self, 
                group_id: str, 
                deployment_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DeploymentOperation]: ...

        @distributed_trace
        def list_at_scope(
                self, 
                scope: str, 
                deployment_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DeploymentOperation]: ...

        @distributed_trace
        def list_at_subscription_scope(
                self, 
                deployment_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DeploymentOperation]: ...

        @distributed_trace
        def list_at_tenant_scope(
                self, 
                deployment_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DeploymentOperation]: ...


    class azure.mgmt.resource.deployments.aio.operations.DeploymentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                parameters: Deployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentExtended]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                parameters: Deployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentExtended]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentExtended]: ...

        @overload
        async def begin_create_or_update_at_management_group_scope(
                self, 
                group_id: str, 
                deployment_name: str, 
                parameters: ScopedDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentExtended]: ...

        @overload
        async def begin_create_or_update_at_management_group_scope(
                self, 
                group_id: str, 
                deployment_name: str, 
                parameters: ScopedDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentExtended]: ...

        @overload
        async def begin_create_or_update_at_management_group_scope(
                self, 
                group_id: str, 
                deployment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentExtended]: ...

        @overload
        async def begin_create_or_update_at_scope(
                self, 
                scope: str, 
                deployment_name: str, 
                parameters: Deployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentExtended]: ...

        @overload
        async def begin_create_or_update_at_scope(
                self, 
                scope: str, 
                deployment_name: str, 
                parameters: Deployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentExtended]: ...

        @overload
        async def begin_create_or_update_at_scope(
                self, 
                scope: str, 
                deployment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentExtended]: ...

        @overload
        async def begin_create_or_update_at_subscription_scope(
                self, 
                deployment_name: str, 
                parameters: Deployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentExtended]: ...

        @overload
        async def begin_create_or_update_at_subscription_scope(
                self, 
                deployment_name: str, 
                parameters: Deployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentExtended]: ...

        @overload
        async def begin_create_or_update_at_subscription_scope(
                self, 
                deployment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentExtended]: ...

        @overload
        async def begin_create_or_update_at_tenant_scope(
                self, 
                deployment_name: str, 
                parameters: ScopedDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentExtended]: ...

        @overload
        async def begin_create_or_update_at_tenant_scope(
                self, 
                deployment_name: str, 
                parameters: ScopedDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentExtended]: ...

        @overload
        async def begin_create_or_update_at_tenant_scope(
                self, 
                deployment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentExtended]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_at_management_group_scope(
                self, 
                group_id: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_at_scope(
                self, 
                scope: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_at_subscription_scope(
                self, 
                deployment_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_at_tenant_scope(
                self, 
                deployment_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_validate(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                parameters: Deployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentValidateResult]: ...

        @overload
        async def begin_validate(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                parameters: Deployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentValidateResult]: ...

        @overload
        async def begin_validate(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentValidateResult]: ...

        @overload
        async def begin_validate_at_management_group_scope(
                self, 
                group_id: str, 
                deployment_name: str, 
                parameters: ScopedDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentValidateResult]: ...

        @overload
        async def begin_validate_at_management_group_scope(
                self, 
                group_id: str, 
                deployment_name: str, 
                parameters: ScopedDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentValidateResult]: ...

        @overload
        async def begin_validate_at_management_group_scope(
                self, 
                group_id: str, 
                deployment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentValidateResult]: ...

        @overload
        async def begin_validate_at_scope(
                self, 
                scope: str, 
                deployment_name: str, 
                parameters: Deployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentValidateResult]: ...

        @overload
        async def begin_validate_at_scope(
                self, 
                scope: str, 
                deployment_name: str, 
                parameters: Deployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentValidateResult]: ...

        @overload
        async def begin_validate_at_scope(
                self, 
                scope: str, 
                deployment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentValidateResult]: ...

        @overload
        async def begin_validate_at_subscription_scope(
                self, 
                deployment_name: str, 
                parameters: Deployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentValidateResult]: ...

        @overload
        async def begin_validate_at_subscription_scope(
                self, 
                deployment_name: str, 
                parameters: Deployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentValidateResult]: ...

        @overload
        async def begin_validate_at_subscription_scope(
                self, 
                deployment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentValidateResult]: ...

        @overload
        async def begin_validate_at_tenant_scope(
                self, 
                deployment_name: str, 
                parameters: ScopedDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentValidateResult]: ...

        @overload
        async def begin_validate_at_tenant_scope(
                self, 
                deployment_name: str, 
                parameters: ScopedDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentValidateResult]: ...

        @overload
        async def begin_validate_at_tenant_scope(
                self, 
                deployment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentValidateResult]: ...

        @overload
        async def begin_what_if(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                parameters: DeploymentWhatIf, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WhatIfOperationResult]: ...

        @overload
        async def begin_what_if(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                parameters: DeploymentWhatIf, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WhatIfOperationResult]: ...

        @overload
        async def begin_what_if(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WhatIfOperationResult]: ...

        @overload
        async def begin_what_if_at_management_group_scope(
                self, 
                group_id: str, 
                deployment_name: str, 
                parameters: ScopedDeploymentWhatIf, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WhatIfOperationResult]: ...

        @overload
        async def begin_what_if_at_management_group_scope(
                self, 
                group_id: str, 
                deployment_name: str, 
                parameters: ScopedDeploymentWhatIf, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WhatIfOperationResult]: ...

        @overload
        async def begin_what_if_at_management_group_scope(
                self, 
                group_id: str, 
                deployment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WhatIfOperationResult]: ...

        @overload
        async def begin_what_if_at_subscription_scope(
                self, 
                deployment_name: str, 
                parameters: DeploymentWhatIf, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WhatIfOperationResult]: ...

        @overload
        async def begin_what_if_at_subscription_scope(
                self, 
                deployment_name: str, 
                parameters: DeploymentWhatIf, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WhatIfOperationResult]: ...

        @overload
        async def begin_what_if_at_subscription_scope(
                self, 
                deployment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WhatIfOperationResult]: ...

        @overload
        async def begin_what_if_at_tenant_scope(
                self, 
                deployment_name: str, 
                parameters: ScopedDeploymentWhatIf, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WhatIfOperationResult]: ...

        @overload
        async def begin_what_if_at_tenant_scope(
                self, 
                deployment_name: str, 
                parameters: ScopedDeploymentWhatIf, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WhatIfOperationResult]: ...

        @overload
        async def begin_what_if_at_tenant_scope(
                self, 
                deployment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WhatIfOperationResult]: ...

        @distributed_trace_async
        async def calculate_template_hash(
                self, 
                template: Any, 
                **kwargs: Any
            ) -> TemplateHashResult: ...

        @distributed_trace_async
        async def cancel(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def cancel_at_management_group_scope(
                self, 
                group_id: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def cancel_at_scope(
                self, 
                scope: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def cancel_at_subscription_scope(
                self, 
                deployment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def cancel_at_tenant_scope(
                self, 
                deployment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def check_existence(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> bool: ...

        @distributed_trace_async
        async def check_existence_at_management_group_scope(
                self, 
                group_id: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> bool: ...

        @distributed_trace_async
        async def check_existence_at_scope(
                self, 
                scope: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> bool: ...

        @distributed_trace_async
        async def check_existence_at_subscription_scope(
                self, 
                deployment_name: str, 
                **kwargs: Any
            ) -> bool: ...

        @distributed_trace_async
        async def check_existence_at_tenant_scope(
                self, 
                deployment_name: str, 
                **kwargs: Any
            ) -> bool: ...

        @distributed_trace_async
        async def export_template(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> DeploymentExportResult: ...

        @distributed_trace_async
        async def export_template_at_management_group_scope(
                self, 
                group_id: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> DeploymentExportResult: ...

        @distributed_trace_async
        async def export_template_at_scope(
                self, 
                scope: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> DeploymentExportResult: ...

        @distributed_trace_async
        async def export_template_at_subscription_scope(
                self, 
                deployment_name: str, 
                **kwargs: Any
            ) -> DeploymentExportResult: ...

        @distributed_trace_async
        async def export_template_at_tenant_scope(
                self, 
                deployment_name: str, 
                **kwargs: Any
            ) -> DeploymentExportResult: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> DeploymentExtended: ...

        @distributed_trace_async
        async def get_at_management_group_scope(
                self, 
                group_id: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> DeploymentExtended: ...

        @distributed_trace_async
        async def get_at_scope(
                self, 
                scope: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> DeploymentExtended: ...

        @distributed_trace_async
        async def get_at_subscription_scope(
                self, 
                deployment_name: str, 
                **kwargs: Any
            ) -> DeploymentExtended: ...

        @distributed_trace_async
        async def get_at_tenant_scope(
                self, 
                deployment_name: str, 
                **kwargs: Any
            ) -> DeploymentExtended: ...

        @distributed_trace
        def list_at_management_group_scope(
                self, 
                group_id: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DeploymentExtended]: ...

        @distributed_trace
        def list_at_scope(
                self, 
                scope: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DeploymentExtended]: ...

        @distributed_trace
        def list_at_subscription_scope(
                self, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DeploymentExtended]: ...

        @distributed_trace
        def list_at_tenant_scope(
                self, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DeploymentExtended]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DeploymentExtended]: ...


namespace azure.mgmt.resource.deployments.models

    class azure.mgmt.resource.deployments.models.Alias(_Model):
        default_metadata: Optional[AliasPathMetadata]
        default_path: Optional[str]
        default_pattern: Optional[AliasPattern]
        name: Optional[str]
        paths: Optional[list[AliasPath]]
        type: Optional[Union[str, AliasType]]

        @overload
        def __init__(
                self, 
                *, 
                default_path: Optional[str] = ..., 
                default_pattern: Optional[AliasPattern] = ..., 
                name: Optional[str] = ..., 
                paths: Optional[list[AliasPath]] = ..., 
                type: Optional[Union[str, AliasType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deployments.models.AliasPath(_Model):
        api_versions: Optional[list[str]]
        metadata: Optional[AliasPathMetadata]
        path: Optional[str]
        pattern: Optional[AliasPattern]

        @overload
        def __init__(
                self, 
                *, 
                api_versions: Optional[list[str]] = ..., 
                path: Optional[str] = ..., 
                pattern: Optional[AliasPattern] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deployments.models.AliasPathAttributes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MODIFIABLE = "Modifiable"
        NONE = "None"


    class azure.mgmt.resource.deployments.models.AliasPathMetadata(_Model):
        attributes: Optional[Union[str, AliasPathAttributes]]
        type: Optional[Union[str, AliasPathTokenType]]


    class azure.mgmt.resource.deployments.models.AliasPathTokenType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANY = "Any"
        ARRAY = "Array"
        BOOLEAN = "Boolean"
        INTEGER = "Integer"
        NOT_SPECIFIED = "NotSpecified"
        NUMBER = "Number"
        OBJECT = "Object"
        STRING = "String"


    class azure.mgmt.resource.deployments.models.AliasPattern(_Model):
        phrase: Optional[str]
        type: Optional[Union[str, AliasPatternType]]
        variable: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                phrase: Optional[str] = ..., 
                type: Optional[Union[str, AliasPatternType]] = ..., 
                variable: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deployments.models.AliasPatternType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXTRACT = "Extract"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.resource.deployments.models.AliasType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MASK = "Mask"
        NOT_SPECIFIED = "NotSpecified"
        PLAIN_TEXT = "PlainText"


    class azure.mgmt.resource.deployments.models.ApiProfile(_Model):
        api_version: Optional[str]
        profile_version: Optional[str]


    class azure.mgmt.resource.deployments.models.BasicDependency(_Model):
        id: Optional[str]
        resource_name: Optional[str]
        resource_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                resource_name: Optional[str] = ..., 
                resource_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deployments.models.ChangeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATE = "Create"
        DELETE = "Delete"
        DEPLOY = "Deploy"
        IGNORE = "Ignore"
        MODIFY = "Modify"
        NO_CHANGE = "NoChange"
        UNSUPPORTED = "Unsupported"


    class azure.mgmt.resource.deployments.models.CloudError(_Model):
        error: Optional[ErrorResponse]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorResponse] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deployments.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.resource.deployments.models.DebugSetting(_Model):
        detail_level: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                detail_level: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deployments.models.Dependency(_Model):
        depends_on: Optional[list[BasicDependency]]
        id: Optional[str]
        resource_name: Optional[str]
        resource_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                depends_on: Optional[list[BasicDependency]] = ..., 
                id: Optional[str] = ..., 
                resource_name: Optional[str] = ..., 
                resource_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deployments.models.Deployment(_Model):
        identity: Optional[DeploymentIdentity]
        location: Optional[str]
        properties: DeploymentProperties
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[DeploymentIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: DeploymentProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deployments.models.DeploymentDiagnosticsDefinition(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: str
        level: Union[str, Level]
        message: str
        target: Optional[str]


    class azure.mgmt.resource.deployments.models.DeploymentExportResult(_Model):
        template: Optional[Any]

        @overload
        def __init__(
                self, 
                *, 
                template: Optional[Any] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deployments.models.DeploymentExtended(ExtensionResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[DeploymentPropertiesExtended]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[DeploymentPropertiesExtended] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deployments.models.DeploymentExtensionConfigItem(_Model):
        key_vault_reference: Optional[KeyVaultParameterReference]
        type: Optional[Union[str, ExtensionConfigPropertyType]]
        value: Optional[Any]

        @overload
        def __init__(
                self, 
                *, 
                key_vault_reference: Optional[KeyVaultParameterReference] = ..., 
                value: Optional[Any] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deployments.models.DeploymentExtensionDefinition(_Model):
        alias: Optional[str]
        config: Optional[dict[str, DeploymentExtensionConfigItem]]
        config_id: Optional[str]
        name: Optional[str]
        version: Optional[str]


    class azure.mgmt.resource.deployments.models.DeploymentExternalInput(_Model):
        value: Any

        @overload
        def __init__(
                self, 
                *, 
                value: Any
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deployments.models.DeploymentExternalInputDefinition(_Model):
        config: Optional[Any]
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                config: Optional[Any] = ..., 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deployments.models.DeploymentIdentity(_Model):
        type: Union[str, DeploymentIdentityType]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, DeploymentIdentityType], 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deployments.models.DeploymentIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.resource.deployments.models.DeploymentMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETE = "Complete"
        INCREMENTAL = "Incremental"


    class azure.mgmt.resource.deployments.models.DeploymentOperation(_Model):
        id: Optional[str]
        operation_id: Optional[str]
        properties: Optional[DeploymentOperationProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DeploymentOperationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deployments.models.DeploymentOperationProperties(_Model):
        duration: Optional[str]
        provisioning_operation: Optional[Union[str, ProvisioningOperation]]
        provisioning_state: Optional[str]
        request: Optional[HttpMessage]
        response: Optional[HttpMessage]
        service_request_id: Optional[str]
        status_code: Optional[str]
        status_message: Optional[StatusMessage]
        target_resource: Optional[TargetResource]
        timestamp: Optional[datetime]


    class azure.mgmt.resource.deployments.models.DeploymentParameter(_Model):
        expression: Optional[str]
        reference: Optional[KeyVaultParameterReference]
        value: Optional[Any]

        @overload
        def __init__(
                self, 
                *, 
                expression: Optional[str] = ..., 
                reference: Optional[KeyVaultParameterReference] = ..., 
                value: Optional[Any] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deployments.models.DeploymentProperties(_Model):
        debug_setting: Optional[DebugSetting]
        expression_evaluation_options: Optional[ExpressionEvaluationOptions]
        extension_configs: Optional[dict[str, dict[str, DeploymentExtensionConfigItem]]]
        external_input_definitions: Optional[dict[str, DeploymentExternalInputDefinition]]
        external_inputs: Optional[dict[str, DeploymentExternalInput]]
        mode: Union[str, DeploymentMode]
        on_error_deployment: Optional[OnErrorDeployment]
        parameters: Optional[dict[str, DeploymentParameter]]
        parameters_link: Optional[ParametersLink]
        template: Optional[Any]
        template_link: Optional[TemplateLink]
        validation_level: Optional[Union[str, ValidationLevel]]

        @overload
        def __init__(
                self, 
                *, 
                debug_setting: Optional[DebugSetting] = ..., 
                expression_evaluation_options: Optional[ExpressionEvaluationOptions] = ..., 
                extension_configs: Optional[dict[str, dict[str, DeploymentExtensionConfigItem]]] = ..., 
                external_input_definitions: Optional[dict[str, DeploymentExternalInputDefinition]] = ..., 
                external_inputs: Optional[dict[str, DeploymentExternalInput]] = ..., 
                mode: Union[str, DeploymentMode], 
                on_error_deployment: Optional[OnErrorDeployment] = ..., 
                parameters: Optional[dict[str, DeploymentParameter]] = ..., 
                parameters_link: Optional[ParametersLink] = ..., 
                template: Optional[Any] = ..., 
                template_link: Optional[TemplateLink] = ..., 
                validation_level: Optional[Union[str, ValidationLevel]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deployments.models.DeploymentPropertiesExtended(_Model):
        correlation_id: Optional[str]
        debug_setting: Optional[DebugSetting]
        dependencies: Optional[list[Dependency]]
        diagnostics: Optional[list[DeploymentDiagnosticsDefinition]]
        duration: Optional[str]
        error: Optional[ErrorResponse]
        extensions: Optional[list[DeploymentExtensionDefinition]]
        mode: Optional[Union[str, DeploymentMode]]
        on_error_deployment: Optional[OnErrorDeploymentExtended]
        output_resources: Optional[list[ResourceReference]]
        outputs: Optional[Any]
        parameters: Optional[Any]
        parameters_link: Optional[ParametersLink]
        providers: Optional[list[Provider]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        template_hash: Optional[str]
        template_link: Optional[TemplateLink]
        timestamp: Optional[datetime]
        validated_resources: Optional[list[ResourceReference]]
        validation_level: Optional[Union[str, ValidationLevel]]

        @overload
        def __init__(
                self, 
                *, 
                validation_level: Optional[Union[str, ValidationLevel]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deployments.models.DeploymentValidateResult(_Model):
        error: Optional[ErrorResponse]
        id: Optional[str]
        name: Optional[str]
        properties: Optional[DeploymentPropertiesExtended]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DeploymentPropertiesExtended] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deployments.models.DeploymentWhatIf(_Model):
        location: Optional[str]
        properties: DeploymentWhatIfProperties

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: DeploymentWhatIfProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deployments.models.DeploymentWhatIfProperties(DeploymentProperties):
        debug_setting: DebugSetting
        expression_evaluation_options: ExpressionEvaluationOptions
        extension_configs: dict[str, dict[str, DeploymentExtensionConfigItem]]
        external_input_definitions: dict[str, DeploymentExternalInputDefinition]
        external_inputs: dict[str, DeploymentExternalInput]
        mode: Union[str, DeploymentMode]
        on_error_deployment: OnErrorDeployment
        parameters: dict[str, DeploymentParameter]
        parameters_link: ParametersLink
        template: any
        template_link: TemplateLink
        validation_level: Union[str, ValidationLevel]
        what_if_settings: Optional[DeploymentWhatIfSettings]

        @overload
        def __init__(
                self, 
                *, 
                debug_setting: Optional[DebugSetting] = ..., 
                expression_evaluation_options: Optional[ExpressionEvaluationOptions] = ..., 
                extension_configs: Optional[dict[str, dict[str, DeploymentExtensionConfigItem]]] = ..., 
                external_input_definitions: Optional[dict[str, DeploymentExternalInputDefinition]] = ..., 
                external_inputs: Optional[dict[str, DeploymentExternalInput]] = ..., 
                mode: Union[str, DeploymentMode], 
                on_error_deployment: Optional[OnErrorDeployment] = ..., 
                parameters: Optional[dict[str, DeploymentParameter]] = ..., 
                parameters_link: Optional[ParametersLink] = ..., 
                template: Optional[Any] = ..., 
                template_link: Optional[TemplateLink] = ..., 
                validation_level: Optional[Union[str, ValidationLevel]] = ..., 
                what_if_settings: Optional[DeploymentWhatIfSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deployments.models.DeploymentWhatIfSettings(_Model):
        result_format: Optional[Union[str, WhatIfResultFormat]]

        @overload
        def __init__(
                self, 
                *, 
                result_format: Optional[Union[str, WhatIfResultFormat]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deployments.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.resource.deployments.models.ErrorResponse(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorResponse]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.resource.deployments.models.ExpressionEvaluationOptions(_Model):
        scope: Optional[Union[str, ExpressionEvaluationOptionsScopeType]]

        @overload
        def __init__(
                self, 
                *, 
                scope: Optional[Union[str, ExpressionEvaluationOptionsScopeType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deployments.models.ExpressionEvaluationOptionsScopeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INNER = "Inner"
        NOT_SPECIFIED = "NotSpecified"
        OUTER = "Outer"


    class azure.mgmt.resource.deployments.models.ExtensionConfigPropertyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARRAY = "Array"
        BOOL = "Bool"
        INT = "Int"
        OBJECT = "Object"
        SECURE_OBJECT = "SecureObject"
        SECURE_STRING = "SecureString"
        STRING = "String"


    class azure.mgmt.resource.deployments.models.ExtensionResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.resource.deployments.models.HttpMessage(_Model):
        content: Optional[Any]

        @overload
        def __init__(
                self, 
                *, 
                content: Optional[Any] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deployments.models.KeyVaultParameterReference(_Model):
        key_vault: KeyVaultReference
        secret_name: str
        secret_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key_vault: KeyVaultReference, 
                secret_name: str, 
                secret_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deployments.models.KeyVaultReference(_Model):
        id: str

        @overload
        def __init__(
                self, 
                *, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deployments.models.Level(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        INFO = "Info"
        WARNING = "Warning"


    class azure.mgmt.resource.deployments.models.OnErrorDeployment(_Model):
        deployment_name: Optional[str]
        type: Optional[Union[str, OnErrorDeploymentType]]

        @overload
        def __init__(
                self, 
                *, 
                deployment_name: Optional[str] = ..., 
                type: Optional[Union[str, OnErrorDeploymentType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deployments.models.OnErrorDeploymentExtended(_Model):
        deployment_name: Optional[str]
        provisioning_state: Optional[str]
        type: Optional[Union[str, OnErrorDeploymentType]]

        @overload
        def __init__(
                self, 
                *, 
                deployment_name: Optional[str] = ..., 
                type: Optional[Union[str, OnErrorDeploymentType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deployments.models.OnErrorDeploymentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LAST_SUCCESSFUL = "LastSuccessful"
        SPECIFIC_DEPLOYMENT = "SpecificDeployment"


    class azure.mgmt.resource.deployments.models.ParametersLink(_Model):
        content_version: Optional[str]
        uri: str

        @overload
        def __init__(
                self, 
                *, 
                content_version: Optional[str] = ..., 
                uri: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deployments.models.PropertyChangeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARRAY = "Array"
        CREATE = "Create"
        DELETE = "Delete"
        MODIFY = "Modify"
        NO_EFFECT = "NoEffect"


    class azure.mgmt.resource.deployments.models.Provider(_Model):
        id: Optional[str]
        namespace: Optional[str]
        provider_authorization_consent_state: Optional[Union[str, ProviderAuthorizationConsentState]]
        registration_policy: Optional[str]
        registration_state: Optional[str]
        resource_types: Optional[list[ProviderResourceType]]

        @overload
        def __init__(
                self, 
                *, 
                namespace: Optional[str] = ..., 
                provider_authorization_consent_state: Optional[Union[str, ProviderAuthorizationConsentState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deployments.models.ProviderAuthorizationConsentState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONSENTED = "Consented"
        NOT_REQUIRED = "NotRequired"
        NOT_SPECIFIED = "NotSpecified"
        REQUIRED = "Required"


    class azure.mgmt.resource.deployments.models.ProviderExtendedLocation(_Model):
        extended_locations: Optional[list[str]]
        location: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                extended_locations: Optional[list[str]] = ..., 
                location: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deployments.models.ProviderResourceType(_Model):
        aliases: Optional[list[Alias]]
        api_profiles: Optional[list[ApiProfile]]
        api_versions: Optional[list[str]]
        capabilities: Optional[str]
        default_api_version: Optional[str]
        location_mappings: Optional[list[ProviderExtendedLocation]]
        locations: Optional[list[str]]
        properties: Optional[dict[str, str]]
        resource_type: Optional[str]
        zone_mappings: Optional[list[ZoneMapping]]

        @overload
        def __init__(
                self, 
                *, 
                aliases: Optional[list[Alias]] = ..., 
                api_versions: Optional[list[str]] = ..., 
                capabilities: Optional[str] = ..., 
                location_mappings: Optional[list[ProviderExtendedLocation]] = ..., 
                locations: Optional[list[str]] = ..., 
                properties: Optional[dict[str, str]] = ..., 
                resource_type: Optional[str] = ..., 
                zone_mappings: Optional[list[ZoneMapping]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deployments.models.ProvisioningOperation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTION = "Action"
        AZURE_ASYNC_OPERATION_WAITING = "AzureAsyncOperationWaiting"
        CREATE = "Create"
        DELETE = "Delete"
        DEPLOYMENT_CLEANUP = "DeploymentCleanup"
        EVALUATE_DEPLOYMENT_OUTPUT = "EvaluateDeploymentOutput"
        NOT_SPECIFIED = "NotSpecified"
        READ = "Read"
        RESOURCE_CACHE_WAITING = "ResourceCacheWaiting"
        WAITING = "Waiting"


    class azure.mgmt.resource.deployments.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATED = "Created"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        FAILED = "Failed"
        NOT_SPECIFIED = "NotSpecified"
        READY = "Ready"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.resource.deployments.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.resource.deployments.models.ResourceReference(_Model):
        api_version: Optional[str]
        extension: Optional[DeploymentExtensionDefinition]
        id: Optional[str]
        identifiers: Optional[Any]
        resource_type: Optional[str]


    class azure.mgmt.resource.deployments.models.ScopedDeployment(_Model):
        location: str
        properties: DeploymentProperties
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: DeploymentProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deployments.models.ScopedDeploymentWhatIf(_Model):
        location: str
        properties: DeploymentWhatIfProperties

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: DeploymentWhatIfProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deployments.models.StatusMessage(_Model):
        error: Optional[ErrorResponse]
        status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorResponse] = ..., 
                status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deployments.models.SystemData(_Model):
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


    class azure.mgmt.resource.deployments.models.TargetResource(_Model):
        api_version: Optional[str]
        extension: Optional[DeploymentExtensionDefinition]
        id: Optional[str]
        identifiers: Optional[Any]
        resource_name: Optional[str]
        resource_type: Optional[str]
        symbolic_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                api_version: Optional[str] = ..., 
                extension: Optional[DeploymentExtensionDefinition] = ..., 
                id: Optional[str] = ..., 
                identifiers: Optional[Any] = ..., 
                resource_name: Optional[str] = ..., 
                resource_type: Optional[str] = ..., 
                symbolic_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deployments.models.TemplateHashResult(_Model):
        minified_template: Optional[str]
        template_hash: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                minified_template: Optional[str] = ..., 
                template_hash: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deployments.models.TemplateLink(_Model):
        content_version: Optional[str]
        id: Optional[str]
        query_string: Optional[str]
        relative_path: Optional[str]
        uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                content_version: Optional[str] = ..., 
                id: Optional[str] = ..., 
                query_string: Optional[str] = ..., 
                relative_path: Optional[str] = ..., 
                uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deployments.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.resource.deployments.models.ValidationLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PROVIDER = "Provider"
        PROVIDER_NO_RBAC = "ProviderNoRbac"
        TEMPLATE = "Template"


    class azure.mgmt.resource.deployments.models.WhatIfChange(_Model):
        after: Optional[Any]
        before: Optional[Any]
        change_type: Union[str, ChangeType]
        delta: Optional[list[WhatIfPropertyChange]]
        deployment_id: Optional[str]
        extension: Optional[DeploymentExtensionDefinition]
        identifiers: Optional[Any]
        resource_id: Optional[str]
        symbolic_name: Optional[str]
        unsupported_reason: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                after: Optional[Any] = ..., 
                before: Optional[Any] = ..., 
                change_type: Union[str, ChangeType], 
                delta: Optional[list[WhatIfPropertyChange]] = ..., 
                deployment_id: Optional[str] = ..., 
                extension: Optional[DeploymentExtensionDefinition] = ..., 
                identifiers: Optional[Any] = ..., 
                resource_id: Optional[str] = ..., 
                symbolic_name: Optional[str] = ..., 
                unsupported_reason: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deployments.models.WhatIfOperationProperties(_Model):
        changes: Optional[list[WhatIfChange]]
        diagnostics: Optional[list[DeploymentDiagnosticsDefinition]]
        potential_changes: Optional[list[WhatIfChange]]

        @overload
        def __init__(
                self, 
                *, 
                changes: Optional[list[WhatIfChange]] = ..., 
                potential_changes: Optional[list[WhatIfChange]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deployments.models.WhatIfOperationResult(_Model):
        error: Optional[ErrorResponse]
        properties: Optional[WhatIfOperationProperties]
        status: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorResponse] = ..., 
                properties: Optional[WhatIfOperationProperties] = ..., 
                status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.resource.deployments.models.WhatIfPropertyChange(_Model):
        after: Optional[Any]
        before: Optional[Any]
        children: Optional[list[WhatIfPropertyChange]]
        path: str
        property_change_type: Union[str, PropertyChangeType]

        @overload
        def __init__(
                self, 
                *, 
                after: Optional[Any] = ..., 
                before: Optional[Any] = ..., 
                children: Optional[list[WhatIfPropertyChange]] = ..., 
                path: str, 
                property_change_type: Union[str, PropertyChangeType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deployments.models.WhatIfResultFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FULL_RESOURCE_PAYLOADS = "FullResourcePayloads"
        RESOURCE_ID_ONLY = "ResourceIdOnly"


    class azure.mgmt.resource.deployments.models.ZoneMapping(_Model):
        location: Optional[str]
        zones: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.resource.deployments.operations

    class azure.mgmt.resource.deployments.operations.DeploymentOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> DeploymentOperation: ...

        @distributed_trace
        def get_at_management_group_scope(
                self, 
                group_id: str, 
                deployment_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> DeploymentOperation: ...

        @distributed_trace
        def get_at_scope(
                self, 
                scope: str, 
                deployment_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> DeploymentOperation: ...

        @distributed_trace
        def get_at_subscription_scope(
                self, 
                deployment_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> DeploymentOperation: ...

        @distributed_trace
        def get_at_tenant_scope(
                self, 
                deployment_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> DeploymentOperation: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DeploymentOperation]: ...

        @distributed_trace
        def list_at_management_group_scope(
                self, 
                group_id: str, 
                deployment_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DeploymentOperation]: ...

        @distributed_trace
        def list_at_scope(
                self, 
                scope: str, 
                deployment_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DeploymentOperation]: ...

        @distributed_trace
        def list_at_subscription_scope(
                self, 
                deployment_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DeploymentOperation]: ...

        @distributed_trace
        def list_at_tenant_scope(
                self, 
                deployment_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DeploymentOperation]: ...


    class azure.mgmt.resource.deployments.operations.DeploymentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                parameters: Deployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentExtended]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                parameters: Deployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentExtended]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentExtended]: ...

        @overload
        def begin_create_or_update_at_management_group_scope(
                self, 
                group_id: str, 
                deployment_name: str, 
                parameters: ScopedDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentExtended]: ...

        @overload
        def begin_create_or_update_at_management_group_scope(
                self, 
                group_id: str, 
                deployment_name: str, 
                parameters: ScopedDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentExtended]: ...

        @overload
        def begin_create_or_update_at_management_group_scope(
                self, 
                group_id: str, 
                deployment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentExtended]: ...

        @overload
        def begin_create_or_update_at_scope(
                self, 
                scope: str, 
                deployment_name: str, 
                parameters: Deployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentExtended]: ...

        @overload
        def begin_create_or_update_at_scope(
                self, 
                scope: str, 
                deployment_name: str, 
                parameters: Deployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentExtended]: ...

        @overload
        def begin_create_or_update_at_scope(
                self, 
                scope: str, 
                deployment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentExtended]: ...

        @overload
        def begin_create_or_update_at_subscription_scope(
                self, 
                deployment_name: str, 
                parameters: Deployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentExtended]: ...

        @overload
        def begin_create_or_update_at_subscription_scope(
                self, 
                deployment_name: str, 
                parameters: Deployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentExtended]: ...

        @overload
        def begin_create_or_update_at_subscription_scope(
                self, 
                deployment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentExtended]: ...

        @overload
        def begin_create_or_update_at_tenant_scope(
                self, 
                deployment_name: str, 
                parameters: ScopedDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentExtended]: ...

        @overload
        def begin_create_or_update_at_tenant_scope(
                self, 
                deployment_name: str, 
                parameters: ScopedDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentExtended]: ...

        @overload
        def begin_create_or_update_at_tenant_scope(
                self, 
                deployment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentExtended]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_at_management_group_scope(
                self, 
                group_id: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_at_scope(
                self, 
                scope: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_at_subscription_scope(
                self, 
                deployment_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_at_tenant_scope(
                self, 
                deployment_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_validate(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                parameters: Deployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentValidateResult]: ...

        @overload
        def begin_validate(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                parameters: Deployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentValidateResult]: ...

        @overload
        def begin_validate(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentValidateResult]: ...

        @overload
        def begin_validate_at_management_group_scope(
                self, 
                group_id: str, 
                deployment_name: str, 
                parameters: ScopedDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentValidateResult]: ...

        @overload
        def begin_validate_at_management_group_scope(
                self, 
                group_id: str, 
                deployment_name: str, 
                parameters: ScopedDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentValidateResult]: ...

        @overload
        def begin_validate_at_management_group_scope(
                self, 
                group_id: str, 
                deployment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentValidateResult]: ...

        @overload
        def begin_validate_at_scope(
                self, 
                scope: str, 
                deployment_name: str, 
                parameters: Deployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentValidateResult]: ...

        @overload
        def begin_validate_at_scope(
                self, 
                scope: str, 
                deployment_name: str, 
                parameters: Deployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentValidateResult]: ...

        @overload
        def begin_validate_at_scope(
                self, 
                scope: str, 
                deployment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentValidateResult]: ...

        @overload
        def begin_validate_at_subscription_scope(
                self, 
                deployment_name: str, 
                parameters: Deployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentValidateResult]: ...

        @overload
        def begin_validate_at_subscription_scope(
                self, 
                deployment_name: str, 
                parameters: Deployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentValidateResult]: ...

        @overload
        def begin_validate_at_subscription_scope(
                self, 
                deployment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentValidateResult]: ...

        @overload
        def begin_validate_at_tenant_scope(
                self, 
                deployment_name: str, 
                parameters: ScopedDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentValidateResult]: ...

        @overload
        def begin_validate_at_tenant_scope(
                self, 
                deployment_name: str, 
                parameters: ScopedDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentValidateResult]: ...

        @overload
        def begin_validate_at_tenant_scope(
                self, 
                deployment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentValidateResult]: ...

        @overload
        def begin_what_if(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                parameters: DeploymentWhatIf, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WhatIfOperationResult]: ...

        @overload
        def begin_what_if(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                parameters: DeploymentWhatIf, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WhatIfOperationResult]: ...

        @overload
        def begin_what_if(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WhatIfOperationResult]: ...

        @overload
        def begin_what_if_at_management_group_scope(
                self, 
                group_id: str, 
                deployment_name: str, 
                parameters: ScopedDeploymentWhatIf, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WhatIfOperationResult]: ...

        @overload
        def begin_what_if_at_management_group_scope(
                self, 
                group_id: str, 
                deployment_name: str, 
                parameters: ScopedDeploymentWhatIf, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WhatIfOperationResult]: ...

        @overload
        def begin_what_if_at_management_group_scope(
                self, 
                group_id: str, 
                deployment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WhatIfOperationResult]: ...

        @overload
        def begin_what_if_at_subscription_scope(
                self, 
                deployment_name: str, 
                parameters: DeploymentWhatIf, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WhatIfOperationResult]: ...

        @overload
        def begin_what_if_at_subscription_scope(
                self, 
                deployment_name: str, 
                parameters: DeploymentWhatIf, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WhatIfOperationResult]: ...

        @overload
        def begin_what_if_at_subscription_scope(
                self, 
                deployment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WhatIfOperationResult]: ...

        @overload
        def begin_what_if_at_tenant_scope(
                self, 
                deployment_name: str, 
                parameters: ScopedDeploymentWhatIf, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WhatIfOperationResult]: ...

        @overload
        def begin_what_if_at_tenant_scope(
                self, 
                deployment_name: str, 
                parameters: ScopedDeploymentWhatIf, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WhatIfOperationResult]: ...

        @overload
        def begin_what_if_at_tenant_scope(
                self, 
                deployment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WhatIfOperationResult]: ...

        @distributed_trace
        def calculate_template_hash(
                self, 
                template: Any, 
                **kwargs: Any
            ) -> TemplateHashResult: ...

        @distributed_trace
        def cancel(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def cancel_at_management_group_scope(
                self, 
                group_id: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def cancel_at_scope(
                self, 
                scope: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def cancel_at_subscription_scope(
                self, 
                deployment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def cancel_at_tenant_scope(
                self, 
                deployment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def check_existence(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> bool: ...

        @distributed_trace
        def check_existence_at_management_group_scope(
                self, 
                group_id: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> bool: ...

        @distributed_trace
        def check_existence_at_scope(
                self, 
                scope: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> bool: ...

        @distributed_trace
        def check_existence_at_subscription_scope(
                self, 
                deployment_name: str, 
                **kwargs: Any
            ) -> bool: ...

        @distributed_trace
        def check_existence_at_tenant_scope(
                self, 
                deployment_name: str, 
                **kwargs: Any
            ) -> bool: ...

        @distributed_trace
        def export_template(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> DeploymentExportResult: ...

        @distributed_trace
        def export_template_at_management_group_scope(
                self, 
                group_id: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> DeploymentExportResult: ...

        @distributed_trace
        def export_template_at_scope(
                self, 
                scope: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> DeploymentExportResult: ...

        @distributed_trace
        def export_template_at_subscription_scope(
                self, 
                deployment_name: str, 
                **kwargs: Any
            ) -> DeploymentExportResult: ...

        @distributed_trace
        def export_template_at_tenant_scope(
                self, 
                deployment_name: str, 
                **kwargs: Any
            ) -> DeploymentExportResult: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> DeploymentExtended: ...

        @distributed_trace
        def get_at_management_group_scope(
                self, 
                group_id: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> DeploymentExtended: ...

        @distributed_trace
        def get_at_scope(
                self, 
                scope: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> DeploymentExtended: ...

        @distributed_trace
        def get_at_subscription_scope(
                self, 
                deployment_name: str, 
                **kwargs: Any
            ) -> DeploymentExtended: ...

        @distributed_trace
        def get_at_tenant_scope(
                self, 
                deployment_name: str, 
                **kwargs: Any
            ) -> DeploymentExtended: ...

        @distributed_trace
        def list_at_management_group_scope(
                self, 
                group_id: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DeploymentExtended]: ...

        @distributed_trace
        def list_at_scope(
                self, 
                scope: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DeploymentExtended]: ...

        @distributed_trace
        def list_at_subscription_scope(
                self, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DeploymentExtended]: ...

        @distributed_trace
        def list_at_tenant_scope(
                self, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DeploymentExtended]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DeploymentExtended]: ...


namespace azure.mgmt.resource.deployments.types

    class azure.mgmt.resource.deployments.types.DebugSetting(TypedDict, total=False):
        key "detailLevel": str
        detail_level: str


    class azure.mgmt.resource.deployments.types.Deployment(TypedDict, total=False):
        key "identity": ForwardRef('DeploymentIdentity', module='types')
        key "location": str
        key "properties": Required[DeploymentProperties]
        identity: DeploymentIdentity
        location: str
        properties: DeploymentProperties
        tags: dict[str, str]


    class azure.mgmt.resource.deployments.types.DeploymentExtensionConfigItem(TypedDict, total=False):
        key "keyVaultReference": ForwardRef('KeyVaultParameterReference', module='types')
        key "type": Union[str, ExtensionConfigPropertyType]
        key "value": Any
        key_vault_reference: KeyVaultParameterReference
        type: Union[str, ExtensionConfigPropertyType]
        value: Any


    class azure.mgmt.resource.deployments.types.DeploymentExternalInput(TypedDict, total=False):
        key "value": Required[Any]
        value: Any


    class azure.mgmt.resource.deployments.types.DeploymentExternalInputDefinition(TypedDict, total=False):
        key "config": Any
        key "kind": Required[str]
        config: Any
        kind: str


    class azure.mgmt.resource.deployments.types.DeploymentIdentity(TypedDict, total=False):
        key "type": Required[Union[str, DeploymentIdentityType]]
        type: Union[str, DeploymentIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]
        user_assigned_identities: dict[str, UserAssignedIdentity]


    class azure.mgmt.resource.deployments.types.DeploymentParameter(TypedDict, total=False):
        key "expression": str
        key "reference": ForwardRef('KeyVaultParameterReference', module='types')
        key "value": Any
        expression: str
        reference: KeyVaultParameterReference
        value: Any


    class azure.mgmt.resource.deployments.types.DeploymentProperties(TypedDict, total=False):
        key "debugSetting": ForwardRef('DebugSetting', module='types')
        key "expressionEvaluationOptions": ForwardRef('ExpressionEvaluationOptions', module='types')
        key "mode": Required[Union[str, DeploymentMode]]
        key "onErrorDeployment": ForwardRef('OnErrorDeployment', module='types')
        key "parametersLink": ForwardRef('ParametersLink', module='types')
        key "template": Any
        key "templateLink": ForwardRef('TemplateLink', module='types')
        key "validationLevel": Union[str, ValidationLevel]
        debug_setting: DebugSetting
        expression_evaluation_options: ExpressionEvaluationOptions
        extensionConfigs: dict[str, dict[str, DeploymentExtensionConfigItem]]
        extension_configs: dict[str, dict[str, DeploymentExtensionConfigItem]]
        externalInputDefinitions: dict[str, DeploymentExternalInputDefinition]
        externalInputs: dict[str, DeploymentExternalInput]
        external_input_definitions: dict[str, DeploymentExternalInputDefinition]
        external_inputs: dict[str, DeploymentExternalInput]
        mode: Union[str, DeploymentMode]
        on_error_deployment: OnErrorDeployment
        parameters: dict[str, DeploymentParameter]
        parameters_link: ParametersLink
        template: Any
        template_link: TemplateLink
        validation_level: Union[str, ValidationLevel]


    class azure.mgmt.resource.deployments.types.DeploymentWhatIf(TypedDict, total=False):
        key "location": str
        key "properties": Required[DeploymentWhatIfProperties]
        location: str
        properties: DeploymentWhatIfProperties


    class azure.mgmt.resource.deployments.types.DeploymentWhatIfProperties(DeploymentProperties):
        key "debugSetting": ForwardRef('DebugSetting', module='types')
        key "expressionEvaluationOptions": ForwardRef('ExpressionEvaluationOptions', module='types')
        key "mode": Required[Union[str, DeploymentMode]]
        key "onErrorDeployment": ForwardRef('OnErrorDeployment', module='types')
        key "parametersLink": ForwardRef('ParametersLink', module='types')
        key "template": Any
        key "templateLink": ForwardRef('TemplateLink', module='types')
        key "validationLevel": Union[str, ValidationLevel]
        key "whatIfSettings": ForwardRef('DeploymentWhatIfSettings', module='types')
        debug_setting: DebugSetting
        expression_evaluation_options: ExpressionEvaluationOptions
        extensionConfigs: dict[str, dict[str, DeploymentExtensionConfigItem]]
        extension_configs: dict[str, dict[str, DeploymentExtensionConfigItem]]
        externalInputDefinitions: dict[str, DeploymentExternalInputDefinition]
        externalInputs: dict[str, DeploymentExternalInput]
        external_input_definitions: dict[str, DeploymentExternalInputDefinition]
        external_inputs: dict[str, DeploymentExternalInput]
        mode: Union[str, DeploymentMode]
        on_error_deployment: OnErrorDeployment
        parameters: dict[str, DeploymentParameter]
        parameters_link: ParametersLink
        template: Any
        template_link: TemplateLink
        validation_level: Union[str, ValidationLevel]
        what_if_settings: DeploymentWhatIfSettings


    class azure.mgmt.resource.deployments.types.DeploymentWhatIfSettings(TypedDict, total=False):
        key "resultFormat": Union[str, WhatIfResultFormat]
        result_format: Union[str, WhatIfResultFormat]


    class azure.mgmt.resource.deployments.types.ExpressionEvaluationOptions(TypedDict, total=False):
        key "scope": Union[str, ExpressionEvaluationOptionsScopeType]
        scope: Union[str, ExpressionEvaluationOptionsScopeType]


    class azure.mgmt.resource.deployments.types.KeyVaultParameterReference(TypedDict, total=False):
        key "keyVault": Required[KeyVaultReference]
        key "secretName": Required[str]
        key "secretVersion": str
        key_vault: KeyVaultReference
        secret_name: str
        secret_version: str


    class azure.mgmt.resource.deployments.types.KeyVaultReference(TypedDict, total=False):
        key "id": Required[str]
        id: str


    class azure.mgmt.resource.deployments.types.OnErrorDeployment(TypedDict, total=False):
        key "deploymentName": str
        key "type": Union[str, OnErrorDeploymentType]
        deployment_name: str
        type: Union[str, OnErrorDeploymentType]


    class azure.mgmt.resource.deployments.types.ParametersLink(TypedDict, total=False):
        key "contentVersion": str
        key "uri": Required[str]
        content_version: str
        uri: str


    class azure.mgmt.resource.deployments.types.ScopedDeployment(TypedDict, total=False):
        key "location": Required[str]
        key "properties": Required[DeploymentProperties]
        location: str
        properties: DeploymentProperties
        tags: dict[str, str]


    class azure.mgmt.resource.deployments.types.ScopedDeploymentWhatIf(TypedDict, total=False):
        key "location": Required[str]
        key "properties": Required[DeploymentWhatIfProperties]
        location: str
        properties: DeploymentWhatIfProperties


    class azure.mgmt.resource.deployments.types.TemplateLink(TypedDict, total=False):
        key "contentVersion": str
        key "id": str
        key "queryString": str
        key "relativePath": str
        key "uri": str
        content_version: str
        id: str
        query_string: str
        relative_path: str
        uri: str


    class azure.mgmt.resource.deployments.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        client_id: str
        principal_id: str


```