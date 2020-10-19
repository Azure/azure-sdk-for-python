# Release History

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
