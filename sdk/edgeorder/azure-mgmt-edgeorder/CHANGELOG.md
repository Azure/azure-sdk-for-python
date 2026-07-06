# Release History

## 3.0.0b1 (2026-07-06)

### Features Added

  - Model `AddressProperties` added property `address_classification`
  - Model `AddressProperties` added property `provisioning_state`
  - Enum `AvailabilityStage` added member `DISCOVERABLE`
  - Model `BasicInformation` added property `fulfilled_by`
  - Model `BillingMeterDetails` added property `term_type_details`
  - Model `CommonProperties` added property `fulfilled_by`
  - Model `ConfigurationProperties` added property `provisioning_support`
  - Model `ConfigurationProperties` added property `child_configuration_types`
  - Model `ConfigurationProperties` added property `grouped_child_configurations`
  - Model `ConfigurationProperties` added property `supported_term_commitment_durations`
  - Model `ConfigurationProperties` added property `fulfilled_by`
  - Model `ConfigurationsRequest` added property `configuration_filter`
  - Model `DeviceDetails` added property `display_serial_number`
  - Model `DeviceDetails` added property `provisioning_support`
  - Model `DeviceDetails` added property `provisioning_details`
  - Model `HierarchyInformation` added property `configuration_id_display_name`
  - Enum `LinkType` added member `DISCOVERABLE`
  - Model `OrderItemDetails` added property `order_item_mode`
  - Model `OrderItemDetails` added property `site_details`
  - Model `OrderItemResource` added property `identity`
  - Enum `OrderItemType` added member `EXTERNAL`
  - Model `OrderItemUpdateParameter` added property `identity`
  - Model `Preferences` added property `term_commitment_preferences`
  - Model `ProductDetails` added property `identification_type`
  - Model `ProductDetails` added property `parent_device_details`
  - Model `ProductDetails` added property `parent_provisioning_details`
  - Model `ProductDetails` added property `opt_in_additional_configurations`
  - Model `ProductDetails` added property `child_configuration_device_details`
  - Model `ProductDetails` added property `term_commitment_information`
  - Model `ProductFamilyProperties` added property `fulfilled_by`
  - Model `ProductLineProperties` added property `fulfilled_by`
  - Model `ProductProperties` added property `fulfilled_by`
  - Model `ProxyResource` added property `system_data`
  - Model `Resource` added property `system_data`
  - Model `ResourceIdentity` added property `user_assigned_identities`
  - Enum `StageName` added member `READY_TO_SETUP`
  - Model `TrackedResource` added property `system_data`
  - Added model `AdditionalConfiguration`
  - Added enum `AddressClassification`
  - Added enum `AutoProvisioningStatus`
  - Added model `CategoryInformation`
  - Added model `ChildConfiguration`
  - Added model `ChildConfigurationFilter`
  - Added model `ChildConfigurationProperties`
  - Added enum `ChildConfigurationType`
  - Added model `ConfigurationDeviceDetails`
  - Added model `ConfigurationFilter`
  - Added model `DevicePresenceVerificationDetails`
  - Added enum `DevicePresenceVerificationStatus`
  - Added enum `FulfillmentType`
  - Added model `GroupedChildConfigurations`
  - Added enum `IdentificationType`
  - Added model `OrderItemDetailsUpdateParameter`
  - Added enum `OrderMode`
  - Added model `ProductDetailsUpdateParameter`
  - Added model `ProvisioningDetails`
  - Added enum `ProvisioningState`
  - Added enum `ProvisioningSupport`
  - Added model `SiteDetails`
  - Added model `TermCommitmentInformation`
  - Added model `TermCommitmentPreferences`
  - Added enum `TermCommitmentType`
  - Added model `TermTypeDetails`
  - Added model `UserAssignedIdentity`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - Deleted or renamed client `EdgeOrderManagementClient`
  - Model `AddressResource` moved instance variable `shipping_address`, `contact_details` and `address_validation_status` under property `properties` whose type is `AddressProperties`
  - Model `AddressUpdateParameter` moved instance variable `shipping_address` and `contact_details` under property `properties` whose type is `AddressUpdateProperties`
  - Model `Configuration` moved instance variable `display_name`, `description`, `image_information`, `cost_information`, `availability_information`, `hierarchy_information`, `filterable_properties`, `specifications` and `dimensions` under property `properties` whose type is `ConfigurationProperties`
  - Model `ConfigurationsRequest` renamed its instance variable `configuration_filters` to `configuration_filter`
  - Model `OrderItemDetails` renamed its instance variable `management_rp_details` to `management_rp_details_list`
  - Model `OrderItemResource` moved instance variable `order_item_details`, `address_details`, `start_time` and `order_id` under property `properties` whose type is `OrderItemProperties`
  - Model `OrderItemUpdateParameter` moved instance variable `forward_address`, `preferences` and `notification_email_list` under property `properties` whose type is `OrderItemUpdateProperties`
  - Model `OrderResource` moved instance variable `order_item_ids`, `current_stage` and `order_stage_history` under property `properties` whose type is `OrderProperties`
  - Model `Product` moved instance variable `display_name`, `description`, `image_information`, `cost_information`, `availability_information`, `hierarchy_information`, `filterable_properties` and `configurations` under property `properties` whose type is `ProductProperties`
  - Model `ProductDetails` renamed its instance variable `device_details` to `parent_device_details`
  - Model `ProductDetails` deleted or renamed its instance variable `count`
  - Model `ProductFamiliesMetadataDetails` moved instance variable `display_name`, `description`, `image_information`, `cost_information`, `availability_information`, `hierarchy_information`, `filterable_properties`, `product_lines` and `resource_provider_details` under property `properties` whose type is `ProductFamilyProperties`
  - Model `ProductFamily` moved instance variable `display_name`, `description`, `image_information`, `cost_information`, `availability_information`, `hierarchy_information`, `filterable_properties`, `product_lines` and `resource_provider_details` under property `properties` whose type is `ProductFamilyProperties`
  - Model `ProductLine` moved instance variable `display_name`, `description`, `image_information`, `cost_information`, `availability_information`, `hierarchy_information`, `filterable_properties` and `products` under property `properties` whose type is `ProductLineProperties`

### Other Changes

  - Deleted model `AddressResourceList`/`ConfigurationFilters`/`Configurations`/`OperationListResult`/`OrderItemResourceList`/`OrderResourceList`/`ProductFamilies`/`ProductFamiliesMetadata`/`ShippingDetails`/`EdgeOrderManagementClientOperationsMixin` which actually were not used by SDK users

## 2.0.0 (2024-10-30)

### Breaking Changes

  - This package now only targets the latest Api-Version available on Azure and removes APIs of other Api-Version. After this change, the package can have much smaller size. If your application requires a specific and non-latest Api-Version, it's recommended to pin this package to the previous released version; If your application always only use latest Api-Version, please ignore this change.

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
