```py
namespace azure.mgmt.edgeorder

    class azure.mgmt.edgeorder.EdgeOrderManagementClient: implements ContextManager 
        addresses: AddressesOperations
        operations: Operations
        order_items: OrderItemsOperations
        orders: OrdersOperations
        products_and_configurations: ProductsAndConfigurationsOperations

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


namespace azure.mgmt.edgeorder.aio

    class azure.mgmt.edgeorder.aio.EdgeOrderManagementClient: implements AsyncContextManager 
        addresses: AddressesOperations
        operations: Operations
        order_items: OrderItemsOperations
        orders: OrdersOperations
        products_and_configurations: ProductsAndConfigurationsOperations

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


namespace azure.mgmt.edgeorder.aio.operations

    class azure.mgmt.edgeorder.aio.operations.AddressesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                address_name: str, 
                address_resource: AddressResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AddressResource]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                address_name: str, 
                address_resource: AddressResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AddressResource]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                address_name: str, 
                address_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AddressResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                address_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                address_name: str, 
                address_update_parameter: AddressUpdateParameter, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[AddressResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                address_name: str, 
                address_update_parameter: AddressUpdateParameter, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[AddressResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                address_name: str, 
                address_update_parameter: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[AddressResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                address_name: str, 
                **kwargs: Any
            ) -> AddressResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AddressResource]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AddressResource]: ...


    class azure.mgmt.edgeorder.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.edgeorder.aio.operations.OrderItemsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                order_item_name: str, 
                order_item_resource: OrderItemResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OrderItemResource]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                order_item_name: str, 
                order_item_resource: OrderItemResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OrderItemResource]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                order_item_name: str, 
                order_item_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OrderItemResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                order_item_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_return_method(
                self, 
                resource_group_name: str, 
                order_item_name: str, 
                return_order_item_details: ReturnOrderItemDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_return_method(
                self, 
                resource_group_name: str, 
                order_item_name: str, 
                return_order_item_details: ReturnOrderItemDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_return_method(
                self, 
                resource_group_name: str, 
                order_item_name: str, 
                return_order_item_details: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                order_item_name: str, 
                order_item_update_parameter: OrderItemUpdateParameter, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OrderItemResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                order_item_name: str, 
                order_item_update_parameter: OrderItemUpdateParameter, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OrderItemResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                order_item_name: str, 
                order_item_update_parameter: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OrderItemResource]: ...

        @overload
        async def cancel(
                self, 
                resource_group_name: str, 
                order_item_name: str, 
                cancellation_reason: CancellationReason, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def cancel(
                self, 
                resource_group_name: str, 
                order_item_name: str, 
                cancellation_reason: CancellationReason, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def cancel(
                self, 
                resource_group_name: str, 
                order_item_name: str, 
                cancellation_reason: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                order_item_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> OrderItemResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[OrderItemResource]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[OrderItemResource]: ...


    class azure.mgmt.edgeorder.aio.operations.OrdersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                location: str, 
                order_name: str, 
                **kwargs: Any
            ) -> OrderResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[OrderResource]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[OrderResource]: ...


    class azure.mgmt.edgeorder.aio.operations.ProductsAndConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def list_configurations(
                self, 
                configurations_request: ConfigurationsRequest, 
                *, 
                content_type: str = "application/json", 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Configuration]: ...

        @overload
        def list_configurations(
                self, 
                configurations_request: ConfigurationsRequest, 
                *, 
                content_type: str = "application/json", 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Configuration]: ...

        @overload
        def list_configurations(
                self, 
                configurations_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Configuration]: ...

        @overload
        def list_product_families(
                self, 
                product_families_request: ProductFamiliesRequest, 
                *, 
                content_type: str = "application/json", 
                expand: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ProductFamily]: ...

        @overload
        def list_product_families(
                self, 
                product_families_request: ProductFamiliesRequest, 
                *, 
                content_type: str = "application/json", 
                expand: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ProductFamily]: ...

        @overload
        def list_product_families(
                self, 
                product_families_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                expand: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ProductFamily]: ...

        @distributed_trace
        def list_product_families_metadata(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ProductFamiliesMetadataDetails]: ...


namespace azure.mgmt.edgeorder.models

    class azure.mgmt.edgeorder.models.ActionStatusEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOWED = "Allowed"
        NOT_ALLOWED = "NotAllowed"


    class azure.mgmt.edgeorder.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.edgeorder.models.AdditionalConfiguration(_Model):
        hierarchy_information: HierarchyInformation
        provisioning_details: Optional[list[ProvisioningDetails]]
        quantity: int

        @overload
        def __init__(
                self, 
                *, 
                hierarchy_information: HierarchyInformation, 
                provisioning_details: Optional[list[ProvisioningDetails]] = ..., 
                quantity: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeorder.models.AddressClassification(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SHIPPING = "Shipping"
        SITE = "Site"


    class azure.mgmt.edgeorder.models.AddressDetails(_Model):
        forward_address: AddressProperties
        return_address: Optional[AddressProperties]

        @overload
        def __init__(
                self, 
                *, 
                forward_address: AddressProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeorder.models.AddressProperties(_Model):
        address_classification: Optional[Union[str, AddressClassification]]
        address_validation_status: Optional[Union[str, AddressValidationStatus]]
        contact_details: Optional[ContactDetails]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        shipping_address: Optional[ShippingAddress]

        @overload
        def __init__(
                self, 
                *, 
                address_classification: Optional[Union[str, AddressClassification]] = ..., 
                contact_details: Optional[ContactDetails] = ..., 
                shipping_address: Optional[ShippingAddress] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeorder.models.AddressResource(TrackedResource):
        id: str
        location: str
        name: str
        properties: AddressProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: AddressProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.edgeorder.models.AddressType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMMERCIAL = "Commercial"
        NONE = "None"
        RESIDENTIAL = "Residential"


    class azure.mgmt.edgeorder.models.AddressUpdateParameter(_Model):
        properties: Optional[AddressUpdateProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AddressUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.edgeorder.models.AddressUpdateProperties(_Model):
        contact_details: Optional[ContactDetails]
        shipping_address: Optional[ShippingAddress]

        @overload
        def __init__(
                self, 
                *, 
                contact_details: Optional[ContactDetails] = ..., 
                shipping_address: Optional[ShippingAddress] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeorder.models.AddressValidationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AMBIGUOUS = "Ambiguous"
        INVALID = "Invalid"
        VALID = "Valid"


    class azure.mgmt.edgeorder.models.AutoProvisioningStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.edgeorder.models.AvailabilityInformation(_Model):
        availability_stage: Optional[Union[str, AvailabilityStage]]
        disabled_reason: Optional[Union[str, DisabledReason]]
        disabled_reason_message: Optional[str]


    class azure.mgmt.edgeorder.models.AvailabilityStage(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        COMING_SOON = "ComingSoon"
        DEPRECATED = "Deprecated"
        DISCOVERABLE = "Discoverable"
        PREVIEW = "Preview"
        SIGNUP = "Signup"
        UNAVAILABLE = "Unavailable"


    class azure.mgmt.edgeorder.models.BasicInformation(_Model):
        availability_information: Optional[AvailabilityInformation]
        cost_information: Optional[CostInformation]
        description: Optional[Description]
        display_name: Optional[str]
        fulfilled_by: Optional[Union[str, FulfillmentType]]
        hierarchy_information: Optional[HierarchyInformation]
        image_information: Optional[list[ImageInformation]]


    class azure.mgmt.edgeorder.models.BillingMeterDetails(_Model):
        frequency: Optional[str]
        meter_details: Optional[MeterDetails]
        metering_type: Optional[Union[str, MeteringType]]
        name: Optional[str]
        term_type_details: Optional[TermTypeDetails]


    class azure.mgmt.edgeorder.models.BillingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PAV2 = "Pav2"
        PURCHASE = "Purchase"


    class azure.mgmt.edgeorder.models.CancellationReason(_Model):
        reason: str

        @overload
        def __init__(
                self, 
                *, 
                reason: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeorder.models.CategoryInformation(_Model):
        category_display_name: Optional[str]
        category_name: Optional[str]
        description: Optional[str]
        links: Optional[list[Link]]

        @overload
        def __init__(
                self, 
                *, 
                category_display_name: Optional[str] = ..., 
                category_name: Optional[str] = ..., 
                description: Optional[str] = ..., 
                links: Optional[list[Link]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeorder.models.ChargingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PER_DEVICE = "PerDevice"
        PER_ORDER = "PerOrder"


    class azure.mgmt.edgeorder.models.ChildConfiguration(_Model):
        properties: Optional[ChildConfigurationProperties]


    class azure.mgmt.edgeorder.models.ChildConfigurationFilter(_Model):
        child_configuration_types: Optional[list[Union[str, ChildConfigurationType]]]
        hierarchy_informations: Optional[list[HierarchyInformation]]

        @overload
        def __init__(
                self, 
                *, 
                child_configuration_types: Optional[list[Union[str, ChildConfigurationType]]] = ..., 
                hierarchy_informations: Optional[list[HierarchyInformation]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeorder.models.ChildConfigurationProperties(_Model):
        availability_information: Optional[AvailabilityInformation]
        child_configuration_type: Optional[Union[str, ChildConfigurationType]]
        child_configuration_types: Optional[list[Union[str, ChildConfigurationType]]]
        cost_information: Optional[CostInformation]
        description: Optional[Description]
        dimensions: Optional[Dimensions]
        display_name: Optional[str]
        filterable_properties: Optional[list[FilterableProperty]]
        fulfilled_by: Optional[Union[str, FulfillmentType]]
        grouped_child_configurations: Optional[list[GroupedChildConfigurations]]
        hierarchy_information: Optional[HierarchyInformation]
        image_information: Optional[list[ImageInformation]]
        is_part_of_base_configuration: Optional[bool]
        maximum_quantity: Optional[int]
        minimum_quantity: Optional[int]
        provisioning_support: Optional[Union[str, ProvisioningSupport]]
        specifications: Optional[list[Specification]]
        supported_term_commitment_durations: Optional[list[timedelta]]


    class azure.mgmt.edgeorder.models.ChildConfigurationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADDITIONAL_CONFIGURATION = "AdditionalConfiguration"
        DEVICE_CONFIGURATION = "DeviceConfiguration"


    class azure.mgmt.edgeorder.models.CommonProperties(BasicInformation):
        availability_information: AvailabilityInformation
        cost_information: CostInformation
        description: Description
        display_name: str
        filterable_properties: Optional[list[FilterableProperty]]
        fulfilled_by: Union[str, FulfillmentType]
        hierarchy_information: HierarchyInformation
        image_information: list[ImageInformation]


    class azure.mgmt.edgeorder.models.Configuration(_Model):
        properties: Optional[ConfigurationProperties]


    class azure.mgmt.edgeorder.models.ConfigurationDeviceDetails(_Model):
        device_details: Optional[list[DeviceDetails]]
        display_info: Optional[DisplayInfo]
        hierarchy_information: Optional[HierarchyInformation]
        identification_type: Optional[Union[str, IdentificationType]]
        quantity: Optional[int]
        term_commitment_information: Optional[TermCommitmentInformation]

        @overload
        def __init__(
                self, 
                *, 
                display_info: Optional[DisplayInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeorder.models.ConfigurationFilter(_Model):
        child_configuration_filter: Optional[ChildConfigurationFilter]
        filterable_property: Optional[list[FilterableProperty]]
        hierarchy_information: HierarchyInformation

        @overload
        def __init__(
                self, 
                *, 
                child_configuration_filter: Optional[ChildConfigurationFilter] = ..., 
                filterable_property: Optional[list[FilterableProperty]] = ..., 
                hierarchy_information: HierarchyInformation
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeorder.models.ConfigurationProperties(CommonProperties):
        availability_information: AvailabilityInformation
        child_configuration_types: Optional[list[Union[str, ChildConfigurationType]]]
        cost_information: CostInformation
        description: Description
        dimensions: Optional[Dimensions]
        display_name: str
        filterable_properties: list[FilterableProperty]
        fulfilled_by: Union[str, FulfillmentType]
        grouped_child_configurations: Optional[list[GroupedChildConfigurations]]
        hierarchy_information: HierarchyInformation
        image_information: list[ImageInformation]
        provisioning_support: Optional[Union[str, ProvisioningSupport]]
        specifications: Optional[list[Specification]]
        supported_term_commitment_durations: Optional[list[timedelta]]


    class azure.mgmt.edgeorder.models.ConfigurationsRequest(_Model):
        configuration_filter: Optional[ConfigurationFilter]
        customer_subscription_details: Optional[CustomerSubscriptionDetails]

        @overload
        def __init__(
                self, 
                *, 
                configuration_filter: Optional[ConfigurationFilter] = ..., 
                customer_subscription_details: Optional[CustomerSubscriptionDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeorder.models.ContactDetails(_Model):
        contact_name: Optional[str]
        email_list: Optional[list[str]]
        mobile: Optional[str]
        phone: Optional[str]
        phone_extension: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                contact_name: Optional[str] = ..., 
                email_list: Optional[list[str]] = ..., 
                mobile: Optional[str] = ..., 
                phone: Optional[str] = ..., 
                phone_extension: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeorder.models.CostInformation(_Model):
        billing_info_url: Optional[str]
        billing_meter_details: Optional[list[BillingMeterDetails]]


    class azure.mgmt.edgeorder.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.edgeorder.models.CustomerSubscriptionDetails(_Model):
        location_placement_id: Optional[str]
        quota_id: str
        registered_features: Optional[list[CustomerSubscriptionRegisteredFeatures]]

        @overload
        def __init__(
                self, 
                *, 
                location_placement_id: Optional[str] = ..., 
                quota_id: str, 
                registered_features: Optional[list[CustomerSubscriptionRegisteredFeatures]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeorder.models.CustomerSubscriptionRegisteredFeatures(_Model):
        name: Optional[str]
        state: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                state: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeorder.models.Description(_Model):
        attributes: Optional[list[str]]
        description_type: Optional[Union[str, DescriptionType]]
        keywords: Optional[list[str]]
        links: Optional[list[Link]]
        long_description: Optional[str]
        short_description: Optional[str]


    class azure.mgmt.edgeorder.models.DescriptionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASE = "Base"


    class azure.mgmt.edgeorder.models.DeviceDetails(_Model):
        display_serial_number: Optional[str]
        management_resource_id: Optional[str]
        management_resource_tenant_id: Optional[str]
        provisioning_details: Optional[ProvisioningDetails]
        provisioning_support: Optional[Union[str, ProvisioningSupport]]
        serial_number: Optional[str]


    class azure.mgmt.edgeorder.models.DevicePresenceVerificationDetails(_Model):
        message: Optional[str]
        status: Optional[Union[str, DevicePresenceVerificationStatus]]


    class azure.mgmt.edgeorder.models.DevicePresenceVerificationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        NOT_INITIATED = "NotInitiated"


    class azure.mgmt.edgeorder.models.Dimensions(_Model):
        depth: Optional[float]
        height: Optional[float]
        length: Optional[float]
        length_height_unit: Optional[Union[str, LengthHeightUnit]]
        weight: Optional[float]
        weight_unit: Optional[Union[str, WeightMeasurementUnit]]
        width: Optional[float]


    class azure.mgmt.edgeorder.models.DisabledReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COUNTRY = "Country"
        FEATURE = "Feature"
        NONE = "None"
        NOT_AVAILABLE = "NotAvailable"
        NO_SUBSCRIPTION_INFO = "NoSubscriptionInfo"
        OFFER_TYPE = "OfferType"
        OUT_OF_STOCK = "OutOfStock"
        REGION = "Region"


    class azure.mgmt.edgeorder.models.DisplayInfo(_Model):
        configuration_display_name: Optional[str]
        product_family_display_name: Optional[str]


    class azure.mgmt.edgeorder.models.DoubleEncryptionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.edgeorder.models.EncryptionPreferences(_Model):
        double_encryption_status: Optional[Union[str, DoubleEncryptionStatus]]

        @overload
        def __init__(
                self, 
                *, 
                double_encryption_status: Optional[Union[str, DoubleEncryptionStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeorder.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.edgeorder.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.edgeorder.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeorder.models.FilterableProperty(_Model):
        supported_values: list[str]
        type: Union[str, SupportedFilterTypes]

        @overload
        def __init__(
                self, 
                *, 
                supported_values: list[str], 
                type: Union[str, SupportedFilterTypes]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeorder.models.ForwardShippingDetails(_Model):
        carrier_display_name: Optional[str]
        carrier_name: Optional[str]
        tracking_id: Optional[str]
        tracking_url: Optional[str]


    class azure.mgmt.edgeorder.models.FulfillmentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXTERNAL = "External"
        MICROSOFT = "Microsoft"


    class azure.mgmt.edgeorder.models.GroupedChildConfigurations(_Model):
        category_information: Optional[CategoryInformation]
        child_configurations: Optional[list[ChildConfiguration]]


    class azure.mgmt.edgeorder.models.HierarchyInformation(_Model):
        configuration_id_display_name: Optional[str]
        configuration_name: Optional[str]
        product_family_name: Optional[str]
        product_line_name: Optional[str]
        product_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                configuration_id_display_name: Optional[str] = ..., 
                configuration_name: Optional[str] = ..., 
                product_family_name: Optional[str] = ..., 
                product_line_name: Optional[str] = ..., 
                product_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeorder.models.IdentificationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_SUPPORTED = "NotSupported"
        SERIAL_NUMBER = "SerialNumber"


    class azure.mgmt.edgeorder.models.ImageInformation(_Model):
        image_type: Optional[Union[str, ImageType]]
        image_url: Optional[str]


    class azure.mgmt.edgeorder.models.ImageType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BULLET_IMAGE = "BulletImage"
        GENERIC_IMAGE = "GenericImage"
        MAIN_IMAGE = "MainImage"


    class azure.mgmt.edgeorder.models.LengthHeightUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CM = "CM"
        IN = "IN"


    class azure.mgmt.edgeorder.models.Link(_Model):
        link_type: Optional[Union[str, LinkType]]
        link_url: Optional[str]


    class azure.mgmt.edgeorder.models.LinkType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISCOVERABLE = "Discoverable"
        DOCUMENTATION = "Documentation"
        GENERIC = "Generic"
        KNOW_MORE = "KnowMore"
        SIGN_UP = "SignUp"
        SPECIFICATION = "Specification"
        TERMS_AND_CONDITIONS = "TermsAndConditions"


    class azure.mgmt.edgeorder.models.ManagementResourcePreferences(_Model):
        preferred_management_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                preferred_management_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeorder.models.MeterDetails(_Model):
        billing_type: str
        charging_type: Optional[Union[str, ChargingType]]
        multiplier: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                billing_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeorder.models.MeteringType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADHOC = "Adhoc"
        ONE_TIME = "OneTime"
        RECURRING = "Recurring"


    class azure.mgmt.edgeorder.models.NotificationPreference(_Model):
        send_notification: bool
        stage_name: Union[str, NotificationStageName]

        @overload
        def __init__(
                self, 
                *, 
                send_notification: bool, 
                stage_name: Union[str, NotificationStageName]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeorder.models.NotificationStageName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELIVERED = "Delivered"
        SHIPPED = "Shipped"


    class azure.mgmt.edgeorder.models.Operation(_Model):
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


    class azure.mgmt.edgeorder.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.edgeorder.models.OrderItemCancellationEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLABLE = "Cancellable"
        CANCELLABLE_WITH_FEE = "CancellableWithFee"
        NOT_CANCELLABLE = "NotCancellable"


    class azure.mgmt.edgeorder.models.OrderItemDetails(_Model):
        cancellation_reason: Optional[str]
        cancellation_status: Optional[Union[str, OrderItemCancellationEnum]]
        current_stage: Optional[StageDetails]
        deletion_status: Optional[Union[str, ActionStatusEnum]]
        error: Optional[ErrorDetail]
        forward_shipping_details: Optional[ForwardShippingDetails]
        management_rp_details_list: Optional[list[ResourceProviderDetails]]
        notification_email_list: Optional[list[str]]
        order_item_mode: Optional[Union[str, OrderMode]]
        order_item_stage_history: Optional[list[StageDetails]]
        order_item_type: Union[str, OrderItemType]
        preferences: Optional[Preferences]
        product_details: ProductDetails
        return_reason: Optional[str]
        return_status: Optional[Union[str, OrderItemReturnEnum]]
        reverse_shipping_details: Optional[ReverseShippingDetails]
        site_details: Optional[SiteDetails]

        @overload
        def __init__(
                self, 
                *, 
                notification_email_list: Optional[list[str]] = ..., 
                order_item_mode: Optional[Union[str, OrderMode]] = ..., 
                order_item_type: Union[str, OrderItemType], 
                preferences: Optional[Preferences] = ..., 
                product_details: ProductDetails, 
                site_details: Optional[SiteDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeorder.models.OrderItemDetailsUpdateParameter(_Model):
        product_details: Optional[ProductDetailsUpdateParameter]
        site_details: Optional[SiteDetails]

        @overload
        def __init__(
                self, 
                *, 
                product_details: Optional[ProductDetailsUpdateParameter] = ..., 
                site_details: Optional[SiteDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeorder.models.OrderItemProperties(_Model):
        address_details: Optional[AddressDetails]
        order_id: str
        order_item_details: OrderItemDetails
        provisioning_state: Optional[Union[str, ProvisioningState]]
        start_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                address_details: Optional[AddressDetails] = ..., 
                order_id: str, 
                order_item_details: OrderItemDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeorder.models.OrderItemResource(TrackedResource):
        id: str
        identity: Optional[ResourceIdentity]
        location: str
        name: str
        properties: OrderItemProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ResourceIdentity] = ..., 
                location: str, 
                properties: OrderItemProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.edgeorder.models.OrderItemReturnEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_RETURNABLE = "NotReturnable"
        RETURNABLE = "Returnable"
        RETURNABLE_WITH_FEE = "ReturnableWithFee"


    class azure.mgmt.edgeorder.models.OrderItemType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXTERNAL = "External"
        PURCHASE = "Purchase"
        RENTAL = "Rental"


    class azure.mgmt.edgeorder.models.OrderItemUpdateParameter(_Model):
        identity: Optional[ResourceIdentity]
        properties: Optional[OrderItemUpdateProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ResourceIdentity] = ..., 
                properties: Optional[OrderItemUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.edgeorder.models.OrderItemUpdateProperties(_Model):
        forward_address: Optional[AddressProperties]
        notification_email_list: Optional[list[str]]
        order_item_details: Optional[OrderItemDetailsUpdateParameter]
        preferences: Optional[Preferences]

        @overload
        def __init__(
                self, 
                *, 
                forward_address: Optional[AddressProperties] = ..., 
                notification_email_list: Optional[list[str]] = ..., 
                order_item_details: Optional[OrderItemDetailsUpdateParameter] = ..., 
                preferences: Optional[Preferences] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeorder.models.OrderMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        DO_NOT_FULFILL = "DoNotFulfill"


    class azure.mgmt.edgeorder.models.OrderProperties(_Model):
        current_stage: Optional[StageDetails]
        order_item_ids: Optional[list[str]]
        order_mode: Optional[Union[str, OrderMode]]
        order_stage_history: Optional[list[StageDetails]]


    class azure.mgmt.edgeorder.models.OrderResource(ProxyResource):
        id: str
        name: str
        properties: OrderProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: OrderProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.edgeorder.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.edgeorder.models.Pav2MeterDetails(MeterDetails, discriminator='Pav2'):
        billing_type: Literal[BillingType.PAV2]
        charging_type: Union[str, ChargingType]
        meter_guid: Optional[str]
        multiplier: float

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeorder.models.Preferences(_Model):
        encryption_preferences: Optional[EncryptionPreferences]
        management_resource_preferences: Optional[ManagementResourcePreferences]
        notification_preferences: Optional[list[NotificationPreference]]
        term_commitment_preferences: Optional[TermCommitmentPreferences]
        transport_preferences: Optional[TransportPreferences]

        @overload
        def __init__(
                self, 
                *, 
                encryption_preferences: Optional[EncryptionPreferences] = ..., 
                management_resource_preferences: Optional[ManagementResourcePreferences] = ..., 
                notification_preferences: Optional[list[NotificationPreference]] = ..., 
                term_commitment_preferences: Optional[TermCommitmentPreferences] = ..., 
                transport_preferences: Optional[TransportPreferences] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeorder.models.Product(_Model):
        properties: Optional[ProductProperties]


    class azure.mgmt.edgeorder.models.ProductDetails(_Model):
        child_configuration_device_details: Optional[list[ConfigurationDeviceDetails]]
        display_info: Optional[DisplayInfo]
        hierarchy_information: HierarchyInformation
        identification_type: Optional[Union[str, IdentificationType]]
        opt_in_additional_configurations: Optional[list[AdditionalConfiguration]]
        parent_device_details: Optional[DeviceDetails]
        parent_provisioning_details: Optional[ProvisioningDetails]
        product_double_encryption_status: Optional[Union[str, DoubleEncryptionStatus]]
        term_commitment_information: Optional[TermCommitmentInformation]

        @overload
        def __init__(
                self, 
                *, 
                display_info: Optional[DisplayInfo] = ..., 
                hierarchy_information: HierarchyInformation, 
                opt_in_additional_configurations: Optional[list[AdditionalConfiguration]] = ..., 
                parent_provisioning_details: Optional[ProvisioningDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeorder.models.ProductDetailsUpdateParameter(_Model):
        parent_provisioning_details: Optional[ProvisioningDetails]

        @overload
        def __init__(
                self, 
                *, 
                parent_provisioning_details: Optional[ProvisioningDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeorder.models.ProductFamiliesMetadataDetails(_Model):
        properties: Optional[ProductFamilyProperties]


    class azure.mgmt.edgeorder.models.ProductFamiliesRequest(_Model):
        customer_subscription_details: Optional[CustomerSubscriptionDetails]
        filterable_properties: dict[str, list[FilterableProperty]]

        @overload
        def __init__(
                self, 
                *, 
                customer_subscription_details: Optional[CustomerSubscriptionDetails] = ..., 
                filterable_properties: dict[str, list[FilterableProperty]]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeorder.models.ProductFamily(_Model):
        properties: Optional[ProductFamilyProperties]


    class azure.mgmt.edgeorder.models.ProductFamilyProperties(CommonProperties):
        availability_information: AvailabilityInformation
        cost_information: CostInformation
        description: Description
        display_name: str
        filterable_properties: list[FilterableProperty]
        fulfilled_by: Union[str, FulfillmentType]
        hierarchy_information: HierarchyInformation
        image_information: list[ImageInformation]
        product_lines: Optional[list[ProductLine]]
        resource_provider_details: Optional[list[ResourceProviderDetails]]

        @overload
        def __init__(
                self, 
                *, 
                resource_provider_details: Optional[list[ResourceProviderDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeorder.models.ProductLine(_Model):
        properties: Optional[ProductLineProperties]


    class azure.mgmt.edgeorder.models.ProductLineProperties(CommonProperties):
        availability_information: AvailabilityInformation
        cost_information: CostInformation
        description: Description
        display_name: str
        filterable_properties: list[FilterableProperty]
        fulfilled_by: Union[str, FulfillmentType]
        hierarchy_information: HierarchyInformation
        image_information: list[ImageInformation]
        products: Optional[list[Product]]


    class azure.mgmt.edgeorder.models.ProductProperties(CommonProperties):
        availability_information: AvailabilityInformation
        configurations: Optional[list[Configuration]]
        cost_information: CostInformation
        description: Description
        display_name: str
        filterable_properties: list[FilterableProperty]
        fulfilled_by: Union[str, FulfillmentType]
        hierarchy_information: HierarchyInformation
        image_information: list[ImageInformation]


    class azure.mgmt.edgeorder.models.ProvisioningDetails(_Model):
        auto_provisioning_status: Optional[Union[str, AutoProvisioningStatus]]
        device_presence_verification: Optional[DevicePresenceVerificationDetails]
        management_resource_arm_id: Optional[str]
        provisioning_arm_id: Optional[str]
        provisioning_end_point: Optional[str]
        quantity: Optional[int]
        ready_to_connect_arm_id: Optional[str]
        serial_number: Optional[str]
        unique_device_identifier: Optional[str]
        vendor_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                auto_provisioning_status: Optional[Union[str, AutoProvisioningStatus]] = ..., 
                device_presence_verification: Optional[DevicePresenceVerificationDetails] = ..., 
                management_resource_arm_id: Optional[str] = ..., 
                provisioning_arm_id: Optional[str] = ..., 
                provisioning_end_point: Optional[str] = ..., 
                quantity: Optional[int] = ..., 
                ready_to_connect_arm_id: Optional[str] = ..., 
                serial_number: Optional[str] = ..., 
                vendor_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeorder.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.edgeorder.models.ProvisioningSupport(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLOUD_BASED = "CloudBased"
        MANUAL = "Manual"


    class azure.mgmt.edgeorder.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.edgeorder.models.PurchaseMeterDetails(MeterDetails, discriminator='Purchase'):
        billing_type: Literal[BillingType.PURCHASE]
        charging_type: Union[str, ChargingType]
        multiplier: float
        product_id: Optional[str]
        sku_id: Optional[str]
        term_id: Optional[str]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeorder.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.edgeorder.models.ResourceIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Optional[str]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[str] = ..., 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeorder.models.ResourceProviderDetails(_Model):
        resource_provider_namespace: Optional[str]


    class azure.mgmt.edgeorder.models.ReturnOrderItemDetails(_Model):
        return_address: Optional[AddressProperties]
        return_reason: str
        service_tag: Optional[str]
        shipping_box_required: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                return_address: Optional[AddressProperties] = ..., 
                return_reason: str, 
                service_tag: Optional[str] = ..., 
                shipping_box_required: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeorder.models.ReverseShippingDetails(_Model):
        carrier_display_name: Optional[str]
        carrier_name: Optional[str]
        sas_key_for_label: Optional[str]
        tracking_id: Optional[str]
        tracking_url: Optional[str]


    class azure.mgmt.edgeorder.models.ShippingAddress(_Model):
        address_type: Optional[Union[str, AddressType]]
        city: Optional[str]
        company_name: Optional[str]
        country: str
        postal_code: Optional[str]
        state_or_province: Optional[str]
        street_address1: Optional[str]
        street_address2: Optional[str]
        street_address3: Optional[str]
        zip_extended_code: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                address_type: Optional[Union[str, AddressType]] = ..., 
                city: Optional[str] = ..., 
                company_name: Optional[str] = ..., 
                country: str, 
                postal_code: Optional[str] = ..., 
                state_or_province: Optional[str] = ..., 
                street_address1: Optional[str] = ..., 
                street_address2: Optional[str] = ..., 
                street_address3: Optional[str] = ..., 
                zip_extended_code: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeorder.models.SiteDetails(_Model):
        site_id: str

        @overload
        def __init__(
                self, 
                *, 
                site_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeorder.models.Specification(_Model):
        name: Optional[str]
        value: Optional[str]


    class azure.mgmt.edgeorder.models.StageDetails(_Model):
        display_name: Optional[str]
        stage_name: Optional[Union[str, StageName]]
        stage_status: Optional[Union[str, StageStatus]]
        start_time: Optional[datetime]


    class azure.mgmt.edgeorder.models.StageName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "Cancelled"
        CONFIRMED = "Confirmed"
        DELIVERED = "Delivered"
        IN_REVIEW = "InReview"
        IN_USE = "InUse"
        PLACED = "Placed"
        READY_TO_SETUP = "ReadyToSetup"
        READY_TO_SHIP = "ReadyToShip"
        RETURNED_TO_MICROSOFT = "ReturnedToMicrosoft"
        RETURN_COMPLETED = "ReturnCompleted"
        RETURN_INITIATED = "ReturnInitiated"
        RETURN_PICKED_UP = "ReturnPickedUp"
        SHIPPED = "Shipped"


    class azure.mgmt.edgeorder.models.StageStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "Cancelled"
        CANCELLING = "Cancelling"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        NONE = "None"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.edgeorder.models.SupportedFilterTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DOUBLE_ENCRYPTION_STATUS = "DoubleEncryptionStatus"
        SHIP_TO_COUNTRIES = "ShipToCountries"


    class azure.mgmt.edgeorder.models.SystemData(_Model):
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


    class azure.mgmt.edgeorder.models.TermCommitmentInformation(_Model):
        pending_days_for_term: Optional[int]
        term_commitment_type: Union[str, TermCommitmentType]
        term_commitment_type_duration: Optional[timedelta]

        @overload
        def __init__(
                self, 
                *, 
                term_commitment_type: Union[str, TermCommitmentType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeorder.models.TermCommitmentPreferences(_Model):
        preferred_term_commitment_duration: Optional[timedelta]
        preferred_term_commitment_type: Union[str, TermCommitmentType]

        @overload
        def __init__(
                self, 
                *, 
                preferred_term_commitment_duration: Optional[timedelta] = ..., 
                preferred_term_commitment_type: Union[str, TermCommitmentType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeorder.models.TermCommitmentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        TIMED = "Timed"
        TRIAL = "Trial"


    class azure.mgmt.edgeorder.models.TermTypeDetails(_Model):
        term_type: Union[str, TermCommitmentType]
        term_type_duration: timedelta

        @overload
        def __init__(
                self, 
                *, 
                term_type: Union[str, TermCommitmentType], 
                term_type_duration: timedelta
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeorder.models.TrackedResource(Resource):
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeorder.models.TransportPreferences(_Model):
        preferred_shipment_type: Union[str, TransportShipmentTypes]

        @overload
        def __init__(
                self, 
                *, 
                preferred_shipment_type: Union[str, TransportShipmentTypes]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeorder.models.TransportShipmentTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOMER_MANAGED = "CustomerManaged"
        MICROSOFT_MANAGED = "MicrosoftManaged"


    class azure.mgmt.edgeorder.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.edgeorder.models.WeightMeasurementUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        KGS = "KGS"
        LBS = "LBS"


namespace azure.mgmt.edgeorder.operations

    class azure.mgmt.edgeorder.operations.AddressesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                address_name: str, 
                address_resource: AddressResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AddressResource]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                address_name: str, 
                address_resource: AddressResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AddressResource]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                address_name: str, 
                address_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AddressResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                address_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                address_name: str, 
                address_update_parameter: AddressUpdateParameter, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[AddressResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                address_name: str, 
                address_update_parameter: AddressUpdateParameter, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[AddressResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                address_name: str, 
                address_update_parameter: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[AddressResource]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                address_name: str, 
                **kwargs: Any
            ) -> AddressResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AddressResource]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AddressResource]: ...


    class azure.mgmt.edgeorder.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.edgeorder.operations.OrderItemsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                order_item_name: str, 
                order_item_resource: OrderItemResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OrderItemResource]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                order_item_name: str, 
                order_item_resource: OrderItemResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OrderItemResource]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                order_item_name: str, 
                order_item_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OrderItemResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                order_item_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_return_method(
                self, 
                resource_group_name: str, 
                order_item_name: str, 
                return_order_item_details: ReturnOrderItemDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_return_method(
                self, 
                resource_group_name: str, 
                order_item_name: str, 
                return_order_item_details: ReturnOrderItemDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_return_method(
                self, 
                resource_group_name: str, 
                order_item_name: str, 
                return_order_item_details: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                order_item_name: str, 
                order_item_update_parameter: OrderItemUpdateParameter, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[OrderItemResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                order_item_name: str, 
                order_item_update_parameter: OrderItemUpdateParameter, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[OrderItemResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                order_item_name: str, 
                order_item_update_parameter: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[OrderItemResource]: ...

        @overload
        def cancel(
                self, 
                resource_group_name: str, 
                order_item_name: str, 
                cancellation_reason: CancellationReason, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def cancel(
                self, 
                resource_group_name: str, 
                order_item_name: str, 
                cancellation_reason: CancellationReason, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def cancel(
                self, 
                resource_group_name: str, 
                order_item_name: str, 
                cancellation_reason: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                order_item_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> OrderItemResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[OrderItemResource]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[OrderItemResource]: ...


    class azure.mgmt.edgeorder.operations.OrdersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                location: str, 
                order_name: str, 
                **kwargs: Any
            ) -> OrderResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[OrderResource]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[OrderResource]: ...


    class azure.mgmt.edgeorder.operations.ProductsAndConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def list_configurations(
                self, 
                configurations_request: ConfigurationsRequest, 
                *, 
                content_type: str = "application/json", 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Configuration]: ...

        @overload
        def list_configurations(
                self, 
                configurations_request: ConfigurationsRequest, 
                *, 
                content_type: str = "application/json", 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Configuration]: ...

        @overload
        def list_configurations(
                self, 
                configurations_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Configuration]: ...

        @overload
        def list_product_families(
                self, 
                product_families_request: ProductFamiliesRequest, 
                *, 
                content_type: str = "application/json", 
                expand: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ProductFamily]: ...

        @overload
        def list_product_families(
                self, 
                product_families_request: ProductFamiliesRequest, 
                *, 
                content_type: str = "application/json", 
                expand: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ProductFamily]: ...

        @overload
        def list_product_families(
                self, 
                product_families_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                expand: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ProductFamily]: ...

        @distributed_trace
        def list_product_families_metadata(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ProductFamiliesMetadataDetails]: ...


namespace azure.mgmt.edgeorder.types

    class azure.mgmt.edgeorder.types.AdditionalConfiguration(TypedDict, total=False):
        key "hierarchyInformation": Required[HierarchyInformation]
        key "quantity": Required[int]
        hierarchy_information: HierarchyInformation
        provisioningDetails: list[ProvisioningDetails]
        provisioning_details: list[ProvisioningDetails]
        quantity: int


    class azure.mgmt.edgeorder.types.AddressDetails(TypedDict, total=False):
        key "forwardAddress": Required[AddressProperties]
        key "returnAddress": ForwardRef('AddressProperties', module='types')
        forward_address: AddressProperties
        return_address: AddressProperties


    class azure.mgmt.edgeorder.types.AddressProperties(TypedDict, total=False):
        key "addressClassification": Union[str, AddressClassification]
        key "addressValidationStatus": Union[str, AddressValidationStatus]
        key "contactDetails": ForwardRef('ContactDetails', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "shippingAddress": ForwardRef('ShippingAddress', module='types')
        address_classification: Union[str, AddressClassification]
        address_validation_status: Union[str, AddressValidationStatus]
        contact_details: ContactDetails
        provisioning_state: Union[str, ProvisioningState]
        shipping_address: ShippingAddress


    class azure.mgmt.edgeorder.types.AddressResource(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": Required[AddressProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: AddressProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.edgeorder.types.AddressUpdateParameter(TypedDict, total=False):
        key "properties": ForwardRef('AddressUpdateProperties', module='types')
        properties: AddressUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.edgeorder.types.AddressUpdateProperties(TypedDict, total=False):
        key "contactDetails": ForwardRef('ContactDetails', module='types')
        key "shippingAddress": ForwardRef('ShippingAddress', module='types')
        contact_details: ContactDetails
        shipping_address: ShippingAddress


    class azure.mgmt.edgeorder.types.AvailabilityInformation(TypedDict, total=False):
        key "availabilityStage": Union[str, AvailabilityStage]
        key "disabledReason": Union[str, DisabledReason]
        key "disabledReasonMessage": str
        availability_stage: Union[str, AvailabilityStage]
        disabled_reason: Union[str, DisabledReason]
        disabled_reason_message: str


    class azure.mgmt.edgeorder.types.BasicInformation(TypedDict, total=False):
        key "availabilityInformation": ForwardRef('AvailabilityInformation', module='types')
        key "costInformation": ForwardRef('CostInformation', module='types')
        key "description": ForwardRef('Description', module='types')
        key "displayName": str
        key "fulfilledBy": Union[str, FulfillmentType]
        key "hierarchyInformation": ForwardRef('HierarchyInformation', module='types')
        availability_information: AvailabilityInformation
        cost_information: CostInformation
        description: Description
        display_name: str
        fulfilled_by: Union[str, FulfillmentType]
        hierarchy_information: HierarchyInformation
        imageInformation: list[ImageInformation]
        image_information: list[ImageInformation]


    class azure.mgmt.edgeorder.types.BillingMeterDetails(TypedDict, total=False):
        key "frequency": str
        key "meterDetails": ForwardRef('MeterDetails', module='types')
        key "meteringType": Union[str, MeteringType]
        key "name": str
        key "termTypeDetails": ForwardRef('TermTypeDetails', module='types')
        frequency: str
        meter_details: MeterDetails
        metering_type: Union[str, MeteringType]
        name: str
        term_type_details: TermTypeDetails


    class azure.mgmt.edgeorder.types.BillingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PAV2 = "Pav2"
        PURCHASE = "Purchase"


    class azure.mgmt.edgeorder.types.CancellationReason(TypedDict, total=False):
        key "reason": Required[str]
        reason: str


    class azure.mgmt.edgeorder.types.CategoryInformation(TypedDict, total=False):
        key "categoryDisplayName": str
        key "categoryName": str
        key "description": str
        category_display_name: str
        category_name: str
        description: str
        links: list[Link]


    class azure.mgmt.edgeorder.types.ChildConfiguration(TypedDict, total=False):
        key "properties": ForwardRef('ChildConfigurationProperties', module='types')
        properties: ChildConfigurationProperties


    class azure.mgmt.edgeorder.types.ChildConfigurationFilter(TypedDict, total=False):
        childConfigurationTypes: list[Union[str, ChildConfigurationType]]
        child_configuration_types: list[Union[str, ChildConfigurationType]]
        hierarchyInformations: list[HierarchyInformation]
        hierarchy_informations: list[HierarchyInformation]


    class azure.mgmt.edgeorder.types.ChildConfigurationProperties(TypedDict, total=False):
        key "availabilityInformation": ForwardRef('AvailabilityInformation', module='types')
        key "childConfigurationType": Union[str, ChildConfigurationType]
        key "costInformation": ForwardRef('CostInformation', module='types')
        key "description": ForwardRef('Description', module='types')
        key "dimensions": ForwardRef('Dimensions', module='types')
        key "displayName": str
        key "fulfilledBy": Union[str, FulfillmentType]
        key "hierarchyInformation": ForwardRef('HierarchyInformation', module='types')
        key "isPartOfBaseConfiguration": bool
        key "maximumQuantity": int
        key "minimumQuantity": int
        key "provisioningSupport": Union[str, ProvisioningSupport]
        availability_information: AvailabilityInformation
        childConfigurationTypes: list[Union[str, ChildConfigurationType]]
        child_configuration_type: Union[str, ChildConfigurationType]
        child_configuration_types: list[Union[str, ChildConfigurationType]]
        cost_information: CostInformation
        description: Description
        dimensions: Dimensions
        display_name: str
        filterableProperties: list[FilterableProperty]
        filterable_properties: list[FilterableProperty]
        fulfilled_by: Union[str, FulfillmentType]
        groupedChildConfigurations: list[GroupedChildConfigurations]
        grouped_child_configurations: list[GroupedChildConfigurations]
        hierarchy_information: HierarchyInformation
        imageInformation: list[ImageInformation]
        image_information: list[ImageInformation]
        is_part_of_base_configuration: bool
        maximum_quantity: int
        minimum_quantity: int
        provisioning_support: Union[str, ProvisioningSupport]
        specifications: list[Specification]
        supportedTermCommitmentDurations: list[str]
        supported_term_commitment_durations: list[str]


    class azure.mgmt.edgeorder.types.CommonProperties(BasicInformation):
        key "availabilityInformation": ForwardRef('AvailabilityInformation', module='types')
        key "costInformation": ForwardRef('CostInformation', module='types')
        key "description": ForwardRef('Description', module='types')
        key "displayName": str
        key "fulfilledBy": Union[str, FulfillmentType]
        key "hierarchyInformation": ForwardRef('HierarchyInformation', module='types')
        availability_information: AvailabilityInformation
        cost_information: CostInformation
        description: Description
        display_name: str
        filterableProperties: list[FilterableProperty]
        filterable_properties: list[FilterableProperty]
        fulfilled_by: Union[str, FulfillmentType]
        hierarchy_information: HierarchyInformation
        imageInformation: list[ImageInformation]
        image_information: list[ImageInformation]


    class azure.mgmt.edgeorder.types.Configuration(TypedDict, total=False):
        key "properties": ForwardRef('ConfigurationProperties', module='types')
        properties: ConfigurationProperties


    class azure.mgmt.edgeorder.types.ConfigurationDeviceDetails(TypedDict, total=False):
        key "displayInfo": ForwardRef('DisplayInfo', module='types')
        key "hierarchyInformation": ForwardRef('HierarchyInformation', module='types')
        key "identificationType": Union[str, IdentificationType]
        key "quantity": int
        key "termCommitmentInformation": ForwardRef('TermCommitmentInformation', module='types')
        deviceDetails: list[DeviceDetails]
        device_details: list[DeviceDetails]
        display_info: DisplayInfo
        hierarchy_information: HierarchyInformation
        identification_type: Union[str, IdentificationType]
        quantity: int
        term_commitment_information: TermCommitmentInformation


    class azure.mgmt.edgeorder.types.ConfigurationFilter(TypedDict, total=False):
        key "childConfigurationFilter": ForwardRef('ChildConfigurationFilter', module='types')
        key "hierarchyInformation": Required[HierarchyInformation]
        child_configuration_filter: ChildConfigurationFilter
        filterableProperty: list[FilterableProperty]
        filterable_property: list[FilterableProperty]
        hierarchy_information: HierarchyInformation


    class azure.mgmt.edgeorder.types.ConfigurationProperties(CommonProperties):
        key "availabilityInformation": ForwardRef('AvailabilityInformation', module='types')
        key "costInformation": ForwardRef('CostInformation', module='types')
        key "description": ForwardRef('Description', module='types')
        key "dimensions": ForwardRef('Dimensions', module='types')
        key "displayName": str
        key "fulfilledBy": Union[str, FulfillmentType]
        key "hierarchyInformation": ForwardRef('HierarchyInformation', module='types')
        key "provisioningSupport": Union[str, ProvisioningSupport]
        availability_information: AvailabilityInformation
        childConfigurationTypes: list[Union[str, ChildConfigurationType]]
        child_configuration_types: list[Union[str, ChildConfigurationType]]
        cost_information: CostInformation
        description: Description
        dimensions: Dimensions
        display_name: str
        filterableProperties: list[FilterableProperty]
        filterable_properties: list[FilterableProperty]
        fulfilled_by: Union[str, FulfillmentType]
        groupedChildConfigurations: list[GroupedChildConfigurations]
        grouped_child_configurations: list[GroupedChildConfigurations]
        hierarchy_information: HierarchyInformation
        imageInformation: list[ImageInformation]
        image_information: list[ImageInformation]
        provisioning_support: Union[str, ProvisioningSupport]
        specifications: list[Specification]
        supportedTermCommitmentDurations: list[str]
        supported_term_commitment_durations: list[str]


    class azure.mgmt.edgeorder.types.ConfigurationsRequest(TypedDict, total=False):
        key "configurationFilter": ForwardRef('ConfigurationFilter', module='types')
        key "customerSubscriptionDetails": ForwardRef('CustomerSubscriptionDetails', module='types')
        configuration_filter: ConfigurationFilter
        customer_subscription_details: CustomerSubscriptionDetails


    class azure.mgmt.edgeorder.types.ContactDetails(TypedDict, total=False):
        key "contactName": str
        key "mobile": str
        key "phone": str
        key "phoneExtension": str
        contact_name: str
        emailList: list[str]
        email_list: list[str]
        mobile: str
        phone: str
        phone_extension: str


    class azure.mgmt.edgeorder.types.CostInformation(TypedDict, total=False):
        key "billingInfoUrl": str
        billingMeterDetails: list[BillingMeterDetails]
        billing_info_url: str
        billing_meter_details: list[BillingMeterDetails]


    class azure.mgmt.edgeorder.types.CustomerSubscriptionDetails(TypedDict, total=False):
        key "locationPlacementId": str
        key "quotaId": Required[str]
        location_placement_id: str
        quota_id: str
        registeredFeatures: list[CustomerSubscriptionRegisteredFeatures]
        registered_features: list[CustomerSubscriptionRegisteredFeatures]


    class azure.mgmt.edgeorder.types.CustomerSubscriptionRegisteredFeatures(TypedDict, total=False):
        key "name": str
        key "state": str
        name: str
        state: str


    class azure.mgmt.edgeorder.types.Description(TypedDict, total=False):
        key "descriptionType": Union[str, DescriptionType]
        key "longDescription": str
        key "shortDescription": str
        attributes: list[str]
        description_type: Union[str, DescriptionType]
        keywords: list[str]
        links: list[Link]
        long_description: str
        short_description: str


    class azure.mgmt.edgeorder.types.DeviceDetails(TypedDict, total=False):
        key "displaySerialNumber": str
        key "managementResourceId": str
        key "managementResourceTenantId": str
        key "provisioningDetails": ForwardRef('ProvisioningDetails', module='types')
        key "provisioningSupport": Union[str, ProvisioningSupport]
        key "serialNumber": str
        display_serial_number: str
        management_resource_id: str
        management_resource_tenant_id: str
        provisioning_details: ProvisioningDetails
        provisioning_support: Union[str, ProvisioningSupport]
        serial_number: str


    class azure.mgmt.edgeorder.types.DevicePresenceVerificationDetails(TypedDict, total=False):
        key "message": str
        key "status": Union[str, DevicePresenceVerificationStatus]
        message: str
        status: Union[str, DevicePresenceVerificationStatus]


    class azure.mgmt.edgeorder.types.Dimensions(TypedDict, total=False):
        key "depth": float
        key "height": float
        key "length": float
        key "lengthHeightUnit": Union[str, LengthHeightUnit]
        key "weight": float
        key "weightUnit": Union[str, WeightMeasurementUnit]
        key "width": float
        depth: float
        height: float
        length: float
        length_height_unit: Union[str, LengthHeightUnit]
        weight: float
        weight_unit: Union[str, WeightMeasurementUnit]
        width: float


    class azure.mgmt.edgeorder.types.DisplayInfo(TypedDict, total=False):
        key "configurationDisplayName": str
        key "productFamilyDisplayName": str
        configuration_display_name: str
        product_family_display_name: str


    class azure.mgmt.edgeorder.types.EncryptionPreferences(TypedDict, total=False):
        key "doubleEncryptionStatus": Union[str, DoubleEncryptionStatus]
        double_encryption_status: Union[str, DoubleEncryptionStatus]


    class azure.mgmt.edgeorder.types.ErrorAdditionalInfo(TypedDict, total=False):
        key "info": Any
        key "type": str
        info: Any
        type: str


    class azure.mgmt.edgeorder.types.ErrorDetail(TypedDict, total=False):
        key "code": str
        key "message": str
        key "target": str
        additionalInfo: list[ErrorAdditionalInfo]
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str


    class azure.mgmt.edgeorder.types.ErrorResponse(TypedDict, total=False):
        key "error": ForwardRef('ErrorDetail', module='types')
        error: ErrorDetail


    class azure.mgmt.edgeorder.types.FilterableProperty(TypedDict, total=False):
        key "supportedValues": Required[list[str]]
        key "type": Required[Union[str, SupportedFilterTypes]]
        supported_values: list[str]
        type: Union[str, SupportedFilterTypes]


    class azure.mgmt.edgeorder.types.ForwardShippingDetails(TypedDict, total=False):
        key "carrierDisplayName": str
        key "carrierName": str
        key "trackingId": str
        key "trackingUrl": str
        carrier_display_name: str
        carrier_name: str
        tracking_id: str
        tracking_url: str


    class azure.mgmt.edgeorder.types.GroupedChildConfigurations(TypedDict, total=False):
        key "categoryInformation": ForwardRef('CategoryInformation', module='types')
        category_information: CategoryInformation
        childConfigurations: list[ChildConfiguration]
        child_configurations: list[ChildConfiguration]


    class azure.mgmt.edgeorder.types.HierarchyInformation(TypedDict, total=False):
        key "configurationIdDisplayName": str
        key "configurationName": str
        key "productFamilyName": str
        key "productLineName": str
        key "productName": str
        configuration_id_display_name: str
        configuration_name: str
        product_family_name: str
        product_line_name: str
        product_name: str


    class azure.mgmt.edgeorder.types.ImageInformation(TypedDict, total=False):
        key "imageType": Union[str, ImageType]
        key "imageUrl": str
        image_type: Union[str, ImageType]
        image_url: str


    class azure.mgmt.edgeorder.types.Link(TypedDict, total=False):
        key "linkType": Union[str, LinkType]
        key "linkUrl": str
        link_type: Union[str, LinkType]
        link_url: str


    class azure.mgmt.edgeorder.types.ManagementResourcePreferences(TypedDict, total=False):
        key "preferredManagementResourceId": str
        preferred_management_resource_id: str


    class azure.mgmt.edgeorder.types.NotificationPreference(TypedDict, total=False):
        key "sendNotification": Required[bool]
        key "stageName": Required[Union[str, NotificationStageName]]
        send_notification: bool
        stage_name: Union[str, NotificationStageName]


    class azure.mgmt.edgeorder.types.Operation(TypedDict, total=False):
        key "actionType": Union[str, ActionType]
        key "display": ForwardRef('OperationDisplay', module='types')
        key "isDataAction": bool
        key "name": str
        key "origin": Union[str, Origin]
        action_type: Union[str, ActionType]
        display: OperationDisplay
        is_data_action: bool
        name: str
        origin: Union[str, Origin]


    class azure.mgmt.edgeorder.types.OperationDisplay(TypedDict, total=False):
        key "description": str
        key "operation": str
        key "provider": str
        key "resource": str
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.edgeorder.types.OrderItemDetails(TypedDict, total=False):
        key "cancellationReason": str
        key "cancellationStatus": Union[str, OrderItemCancellationEnum]
        key "currentStage": ForwardRef('StageDetails', module='types')
        key "deletionStatus": Union[str, ActionStatusEnum]
        key "error": ForwardRef('ErrorDetail', module='types')
        key "forwardShippingDetails": ForwardRef('ForwardShippingDetails', module='types')
        key "orderItemMode": Union[str, OrderMode]
        key "orderItemType": Required[Union[str, OrderItemType]]
        key "preferences": ForwardRef('Preferences', module='types')
        key "productDetails": Required[ProductDetails]
        key "returnReason": str
        key "returnStatus": Union[str, OrderItemReturnEnum]
        key "reverseShippingDetails": ForwardRef('ReverseShippingDetails', module='types')
        key "siteDetails": ForwardRef('SiteDetails', module='types')
        cancellation_reason: str
        cancellation_status: Union[str, OrderItemCancellationEnum]
        current_stage: StageDetails
        deletion_status: Union[str, ActionStatusEnum]
        error: ErrorDetail
        forward_shipping_details: ForwardShippingDetails
        managementRpDetailsList: list[ResourceProviderDetails]
        management_rp_details_list: list[ResourceProviderDetails]
        notificationEmailList: list[str]
        notification_email_list: list[str]
        orderItemStageHistory: list[StageDetails]
        order_item_mode: Union[str, OrderMode]
        order_item_stage_history: list[StageDetails]
        order_item_type: Union[str, OrderItemType]
        preferences: Preferences
        product_details: ProductDetails
        return_reason: str
        return_status: Union[str, OrderItemReturnEnum]
        reverse_shipping_details: ReverseShippingDetails
        site_details: SiteDetails


    class azure.mgmt.edgeorder.types.OrderItemDetailsUpdateParameter(TypedDict, total=False):
        key "productDetails": ForwardRef('ProductDetailsUpdateParameter', module='types')
        key "siteDetails": ForwardRef('SiteDetails', module='types')
        product_details: ProductDetailsUpdateParameter
        site_details: SiteDetails


    class azure.mgmt.edgeorder.types.OrderItemProperties(TypedDict, total=False):
        key "addressDetails": ForwardRef('AddressDetails', module='types')
        key "orderId": Required[str]
        key "orderItemDetails": Required[OrderItemDetails]
        key "provisioningState": Union[str, ProvisioningState]
        key "startTime": str
        address_details: AddressDetails
        order_id: str
        order_item_details: OrderItemDetails
        provisioning_state: Union[str, ProvisioningState]
        start_time: str


    class azure.mgmt.edgeorder.types.OrderItemResource(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ResourceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": Required[OrderItemProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ResourceIdentity
        location: str
        name: str
        properties: OrderItemProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.edgeorder.types.OrderItemUpdateParameter(TypedDict, total=False):
        key "identity": ForwardRef('ResourceIdentity', module='types')
        key "properties": ForwardRef('OrderItemUpdateProperties', module='types')
        identity: ResourceIdentity
        properties: OrderItemUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.edgeorder.types.OrderItemUpdateProperties(TypedDict, total=False):
        key "forwardAddress": ForwardRef('AddressProperties', module='types')
        key "orderItemDetails": ForwardRef('OrderItemDetailsUpdateParameter', module='types')
        key "preferences": ForwardRef('Preferences', module='types')
        forward_address: AddressProperties
        notificationEmailList: list[str]
        notification_email_list: list[str]
        order_item_details: OrderItemDetailsUpdateParameter
        preferences: Preferences


    class azure.mgmt.edgeorder.types.OrderProperties(TypedDict, total=False):
        key "currentStage": ForwardRef('StageDetails', module='types')
        key "orderMode": Union[str, OrderMode]
        current_stage: StageDetails
        orderItemIds: list[str]
        orderStageHistory: list[StageDetails]
        order_item_ids: list[str]
        order_mode: Union[str, OrderMode]
        order_stage_history: list[StageDetails]


    class azure.mgmt.edgeorder.types.OrderResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[OrderProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: OrderProperties
        system_data: SystemData
        type: str


    class azure.mgmt.edgeorder.types.Pav2MeterDetails(TypedDict, total=False):
        key "billingType": Required[Literal[BillingType.PAV2]]
        key "chargingType": Union[str, ChargingType]
        key "meterGuid": str
        key "multiplier": float
        billing_type: Literal[BillingType.PAV2]
        charging_type: Union[str, ChargingType]
        meter_guid: str
        multiplier: float


    class azure.mgmt.edgeorder.types.Preferences(TypedDict, total=False):
        key "encryptionPreferences": ForwardRef('EncryptionPreferences', module='types')
        key "managementResourcePreferences": ForwardRef('ManagementResourcePreferences', module='types')
        key "termCommitmentPreferences": ForwardRef('TermCommitmentPreferences', module='types')
        key "transportPreferences": ForwardRef('TransportPreferences', module='types')
        encryption_preferences: EncryptionPreferences
        management_resource_preferences: ManagementResourcePreferences
        notificationPreferences: list[NotificationPreference]
        notification_preferences: list[NotificationPreference]
        term_commitment_preferences: TermCommitmentPreferences
        transport_preferences: TransportPreferences


    class azure.mgmt.edgeorder.types.Product(TypedDict, total=False):
        key "properties": ForwardRef('ProductProperties', module='types')
        properties: ProductProperties


    class azure.mgmt.edgeorder.types.ProductDetails(TypedDict, total=False):
        key "displayInfo": ForwardRef('DisplayInfo', module='types')
        key "hierarchyInformation": Required[HierarchyInformation]
        key "identificationType": Union[str, IdentificationType]
        key "parentDeviceDetails": ForwardRef('DeviceDetails', module='types')
        key "parentProvisioningDetails": ForwardRef('ProvisioningDetails', module='types')
        key "productDoubleEncryptionStatus": Union[str, DoubleEncryptionStatus]
        key "termCommitmentInformation": ForwardRef('TermCommitmentInformation', module='types')
        childConfigurationDeviceDetails: list[ConfigurationDeviceDetails]
        child_configuration_device_details: list[ConfigurationDeviceDetails]
        display_info: DisplayInfo
        hierarchy_information: HierarchyInformation
        identification_type: Union[str, IdentificationType]
        optInAdditionalConfigurations: list[AdditionalConfiguration]
        opt_in_additional_configurations: list[AdditionalConfiguration]
        parent_device_details: DeviceDetails
        parent_provisioning_details: ProvisioningDetails
        product_double_encryption_status: Union[str, DoubleEncryptionStatus]
        term_commitment_information: TermCommitmentInformation


    class azure.mgmt.edgeorder.types.ProductDetailsUpdateParameter(TypedDict, total=False):
        key "parentProvisioningDetails": ForwardRef('ProvisioningDetails', module='types')
        parent_provisioning_details: ProvisioningDetails


    class azure.mgmt.edgeorder.types.ProductFamiliesMetadataDetails(TypedDict, total=False):
        key "properties": ForwardRef('ProductFamilyProperties', module='types')
        properties: ProductFamilyProperties


    class azure.mgmt.edgeorder.types.ProductFamiliesRequest(TypedDict, total=False):
        key "customerSubscriptionDetails": ForwardRef('CustomerSubscriptionDetails', module='types')
        key "filterableProperties": Required[dict[str, list[FilterableProperty]]]
        customer_subscription_details: CustomerSubscriptionDetails
        filterable_properties: dict[str, list[FilterableProperty]]


    class azure.mgmt.edgeorder.types.ProductFamily(TypedDict, total=False):
        key "properties": ForwardRef('ProductFamilyProperties', module='types')
        properties: ProductFamilyProperties


    class azure.mgmt.edgeorder.types.ProductFamilyProperties(CommonProperties):
        key "availabilityInformation": ForwardRef('AvailabilityInformation', module='types')
        key "costInformation": ForwardRef('CostInformation', module='types')
        key "description": ForwardRef('Description', module='types')
        key "displayName": str
        key "fulfilledBy": Union[str, FulfillmentType]
        key "hierarchyInformation": ForwardRef('HierarchyInformation', module='types')
        availability_information: AvailabilityInformation
        cost_information: CostInformation
        description: Description
        display_name: str
        filterableProperties: list[FilterableProperty]
        filterable_properties: list[FilterableProperty]
        fulfilled_by: Union[str, FulfillmentType]
        hierarchy_information: HierarchyInformation
        imageInformation: list[ImageInformation]
        image_information: list[ImageInformation]
        productLines: list[ProductLine]
        product_lines: list[ProductLine]
        resourceProviderDetails: list[ResourceProviderDetails]
        resource_provider_details: list[ResourceProviderDetails]


    class azure.mgmt.edgeorder.types.ProductLine(TypedDict, total=False):
        key "properties": ForwardRef('ProductLineProperties', module='types')
        properties: ProductLineProperties


    class azure.mgmt.edgeorder.types.ProductLineProperties(CommonProperties):
        key "availabilityInformation": ForwardRef('AvailabilityInformation', module='types')
        key "costInformation": ForwardRef('CostInformation', module='types')
        key "description": ForwardRef('Description', module='types')
        key "displayName": str
        key "fulfilledBy": Union[str, FulfillmentType]
        key "hierarchyInformation": ForwardRef('HierarchyInformation', module='types')
        availability_information: AvailabilityInformation
        cost_information: CostInformation
        description: Description
        display_name: str
        filterableProperties: list[FilterableProperty]
        filterable_properties: list[FilterableProperty]
        fulfilled_by: Union[str, FulfillmentType]
        hierarchy_information: HierarchyInformation
        imageInformation: list[ImageInformation]
        image_information: list[ImageInformation]
        products: list[Product]


    class azure.mgmt.edgeorder.types.ProductProperties(CommonProperties):
        key "availabilityInformation": ForwardRef('AvailabilityInformation', module='types')
        key "costInformation": ForwardRef('CostInformation', module='types')
        key "description": ForwardRef('Description', module='types')
        key "displayName": str
        key "fulfilledBy": Union[str, FulfillmentType]
        key "hierarchyInformation": ForwardRef('HierarchyInformation', module='types')
        availability_information: AvailabilityInformation
        configurations: list[Configuration]
        cost_information: CostInformation
        description: Description
        display_name: str
        filterableProperties: list[FilterableProperty]
        filterable_properties: list[FilterableProperty]
        fulfilled_by: Union[str, FulfillmentType]
        hierarchy_information: HierarchyInformation
        imageInformation: list[ImageInformation]
        image_information: list[ImageInformation]


    class azure.mgmt.edgeorder.types.ProvisioningDetails(TypedDict, total=False):
        key "autoProvisioningStatus": Union[str, AutoProvisioningStatus]
        key "devicePresenceVerification": ForwardRef('DevicePresenceVerificationDetails', module='types')
        key "managementResourceArmId": str
        key "provisioningArmId": str
        key "provisioningEndPoint": str
        key "quantity": int
        key "readyToConnectArmId": str
        key "serialNumber": str
        key "uniqueDeviceIdentifier": str
        key "vendorName": str
        auto_provisioning_status: Union[str, AutoProvisioningStatus]
        device_presence_verification: DevicePresenceVerificationDetails
        management_resource_arm_id: str
        provisioning_arm_id: str
        provisioning_end_point: str
        quantity: int
        ready_to_connect_arm_id: str
        serial_number: str
        unique_device_identifier: str
        vendor_name: str


    class azure.mgmt.edgeorder.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.edgeorder.types.PurchaseMeterDetails(TypedDict, total=False):
        key "billingType": Required[Literal[BillingType.PURCHASE]]
        key "chargingType": Union[str, ChargingType]
        key "multiplier": float
        key "productId": str
        key "skuId": str
        key "termId": str
        billing_type: Literal[BillingType.PURCHASE]
        charging_type: Union[str, ChargingType]
        multiplier: float
        product_id: str
        sku_id: str
        term_id: str


    class azure.mgmt.edgeorder.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.edgeorder.types.ResourceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": str
        principal_id: str
        tenant_id: str
        type: str
        userAssignedIdentities: dict[str, UserAssignedIdentity]
        user_assigned_identities: dict[str, UserAssignedIdentity]


    class azure.mgmt.edgeorder.types.ResourceProviderDetails(TypedDict, total=False):
        key "resourceProviderNamespace": str
        resource_provider_namespace: str


    class azure.mgmt.edgeorder.types.ReturnOrderItemDetails(TypedDict, total=False):
        key "returnAddress": ForwardRef('AddressProperties', module='types')
        key "returnReason": Required[str]
        key "serviceTag": str
        key "shippingBoxRequired": bool
        return_address: AddressProperties
        return_reason: str
        service_tag: str
        shipping_box_required: bool


    class azure.mgmt.edgeorder.types.ReverseShippingDetails(TypedDict, total=False):
        key "carrierDisplayName": str
        key "carrierName": str
        key "sasKeyForLabel": str
        key "trackingId": str
        key "trackingUrl": str
        carrier_display_name: str
        carrier_name: str
        sas_key_for_label: str
        tracking_id: str
        tracking_url: str


    class azure.mgmt.edgeorder.types.ShippingAddress(TypedDict, total=False):
        key "addressType": Union[str, AddressType]
        key "city": str
        key "companyName": str
        key "country": Required[str]
        key "postalCode": str
        key "stateOrProvince": str
        key "streetAddress1": str
        key "streetAddress2": str
        key "streetAddress3": str
        key "zipExtendedCode": str
        address_type: Union[str, AddressType]
        city: str
        company_name: str
        country: str
        postal_code: str
        state_or_province: str
        street_address1: str
        street_address2: str
        street_address3: str
        zip_extended_code: str


    class azure.mgmt.edgeorder.types.SiteDetails(TypedDict, total=False):
        key "siteId": Required[str]
        site_id: str


    class azure.mgmt.edgeorder.types.Specification(TypedDict, total=False):
        key "name": str
        key "value": str
        name: str
        value: str


    class azure.mgmt.edgeorder.types.StageDetails(TypedDict, total=False):
        key "displayName": str
        key "stageName": Union[str, StageName]
        key "stageStatus": Union[str, StageStatus]
        key "startTime": str
        display_name: str
        stage_name: Union[str, StageName]
        stage_status: Union[str, StageStatus]
        start_time: str


    class azure.mgmt.edgeorder.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.edgeorder.types.TermCommitmentInformation(TypedDict, total=False):
        key "pendingDaysForTerm": int
        key "termCommitmentType": Required[Union[str, TermCommitmentType]]
        key "termCommitmentTypeDuration": str
        pending_days_for_term: int
        term_commitment_type: Union[str, TermCommitmentType]
        term_commitment_type_duration: str


    class azure.mgmt.edgeorder.types.TermCommitmentPreferences(TypedDict, total=False):
        key "preferredTermCommitmentDuration": str
        key "preferredTermCommitmentType": Required[Union[str, TermCommitmentType]]
        preferred_term_commitment_duration: str
        preferred_term_commitment_type: Union[str, TermCommitmentType]


    class azure.mgmt.edgeorder.types.TermTypeDetails(TypedDict, total=False):
        key "termType": Required[Union[str, TermCommitmentType]]
        key "termTypeDuration": Required[str]
        term_type: Union[str, TermCommitmentType]
        term_type_duration: str


    class azure.mgmt.edgeorder.types.TrackedResource(Resource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.edgeorder.types.TransportPreferences(TypedDict, total=False):
        key "preferredShipmentType": Required[Union[str, TransportShipmentTypes]]
        preferred_shipment_type: Union[str, TransportShipmentTypes]


    class azure.mgmt.edgeorder.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        client_id: str
        principal_id: str


```