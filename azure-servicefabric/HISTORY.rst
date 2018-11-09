.. :changelog:

Release History
===============

6.3.0.0 (2018-07-27)
++++++++++++++++++++

**Bugfixes**

- Numerous improvements to descriptions and help texts

**Features**

- Add application health policies parameter for config upgrade
- Query to get nodes now supports specification to limit number of returned items

6.2.0.0 (2018-05-10)
++++++++++++++++++++

**General Breaking changes**

This version uses a next-generation code generator that *might* introduce breaking changes.

- Model signatures now use only keyword-argument syntax. All positional arguments must be re-written as keyword-arguments.
  To keep auto-completion in most cases, models are now generated for Python 2 and Python 3. Python 3 uses the "*" syntax for keyword-only arguments.
- Enum types now use the "str" mixin (class AzureEnum(str, Enum)) to improve the behavior when unrecognized enum values are encountered.
  While this is not a breaking change, the distinctions are important, and are documented here:
  https://docs.python.org/3/library/enum.html#others
  At a glance:

  - "is" should not be used at all.
  - "format" will return the string value, where "%s" string formatting will return `NameOfEnum.stringvalue`. Format syntax should be prefered.

- New Long Running Operation:

  - Return type changes from `msrestazure.azure_operation.AzureOperationPoller` to `msrest.polling.LROPoller`. External API is the same.
  - Return type is now **always** a `msrest.polling.LROPoller`, regardless of the optional parameters used.
  - The behavior has changed when using `raw=True`. Instead of returning the initial call result as `ClientRawResponse`, 
    without polling, now this returns an LROPoller. After polling, the final resource will be returned as a `ClientRawResponse`.
  - New `polling` parameter. The default behavior is `Polling=True` which will poll using ARM algorithm. When `Polling=False`,
    the response of the initial call will be returned without polling.
  - `polling` parameter accepts instances of subclasses of `msrest.polling.PollingMethod`.
  - `add_done_callback` will no longer raise if called after polling is finished, but will instead execute the callback right away.

**Bugfixes**
 
- Numerous fixes to descriptions and help text of entities
- Compatibility of the sdist with wheel 0.31.0
 
**Features**
 
- Add support for invoking container APIs
- Add option to fetch container logs from exited containers
- Query to get chaos events now supports specification to limit number of returned items
- Client class can be used as a context manager to keep the underlying HTTP session open for performance

6.1.2.9 (2018-02-05)
++++++++++++++++++++

**Bugfixes**

- Numerous fixes to descriptions and help text of entities

**Features**

- Chaos service now supports a target filter
- Application types can now be provisioned and created in external stores
- Added Orchestration Service internal support APIs
- Added container deployment management APIs

6.1.1.9 (2018-01-23)
++++++++++++++++++++

This version was broken and has been removed from PyPI.

6.0.2 (2017-10-26)
++++++++++++++++++

**Bugfixes**

- remove application_type_version in get_application_type_info_list_by_name
- fix application_type_definition_kind_filter default value from 65535 to 0

**Features**

- add create_name, get_name_exists_info, delete_name, get_sub_name_info_list,
  get_property_info_list, put_property, get_property_info, delete_property,
  submit_property_batch

6.0.1 (2017-09-28)
++++++++++++++++++

**Bug fix**

- Fix some unexpected exceptions

6.0 (2017-09-22)
++++++++++++++++

* Stable 6.0 api

6.0.0rc1 (2017-09-16)
+++++++++++++++++++++

* Release candidate for Service Fabric 6.0 runtime

5.6.130 (2017-05-04)
++++++++++++++++++++

* Initial Release
