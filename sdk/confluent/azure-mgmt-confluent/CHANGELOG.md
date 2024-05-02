# Release History

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
