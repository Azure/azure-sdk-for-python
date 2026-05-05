```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.powerbidedicated

    class azure.mgmt.powerbidedicated.PowerBIDedicated: implements ContextManager 
        auto_scale_vcores: AutoScaleVCoresOperations
        capacities: CapacitiesOperations
        operations: Operations

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


namespace azure.mgmt.powerbidedicated.aio

    class azure.mgmt.powerbidedicated.aio.PowerBIDedicated: implements AsyncContextManager 
        auto_scale_vcores: AutoScaleVCoresOperations
        capacities: CapacitiesOperations
        operations: Operations

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


namespace azure.mgmt.powerbidedicated.aio.operations

    class azure.mgmt.powerbidedicated.aio.operations.AutoScaleVCoresOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                vcore_name: str, 
                v_core_parameters: AutoScaleVCore, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoScaleVCore: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                vcore_name: str, 
                v_core_parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoScaleVCore: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                vcore_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vcore_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AutoScaleVCore: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[AutoScaleVCore]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[AutoScaleVCore]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                vcore_name: str, 
                v_core_update_parameters: AutoScaleVCoreUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoScaleVCore: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                vcore_name: str, 
                v_core_update_parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoScaleVCore: ...


    class azure.mgmt.powerbidedicated.aio.operations.CapacitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                dedicated_capacity_name: str, 
                capacity_parameters: DedicatedCapacity, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DedicatedCapacity]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                dedicated_capacity_name: str, 
                capacity_parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DedicatedCapacity]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                dedicated_capacity_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_resume(
                self, 
                resource_group_name: str, 
                dedicated_capacity_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_suspend(
                self, 
                resource_group_name: str, 
                dedicated_capacity_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dedicated_capacity_name: str, 
                capacity_update_parameters: DedicatedCapacityUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DedicatedCapacity]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dedicated_capacity_name: str, 
                capacity_update_parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DedicatedCapacity]: ...

        @overload
        async def check_name_availability(
                self, 
                location: str, 
                capacity_parameters: CheckCapacityNameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckCapacityNameAvailabilityResult: ...

        @overload
        async def check_name_availability(
                self, 
                location: str, 
                capacity_parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckCapacityNameAvailabilityResult: ...

        @distributed_trace_async
        async def get_details(
                self, 
                resource_group_name: str, 
                dedicated_capacity_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> DedicatedCapacity: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[DedicatedCapacity]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[DedicatedCapacity]: ...

        @distributed_trace_async
        async def list_skus(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SkuEnumerationForNewResourceResult: ...

        @distributed_trace_async
        async def list_skus_for_capacity(
                self, 
                resource_group_name: str, 
                dedicated_capacity_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SkuEnumerationForExistingResourceResult: ...


    class azure.mgmt.powerbidedicated.aio.operations.Operations:

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


namespace azure.mgmt.powerbidedicated.models

    class azure.mgmt.powerbidedicated.models.AutoScaleVCore(Resource):
        capacity_limit: int
        capacity_object_id: str
        id: str
        location: str
        name: str
        provisioning_state: Union[str, VCoreProvisioningState]
        sku: AutoScaleVCoreSku
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                capacity_limit: Optional[int] = ..., 
                capacity_object_id: Optional[str] = ..., 
                location: str, 
                sku: AutoScaleVCoreSku, 
                system_data: Optional[SystemData] = ..., 
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


    class azure.mgmt.powerbidedicated.models.AutoScaleVCoreListResult(Model):
        value: list[AutoScaleVCore]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: List[AutoScaleVCore], 
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


    class azure.mgmt.powerbidedicated.models.AutoScaleVCoreMutableProperties(Model):
        capacity_limit: int

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                capacity_limit: Optional[int] = ..., 
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


    class azure.mgmt.powerbidedicated.models.AutoScaleVCoreProperties(AutoScaleVCoreMutableProperties):
        capacity_limit: int
        capacity_object_id: str
        provisioning_state: Union[str, VCoreProvisioningState]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                capacity_limit: Optional[int] = ..., 
                capacity_object_id: Optional[str] = ..., 
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


    class azure.mgmt.powerbidedicated.models.AutoScaleVCoreSku(Model):
        capacity: int
        name: str
        tier: Union[str, VCoreSkuTier]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                name: str, 
                tier: Optional[Union[str, VCoreSkuTier]] = ..., 
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


    class azure.mgmt.powerbidedicated.models.AutoScaleVCoreUpdateParameters(Model):
        capacity_limit: int
        sku: AutoScaleVCoreSku
        tags: dict[str, str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                capacity_limit: Optional[int] = ..., 
                sku: Optional[AutoScaleVCoreSku] = ..., 
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


    class azure.mgmt.powerbidedicated.models.CapacityProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETING = "Deleting"
        FAILED = "Failed"
        PAUSED = "Paused"
        PAUSING = "Pausing"
        PREPARING = "Preparing"
        PROVISIONING = "Provisioning"
        RESUMING = "Resuming"
        SCALING = "Scaling"
        SUCCEEDED = "Succeeded"
        SUSPENDED = "Suspended"
        SUSPENDING = "Suspending"
        UPDATING = "Updating"


    class azure.mgmt.powerbidedicated.models.CapacitySku(Model):
        capacity: int
        name: str
        tier: Union[str, CapacitySkuTier]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                name: str, 
                tier: Optional[Union[str, CapacitySkuTier]] = ..., 
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


    class azure.mgmt.powerbidedicated.models.CapacitySkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO_PREMIUM_HOST = "AutoPremiumHost"
        PBIE_AZURE = "PBIE_Azure"
        PREMIUM = "Premium"


    class azure.mgmt.powerbidedicated.models.CheckCapacityNameAvailabilityParameters(Model):
        name: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: str = "Microsoft.PowerBIDedicated/capacities", 
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


    class azure.mgmt.powerbidedicated.models.CheckCapacityNameAvailabilityResult(Model):
        message: str
        name_available: bool
        reason: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                name_available: Optional[bool] = ..., 
                reason: Optional[str] = ..., 
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


    class azure.mgmt.powerbidedicated.models.DedicatedCapacities(Model):
        value: list[DedicatedCapacity]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: List[DedicatedCapacity], 
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


    class azure.mgmt.powerbidedicated.models.DedicatedCapacity(Resource):
        administration: DedicatedCapacityAdministrators
        friendly_name: str
        id: str
        location: str
        mode: Union[str, Mode]
        name: str
        provisioning_state: Union[str, CapacityProvisioningState]
        sku: CapacitySku
        state: Union[str, State]
        system_data: SystemData
        tags: dict[str, str]
        tenant_id: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                administration: Optional[DedicatedCapacityAdministrators] = ..., 
                location: str, 
                mode: Optional[Union[str, Mode]] = ..., 
                sku: CapacitySku, 
                system_data: Optional[SystemData] = ..., 
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


    class azure.mgmt.powerbidedicated.models.DedicatedCapacityAdministrators(Model):
        members: list[str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                members: Optional[List[str]] = ..., 
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


    class azure.mgmt.powerbidedicated.models.DedicatedCapacityMutableProperties(Model):
        administration: DedicatedCapacityAdministrators
        friendly_name: str
        mode: Union[str, Mode]
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                administration: Optional[DedicatedCapacityAdministrators] = ..., 
                mode: Optional[Union[str, Mode]] = ..., 
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


    class azure.mgmt.powerbidedicated.models.DedicatedCapacityProperties(DedicatedCapacityMutableProperties):
        administration: DedicatedCapacityAdministrators
        friendly_name: str
        mode: Union[str, Mode]
        provisioning_state: Union[str, CapacityProvisioningState]
        state: Union[str, State]
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                administration: Optional[DedicatedCapacityAdministrators] = ..., 
                mode: Optional[Union[str, Mode]] = ..., 
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


    class azure.mgmt.powerbidedicated.models.DedicatedCapacityUpdateParameters(Model):
        administration: DedicatedCapacityAdministrators
        friendly_name: str
        mode: Union[str, Mode]
        sku: CapacitySku
        tags: dict[str, str]
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                administration: Optional[DedicatedCapacityAdministrators] = ..., 
                mode: Optional[Union[str, Mode]] = ..., 
                sku: Optional[CapacitySku] = ..., 
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


    class azure.mgmt.powerbidedicated.models.ErrorResponse(Model):
        error: ErrorResponseError

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorResponseError] = ..., 
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


    class azure.mgmt.powerbidedicated.models.ErrorResponseError(Model):
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


    class azure.mgmt.powerbidedicated.models.IdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.powerbidedicated.models.LogSpecification(Model):
        blob_duration: str
        display_name: str
        name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
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


    class azure.mgmt.powerbidedicated.models.MetricSpecification(Model):
        aggregation_type: str
        dimensions: list[MetricSpecificationDimensionsItem]
        display_description: str
        display_name: str
        metric_filter_pattern: str
        name: str
        unit: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                dimensions: Optional[List[MetricSpecificationDimensionsItem]] = ..., 
                display_description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
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


    class azure.mgmt.powerbidedicated.models.MetricSpecificationDimensionsItem(Model):
        display_name: str
        name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
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


    class azure.mgmt.powerbidedicated.models.Mode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GEN1 = "Gen1"
        GEN2 = "Gen2"


    class azure.mgmt.powerbidedicated.models.Operation(Model):
        display: OperationDisplay
        name: str
        origin: str
        properties: OperationProperties

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                properties: Optional[OperationProperties] = ..., 
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


    class azure.mgmt.powerbidedicated.models.OperationDisplay(Model):
        description: str
        operation: str
        provider: str
        resource: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
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


    class azure.mgmt.powerbidedicated.models.OperationListResult(Model):
        next_link: str
        value: list[Operation]

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


    class azure.mgmt.powerbidedicated.models.OperationProperties(Model):
        service_specification: ServiceSpecification

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                service_specification: Optional[ServiceSpecification] = ..., 
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


    class azure.mgmt.powerbidedicated.models.Resource(Model):
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                location: str, 
                system_data: Optional[SystemData] = ..., 
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


    class azure.mgmt.powerbidedicated.models.ServiceSpecification(Model):
        log_specifications: list[LogSpecification]
        metric_specifications: list[MetricSpecification]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                log_specifications: Optional[List[LogSpecification]] = ..., 
                metric_specifications: Optional[List[MetricSpecification]] = ..., 
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


    class azure.mgmt.powerbidedicated.models.SkuDetailsForExistingResource(Model):
        resource_type: str
        sku: CapacitySku

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                resource_type: Optional[str] = ..., 
                sku: Optional[CapacitySku] = ..., 
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


    class azure.mgmt.powerbidedicated.models.SkuEnumerationForExistingResourceResult(Model):
        value: list[SkuDetailsForExistingResource]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: Optional[List[SkuDetailsForExistingResource]] = ..., 
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


    class azure.mgmt.powerbidedicated.models.SkuEnumerationForNewResourceResult(Model):
        value: list[CapacitySku]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: Optional[List[CapacitySku]] = ..., 
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


    class azure.mgmt.powerbidedicated.models.State(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETING = "Deleting"
        FAILED = "Failed"
        PAUSED = "Paused"
        PAUSING = "Pausing"
        PREPARING = "Preparing"
        PROVISIONING = "Provisioning"
        RESUMING = "Resuming"
        SCALING = "Scaling"
        SUCCEEDED = "Succeeded"
        SUSPENDED = "Suspended"
        SUSPENDING = "Suspending"
        UPDATING = "Updating"


    class azure.mgmt.powerbidedicated.models.SystemData(Model):
        created_at: datetime
        created_by: str
        created_by_type: Union[str, IdentityType]
        last_modified_at: datetime
        last_modified_by: str
        last_modified_by_type: Union[str, IdentityType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                created_by_type: Optional[Union[str, IdentityType]] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_by_type: Optional[Union[str, IdentityType]] = ..., 
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


    class azure.mgmt.powerbidedicated.models.VCoreProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SUCCEEDED = "Succeeded"


    class azure.mgmt.powerbidedicated.models.VCoreSkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO_SCALE = "AutoScale"


namespace azure.mgmt.powerbidedicated.operations

    class azure.mgmt.powerbidedicated.operations.AutoScaleVCoresOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                vcore_name: str, 
                v_core_parameters: AutoScaleVCore, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoScaleVCore: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                vcore_name: str, 
                v_core_parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoScaleVCore: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                vcore_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vcore_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AutoScaleVCore: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[AutoScaleVCore]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[AutoScaleVCore]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                vcore_name: str, 
                v_core_update_parameters: AutoScaleVCoreUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoScaleVCore: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                vcore_name: str, 
                v_core_update_parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoScaleVCore: ...


    class azure.mgmt.powerbidedicated.operations.CapacitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                dedicated_capacity_name: str, 
                capacity_parameters: DedicatedCapacity, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DedicatedCapacity]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                dedicated_capacity_name: str, 
                capacity_parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DedicatedCapacity]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                dedicated_capacity_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_resume(
                self, 
                resource_group_name: str, 
                dedicated_capacity_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_suspend(
                self, 
                resource_group_name: str, 
                dedicated_capacity_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dedicated_capacity_name: str, 
                capacity_update_parameters: DedicatedCapacityUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DedicatedCapacity]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dedicated_capacity_name: str, 
                capacity_update_parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DedicatedCapacity]: ...

        @overload
        def check_name_availability(
                self, 
                location: str, 
                capacity_parameters: CheckCapacityNameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckCapacityNameAvailabilityResult: ...

        @overload
        def check_name_availability(
                self, 
                location: str, 
                capacity_parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckCapacityNameAvailabilityResult: ...

        @distributed_trace
        def get_details(
                self, 
                resource_group_name: str, 
                dedicated_capacity_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> DedicatedCapacity: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[DedicatedCapacity]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[DedicatedCapacity]: ...

        @distributed_trace
        def list_skus(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SkuEnumerationForNewResourceResult: ...

        @distributed_trace
        def list_skus_for_capacity(
                self, 
                resource_group_name: str, 
                dedicated_capacity_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SkuEnumerationForExistingResourceResult: ...


    class azure.mgmt.powerbidedicated.operations.Operations:

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


```