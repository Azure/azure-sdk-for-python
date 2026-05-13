```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.subscription

    class azure.mgmt.subscription.SubscriptionClient: implements ContextManager 
        alias: AliasOperations
        billing_account: BillingAccountOperations
        operations: Operations
        subscription: SubscriptionOperations
        subscription_policy: SubscriptionPolicyOperations
        subscriptions: SubscriptionsOperations
        tenants: TenantsOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                base_url: str = "https://management.azure.com", 
                *, 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...


namespace azure.mgmt.subscription.aio

    class azure.mgmt.subscription.aio.SubscriptionClient: implements AsyncContextManager 
        alias: AliasOperations
        billing_account: BillingAccountOperations
        operations: Operations
        subscription: SubscriptionOperations
        subscription_policy: SubscriptionPolicyOperations
        subscriptions: SubscriptionsOperations
        tenants: TenantsOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                base_url: str = "https://management.azure.com", 
                *, 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...


namespace azure.mgmt.subscription.aio.operations

    class azure.mgmt.subscription.aio.operations.AliasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                alias_name: str, 
                body: PutAliasRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SubscriptionAliasResponse]: ...

        @overload
        async def begin_create(
                self, 
                alias_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SubscriptionAliasResponse]: ...

        @distributed_trace_async
        async def delete(
                self, 
                alias_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                alias_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SubscriptionAliasResponse: ...

        @distributed_trace_async
        async def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SubscriptionAliasListResult: ...


    class azure.mgmt.subscription.aio.operations.BillingAccountOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_policy(
                self, 
                billing_account_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> BillingAccountPoliciesResponse: ...


    class azure.mgmt.subscription.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Operation]: ...


    class azure.mgmt.subscription.aio.operations.SubscriptionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def accept_ownership_status(
                self, 
                subscription_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AcceptOwnershipStatusResponse: ...

        @overload
        async def begin_accept_ownership(
                self, 
                subscription_id: str, 
                body: AcceptOwnershipRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_accept_ownership(
                self, 
                subscription_id: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def cancel(
                self, 
                subscription_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> CanceledSubscriptionId: ...

        @distributed_trace_async
        async def enable(
                self, 
                subscription_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> EnabledSubscriptionId: ...

        @overload
        async def rename(
                self, 
                subscription_id: str, 
                body: SubscriptionName, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RenamedSubscriptionId: ...

        @overload
        async def rename(
                self, 
                subscription_id: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RenamedSubscriptionId: ...


    class azure.mgmt.subscription.aio.operations.SubscriptionPolicyOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def add_update_policy_for_tenant(
                self, 
                body: PutTenantPolicyRequestProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GetTenantPolicyResponse: ...

        @overload
        async def add_update_policy_for_tenant(
                self, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GetTenantPolicyResponse: ...

        @distributed_trace_async
        async def get_policy_for_tenant(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> GetTenantPolicyResponse: ...

        @distributed_trace
        def list_policy_for_tenant(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[GetTenantPolicyResponse]: ...


    class azure.mgmt.subscription.aio.operations.SubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                subscription_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Subscription: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Subscription]: ...

        @distributed_trace
        def list_locations(
                self, 
                subscription_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Location]: ...


    class azure.mgmt.subscription.aio.operations.TenantsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[TenantIdDescription]: ...


namespace azure.mgmt.subscription.models

    class azure.mgmt.subscription.models.AcceptOwnership(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        EXPIRED = "Expired"
        PENDING = "Pending"


    class azure.mgmt.subscription.models.AcceptOwnershipRequest(Model):
        properties: AcceptOwnershipRequestProperties

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                properties: Optional[AcceptOwnershipRequestProperties] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.subscription.models.AcceptOwnershipRequestProperties(Model):
        display_name: str
        management_group_id: str
        tags: dict[str, str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                display_name: str, 
                management_group_id: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.subscription.models.AcceptOwnershipStatusResponse(Model):
        accept_ownership_state: Union[str, AcceptOwnership]
        billing_owner: str
        display_name: str
        provisioning_state: Union[str, Provisioning]
        subscription_id: str
        subscription_tenant_id: str
        tags: dict[str, str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                subscription_tenant_id: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.subscription.models.BillingAccountPoliciesResponse(Model):
        id: str
        name: str
        properties: BillingAccountPoliciesResponseProperties
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                properties: Optional[BillingAccountPoliciesResponseProperties] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.subscription.models.BillingAccountPoliciesResponseProperties(Model):
        allow_transfers: bool
        service_tenants: list[ServiceTenantResponse]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                allow_transfers: Optional[bool] = ..., 
                service_tenants: Optional[List[ServiceTenantResponse]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.subscription.models.CanceledSubscriptionId(Model):
        subscription_id: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.subscription.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.subscription.models.EnabledSubscriptionId(Model):
        subscription_id: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.subscription.models.ErrorResponse(Model):
        code: str
        message: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.subscription.models.ErrorResponseBody(Model):
        code: str
        error: ErrorResponse
        message: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                error: Optional[ErrorResponse] = ..., 
                message: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.subscription.models.GetTenantPolicyListResponse(Model):
        next_link: str
        value: list[GetTenantPolicyResponse]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.subscription.models.GetTenantPolicyResponse(Model):
        id: str
        name: str
        properties: TenantPolicy
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                properties: Optional[TenantPolicy] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.subscription.models.Location(Model):
        display_name: str
        id: str
        latitude: str
        longitude: str
        name: str
        subscription_id: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.subscription.models.LocationListResult(Model):
        value: list[Location]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: Optional[List[Location]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.subscription.models.Operation(Model):
        display: OperationDisplay
        is_data_action: bool
        name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                is_data_action: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.subscription.models.OperationDisplay(Model):
        description: str
        operation: str
        provider: str
        resource: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.subscription.models.OperationListResult(Model):
        next_link: str
        value: list[Operation]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Operation]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.subscription.models.Provisioning(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        PENDING = "Pending"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.subscription.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.subscription.models.PutAliasRequest(Model):
        properties: PutAliasRequestProperties

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                properties: Optional[PutAliasRequestProperties] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.subscription.models.PutAliasRequestAdditionalProperties(Model):
        management_group_id: str
        subscription_owner_id: str
        subscription_tenant_id: str
        tags: dict[str, str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                management_group_id: Optional[str] = ..., 
                subscription_owner_id: Optional[str] = ..., 
                subscription_tenant_id: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.subscription.models.PutAliasRequestProperties(Model):
        additional_properties: PutAliasRequestAdditionalProperties
        billing_scope: str
        display_name: str
        reseller_id: str
        subscription_id: str
        workload: Union[str, Workload]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[PutAliasRequestAdditionalProperties] = ..., 
                billing_scope: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                reseller_id: Optional[str] = ..., 
                subscription_id: Optional[str] = ..., 
                workload: Optional[Union[str, Workload]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.subscription.models.PutTenantPolicyRequestProperties(Model):
        block_subscriptions_into_tenant: bool
        block_subscriptions_leaving_tenant: bool
        exempted_principals: list[str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                block_subscriptions_into_tenant: Optional[bool] = ..., 
                block_subscriptions_leaving_tenant: Optional[bool] = ..., 
                exempted_principals: Optional[List[str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.subscription.models.RenamedSubscriptionId(Model):
        subscription_id: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.subscription.models.ServiceTenantResponse(Model):
        tenant_id: str
        tenant_name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                tenant_id: Optional[str] = ..., 
                tenant_name: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.subscription.models.SpendingLimit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CURRENT_PERIOD_OFF = "CurrentPeriodOff"
        OFF = "Off"
        ON = "On"


    class azure.mgmt.subscription.models.Subscription(Model):
        authorization_source: str
        display_name: str
        id: str
        state: Union[str, SubscriptionState]
        subscription_id: str
        subscription_policies: SubscriptionPolicies
        tags: dict[str, str]
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                authorization_source: Optional[str] = ..., 
                subscription_policies: Optional[SubscriptionPolicies] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.subscription.models.SubscriptionAliasListResult(Model):
        next_link: str
        value: list[SubscriptionAliasResponse]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.subscription.models.SubscriptionAliasResponse(Model):
        id: str
        name: str
        properties: SubscriptionAliasResponseProperties
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                properties: Optional[SubscriptionAliasResponseProperties] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.subscription.models.SubscriptionAliasResponseProperties(Model):
        accept_ownership_state: Union[str, AcceptOwnership]
        accept_ownership_url: str
        billing_scope: str
        created_time: str
        display_name: str
        management_group_id: str
        provisioning_state: Union[str, ProvisioningState]
        reseller_id: str
        subscription_id: str
        subscription_owner_id: str
        tags: dict[str, str]
        workload: Union[str, Workload]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                billing_scope: Optional[str] = ..., 
                created_time: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                management_group_id: Optional[str] = ..., 
                provisioning_state: Optional[Union[str, ProvisioningState]] = ..., 
                reseller_id: Optional[str] = ..., 
                subscription_owner_id: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                workload: Optional[Union[str, Workload]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.subscription.models.SubscriptionListResult(Model):
        next_link: str
        value: list[Subscription]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Subscription]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.subscription.models.SubscriptionName(Model):
        subscription_name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                subscription_name: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.subscription.models.SubscriptionPolicies(Model):
        location_placement_id: str
        quota_id: str
        spending_limit: Union[str, SpendingLimit]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.subscription.models.SubscriptionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETED = "Deleted"
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        PAST_DUE = "PastDue"
        WARNED = "Warned"


    class azure.mgmt.subscription.models.SystemData(Model):
        created_at: datetime
        created_by: str
        created_by_type: Union[str, CreatedByType]
        last_modified_at: datetime
        last_modified_by: str
        last_modified_by_type: Union[str, CreatedByType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                created_by_type: Optional[Union[str, CreatedByType]] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_by_type: Optional[Union[str, CreatedByType]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.subscription.models.TenantIdDescription(Model):
        country: str
        country_code: str
        default_domain: str
        display_name: str
        domains: str
        id: str
        tenant_category: str
        tenant_id: str
        tenant_type: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.subscription.models.TenantListResult(Model):
        next_link: str
        value: list[TenantIdDescription]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: str, 
                value: Optional[List[TenantIdDescription]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.subscription.models.TenantPolicy(Model):
        block_subscriptions_into_tenant: bool
        block_subscriptions_leaving_tenant: bool
        exempted_principals: list[str]
        policy_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                block_subscriptions_into_tenant: Optional[bool] = ..., 
                block_subscriptions_leaving_tenant: Optional[bool] = ..., 
                exempted_principals: Optional[List[str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.subscription.models.Workload(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEV_TEST = "DevTest"
        PRODUCTION = "Production"


namespace azure.mgmt.subscription.operations

    class azure.mgmt.subscription.operations.AliasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                alias_name: str, 
                body: PutAliasRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SubscriptionAliasResponse]: ...

        @overload
        def begin_create(
                self, 
                alias_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SubscriptionAliasResponse]: ...

        @distributed_trace
        def delete(
                self, 
                alias_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                alias_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SubscriptionAliasResponse: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SubscriptionAliasListResult: ...


    class azure.mgmt.subscription.operations.BillingAccountOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get_policy(
                self, 
                billing_account_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> BillingAccountPoliciesResponse: ...


    class azure.mgmt.subscription.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Operation]: ...


    class azure.mgmt.subscription.operations.SubscriptionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def accept_ownership_status(
                self, 
                subscription_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AcceptOwnershipStatusResponse: ...

        @overload
        def begin_accept_ownership(
                self, 
                subscription_id: str, 
                body: AcceptOwnershipRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_accept_ownership(
                self, 
                subscription_id: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def cancel(
                self, 
                subscription_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> CanceledSubscriptionId: ...

        @distributed_trace
        def enable(
                self, 
                subscription_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> EnabledSubscriptionId: ...

        @overload
        def rename(
                self, 
                subscription_id: str, 
                body: SubscriptionName, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RenamedSubscriptionId: ...

        @overload
        def rename(
                self, 
                subscription_id: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RenamedSubscriptionId: ...


    class azure.mgmt.subscription.operations.SubscriptionPolicyOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def add_update_policy_for_tenant(
                self, 
                body: PutTenantPolicyRequestProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GetTenantPolicyResponse: ...

        @overload
        def add_update_policy_for_tenant(
                self, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GetTenantPolicyResponse: ...

        @distributed_trace
        def get_policy_for_tenant(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> GetTenantPolicyResponse: ...

        @distributed_trace
        def list_policy_for_tenant(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[GetTenantPolicyResponse]: ...


    class azure.mgmt.subscription.operations.SubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                subscription_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Subscription: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Subscription]: ...

        @distributed_trace
        def list_locations(
                self, 
                subscription_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Location]: ...


    class azure.mgmt.subscription.operations.TenantsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[TenantIdDescription]: ...


```