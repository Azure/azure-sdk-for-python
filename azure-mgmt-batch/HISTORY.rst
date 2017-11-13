.. :changelog:

Release History
===============

5.0.0 (2017-11-13)
++++++++++++++++++

- Batch Pools are now ARM resources that can be created, updated and managed using the new client.PoolOperations.
- Batch Certificates are now ARM resources that can be created, updated and managed using the new client.CertificateOperations.

4.1.0 (2017-07-24)
++++++++++++++++++

- New operation to check the availability and validity of a Batch account name.

4.0.0 (2017-05-10)
++++++++++++++++++

- New operation to list the operations available for the Microsoft.Batch provider, includes new `Operation` and `OperationDisplay` models.
- Renamed `AddApplicationParameters` to `ApplicationCreateParameters`.
- Renamed `UpdateApplicationParameters` to `ApplicationUpdateParameters`.
- Removed `core_quota` attribute from `BatchAccount` object, now replaced by separate `dedicated_core_quota` and `low_priority_core_quota`.
- `BatchAccountKeys` object now has additional `account_name` attribute.

3.0.1 (2017-04-19)
++++++++++++++++++

- This wheel package is now built with the azure wheel extension

3.0.0 (2017-03-07)
++++++++++++++++++

- Updated `BatchAccount` model - support for pool allocation in the user's subscription.
- Updated `BatchAccount` model - support for referencing an Azure Key Vault for accounts created with a pool allocation mode of UserSubscription.
- Updated `BatchAccount` model - properties are now read only.
- Updated `ApplicationPackage` model - properties are now read only.
- Updated `BatchAccountKeys` model - properties are now read only.
- Updated `BatchLocationQuota` model - properties are now read only.

2.0.0 (2016-10-04)
++++++++++++++++++

- Renamed `AccountResource` to `BatchAccount`.
- Renamed `AccountOperations` to `BatchAccountOperations`. The `IBatchManagementClient.Account` property was also renamed to `IBatchManagementClient.BatchAccount`.
- Split `Application` and `ApplicationPackage` operations up into two separate operation groups. 
- Updated `Application` and `ApplicationPackage` methods to use the standard `Create`, `Delete`, `Update` syntax. For example creating an `Application` is done via `ApplicationOperations.Create`.
- Renamed `SubscriptionOperations` to `LocationOperations` and changed `SubscriptionOperations.GetSubscriptionQuotas` to be `LocationOperations.GetQuotas`.
- This version targets REST API version 2015-12-01.

1.0.0 (2016-08-09)
++++++++++++++++++

- Initial Release
