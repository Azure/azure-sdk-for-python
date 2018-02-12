.. :changelog:

Release History
===============
0.4.0 (2018-02-12)
++++++++++++++++++

**Breaking changes**

- The account operations object has been changed from "account" to "accounts"
    - E.g., account.get(...) to accounts.get(...)
- When creating or updating resources (accounts, firewall rules, etc.), explicit parameter objects are now required:
    - Account creation:
        - "DataLakeStoreAccount" to "CreateDataLakeStoreAccountParameters"
            - List of "FirewallRule" to "CreateFirewallRuleWithAccountParameters"
            - List of "TrustedIdProvider" to "CreateTrustedIdProviderWithAccountParameters"
    - Account update:
        - "DataLakeStoreUpdateParameters" to "UpdateDataLakeStoreParameters"
            - List of "FirewallRule" to "UpdateFirewallRuleWithAccountParameters"
            - List of "TrustedIdProvider" to "UpdateTrustedIdProviderWithAccountParameters"
    - Firewall rule creation and update:
        - "FirewallRule" to "CreateOrUpdateFirewallRuleParameters"
        - "FirewallRule" to "UpdateFirewallRuleParameters"
    - Trusted identity provider creation and update:
        - "TrustedIdProvider" to "CreateOrUpdateTrustedIdProviderParameters"
        - "TrustedIdProvider" to "UpdateTrustedIdProviderParameters"

0.3.0 (2018-01-09)
++++++++++++++++++

**Breaking changes**

* Changed the ODataQuery parameter type from DataLakeStoreAccount to DataLakeStoreAccountBasic for these APIs:

  * Account_List
  * Account_ListByResourceGroup

**Notes**

* Added two more states to DataLakeStoreAccountStatus enum: Undeleting and Canceled
* Added new Account APIs:

  * Account_CheckNameAvailability
  * Location_GetCapability
  * Operation_List

0.2.0 (2017-08-17)
++++++++++++++++++

**Breaking change**

* When getting a list of accounts, the object type that is returned is DataLakeAnalyticsAccountBasic and not DataLakeAnalyticsAccount (more information on the difference is below in the Notes section)
* Standardized the parameter name for file paths in the url (e.g. fileDestination to path)

**Notes**

* When getting a list of accounts, the account information for each account now includes a strict subset of the account information that is returned when getting a single account
  
  * There are two ways to get a list of accounts: List and ListByResource methods
  * The following fields are included in the account information when getting a list of accounts, which is less than the account information retrieved for a single account:
    
	* provisioningState
	* state
	* creationTime
	* lastModifiedTime
	* endpoint
	
* When retrieving account information, an account id field called "accountId" is now included.
  
  * accountId's description: The unique identifier associated with this Data Lake Analytics account.

0.1.6 (2017-06-19)
++++++++++++++++++
* Fixing a regression discovered in 0.1.5. Please update to 0.1.6 to avoid any issues caused by that regression.

0.1.5 (2017-06-07)
++++++++++++++++++

**New features**

* Add support for updating a User Managed KeyVault key.

0.1.4 (2017-04-20)
++++++++++++++++++

This wheel package is now built with the azure wheel extension

0.1.3 (2017-02-13)
++++++++++++++++++

**New features**

* Added extended firewall rule support, enabling allowing/blocking all azure IP traffic
* Add Update support for existing firewall rules (instead of replace)
* Added support for updating existing trusted identity providers (instead of replace)
* Fix various documentation bugs to reflect accurate information.

0.1.2 (2017-01-09)
++++++++++++++++++

**New features**

* Added the ability to create and update accounts with usage commitment levels for Data Lake Store and Data Lake Analytics

0.1.1 (2016-12-12)
++++++++++++++++++

**Breaking change**

* "account_name" parameter is now "name" in account operation

0.1.0 (2016-11-14)
++++++++++++++++++

* Initial Release
