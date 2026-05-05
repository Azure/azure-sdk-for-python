```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.resource.policy

    class azure.mgmt.resource.policy.PolicyClient: implements ContextManager 
        data_policy_manifests: DataPolicyManifestsOperations
        policy_assignments: PolicyAssignmentsOperations
        policy_definition_versions: PolicyDefinitionVersionsOperations
        policy_definitions: PolicyDefinitionsOperations
        policy_set_definition_versions: PolicySetDefinitionVersionsOperations
        policy_set_definitions: PolicySetDefinitionsOperations
        policy_tokens: PolicyTokensOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                cloud_setting: Optional[AzureClouds] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...


namespace azure.mgmt.resource.policy.aio

    class azure.mgmt.resource.policy.aio.PolicyClient: implements AsyncContextManager 
        data_policy_manifests: DataPolicyManifestsOperations
        policy_assignments: PolicyAssignmentsOperations
        policy_definition_versions: PolicyDefinitionVersionsOperations
        policy_definitions: PolicyDefinitionsOperations
        policy_set_definition_versions: PolicySetDefinitionVersionsOperations
        policy_set_definitions: PolicySetDefinitionsOperations
        policy_tokens: PolicyTokensOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                cloud_setting: Optional[AzureClouds] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...


namespace azure.mgmt.resource.policy.aio.operations

    class azure.mgmt.resource.policy.aio.operations.DataPolicyManifestsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_by_policy_mode(
                self, 
                policy_mode: str, 
                **kwargs: Any
            ) -> DataPolicyManifest: ...

        @distributed_trace
        def list(
                self, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[DataPolicyManifest]: ...


    class azure.mgmt.resource.policy.aio.operations.PolicyAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                scope: str, 
                policy_assignment_name: str, 
                parameters: PolicyAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @overload
        async def create(
                self, 
                scope: str, 
                policy_assignment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @overload
        async def create_by_id(
                self, 
                policy_assignment_id: str, 
                parameters: PolicyAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @overload
        async def create_by_id(
                self, 
                policy_assignment_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @distributed_trace_async
        async def delete(
                self, 
                scope: str, 
                policy_assignment_name: str, 
                **kwargs: Any
            ) -> Optional[PolicyAssignment]: ...

        @distributed_trace_async
        async def delete_by_id(
                self, 
                policy_assignment_id: str, 
                **kwargs: Any
            ) -> Optional[PolicyAssignment]: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                policy_assignment_name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @distributed_trace_async
        async def get_by_id(
                self, 
                policy_assignment_id: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @distributed_trace
        def list(
                self, 
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyAssignment]: ...

        @distributed_trace
        def list_for_management_group(
                self, 
                management_group_id: str, 
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyAssignment]: ...

        @distributed_trace
        def list_for_resource(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_path: str, 
                resource_type: str, 
                resource_name: str, 
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyAssignment]: ...

        @distributed_trace
        def list_for_resource_group(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyAssignment]: ...

        @overload
        async def update(
                self, 
                scope: str, 
                policy_assignment_name: str, 
                parameters: PolicyAssignmentUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @overload
        async def update(
                self, 
                scope: str, 
                policy_assignment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @overload
        async def update_by_id(
                self, 
                policy_assignment_id: str, 
                parameters: PolicyAssignmentUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @overload
        async def update_by_id(
                self, 
                policy_assignment_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyAssignment: ...


    class azure.mgmt.resource.policy.aio.operations.PolicyDefinitionVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                policy_definition_name: str, 
                policy_definition_version: str, 
                parameters: PolicyDefinitionVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyDefinitionVersion: ...

        @overload
        async def create_or_update(
                self, 
                policy_definition_name: str, 
                policy_definition_version: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyDefinitionVersion: ...

        @overload
        async def create_or_update_at_management_group(
                self, 
                management_group_name: str, 
                policy_definition_name: str, 
                policy_definition_version: str, 
                parameters: PolicyDefinitionVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyDefinitionVersion: ...

        @overload
        async def create_or_update_at_management_group(
                self, 
                management_group_name: str, 
                policy_definition_name: str, 
                policy_definition_version: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyDefinitionVersion: ...

        @distributed_trace_async
        async def delete(
                self, 
                policy_definition_name: str, 
                policy_definition_version: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_at_management_group(
                self, 
                management_group_name: str, 
                policy_definition_name: str, 
                policy_definition_version: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                policy_definition_name: str, 
                policy_definition_version: str, 
                **kwargs: Any
            ) -> PolicyDefinitionVersion: ...

        @distributed_trace_async
        async def get_at_management_group(
                self, 
                management_group_name: str, 
                policy_definition_name: str, 
                policy_definition_version: str, 
                **kwargs: Any
            ) -> PolicyDefinitionVersion: ...

        @distributed_trace_async
        async def get_built_in(
                self, 
                policy_definition_name: str, 
                policy_definition_version: str, 
                **kwargs: Any
            ) -> PolicyDefinitionVersion: ...

        @distributed_trace
        def list(
                self, 
                policy_definition_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyDefinitionVersion]: ...

        @distributed_trace_async
        async def list_all(self, **kwargs: Any) -> PolicyDefinitionVersionListResult: ...

        @distributed_trace_async
        async def list_all_at_management_group(
                self, 
                management_group_name: str, 
                **kwargs: Any
            ) -> PolicyDefinitionVersionListResult: ...

        @distributed_trace_async
        async def list_all_builtins(self, **kwargs: Any) -> PolicyDefinitionVersionListResult: ...

        @distributed_trace
        def list_built_in(
                self, 
                policy_definition_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyDefinitionVersion]: ...

        @distributed_trace
        def list_by_management_group(
                self, 
                management_group_name: str, 
                policy_definition_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyDefinitionVersion]: ...


    class azure.mgmt.resource.policy.aio.operations.PolicyDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                policy_definition_name: str, 
                parameters: PolicyDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyDefinition: ...

        @overload
        async def create_or_update(
                self, 
                policy_definition_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyDefinition: ...

        @overload
        async def create_or_update_at_management_group(
                self, 
                management_group_id: str, 
                policy_definition_name: str, 
                parameters: PolicyDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyDefinition: ...

        @overload
        async def create_or_update_at_management_group(
                self, 
                management_group_id: str, 
                policy_definition_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyDefinition: ...

        @distributed_trace_async
        async def delete(
                self, 
                policy_definition_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_at_management_group(
                self, 
                management_group_id: str, 
                policy_definition_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                policy_definition_name: str, 
                **kwargs: Any
            ) -> PolicyDefinition: ...

        @distributed_trace_async
        async def get_at_management_group(
                self, 
                management_group_id: str, 
                policy_definition_name: str, 
                **kwargs: Any
            ) -> PolicyDefinition: ...

        @distributed_trace_async
        async def get_built_in(
                self, 
                policy_definition_name: str, 
                **kwargs: Any
            ) -> PolicyDefinition: ...

        @distributed_trace
        def list(
                self, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyDefinition]: ...

        @distributed_trace
        def list_built_in(
                self, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyDefinition]: ...

        @distributed_trace
        def list_by_management_group(
                self, 
                management_group_id: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyDefinition]: ...


    class azure.mgmt.resource.policy.aio.operations.PolicySetDefinitionVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                policy_set_definition_name: str, 
                policy_definition_version: str, 
                parameters: PolicySetDefinitionVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicySetDefinitionVersion: ...

        @overload
        async def create_or_update(
                self, 
                policy_set_definition_name: str, 
                policy_definition_version: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicySetDefinitionVersion: ...

        @overload
        async def create_or_update_at_management_group(
                self, 
                management_group_name: str, 
                policy_set_definition_name: str, 
                policy_definition_version: str, 
                parameters: PolicySetDefinitionVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicySetDefinitionVersion: ...

        @overload
        async def create_or_update_at_management_group(
                self, 
                management_group_name: str, 
                policy_set_definition_name: str, 
                policy_definition_version: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicySetDefinitionVersion: ...

        @distributed_trace_async
        async def delete(
                self, 
                policy_set_definition_name: str, 
                policy_definition_version: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_at_management_group(
                self, 
                management_group_name: str, 
                policy_set_definition_name: str, 
                policy_definition_version: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                policy_set_definition_name: str, 
                policy_definition_version: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> PolicySetDefinitionVersion: ...

        @distributed_trace_async
        async def get_at_management_group(
                self, 
                management_group_name: str, 
                policy_set_definition_name: str, 
                policy_definition_version: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> PolicySetDefinitionVersion: ...

        @distributed_trace_async
        async def get_built_in(
                self, 
                policy_set_definition_name: str, 
                policy_definition_version: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> PolicySetDefinitionVersion: ...

        @distributed_trace
        def list(
                self, 
                policy_set_definition_name: str, 
                expand: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicySetDefinitionVersion]: ...

        @distributed_trace_async
        async def list_all(self, **kwargs: Any) -> PolicySetDefinitionVersionListResult: ...

        @distributed_trace_async
        async def list_all_at_management_group(
                self, 
                management_group_name: str, 
                **kwargs: Any
            ) -> PolicySetDefinitionVersionListResult: ...

        @distributed_trace_async
        async def list_all_builtins(self, **kwargs: Any) -> PolicySetDefinitionVersionListResult: ...

        @distributed_trace
        def list_built_in(
                self, 
                policy_set_definition_name: str, 
                expand: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicySetDefinitionVersion]: ...

        @distributed_trace
        def list_by_management_group(
                self, 
                management_group_name: str, 
                policy_set_definition_name: str, 
                expand: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicySetDefinitionVersion]: ...


    class azure.mgmt.resource.policy.aio.operations.PolicySetDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                policy_set_definition_name: str, 
                parameters: PolicySetDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicySetDefinition: ...

        @overload
        async def create_or_update(
                self, 
                policy_set_definition_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicySetDefinition: ...

        @overload
        async def create_or_update_at_management_group(
                self, 
                management_group_id: str, 
                policy_set_definition_name: str, 
                parameters: PolicySetDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicySetDefinition: ...

        @overload
        async def create_or_update_at_management_group(
                self, 
                management_group_id: str, 
                policy_set_definition_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicySetDefinition: ...

        @distributed_trace_async
        async def delete(
                self, 
                policy_set_definition_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_at_management_group(
                self, 
                management_group_id: str, 
                policy_set_definition_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                policy_set_definition_name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> PolicySetDefinition: ...

        @distributed_trace_async
        async def get_at_management_group(
                self, 
                management_group_id: str, 
                policy_set_definition_name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> PolicySetDefinition: ...

        @distributed_trace_async
        async def get_built_in(
                self, 
                policy_set_definition_name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> PolicySetDefinition: ...

        @distributed_trace
        def list(
                self, 
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicySetDefinition]: ...

        @distributed_trace
        def list_built_in(
                self, 
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicySetDefinition]: ...

        @distributed_trace
        def list_by_management_group(
                self, 
                management_group_id: str, 
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicySetDefinition]: ...


    class azure.mgmt.resource.policy.aio.operations.PolicyTokensOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def acquire(
                self, 
                parameters: PolicyTokenRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyTokenResponse: ...

        @overload
        async def acquire(
                self, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyTokenResponse: ...

        @overload
        async def acquire_at_management_group(
                self, 
                management_group_name: str, 
                parameters: PolicyTokenRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyTokenResponse: ...

        @overload
        async def acquire_at_management_group(
                self, 
                management_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyTokenResponse: ...


namespace azure.mgmt.resource.policy.models

    class azure.mgmt.resource.policy.models.Alias(Model):
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
                paths: Optional[list[AliasPath]] = ..., 
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


    class azure.mgmt.resource.policy.models.AliasPath(Model):
        api_versions: list[str]
        metadata: AliasPathMetadata
        path: str
        pattern: AliasPattern

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                api_versions: Optional[list[str]] = ..., 
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


    class azure.mgmt.resource.policy.models.AliasPathAttributes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MODIFIABLE = "Modifiable"
        NONE = "None"


    class azure.mgmt.resource.policy.models.AliasPathMetadata(Model):
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


    class azure.mgmt.resource.policy.models.AliasPathTokenType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANY = "Any"
        ARRAY = "Array"
        BOOLEAN = "Boolean"
        INTEGER = "Integer"
        NOT_SPECIFIED = "NotSpecified"
        NUMBER = "Number"
        OBJECT = "Object"
        STRING = "String"


    class azure.mgmt.resource.policy.models.AliasPattern(Model):
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


    class azure.mgmt.resource.policy.models.AliasPatternType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXTRACT = "Extract"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.resource.policy.models.AliasType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MASK = "Mask"
        NOT_SPECIFIED = "NotSpecified"
        PLAIN_TEXT = "PlainText"


    class azure.mgmt.resource.policy.models.AssignmentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM = "Custom"
        NOT_SPECIFIED = "NotSpecified"
        SYSTEM = "System"
        SYSTEM_HIDDEN = "SystemHidden"


    class azure.mgmt.resource.policy.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.resource.policy.models.DataEffect(Model):
        details_schema: JSON
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                details_schema: Optional[JSON] = ..., 
                name: Optional[str] = ..., 
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


    class azure.mgmt.resource.policy.models.DataManifestCustomResourceFunctionDefinition(Model):
        allow_custom_properties: bool
        default_properties: list[str]
        fully_qualified_resource_type: str
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allow_custom_properties: Optional[bool] = ..., 
                default_properties: Optional[list[str]] = ..., 
                fully_qualified_resource_type: Optional[str] = ..., 
                name: Optional[str] = ..., 
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


    class azure.mgmt.resource.policy.models.DataPolicyManifest(Model):
        custom: list[DataManifestCustomResourceFunctionDefinition]
        effects: list[DataEffect]
        field_values: list[str]
        id: str
        is_built_in_only: bool
        name: str
        namespaces: list[str]
        policy_mode: str
        resource_type_aliases: list[ResourceTypeAliases]
        standard: list[str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                custom: Optional[list[DataManifestCustomResourceFunctionDefinition]] = ..., 
                effects: Optional[list[DataEffect]] = ..., 
                field_values: Optional[list[str]] = ..., 
                is_built_in_only: Optional[bool] = ..., 
                namespaces: Optional[list[str]] = ..., 
                policy_mode: Optional[str] = ..., 
                resource_type_aliases: Optional[list[ResourceTypeAliases]] = ..., 
                standard: Optional[list[str]] = ..., 
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


    class azure.mgmt.resource.policy.models.DataPolicyManifestListResult(Model):
        next_link: str
        value: list[DataPolicyManifest]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[DataPolicyManifest]] = ..., 
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


    class azure.mgmt.resource.policy.models.EnforcementMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        DO_NOT_ENFORCE = "DoNotEnforce"
        ENROLL = "Enroll"


    class azure.mgmt.resource.policy.models.ErrorAdditionalInfo(Model):
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


    class azure.mgmt.resource.policy.models.ErrorDetail(Model):
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


    class azure.mgmt.resource.policy.models.ErrorResponse(Model):
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


    class azure.mgmt.resource.policy.models.ExternalEndpointResult(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.resource.policy.models.ExternalEvaluationEndpointInvocationResult(Model):
        claims: any
        expiration: datetime
        message: str
        policy_info: PolicyLogInfo
        result: Union[str, ExternalEndpointResult]
        retry_after: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                claims: Optional[Any] = ..., 
                expiration: Optional[datetime] = ..., 
                message: Optional[str] = ..., 
                policy_info: Optional[PolicyLogInfo] = ..., 
                result: Optional[Union[str, ExternalEndpointResult]] = ..., 
                retry_after: Optional[datetime] = ..., 
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


    class azure.mgmt.resource.policy.models.ExternalEvaluationEndpointSettings(Model):
        details: any
        kind: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                details: Optional[Any] = ..., 
                kind: Optional[str] = ..., 
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


    class azure.mgmt.resource.policy.models.ExternalEvaluationEnforcementSettings(Model):
        endpoint_settings: ExternalEvaluationEndpointSettings
        missing_token_action: str
        result_lifespan: str
        role_definition_ids: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                endpoint_settings: Optional[ExternalEvaluationEndpointSettings] = ..., 
                missing_token_action: Optional[str] = ..., 
                result_lifespan: Optional[str] = ..., 
                role_definition_ids: Optional[list[str]] = ..., 
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


    class azure.mgmt.resource.policy.models.Identity(Model):
        principal_id: str
        tenant_id: str
        type: Union[str, ResourceIdentityType]
        user_assigned_identities: dict[str, UserAssignedIdentitiesValue]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ResourceIdentityType]] = ..., 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentitiesValue]] = ..., 
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


    class azure.mgmt.resource.policy.models.NonComplianceMessage(Model):
        message: str
        policy_definition_reference_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                message: str, 
                policy_definition_reference_id: Optional[str] = ..., 
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


    class azure.mgmt.resource.policy.models.Override(Model):
        kind: Union[str, OverrideKind]
        selectors: list[Selector]
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                kind: Optional[Union[str, OverrideKind]] = ..., 
                selectors: Optional[list[Selector]] = ..., 
                value: Optional[str] = ..., 
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


    class azure.mgmt.resource.policy.models.OverrideKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFINITION_VERSION = "definitionVersion"
        POLICY_EFFECT = "policyEffect"


    class azure.mgmt.resource.policy.models.ParameterDefinitionsValue(Model):
        allowed_values: list[any]
        default_value: any
        metadata: ParameterDefinitionsValueMetadata
        schema: any
        type: Union[str, ParameterType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allowed_values: Optional[list[Any]] = ..., 
                default_value: Optional[Any] = ..., 
                metadata: Optional[ParameterDefinitionsValueMetadata] = ..., 
                schema: Optional[Any] = ..., 
                type: Optional[Union[str, ParameterType]] = ..., 
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


    class azure.mgmt.resource.policy.models.ParameterDefinitionsValueMetadata(Model):
        additional_properties: dict[str, any]
        assign_permissions: bool
        description: str
        display_name: str
        strong_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[dict[str, Any]] = ..., 
                assign_permissions: Optional[bool] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                strong_type: Optional[str] = ..., 
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


    class azure.mgmt.resource.policy.models.ParameterType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARRAY = "Array"
        BOOLEAN = "Boolean"
        DATE_TIME = "DateTime"
        FLOAT = "Float"
        INTEGER = "Integer"
        OBJECT = "Object"
        STRING = "String"


    class azure.mgmt.resource.policy.models.ParameterValuesValue(Model):
        value: any

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
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


    class azure.mgmt.resource.policy.models.PolicyAssignment(ProxyResource):
        assignment_type: Union[str, AssignmentType]
        definition_version: str
        description: str
        display_name: str
        effective_definition_version: str
        enforcement_mode: Union[str, EnforcementMode]
        id: str
        identity: Identity
        instance_id: str
        latest_definition_version: str
        location: str
        metadata: any
        name: str
        non_compliance_messages: list[NonComplianceMessage]
        not_scopes: list[str]
        overrides: list[Override]
        parameters: dict[str, ParameterValuesValue]
        policy_definition_id: str
        resource_selectors: list[ResourceSelector]
        scope: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                assignment_type: Optional[Union[str, AssignmentType]] = ..., 
                definition_version: Optional[str] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                enforcement_mode: Union[str, EnforcementMode] = "Default", 
                identity: Optional[Identity] = ..., 
                location: Optional[str] = ..., 
                metadata: Optional[Any] = ..., 
                non_compliance_messages: Optional[list[NonComplianceMessage]] = ..., 
                not_scopes: Optional[list[str]] = ..., 
                overrides: Optional[list[Override]] = ..., 
                parameters: Optional[dict[str, ParameterValuesValue]] = ..., 
                policy_definition_id: Optional[str] = ..., 
                resource_selectors: Optional[list[ResourceSelector]] = ..., 
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


    class azure.mgmt.resource.policy.models.PolicyAssignmentListResult(Model):
        next_link: str
        value: list[PolicyAssignment]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[PolicyAssignment], 
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


    class azure.mgmt.resource.policy.models.PolicyAssignmentUpdate(Model):
        identity: Identity
        location: str
        overrides: list[Override]
        resource_selectors: list[ResourceSelector]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[Identity] = ..., 
                location: Optional[str] = ..., 
                overrides: Optional[list[Override]] = ..., 
                resource_selectors: Optional[list[ResourceSelector]] = ..., 
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


    class azure.mgmt.resource.policy.models.PolicyDefinition(ProxyResource):
        description: str
        display_name: str
        external_evaluation_enforcement_settings: ExternalEvaluationEnforcementSettings
        id: str
        metadata: any
        mode: str
        name: str
        parameters: dict[str, ParameterDefinitionsValue]
        policy_rule: any
        policy_type: Union[str, PolicyType]
        system_data: SystemData
        type: str
        version: str
        versions: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                external_evaluation_enforcement_settings: Optional[ExternalEvaluationEnforcementSettings] = ..., 
                metadata: Optional[Any] = ..., 
                mode: str = "Indexed", 
                parameters: Optional[dict[str, ParameterDefinitionsValue]] = ..., 
                policy_rule: Optional[Any] = ..., 
                policy_type: Optional[Union[str, PolicyType]] = ..., 
                version: Optional[str] = ..., 
                versions: Optional[list[str]] = ..., 
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


    class azure.mgmt.resource.policy.models.PolicyDefinitionGroup(Model):
        additional_metadata_id: str
        category: str
        description: str
        display_name: str
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_metadata_id: Optional[str] = ..., 
                category: Optional[str] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                name: str, 
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


    class azure.mgmt.resource.policy.models.PolicyDefinitionListResult(Model):
        next_link: str
        value: list[PolicyDefinition]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[PolicyDefinition], 
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


    class azure.mgmt.resource.policy.models.PolicyDefinitionReference(Model):
        definition_version: str
        effective_definition_version: str
        group_names: list[str]
        latest_definition_version: str
        parameters: dict[str, ParameterValuesValue]
        policy_definition_id: str
        policy_definition_reference_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                definition_version: Optional[str] = ..., 
                group_names: Optional[list[str]] = ..., 
                parameters: Optional[dict[str, ParameterValuesValue]] = ..., 
                policy_definition_id: str, 
                policy_definition_reference_id: Optional[str] = ..., 
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


    class azure.mgmt.resource.policy.models.PolicyDefinitionVersion(ProxyResource):
        description: str
        display_name: str
        external_evaluation_enforcement_settings: ExternalEvaluationEnforcementSettings
        id: str
        metadata: any
        mode: str
        name: str
        parameters: dict[str, ParameterDefinitionsValue]
        policy_rule: any
        policy_type: Union[str, PolicyType]
        system_data: SystemData
        type: str
        version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                external_evaluation_enforcement_settings: Optional[ExternalEvaluationEnforcementSettings] = ..., 
                metadata: Optional[Any] = ..., 
                mode: str = "Indexed", 
                parameters: Optional[dict[str, ParameterDefinitionsValue]] = ..., 
                policy_rule: Optional[Any] = ..., 
                policy_type: Optional[Union[str, PolicyType]] = ..., 
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


    class azure.mgmt.resource.policy.models.PolicyDefinitionVersionListResult(Model):
        next_link: str
        value: list[PolicyDefinitionVersion]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[PolicyDefinitionVersion], 
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


    class azure.mgmt.resource.policy.models.PolicyLogInfo(Model):
        ancestors: str
        compliance_reason_code: str
        policy_assignment_display_name: str
        policy_assignment_id: str
        policy_assignment_name: str
        policy_assignment_scope: str
        policy_assignment_version: str
        policy_definition_display_name: str
        policy_definition_effect: str
        policy_definition_group_names: list[str]
        policy_definition_id: str
        policy_definition_name: str
        policy_definition_reference_id: str
        policy_definition_version: str
        policy_exemption_ids: list[str]
        policy_set_definition_category: str
        policy_set_definition_display_name: str
        policy_set_definition_id: str
        policy_set_definition_name: str
        policy_set_definition_version: str
        resource_location: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ancestors: Optional[str] = ..., 
                compliance_reason_code: Optional[str] = ..., 
                policy_assignment_display_name: Optional[str] = ..., 
                policy_assignment_id: Optional[str] = ..., 
                policy_assignment_name: Optional[str] = ..., 
                policy_assignment_scope: Optional[str] = ..., 
                policy_assignment_version: Optional[str] = ..., 
                policy_definition_display_name: Optional[str] = ..., 
                policy_definition_effect: Optional[str] = ..., 
                policy_definition_group_names: Optional[list[str]] = ..., 
                policy_definition_id: Optional[str] = ..., 
                policy_definition_name: Optional[str] = ..., 
                policy_definition_reference_id: Optional[str] = ..., 
                policy_definition_version: Optional[str] = ..., 
                policy_exemption_ids: Optional[list[str]] = ..., 
                policy_set_definition_category: Optional[str] = ..., 
                policy_set_definition_display_name: Optional[str] = ..., 
                policy_set_definition_id: Optional[str] = ..., 
                policy_set_definition_name: Optional[str] = ..., 
                policy_set_definition_version: Optional[str] = ..., 
                resource_location: Optional[str] = ..., 
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


    class azure.mgmt.resource.policy.models.PolicySetDefinition(ProxyResource):
        description: str
        display_name: str
        id: str
        metadata: any
        name: str
        parameters: dict[str, ParameterDefinitionsValue]
        policy_definition_groups: list[PolicyDefinitionGroup]
        policy_definitions: list[PolicyDefinitionReference]
        policy_type: Union[str, PolicyType]
        system_data: SystemData
        type: str
        version: str
        versions: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                metadata: Optional[Any] = ..., 
                parameters: Optional[dict[str, ParameterDefinitionsValue]] = ..., 
                policy_definition_groups: Optional[list[PolicyDefinitionGroup]] = ..., 
                policy_definitions: Optional[list[PolicyDefinitionReference]] = ..., 
                policy_type: Optional[Union[str, PolicyType]] = ..., 
                version: Optional[str] = ..., 
                versions: Optional[list[str]] = ..., 
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


    class azure.mgmt.resource.policy.models.PolicySetDefinitionListResult(Model):
        next_link: str
        value: list[PolicySetDefinition]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[PolicySetDefinition], 
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


    class azure.mgmt.resource.policy.models.PolicySetDefinitionVersion(ProxyResource):
        description: str
        display_name: str
        id: str
        metadata: any
        name: str
        parameters: dict[str, ParameterDefinitionsValue]
        policy_definition_groups: list[PolicyDefinitionGroup]
        policy_definitions: list[PolicyDefinitionReference]
        policy_type: Union[str, PolicyType]
        system_data: SystemData
        type: str
        version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                metadata: Optional[Any] = ..., 
                parameters: Optional[dict[str, ParameterDefinitionsValue]] = ..., 
                policy_definition_groups: Optional[list[PolicyDefinitionGroup]] = ..., 
                policy_definitions: Optional[list[PolicyDefinitionReference]] = ..., 
                policy_type: Optional[Union[str, PolicyType]] = ..., 
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


    class azure.mgmt.resource.policy.models.PolicySetDefinitionVersionListResult(Model):
        next_link: str
        value: list[PolicySetDefinitionVersion]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[PolicySetDefinitionVersion], 
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


    class azure.mgmt.resource.policy.models.PolicyTokenOperation(Model):
        content: any
        http_method: str
        uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                content: Optional[Any] = ..., 
                http_method: str, 
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


    class azure.mgmt.resource.policy.models.PolicyTokenRequest(Model):
        change_reference: str
        operation: PolicyTokenOperation

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                change_reference: Optional[str] = ..., 
                operation: PolicyTokenOperation, 
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


    class azure.mgmt.resource.policy.models.PolicyTokenResponse(Model):
        change_reference: str
        expiration: datetime
        message: str
        result: Union[str, PolicyTokenResult]
        results: list[ExternalEvaluationEndpointInvocationResult]
        retry_after: datetime
        token: str
        token_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                change_reference: Optional[str] = ..., 
                expiration: Optional[datetime] = ..., 
                message: Optional[str] = ..., 
                result: Optional[Union[str, PolicyTokenResult]] = ..., 
                results: Optional[list[ExternalEvaluationEndpointInvocationResult]] = ..., 
                retry_after: Optional[datetime] = ..., 
                token: Optional[str] = ..., 
                token_id: Optional[str] = ..., 
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


    class azure.mgmt.resource.policy.models.PolicyTokenResult(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.resource.policy.models.PolicyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUILT_IN = "BuiltIn"
        CUSTOM = "Custom"
        NOT_SPECIFIED = "NotSpecified"
        STATIC = "Static"


    class azure.mgmt.resource.policy.models.ProxyResource(Resource):
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


    class azure.mgmt.resource.policy.models.Resource(Model):
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


    class azure.mgmt.resource.policy.models.ResourceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.resource.policy.models.ResourceSelector(Model):
        name: str
        selectors: list[Selector]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                selectors: Optional[list[Selector]] = ..., 
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


    class azure.mgmt.resource.policy.models.ResourceTypeAliases(Model):
        aliases: list[Alias]
        resource_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                aliases: Optional[list[Alias]] = ..., 
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


    class azure.mgmt.resource.policy.models.Selector(Model):
        in_property: list[str]
        kind: Union[str, SelectorKind]
        not_in: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                in_property: Optional[list[str]] = ..., 
                kind: Optional[Union[str, SelectorKind]] = ..., 
                not_in: Optional[list[str]] = ..., 
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


    class azure.mgmt.resource.policy.models.SelectorKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        POLICY_DEFINITION_REFERENCE_ID = "policyDefinitionReferenceId"
        RESOURCE_LOCATION = "resourceLocation"
        RESOURCE_TYPE = "resourceType"
        RESOURCE_WITHOUT_LOCATION = "resourceWithoutLocation"


    class azure.mgmt.resource.policy.models.SystemData(Model):
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


    class azure.mgmt.resource.policy.models.UserAssignedIdentitiesValue(Model):
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


namespace azure.mgmt.resource.policy.operations

    class azure.mgmt.resource.policy.operations.DataPolicyManifestsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_by_policy_mode(
                self, 
                policy_mode: str, 
                **kwargs: Any
            ) -> DataPolicyManifest: ...

        @distributed_trace
        def list(
                self, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> ItemPaged[DataPolicyManifest]: ...


    class azure.mgmt.resource.policy.operations.PolicyAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                scope: str, 
                policy_assignment_name: str, 
                parameters: PolicyAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @overload
        def create(
                self, 
                scope: str, 
                policy_assignment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @overload
        def create_by_id(
                self, 
                policy_assignment_id: str, 
                parameters: PolicyAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @overload
        def create_by_id(
                self, 
                policy_assignment_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @distributed_trace
        def delete(
                self, 
                scope: str, 
                policy_assignment_name: str, 
                **kwargs: Any
            ) -> Optional[PolicyAssignment]: ...

        @distributed_trace
        def delete_by_id(
                self, 
                policy_assignment_id: str, 
                **kwargs: Any
            ) -> Optional[PolicyAssignment]: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                policy_assignment_name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @distributed_trace
        def get_by_id(
                self, 
                policy_assignment_id: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @distributed_trace
        def list(
                self, 
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[PolicyAssignment]: ...

        @distributed_trace
        def list_for_management_group(
                self, 
                management_group_id: str, 
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[PolicyAssignment]: ...

        @distributed_trace
        def list_for_resource(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_path: str, 
                resource_type: str, 
                resource_name: str, 
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[PolicyAssignment]: ...

        @distributed_trace
        def list_for_resource_group(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[PolicyAssignment]: ...

        @overload
        def update(
                self, 
                scope: str, 
                policy_assignment_name: str, 
                parameters: PolicyAssignmentUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @overload
        def update(
                self, 
                scope: str, 
                policy_assignment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @overload
        def update_by_id(
                self, 
                policy_assignment_id: str, 
                parameters: PolicyAssignmentUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @overload
        def update_by_id(
                self, 
                policy_assignment_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyAssignment: ...


    class azure.mgmt.resource.policy.operations.PolicyDefinitionVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                policy_definition_name: str, 
                policy_definition_version: str, 
                parameters: PolicyDefinitionVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyDefinitionVersion: ...

        @overload
        def create_or_update(
                self, 
                policy_definition_name: str, 
                policy_definition_version: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyDefinitionVersion: ...

        @overload
        def create_or_update_at_management_group(
                self, 
                management_group_name: str, 
                policy_definition_name: str, 
                policy_definition_version: str, 
                parameters: PolicyDefinitionVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyDefinitionVersion: ...

        @overload
        def create_or_update_at_management_group(
                self, 
                management_group_name: str, 
                policy_definition_name: str, 
                policy_definition_version: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyDefinitionVersion: ...

        @distributed_trace
        def delete(
                self, 
                policy_definition_name: str, 
                policy_definition_version: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_at_management_group(
                self, 
                management_group_name: str, 
                policy_definition_name: str, 
                policy_definition_version: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                policy_definition_name: str, 
                policy_definition_version: str, 
                **kwargs: Any
            ) -> PolicyDefinitionVersion: ...

        @distributed_trace
        def get_at_management_group(
                self, 
                management_group_name: str, 
                policy_definition_name: str, 
                policy_definition_version: str, 
                **kwargs: Any
            ) -> PolicyDefinitionVersion: ...

        @distributed_trace
        def get_built_in(
                self, 
                policy_definition_name: str, 
                policy_definition_version: str, 
                **kwargs: Any
            ) -> PolicyDefinitionVersion: ...

        @distributed_trace
        def list(
                self, 
                policy_definition_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[PolicyDefinitionVersion]: ...

        @distributed_trace
        def list_all(self, **kwargs: Any) -> PolicyDefinitionVersionListResult: ...

        @distributed_trace
        def list_all_at_management_group(
                self, 
                management_group_name: str, 
                **kwargs: Any
            ) -> PolicyDefinitionVersionListResult: ...

        @distributed_trace
        def list_all_builtins(self, **kwargs: Any) -> PolicyDefinitionVersionListResult: ...

        @distributed_trace
        def list_built_in(
                self, 
                policy_definition_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[PolicyDefinitionVersion]: ...

        @distributed_trace
        def list_by_management_group(
                self, 
                management_group_name: str, 
                policy_definition_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[PolicyDefinitionVersion]: ...


    class azure.mgmt.resource.policy.operations.PolicyDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                policy_definition_name: str, 
                parameters: PolicyDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyDefinition: ...

        @overload
        def create_or_update(
                self, 
                policy_definition_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyDefinition: ...

        @overload
        def create_or_update_at_management_group(
                self, 
                management_group_id: str, 
                policy_definition_name: str, 
                parameters: PolicyDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyDefinition: ...

        @overload
        def create_or_update_at_management_group(
                self, 
                management_group_id: str, 
                policy_definition_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyDefinition: ...

        @distributed_trace
        def delete(
                self, 
                policy_definition_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_at_management_group(
                self, 
                management_group_id: str, 
                policy_definition_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                policy_definition_name: str, 
                **kwargs: Any
            ) -> PolicyDefinition: ...

        @distributed_trace
        def get_at_management_group(
                self, 
                management_group_id: str, 
                policy_definition_name: str, 
                **kwargs: Any
            ) -> PolicyDefinition: ...

        @distributed_trace
        def get_built_in(
                self, 
                policy_definition_name: str, 
                **kwargs: Any
            ) -> PolicyDefinition: ...

        @distributed_trace
        def list(
                self, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[PolicyDefinition]: ...

        @distributed_trace
        def list_built_in(
                self, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[PolicyDefinition]: ...

        @distributed_trace
        def list_by_management_group(
                self, 
                management_group_id: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[PolicyDefinition]: ...


    class azure.mgmt.resource.policy.operations.PolicySetDefinitionVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                policy_set_definition_name: str, 
                policy_definition_version: str, 
                parameters: PolicySetDefinitionVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicySetDefinitionVersion: ...

        @overload
        def create_or_update(
                self, 
                policy_set_definition_name: str, 
                policy_definition_version: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicySetDefinitionVersion: ...

        @overload
        def create_or_update_at_management_group(
                self, 
                management_group_name: str, 
                policy_set_definition_name: str, 
                policy_definition_version: str, 
                parameters: PolicySetDefinitionVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicySetDefinitionVersion: ...

        @overload
        def create_or_update_at_management_group(
                self, 
                management_group_name: str, 
                policy_set_definition_name: str, 
                policy_definition_version: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicySetDefinitionVersion: ...

        @distributed_trace
        def delete(
                self, 
                policy_set_definition_name: str, 
                policy_definition_version: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_at_management_group(
                self, 
                management_group_name: str, 
                policy_set_definition_name: str, 
                policy_definition_version: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                policy_set_definition_name: str, 
                policy_definition_version: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> PolicySetDefinitionVersion: ...

        @distributed_trace
        def get_at_management_group(
                self, 
                management_group_name: str, 
                policy_set_definition_name: str, 
                policy_definition_version: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> PolicySetDefinitionVersion: ...

        @distributed_trace
        def get_built_in(
                self, 
                policy_set_definition_name: str, 
                policy_definition_version: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> PolicySetDefinitionVersion: ...

        @distributed_trace
        def list(
                self, 
                policy_set_definition_name: str, 
                expand: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[PolicySetDefinitionVersion]: ...

        @distributed_trace
        def list_all(self, **kwargs: Any) -> PolicySetDefinitionVersionListResult: ...

        @distributed_trace
        def list_all_at_management_group(
                self, 
                management_group_name: str, 
                **kwargs: Any
            ) -> PolicySetDefinitionVersionListResult: ...

        @distributed_trace
        def list_all_builtins(self, **kwargs: Any) -> PolicySetDefinitionVersionListResult: ...

        @distributed_trace
        def list_built_in(
                self, 
                policy_set_definition_name: str, 
                expand: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[PolicySetDefinitionVersion]: ...

        @distributed_trace
        def list_by_management_group(
                self, 
                management_group_name: str, 
                policy_set_definition_name: str, 
                expand: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[PolicySetDefinitionVersion]: ...


    class azure.mgmt.resource.policy.operations.PolicySetDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                policy_set_definition_name: str, 
                parameters: PolicySetDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicySetDefinition: ...

        @overload
        def create_or_update(
                self, 
                policy_set_definition_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicySetDefinition: ...

        @overload
        def create_or_update_at_management_group(
                self, 
                management_group_id: str, 
                policy_set_definition_name: str, 
                parameters: PolicySetDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicySetDefinition: ...

        @overload
        def create_or_update_at_management_group(
                self, 
                management_group_id: str, 
                policy_set_definition_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicySetDefinition: ...

        @distributed_trace
        def delete(
                self, 
                policy_set_definition_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_at_management_group(
                self, 
                management_group_id: str, 
                policy_set_definition_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                policy_set_definition_name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> PolicySetDefinition: ...

        @distributed_trace
        def get_at_management_group(
                self, 
                management_group_id: str, 
                policy_set_definition_name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> PolicySetDefinition: ...

        @distributed_trace
        def get_built_in(
                self, 
                policy_set_definition_name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> PolicySetDefinition: ...

        @distributed_trace
        def list(
                self, 
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[PolicySetDefinition]: ...

        @distributed_trace
        def list_built_in(
                self, 
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[PolicySetDefinition]: ...

        @distributed_trace
        def list_by_management_group(
                self, 
                management_group_id: str, 
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[PolicySetDefinition]: ...


    class azure.mgmt.resource.policy.operations.PolicyTokensOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def acquire(
                self, 
                parameters: PolicyTokenRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyTokenResponse: ...

        @overload
        def acquire(
                self, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyTokenResponse: ...

        @overload
        def acquire_at_management_group(
                self, 
                management_group_name: str, 
                parameters: PolicyTokenRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyTokenResponse: ...

        @overload
        def acquire_at_management_group(
                self, 
                management_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyTokenResponse: ...


```