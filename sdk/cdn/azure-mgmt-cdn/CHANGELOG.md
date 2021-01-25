# Release History

## 10.0.0 (2021-01-19)

**Features**

  - Model ProxyResource has a new parameter system_data
  - Model OriginGroup has a new parameter system_data
  - Model Endpoint has a new parameter system_data
  - Model EdgeNode has a new parameter system_data
  - Model Origin has a new parameter system_data
  - Model TrackedResource has a new parameter system_data
  - Model Profile has a new parameter system_data
  - Model Profile has a new parameter frontdoor_id
  - Model CdnWebApplicationFirewallPolicy has a new parameter system_data
  - Model CustomDomain has a new parameter system_data
  - Added operation group AFDOriginsOperations
  - Added operation group AFDProfilesOperations
  - Added operation group AFDEndpointsOperations
  - Added operation group RoutesOperations
  - Added operation group LogAnalyticsOperations
  - Added operation group RulesOperations
  - Added operation group ValidateOperations
  - Added operation group AFDOriginGroupsOperations
  - Added operation group SecretsOperations
  - Added operation group SecurityPoliciesOperations
  - Added operation group AFDCustomDomainsOperations
  - Added operation group RuleSetsOperations

**Breaking changes**

  - Parameter odata_type of model UrlSigningActionParameters is now required
  - Operation PoliciesOperations.begin_update has a new signature
  - Operation EndpointsOperations.validate_custom_domain has a new signature
  - Operation EndpointsOperations.begin_load_content has a new signature
  - Operation EndpointsOperations.begin_purge_content has a new signature
  - Operation ProfilesOperations.begin_update has a new signature
  - Operation CdnManagementClientOperationsMixin.check_name_availability has a new signature
  - Operation CdnManagementClientOperationsMixin.check_name_availability_with_subscription has a new signature
  - Operation CdnManagementClientOperationsMixin.validate_probe has a new signature
  - Operation CustomDomainsOperations.begin_create has a new signature
  - Model UrlSigningActionParameters no longer has parameter ip_subnets
  - Model UrlSigningActionParameters no longer has parameter key_id

## 10.0.0b1 (2020-10-31)
This is beta preview version.
For detailed changelog please refer to equivalent stable version 5.1.0 (https://pypi.org/project/azure-mgmt-cdn/5.1.0/)

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
  - For a complete set of supported options, see the [parameters accept in Request documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)

**General new features**

- Type annotations support using `typing`. SDKs are mypy ready.
- This client has now stable and official support for async. Check the `aio` namespace of your package to find the async client.
- This client now support natively tracing library like OpenCensus or OpenTelemetry. See this [tracing quickstart](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/core/azure-core-tracing-opentelemetry) for an overview.

## 5.1.0 (2020-08-10)

**Features**
  - Add UrlSigningAction

## 5.0.0 (2020-07-21)

**Features**

  - Model Origin has a new parameter private_link_approval_message
  - Model Origin has a new parameter enabled
  - Model Origin has a new parameter weight
  - Model Origin has a new parameter origin_host_header
  - Model Origin has a new parameter private_link_resource_id
  - Model Origin has a new parameter private_link_location
  - Model Origin has a new parameter private_link_alias
  - Model Origin has a new parameter priority
  - Model Origin has a new parameter private_endpoint_status
  - Model EndpointUpdateParameters has a new parameter url_signing_keys
  - Model EndpointUpdateParameters has a new parameter default_origin_group
  - Model Endpoint has a new parameter url_signing_keys
  - Model Endpoint has a new parameter origin_groups
  - Model Endpoint has a new parameter default_origin_group
  - Added operation OriginsOperations.create
  - Added operation OriginsOperations.delete
  - Added operation group OriginGroupsOperations

**Breaking changes**

  - Model Origin no longer has parameter location
  - Model Origin no longer has parameter tags
  - Model CustomDomain no longer has parameter custom_https_parameters
  - Model DeepCreatedOrigin has a new signature
  - Model OriginUpdateParameters has a new signature

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
