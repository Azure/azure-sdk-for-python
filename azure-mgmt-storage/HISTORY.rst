.. :changelog:

Release History
===============

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
