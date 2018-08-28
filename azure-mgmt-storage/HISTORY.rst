.. :changelog:

Release History
===============

2.0.0 (2018-08-01)
++++++++++++++++++

**Bugfixes**

- Set the signed resource as optional instead of required

2.0.0rc4 (2018-06-26)
+++++++++++++++++++++

**Features (2018-02-01/2018-03-01-preview)**

Support HDFS feature and web endpoint in Account properties

- Model StorageAccountCreateParameters has a new parameter is_hns_enabled
- Model Endpoints has a new parameter web
- Model Endpoints has a new parameter dfs
- Model StorageAccount has a new parameter is_hns_enabled

2.0.0rc3 (2018-05-30)
+++++++++++++++++++++

**Features**

- Add preview version of management policy (API 2018-03-01-preview only). This is considered preview and breaking changes might happen
  if you opt in for that Api Version.

**Bugfixes**

- Correct azure-common dependency

2.0.0rc2 (2018-05-16)
+++++++++++++++++++++

**Bugfixes**

- Fix default "models" import to 2018-02-01

2.0.0rc1 (2018-05-11)
+++++++++++++++++++++

**Features**

- Add blob containers operations, immutability policy
- Add usage.list_by_location
- Client now supports Azure profiles.
- Client class can be used as a context manager to keep the underlying HTTP session open for performance

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


1.5.0 (2017-12-12)
++++++++++++++++++

**Features**

- Add StorageV2 as valid kind
- Add official support for API version 2017-10-01

1.4.0 (2017-09-26)
++++++++++++++++++

**Bug fixes**

- Add skus operations group to the generic client

**Features**

- Add official support for API version 2016-01-01

1.3.0 (2017-09-08)
++++++++++++++++++

**Features**

- Adds list_skus operation (2017-06-01)

**Breaking changes**

- Rename the preview attribute "network_acls" to "network_rule_set"

1.2.1 (2017-08-14)
++++++++++++++++++

**Bugfixes**

- Remove "tests" packaged by mistake (#1365)

1.2.0 (2017-07-19)
++++++++++++++++++

**Features**

- Api version 2017-06-01 is now the default
- This API version adds Network ACLs objects (2017-06-01 as preview)

1.1.0 (2017-06-28)
++++++++++++++++++

- Added support for https traffic only (2016-12-01)

1.0.0 (2017-05-15)
++++++++++++++++++

- Tag 1.0.0rc1 as stable (same content)

1.0.0rc1 (2017-04-11)
+++++++++++++++++++++

**Features**

To help customers with sovereign clouds (not general Azure),
this version has official multi ApiVersion support for 2015-06-15 and 2016-12-01

0.31.0 (2017-01-19)
+++++++++++++++++++

* New `list_account_sas` operation
* New `list_service_sas` operation
* Name syntax are now checked before RestAPI call, not the server (exception changed)

Based on API version 2016-12-01.

0.30.0 (2016-11-14)
+++++++++++++++++++

* Initial release. Based on API version 2016-01-01
  Note that this is the same content as 0.30.0rc6, committed as 0.30.0.

0.20.0 (2015-08-31)
+++++++++++++++++++

* Initial preview release. Based on API version 2015-05-01-preview.
