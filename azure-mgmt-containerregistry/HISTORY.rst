.. :changelog:

Release History
===============

1.0.0 (2017-09-22)
++++++++++++++++++

* New default API version 2017-10-01.
* Remove support for API Version 2017-06-01-preview
* New support for managed registries with three Managed SKUs.
* New support for registry webhooks and replications.
* Rename Basic SKU to Classic SKU.

0.3.1 (2017-06-30)
++++++++++++++++++

* Support for registry SKU update (2017-06-01-preview)
* New listUsages API to get the quota usages for a container registry (2017-06-01-preview)

0.3.0 (2017-06-15)
++++++++++++++++++

* This package now supports an additional ApiVersion 2017-06-01-preview

0.2.1 (2017-04-20)
++++++++++++++++++

This wheel package is now built with the azure wheel extension

0.2.0 (2017-03-20)
++++++++++++++++++

* New ApiVersion 2017-03-01
* Update getCredentials to listCredentials to support multiple login credentials.
* Refine regenerateCredential to support regenerate the specified login credential.
* Add Sku to registry properties as a required property.
* Rename GetProperties to Get.
* Change CreateOrUpdate to Create, add registry create parameters.

0.1.1 (2016-12-12)
++++++++++++++++++

**Bugfixes**

* Fix random error on Create and Delete operation

0.1.0 (2016-11-04)
++++++++++++++++++

* Initial Release
