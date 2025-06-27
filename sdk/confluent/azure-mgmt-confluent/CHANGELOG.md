# Release History

## 3.0.0 (2025-06-27)

### Features Added

  - Model `APIKeyRecord` added property `properties`
  - Model `ConfluentAgreementResource` added property `properties`
  - Model `RegionRecord` added property `properties`
  - Model `SCClusterRecord` added property `properties`
  - Model `SCClusterRecord` added property `type`
  - Model `SCClusterRecord` added property `system_data`
  - Model `SCClusterSpecEntity` added property `package`
  - Model `SCEnvironmentRecord` added property `properties`
  - Model `SCEnvironmentRecord` added property `type`
  - Model `SCEnvironmentRecord` added property `system_data`
  - Model `SchemaRegistryClusterRecord` added property `properties`
  - Added model `APIKeyProperties`
  - Added enum `AuthType`
  - Added model `AzureBlobStorageSinkConnectorServiceInfo`
  - Added model `AzureBlobStorageSourceConnectorServiceInfo`
  - Added model `AzureCosmosDBSinkConnectorServiceInfo`
  - Added model `AzureCosmosDBSourceConnectorServiceInfo`
  - Added model `AzureSynapseAnalyticsSinkConnectorServiceInfo`
  - Added model `ClusterProperties`
  - Added model `ConfluentAgreementProperties`
  - Added enum `ConnectorClass`
  - Added model `ConnectorInfoBase`
  - Added model `ConnectorResource`
  - Added model `ConnectorResourceProperties`
  - Added enum `ConnectorServiceType`
  - Added model `ConnectorServiceTypeInfoBase`
  - Added enum `ConnectorStatus`
  - Added enum `ConnectorType`
  - Added enum `DataFormatType`
  - Added model `EnvironmentProperties`
  - Added model `ErrorAdditionalInfo`
  - Added model `ErrorDetail`
  - Added model `ErrorResponse`
  - Added model `KafkaAzureBlobStorageSinkConnectorInfo`
  - Added model `KafkaAzureBlobStorageSourceConnectorInfo`
  - Added model `KafkaAzureCosmosDBSinkConnectorInfo`
  - Added model `KafkaAzureCosmosDBSourceConnectorInfo`
  - Added model `KafkaAzureSynapseAnalyticsSinkConnectorInfo`
  - Added enum `Package`
  - Added enum `PartnerConnectorType`
  - Added model `PartnerInfoBase`
  - Added model `ProxyResource`
  - Added model `RegionProperties`
  - Added model `Resource`
  - Added model `SchemaRegistryClusterProperties`
  - Added model `StreamGovernanceConfig`
  - Added model `TopicMetadataEntity`
  - Added model `TopicProperties`
  - Added model `TopicRecord`
  - Added model `TopicsInputConfig`
  - Added model `TopicsRelatedLink`
  - Added model `TrackedResource`
  - Added model `ClusterOperations`
  - Added model `ConnectorOperations`
  - Added model `EnvironmentOperations`
  - Added model `TopicsOperations`

### Breaking Changes

  - Deleted or renamed client `ConfluentManagementClient`
  - Model `APIKeyRecord` deleted or renamed its instance variable `metadata`
  - Model `APIKeyRecord` deleted or renamed its instance variable `spec`
  - Model `ConfluentAgreementResource` deleted or renamed its instance variable `publisher`
  - Model `ConfluentAgreementResource` deleted or renamed its instance variable `product`
  - Model `ConfluentAgreementResource` deleted or renamed its instance variable `plan`
  - Model `ConfluentAgreementResource` deleted or renamed its instance variable `license_text_link`
  - Model `ConfluentAgreementResource` deleted or renamed its instance variable `privacy_policy_link`
  - Model `ConfluentAgreementResource` deleted or renamed its instance variable `retrieve_datetime`
  - Model `ConfluentAgreementResource` deleted or renamed its instance variable `signature`
  - Model `ConfluentAgreementResource` deleted or renamed its instance variable `accepted`
  - Model `RegionRecord` deleted or renamed its instance variable `metadata`
  - Model `RegionRecord` deleted or renamed its instance variable `spec`
  - Model `SCClusterRecord` deleted or renamed its instance variable `metadata`
  - Model `SCClusterRecord` deleted or renamed its instance variable `spec`
  - Model `SCClusterRecord` deleted or renamed its instance variable `status`
  - Model `SCEnvironmentRecord` deleted or renamed its instance variable `metadata`
  - Model `SchemaRegistryClusterRecord` deleted or renamed its instance variable `metadata`
  - Model `SchemaRegistryClusterRecord` deleted or renamed its instance variable `spec`
  - Model `SchemaRegistryClusterRecord` deleted or renamed its instance variable `status`
  - Deleted or renamed model `ConfluentAgreementResourceListResponse`
  - Deleted or renamed model `GetEnvironmentsResponse`
  - Deleted or renamed model `ListClustersSuccessResponse`
  - Deleted or renamed model `ListSchemaRegistryClustersResponse`
  - Deleted or renamed model `SCConfluentListMetadata`
  - Method `OrganizationOperations.list_clusters` changed its parameter `page_size` from `positional_or_keyword` to `keyword_only`
  - Method `OrganizationOperations.list_clusters` changed its parameter `page_token` from `positional_or_keyword` to `keyword_only`
  - Method `OrganizationOperations.list_environments` changed its parameter `page_size` from `positional_or_keyword` to `keyword_only`
  - Method `OrganizationOperations.list_environments` changed its parameter `page_token` from `positional_or_keyword` to `keyword_only`
  - Method `OrganizationOperations.list_schema_registry_clusters` changed its parameter `page_size` from `positional_or_keyword` to `keyword_only`
  - Method `OrganizationOperations.list_schema_registry_clusters` changed its parameter `page_token` from `positional_or_keyword` to `keyword_only`

