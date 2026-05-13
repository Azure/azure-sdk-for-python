```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.resource.features

    class azure.mgmt.resource.features.FeatureClient(_FeatureClientOperationsMixin): implements ContextManager 
        features: FeaturesOperations
        subscription_feature_registrations: SubscriptionFeatureRegistrationsOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @distributed_trace
        def list_operations(self, **kwargs: Any) -> ItemPaged[Operation]: ...


namespace azure.mgmt.resource.features.aio

    class azure.mgmt.resource.features.aio.FeatureClient(_FeatureClientOperationsMixin): implements AsyncContextManager 
        features: FeaturesOperations
        subscription_feature_registrations: SubscriptionFeatureRegistrationsOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        @distributed_trace
        def list_operations(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


namespace azure.mgmt.resource.features.aio.operations

    class azure.mgmt.resource.features.aio.operations.FeaturesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_provider_namespace: str, 
                feature_name: str, 
                **kwargs: Any
            ) -> FeatureResult: ...

        @distributed_trace
        def list(
                self, 
                resource_provider_namespace: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[FeatureResult]: ...

        @distributed_trace
        def list_all(self, **kwargs: Any) -> AsyncItemPaged[FeatureResult]: ...

        @distributed_trace_async
        async def register(
                self, 
                resource_provider_namespace: str, 
                feature_name: str, 
                **kwargs: Any
            ) -> FeatureResult: ...

        @distributed_trace_async
        async def unregister(
                self, 
                resource_provider_namespace: str, 
                feature_name: str, 
                **kwargs: Any
            ) -> FeatureResult: ...


    class azure.mgmt.resource.features.aio.operations.SubscriptionFeatureRegistrationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                provider_namespace: str, 
                feature_name: str, 
                subscription_feature_registration_type: Optional[SubscriptionFeatureRegistration] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SubscriptionFeatureRegistration: ...

        @overload
        async def create_or_update(
                self, 
                provider_namespace: str, 
                feature_name: str, 
                subscription_feature_registration_type: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SubscriptionFeatureRegistration: ...

        @distributed_trace_async
        async def delete(
                self, 
                provider_namespace: str, 
                feature_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                provider_namespace: str, 
                feature_name: str, 
                **kwargs: Any
            ) -> SubscriptionFeatureRegistration: ...

        @distributed_trace
        def list_all_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[SubscriptionFeatureRegistration]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                provider_namespace: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SubscriptionFeatureRegistration]: ...


namespace azure.mgmt.resource.features.models

    class azure.mgmt.resource.features.models.AuthorizationProfile(Model):
        approved_time: datetime
        approver: str
        requested_time: datetime
        requester: str
        requester_object_id: str

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


    class azure.mgmt.resource.features.models.ErrorDefinition(Model):
        code: str
        details: list[ErrorDefinition]
        message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                details: Optional[list[ErrorDefinition]] = ..., 
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


    class azure.mgmt.resource.features.models.ErrorResponse(Model):
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


    class azure.mgmt.resource.features.models.FeatureOperationsListResult(Model):
        next_link: str
        value: list[FeatureResult]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[FeatureResult]] = ..., 
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


    class azure.mgmt.resource.features.models.FeatureProperties(Model):
        state: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                state: Optional[str] = ..., 
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


    class azure.mgmt.resource.features.models.FeatureResult(Model):
        id: str
        name: str
        properties: FeatureProperties
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[FeatureProperties] = ..., 
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


    class azure.mgmt.resource.features.models.Operation(Model):
        display: OperationDisplay
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
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


    class azure.mgmt.resource.features.models.OperationDisplay(Model):
        operation: str
        provider: str
        resource: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
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


    class azure.mgmt.resource.features.models.OperationListResult(Model):
        next_link: str
        value: list[Operation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[Operation]] = ..., 
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


    class azure.mgmt.resource.features.models.ProxyResource(Model):
        id: str
        name: str
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


    class azure.mgmt.resource.features.models.SubscriptionFeatureRegistration(ProxyResource):
        id: str
        name: str
        properties: SubscriptionFeatureRegistrationProperties
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[SubscriptionFeatureRegistrationProperties] = ..., 
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


    class azure.mgmt.resource.features.models.SubscriptionFeatureRegistrationApprovalType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVAL_REQUIRED = "ApprovalRequired"
        AUTO_APPROVAL = "AutoApproval"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.resource.features.models.SubscriptionFeatureRegistrationList(Model):
        next_link: str
        value: list[SubscriptionFeatureRegistration]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[SubscriptionFeatureRegistration]] = ..., 
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


    class azure.mgmt.resource.features.models.SubscriptionFeatureRegistrationProperties(Model):
        approval_type: Union[str, SubscriptionFeatureRegistrationApprovalType]
        authorization_profile: AuthorizationProfile
        description: str
        display_name: str
        documentation_link: str
        feature_name: str
        metadata: dict[str, str]
        provider_namespace: str
        registration_date: datetime
        release_date: datetime
        should_feature_display_in_portal: bool
        state: Union[str, SubscriptionFeatureRegistrationState]
        subscription_id: str
        tenant_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                authorization_profile: Optional[AuthorizationProfile] = ..., 
                description: Optional[str] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                should_feature_display_in_portal: bool = False, 
                state: Optional[Union[str, SubscriptionFeatureRegistrationState]] = ..., 
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


    class azure.mgmt.resource.features.models.SubscriptionFeatureRegistrationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_REGISTERED = "NotRegistered"
        NOT_SPECIFIED = "NotSpecified"
        PENDING = "Pending"
        REGISTERED = "Registered"
        REGISTERING = "Registering"
        UNREGISTERED = "Unregistered"
        UNREGISTERING = "Unregistering"


namespace azure.mgmt.resource.features.operations

    class azure.mgmt.resource.features.operations.FeaturesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_provider_namespace: str, 
                feature_name: str, 
                **kwargs: Any
            ) -> FeatureResult: ...

        @distributed_trace
        def list(
                self, 
                resource_provider_namespace: str, 
                **kwargs: Any
            ) -> ItemPaged[FeatureResult]: ...

        @distributed_trace
        def list_all(self, **kwargs: Any) -> ItemPaged[FeatureResult]: ...

        @distributed_trace
        def register(
                self, 
                resource_provider_namespace: str, 
                feature_name: str, 
                **kwargs: Any
            ) -> FeatureResult: ...

        @distributed_trace
        def unregister(
                self, 
                resource_provider_namespace: str, 
                feature_name: str, 
                **kwargs: Any
            ) -> FeatureResult: ...


    class azure.mgmt.resource.features.operations.SubscriptionFeatureRegistrationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                provider_namespace: str, 
                feature_name: str, 
                subscription_feature_registration_type: Optional[SubscriptionFeatureRegistration] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SubscriptionFeatureRegistration: ...

        @overload
        def create_or_update(
                self, 
                provider_namespace: str, 
                feature_name: str, 
                subscription_feature_registration_type: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SubscriptionFeatureRegistration: ...

        @distributed_trace
        def delete(
                self, 
                provider_namespace: str, 
                feature_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                provider_namespace: str, 
                feature_name: str, 
                **kwargs: Any
            ) -> SubscriptionFeatureRegistration: ...

        @distributed_trace
        def list_all_by_subscription(self, **kwargs: Any) -> ItemPaged[SubscriptionFeatureRegistration]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                provider_namespace: str, 
                **kwargs: Any
            ) -> ItemPaged[SubscriptionFeatureRegistration]: ...


```