# Release History

## 4.1.0rc1 (2020-01-18)

**Features**

  - Model Endpoint has a new parameter
    web_application_firewall_policy_link
  - Model EndpointUpdateParameters has a new parameter
    web_application_firewall_policy_link
  - Added operation group PoliciesOperations
  - Added operation group ManagedRuleSetsOperations

## 4.0.0 (2019-11-25)

**Features**

  - Model DeliveryRule has a new parameter name
  - Model CdnManagedHttpsParameters has a new parameter
    minimum_tls_version
  - Model UserManagedHttpsParameters has a new parameter
    minimum_tls_version
  - Model CustomDomainHttpsParameters has a new parameter
    minimum_tls_version
  - Model CustomDomain has a new parameter custom_https_parameters
  - Added operation group CdnManagementClientOperationsMixin

**General Breaking Changes**

This version uses a next-generation code generator that *might*
introduce breaking changes. In summary, some modules were incorrectly
visible/importable and have been renamed. This fixed several issues
caused by usage of classes that were not supposed to be used in the
first place.

  - CdnManagementClient cannot be imported from
    `azure.mgmt.cdn.cdn_management_client` anymore (import from
    `azure.mgmt.cdn` works like before)
  - CdnManagementClientConfiguration import has been moved from
    `azure.mgmt.cdn.cdn_management_client` to `azure.mgmt.cdn`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.cdn.models.my_class` (import from
    `azure.mgmt.cdn.models` works like before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.cdn.operations.my_class_operations` (import from
    `azure.mgmt.cdn.operations` works like before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 3.1.0 (2019-03-05)

**Features**

  - Add custom_domain_https_parameters support

## 3.0.0 (2018-05-25)

**Features**

  - Add client method check_name_availability_with_subscription
  - Model EndpointUpdateParameters has a new parameter delivery_policy
  - Model Endpoint has a new parameter delivery_policy
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

## 2.0.0 (2017-10-26)

**Features**

  - Add probe operations and in some models
  - Add list_supported_optimization_types

**Breaking changes**

  - move resource_usage into its own operation group
  - move operations list into its own operation group

Api version changed from 2016-10-02 to 2017-04-02

## 1.0.0 (2017-06-30)

**Features**

  - Add disable_custom_https and enable_custom_https

**Breaking changes**

  - Rename check_resource_usage to list_resource_usage
  - list EdgeNode now returns an iterator of EdgeNode, not a
    EdgenodeResult instance with an attribute "value" being a list of
    EdgeNode

## 0.30.3 (2017-05-15)

  - This wheel package is now built with the azure wheel extension

## 0.30.2 (2016-12-22)

  - Fix EdgeNode attributes content

## 0.30.1 (2016-12-15)

  - Fix list EdgeNodes method return type

## 0.30.0 (2016-12-14)

  - Initial preview release (API Version 2016-10-02)
  - Major breaking changes from 0.30.0rc6

## 0.30.0rc6 (2016-09-02)

  - Initial alpha release (API Version 2016-04-02)
