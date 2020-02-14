# Release History

## 3.0.0 (2019-06-18)

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes if you were importing from the v20xx_yy_zz
API folders. In summary, some modules were incorrectly
visible/importable and have been renamed. This fixed several issues
caused by usage of classes that were not supposed to be used in the
first place.

  - DnsManagementClient cannot be imported from
    `azure.mgmt.dns.v20xx_yy_zz.dns_management_client` anymore
    (import from `azure.mgmt.dns.v20xx_yy_zz` works like before)
  - DnsManagementClientConfiguration import has been moved from
    `azure.mgmt.dns.v20xx_yy_zz.dns_management_client` to
    `azure.mgmt.dns.v20xx_yy_zz`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.dns.v20xx_yy_zz.models.my_class`
    (import from `azure.mgmt.dns.v20xx_yy_zz.models` works like
    before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.dns.v20xx_yy_zz.operations.my_class_operations`
    (import from `azure.mgmt.dns.v20xx_yy_zz.operations` works like
    before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 2.1.0 (2018-09-10)

**Features**

  - Model RecordSet has a new parameter target_resource
  - Added operation group DnsResourceReferenceOperations

## 2.0.0 (2018-07-01)

**Bugfixes**

  - Fix ARM compliance (correct settings of location, tags, etc.)

## 2.0.0rc2 (2018-07-05)

**Features**

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

## 2.0.0rc1 (2018-03-14)

**Features**

  - Add public/private zone
  - Add record_sets.list_all_by_dns_zone operation
  - Add zones.update operation

**Breaking changes**

  - 'zone_type' is now required when creating a zone ('Public' is
    equivalent as previous behavior)

New API version 2018-03-01-preview

## 1.2.0 (2017-10-26)

  - add record_type CAA
  - remove pointless return type of delete

Api version moves from 2016-04-01 to 2017-09-01

## 1.1.0 (2017-10-10)

  - Add "recordsetnamesuffix" filter parameter to list operations

## 1.0.1 (2017-04-20)

This wheel package is now built with the azure wheel extension

## 1.0.0 (2016-12-12)

  - Initial release
