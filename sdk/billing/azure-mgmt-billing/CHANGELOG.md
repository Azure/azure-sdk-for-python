# Release History

## 0.3.0 (2020-10-10)
**Features**

  - Model ErrorDetails has a new parameter details
  - Added operation InvoicesOperations.download_billing_subscription_invoice
  - Added operation InvoicesOperations.list_by_billing_profile
  - Added operation InvoicesOperations.list_by_billing_subscription
  - Added operation InvoicesOperations.list_by_billing_account
  - Added operation InvoicesOperations.get_by_subscription_and_invoice_id
  - Added operation InvoicesOperations.get_by_id
  - Added operation InvoicesOperations.download_multiple_billing_subscription_invoice
  - Added operation InvoicesOperations.download_invoice
  - Added operation InvoicesOperations.download_multiple_modern_invoice
  - Added operation group AddressOperations
  - Added operation group BillingRoleDefinitionsOperations
  - Added operation group ProductsOperations
  - Added operation group BillingPermissionsOperations
  - Added operation group BillingPropertyOperations
  - Added operation group InvoiceSectionsOperations
  - Added operation group AgreementsOperations
  - Added operation group BillingRoleAssignmentsOperations
  - Added operation group TransactionsOperations
  - Added operation group BillingAccountsOperations
  - Added operation group PoliciesOperations
  - Added operation group BillingSubscriptionsOperations
  - Added operation group InstructionsOperations
  - Added operation group CustomersOperations
  - Added operation group BillingProfilesOperations
  - Added operation group AvailableBalancesOperations

**Breaking changes**

  - Model EnrollmentAccount has a new signature
  - Model Invoice has a new signature
  - Removed operation InvoicesOperations.get_latest
  - Removed operation InvoicesOperations.list

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes. In summary, some modules were incorrectly
visible/importable and have been renamed. This fixed several issues
caused by usage of classes that were not supposed to be used in the
first place.

  - Model signatures now use only keyword-argument syntax. All
    positional arguments must be re-written as keyword-arguments. To
    keep auto-completion in most cases, models are now generated for
    Python 2 and Python 3. Python 3 uses the "*" syntax for
    keyword-only arguments.
  - Enum types now use the "str" mixin (class AzureEnum(str, Enum)) to
    improve the behavior when unrecognized enum values are encountered.
    While this is not a breaking change, the distinctions are important,
    and are documented here:
    <https://docs.python.org/3/library/enum.html#others> At a glance:
      - "is" should not be used at all.
      - "format" will return the string value, where "%s" string
        formatting will return `NameOfEnum.stringvalue`. Format syntax
        should be prefered.
  - New Long Running Operation:
      - Return type changes from
        `msrestazure.azure_operation.AzureOperationPoller` to
        `msrest.polling.LROPoller`. External API is the same.
      - Return type is now **always** a `msrest.polling.LROPoller`,
        regardless of the optional parameters used.
      - The behavior has changed when using `raw=True`. Instead of
        returning the initial call result as `ClientRawResponse`,
        without polling, now this returns an LROPoller. After polling,
        the final resource will be returned as a `ClientRawResponse`.
      - New `polling` parameter. The default behavior is
        `Polling=True` which will poll using ARM algorithm. When
        `Polling=False`, the response of the initial call will be
        returned without polling.
      - `polling` parameter accepts instances of subclasses of
        `msrest.polling.PollingMethod`.
      - `add_done_callback` will no longer raise if called after
        polling is finished, but will instead execute the callback right
        away.
  - BillingManagementClient cannot be imported from
    `azure.mgmt.billing.billing_management_client` anymore (import from
    `azure.mgmt.billing` works like before)
  - BillingManagementClientConfiguration import has been moved from
    `azure.mgmt.billing.billing_management_client` 
    to `azure.mgmt.billing`  
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.billing.models.my_class` (import from
    `azure.mgmt.billing.models` works like before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.billing.operations.my_class_operations` (import from
    `azure.mgmt.billing.operations` works like before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 0.2.0 (2018-03-29)

  - Add new nrollment_accounts operation groups
  - Now all operation groups have a "models" attributes

## 0.1.0 (2017-05-18)

  - Initial Release
