# Release History

## 6.0.0b1 (2020-11-20)

This is beta preview version.

This version uses a next-generation code generator that introduces important breaking changes, but also important new features (like unified authentication and async programming).

**General breaking changes**

- Credential system has been completly revamped:

  - `azure.common.credentials` or `msrestazure.azure_active_directory` instances are no longer supported, use the `azure-identity` classes instead: https://pypi.org/project/azure-identity/
  - `credentials` parameter has been renamed `credential`

- The `config` attribute no longer exists on a client, configuration should be passed as kwarg. Example: `MyClient(credential, subscription_id, enable_logging=True)`. For a complete set of
  supported options, see the [parameters accept in init documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)
- You can't import a `version` module anymore, use `__version__` instead
- Operations that used to return a `msrest.polling.LROPoller` now returns a `azure.core.polling.LROPoller` and are prefixed with `begin_`.
- Exceptions tree have been simplified and most exceptions are now `azure.core.exceptions.HttpResponseError` (`CloudError` has been removed).
- Most of the operation kwarg have changed. Some of the most noticeable:

  - `raw` has been removed. Equivalent feature can be found using `cls`, a callback that will give access to internal HTTP response for advanced user
  - For a complete set of
  supported options, see the [parameters accept in Request documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)

**General new features**

- Type annotations support using `typing`. SDKs are mypy ready.
- This client has now stable and official support for async. Check the `aio` namespace of your package to find the async client.
- This client now support natively tracing library like OpenCensus or OpenTelemetry. See this [tracing quickstart](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/core/azure-core-tracing-opentelemetry) for an overview.

## 1.0.0 (2020-10-19)

**Features**

  - Model ErrorDetails has a new parameter details
  - Added operation InvoicesOperations.download_multiple_billing_subscription_invoice
  - Added operation InvoicesOperations.get_by_id
  - Added operation InvoicesOperations.download_invoice
  - Added operation InvoicesOperations.list_by_billing_subscription
  - Added operation InvoicesOperations.list_by_billing_account
  - Added operation InvoicesOperations.download_billing_subscription_invoice
  - Added operation InvoicesOperations.download_multiple_modern_invoice
  - Added operation InvoicesOperations.list_by_billing_profile
  - Added operation InvoicesOperations.get_by_subscription_and_invoice_id
  - Added operation group InvoiceSectionsOperations
  - Added operation group PoliciesOperations
  - Added operation group InstructionsOperations
  - Added operation group ProductsOperations
  - Added operation group AddressOperations
  - Added operation group BillingProfilesOperations
  - Added operation group TransactionsOperations
  - Added operation group BillingPermissionsOperations
  - Added operation group BillingRoleDefinitionsOperations
  - Added operation group BillingRoleAssignmentsOperations
  - Added operation group BillingSubscriptionsOperations
  - Added operation group AvailableBalancesOperations
  - Added operation group CustomersOperations
  - Added operation group AgreementsOperations
  - Added operation group BillingAccountsOperations
  - Added operation group BillingPropertyOperations

**Breaking changes**

  - Model Invoice has a new signature
  - Model EnrollmentAccount has a new signature
  - Removed operation InvoicesOperations.get_latest
  - Removed operation InvoicesOperations.list

## 0.2.0 (2018-03-29)

  - Add new nrollment_accounts operation groups
  - Now all operation groups have a "models" attributes

## 0.1.0 (2017-05-18)

  - Initial Release
