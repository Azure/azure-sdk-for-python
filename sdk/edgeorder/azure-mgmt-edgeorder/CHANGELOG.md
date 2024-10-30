# Release History

## 2.0.0 (2024-10-30)

### Features Added

  - Enum `LengthHeightUnit` added member `IN`
  - Method `EdgeOrderManagementClient.begin_create_address` has a new overload `def begin_create_address(self: None, address_name: str, resource_group_name: str, address_resource: AddressResource, content_type: str)`
  - Method `EdgeOrderManagementClient.begin_create_address` has a new overload `def begin_create_address(self: None, address_name: str, resource_group_name: str, address_resource: IO[bytes], content_type: str)`
  - Method `EdgeOrderManagementClient.begin_create_order_item` has a new overload `def begin_create_order_item(self: None, order_item_name: str, resource_group_name: str, order_item_resource: OrderItemResource, content_type: str)`
  - Method `EdgeOrderManagementClient.begin_create_order_item` has a new overload `def begin_create_order_item(self: None, order_item_name: str, resource_group_name: str, order_item_resource: IO[bytes], content_type: str)`
  - Method `EdgeOrderManagementClient.begin_return_order_item` has a new overload `def begin_return_order_item(self: None, order_item_name: str, resource_group_name: str, return_order_item_details: ReturnOrderItemDetails, content_type: str)`
  - Method `EdgeOrderManagementClient.begin_return_order_item` has a new overload `def begin_return_order_item(self: None, order_item_name: str, resource_group_name: str, return_order_item_details: IO[bytes], content_type: str)`
  - Method `EdgeOrderManagementClient.begin_update_address` has a new overload `def begin_update_address(self: None, address_name: str, resource_group_name: str, address_update_parameter: AddressUpdateParameter, if_match: Optional[str], content_type: str)`
  - Method `EdgeOrderManagementClient.begin_update_address` has a new overload `def begin_update_address(self: None, address_name: str, resource_group_name: str, address_update_parameter: IO[bytes], if_match: Optional[str], content_type: str)`
  - Method `EdgeOrderManagementClient.begin_update_order_item` has a new overload `def begin_update_order_item(self: None, order_item_name: str, resource_group_name: str, order_item_update_parameter: OrderItemUpdateParameter, if_match: Optional[str], content_type: str)`
  - Method `EdgeOrderManagementClient.begin_update_order_item` has a new overload `def begin_update_order_item(self: None, order_item_name: str, resource_group_name: str, order_item_update_parameter: IO[bytes], if_match: Optional[str], content_type: str)`
  - Method `EdgeOrderManagementClient.cancel_order_item` has a new overload `def cancel_order_item(self: None, order_item_name: str, resource_group_name: str, cancellation_reason: CancellationReason, content_type: str)`
  - Method `EdgeOrderManagementClient.cancel_order_item` has a new overload `def cancel_order_item(self: None, order_item_name: str, resource_group_name: str, cancellation_reason: IO[bytes], content_type: str)`
  - Method `EdgeOrderManagementClient.list_configurations` has a new overload `def list_configurations(self: None, configurations_request: ConfigurationsRequest, skip_token: Optional[str], content_type: str)`
  - Method `EdgeOrderManagementClient.list_configurations` has a new overload `def list_configurations(self: None, configurations_request: IO[bytes], skip_token: Optional[str], content_type: str)`
  - Method `EdgeOrderManagementClient.list_product_families` has a new overload `def list_product_families(self: None, product_families_request: ProductFamiliesRequest, expand: Optional[str], skip_token: Optional[str], content_type: str)`
  - Method `EdgeOrderManagementClient.list_product_families` has a new overload `def list_product_families(self: None, product_families_request: IO[bytes], expand: Optional[str], skip_token: Optional[str], content_type: str)`
  - Method `EdgeOrderManagementClientOperationsMixin.begin_create_address` has a new overload `def begin_create_address(self: None, address_name: str, resource_group_name: str, address_resource: AddressResource, content_type: str)`
  - Method `EdgeOrderManagementClientOperationsMixin.begin_create_address` has a new overload `def begin_create_address(self: None, address_name: str, resource_group_name: str, address_resource: IO[bytes], content_type: str)`
  - Method `EdgeOrderManagementClientOperationsMixin.begin_create_order_item` has a new overload `def begin_create_order_item(self: None, order_item_name: str, resource_group_name: str, order_item_resource: OrderItemResource, content_type: str)`
  - Method `EdgeOrderManagementClientOperationsMixin.begin_create_order_item` has a new overload `def begin_create_order_item(self: None, order_item_name: str, resource_group_name: str, order_item_resource: IO[bytes], content_type: str)`
  - Method `EdgeOrderManagementClientOperationsMixin.begin_return_order_item` has a new overload `def begin_return_order_item(self: None, order_item_name: str, resource_group_name: str, return_order_item_details: ReturnOrderItemDetails, content_type: str)`
  - Method `EdgeOrderManagementClientOperationsMixin.begin_return_order_item` has a new overload `def begin_return_order_item(self: None, order_item_name: str, resource_group_name: str, return_order_item_details: IO[bytes], content_type: str)`
  - Method `EdgeOrderManagementClientOperationsMixin.begin_update_address` has a new overload `def begin_update_address(self: None, address_name: str, resource_group_name: str, address_update_parameter: AddressUpdateParameter, if_match: Optional[str], content_type: str)`
  - Method `EdgeOrderManagementClientOperationsMixin.begin_update_address` has a new overload `def begin_update_address(self: None, address_name: str, resource_group_name: str, address_update_parameter: IO[bytes], if_match: Optional[str], content_type: str)`
  - Method `EdgeOrderManagementClientOperationsMixin.begin_update_order_item` has a new overload `def begin_update_order_item(self: None, order_item_name: str, resource_group_name: str, order_item_update_parameter: OrderItemUpdateParameter, if_match: Optional[str], content_type: str)`
  - Method `EdgeOrderManagementClientOperationsMixin.begin_update_order_item` has a new overload `def begin_update_order_item(self: None, order_item_name: str, resource_group_name: str, order_item_update_parameter: IO[bytes], if_match: Optional[str], content_type: str)`
  - Method `EdgeOrderManagementClientOperationsMixin.cancel_order_item` has a new overload `def cancel_order_item(self: None, order_item_name: str, resource_group_name: str, cancellation_reason: CancellationReason, content_type: str)`
  - Method `EdgeOrderManagementClientOperationsMixin.cancel_order_item` has a new overload `def cancel_order_item(self: None, order_item_name: str, resource_group_name: str, cancellation_reason: IO[bytes], content_type: str)`
  - Method `EdgeOrderManagementClientOperationsMixin.list_configurations` has a new overload `def list_configurations(self: None, configurations_request: ConfigurationsRequest, skip_token: Optional[str], content_type: str)`
  - Method `EdgeOrderManagementClientOperationsMixin.list_configurations` has a new overload `def list_configurations(self: None, configurations_request: IO[bytes], skip_token: Optional[str], content_type: str)`
  - Method `EdgeOrderManagementClientOperationsMixin.list_product_families` has a new overload `def list_product_families(self: None, product_families_request: ProductFamiliesRequest, expand: Optional[str], skip_token: Optional[str], content_type: str)`
  - Method `EdgeOrderManagementClientOperationsMixin.list_product_families` has a new overload `def list_product_families(self: None, product_families_request: IO[bytes], expand: Optional[str], skip_token: Optional[str], content_type: str)`

