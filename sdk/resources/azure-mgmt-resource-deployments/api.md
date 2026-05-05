```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


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
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...


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
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...


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
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[DeploymentOperation]: ...

        @distributed_trace
        def list_at_management_group_scope(
                self, 
                group_id: str, 
                deployment_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[DeploymentOperation]: ...

        @distributed_trace
        def list_at_scope(
                self, 
                scope: str, 
                deployment_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[DeploymentOperation]: ...

        @distributed_trace
        def list_at_subscription_scope(
                self, 
                deployment_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[DeploymentOperation]: ...

        @distributed_trace
        def list_at_tenant_scope(
                self, 
                deployment_name: str, 
                top: Optional[int] = None, 
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
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WhatIfOperationResult]: ...

        @distributed_trace_async
        async def calculate_template_hash(
                self, 
                template: JSON, 
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
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[DeploymentExtended]: ...

        @distributed_trace
        def list_at_scope(
                self, 
                scope: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[DeploymentExtended]: ...

        @distributed_trace
        def list_at_subscription_scope(
                self, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[DeploymentExtended]: ...

        @distributed_trace
        def list_at_tenant_scope(
                self, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[DeploymentExtended]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[DeploymentExtended]: ...


namespace azure.mgmt.resource.deployments.models

    class azure.mgmt.resource.deployments.models.Alias(Model):
        default_metadata: AliasPathMetadata
        default_path: str
        default_pattern: AliasPattern
        name: str
        paths: list[AliasPath]
        type: Union[str, AliasType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                default_path: Optional[str] = ..., 
                default_pattern: Optional[AliasPattern] = ..., 
                name: Optional[str] = ..., 
                paths: Optional[List[AliasPath]] = ..., 
                type: Optional[Union[str, AliasType]] = ..., 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.AliasPath(Model):
        api_versions: list[str]
        metadata: AliasPathMetadata
        path: str
        pattern: AliasPattern

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                api_versions: Optional[List[str]] = ..., 
                path: Optional[str] = ..., 
                pattern: Optional[AliasPattern] = ..., 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.AliasPathAttributes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MODIFIABLE = "Modifiable"
        NONE = "None"


    class azure.mgmt.resource.deployments.models.AliasPathMetadata(Model):
        attributes: Union[str, AliasPathAttributes]
        type: Union[str, AliasPathTokenType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.AliasPathTokenType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANY = "Any"
        ARRAY = "Array"
        BOOLEAN = "Boolean"
        INTEGER = "Integer"
        NOT_SPECIFIED = "NotSpecified"
        NUMBER = "Number"
        OBJECT = "Object"
        STRING = "String"


    class azure.mgmt.resource.deployments.models.AliasPattern(Model):
        phrase: str
        type: Union[str, AliasPatternType]
        variable: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                phrase: Optional[str] = ..., 
                type: Optional[Union[str, AliasPatternType]] = ..., 
                variable: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.AliasPatternType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXTRACT = "Extract"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.resource.deployments.models.AliasType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MASK = "Mask"
        NOT_SPECIFIED = "NotSpecified"
        PLAIN_TEXT = "PlainText"


    class azure.mgmt.resource.deployments.models.ApiProfile(Model):
        api_version: str
        profile_version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.BasicDependency(Model):
        id: str
        resource_name: str
        resource_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                resource_name: Optional[str] = ..., 
                resource_type: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.ChangeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATE = "Create"
        DELETE = "Delete"
        DEPLOY = "Deploy"
        IGNORE = "Ignore"
        MODIFY = "Modify"
        NO_CHANGE = "NoChange"
        UNSUPPORTED = "Unsupported"


    class azure.mgmt.resource.deployments.models.DebugSetting(Model):
        detail_level: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                detail_level: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.Dependency(Model):
        depends_on: list[BasicDependency]
        id: str
        resource_name: str
        resource_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                depends_on: Optional[List[BasicDependency]] = ..., 
                id: Optional[str] = ..., 
                resource_name: Optional[str] = ..., 
                resource_type: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.Deployment(Model):
        identity: DeploymentIdentity
        location: str
        properties: DeploymentProperties
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[DeploymentIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: DeploymentProperties, 
                tags: Optional[Dict[str, str]] = ..., 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.DeploymentDiagnosticsDefinition(Model):
        additional_info: list[ErrorAdditionalInfo]
        code: str
        level: Union[str, Level]
        message: str
        target: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.DeploymentExportResult(Model):
        template: JSON

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                template: Optional[JSON] = ..., 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.DeploymentExtended(Model):
        id: str
        location: str
        name: str
        properties: DeploymentPropertiesExtended
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[DeploymentPropertiesExtended] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.DeploymentExtendedFilter(Model):
        provisioning_state: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                provisioning_state: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.DeploymentExtensionConfigItem(Model):
        key_vault_reference: KeyVaultParameterReference
        type: Union[str, ExtensionConfigPropertyType]
        value: any

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key_vault_reference: Optional[KeyVaultParameterReference] = ..., 
                value: Optional[Any] = ..., 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.DeploymentExtensionDefinition(Model):
        alias: str
        config: dict[str, DeploymentExtensionConfigItem]
        config_id: str
        name: str
        version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.DeploymentExternalInput(Model):
        value: any

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Any, 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.DeploymentExternalInputDefinition(Model):
        config: any
        kind: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                config: Optional[Any] = ..., 
                kind: str, 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.DeploymentIdentity(Model):
        type: Union[str, DeploymentIdentityType]
        user_assigned_identities: dict[str, UserAssignedIdentity]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Union[str, DeploymentIdentityType], 
                user_assigned_identities: Optional[Dict[str, UserAssignedIdentity]] = ..., 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.DeploymentIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.resource.deployments.models.DeploymentListResult(Model):
        next_link: str
        value: list[DeploymentExtended]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[DeploymentExtended]] = ..., 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.DeploymentMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETE = "Complete"
        INCREMENTAL = "Incremental"


    class azure.mgmt.resource.deployments.models.DeploymentOperation(Model):
        id: str
        operation_id: str
        properties: DeploymentOperationProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[DeploymentOperationProperties] = ..., 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.DeploymentOperationProperties(Model):
        duration: str
        provisioning_operation: Union[str, ProvisioningOperation]
        provisioning_state: str
        request: HttpMessage
        response: HttpMessage
        service_request_id: str
        status_code: str
        status_message: StatusMessage
        target_resource: TargetResource
        timestamp: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.DeploymentOperationsListResult(Model):
        next_link: str
        value: list[DeploymentOperation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[DeploymentOperation]] = ..., 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.DeploymentParameter(Model):
        expression: str
        reference: KeyVaultParameterReference
        value: any

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                expression: Optional[str] = ..., 
                reference: Optional[KeyVaultParameterReference] = ..., 
                value: Optional[Any] = ..., 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.DeploymentProperties(Model):
        debug_setting: DebugSetting
        expression_evaluation_options: ExpressionEvaluationOptions
        extension_configs: dict[str, dict[str, DeploymentExtensionConfigItem]]
        external_input_definitions: dict[str, DeploymentExternalInputDefinition]
        external_inputs: dict[str, DeploymentExternalInput]
        mode: Union[str, DeploymentMode]
        on_error_deployment: OnErrorDeployment
        parameters: dict[str, DeploymentParameter]
        parameters_link: ParametersLink
        template: JSON
        template_link: TemplateLink
        validation_level: Union[str, ValidationLevel]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                debug_setting: Optional[DebugSetting] = ..., 
                expression_evaluation_options: Optional[ExpressionEvaluationOptions] = ..., 
                extension_configs: Optional[Dict[str, Dict[str, DeploymentExtensionConfigItem]]] = ..., 
                external_input_definitions: Optional[Dict[str, DeploymentExternalInputDefinition]] = ..., 
                external_inputs: Optional[Dict[str, DeploymentExternalInput]] = ..., 
                mode: Union[str, DeploymentMode], 
                on_error_deployment: Optional[OnErrorDeployment] = ..., 
                parameters: Optional[Dict[str, DeploymentParameter]] = ..., 
                parameters_link: Optional[ParametersLink] = ..., 
                template: Optional[JSON] = ..., 
                template_link: Optional[TemplateLink] = ..., 
                validation_level: Optional[Union[str, ValidationLevel]] = ..., 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.DeploymentPropertiesExtended(Model):
        correlation_id: str
        debug_setting: DebugSetting
        dependencies: list[Dependency]
        diagnostics: list[DeploymentDiagnosticsDefinition]
        duration: str
        error: ErrorResponse
        extensions: list[DeploymentExtensionDefinition]
        mode: Union[str, DeploymentMode]
        on_error_deployment: OnErrorDeploymentExtended
        output_resources: list[ResourceReference]
        outputs: JSON
        parameters: JSON
        parameters_link: ParametersLink
        providers: list[Provider]
        provisioning_state: Union[str, ProvisioningState]
        template_hash: str
        template_link: TemplateLink
        timestamp: datetime
        validated_resources: list[ResourceReference]
        validation_level: Union[str, ValidationLevel]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                validation_level: Optional[Union[str, ValidationLevel]] = ..., 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.DeploymentValidateResult(Model):
        error: ErrorResponse
        id: str
        name: str
        properties: DeploymentPropertiesExtended
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[DeploymentPropertiesExtended] = ..., 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.DeploymentWhatIf(Model):
        location: str
        properties: DeploymentWhatIfProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: DeploymentWhatIfProperties, 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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
        template: JSON
        template_link: TemplateLink
        validation_level: Union[str, ValidationLevel]
        what_if_settings: DeploymentWhatIfSettings

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                debug_setting: Optional[DebugSetting] = ..., 
                expression_evaluation_options: Optional[ExpressionEvaluationOptions] = ..., 
                extension_configs: Optional[Dict[str, Dict[str, DeploymentExtensionConfigItem]]] = ..., 
                external_input_definitions: Optional[Dict[str, DeploymentExternalInputDefinition]] = ..., 
                external_inputs: Optional[Dict[str, DeploymentExternalInput]] = ..., 
                mode: Union[str, DeploymentMode], 
                on_error_deployment: Optional[OnErrorDeployment] = ..., 
                parameters: Optional[Dict[str, DeploymentParameter]] = ..., 
                parameters_link: Optional[ParametersLink] = ..., 
                template: Optional[JSON] = ..., 
                template_link: Optional[TemplateLink] = ..., 
                validation_level: Optional[Union[str, ValidationLevel]] = ..., 
                what_if_settings: Optional[DeploymentWhatIfSettings] = ..., 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.DeploymentWhatIfSettings(Model):
        result_format: Union[str, WhatIfResultFormat]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                result_format: Optional[Union[str, WhatIfResultFormat]] = ..., 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.ErrorAdditionalInfo(Model):
        info: JSON
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.ErrorResponse(Model):
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorResponse]
        message: str
        target: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.ExpressionEvaluationOptions(Model):
        scope: Union[str, ExpressionEvaluationOptionsScopeType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                scope: Optional[Union[str, ExpressionEvaluationOptionsScopeType]] = ..., 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.ExpressionEvaluationOptionsScopeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INNER = "Inner"
        NOT_SPECIFIED = "NotSpecified"
        OUTER = "Outer"


    class azure.mgmt.resource.deployments.models.ExtensionConfigPropertyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARRAY = "Array"
        BOOL = "Bool"
        INT = "Int"
        INT_ENUM = "Int"
        OBJECT = "Object"
        SECURE_OBJECT = "SecureObject"
        SECURE_STRING = "SecureString"
        STRING = "String"


    class azure.mgmt.resource.deployments.models.HttpMessage(Model):
        content: JSON

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                content: Optional[JSON] = ..., 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.KeyVaultParameterReference(Model):
        key_vault: KeyVaultReference
        secret_name: str
        secret_version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key_vault: KeyVaultReference, 
                secret_name: str, 
                secret_version: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.KeyVaultReference(Model):
        id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: str, 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.Level(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        INFO = "Info"
        WARNING = "Warning"


    class azure.mgmt.resource.deployments.models.OnErrorDeployment(Model):
        deployment_name: str
        type: Union[str, OnErrorDeploymentType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                deployment_name: Optional[str] = ..., 
                type: Optional[Union[str, OnErrorDeploymentType]] = ..., 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.OnErrorDeploymentExtended(Model):
        deployment_name: str
        provisioning_state: str
        type: Union[str, OnErrorDeploymentType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                deployment_name: Optional[str] = ..., 
                type: Optional[Union[str, OnErrorDeploymentType]] = ..., 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.OnErrorDeploymentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LAST_SUCCESSFUL = "LastSuccessful"
        SPECIFIC_DEPLOYMENT = "SpecificDeployment"


    class azure.mgmt.resource.deployments.models.ParametersLink(Model):
        content_version: str
        uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                content_version: Optional[str] = ..., 
                uri: str, 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.PropertyChangeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARRAY = "Array"
        CREATE = "Create"
        DELETE = "Delete"
        MODIFY = "Modify"
        NO_EFFECT = "NoEffect"


    class azure.mgmt.resource.deployments.models.Provider(Model):
        id: str
        namespace: str
        provider_authorization_consent_state: Union[str, ProviderAuthorizationConsentState]
        registration_policy: str
        registration_state: str
        resource_types: list[ProviderResourceType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                namespace: Optional[str] = ..., 
                provider_authorization_consent_state: Optional[Union[str, ProviderAuthorizationConsentState]] = ..., 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.ProviderAuthorizationConsentState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONSENTED = "Consented"
        NOT_REQUIRED = "NotRequired"
        NOT_SPECIFIED = "NotSpecified"
        REQUIRED = "Required"


    class azure.mgmt.resource.deployments.models.ProviderExtendedLocation(Model):
        extended_locations: list[str]
        location: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                extended_locations: Optional[List[str]] = ..., 
                location: Optional[str] = ..., 
                type: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.ProviderResourceType(Model):
        aliases: list[Alias]
        api_profiles: list[ApiProfile]
        api_versions: list[str]
        capabilities: str
        default_api_version: str
        location_mappings: list[ProviderExtendedLocation]
        locations: list[str]
        properties: dict[str, str]
        resource_type: str
        zone_mappings: list[ZoneMapping]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                aliases: Optional[List[Alias]] = ..., 
                api_versions: Optional[List[str]] = ..., 
                capabilities: Optional[str] = ..., 
                location_mappings: Optional[List[ProviderExtendedLocation]] = ..., 
                locations: Optional[List[str]] = ..., 
                properties: Optional[Dict[str, str]] = ..., 
                resource_type: Optional[str] = ..., 
                zone_mappings: Optional[List[ZoneMapping]] = ..., 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.ResourceProviderOperationDisplayProperties(Model):
        description: str
        operation: str
        provider: str
        publisher: str
        resource: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                publisher: Optional[str] = ..., 
                resource: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.ResourceReference(Model):
        api_version: str
        extension: DeploymentExtensionDefinition
        id: str
        identifiers: JSON
        resource_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.ScopedDeployment(Model):
        location: str
        properties: DeploymentProperties
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
                properties: DeploymentProperties, 
                tags: Optional[Dict[str, str]] = ..., 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.ScopedDeploymentWhatIf(Model):
        location: str
        properties: DeploymentWhatIfProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
                properties: DeploymentWhatIfProperties, 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.StatusMessage(Model):
        error: ErrorResponse
        status: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorResponse] = ..., 
                status: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.SubResource(Model):
        id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.TargetResource(Model):
        api_version: str
        extension: DeploymentExtensionDefinition
        id: str
        identifiers: JSON
        resource_name: str
        resource_type: str
        symbolic_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                api_version: Optional[str] = ..., 
                extension: Optional[DeploymentExtensionDefinition] = ..., 
                id: Optional[str] = ..., 
                identifiers: Optional[JSON] = ..., 
                resource_name: Optional[str] = ..., 
                resource_type: Optional[str] = ..., 
                symbolic_name: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.TemplateHashResult(Model):
        minified_template: str
        template_hash: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                minified_template: Optional[str] = ..., 
                template_hash: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.TemplateLink(Model):
        content_version: str
        id: str
        query_string: str
        relative_path: str
        uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                content_version: Optional[str] = ..., 
                id: Optional[str] = ..., 
                query_string: Optional[str] = ..., 
                relative_path: Optional[str] = ..., 
                uri: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.UserAssignedIdentity(Model):
        client_id: str
        principal_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.ValidationLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PROVIDER = "Provider"
        PROVIDER_NO_RBAC = "ProviderNoRbac"
        TEMPLATE = "Template"


    class azure.mgmt.resource.deployments.models.WhatIfChange(Model):
        after: JSON
        before: JSON
        change_type: Union[str, ChangeType]
        delta: list[WhatIfPropertyChange]
        deployment_id: str
        extension: DeploymentExtensionDefinition
        identifiers: JSON
        resource_id: str
        symbolic_name: str
        unsupported_reason: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                after: Optional[JSON] = ..., 
                before: Optional[JSON] = ..., 
                change_type: Union[str, ChangeType], 
                delta: Optional[List[WhatIfPropertyChange]] = ..., 
                deployment_id: Optional[str] = ..., 
                extension: Optional[DeploymentExtensionDefinition] = ..., 
                identifiers: Optional[JSON] = ..., 
                resource_id: Optional[str] = ..., 
                symbolic_name: Optional[str] = ..., 
                unsupported_reason: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.WhatIfOperationResult(Model):
        changes: list[WhatIfChange]
        diagnostics: list[DeploymentDiagnosticsDefinition]
        error: ErrorResponse
        potential_changes: list[WhatIfChange]
        status: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                changes: Optional[List[WhatIfChange]] = ..., 
                error: Optional[ErrorResponse] = ..., 
                potential_changes: Optional[List[WhatIfChange]] = ..., 
                status: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.WhatIfPropertyChange(Model):
        after: JSON
        before: JSON
        children: list[WhatIfPropertyChange]
        path: str
        property_change_type: Union[str, PropertyChangeType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                after: Optional[JSON] = ..., 
                before: Optional[JSON] = ..., 
                children: Optional[List[WhatIfPropertyChange]] = ..., 
                path: str, 
                property_change_type: Union[str, PropertyChangeType], 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.mgmt.resource.deployments.models.WhatIfResultFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FULL_RESOURCE_PAYLOADS = "FullResourcePayloads"
        RESOURCE_ID_ONLY = "ResourceIdOnly"


    class azure.mgmt.resource.deployments.models.ZoneMapping(Model):
        location: str
        zones: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                zones: Optional[List[str]] = ..., 
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
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[DeploymentOperation]: ...

        @distributed_trace
        def list_at_management_group_scope(
                self, 
                group_id: str, 
                deployment_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[DeploymentOperation]: ...

        @distributed_trace
        def list_at_scope(
                self, 
                scope: str, 
                deployment_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[DeploymentOperation]: ...

        @distributed_trace
        def list_at_subscription_scope(
                self, 
                deployment_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[DeploymentOperation]: ...

        @distributed_trace
        def list_at_tenant_scope(
                self, 
                deployment_name: str, 
                top: Optional[int] = None, 
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
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WhatIfOperationResult]: ...

        @distributed_trace
        def calculate_template_hash(
                self, 
                template: JSON, 
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
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[DeploymentExtended]: ...

        @distributed_trace
        def list_at_scope(
                self, 
                scope: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[DeploymentExtended]: ...

        @distributed_trace
        def list_at_subscription_scope(
                self, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[DeploymentExtended]: ...

        @distributed_trace
        def list_at_tenant_scope(
                self, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[DeploymentExtended]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[DeploymentExtended]: ...


```