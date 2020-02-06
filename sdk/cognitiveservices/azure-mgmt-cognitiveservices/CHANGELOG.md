# Release History

## 5.0.0 (2019-06-21)

**Features**

  - Model CognitiveServicesAccount has a new parameter network_acls
  - Add operation check_domain_availability

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes for some imports. In summary, some modules
were incorrectly visible/importable and have been renamed. This fixed
several issues caused by usage of classes that were not supposed to be
used in the first place.

  - CognitiveServicesManagementClient cannot be imported from
    `azure.mgmt.cognitiveservices.v20xx_yy_zz.cognitive_services_management_client`
    anymore (import from `azure.mgmt.cognitiveservices.v20xx_yy_zz`
    works like before)
  - CognitiveServicesManagementClientConfiguration import has been moved
    from
    `azure.mgmt.cognitiveservices.v20xx_yy_zz.cognitive_services_management_client`
    to `azure.mgmt.cognitiveservices.v20xx_yy_zz`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using
    `azure.mgmt.cognitiveservices.v20xx_yy_zz.models.my_class`
    (import from `azure.mgmt.cognitiveservices.v20xx_yy_zz.models`
    works like before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.cognitiveservices.v20xx_yy_zz.operations.my_class_operations`
    (import from
    `azure.mgmt.cognitiveservices.v20xx_yy_zz.operations` works like
    before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 4.0.0 (2019-05-01)

**Features**

  - Model CognitiveServicesAccount has a new parameter
    custom_sub_domain_name
  - Model CognitiveServicesAccountUpdateParameters has a new parameter
    properties
  - Operation AccountsOperations.update now takes optional properties

**Breaking changes**

  - Remove limited enum Kind and SkuName. Replace all usage by a simple
    string (e.g. "Bing.SpellCheck.v7")

## 3.0.0 (2018-05-21)

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

**Features**

  - Add "resource_skus" operation group
  - Update SKU list
  - Add "accounts.get_usages" operation
  - Client class can be used as a context manager to keep the underlying
    HTTP session open for performance

**Bugfixes**

  - Compatibility of the sdist with wheel 0.31.0

## 2.0.0 (2017-10-26)

**Breaking changes**

  - remove "location" as a constructor parameter
  - sku_name in "check_sku_availability" result is now a str (from an
    enum)
  - merge "cognitive_services_accounts" into "accounts" operation
    group
  - "key_name" is now required to regenerate keys
  - "location/skus/kind/type" are now required for "list" available skus

## 1.0.0 (2017-05-01)

  - No changes, this is the 0.30.0 approved as stable.

## 0.30.0 (2017-05-01)

  - Initial Release (ApiVersion 2017-04-18)
  - This wheel package is now built with the azure wheel extension