## 2.1.0 (2024-03-18)

### Features Added

  - Added operation AccessOperations.create_role_binding
  - Added operation AccessOperations.delete_role_binding
  - Added operation AccessOperations.list_role_binding_name_list
  - Added operation OrganizationOperations.create_api_key
  - Added operation OrganizationOperations.delete_cluster_api_key
  - Added operation OrganizationOperations.get_cluster_api_key
  - Added operation OrganizationOperations.get_cluster_by_id
  - Added operation OrganizationOperations.get_environment_by_id
  - Added operation OrganizationOperations.get_schema_registry_cluster_by_id
  - Added operation OrganizationOperations.list_clusters
  - Added operation OrganizationOperations.list_environments
  - Added operation OrganizationOperations.list_regions
  - Added operation OrganizationOperations.list_schema_registry_clusters

## 2.0.0 (2023-11-20)

### Features Added

  - Added operation group AccessOperations
  - Added operation group ValidationsOperations
  - Model ConfluentAgreementResource has a new parameter system_data
  - Model OfferDetail has a new parameter private_offer_id
  - Model OfferDetail has a new parameter private_offer_ids
  - Model OfferDetail has a new parameter term_id
  - Model OrganizationResource has a new parameter link_organization
  - Model OrganizationResource has a new parameter system_data
  - Model UserDetail has a new parameter aad_email
  - Model UserDetail has a new parameter user_principal_name

### Breaking Changes

  - Parameter email_address of model UserDetail is now required
  - Parameter id of model OfferDetail is now required
  - Parameter offer_detail of model OrganizationResource is now required
  - Parameter plan_id of model OfferDetail is now required
  - Parameter plan_name of model OfferDetail is now required
  - Parameter publisher_id of model OfferDetail is now required
  - Parameter term_unit of model OfferDetail is now required
  - Parameter user_detail of model OrganizationResource is now required

## 2.0.0b2 (2022-11-02)

### Features Added

  - Added operation group ValidationsOperations
  - Model ConfluentAgreementResource has a new parameter system_data
  - Model OrganizationResource has a new parameter system_data

### Breaking Changes

  - Parameter email_address of model UserDetail is now required
  - Parameter id of model OfferDetail is now required
  - Parameter offer_detail of model OrganizationResource is now required
  - Parameter plan_id of model OfferDetail is now required
  - Parameter plan_name of model OfferDetail is now required
  - Parameter publisher_id of model OfferDetail is now required
  - Parameter term_unit of model OfferDetail is now required
  - Parameter user_detail of model OrganizationResource is now required

## 2.0.0b1 (2021-05-24)

**Features**

  - Model ConfluentAgreementResource has a new parameter system_data
  - Model OrganizationResource has a new parameter system_data
  - Added operation group ValidationsOperations

**Breaking changes**

  - Parameter offer_detail of model OrganizationResource is now required
  - Parameter user_detail of model OrganizationResource is now required
  - Parameter email_address of model UserDetail is now required
  - Parameter plan_name of model OfferDetail is now required
  - Parameter term_unit of model OfferDetail is now required
  - Parameter plan_id of model OfferDetail is now required
  - Parameter publisher_id of model OfferDetail is now required
  - Parameter id of model OfferDetail is now required

## 1.0.0 (2021-01-18)

**Features**

  - Model OperationResult has a new parameter is_data_action

**Breaking changes**
  - Operation MarketplaceAgreementsOperations.create has a new signature
  - Operation OrganizationOperations.update has a new signature
  - Model ConfluentAgreementResource has a new signature

## 1.0.0b1 (2020-11-23)

* Initial Release