### Breaking Changes

  - Method `EdgeOrderManagementClient.__init__` parameter `base_url` changed default value from `None` to `str`
  - Deleted or renamed enum value `LengthHeightUnit.IN_ENUM`

## 2.0.0b1 (2023-02-13)

### Features Added

  - Added operation group AddressesOperations
  - Added operation group Operations
  - Added operation group OrderItemsOperations
  - Added operation group OrdersOperations
  - Added operation group ProductsAndConfigurationsOperations
  - Model BasicInformation has a new parameter fulfilled_by
  - Model CommonProperties has a new parameter fulfilled_by
  - Model Configuration has a new parameter child_configuration_types
  - Model Configuration has a new parameter fulfilled_by
  - Model Configuration has a new parameter grouped_child_configurations
  - Model ConfigurationProperties has a new parameter child_configuration_types
  - Model ConfigurationProperties has a new parameter fulfilled_by
  - Model ConfigurationProperties has a new parameter grouped_child_configurations
  - Model ConfigurationsRequest has a new parameter configuration_filter
  - Model OrderItemDetails has a new parameter order_item_mode
  - Model OrderResource has a new parameter order_mode
  - Model Product has a new parameter fulfilled_by
  - Model ProductDetails has a new parameter child_configuration_device_details
  - Model ProductDetails has a new parameter identification_type
  - Model ProductDetails has a new parameter opt_in_additional_configurations
  - Model ProductDetails has a new parameter parent_device_details
  - Model ProductFamiliesMetadataDetails has a new parameter fulfilled_by
  - Model ProductFamily has a new parameter fulfilled_by
  - Model ProductFamilyProperties has a new parameter fulfilled_by
  - Model ProductLine has a new parameter fulfilled_by
  - Model ProductLineProperties has a new parameter fulfilled_by
  - Model ProductProperties has a new parameter fulfilled_by

### Breaking Changes

  - Model ConfigurationsRequest no longer has parameter configuration_filters
  - Model OrderItemDetails no longer has parameter management_rp_details
  - Model ProductDetails no longer has parameter count
  - Model ProductDetails no longer has parameter device_details

## 1.0.0 (2021-12-23)

**Features**

  - Model OrderItemDetails has a new parameter management_rp_details_list
  - Model ReturnOrderItemDetails has a new parameter shipping_box_required
  - Model ReturnOrderItemDetails has a new parameter service_tag
  - Model AddressResource has a new parameter address_validation_status
  - Model DeviceDetails has a new parameter management_resource_tenant_id
  - Model ProductFamily has a new parameter resource_provider_details
  - Model ProductFamilyProperties has a new parameter resource_provider_details
  - Model ProductFamiliesMetadataDetails has a new parameter resource_provider_details
  - Model ProductDetails has a new parameter product_double_encryption_status
  - Model AddressProperties has a new parameter address_validation_status

**Breaking changes**

  - Operation EdgeOrderManagementClientOperationsMixin.list_order_items_at_subscription_level has a new signature

## 1.0.0b1 (2021-07-27)

* Initial Release
