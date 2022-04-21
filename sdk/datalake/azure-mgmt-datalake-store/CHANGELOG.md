# Release History

## 1.0.0 (2020-12-21)

**Breaking changes**

  - Operation FirewallRulesOperations.create_or_update has a new signature
  - Operation FirewallRulesOperations.update has a new signature
  - Operation VirtualNetworkRulesOperations.create_or_update has a new signature
  - Operation VirtualNetworkRulesOperations.update has a new signature
  - Operation TrustedIdProvidersOperations.create_or_update has a new signature
  - Operation TrustedIdProvidersOperations.update has a new signature
  - Operation AccountsOperations.check_name_availability has a new signature
  - Operation FirewallRulesOperations.update has a new signature
  - Operation FirewallRulesOperations.create_or_update has a new signature

## 1.0.0b1 (2020-10-31)

This is beta preview version.
For detailed changelog please refer to equivalent stable version 0.5.0 (https://pypi.org/project/azure-mgmt-datalake-store/0.5.0/)

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
  - For a complete set of supported options, see the [parameters accept in Request documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)

**General new features**

- Type annotations support using `typing`. SDKs are mypy ready.
- This client has now stable and official support for async. Check the `aio` namespace of your package to find the async client.
- This client now support natively tracing library like OpenCensus or OpenTelemetry. See this [tracing quickstart](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core-tracing-opentelemetry) for an overview.

## 0.5.0 (2018-06-14)

**Features**

  - Model CreateDataLakeStoreAccountParameters has a new parameter
    virtual_network_rules
  - Model DataLakeStoreAccount has a new parameter
    virtual_network_rules
  - Model UpdateDataLakeStoreAccountParameters has a new parameter
    virtual_network_rules
  - Added operation group VirtualNetworkRulesOperations
  - Client class can be used as a context manager to keep the underlying
    HTTP session open for performance

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes.

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

**Bugfixes**

  - Compatibility of the sdist with wheel 0.31.0

## 0.4.0 (2018-02-12)

**Breaking changes**

  -   - The account operations object has been changed from "account" to
        "accounts"

          - E.g., account.get(...) to accounts.get(...)

  -   - When creating or updating resources (accounts, firewall rules,
        etc.), explicit parameter objects are now required:

          -   - Account creation:

                  -   - "DataLakeStoreAccount" to
                        "CreateDataLakeStoreAccountParameters"

                          - List of "FirewallRule" to
                            "CreateFirewallRuleWithAccountParameters"
                          - List of "TrustedIdProvider" to
                            "CreateTrustedIdProviderWithAccountParameters"

          -   - Account update:

                  -   - "DataLakeStoreUpdateParameters" to
                        "UpdateDataLakeStoreParameters"

                          - List of "FirewallRule" to
                            "UpdateFirewallRuleWithAccountParameters"
                          - List of "TrustedIdProvider" to
                            "UpdateTrustedIdProviderWithAccountParameters"

          -   - Firewall rule creation and update:

                  - "FirewallRule" to
                    "CreateOrUpdateFirewallRuleParameters"
                  - "FirewallRule" to "UpdateFirewallRuleParameters"

          -   - Trusted identity provider creation and update:

                  - "TrustedIdProvider" to
                    "CreateOrUpdateTrustedIdProviderParameters"
                  - "TrustedIdProvider" to
                    "UpdateTrustedIdProviderParameters"

## 0.3.0 (2018-01-09)

**Breaking changes**

  - Changed the ODataQuery parameter type from DataLakeStoreAccount to
    DataLakeStoreAccountBasic for these APIs:
      - Account_List
      - Account_ListByResourceGroup

**Notes**

  - Added two more states to DataLakeStoreAccountStatus enum: Undeleting
    and Canceled
  - Added new Account APIs:
      - Account_CheckNameAvailability
      - Location_GetCapability
      - Operation_List

## 0.2.0 (2017-08-17)

**Breaking change**

  - When getting a list of accounts, the object type that is returned is
    DataLakeAnalyticsAccountBasic and not DataLakeAnalyticsAccount (more
    information on the difference is below in the Notes section)
  - Standardized the parameter name for file paths in the url (e.g.
    fileDestination to path)

**Notes**

  - When getting a list of accounts, the account information for each
    account now includes a strict subset of the account information that
    is returned when getting a single account
      - There are two ways to get a list of accounts: List and
        ListByResource methods
      - The following fields are included in the account information
        when getting a list of accounts, which is less than the account
        information retrieved for a single account:
          - provisioningState
          - state
          - creationTime
          - lastModifiedTime
          - endpoint
  - When retrieving account information, an account id field called
    "accountId" is now included.
      - accountId's description: The unique identifier associated with
        this Data Lake Analytics account.

## 0.1.6 (2017-06-19)

  - Fixing a regression discovered in 0.1.5. Please update to 0.1.6 to
    avoid any issues caused by that regression.

## 0.1.5 (2017-06-07)

**New features**

  - Add support for updating a User Managed KeyVault key.

## 0.1.4 (2017-04-20)

This wheel package is now built with the azure wheel extension

## 0.1.3 (2017-02-13)

**New features**

  - Added extended firewall rule support, enabling allowing/blocking all
    azure IP traffic
  - Add Update support for existing firewall rules (instead of replace)
  - Added support for updating existing trusted identity providers
    (instead of replace)
  - Fix various documentation bugs to reflect accurate information.

## 0.1.2 (2017-01-09)

**New features**

  - Added the ability to create and update accounts with usage
    commitment levels for Data Lake Store and Data Lake Analytics

## 0.1.1 (2016-12-12)

**Breaking change**

  - "account_name" parameter is now "name" in account operation

## 0.1.0 (2016-11-14)

  - Initial Release
