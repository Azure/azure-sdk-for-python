# Release History

## 2.0.0 (2022-04-20)

**Features**

  - Added operation ReservationOperations.list_all
  - Added operation ReservationOrderOperations.change_directory
  - Model CalculatePriceResponseProperties has a new parameter grand_total
  - Model CalculatePriceResponseProperties has a new parameter is_tax_included
  - Model CalculatePriceResponseProperties has a new parameter net_total
  - Model CalculatePriceResponseProperties has a new parameter tax_total
  - Model Catalog has a new parameter capabilities
  - Model Catalog has a new parameter msrp
  - Model Catalog has a new parameter size
  - Model Catalog has a new parameter tier
  - Model CurrentQuotaLimit has a new parameter id
  - Model CurrentQuotaLimit has a new parameter name
  - Model CurrentQuotaLimit has a new parameter type
  - Model CurrentQuotaLimitBase has a new parameter id
  - Model CurrentQuotaLimitBase has a new parameter name
  - Model CurrentQuotaLimitBase has a new parameter type
  - Model OperationResponse has a new parameter is_data_action
  - Model OperationResponse has a new parameter properties
  - Model QuotaRequestOneResourceSubmitResponse has a new parameter id_properties_id
  - Model QuotaRequestOneResourceSubmitResponse has a new parameter name_properties_name
  - Model QuotaRequestOneResourceSubmitResponse has a new parameter type_properties_type
  - Model ReservationOrderResponse has a new parameter benefit_start_time
  - Model ReservationOrderResponse has a new parameter system_data
  - Model ReservationResponse has a new parameter kind
  - Model ReservationResponse has a new parameter system_data

**Breaking changes**

  - Operation AzureReservationAPIOperationsMixin.get_catalog has a new parameter offer_id
  - Operation AzureReservationAPIOperationsMixin.get_catalog has a new parameter plan_id
  - Operation AzureReservationAPIOperationsMixin.get_catalog has a new parameter publisher_id

## 1.0.0 (2021-05-20)

**Features**

  - Model ReservationToPurchaseExchange has a new parameter reservation_id
  - Model ReservationToPurchaseExchange has a new parameter properties
  - Model ReservationToPurchaseCalculateExchange has a new parameter properties

**Breaking changes**

  - Removed operation ReservationOrderOperations.change_directory
  - Removed operation group AutoQuotaIncreaseOperations

## 1.0.0b1 (2020-12-09)

This is beta preview version.

This version uses a next-generation code generator that introduces important breaking changes, but also important new features (like unified authentication and async programming).

**General breaking changes**

- Credential system has been completly revamped:

  - `azure.common.credentials` or `msrestazure.azure_active_directory` instances are no longer supported, use the `azure-identity` classes instead: https://pypi.org/project/azure-identity/
  - `credentials` parameter has been renamed `credential`

- The `config` attribute no longer exists on a client, configuration should be passed as kwarg. Example: `MyClient(credential, subscription_id, enable_logging=True)`. For a complete set of
  supported options, see the [parameters accept in init documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)
- You can't import a `version` module anymore, use `__version__` instead
- Operations that used to return a `msrest.polling.LROPoller` now returns a `azure.core.polling.LROPoller` and are prefixed with `begin_`.
- Exceptions tree have been simplified and most exceptions are now `azure.core.exceptions.HttpResponseError` (`CloudError` has been removed).
- Most of the operation kwarg have changed. Some of the most noticeable:

  - `raw` has been removed. Equivalent feature can be found using `cls`, a callback that will give access to internal HTTP response for advanced user
  - For a complete set of
  supported options, see the [parameters accept in Request documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)

**General new features**

- Type annotations support using `typing`. SDKs are mypy ready.
- This client has now stable and official support for async. Check the `aio` namespace of your package to find the async client.
- This client now support natively tracing library like OpenCensus or OpenTelemetry. See this [tracing quickstart](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core-tracing-opentelemetry) for an overview.

## 0.8.0 (2020-07-15)

**Features**

  - Added operation QuotaOperations.get
  - Added operation QuotaOperations.create_or_update
  - Added operation QuotaOperations.list
  - Added operation QuotaOperations.update
  - Added operation group QuotaRequestStatusOperations
  - Added reservedResourceType

**Breaking changes**

  - Model SupportRequestAction no longer has parameter auto_quota_increase_state
  - Model QuotaRequestOneResourceSubmitResponse no longer has parameter resource_type
  - Model QuotaRequestOneResourceSubmitResponse no longer has parameter limit
  - Model QuotaRequestOneResourceSubmitResponse no longer has parameter unit
  - Model QuotaRequestOneResourceSubmitResponse no longer has parameter name1
  - Model QuotaRequestOneResourceSubmitResponse no longer has parameter current_value
  - Model QuotaRequestOneResourceSubmitResponse no longer has parameter quota_period
  - Model EmailActions has a new signature
  - Model CurrentQuotaLimit has a new signature
  - Model CurrentQuotaLimitBase has a new signature
  - Removed operation QuotaOperations.list_status
  - Removed operation group QuotasOperations
  - Removed operation group QuotaRequestOperations
  - Removed operation group QuotaRequestsOperations

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
