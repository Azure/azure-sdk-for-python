.. :changelog:

Release History
===============

3.0.0 (2017-02-17)
++++++++++++++++++

- Updated `BatchAccount` model - support for pool allocation in the users subscription.
- Updated `BatchAccount` model - support for referencing an Azure Key Vault when allocation pools in users subscription.
- Updated `BatchAccount` model - properties are now read only.
- Updated `ApplicationPackage` model - properties are now read only.
- Updated `BatchAccountKeys` model - properties are now read only.
- Updated `BatchLocationQuota` model - properties are now read only.
- Update Batch Account operation now takes a `BatchAccountUpdateParameters` object rather than `tags` and `auto_storage` parameters.

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

* Initial Release
