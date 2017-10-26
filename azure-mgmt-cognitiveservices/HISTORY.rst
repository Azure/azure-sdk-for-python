.. :changelog:

Release History
===============

2.0.0 (2017-10-26)
++++++++++++++++++

**Breaking changes**

- remove "location" as a constructor parameter
- sku_name in "check_sku_availability" result is now a str (from an enum)
- merge "cognitive_services_accounts" into "accounts" operation group
- "key_name" is now required to regenerate keys
- "location/skus/kind/type" are now required for "list" available skus

1.0.0 (2017-05-01)
++++++++++++++++++

* No changes, this is the 0.30.0 approved as stable.

0.30.0 (2017-05-01)
+++++++++++++++++++

* Initial Release (ApiVersion 2017-04-18)
* This wheel package is now built with the azure wheel extension