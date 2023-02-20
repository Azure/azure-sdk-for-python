# Release History

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
