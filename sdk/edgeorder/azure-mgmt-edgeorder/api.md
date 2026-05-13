```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.edgeorder

    class azure.mgmt.edgeorder.EdgeOrderManagementClient(EdgeOrderManagementClientOperationsMixin): implements ContextManager 

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

        @overload
        def begin_create_address(
                self, 
                address_name: str, 
                resource_group_name: str, 
                address_resource: AddressResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AddressResource]: ...

        @overload
        def begin_create_address(
                self, 
                address_name: str, 
                resource_group_name: str, 
                address_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AddressResource]: ...

        @overload
        def begin_create_order_item(
                self, 
                order_item_name: str, 
                resource_group_name: str, 
                order_item_resource: OrderItemResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OrderItemResource]: ...

        @overload
        def begin_create_order_item(
                self, 
                order_item_name: str, 
                resource_group_name: str, 
                order_item_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OrderItemResource]: ...

        @distributed_trace
        def begin_delete_address_by_name(
                self, 
                address_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_order_item_by_name(
                self, 
                order_item_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_return_order_item(
                self, 
                order_item_name: str, 
                resource_group_name: str, 
                return_order_item_details: ReturnOrderItemDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_return_order_item(
                self, 
                order_item_name: str, 
                resource_group_name: str, 
                return_order_item_details: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update_address(
                self, 
                address_name: str, 
                resource_group_name: str, 
                address_update_parameter: AddressUpdateParameter, 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AddressResource]: ...

        @overload
        def begin_update_address(
                self, 
                address_name: str, 
                resource_group_name: str, 
                address_update_parameter: IO[bytes], 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AddressResource]: ...

        @overload
        def begin_update_order_item(
                self, 
                order_item_name: str, 
                resource_group_name: str, 
                order_item_update_parameter: OrderItemUpdateParameter, 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OrderItemResource]: ...

        @overload
        def begin_update_order_item(
                self, 
                order_item_name: str, 
                resource_group_name: str, 
                order_item_update_parameter: IO[bytes], 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OrderItemResource]: ...

        @overload
        def cancel_order_item(
                self, 
                order_item_name: str, 
                resource_group_name: str, 
                cancellation_reason: CancellationReason, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def cancel_order_item(
                self, 
                order_item_name: str, 
                resource_group_name: str, 
                cancellation_reason: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @distributed_trace
        def get_address_by_name(
                self, 
                address_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AddressResource: ...

        @distributed_trace
        def get_order_by_name(
                self, 
                order_name: str, 
                resource_group_name: str, 
                location: str, 
                **kwargs: Any
            ) -> OrderResource: ...

        @distributed_trace
        def get_order_item_by_name(
                self, 
                order_item_name: str, 
                resource_group_name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> OrderItemResource: ...

        @distributed_trace
        def list_addresses_at_resource_group_level(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                skip_token: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[AddressResource]: ...

        @distributed_trace
        def list_addresses_at_subscription_level(
                self, 
                filter: Optional[str] = None, 
                skip_token: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[AddressResource]: ...

        @overload
        def list_configurations(
                self, 
                configurations_request: ConfigurationsRequest, 
                skip_token: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Iterable[Configuration]: ...

        @overload
        def list_configurations(
                self, 
                configurations_request: IO[bytes], 
                skip_token: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Iterable[Configuration]: ...

        @distributed_trace
        def list_operations(self, **kwargs: Any) -> Iterable[Operation]: ...

        @distributed_trace
        def list_order_at_resource_group_level(
                self, 
                resource_group_name: str, 
                skip_token: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[OrderResource]: ...

        @distributed_trace
        def list_order_at_subscription_level(
                self, 
                skip_token: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[OrderResource]: ...

        @distributed_trace
        def list_order_items_at_resource_group_level(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
                skip_token: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[OrderItemResource]: ...

        @distributed_trace
        def list_order_items_at_subscription_level(
                self, 
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
                skip_token: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[OrderItemResource]: ...

        @overload
        def list_product_families(
                self, 
                product_families_request: ProductFamiliesRequest, 
                expand: Optional[str] = None, 
                skip_token: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Iterable[ProductFamily]: ...

        @overload
        def list_product_families(
                self, 
                product_families_request: IO[bytes], 
                expand: Optional[str] = None, 
                skip_token: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Iterable[ProductFamily]: ...

        @distributed_trace
        def list_product_families_metadata(
                self, 
                skip_token: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[ProductFamiliesMetadataDetails]: ...


namespace azure.mgmt.edgeorder.aio

    class azure.mgmt.edgeorder.aio.EdgeOrderManagementClient(EdgeOrderManagementClientOperationsMixin): implements AsyncContextManager 

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

        @overload
        async def begin_create_address(
                self, 
                address_name: str, 
                resource_group_name: str, 
                address_resource: AddressResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AddressResource]: ...

        @overload
        async def begin_create_address(
                self, 
                address_name: str, 
                resource_group_name: str, 
                address_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AddressResource]: ...

        @overload
        async def begin_create_order_item(
                self, 
                order_item_name: str, 
                resource_group_name: str, 
                order_item_resource: OrderItemResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OrderItemResource]: ...

        @overload
        async def begin_create_order_item(
                self, 
                order_item_name: str, 
                resource_group_name: str, 
                order_item_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OrderItemResource]: ...

        @distributed_trace_async
        async def begin_delete_address_by_name(
                self, 
                address_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_order_item_by_name(
                self, 
                order_item_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_return_order_item(
                self, 
                order_item_name: str, 
                resource_group_name: str, 
                return_order_item_details: ReturnOrderItemDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_return_order_item(
                self, 
                order_item_name: str, 
                resource_group_name: str, 
                return_order_item_details: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update_address(
                self, 
                address_name: str, 
                resource_group_name: str, 
                address_update_parameter: AddressUpdateParameter, 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AddressResource]: ...

        @overload
        async def begin_update_address(
                self, 
                address_name: str, 
                resource_group_name: str, 
                address_update_parameter: IO[bytes], 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AddressResource]: ...

        @overload
        async def begin_update_order_item(
                self, 
                order_item_name: str, 
                resource_group_name: str, 
                order_item_update_parameter: OrderItemUpdateParameter, 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OrderItemResource]: ...

        @overload
        async def begin_update_order_item(
                self, 
                order_item_name: str, 
                resource_group_name: str, 
                order_item_update_parameter: IO[bytes], 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OrderItemResource]: ...

        @overload
        async def cancel_order_item(
                self, 
                order_item_name: str, 
                resource_group_name: str, 
                cancellation_reason: CancellationReason, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def cancel_order_item(
                self, 
                order_item_name: str, 
                resource_group_name: str, 
                cancellation_reason: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def get_address_by_name(
                self, 
                address_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AddressResource: ...

        @distributed_trace_async
        async def get_order_by_name(
                self, 
                order_name: str, 
                resource_group_name: str, 
                location: str, 
                **kwargs: Any
            ) -> OrderResource: ...

        @distributed_trace_async
        async def get_order_item_by_name(
                self, 
                order_item_name: str, 
                resource_group_name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> OrderItemResource: ...

        @distributed_trace
        def list_addresses_at_resource_group_level(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                skip_token: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[AddressResource]: ...

        @distributed_trace
        def list_addresses_at_subscription_level(
                self, 
                filter: Optional[str] = None, 
                skip_token: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[AddressResource]: ...

        @overload
        def list_configurations(
                self, 
                configurations_request: ConfigurationsRequest, 
                skip_token: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncIterable[Configuration]: ...

        @overload
        def list_configurations(
                self, 
                configurations_request: IO[bytes], 
                skip_token: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncIterable[Configuration]: ...

        @distributed_trace
        def list_operations(self, **kwargs: Any) -> AsyncIterable[Operation]: ...

        @distributed_trace
        def list_order_at_resource_group_level(
                self, 
                resource_group_name: str, 
                skip_token: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[OrderResource]: ...

        @distributed_trace
        def list_order_at_subscription_level(
                self, 
                skip_token: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[OrderResource]: ...

        @distributed_trace
        def list_order_items_at_resource_group_level(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
                skip_token: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[OrderItemResource]: ...

        @distributed_trace
        def list_order_items_at_subscription_level(
                self, 
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
                skip_token: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[OrderItemResource]: ...

        @overload
        def list_product_families(
                self, 
                product_families_request: ProductFamiliesRequest, 
                expand: Optional[str] = None, 
                skip_token: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncIterable[ProductFamily]: ...

        @overload
        def list_product_families(
                self, 
                product_families_request: IO[bytes], 
                expand: Optional[str] = None, 
                skip_token: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncIterable[ProductFamily]: ...

        @distributed_trace
        def list_product_families_metadata(
                self, 
                skip_token: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[ProductFamiliesMetadataDetails]: ...


namespace azure.mgmt.edgeorder.aio.operations

    class azure.mgmt.edgeorder.aio.operations.EdgeOrderManagementClientOperationsMixin(EdgeOrderManagementClientMixinABC):

        @overload
        async def begin_create_address(
                self, 
                address_name: str, 
                resource_group_name: str, 
                address_resource: AddressResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AddressResource]: ...

        @overload
        async def begin_create_address(
                self, 
                address_name: str, 
                resource_group_name: str, 
                address_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AddressResource]: ...

        @overload
        async def begin_create_order_item(
                self, 
                order_item_name: str, 
                resource_group_name: str, 
                order_item_resource: OrderItemResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OrderItemResource]: ...

        @overload
        async def begin_create_order_item(
                self, 
                order_item_name: str, 
                resource_group_name: str, 
                order_item_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OrderItemResource]: ...

        @distributed_trace_async
        async def begin_delete_address_by_name(
                self, 
                address_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_order_item_by_name(
                self, 
                order_item_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_return_order_item(
                self, 
                order_item_name: str, 
                resource_group_name: str, 
                return_order_item_details: ReturnOrderItemDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_return_order_item(
                self, 
                order_item_name: str, 
                resource_group_name: str, 
                return_order_item_details: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update_address(
                self, 
                address_name: str, 
                resource_group_name: str, 
                address_update_parameter: AddressUpdateParameter, 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AddressResource]: ...

        @overload
        async def begin_update_address(
                self, 
                address_name: str, 
                resource_group_name: str, 
                address_update_parameter: IO[bytes], 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AddressResource]: ...

        @overload
        async def begin_update_order_item(
                self, 
                order_item_name: str, 
                resource_group_name: str, 
                order_item_update_parameter: OrderItemUpdateParameter, 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OrderItemResource]: ...

        @overload
        async def begin_update_order_item(
                self, 
                order_item_name: str, 
                resource_group_name: str, 
                order_item_update_parameter: IO[bytes], 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OrderItemResource]: ...

        @overload
        async def cancel_order_item(
                self, 
                order_item_name: str, 
                resource_group_name: str, 
                cancellation_reason: CancellationReason, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def cancel_order_item(
                self, 
                order_item_name: str, 
                resource_group_name: str, 
                cancellation_reason: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_address_by_name(
                self, 
                address_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AddressResource: ...

        @distributed_trace_async
        async def get_order_by_name(
                self, 
                order_name: str, 
                resource_group_name: str, 
                location: str, 
                **kwargs: Any
            ) -> OrderResource: ...

        @distributed_trace_async
        async def get_order_item_by_name(
                self, 
                order_item_name: str, 
                resource_group_name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> OrderItemResource: ...

        @distributed_trace
        def list_addresses_at_resource_group_level(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                skip_token: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[AddressResource]: ...

        @distributed_trace
        def list_addresses_at_subscription_level(
                self, 
                filter: Optional[str] = None, 
                skip_token: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[AddressResource]: ...

        @overload
        def list_configurations(
                self, 
                configurations_request: ConfigurationsRequest, 
                skip_token: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncIterable[Configuration]: ...

        @overload
        def list_configurations(
                self, 
                configurations_request: IO[bytes], 
                skip_token: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncIterable[Configuration]: ...

        @distributed_trace
        def list_operations(self, **kwargs: Any) -> AsyncIterable[Operation]: ...

        @distributed_trace
        def list_order_at_resource_group_level(
                self, 
                resource_group_name: str, 
                skip_token: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[OrderResource]: ...

        @distributed_trace
        def list_order_at_subscription_level(
                self, 
                skip_token: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[OrderResource]: ...

        @distributed_trace
        def list_order_items_at_resource_group_level(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
                skip_token: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[OrderItemResource]: ...

        @distributed_trace
        def list_order_items_at_subscription_level(
                self, 
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
                skip_token: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[OrderItemResource]: ...

        @overload
        def list_product_families(
                self, 
                product_families_request: ProductFamiliesRequest, 
                expand: Optional[str] = None, 
                skip_token: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncIterable[ProductFamily]: ...

        @overload
        def list_product_families(
                self, 
                product_families_request: IO[bytes], 
                expand: Optional[str] = None, 
                skip_token: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncIterable[ProductFamily]: ...

        @distributed_trace
        def list_product_families_metadata(
                self, 
                skip_token: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[ProductFamiliesMetadataDetails]: ...


namespace azure.mgmt.edgeorder.models

    class azure.mgmt.edgeorder.models.ActionStatusEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOWED = "Allowed"
        NOT_ALLOWED = "NotAllowed"


    class azure.mgmt.edgeorder.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.edgeorder.models.AddressDetails(Model):
        forward_address: AddressProperties
        return_address: AddressProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                forward_address: AddressProperties, 
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


    class azure.mgmt.edgeorder.models.AddressProperties(Model):
        address_validation_status: Union[str, AddressValidationStatus]
        contact_details: ContactDetails
        shipping_address: ShippingAddress

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                contact_details: ContactDetails, 
                shipping_address: Optional[ShippingAddress] = ..., 
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


    class azure.mgmt.edgeorder.models.AddressResource(TrackedResource):
        address_validation_status: Union[str, AddressValidationStatus]
        contact_details: ContactDetails
        id: str
        location: str
        name: str
        shipping_address: ShippingAddress
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                contact_details: ContactDetails, 
                location: str, 
                shipping_address: Optional[ShippingAddress] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.edgeorder.models.AddressResourceList(Model):
        next_link: str
        value: list[AddressResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
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


    class azure.mgmt.edgeorder.models.AddressType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMMERCIAL = "Commercial"
        NONE = "None"
        RESIDENTIAL = "Residential"


    class azure.mgmt.edgeorder.models.AddressUpdateParameter(Model):
        contact_details: ContactDetails
        shipping_address: ShippingAddress
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                contact_details: Optional[ContactDetails] = ..., 
                shipping_address: Optional[ShippingAddress] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.edgeorder.models.AddressValidationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AMBIGUOUS = "Ambiguous"
        INVALID = "Invalid"
        VALID = "Valid"


    class azure.mgmt.edgeorder.models.AvailabilityInformation(Model):
        availability_stage: Union[str, AvailabilityStage]
        disabled_reason: Union[str, DisabledReason]
        disabled_reason_message: str

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


    class azure.mgmt.edgeorder.models.AvailabilityStage(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        COMING_SOON = "ComingSoon"
        DEPRECATED = "Deprecated"
        PREVIEW = "Preview"
        SIGNUP = "Signup"
        UNAVAILABLE = "Unavailable"


    class azure.mgmt.edgeorder.models.BasicInformation(Model):
        availability_information: AvailabilityInformation
        cost_information: CostInformation
        description: Description
        display_name: str
        hierarchy_information: HierarchyInformation
        image_information: list[ImageInformation]

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


    class azure.mgmt.edgeorder.models.BillingMeterDetails(Model):
        frequency: str
        meter_details: MeterDetails
        metering_type: Union[str, MeteringType]
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


    class azure.mgmt.edgeorder.models.BillingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PAV2 = "Pav2"
        PURCHASE = "Purchase"


    class azure.mgmt.edgeorder.models.CancellationReason(Model):
        reason: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                reason: str, 
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


    class azure.mgmt.edgeorder.models.ChargingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PER_DEVICE = "PerDevice"
        PER_ORDER = "PerOrder"


    class azure.mgmt.edgeorder.models.CommonProperties(BasicInformation):
        availability_information: AvailabilityInformation
        cost_information: CostInformation
        description: Description
        display_name: str
        filterable_properties: list[FilterableProperty]
        hierarchy_information: HierarchyInformation
        image_information: list[ImageInformation]

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


    class azure.mgmt.edgeorder.models.Configuration(Model):
        availability_information: AvailabilityInformation
        cost_information: CostInformation
        description: Description
        dimensions: Dimensions
        display_name: str
        filterable_properties: list[FilterableProperty]
        hierarchy_information: HierarchyInformation
        image_information: list[ImageInformation]
        specifications: list[Specification]

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


    class azure.mgmt.edgeorder.models.ConfigurationFilters(Model):
        filterable_property: list[FilterableProperty]
        hierarchy_information: HierarchyInformation

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                filterable_property: Optional[List[FilterableProperty]] = ..., 
                hierarchy_information: HierarchyInformation, 
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


    class azure.mgmt.edgeorder.models.ConfigurationProperties(CommonProperties):
        availability_information: AvailabilityInformation
        cost_information: CostInformation
        description: Description
        dimensions: Dimensions
        display_name: str
        filterable_properties: list[FilterableProperty]
        hierarchy_information: HierarchyInformation
        image_information: list[ImageInformation]
        specifications: list[Specification]

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


    class azure.mgmt.edgeorder.models.Configurations(Model):
        next_link: str
        value: list[Configuration]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
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


    class azure.mgmt.edgeorder.models.ConfigurationsRequest(Model):
        configuration_filters: list[ConfigurationFilters]
        customer_subscription_details: CustomerSubscriptionDetails

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                configuration_filters: List[ConfigurationFilters], 
                customer_subscription_details: Optional[CustomerSubscriptionDetails] = ..., 
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


    class azure.mgmt.edgeorder.models.ContactDetails(Model):
        contact_name: str
        email_list: list[str]
        mobile: str
        phone: str
        phone_extension: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                contact_name: str, 
                email_list: List[str], 
                mobile: Optional[str] = ..., 
                phone: str, 
                phone_extension: Optional[str] = ..., 
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


    class azure.mgmt.edgeorder.models.CostInformation(Model):
        billing_info_url: str
        billing_meter_details: list[BillingMeterDetails]

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


    class azure.mgmt.edgeorder.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.edgeorder.models.CustomerSubscriptionDetails(Model):
        location_placement_id: str
        quota_id: str
        registered_features: list[CustomerSubscriptionRegisteredFeatures]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location_placement_id: Optional[str] = ..., 
                quota_id: str, 
                registered_features: Optional[List[CustomerSubscriptionRegisteredFeatures]] = ..., 
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


    class azure.mgmt.edgeorder.models.CustomerSubscriptionRegisteredFeatures(Model):
        name: str
        state: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                state: Optional[str] = ..., 
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


    class azure.mgmt.edgeorder.models.Description(Model):
        attributes: list[str]
        description_type: Union[str, DescriptionType]
        keywords: list[str]
        links: list[Link]
        long_description: str
        short_description: str

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


    class azure.mgmt.edgeorder.models.DescriptionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASE = "Base"


    class azure.mgmt.edgeorder.models.DeviceDetails(Model):
        management_resource_id: str
        management_resource_tenant_id: str
        serial_number: str

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


    class azure.mgmt.edgeorder.models.Dimensions(Model):
        depth: float
        height: float
        length: float
        length_height_unit: Union[str, LengthHeightUnit]
        weight: float
        weight_unit: Union[str, WeightMeasurementUnit]
        width: float

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


    class azure.mgmt.edgeorder.models.DisabledReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COUNTRY = "Country"
        FEATURE = "Feature"
        NONE = "None"
        NOT_AVAILABLE = "NotAvailable"
        NO_SUBSCRIPTION_INFO = "NoSubscriptionInfo"
        OFFER_TYPE = "OfferType"
        OUT_OF_STOCK = "OutOfStock"
        REGION = "Region"


    class azure.mgmt.edgeorder.models.DisplayInfo(Model):
        configuration_display_name: str
        product_family_display_name: str

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


    class azure.mgmt.edgeorder.models.DoubleEncryptionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.edgeorder.models.EncryptionPreferences(Model):
        double_encryption_status: Union[str, DoubleEncryptionStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                double_encryption_status: Optional[Union[str, DoubleEncryptionStatus]] = ..., 
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


    class azure.mgmt.edgeorder.models.ErrorAdditionalInfo(Model):
        info: JSON
        type: str

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


    class azure.mgmt.edgeorder.models.ErrorDetail(Model):
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


    class azure.mgmt.edgeorder.models.ErrorResponse(Model):
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


    class azure.mgmt.edgeorder.models.FilterableProperty(Model):
        supported_values: list[str]
        type: Union[str, SupportedFilterTypes]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                supported_values: List[str], 
                type: Union[str, SupportedFilterTypes], 
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


    class azure.mgmt.edgeorder.models.ForwardShippingDetails(Model):
        carrier_display_name: str
        carrier_name: str
        tracking_id: str
        tracking_url: str

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


    class azure.mgmt.edgeorder.models.HierarchyInformation(Model):
        configuration_name: str
        product_family_name: str
        product_line_name: str
        product_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                configuration_name: Optional[str] = ..., 
                product_family_name: Optional[str] = ..., 
                product_line_name: Optional[str] = ..., 
                product_name: Optional[str] = ..., 
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


    class azure.mgmt.edgeorder.models.ImageInformation(Model):
        image_type: Union[str, ImageType]
        image_url: str

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


    class azure.mgmt.edgeorder.models.ImageType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BULLET_IMAGE = "BulletImage"
        GENERIC_IMAGE = "GenericImage"
        MAIN_IMAGE = "MainImage"


    class azure.mgmt.edgeorder.models.LengthHeightUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CM = "CM"
        IN = "IN"
        IN_ENUM = "IN"


    class azure.mgmt.edgeorder.models.Link(Model):
        link_type: Union[str, LinkType]
        link_url: str

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


    class azure.mgmt.edgeorder.models.LinkType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DOCUMENTATION = "Documentation"
        GENERIC = "Generic"
        KNOW_MORE = "KnowMore"
        SIGN_UP = "SignUp"
        SPECIFICATION = "Specification"
        TERMS_AND_CONDITIONS = "TermsAndConditions"


    class azure.mgmt.edgeorder.models.ManagementResourcePreferences(Model):
        preferred_management_resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                preferred_management_resource_id: Optional[str] = ..., 
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


    class azure.mgmt.edgeorder.models.MeterDetails(Model):
        billing_type: Union[str, BillingType]
        charging_type: Union[str, ChargingType]
        multiplier: float

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


    class azure.mgmt.edgeorder.models.MeteringType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADHOC = "Adhoc"
        ONE_TIME = "OneTime"
        RECURRING = "Recurring"


    class azure.mgmt.edgeorder.models.NotificationPreference(Model):
        send_notification: bool
        stage_name: Union[str, NotificationStageName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                send_notification: bool, 
                stage_name: Union[str, NotificationStageName], 
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


    class azure.mgmt.edgeorder.models.NotificationStageName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELIVERED = "Delivered"
        SHIPPED = "Shipped"


    class azure.mgmt.edgeorder.models.Operation(Model):
        action_type: Union[str, ActionType]
        display: OperationDisplay
        is_data_action: bool
        name: str
        origin: Union[str, Origin]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
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


    class azure.mgmt.edgeorder.models.OperationDisplay(Model):
        description: str
        operation: str
        provider: str
        resource: str

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


    class azure.mgmt.edgeorder.models.OperationListResult(Model):
        next_link: str
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


    class azure.mgmt.edgeorder.models.OrderItemCancellationEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLABLE = "Cancellable"
        CANCELLABLE_WITH_FEE = "CancellableWithFee"
        NOT_CANCELLABLE = "NotCancellable"


    class azure.mgmt.edgeorder.models.OrderItemDetails(Model):
        cancellation_reason: str
        cancellation_status: Union[str, OrderItemCancellationEnum]
        current_stage: StageDetails
        deletion_status: Union[str, ActionStatusEnum]
        error: ErrorDetail
        forward_shipping_details: ForwardShippingDetails
        management_rp_details: ResourceProviderDetails
        management_rp_details_list: list[ResourceProviderDetails]
        notification_email_list: list[str]
        order_item_stage_history: list[StageDetails]
        order_item_type: Union[str, OrderItemType]
        preferences: Preferences
        product_details: ProductDetails
        return_reason: str
        return_status: Union[str, OrderItemReturnEnum]
        reverse_shipping_details: ReverseShippingDetails

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                notification_email_list: Optional[List[str]] = ..., 
                order_item_type: Union[str, OrderItemType], 
                preferences: Optional[Preferences] = ..., 
                product_details: ProductDetails, 
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


    class azure.mgmt.edgeorder.models.OrderItemResource(TrackedResource):
        address_details: AddressDetails
        id: str
        location: str
        name: str
        order_id: str
        order_item_details: OrderItemDetails
        start_time: datetime
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                address_details: AddressDetails, 
                location: str, 
                order_id: str, 
                order_item_details: OrderItemDetails, 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.edgeorder.models.OrderItemResourceList(Model):
        next_link: str
        value: list[OrderItemResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
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


    class azure.mgmt.edgeorder.models.OrderItemReturnEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_RETURNABLE = "NotReturnable"
        RETURNABLE = "Returnable"
        RETURNABLE_WITH_FEE = "ReturnableWithFee"


    class azure.mgmt.edgeorder.models.OrderItemType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PURCHASE = "Purchase"
        RENTAL = "Rental"


    class azure.mgmt.edgeorder.models.OrderItemUpdateParameter(Model):
        forward_address: AddressProperties
        notification_email_list: list[str]
        preferences: Preferences
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                forward_address: Optional[AddressProperties] = ..., 
                notification_email_list: Optional[List[str]] = ..., 
                preferences: Optional[Preferences] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.edgeorder.models.OrderResource(ProxyResource):
        current_stage: StageDetails
        id: str
        name: str
        order_item_ids: list[str]
        order_stage_history: list[StageDetails]
        system_data: SystemData
        type: str

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


    class azure.mgmt.edgeorder.models.OrderResourceList(Model):
        next_link: str
        value: list[OrderResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
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


    class azure.mgmt.edgeorder.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.edgeorder.models.Pav2MeterDetails(MeterDetails):
        billing_type: Union[str, BillingType]
        charging_type: Union[str, ChargingType]
        meter_guid: str
        multiplier: float

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


    class azure.mgmt.edgeorder.models.Preferences(Model):
        encryption_preferences: EncryptionPreferences
        management_resource_preferences: ManagementResourcePreferences
        notification_preferences: list[NotificationPreference]
        transport_preferences: TransportPreferences

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                encryption_preferences: Optional[EncryptionPreferences] = ..., 
                management_resource_preferences: Optional[ManagementResourcePreferences] = ..., 
                notification_preferences: Optional[List[NotificationPreference]] = ..., 
                transport_preferences: Optional[TransportPreferences] = ..., 
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


    class azure.mgmt.edgeorder.models.Product(Model):
        availability_information: AvailabilityInformation
        configurations: list[Configuration]
        cost_information: CostInformation
        description: Description
        display_name: str
        filterable_properties: list[FilterableProperty]
        hierarchy_information: HierarchyInformation
        image_information: list[ImageInformation]

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


    class azure.mgmt.edgeorder.models.ProductDetails(Model):
        count: int
        device_details: list[DeviceDetails]
        display_info: DisplayInfo
        hierarchy_information: HierarchyInformation
        product_double_encryption_status: Union[str, DoubleEncryptionStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display_info: Optional[DisplayInfo] = ..., 
                hierarchy_information: HierarchyInformation, 
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


    class azure.mgmt.edgeorder.models.ProductFamilies(Model):
        next_link: str
        value: list[ProductFamily]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
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


    class azure.mgmt.edgeorder.models.ProductFamiliesMetadata(Model):
        next_link: str
        value: list[ProductFamiliesMetadataDetails]

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


    class azure.mgmt.edgeorder.models.ProductFamiliesMetadataDetails(Model):
        availability_information: AvailabilityInformation
        cost_information: CostInformation
        description: Description
        display_name: str
        filterable_properties: list[FilterableProperty]
        hierarchy_information: HierarchyInformation
        image_information: list[ImageInformation]
        product_lines: list[ProductLine]
        resource_provider_details: list[ResourceProviderDetails]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                resource_provider_details: Optional[List[ResourceProviderDetails]] = ..., 
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


    class azure.mgmt.edgeorder.models.ProductFamiliesRequest(Model):
        customer_subscription_details: CustomerSubscriptionDetails
        filterable_properties: dict[str, list[FilterableProperty]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                customer_subscription_details: Optional[CustomerSubscriptionDetails] = ..., 
                filterable_properties: Dict[str, List[FilterableProperty]], 
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


    class azure.mgmt.edgeorder.models.ProductFamily(Model):
        availability_information: AvailabilityInformation
        cost_information: CostInformation
        description: Description
        display_name: str
        filterable_properties: list[FilterableProperty]
        hierarchy_information: HierarchyInformation
        image_information: list[ImageInformation]
        product_lines: list[ProductLine]
        resource_provider_details: list[ResourceProviderDetails]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                resource_provider_details: Optional[List[ResourceProviderDetails]] = ..., 
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


    class azure.mgmt.edgeorder.models.ProductFamilyProperties(CommonProperties):
        availability_information: AvailabilityInformation
        cost_information: CostInformation
        description: Description
        display_name: str
        filterable_properties: list[FilterableProperty]
        hierarchy_information: HierarchyInformation
        image_information: list[ImageInformation]
        product_lines: list[ProductLine]
        resource_provider_details: list[ResourceProviderDetails]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                resource_provider_details: Optional[List[ResourceProviderDetails]] = ..., 
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


    class azure.mgmt.edgeorder.models.ProductLine(Model):
        availability_information: AvailabilityInformation
        cost_information: CostInformation
        description: Description
        display_name: str
        filterable_properties: list[FilterableProperty]
        hierarchy_information: HierarchyInformation
        image_information: list[ImageInformation]
        products: list[Product]

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


    class azure.mgmt.edgeorder.models.ProductLineProperties(CommonProperties):
        availability_information: AvailabilityInformation
        cost_information: CostInformation
        description: Description
        display_name: str
        filterable_properties: list[FilterableProperty]
        hierarchy_information: HierarchyInformation
        image_information: list[ImageInformation]
        products: list[Product]

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


    class azure.mgmt.edgeorder.models.ProductProperties(CommonProperties):
        availability_information: AvailabilityInformation
        configurations: list[Configuration]
        cost_information: CostInformation
        description: Description
        display_name: str
        filterable_properties: list[FilterableProperty]
        hierarchy_information: HierarchyInformation
        image_information: list[ImageInformation]

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


    class azure.mgmt.edgeorder.models.ProxyResource(Resource):
        id: str
        name: str
        type: str

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


    class azure.mgmt.edgeorder.models.PurchaseMeterDetails(MeterDetails):
        billing_type: Union[str, BillingType]
        charging_type: Union[str, ChargingType]
        multiplier: float
        product_id: str
        sku_id: str
        term_id: str

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


    class azure.mgmt.edgeorder.models.Resource(Model):
        id: str
        name: str
        type: str

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


    class azure.mgmt.edgeorder.models.ResourceIdentity(Model):
        principal_id: str
        tenant_id: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Optional[str] = ..., 
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


    class azure.mgmt.edgeorder.models.ResourceProviderDetails(Model):
        resource_provider_namespace: str

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


    class azure.mgmt.edgeorder.models.ReturnOrderItemDetails(Model):
        return_address: AddressProperties
        return_reason: str
        service_tag: str
        shipping_box_required: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                return_address: Optional[AddressProperties] = ..., 
                return_reason: str, 
                service_tag: Optional[str] = ..., 
                shipping_box_required: bool = False, 
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


    class azure.mgmt.edgeorder.models.ReverseShippingDetails(Model):
        carrier_display_name: str
        carrier_name: str
        sas_key_for_label: str
        tracking_id: str
        tracking_url: str

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


    class azure.mgmt.edgeorder.models.ShippingAddress(Model):
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

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                address_type: Optional[Union[str, AddressType]] = ..., 
                city: Optional[str] = ..., 
                company_name: Optional[str] = ..., 
                country: str, 
                postal_code: Optional[str] = ..., 
                state_or_province: Optional[str] = ..., 
                street_address1: str, 
                street_address2: Optional[str] = ..., 
                street_address3: Optional[str] = ..., 
                zip_extended_code: Optional[str] = ..., 
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


    class azure.mgmt.edgeorder.models.ShippingDetails(Model):
        carrier_display_name: str
        carrier_name: str
        tracking_id: str
        tracking_url: str

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


    class azure.mgmt.edgeorder.models.Specification(Model):
        name: str
        value: str

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


    class azure.mgmt.edgeorder.models.StageDetails(Model):
        display_name: str
        stage_name: Union[str, StageName]
        stage_status: Union[str, StageStatus]
        start_time: datetime

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


    class azure.mgmt.edgeorder.models.StageName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "Cancelled"
        CONFIRMED = "Confirmed"
        DELIVERED = "Delivered"
        IN_REVIEW = "InReview"
        IN_USE = "InUse"
        PLACED = "Placed"
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


    class azure.mgmt.edgeorder.models.SystemData(Model):
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


    class azure.mgmt.edgeorder.models.TrackedResource(Resource):
        id: str
        location: str
        name: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.edgeorder.models.TransportPreferences(Model):
        preferred_shipment_type: Union[str, TransportShipmentTypes]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                preferred_shipment_type: Union[str, TransportShipmentTypes], 
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


    class azure.mgmt.edgeorder.models.TransportShipmentTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOMER_MANAGED = "CustomerManaged"
        MICROSOFT_MANAGED = "MicrosoftManaged"


    class azure.mgmt.edgeorder.models.WeightMeasurementUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        KGS = "KGS"
        LBS = "LBS"


namespace azure.mgmt.edgeorder.operations

    class azure.mgmt.edgeorder.operations.EdgeOrderManagementClientOperationsMixin(EdgeOrderManagementClientMixinABC):

        @overload
        def begin_create_address(
                self, 
                address_name: str, 
                resource_group_name: str, 
                address_resource: AddressResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AddressResource]: ...

        @overload
        def begin_create_address(
                self, 
                address_name: str, 
                resource_group_name: str, 
                address_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AddressResource]: ...

        @overload
        def begin_create_order_item(
                self, 
                order_item_name: str, 
                resource_group_name: str, 
                order_item_resource: OrderItemResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OrderItemResource]: ...

        @overload
        def begin_create_order_item(
                self, 
                order_item_name: str, 
                resource_group_name: str, 
                order_item_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OrderItemResource]: ...

        @distributed_trace
        def begin_delete_address_by_name(
                self, 
                address_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_order_item_by_name(
                self, 
                order_item_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_return_order_item(
                self, 
                order_item_name: str, 
                resource_group_name: str, 
                return_order_item_details: ReturnOrderItemDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_return_order_item(
                self, 
                order_item_name: str, 
                resource_group_name: str, 
                return_order_item_details: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update_address(
                self, 
                address_name: str, 
                resource_group_name: str, 
                address_update_parameter: AddressUpdateParameter, 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AddressResource]: ...

        @overload
        def begin_update_address(
                self, 
                address_name: str, 
                resource_group_name: str, 
                address_update_parameter: IO[bytes], 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AddressResource]: ...

        @overload
        def begin_update_order_item(
                self, 
                order_item_name: str, 
                resource_group_name: str, 
                order_item_update_parameter: OrderItemUpdateParameter, 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OrderItemResource]: ...

        @overload
        def begin_update_order_item(
                self, 
                order_item_name: str, 
                resource_group_name: str, 
                order_item_update_parameter: IO[bytes], 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OrderItemResource]: ...

        @overload
        def cancel_order_item(
                self, 
                order_item_name: str, 
                resource_group_name: str, 
                cancellation_reason: CancellationReason, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def cancel_order_item(
                self, 
                order_item_name: str, 
                resource_group_name: str, 
                cancellation_reason: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_address_by_name(
                self, 
                address_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AddressResource: ...

        @distributed_trace
        def get_order_by_name(
                self, 
                order_name: str, 
                resource_group_name: str, 
                location: str, 
                **kwargs: Any
            ) -> OrderResource: ...

        @distributed_trace
        def get_order_item_by_name(
                self, 
                order_item_name: str, 
                resource_group_name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> OrderItemResource: ...

        @distributed_trace
        def list_addresses_at_resource_group_level(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                skip_token: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[AddressResource]: ...

        @distributed_trace
        def list_addresses_at_subscription_level(
                self, 
                filter: Optional[str] = None, 
                skip_token: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[AddressResource]: ...

        @overload
        def list_configurations(
                self, 
                configurations_request: ConfigurationsRequest, 
                skip_token: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Iterable[Configuration]: ...

        @overload
        def list_configurations(
                self, 
                configurations_request: IO[bytes], 
                skip_token: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Iterable[Configuration]: ...

        @distributed_trace
        def list_operations(self, **kwargs: Any) -> Iterable[Operation]: ...

        @distributed_trace
        def list_order_at_resource_group_level(
                self, 
                resource_group_name: str, 
                skip_token: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[OrderResource]: ...

        @distributed_trace
        def list_order_at_subscription_level(
                self, 
                skip_token: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[OrderResource]: ...

        @distributed_trace
        def list_order_items_at_resource_group_level(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
                skip_token: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[OrderItemResource]: ...

        @distributed_trace
        def list_order_items_at_subscription_level(
                self, 
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
                skip_token: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[OrderItemResource]: ...

        @overload
        def list_product_families(
                self, 
                product_families_request: ProductFamiliesRequest, 
                expand: Optional[str] = None, 
                skip_token: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Iterable[ProductFamily]: ...

        @overload
        def list_product_families(
                self, 
                product_families_request: IO[bytes], 
                expand: Optional[str] = None, 
                skip_token: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Iterable[ProductFamily]: ...

        @distributed_trace
        def list_product_families_metadata(
                self, 
                skip_token: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[ProductFamiliesMetadataDetails]: ...


```