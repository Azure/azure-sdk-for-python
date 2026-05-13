```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.managedservices

    class azure.mgmt.managedservices.ManagedServicesClient: implements ContextManager 
        marketplace_registration_definitions: MarketplaceRegistrationDefinitionsOperations
        marketplace_registration_definitions_without_scope: MarketplaceRegistrationDefinitionsWithoutScopeOperations
        operations: Operations
        operations_with_scope: OperationsWithScopeOperations
        registration_assignments: RegistrationAssignmentsOperations
        registration_definitions: RegistrationDefinitionsOperations

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


namespace azure.mgmt.managedservices.aio

    class azure.mgmt.managedservices.aio.ManagedServicesClient: implements AsyncContextManager 
        marketplace_registration_definitions: MarketplaceRegistrationDefinitionsOperations
        marketplace_registration_definitions_without_scope: MarketplaceRegistrationDefinitionsWithoutScopeOperations
        operations: Operations
        operations_with_scope: OperationsWithScopeOperations
        registration_assignments: RegistrationAssignmentsOperations
        registration_definitions: RegistrationDefinitionsOperations

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


namespace azure.mgmt.managedservices.aio.operations

    class azure.mgmt.managedservices.aio.operations.MarketplaceRegistrationDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                marketplace_identifier: str, 
                **kwargs: Any
            ) -> MarketplaceRegistrationDefinition: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[MarketplaceRegistrationDefinition]: ...


    class azure.mgmt.managedservices.aio.operations.MarketplaceRegistrationDefinitionsWithoutScopeOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                marketplace_identifier: str, 
                **kwargs: Any
            ) -> MarketplaceRegistrationDefinition: ...

        @distributed_trace
        def list(
                self, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[MarketplaceRegistrationDefinition]: ...


    class azure.mgmt.managedservices.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def list(self, **kwargs: Any) -> OperationList: ...


    class azure.mgmt.managedservices.aio.operations.OperationsWithScopeOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def list(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> OperationList: ...


    class azure.mgmt.managedservices.aio.operations.RegistrationAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                scope: str, 
                registration_assignment_id: str, 
                request_body: RegistrationAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RegistrationAssignment]: ...

        @overload
        async def begin_create_or_update(
                self, 
                scope: str, 
                registration_assignment_id: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RegistrationAssignment]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                scope: str, 
                registration_assignment_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                registration_assignment_id: str, 
                expand_registration_definition: Optional[bool] = None, 
                **kwargs: Any
            ) -> RegistrationAssignment: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                expand_registration_definition: Optional[bool] = None, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[RegistrationAssignment]: ...


    class azure.mgmt.managedservices.aio.operations.RegistrationDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                registration_definition_id: str, 
                scope: str, 
                request_body: RegistrationDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RegistrationDefinition]: ...

        @overload
        async def begin_create_or_update(
                self, 
                registration_definition_id: str, 
                scope: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RegistrationDefinition]: ...

        @distributed_trace_async
        async def delete(
                self, 
                registration_definition_id: str, 
                scope: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                registration_definition_id: str, 
                **kwargs: Any
            ) -> RegistrationDefinition: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[RegistrationDefinition]: ...


namespace azure.mgmt.managedservices.models

    class azure.mgmt.managedservices.models.Authorization(Model):
        delegated_role_definition_ids: list[str]
        principal_id: str
        principal_id_display_name: str
        role_definition_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                delegated_role_definition_ids: Optional[List[str]] = ..., 
                principal_id: str, 
                principal_id_display_name: Optional[str] = ..., 
                role_definition_id: str, 
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


    class azure.mgmt.managedservices.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.managedservices.models.EligibleApprover(Model):
        principal_id: str
        principal_id_display_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                principal_id: str, 
                principal_id_display_name: Optional[str] = ..., 
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


    class azure.mgmt.managedservices.models.EligibleAuthorization(Model):
        just_in_time_access_policy: JustInTimeAccessPolicy
        principal_id: str
        principal_id_display_name: str
        role_definition_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                just_in_time_access_policy: Optional[JustInTimeAccessPolicy] = ..., 
                principal_id: str, 
                principal_id_display_name: Optional[str] = ..., 
                role_definition_id: str, 
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


    class azure.mgmt.managedservices.models.ErrorDefinition(Model):
        code: str
        details: list[ErrorDefinition]
        message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: str, 
                details: Optional[List[ErrorDefinition]] = ..., 
                message: str, 
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


    class azure.mgmt.managedservices.models.ErrorResponse(Model):
        error: ErrorDefinition

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorDefinition] = ..., 
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


    class azure.mgmt.managedservices.models.JustInTimeAccessPolicy(Model):
        managed_by_tenant_approvers: list[EligibleApprover]
        maximum_activation_duration: timedelta
        multi_factor_auth_provider: Union[str, MultiFactorAuthProvider]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                managed_by_tenant_approvers: Optional[List[EligibleApprover]] = ..., 
                maximum_activation_duration: timedelta = "PT8H", 
                multi_factor_auth_provider: Union[str, MultiFactorAuthProvider] = None, 
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


    class azure.mgmt.managedservices.models.MarketplaceRegistrationDefinition(Model):
        id: str
        name: str
        plan: Plan
        properties: MarketplaceRegistrationDefinitionProperties
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                plan: Optional[Plan] = ..., 
                properties: Optional[MarketplaceRegistrationDefinitionProperties] = ..., 
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


    class azure.mgmt.managedservices.models.MarketplaceRegistrationDefinitionList(Model):
        next_link: str
        value: list[MarketplaceRegistrationDefinition]

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


    class azure.mgmt.managedservices.models.MarketplaceRegistrationDefinitionProperties(Model):
        authorizations: list[Authorization]
        eligible_authorizations: list[EligibleAuthorization]
        managed_by_tenant_id: str
        offer_display_name: str
        plan_display_name: str
        publisher_display_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                authorizations: List[Authorization], 
                eligible_authorizations: Optional[List[EligibleAuthorization]] = ..., 
                managed_by_tenant_id: str, 
                offer_display_name: Optional[str] = ..., 
                plan_display_name: Optional[str] = ..., 
                publisher_display_name: Optional[str] = ..., 
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


    class azure.mgmt.managedservices.models.MultiFactorAuthProvider(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE = "Azure"
        NONE = "None"


    class azure.mgmt.managedservices.models.Operation(Model):
        display: OperationDisplay
        name: str

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


    class azure.mgmt.managedservices.models.OperationDisplay(Model):
        description: str
        operation: str
        provider: str
        resource: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ..., 
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


    class azure.mgmt.managedservices.models.OperationList(Model):
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


    class azure.mgmt.managedservices.models.Plan(Model):
        name: str
        product: str
        publisher: str
        version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: str, 
                product: str, 
                publisher: str, 
                version: str, 
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


    class azure.mgmt.managedservices.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
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


    class azure.mgmt.managedservices.models.RegistrationAssignment(Model):
        id: str
        name: str
        properties: RegistrationAssignmentProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[RegistrationAssignmentProperties] = ..., 
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


    class azure.mgmt.managedservices.models.RegistrationAssignmentList(Model):
        next_link: str
        value: list[RegistrationAssignment]

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


    class azure.mgmt.managedservices.models.RegistrationAssignmentProperties(Model):
        provisioning_state: Union[str, ProvisioningState]
        registration_definition: RegistrationAssignmentPropertiesRegistrationDefinition
        registration_definition_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                registration_definition_id: str, 
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


    class azure.mgmt.managedservices.models.RegistrationAssignmentPropertiesRegistrationDefinition(Model):
        id: str
        name: str
        plan: Plan
        properties: RegistrationAssignmentPropertiesRegistrationDefinitionProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                plan: Optional[Plan] = ..., 
                properties: Optional[RegistrationAssignmentPropertiesRegistrationDefinitionProperties] = ..., 
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


    class azure.mgmt.managedservices.models.RegistrationAssignmentPropertiesRegistrationDefinitionProperties(Model):
        authorizations: list[Authorization]
        description: str
        eligible_authorizations: list[EligibleAuthorization]
        managed_by_tenant_id: str
        managed_by_tenant_name: str
        managee_tenant_id: str
        managee_tenant_name: str
        provisioning_state: Union[str, ProvisioningState]
        registration_definition_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                authorizations: Optional[List[Authorization]] = ..., 
                description: Optional[str] = ..., 
                eligible_authorizations: Optional[List[EligibleAuthorization]] = ..., 
                managed_by_tenant_id: Optional[str] = ..., 
                managed_by_tenant_name: Optional[str] = ..., 
                managee_tenant_id: Optional[str] = ..., 
                managee_tenant_name: Optional[str] = ..., 
                provisioning_state: Optional[Union[str, ProvisioningState]] = ..., 
                registration_definition_name: Optional[str] = ..., 
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


    class azure.mgmt.managedservices.models.RegistrationDefinition(Model):
        id: str
        name: str
        plan: Plan
        properties: RegistrationDefinitionProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                plan: Optional[Plan] = ..., 
                properties: Optional[RegistrationDefinitionProperties] = ..., 
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


    class azure.mgmt.managedservices.models.RegistrationDefinitionList(Model):
        next_link: str
        value: list[RegistrationDefinition]

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


    class azure.mgmt.managedservices.models.RegistrationDefinitionProperties(Model):
        authorizations: list[Authorization]
        description: str
        eligible_authorizations: list[EligibleAuthorization]
        managed_by_tenant_id: str
        managed_by_tenant_name: str
        managee_tenant_id: str
        managee_tenant_name: str
        provisioning_state: Union[str, ProvisioningState]
        registration_definition_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                authorizations: List[Authorization], 
                description: Optional[str] = ..., 
                eligible_authorizations: Optional[List[EligibleAuthorization]] = ..., 
                managed_by_tenant_id: str, 
                registration_definition_name: Optional[str] = ..., 
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


    class azure.mgmt.managedservices.models.SystemData(Model):
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


namespace azure.mgmt.managedservices.operations

    class azure.mgmt.managedservices.operations.MarketplaceRegistrationDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                marketplace_identifier: str, 
                **kwargs: Any
            ) -> MarketplaceRegistrationDefinition: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[MarketplaceRegistrationDefinition]: ...


    class azure.mgmt.managedservices.operations.MarketplaceRegistrationDefinitionsWithoutScopeOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                marketplace_identifier: str, 
                **kwargs: Any
            ) -> MarketplaceRegistrationDefinition: ...

        @distributed_trace
        def list(
                self, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[MarketplaceRegistrationDefinition]: ...


    class azure.mgmt.managedservices.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(self, **kwargs: Any) -> OperationList: ...


    class azure.mgmt.managedservices.operations.OperationsWithScopeOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> OperationList: ...


    class azure.mgmt.managedservices.operations.RegistrationAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                scope: str, 
                registration_assignment_id: str, 
                request_body: RegistrationAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RegistrationAssignment]: ...

        @overload
        def begin_create_or_update(
                self, 
                scope: str, 
                registration_assignment_id: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RegistrationAssignment]: ...

        @distributed_trace
        def begin_delete(
                self, 
                scope: str, 
                registration_assignment_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                registration_assignment_id: str, 
                expand_registration_definition: Optional[bool] = None, 
                **kwargs: Any
            ) -> RegistrationAssignment: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                expand_registration_definition: Optional[bool] = None, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[RegistrationAssignment]: ...


    class azure.mgmt.managedservices.operations.RegistrationDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                registration_definition_id: str, 
                scope: str, 
                request_body: RegistrationDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RegistrationDefinition]: ...

        @overload
        def begin_create_or_update(
                self, 
                registration_definition_id: str, 
                scope: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RegistrationDefinition]: ...

        @distributed_trace
        def delete(
                self, 
                registration_definition_id: str, 
                scope: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                registration_definition_id: str, 
                **kwargs: Any
            ) -> RegistrationDefinition: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[RegistrationDefinition]: ...


```