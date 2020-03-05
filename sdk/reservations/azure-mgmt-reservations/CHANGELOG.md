# Release History

## 0.7.0 (2020-01-29)

**Features**

- Added operation group QuotaRequestsOperations
- Added operation group QuotaOperations
- Added operation group QuotaRequestOperations
- Added operation group AutoQuotaIncreaseOperations
- Added operation group QuotasOperations

## 0.6.0 (2019-10-24)

**Bugfix**

  - Fixed Catalog model structure not matching actual API

**Breaking changes**

  - Removed CatalogBillingPlansItem that could be considered a breaking
    change

## 0.5.0 (2019-10-04)

**Features**

  - Model ReservationProperties has a new parameter billing_plan
  - Model CalculatePriceResponseProperties has a new parameter
    payment_schedule
  - Model ReservationOrderResponse has a new parameter plan_information
  - Model ReservationOrderResponse has a new parameter billing_plan
  - Model Catalog has a new parameter billing_plans
  - Model PurchaseRequest has a new parameter billing_plan

**Breaking changes**

  - Operation ReservationOrderOperations.get has a new signature

## 0.4.0 (2019-09-09)

**Features**

  - Model ReservationProperties has a new parameter term
  - Model ReservationProperties has a new parameter renew_properties
  - Model ReservationProperties has a new parameter renew_source
  - Model ReservationProperties has a new parameter billing_scope_id
  - Model ReservationProperties has a new parameter renew
  - Model ReservationProperties has a new parameter renew_destination
  - Model Patch has a new parameter renew_properties
  - Model Patch has a new parameter renew
  - Model PurchaseRequest has a new parameter renew
  - Added operation ReservationOperations.available_scopes
  - Added operation group AzureReservationAPIOperationsMixin

**Breaking changes**

  - Operation ReservationOperations.get has a new signature

**General breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes if from some import. In summary, some modules
were incorrectly visible/importable and have been renamed. This fixed
several issues caused by usage of classes that were not supposed to be
used in the first place.

  - AzureReservationAPI cannot be imported from
    `azure.mgmt.reservations.azure_reservation_api` anymore (import
    from `azure.mgmt.reservations` works like before)
  - AzureReservationAPIConfiguration import has been moved from
    `azure.mgmt.reservations.azure_reservation_api` to
    `azure.mgmt.reservations`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.reservations.models.my_class` (import
    from `azure.mgmt.reservations.models` works like before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.reservations.operations.my_class_operations` (import
    from `azure.mgmt.reservations.operations` works like before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 0.3.2 (2019-04-18)

**Features**

  - Added operation ReservationOrderOperations.purchase
  - Added operation ReservationOrderOperations.calculate

## 0.3.1 (2018-11-05)

**Features**

  - Add redhat support

## 0.3.0 (2018-08-22)

**Features**

  - Model Patch has a new parameter 'name'
  - Enum ReservedResourceType has a new value 'cosmos_db'

## 0.2.1 (2018-06-14)

  - Provide enum definitions when applicable

## 0.2.0 (2018-06-12)

**Notes**

  -   - Changed Update Reservation API
        
          - Added optional InstanceFlexibility parameter

  - Support for InstanceFlexibility

  - Support for ReservedResourceType (VirtualMachines, SqlDatabases,
    SuseLinux)

  - Upgrade to rest api version 2018-06-01

**Breaking change**

  -   - Updated Get Catalog API
        
          - Added required parameter 'reserved_resource_type'
          - Added optional parameter 'location'

  -   - Updated Catalog model
        
          - Renamed property 'capabilities' to 'sku_properties'
          - Removed properties 'size' and 'tier'

  -   - Updated ReservationProperties model
        
          - Removed property 'kind'

## 0.1.0 (2017-11-03)

  - Initial Release
